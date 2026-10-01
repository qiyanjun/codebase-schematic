#!/usr/bin/env python3
"""Validate the codebase-schematic plugin.

The plugin directory comes from .claude-plugin/marketplace.json
plugins[0].source ("./" = the repo root). Checks:
  1. every skills/<dir>/SKILL.md has frontmatter that parses as strict YAML,
     with `name` and `description`; `name` matches the directory;
     `description` is within the 1024-character limit (longer descriptions
     are truncated or rejected). skills/codebase-schematic must exist.
  2. plugin.json and marketplace.json agree on the plugin name, and on the
     version when marketplace.json pins one — a bump that touches only one
     of them ships a stale cache
  3. every `/codebase-schematic:<x>` and backticked `codebase-schematic:<x>`
     mention resolves to a skill (or a commands/<x>.md, if any exist)
  4. every backticked `references/...` or `scripts/...` path resolves to a
     real file (relative to the skill directory — any skill's, for docs
     outside skills/ — the referencing file, the plugin root, or the repo
     root), and so does every
     ${CLAUDE_PLUGIN_ROOT}/... path
  5. every .py file in the plugin (tests/, skills/*/references/,
     skills/*/scripts/) compiles, and every .sh file passes `bash -n`
  6. render_template.html does not import the esm.sh bundle with `?bundle` —
     that query param produced a broken transitive dependency path when
     tested directly (see docs/superpowers/specs/2026-09-10-codebase-schematic-design.md)
  7. every arrow element in every examples/*.excalidraw file has at most one
     non-null arrowhead — dependency arrows must be one-directional, per
     SKILL.md / design-methodology.md / element-templates.md / README.md
"""
import glob
import json
import os
import re
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("pyyaml is required: pip install pyyaml")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_SKILL = "codebase-schematic"
EXAMPLES_DIR = os.path.join(ROOT, "examples")
MAX_DESC = 1024
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules", ".superpowers"}


def rel(path: str) -> str:
    return os.path.relpath(path, ROOT)


def plugin_dir(errors: list) -> str | None:
    market_json = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    try:
        market = json.load(open(market_json, encoding="utf-8"))
        source = market["plugins"][0]["source"]
        if isinstance(source, dict):  # e.g. {"source": "git-subdir", "path": "<dir>"}
            source = source.get("path", ".")
    except (OSError, json.JSONDecodeError, KeyError, IndexError) as e:
        errors.append(f"{rel(market_json)}: unreadable or has no plugin entry: {e}")
        return None
    path = os.path.normpath(os.path.join(ROOT, source))
    if not os.path.isdir(path):
        errors.append(f"marketplace source {source!r} is not a directory")
        return None
    return path


def frontmatter(path: str) -> dict | None:
    text = open(path, encoding="utf-8").read()
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return None
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def check_skills(errors: list, plugin: str) -> set:
    names = set()
    for skill_md in sorted(glob.glob(os.path.join(plugin, "skills", "*", "SKILL.md"))):
        dirname = os.path.basename(os.path.dirname(skill_md))
        names.add(dirname)
        fm = frontmatter(skill_md)
        if fm is None:
            errors.append(f"{rel(skill_md)}: frontmatter missing or not valid YAML")
            continue
        if fm.get("name") != dirname:
            errors.append(f"{rel(skill_md)}: name is {fm.get('name')!r} but directory is {dirname!r}")
        desc = " ".join(str(fm.get("description") or "").split())
        if not desc:
            errors.append(f"{rel(skill_md)}: frontmatter missing `description`")
        elif len(desc) > MAX_DESC:
            errors.append(f"{rel(skill_md)}: description is {len(desc)} chars (max {MAX_DESC})")
    if MAIN_SKILL not in names:
        errors.append(f"missing {rel(os.path.join(plugin, 'skills', MAIN_SKILL, 'SKILL.md'))}")
    return names


