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
