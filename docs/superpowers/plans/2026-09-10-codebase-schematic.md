# Codebase Schematic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `codebase-schematic` Claude Code plugin — a single skill that produces a PNG architecture-overview diagram for any codebase — from an empty repo (currently just `README.md` and `LICENSE`) to an installed, pushed, CI-validated plugin.

**Architecture:** A single-skill plugin (`.claude-plugin/plugin.json` + `marketplace.json`, mirroring the verified-working pattern from `strategy-stack-skills`). The skill itself has a lean `SKILL.md` (explore → find the one argument → design → render/view/fix → deliver) that defers detail to `references/*.md`, plus a self-contained render pipeline (Playwright + a local HTML page that loads `@excalidraw/excalidraw` from esm.sh) written fresh for this repo rather than vendored, since the repo we'd otherwise copy from has no LICENSE file.

**Tech Stack:** Markdown (SKILL.md + references), Python 3.11+ with Playwright (render pipeline + validator), pytest (unit tests for the pure bounding-box logic), GitHub Actions (CI).

**Spec:** `docs/superpowers/specs/2026-09-10-codebase-schematic-design.md`

## Global Constraints

- **Nothing is copied from `coleam00/excalidraw-diagram-skill` or from `strategy-stack-skills`' now-deleted `excalidraw-diagram` skill** — every file (SKILL.md, references, scripts) is freshly authored. This is the entire reason this repo exists as a separate effort; violating it defeats the point.
- **One diagram style only**: architecture overview. No style-selector, no dependency-graph/AST parser, no multi-mode SKILL.md.
- **No code-parsing engine.** The "analysis" is Claude reading the codebase like it reads any other codebase — README, manifests, directory structure, entry points.
- **The render pipeline is self-contained**: Playwright + a local `render_template.html` that imports `@excalidraw/excalidraw` from `https://esm.sh/@excalidraw/excalidraw` — **never** append `?bundle` to that import; it produces a broken transitive dependency path (confirmed by direct testing in the sibling repo this session).
- **Dependency arrows in every generated diagram are one-directional**, never double-headed.
- Python `>=3.11`, `playwright>=1.40.0`, `pytest>=8.0.0` (dev only) — no other runtime dependencies.
- License: MIT, copyright "Yanjun Qi / Jane" 2026 — already committed, not part of this plan's tasks.
- The skill **offers, never assumes**, embedding its output into a target repo's README.

---

### Task 1: Plugin and marketplace manifests, `.gitignore`

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Create: `.gitignore`

**Interfaces:**
- Consumes: nothing
- Produces: a plugin manifest and single-plugin marketplace manifest that `claude plugin validate .` and `claude plugin marketplace add .` accept, plus exclusion rules so Task 4's `.venv/`, `uv.lock`-adjacent caches, and `__pycache__/` never get committed. Later tasks (and Task 8) depend on the manifests existing and being valid.

- [ ] **Step 1: Write `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
.venv/
*.egg-info/

# macOS
.DS_Store

# Playwright
node_modules/

# Subagent-driven-development scratch workspace (ledger, briefs, reports)
.superpowers/
```

- [ ] **Step 2: Write `plugin.json`**

```json
{
  "name": "codebase-schematic",
  "displayName": "Codebase Schematic",
  "version": "0.1.0",
  "description": "Generates a PNG architecture-overview diagram for a codebase: one schematic showing the single structural fact most worth understanding about how it fits together.",
  "author": { "name": "Yanjun Qi / Jane" },
  "license": "MIT",
  "keywords": ["diagram", "architecture", "excalidraw", "codebase", "schematic"]
}
```

- [ ] **Step 3: Write `marketplace.json`**

```json
{
  "$schema": "https://anthropic.com/claude-code/marketplace.schema.json",
  "name": "codebase-schematic",
  "description": "Generates a PNG architecture-overview diagram for a codebase.",
  "owner": { "name": "Yanjun Qi / Jane" },
  "plugins": [
    {
      "name": "codebase-schematic",
      "description": "Generates a PNG architecture-overview diagram for a codebase: one schematic showing the single structural fact most worth understanding about how it fits together.",
      "author": { "name": "Yanjun Qi / Jane" },
      "source": "./"
    }
  ]
}
```

- [ ] **Step 4: Validate the manifests**

Run: `claude plugin validate .` (from the repo root)
Expected: `✔ Validation passed`

- [ ] **Step 5: Commit**

```bash
git add .gitignore .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "Add plugin and marketplace manifests, .gitignore"
```

---

### Task 2: SKILL.md

**Files:**
- Create: `skills/codebase-schematic/SKILL.md`

**Interfaces:**
- Consumes: nothing directly (references paths that Task 3 and Task 4 will fill in — `references/design-methodology.md`, `references/color-palette.md`, `references/element-templates.md`, `references/render_excalidraw.py`)
- Produces: the skill's frontmatter `name: codebase-schematic` and `description`, which Task 5's validator checks

- [ ] **Step 1: Create the skill directory and write `SKILL.md`**

