# codebase-schematic — Design

## One-line pitch

A single-skill Claude Code plugin that produces a PNG architecture-overview
diagram for any codebase. Claude reads the target repo, judges what single
structural fact is actually worth arguing visually, and renders it as a
schematic diagram — same underlying technique proven out this session while
building `strategy-stack-skills`' diagram, but scoped to exactly one job
instead of open-ended diagramming.

## Why this exists, and why it's a separate repo

`strategy-stack-skills` briefly vendored a general-purpose diagramming skill
(`excalidraw-diagram`, from `coleam00/excalidraw-diagram-skill`) and then
removed it — it was the only skill in that plugin with a real dependency
footprint (Playwright + a downloaded Chromium) and an external-CDN runtime
dependency, and no orchestrator in that plugin actually required it.

`codebase-schematic` is a deliberate second attempt at the same underlying
capability, done right: a standalone repo whose *entire purpose* is producing
a diagram, so the Playwright/Chromium footprint is no longer a mismatched
dependency tacked onto an unrelated plugin — it's the actual point. Narrowing
scope to one diagram type (architecture overview) instead of arbitrary
diagramming is what keeps it a focused skill rather than a second copy of a
generic tool.

## Origin and licensing — everything here is freshly authored

While researching `coleam00/excalidraw-diagram-skill` for this design, we
found it has **no LICENSE file** — no declared license means default
copyright applies, and redistributing its file contents isn't clearly
permitted. `strategy-stack-skills` vendored those files anyway (with
attribution) before this was checked; that gap is now known and unresolved
there.

`codebase-schematic` avoids the question entirely: **no file or verbatim text
is copied from that repo.** Every file here — `SKILL.md`, the
`references/*.md` design-methodology docs, `render_excalidraw.py`,
`render_template.html` — is written fresh for this repo. It's informed by the
same general, non-copyrightable ideas (Excalidraw's own JSON element format,
the technique of calling `exportToSvg` from `@excalidraw/excalidraw` in a
headless browser and screenshotting the result, and general diagram-design
sense refined by actually building and fixing the two-pipelines diagram this
session) but the expression — the actual wording, structure, and code — is
original to this repo.

## Repo layout

```
codebase-schematic/
├── .claude-plugin/plugin.json
├── .claude-plugin/marketplace.json      # single-plugin marketplace, verified pattern
├── skills/codebase-schematic/
│   ├── SKILL.md                         # lean: workflow + links into references/
│   └── references/
│       ├── design-methodology.md        # shape meaning, layout principles,
│       │                                #   render-validate-fix loop — original text
│       ├── color-palette.md             # semantic fill/stroke pairs — single source
│       │                                #   of truth, swappable for brand colors
│       ├── element-templates.md         # copy-paste JSON templates per element type
│       ├── render_excalidraw.py         # renders .excalidraw JSON -> PNG via Playwright
│       ├── render_template.html         # loads @excalidraw/excalidraw from esm.sh
│       │                                #   WITHOUT the broken `?bundle` param
│       └── pyproject.toml               # playwright dependency only
├── examples/self/                       # dogfood: a schematic of this repo's own structure
├── tests/validate_plugin.py             # frontmatter checks + a render-pipeline regression
│                                         #   test guarding against the ?bundle-style breakage
├── .github/workflows/validate.yml       # runs validate_plugin.py + a full render smoke test
├── README.md
└── LICENSE                              # MIT, this repo's own original content
```

## `SKILL.md` workflow

Frontmatter triggers on: "diagram this codebase", "show me the architecture
of X visually", "create a schematic of how this project fits together",
"visualize this codebase's structure" — and explicitly states the scope
boundary (one diagram style; for anything else, this isn't the right skill)
so it doesn't compete with unrelated diagram requests.

1. **Explore.** README, manifest files (`package.json` / `pyproject.toml` /
   `Cargo.toml` / `go.mod` / etc.), top-level directory structure, entry
   points. Depth scales to repo size — sample key files and lean on
   directory structure + README + entry-point imports for a large repo;
   read broadly for a small one. No AST parser, no exhaustive read.

2. **Find the one argument worth making.** Per the "diagrams argue, not
   display" principle: identify the single most important structural fact
   about this codebase — strict layering, a plugin/dispatch system, a
   pipeline, independent packages sharing one core, whatever it actually is.
   This is the same judgment call made by hand for the two-pipelines
   diagram (the shared `field-understanding` step was *the* argument, not
   just another box).

3. **Map to a visual pattern.** Reuse a small pattern library (fan-out,
   layered bands, timeline, tree, convergence) documented in
   `references/design-methodology.md`, plus one rule specific to codebases
   that a generic diagramming tool wouldn't know to enforce: **dependency
   arrows are always drawn one-directional.** A real codebase has a
   dependency direction; the diagram should never draw it as bidirectional
   even when two modules reference each other's types.

4. **Generate the Excalidraw JSON**, then run the **render → view → fix**
   loop: render to PNG, read the image, audit it against the argument from
   step 2, fix defects, repeat until clean. Mandatory, not optional — this
   is exactly the process that caught and fixed the connector/title overlap
   in the two-pipelines diagram.

5. **Deliver** the PNG (and the `.excalidraw` source) via file delivery.
   Offer — don't assume — to embed it in the target repo's README, mirroring
   how `strategy-stack-skills`' README ended up with its diagram.

## Explicit non-goals (YAGNI)

- No AST/dependency parser. No per-language static analysis. Claude's own
  reading of the codebase is the analysis engine.
- No multiple selectable diagram styles (dependency graph, directory tree,
  per-workflow call-flow). One style, done well: architecture overview.
- No automatic README-editing. Delivery is the PNG; embedding it is offered,
  never done unprompted.

## Testing & CI

`tests/validate_plugin.py`:
- `SKILL.md` frontmatter has `name` matching the directory and a `description`
  within the length limit (same checks `strategy-stack-skills` runs, minus
  the cross-skill reference check — there's only one skill here).
- **Regression guard for the exact bug we hit this session**: assert
  `render_template.html` does not import `@excalidraw/excalidraw?bundle` —
  fails loudly if that broken pattern is ever reintroduced.

CI (`.github/workflows/validate.yml`) runs `validate_plugin.py` **and** a
full render smoke test — `uv sync && uv run playwright install chromium &&
uv run python render_excalidraw.py examples/self/*.excalidraw` — so a future
esm.sh-side breakage (the actual failure mode we hit by hand this session)
gets caught by CI automatically instead of discovered manually next time.

## Example

`examples/self/`: a schematic diagram of `codebase-schematic`'s own
structure (this exact repo layout — the plugin manifest, the one skill, its
references, tests, CI). Small, fast to regenerate, and doubles as a working
demo the same way `strategy-stack-skills`' examples do.

## Open question for implementation time

None blocking — packaging (single-skill plugin), naming, location, analysis
approach (explore-and-hand-design, no parser), and the licensing approach
(fresh implementation, no vendoring) are all decided above.
