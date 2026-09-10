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