```markdown
---
name: codebase-schematic
description: Generate a single PNG schematic diagram showing the architecture of a codebase — the one structural fact most worth understanding about how it fits together, rendered as a clean modular diagram. Use when someone asks to "diagram this codebase", "show me the architecture visually", "create a schematic of how this project fits together", "visualize this codebase's structure", or "draw a picture of how this repo is organized". This skill produces exactly one diagram style — an architecture overview — not arbitrary diagrams (for that, use a general-purpose diagramming skill instead) and not a literal dependency graph from static analysis (there is no code parser here; the diagram reflects Claude's read of the codebase).
---

# Codebase Schematic

Turn a codebase into one PNG diagram that argues a specific point about its
architecture, not a decorative box-and-arrow illustration of the file tree.

## Step 1 — Explore the codebase

Read enough to understand the shape of the system, not every file:

- `README.md` and any architecture/design docs
- Manifest files (`package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`,
  `.claude-plugin/plugin.json`, etc.) for what the project declares itself
  to be and what it depends on
- Top-level directory structure
- Entry points (`main.*`, `index.*`, `cli.*`, or whatever the manifest
  points at) and their top-level imports

Scale the depth to the repo's size. A small repo: read broadly. A large
one: sample the entry points and a couple of the largest/most-central
directories, and lean on the directory structure and README rather than
reading every file.

## Step 2 — Find the one argument worth making

This is the step that matters most. A schematic either argues a specific
structural fact or it's just a labeled box grid — decide which fact *this*
codebase deserves before touching any JSON.

Ask: if someone could see only one thing about how this codebase is put
together, what should it be? Common answers:

- **Strict layering** — a fixed dependency direction between layers
  (e.g. UI never imports from the database layer directly)
- **A plugin/dispatch system** — a small core that fans out to independent,
  mutually-unaware plugins or handlers
- **A pipeline** — data or requests moving through an ordered sequence of
  stages
- **Independent packages sharing one core** — a monorepo shape where
  siblings don't depend on each other, only on a shared base
- **A mirrored pair** — two parallel subsystems that share one step and
  otherwise diverge

Name the fact in one sentence before designing anything. If nothing stands
out as more important than anything else, say so plainly rather than
inventing a false structure — a flat, undifferentiated codebase is itself
a legitimate (if less exciting) finding.

## Step 3 — Design the diagram

Read `references/design-methodology.md` for the full visual-pattern
library, shape-meaning table, and layout principles, and
`references/color-palette.md` for the semantic color pairs — pull every
color from there, never invent one inline.

One codebase-specific rule the general methodology doesn't cover:
**dependency arrows are always drawn one-directional.** A real codebase
has a dependency direction — even if two modules reference each other's
types, the diagram should show the direction that actually matters for
the argument in Step 2, not a bidirectional arrow that says nothing.

Match the pattern to the fact from Step 2 (layers → stacked horizontal
bands; plugin system → fan-out from a core; pipeline → timeline; mirrored
pair → two parallel timelines with a shared-node connector). See
`references/element-templates.md` for the exact JSON shape of each element
type.

Default to the **simple/conceptual** depth — module names and one-line
labels, not literal code snippets or file contents. This skill's whole
point is one clear architecture argument, not a comprehensive technical
reference diagram.

## Step 4 — Render, view, and fix (mandatory loop)

```bash
cd skills/codebase-schematic/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
```

This produces a PNG next to the `.excalidraw` file. Read it with the Read
tool — you cannot judge a diagram from its JSON. Check it against the
argument from Step 2: does the structure alone communicate that fact? Are
any labels clipped or overlapping? Do arrows land on the right elements
and route around others rather than through them? Fix what's wrong and
re-render. Repeat until the answer to all of those is yes — typically
2-4 passes, per `references/design-methodology.md`.

### First-time setup

```bash
cd skills/codebase-schematic/references
uv sync
uv run playwright install chromium
```

## Step 5 — Deliver

Send the PNG (and the `.excalidraw` source, if the person might want to
edit it) as a file. Offer — don't assume — to embed it in the target
repo's README; some people want the file, not a README edit.

## Guardrails

- One diagram, one argument. Resist the pull to show everything the
  codebase does — the value is in what gets left out.
- No invented structure. If Step 2 genuinely finds nothing more important
  than anything else, say so and diagram the flattest honest version
  rather than manufacturing a hierarchy.
- No code parser, no dependency-graph extraction tool. The analysis is
  Claude reading the codebase, the same way it would to answer any other
  question about it.
```

- [ ] **Step 2: Commit**

```bash
mkdir -p skills/codebase-schematic
git add skills/codebase-schematic/SKILL.md
git commit -m "Add codebase-schematic SKILL.md"
```

---

### Task 3: Reference docs — design methodology, color palette, element templates

**Files:**
- Create: `skills/codebase-schematic/references/design-methodology.md`
- Create: `skills/codebase-schematic/references/color-palette.md`
- Create: `skills/codebase-schematic/references/element-templates.md`

**Interfaces:**
- Consumes: nothing
- Produces: the reference material `SKILL.md` (Task 2) links to. Task 6 (the self-schematic example) reads all three directly while designing its diagram.

