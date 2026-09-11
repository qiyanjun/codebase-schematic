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

Write the `.excalidraw` JSON to a scratch/working location outside the
target codebase — the session's scratchpad directory if the environment
provides one, otherwise a temp directory. Don't create files inside the
repo being diagrammed at this stage; that only happens later, and only if
asked (see Step 5).

## Step 4 — Render, view, and fix (mandatory loop)

```bash
cd ${CLAUDE_PLUGIN_ROOT}/skills/codebase-schematic/references && uv run python render_excalidraw.py <path-to-file.excalidraw>
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
cd ${CLAUDE_PLUGIN_ROOT}/skills/codebase-schematic/references
uv sync
uv run playwright install chromium
```

## Step 5 — Deliver

Send the PNG (and the `.excalidraw` source, if the person might want to
edit it) as a file attachment — do not leave the only copies sitting
uncommitted in the target repo's working tree. Offer — don't assume — to
also embed the PNG in the target repo's README; only write the files into
the repo itself (e.g. under `examples/`) if the person accepts that offer
or otherwise asks for the source to live there.

## Guardrails

- One diagram, one argument. Resist the pull to show everything the
  codebase does — the value is in what gets left out.
- No invented structure. If Step 2 genuinely finds nothing more important
  than anything else, say so and diagram the flattest honest version
  rather than manufacturing a hierarchy.
- No code parser, no dependency-graph extraction tool. The analysis is
  Claude reading the codebase, the same way it would to answer any other
  question about it.
