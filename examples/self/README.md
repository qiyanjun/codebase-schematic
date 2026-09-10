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