- [ ] **Step 1: Write `design-methodology.md`**

```markdown
# Design Methodology

How to turn a codebase's architecture into a diagram that argues something,
rather than a decorated list of its files.

## The core test

Before writing any JSON, ask: **if every label were removed, would the
shapes and their arrangement alone communicate the structural fact from
SKILL.md Step 2?** A diagram that only passes with labels intact is a
labeled list, not a diagram — the visual structure itself has to carry
meaning: which things sit inside which; which arrows only point one way;
which element is bigger because it matters more.

## Shape meaning

| What it represents | Shape | Why |
|---|---|---|
| A label, a short description | no shape — free-floating text | typography alone is enough |
| A module, service, or component | rectangle | a contained unit of code |
| An entry point or a terminal output | ellipse | origin/destination, softer than a box |
| A branch point (a router, a dispatcher) | diamond | the classic decision symbol |
| A shared or cross-cutting concern | overlapping ellipses | fuzzy, spans multiple things |
| A step in a sequence or pipeline | small ellipse (10-20px) on a line | a marker, not a container |

Default to no shape at all. Add one only when it earns its place — most of
a good diagram's text should be free-floating labels next to lines and
arrows, not boxed. Aim for under a third of your text elements living
inside a container.

## Layout principles

- **Scale means importance.** The component that matters most in the
  argument should be visibly larger than supporting ones — roughly:
  hero ~300×150, primary ~180×90, secondary ~120×60.
- **Whitespace means importance too.** Give the most important element the
  most empty space around it; a cramped hero reads as minor.
- **Direction is left-to-right or top-to-bottom for sequences**, and radial
  for hub-and-spoke shapes (a core with satellite plugins, for instance).
- **Every relationship needs a line.** Two boxes sitting near each other
  implies nothing on its own — if a dependency, a call, or a data flow
  exists between them, draw it.
- **Dependency arrows are one-directional, always.** Even when two modules
  reference each other's types, decide which direction actually matters
  for the argument you're making and draw only that one. A double-headed
  arrow between two boxes says nothing about which one depends on the
  other, which is usually the entire point of an architecture diagram.

## Visual patterns and when a codebase calls for each

| Pattern | Looks like | Use for |
|---|---|---|
| **Layers** | stacked horizontal (or vertical) bands, arrows crossing only in the allowed direction | a codebase with an enforced dependency direction between layers |
| **Fan-out** | one central shape, arrows radiating out | a small core dispatching to independent, mutually-unaware plugins or handlers |
| **Timeline** | a line with markers and labels beside each one | a pipeline — data or a request moving through ordered stages |
| **Tree** | a trunk line with branch lines, free-floating labels, no boxes | a directory or module hierarchy with real parent-child structure |
| **Convergence** | several inputs merging into one shape | multiple sources feeding a single aggregator, cache, or build step |
| **Mirrored pair** | two parallel timelines or trees, connected at the point they share | two subsystems that share one step and otherwise diverge |

Pick exactly one pattern per diagram. Mixing several is usually a sign the
Step 2 argument wasn't actually narrowed down to one fact.

## Color

Every color comes from `color-palette.md` — never invent one inline. Colors
encode meaning (what kind of thing this is), not decoration.

## The render → view → fix loop

You cannot judge a diagram from its JSON — always render it and look.

1. **Render** with `render_excalidraw.py`, then **read the PNG**.
2. **Check it against the argument.** Does the shape alone say what Step 2
   named? Is the eye led through it in the order you intended?
3. **Check for defects**: clipped or overlapping text, arrows crossing
   through unrelated shapes, uneven spacing, a hero element that isn't
   visually dominant, a composition that's lopsided.
4. **Fix and re-render.** Widen a box if text clips; adjust coordinates for
   spacing; add a waypoint to an arrow's `points` array to route it around
   something in the way.
5. **Stop** once the diagram passes both checks and you'd show it to
   someone without a caveat. Two to four passes is typical for a first
   diagram of a new codebase; don't stop at pass one just because nothing
   is obviously broken — check whether the composition could be tighter.

## Technical defaults

- `roughness: 0` (clean, not hand-drawn), `opacity: 100` on every element
  (use color/size for hierarchy, not transparency)
- `fontFamily: 3`, `fontSize: 16` for most labels, larger for the title
- Every `text` element's `text` field holds only the words a human reads —
  no markup, no citation syntax, nothing that only resolves in a chat UI
```

- [ ] **Step 2: Write `color-palette.md`**

```markdown
# Color Palette

Single source of truth for every color used in a codebase-schematic
diagram. Swap these values to match your own brand; nothing else in this
skill needs to change.

## Shape colors (semantic)

| Purpose | Fill | Stroke |
|---|---|---|
| Core / primary component | `#dbeafe` | `#1d4ed8` |
| Secondary component | `#e0e7ff` | `#4338ca` |
| Entry point / trigger | `#fef3c7` | `#b45309` |
| Terminal output / result | `#dcfce7` | `#15803d` |
| Shared / cross-cutting concern | `#f3e8ff` | `#7e22ce` |
| External dependency (outside this codebase) | `#f1f5f9` | `#64748b` (dashed stroke) |

