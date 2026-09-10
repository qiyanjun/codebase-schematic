#!/usr/bin/env python3
"""Validate the codebase-schematic plugin.

Checks:
  1. skills/codebase-schematic/SKILL.md exists
  2. YAML frontmatter parses, with `name` and `description`
  3. frontmatter `name` matches the skill directory name
  4. `description` is within the 1024-character limit
  5. render_template.html does not import the esm.sh bundle with `?bundle` —
     that query param produced a broken transitive dependency path when
     tested directly (see docs/superpowers/specs/2026-09-10-codebase-schematic-design.md)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(ROOT, "skills", "codebase-schematic")
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
RENDER_TEMPLATE = os.path.join(SKILL_DIR, "references", "render_template.html")
MAX_DESC = 1024


def parse_frontmatter(text: str) -> dict | None:
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    if not match:
        return None
    block = match.group(1)
    name = re.search(r"^name:\s*(.+)$", block, re.M)
    desc = re.search(r"^description:\s*(>-?|\|)?\s*\n?(.*?)(?=\n[a-z_-]+:|\Z)", block, re.S | re.M)
    description = " ".join(desc.group(2).split()) if desc else None
    if description and len(description) >= 2 and description[0] == description[-1] and description[0] in ('"', "'"):
        description = description[1:-1]
    return {
        "name": name.group(1).strip() if name else None,
        "description": description,
    }


def main() -> int:
    errors = []

    if not os.path.exists(SKILL_MD):
        errors.append(f"missing {SKILL_MD}")
    else:
        text = open(SKILL_MD, encoding="utf-8").read()
        frontmatter = parse_frontmatter(text)
        if frontmatter is None:
            errors.append("SKILL.md: no YAML frontmatter")
        else:
            if not frontmatter["name"]:
                errors.append("SKILL.md: frontmatter missing `name`")
            elif frontmatter["name"] != "codebase-schematic":
                errors.append(
                    f"SKILL.md: frontmatter name is '{frontmatter['name']}' but directory is 'codebase-schematic'"
                )
            if not frontmatter["description"]:
                errors.append("SKILL.md: frontmatter missing `description`")
            elif len(frontmatter["description"]) > MAX_DESC:
                errors.append(
                    f"SKILL.md: description is {len(frontmatter['description'])} chars (max {MAX_DESC})"
                )

    if not os.path.exists(RENDER_TEMPLATE):
        errors.append(f"missing {RENDER_TEMPLATE}")
    else:
        template_text = open(RENDER_TEMPLATE, encoding="utf-8").read()
        if "?bundle" in template_text:
            errors.append(
                "render_template.html imports the esm.sh bundle with '?bundle' — "
                "this query param has produced a broken transitive dependency path "
                "before (a 404 on a @braintree/sanitize-url sub-path). Import the "
                "package directly instead."
            )

    if errors:
        print(f"{len(errors)} error(s):")
        for error in errors:
            print(f"  ERROR {error}")
        return 1

    print("codebase-schematic: 0 errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
