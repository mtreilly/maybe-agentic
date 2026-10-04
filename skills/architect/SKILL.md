---
name: architect
description: Design types, interfaces, ownership, and module boundaries before a substantial implementation. Use for explicit architecture requests or changes where committing to the first structure would make later behavior difficult to implement or verify.
---

# Design the code's shape

Derive the interface from realistic caller usage and the surrounding system's constraints. The deliverable is a coherent design; implement it only when implementation is included in the request.

## Ground the design

Trace existing entry points, state ownership, lifecycle, and integration boundaries. Inspect history or design records when they explain constraints the new design must preserve. Name the domain data shape and invariants before writing orchestration. A file inventory is not an architecture model.

## Compare shapes

Write plausible consumer call sites first, then derive types, signatures, responsibilities, and a module sketch. Avoid shipping stubs into working code merely to illustrate a design. Put illustrative sketches in the requested design artifact unless implementation scaffolding is authorized.

Where there is a real architectural fork, compare structurally distinct candidates. Evaluate the complexity hidden behind each interface, exposed policy, ownership, compatibility, and verification cost. Independent candidates or reviewers are optional when authorized and worthwhile; a particular model, arena skill, or delegation API is not required.

Screen candidates against [references/design-red-flags.md](references/design-red-flags.md). Prefer clear ownership, small useful interfaces, unreachable internals, and one authoritative representation. Do not equate a long call chain with a deep module.

## Choose and explain

State the chosen shape, consumer usage, core types, ownership boundaries, accepted tradeoffs, rejected alternatives, open questions, and the next concrete implementation step. Include why the design fits the constraints, not only what it looks like. If the user requested a design checkpoint, stop there; otherwise continue only with the already-authorized implementation.

## Revisit when implementation contradicts it

Repeated special cases, casts, duplicated owners, caller knowledge of internals, or the same workaround in unrelated places can indicate the design missed a constraint. One edge case alone does not condemn the architecture. Re-ground the problem, compare the revised shapes, and make a coherent correction instead of accumulating escape hatches. Preserve unrelated work and public compatibility obligations.

## Attribution

Adapted from Lauren Tan's pstack `architect`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. The design red flags are retained; mandatory model panels and cross-skill calls were removed. See [LICENSE.txt](LICENSE.txt).