def check_manifests(errors: list, plugin: str) -> str | None:
    plugin_json = os.path.join(plugin, ".claude-plugin", "plugin.json")
    market_json = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
    try:
        meta = json.load(open(plugin_json, encoding="utf-8"))
        market = json.load(open(market_json, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"manifest unreadable: {e}")
        return None
    if not meta.get("version"):
        errors.append(f"{rel(plugin_json)}: missing `version` (claude plugin update compares it)")
    entries = [p for p in market.get("plugins", []) if p.get("name") == meta.get("name")]
    if not entries:
        errors.append(f"marketplace.json has no entry named {meta.get('name')!r}")
    elif "version" in entries[0] and entries[0]["version"] != meta.get("version"):
        errors.append(
            f"version mismatch: plugin.json {meta.get('version')} vs "
            f"marketplace.json {entries[0].get('version')}"
        )
    return meta.get("name")


def doc_files(plugin: str) -> list:
    docs = []
    for root, dirs, names in os.walk(plugin):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        docs += [os.path.join(root, n) for n in names if n.endswith(".md")]
    readme = os.path.join(ROOT, "README.md")
    if os.path.exists(readme) and readme not in docs:
        docs.append(readme)
    return sorted(docs)


def check_links(errors: list, plugin: str, name: str, skills: set) -> None:
    commands = {os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(plugin, "commands", "*.md"))}
    targets = skills | commands
    ns = re.escape(name)
    skills_dir = os.path.join(plugin, "skills")

    for path in doc_files(plugin):
        skill_dir = None
        parts = os.path.relpath(path, skills_dir).split(os.sep)
        if parts[0] != ".." and len(parts) > 1:
            skill_dir = os.path.join(skills_dir, parts[0])
        here = os.path.dirname(path)

        for lineno, line in enumerate(open(path, encoding="utf-8"), 1):
            where = f"{rel(path)}:{lineno}"
            for ref in re.findall(rf"(?<![\w.-])/{ns}:([a-z][a-z0-9-]*)", line):
                if ref not in targets:
                    errors.append(f"{where}: /{name}:{ref} is not a skill or command in this plugin")
            for ref in re.findall(rf"`{ns}:([a-z][a-z0-9-]*)`", line):
                if ref not in targets:
                    errors.append(f"{where}: `{name}:{ref}` is not a skill or command in this plugin")

            for ref in re.findall(r"`([^`\s]*?(?:references|scripts)/[A-Za-z0-9_.-]+\.(?:md|sh|py|js|html|toml|json|lock))`", line):
                # Docs outside skills/ (README, design notes) name paths relative to a skill.
                bases = [skill_dir] if skill_dir else [os.path.join(skills_dir, s) for s in skills]
                bases += [here, plugin, ROOT]
                if not any(b and os.path.exists(os.path.normpath(os.path.join(b, ref))) for b in bases):
                    errors.append(f"{where}: `{ref}` does not exist")
            for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]*[A-Za-z0-9_-])", line):
                if not os.path.exists(os.path.join(plugin, ref)):
                    errors.append(f"{where}: ${{CLAUDE_PLUGIN_ROOT}}/{ref} does not exist")


def check_code(errors: list, plugin: str) -> None:
    py, sh = [], []
    for root, dirs, names in os.walk(plugin):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        py += [os.path.join(root, n) for n in names if n.endswith(".py")]
        sh += [os.path.join(root, n) for n in names if n.endswith(".sh")]
    for script in sorted(py):
        try:
            compile(open(script, encoding="utf-8").read(), script, "exec")
        except SyntaxError as e:
            errors.append(f"{rel(script)}: does not compile: {e}")
    for script in sorted(sh):
        result = subprocess.run(["bash", "-n", script], capture_output=True, text=True)
        if result.returncode != 0:
            errors.append(f"{rel(script)}: bash -n failed: {result.stderr.strip()}")


def check_render_template(errors: list, plugin: str) -> None:
    render_template = os.path.join(plugin, "skills", MAIN_SKILL, "references", "render_template.html")
    if not os.path.exists(render_template):
        errors.append(f"missing {rel(render_template)}")
        return
    if "?bundle" in open(render_template, encoding="utf-8").read():
        errors.append(
            "render_template.html imports the esm.sh bundle with '?bundle' — "
            "this query param has produced a broken transitive dependency path "
            "before (a 404 on a @braintree/sanitize-url sub-path). Import the "
            "package directly instead."
        )


def check_examples(errors: list) -> None:
    excalidraw_files = sorted(
        glob.glob(os.path.join(EXAMPLES_DIR, "**", "*.excalidraw"), recursive=True)
    )
    for excalidraw_file in excalidraw_files:
        rel_path = rel(excalidraw_file)
        try:
            with open(excalidraw_file, encoding="utf-8") as f:
                doc = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{rel_path}: invalid JSON: {e}")
            continue

        for element in doc.get("elements", []):
            if element.get("type") != "arrow":
                continue
            if element.get("startArrowhead") and element.get("endArrowhead"):
                errors.append(
                    f"{rel_path}: arrow '{element.get('id')}' has both "
                    f"startArrowhead ({element['startArrowhead']!r}) and "
                    f"endArrowhead ({element['endArrowhead']!r}) set — "
                    "dependency arrows must be one-directional"
                )


def main() -> int:
    errors = []
    plugin = plugin_dir(errors)
    if plugin is None:
        print(f"ERROR {errors[0]}")
        return 1

    skills = check_skills(errors, plugin)
    name = check_manifests(errors, plugin) or os.path.basename(plugin)
    check_links(errors, plugin, name, skills)
    check_code(errors, plugin)
    check_render_template(errors, plugin)
    check_examples(errors)

    if errors:
        print(f"{len(errors)} error(s):")
        for error in errors:
            print(f"  ERROR {error}")
        return 1

    print(f"{name}: 0 errors ({len(skills)} skill(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
