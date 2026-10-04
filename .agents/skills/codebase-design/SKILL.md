---
name: codebase-design
description: Design or improve module interfaces when complexity leaks into callers, one change requires scattered edits, or behavior is hard to test through a useful boundary. Use for interface design and focused architecture improvements, following the project's existing vocabulary and constraints.
---

# Codebase design

Hide substantial behavior behind an interface that callers can understand and use correctly. A useful abstraction reduces what callers must know and keeps implementation changes, defects, and verification concentrated in one place.

## Establish the friction

Read the relevant implementation, callers, tests, project terminology, and architectural decisions before proposing a new shape. Follow the user's named scope. For a broader review, prioritize areas with repeated changes or demonstrated navigation and maintenance difficulty.

Look for evidence: callers repeat business rules, one behavior is spread across unrelated files, callers must orchestrate many internal steps, or tests require private details to reach the actual bug. A small file, forwarding function, or large implementation alone is not a design defect.

## Design the contract

An interface includes more than a type signature: invariants, ordering, lifecycle, error behavior, required configuration, and relevant performance expectations are facts callers must know. Make these explicit or hide unnecessary obligations inside the implementation.

Ask:

- What useful behavior does a caller get, and how much must they learn to get it?
- Which decisions can the implementation own instead of every caller repeating them?
- If this abstraction disappeared, would complexity disappear too, or spread across callers?
- Can the likely next change be made and verified in one place?

Prefer a simple common path, but preserve meaningful error handling and legitimate use cases. Fewer methods or parameters do not help if they hide required knowledge. Use the codebase's familiar terms; a service, component, function, or package can all provide a useful interface.

For consequential interface choices, compare a small number of materially different designs with usage examples and tradeoffs. Choose based on actual callers and constraints, not hypothetical flexibility. Respect existing decisions; explain concrete evidence when proposing to revisit one.

## Dependencies and verification

Keep pure computation independent of I/O where that makes the behavior clearer. Inject external dependencies when it provides needed control over lifecycle or testing. Introduce an abstraction when a stable contract, deployment boundary, real variation, or distinct risk justifies its cost; avoid wrappers added solely to make everything mockable.

Test observable behavior at the boundary that protects the contract. Use real components where practical and controlled substitutes for external effects. A local database substitute may not reproduce production SQL, transactions, or concurrency; retain separate checks for those risks when relevant.

During a refactor, establish replacement coverage before removing tests. Keep lower-level tests that protect distinct contracts or risks. Avoid adding production methods or exports whose only purpose is test access.

## Propose or implement

A review produces concrete candidates: affected code and callers, observed friction, proposed interface, benefits, tradeoffs, and confidence. Include a before/after sketch when it clarifies ownership or data flow.

When implementation is requested, make the smallest coherent change, preserve compatibility as required, and verify affected callers and behavior. Stay within the authorized scope; a design opportunity does not justify unrelated restructuring.

## Attribution

Adapted from Matt Pocock's `codebase-design` and `DEEPENING.md` at commit `24fe0ef7737efae15c87225755e9f6f5965e4888` (1.3.1). Vocabulary, dependency guidance, and verification rules are maintained locally. The upstream MIT license is included in [LICENSE.txt](LICENSE.txt).