Always pair a light fill with a noticeably darker stroke of the same hue
family — that contrast is what makes a shape read clearly against the
white background.

## Text colors (hierarchy)

| Level | Color | Use for |
|---|---|---|
| Title | `#1e3a8a` | the diagram's title |
| Subtitle | `#1d4ed8` | the one-line argument statement under the title |
| Label | `#334155` | component names, phase names |
| Annotation | `#64748b` | supporting detail, captions, footnotes |

## Lines

| Element | Color |
|---|---|
| Structural lines (timelines, tree trunks/branches) | `#334155` |
| A connector marking two things as "the same" across the diagram | `#64748b`, dashed |
| Dependency arrows | match the stroke color of the component the arrow originates from |

## Background

Canvas background: `#ffffff`, always — this skill's diagrams are meant to
sit cleanly in a README or a chat, not float on a dark canvas.
```

- [ ] **Step 3: Write `element-templates.md`**

```markdown
# Element Templates

Minimal, copy-pasteable JSON for each Excalidraw element type this skill
uses. Pull `strokeColor`/`backgroundColor` from `color-palette.md` based on
the element's semantic purpose — the placeholders below are just examples.

Every element needs these common fields regardless of type: `id` (a
descriptive string, not a random one — `"core_rect"` not `"el1"`),
`roughness: 0`, `opacity: 100`, `angle: 0`, a unique `seed` and
`versionNonce`, `version: 1`, `isDeleted: false`, `groupIds: []`,
`boundElements`, `link: null`, `locked: false`.

## Free-floating text (no container)

```json
{
  "type": "text", "id": "title", "x": 100, "y": 20, "width": 800, "height": 36,
  "text": "The words a human reads, nothing else",
  "originalText": "The words a human reads, nothing else",
  "fontSize": 28, "fontFamily": 3, "textAlign": "left", "verticalAlign": "top",
  "strokeColor": "#1e3a8a", "backgroundColor": "transparent", "fillStyle": "solid",
  "strokeWidth": 1, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1001, "version": 1, "versionNonce": 2001, "isDeleted": false,
  "groupIds": [], "boundElements": null, "link": null, "locked": false, "lineHeight": 1.25
}
```

## Rectangle (a component)

```json
{
  "type": "rectangle", "id": "core_rect", "x": 100, "y": 100, "width": 180, "height": 90,
  "strokeColor": "#1d4ed8", "backgroundColor": "#dbeafe", "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1002, "version": 1, "versionNonce": 2002, "isDeleted": false,
  "groupIds": [], "boundElements": [{"id": "core_label", "type": "text"}],
  "link": null, "locked": false, "roundness": {"type": 3}
}
```

## Small marker dot (a step on a timeline)

```json
{
  "type": "ellipse", "id": "step_0", "x": 138, "y": 238, "width": 16, "height": 16,
  "strokeColor": "#1d4ed8", "backgroundColor": "#dbeafe", "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1003, "version": 1, "versionNonce": 2003, "isDeleted": false,
  "groupIds": [], "boundElements": null, "link": null, "locked": false
}
```

## Structural line (a timeline spine, a tree trunk)

```json
{
  "type": "line", "id": "spine", "x": 150, "y": 250, "width": 1600, "height": 0,
  "strokeColor": "#334155", "backgroundColor": "transparent", "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1004, "version": 1, "versionNonce": 2004, "isDeleted": false,
  "groupIds": [], "boundElements": null, "link": null, "locked": false,
  "points": [[0, 0], [1600, 0]]
}
```

## Dependency arrow (one-directional, always)

```json
{
  "type": "arrow", "id": "core_to_plugin_a", "x": 280, "y": 145, "width": 120, "height": 0,
  "strokeColor": "#1d4ed8", "backgroundColor": "transparent", "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1005, "version": 1, "versionNonce": 2005, "isDeleted": false,
  "groupIds": [], "boundElements": null, "link": null, "locked": false,
  "points": [[0, 0], [120, 0]],
  "startBinding": null, "endBinding": null,
  "startArrowhead": null, "endArrowhead": "triangle"
}
```

Never set both `startArrowhead` and `endArrowhead` on a dependency arrow —
that draws it as bidirectional, which this skill's methodology explicitly
rules out.

## Top-level document

```json
{
  "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
  "elements": [ ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 },
  "files": {}
}
```
```

- [ ] **Step 4: Commit**

```bash
mkdir -p skills/codebase-schematic/references
git add skills/codebase-schematic/references/design-methodology.md skills/codebase-schematic/references/color-palette.md skills/codebase-schematic/references/element-templates.md
git commit -m "Add design methodology, color palette, and element template references"
```

---

### Task 4: Render pipeline (`render_excalidraw.py`, `render_template.html`, `pyproject.toml`)

**Files:**
- Create: `skills/codebase-schematic/references/render_excalidraw.py`
- Create: `skills/codebase-schematic/references/render_template.html`
- Create: `skills/codebase-schematic/references/pyproject.toml`
- Create: `skills/codebase-schematic/references/test_render_excalidraw.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `compute_bounding_box(elements: list[dict]) -> tuple[float, float, float, float]`
  - `validate_excalidraw(data: dict) -> list[str]`
  - `render(excalidraw_path: Path, output_path: Path | None, scale: int, max_width: int) -> Path`
  - a CLI: `python render_excalidraw.py <path-to-file.excalidraw> [--output PATH] [--scale N] [--width N]`
  - Task 5's validator reads `render_template.html`'s text (checks for the absence of `?bundle`)
  - Task 6 (and every future use of the skill) calls the CLI

