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
