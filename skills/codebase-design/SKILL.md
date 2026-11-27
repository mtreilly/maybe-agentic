---
name: codebase-design
description: Design types, module interfaces, ownership, and boundaries before substantial implementation, or improve existing modules when complexity leaks into callers, one change requires scattered edits, or behavior is hard to test through a useful boundary.
---

# Codebase design

Hide substantial behavior behind an interface that callers can understand and use correctly. A useful abstraction reduces what callers must know and keeps implementation changes, defects, and verification concentrated in one place.

## Ground the design

Read the relevant entry points, implementation, callers, tests, state ownership, lifecycle, project terminology, and architectural decisions before proposing a new shape. Follow the user's named scope. A file inventory is not an architecture model.

For new work, name the domain data shape and invariants before writing orchestration. For existing code, look for demonstrated friction: callers repeat business rules, one behavior is spread across unrelated files, callers orchestrate many internal steps, or tests require private details to reach the actual bug. A small file, forwarding function, or large implementation alone is not a design defect.

## Design and compare shapes

Write plausible consumer call sites first, then derive types, signatures, responsibilities, and a module sketch. Avoid shipping stubs into working code merely to illustrate a design; put illustrative sketches in the design artifact unless implementation scaffolding is authorized.

An interface includes more than a type signature: invariants, ordering, lifecycle, error behavior, required configuration, and performance expectations are facts callers must know. Make these explicit or hide unnecessary obligations inside the implementation.

Ask:

- What useful behavior does a caller get, and how much must they learn to get it?
- Which decisions can the implementation own instead of every caller repeating them?
- If this abstraction disappeared, would complexity disappear too, or spread across callers?
- Can the likely next change be made and verified in one place?

Where there is a consequential fork, compare a small number of structurally distinct candidates with realistic usage examples and tradeoffs. Screen candidates against [references/design-red-flags.md](references/design-red-flags.md). Prefer clear ownership, small useful interfaces, unreachable internals, and one authoritative representation. Do not equate a long call chain with a deep module.

## Dependencies and verification

Keep pure computation independent of I/O where that makes the behavior clearer. Inject external dependencies when it provides needed control over lifecycle or testing. Introduce an abstraction when a stable contract, deployment boundary, real variation, or distinct risk justifies its cost; avoid wrappers added solely to make everything mockable.

Test observable behavior at the boundary that protects the contract. Use real components where practical and controlled substitutes for external effects. A local database substitute may not reproduce production SQL, transactions, or concurrency; retain separate checks for those risks when relevant.

During an improvement, establish replacement coverage before removing tests. Keep lower-level tests that protect distinct contracts or risks. Avoid adding production methods or exports whose only purpose is test access.

## Propose, implement, or revisit

For a design checkpoint or review, state the chosen shape, consumer usage, core types, ownership boundaries, accepted tradeoffs, rejected alternatives, open questions, and the next concrete step. Include why the design fits the constraints, not only what it looks like. Stop there unless implementation is included in the request.

When implementation is requested, make the smallest coherent change, preserve compatibility as required, and verify affected callers and behavior. Stay within the authorized scope; a design opportunity does not justify unrelated restructuring.

If implementation contradicts the design — repeated special cases, casts, duplicated owners, caller knowledge of internals, or the same workaround in unrelated places — re-ground the problem and make a coherent correction instead of accumulating escape hatches. One edge case alone does not condemn the architecture.

## Attribution

Adapted from Matt Pocock's `codebase-design` and `DEEPENING.md` at commit `24fe0ef7737efae15c87225755e9f6f5965e4888` (1.3.1, [LICENSE.txt](LICENSE.txt)) and Lauren Tan's pstack `architect` at commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a` ([LICENSE.pstack.txt](LICENSE.pstack.txt)). Vocabulary, design red flags, dependency guidance, and verification rules are maintained locally.