- [ ] **Step 1: Write the failing tests for `compute_bounding_box`**

Create `skills/codebase-schematic/references/test_render_excalidraw.py`:

```python
from render_excalidraw import compute_bounding_box, validate_excalidraw


def test_compute_bounding_box_positive_size():
    elements = [{"x": 100, "y": 100, "width": 50, "height": 30, "type": "rectangle"}]
    assert compute_bounding_box(elements) == (100, 100, 150, 130)


def test_compute_bounding_box_negative_size():
    # A rectangle dragged up-and-left has negative width/height in Excalidraw.
    # The visible region is x:[100,200], y:[150,200] — the bbox must land there,
    # not on the opposite side of the anchor point.
    elements = [{"x": 200, "y": 200, "width": -100, "height": -50, "type": "rectangle"}]
    assert compute_bounding_box(elements) == (100, 150, 200, 200)


def test_compute_bounding_box_arrow_uses_points():
    elements = [{"x": 0, "y": 0, "type": "arrow", "points": [[0, 0], [50, 20]]}]
    assert compute_bounding_box(elements) == (0, 0, 50, 20)


def test_compute_bounding_box_empty_elements_returns_default():
    assert compute_bounding_box([]) == (0, 0, 800, 600)


def test_compute_bounding_box_skips_deleted_elements():
    elements = [{"x": 0, "y": 0, "width": 10, "height": 10, "isDeleted": True}]
    assert compute_bounding_box(elements) == (0, 0, 800, 600)


def test_validate_excalidraw_accepts_well_formed_document():
    data = {"type": "excalidraw", "elements": [{"type": "rectangle"}]}
    assert validate_excalidraw(data) == []


def test_validate_excalidraw_rejects_empty_elements():
    data = {"type": "excalidraw", "elements": []}
    errors = validate_excalidraw(data)
    assert len(errors) == 1
    assert "empty" in errors[0]


def test_validate_excalidraw_rejects_missing_elements_key():
    data = {"type": "excalidraw"}
    errors = validate_excalidraw(data)
    assert any("elements" in e for e in errors)
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `cd skills/codebase-schematic/references && uv run pytest test_render_excalidraw.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'render_excalidraw'` (the module doesn't exist yet)

- [ ] **Step 3: Write `pyproject.toml`**

```toml
[project]
name = "codebase-schematic-render"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "playwright>=1.40.0",
]

