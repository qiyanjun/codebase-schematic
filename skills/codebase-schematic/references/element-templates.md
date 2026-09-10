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

## Diamond (a branch point)

Same shape as the Rectangle template above but `"type": "diamond"` — the
classic decision symbol from `design-methodology.md`'s shape-meaning table
(a router or dispatcher). `color-palette.md` has no dedicated "decision"
entry in its shape-colors table, so this uses the Secondary component pair
as a neutral, already-in-palette default.

```json
{
  "type": "diamond", "id": "decision_diamond", "x": 100, "y": 100, "width": 140, "height": 100,
  "strokeColor": "#4338ca", "backgroundColor": "#e0e7ff", "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1006, "version": 1, "versionNonce": 2006, "isDeleted": false,
  "groupIds": [], "boundElements": [{"id": "decision_label", "type": "text"}],
  "link": null, "locked": false, "roundness": {"type": 2}
}
```

## Entry point / terminal output (ellipse)

A larger ellipse marking where the diagram's flow begins or ends — distinct
from the small 16px timeline marker dot above. Use the Entry/Trigger colors
for a starting point; use the Terminal/Output colors instead
(`strokeColor: "#15803d"`, `backgroundColor: "#dcfce7"`) for an ending
point. Sized from the real usage in `examples/self/codebase-schematic.excalidraw`.

```json
{
  "type": "ellipse", "id": "trigger_ellipse", "x": 80, "y": 286, "width": 210, "height": 100,
  "strokeColor": "#b45309", "backgroundColor": "#fef3c7", "fillStyle": "solid",
  "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1007, "version": 1, "versionNonce": 2007, "isDeleted": false,
  "groupIds": [], "boundElements": [{"id": "trigger_label", "type": "text"}],
  "link": null, "locked": false
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

## Dashed stroke (external dependency or a "same thing" connector)

The same line shape as above, but with `"strokeStyle": "dashed"` instead of
`"solid"`. Used for two distinct purposes per `color-palette.md`: marking
an external dependency (outside this codebase), or connecting two elements
that represent the same thing across the diagram — this is a plain
connector, not a dependency arrow, so it carries no arrowhead.

```json
{
  "type": "line", "id": "dashed_same_thing_line", "x": 450, "y": 654, "width": 120, "height": 44,
  "strokeColor": "#64748b", "backgroundColor": "transparent", "fillStyle": "solid",
  "strokeWidth": 1, "strokeStyle": "dashed", "roughness": 0, "opacity": 100, "angle": 0,
  "seed": 1008, "version": 1, "versionNonce": 2008, "isDeleted": false,
  "groupIds": [], "boundElements": null, "link": null, "locked": false,
  "points": [[0, 0], [-120, 44]]
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

Never set both `startArrowhead` and `endArrowhead` to a non-null value on a
dependency arrow — exactly one end should carry an arrowhead. Setting both
to a real arrowhead draws it as bidirectional, which this skill's
methodology explicitly rules out.

## Top-level document

```json
{
  "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
  "elements": [ ],
  "appState": { "viewBackgroundColor": "#ffffff", "gridSize": 20 },
  "files": {}
}
```