[dependency-groups]
dev = ["pytest>=8.0.0"]
```

- [ ] **Step 4: Write `render_excalidraw.py`**

```python
#!/usr/bin/env python3
"""Render an Excalidraw JSON file to a PNG screenshot.

Loads the diagram in a headless Chromium page (via Playwright), calls
Excalidraw's own exportToSvg() to produce the real rendering, then
screenshots the resulting SVG element. This is a rendering step, not a
layout engine of our own — Excalidraw does the layout; we just capture it.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_TOP_LEVEL_KEYS = ("type", "elements")


def validate_excalidraw(data: dict) -> list[str]:
    """Return human-readable problems with an Excalidraw document.

    An empty list means the document is well-formed enough to attempt a render.
    """
    errors: list[str] = []
    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in data:
            errors.append(f"missing top-level '{key}' key")

    elements = data.get("elements")
    if elements is not None:
        if not isinstance(elements, list):
            errors.append("'elements' must be a list")
        elif len(elements) == 0:
            errors.append("'elements' is empty — nothing to render")

    return errors


def compute_bounding_box(elements: list[dict]) -> tuple[float, float, float, float]:
    """Compute (min_x, min_y, max_x, max_y) across all non-deleted elements.

    Width/height can be negative in Excalidraw (the user dragged up-left
    instead of down-right), so every corner is compared against every other
    corner rather than assuming (x, y) is the top-left corner.
    """
    min_x = min_y = float("inf")
    max_x = max_y = float("-inf")

    for element in elements:
        if element.get("isDeleted"):
            continue

        x = element.get("x", 0)
        y = element.get("y", 0)

        if element.get("type") in ("arrow", "line") and "points" in element:
            corners = [(x + px, y + py) for px, py in element["points"]]
        else:
            w = element.get("width", 0)
            h = element.get("height", 0)
            corners = [(x, y), (x + w, y + h)]

        for corner_x, corner_y in corners:
            min_x, max_x = min(min_x, corner_x), max(max_x, corner_x)
            min_y, max_y = min(min_y, corner_y), max(max_y, corner_y)

    if min_x == float("inf"):
        return (0, 0, 800, 600)

    return (min_x, min_y, max_x, max_y)


def render(
    excalidraw_path: Path,
    output_path: Path | None = None,
    scale: int = 2,
    max_width: int = 1920,
) -> Path:
    """Render an .excalidraw file to PNG. Returns the output PNG path."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        print(
            "Run: cd skills/codebase-schematic/references && uv sync && uv run playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    raw = excalidraw_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: invalid JSON in {excalidraw_path}: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_excalidraw(data)
    if errors:
        print("ERROR: invalid Excalidraw document:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    elements = [e for e in data["elements"] if not e.get("isDeleted")]
    min_x, min_y, max_x, max_y = compute_bounding_box(elements)
    padding = 80
    viewport_width = min(int(max_x - min_x + padding * 2), max_width)
    viewport_height = max(int(max_y - min_y + padding * 2), 600)

    if output_path is None:
        output_path = excalidraw_path.with_suffix(".png")

    template_path = Path(__file__).parent / "render_template.html"
    if not template_path.exists():
        print(f"ERROR: template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
        except Exception as e:
            if "Executable doesn't exist" in str(e):
                print("ERROR: Chromium not installed for Playwright.", file=sys.stderr)
                print(
                    "Run: cd skills/codebase-schematic/references && uv run playwright install chromium",
                    file=sys.stderr,
                )
                sys.exit(1)
            raise

        page = browser.new_page(
            viewport={"width": viewport_width, "height": viewport_height},
            device_scale_factor=scale,
        )
        page.goto(template_path.as_uri())
        page.wait_for_function("window.__moduleReady === true", timeout=30000)

        result = page.evaluate(f"window.renderDiagram({json.dumps(data)})")
        if not result or not result.get("success"):
            error = result.get("error", "unknown render error") if result else "renderDiagram returned null"
            print(f"ERROR: render failed: {error}", file=sys.stderr)
            browser.close()
            sys.exit(1)

        page.wait_for_function("window.__renderComplete === true", timeout=15000)

        svg = page.query_selector("#root svg")
        if svg is None:
            print("ERROR: no SVG element found after render.", file=sys.stderr)
            browser.close()
            sys.exit(1)

        svg.screenshot(path=str(output_path))
        browser.close()

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render an .excalidraw file to PNG")
    parser.add_argument("input", type=Path, help="path to the .excalidraw JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None)
    parser.add_argument("--scale", "-s", type=int, default=2)
    parser.add_argument("--width", "-w", type=int, default=1920)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    png_path = render(args.input, args.output, args.scale, args.width)
    print(str(png_path))


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `cd skills/codebase-schematic/references && uv run pytest test_render_excalidraw.py -v`
Expected: PASS — all 8 tests green

- [ ] **Step 6: Write `render_template.html`**

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #ffffff; overflow: hidden; }
    #root { display: inline-block; }
    #root svg { display: block; }
  </style>
</head>
<body>
  <div id="root"></div>
  <script type="module">
    import { exportToSvg } from "https://esm.sh/@excalidraw/excalidraw";

    window.renderDiagram = async function (diagram) {
      try {
        const data = typeof diagram === "string" ? JSON.parse(diagram) : diagram;
        const appState = {
          ...(data.appState || {}),
          viewBackgroundColor: (data.appState && data.appState.viewBackgroundColor) || "#ffffff",
          exportWithDarkMode: false,
          exportBackground: true,
        };

        const svg = await exportToSvg({
          elements: data.elements || [],
          appState,
          files: data.files || {},
        });

        const root = document.getElementById("root");
        root.innerHTML = "";
        root.appendChild(svg);

        window.__renderComplete = true;
        window.__renderError = null;
        return { success: true };
      } catch (err) {
        window.__renderComplete = true;
        window.__renderError = err.message;
        return { success: false, error: err.message };
      }
    };

    window.__moduleReady = true;
  </script>
</body>
</html>
```

**This import line is load-bearing: do not append `?bundle`.** That query
parameter has produced a broken transitive dependency path (a 404 on a
`@braintree/sanitize-url` sub-path) when tested directly — the plain
package import works because it resolves each module individually instead
of through esm.sh's bundler.

- [ ] **Step 7: Set up the render environment**

```bash
cd skills/codebase-schematic/references
uv sync
uv run playwright install chromium
```

- [ ] **Step 8: Smoke-test the full pipeline end to end**

Create a throwaway fixture and render it:

```bash
cd skills/codebase-schematic/references
cat > /tmp/smoke.excalidraw << 'EOF'
{
  "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
  "elements": [
    {"type": "rectangle", "id": "r1", "x": 100, "y": 100, "width": 180, "height": 90,
     "strokeColor": "#1d4ed8", "backgroundColor": "#dbeafe", "fillStyle": "solid",
     "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
     "seed": 1, "version": 1, "versionNonce": 1, "isDeleted": false,
     "groupIds": [], "boundElements": null, "link": null, "locked": false}
  ],
  "appState": {"viewBackgroundColor": "#ffffff", "gridSize": 20},
  "files": {}
}
EOF
uv run python render_excalidraw.py /tmp/smoke.excalidraw
```

Expected: prints `/tmp/smoke.png` with exit code 0. Read the PNG with the
Read tool and confirm it shows a single blue-outlined rectangle on a white
background. Delete the fixture afterward: `rm /tmp/smoke.excalidraw /tmp/smoke.png`.

- [ ] **Step 9: Commit**

```bash
git add skills/codebase-schematic/references/render_excalidraw.py \
        skills/codebase-schematic/references/render_template.html \
        skills/codebase-schematic/references/pyproject.toml \
        skills/codebase-schematic/references/test_render_excalidraw.py \
        skills/codebase-schematic/references/uv.lock
git commit -m "Add render pipeline: render_excalidraw.py, render_template.html, tests"
```

`.gitignore` was already created in Task 1, so `.venv/` and `uv.lock`'s
adjacent caches from `uv sync` won't be picked up by the `git add` above —
confirm with `git status --short` before committing if anything unexpected
shows up.

---

### Task 5: `tests/validate_plugin.py`

**Files:**
- Create: `tests/validate_plugin.py`

**Interfaces:**
- Consumes: `skills/codebase-schematic/SKILL.md` (Task 2), `skills/codebase-schematic/references/render_template.html` (Task 4)
- Produces: an executable validator, exit code 0 (pass) or 1 (fail), used by Task 7's CI workflow

- [ ] **Step 1: Write `tests/validate_plugin.py`**

```python
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
```

- [ ] **Step 2: Run it against the real repo**

Run: `python3 tests/validate_plugin.py`
Expected: `codebase-schematic: 0 errors`, exit code 0

- [ ] **Step 3: Confirm the regression guard actually catches the bug**

```bash
cp skills/codebase-schematic/references/render_template.html /tmp/render_template_bad.html
sed -i.bak 's|@excalidraw/excalidraw"|@excalidraw/excalidraw?bundle"|' /tmp/render_template_bad.html
python3 -c "
import sys
sys.path.insert(0, 'tests')
from validate_plugin import RENDER_TEMPLATE
text = open('/tmp/render_template_bad.html').read()
assert '?bundle' in text
print('regression guard would catch this: OK')
"
rm /tmp/render_template_bad.html /tmp/render_template_bad.html.bak
```

Expected: `regression guard would catch this: OK`

- [ ] **Step 4: Commit**

```bash
mkdir -p tests
git add tests/validate_plugin.py
git commit -m "Add tests/validate_plugin.py with the esm.sh ?bundle regression guard"
```

---

### Task 6: `examples/self` — a real schematic of this repo's own structure

**Files:**
- Create: `examples/self/codebase-schematic.excalidraw`
- Create: `examples/self/codebase-schematic.png` (generated, not hand-written)
- Create: `examples/self/README.md`

**Interfaces:**
- Consumes: `skills/codebase-schematic/references/render_excalidraw.py` (Task 4), `design-methodology.md` / `color-palette.md` / `element-templates.md` (Task 3)
- Produces: the fixture Task 7's CI smoke test renders on every push

This is the one task in this plan that is inherently a design task, not a
scripted one — per `design-methodology.md`, you cannot know if a diagram is
right until you've rendered and looked at it. The steps below give you the
argument to draw and the exact commands to run; the JSON layout itself is
produced live, through the render → view → fix loop, not pre-written here.

- [ ] **Step 1: Apply Step 2 of the skill to this repo**

The argument this diagram should make (already true of the repo as built
by Tasks 1-5): **one thin `SKILL.md` that, on demand, pulls in three
reference docs for design guidance and shells out to a separate two-file
render pipeline — validated by a test and a CI smoke test that actually
renders something on every push.** That's a fan-out pattern (SKILL.md at
the center, references as satellites) plus a distinct "render pipeline"
component it calls out to as a subprocess, plus a small validation loop
annotation.

- [ ] **Step 2: Draft the `.excalidraw` JSON**

Following `element-templates.md` and `color-palette.md`, build:
- A title + one-line subtitle stating the argument from Step 1
- A "core" rectangle for `SKILL.md` (core/primary color)
- Three smaller rectangles fanning out from it for the three
  `references/*.md` docs (secondary color), one-directional arrows from
  `SKILL.md` to each
- A separate rectangle for the render pipeline (`render_excalidraw.py` +
  `render_template.html`), with a one-directional arrow from `SKILL.md`
  to it labeled with the actual shell command it runs
- A small annotation (dashed line + label) connecting `tests/validate_plugin.py`
  and the CI workflow to the render pipeline, showing the validation loop

Save as `examples/self/codebase-schematic.excalidraw`.

- [ ] **Step 3: Render it**

```bash
cd skills/codebase-schematic/references
uv run python render_excalidraw.py ../../../examples/self/codebase-schematic.excalidraw
```

- [ ] **Step 4: View and audit**

Read `examples/self/codebase-schematic.png` with the Read tool. Check
against `design-methodology.md`'s render-view-fix checklist: does the
fan-out read clearly, is the render-pipeline box visually distinct from
the reference docs, is anything clipped or overlapping, is the dependency
arrow direction correct (SKILL.md → references and SKILL.md → render
pipeline, never the reverse)?

- [ ] **Step 5: Fix and re-render until clean**

Repeat Steps 3-4, adjusting the JSON, until the diagram needs no caveats.

- [ ] **Step 6: Write `examples/self/README.md`**

```markdown
# Demo — Diagramming this repo's own structure

**Prompt**

> Diagram this codebase's architecture.

**Which skill fires:** `codebase-schematic`

**The argument this diagram makes:** one thin `SKILL.md` that, on demand,
pulls in three reference docs for design guidance and shells out to a
separate two-file render pipeline — validated by a test and a CI smoke
test that actually renders something on every push.

**What to check in the output**
- [ ] The diagram states one specific structural fact, not a generic file listing
- [ ] Dependency arrows all point one direction (SKILL.md → its dependencies)
- [ ] The render pipeline reads as a visually distinct component, not just
      another reference doc
- [ ] No clipped or overlapping text, arrows land on the intended shapes

![Schematic of codebase-schematic's own architecture](codebase-schematic.png)
```

- [ ] **Step 7: Commit**

```bash
git add examples/self/
git commit -m "Add examples/self: a rendered schematic of this repo's own architecture"
```

---

### Task 7: CI workflow

**Files:**
- Create: `.github/workflows/validate.yml`

**Interfaces:**
- Consumes: `tests/validate_plugin.py` (Task 5), `skills/codebase-schematic/references/{render_excalidraw.py,pyproject.toml}` (Task 4), `examples/self/codebase-schematic.excalidraw` (Task 6)
- Produces: two CI jobs that run on every push/PR

- [ ] **Step 1: Write `.github/workflows/validate.yml`**

```yaml
name: validate
on: [push, pull_request]
jobs:
  validate-plugin:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: python3 tests/validate_plugin.py

  render-smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - name: Install render pipeline dependencies
        working-directory: skills/codebase-schematic/references
        run: |
          uv sync
          uv run playwright install --with-deps chromium
      - name: Render the example diagram
        working-directory: skills/codebase-schematic/references
        run: |
          uv run python render_excalidraw.py ../../../examples/self/codebase-schematic.excalidraw
      - name: Verify the PNG was produced
        run: test -f examples/self/codebase-schematic.png
```

This is exactly the check that would have caught the `?bundle` breakage
automatically instead of it being found by hand: `render-smoke-test`
exercises the real network call to esm.sh and the real Playwright render
on every push, not just the static text-match in `validate_plugin.py`.

- [ ] **Step 2: Commit**

```bash
mkdir -p .github/workflows
git add .github/workflows/validate.yml
git commit -m "Add CI: plugin validation + a full render smoke test"
```

---

### Task 8: Install, verify, and push

**Files:** none created — this task exercises the whole repo built by Tasks 1-7.

**Interfaces:**
- Consumes: the entire repo
- Produces: an installed, enabled plugin in the local Claude Code environment, and a pushed `main` branch on GitHub

- [ ] **Step 1: Final local validation**

```bash
python3 tests/validate_plugin.py
claude plugin validate .
```

Expected: both pass with 0 errors.

- [ ] **Step 2: Install as a plugin**

```bash
claude plugin marketplace add /Users/qiyanjun/Downloads/27-business/codebase-schematic
claude plugin install codebase-schematic@codebase-schematic -y
```

- [ ] **Step 3: Verify the install**

```bash
claude plugin list
claude plugin details codebase-schematic@codebase-schematic
```

Expected: `codebase-schematic@codebase-schematic` listed as enabled, with
`Skills (1)  codebase-schematic` in the component inventory.

- [ ] **Step 4: Push to GitHub**

```bash
git push origin main
```

- [ ] **Step 5: Verify a fresh clone installs cleanly too**

This repeats the exact verification done for `strategy-stack-skills` —
confirms the documented install flow works for someone with zero prior
state, not just against the already-set-up dev directory.

```bash
claude plugin uninstall codebase-schematic@codebase-schematic
claude plugin marketplace remove codebase-schematic
rm -rf /tmp/codebase-schematic-fresh-test
git clone https://github.com/qiyanjun/codebase-schematic.git /tmp/codebase-schematic-fresh-test
claude plugin marketplace add /tmp/codebase-schematic-fresh-test
claude plugin install codebase-schematic@codebase-schematic -y
claude plugin list
```

Expected: installs and shows enabled, identical to Step 3.

- [ ] **Step 6: Restore the permanent install and clean up**

```bash
claude plugin uninstall codebase-schematic@codebase-schematic
claude plugin marketplace remove codebase-schematic
claude plugin marketplace add /Users/qiyanjun/Downloads/27-business/codebase-schematic
claude plugin install codebase-schematic@codebase-schematic -y
rm -rf /tmp/codebase-schematic-fresh-test
```

No commit in this task — it's verification only, against work already committed and pushed in Tasks 1-7.
