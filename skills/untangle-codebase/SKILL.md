---
name: untangle-codebase
description: Refactor existing code around demonstrated change friction, hidden dependencies, and unclear ownership while preserving observable behaviour. Use for requests to untangle a codebase or refactor across module or workflow boundaries. Bound the work to concrete problems rather than an exhaustive rewrite.
---

# Untangle a codebase

Make a recurring change easier to understand, implement, and verify. Ask whether pieces should change together, then use concrete behaviour and caller needs to justify the structure.

A review request produces findings and proposals. An implementation request carries the scoped changes through verification. Do not turn a request to assess a design into permission to rewrite it.

## Bound the work

Follow the named area and constraints. For a broad request, inspect representative user flows, callers, tests, and architectural decisions. Select a coherent set of problems based on demonstrated maintenance cost or correctness risk. State that scope and what would count as resolving it, then proceed within the existing authorisation.

Use history, dependency graphs, and repeated call-site obligations as evidence when useful. File size, forwarding functions, folder layers, or a dependency's edit frequency alone do not establish a defect. Keep a short decision log for work that spans several changes: evidence, chosen fix, rejected alternatives, and verification. A chat summary suffices for small changes.

Stop when the selected problems are resolved and relevant checks pass. Record worthwhile discoveries outside the boundary without continually expanding the refactor. There is no requirement to find or fix every architectural issue.

## Establish the behaviour to preserve

Trace relevant inputs, state owners, transitions, and effects before changing structure. The boundary includes screens, public interfaces, stored data, external writes, error behaviour, and relevant timing or ordering guarantees. Include internal state that affects future observations.

For lifecycle-heavy code, recover the relevant implicit machines: state, events, guards, effects, and interactions. `find-state-machines` can help if available, but a local sketch may be enough. Determine which operations commute or tolerate repetition, including their external effects. Identify invariants, enforcement, and environmental assumptions.

Distinguish existing behaviour from intended behaviour supported by requirements. Establish a baseline with the relevant existing checks or a focused reproduction. Record pre-existing failures and verification gaps. Do not call a behavioural difference a bug fix solely because the new design seems cleaner.

## Find and choose structural fixes

Look for:

- **Hidden links:** duplicated rules that must agree, distant pieces repeatedly changed together, globals, implicit sequencing, or callers coordinating internal steps.
- **Needless links:** callers depending on private details, general interfaces carrying one workflow's policy, or an implementation choice spreading through unrelated callers.
- **Unclear ownership:** several authoritative copies of one fact, competing transition writers, or effects whose prerequisites nobody owns.
- **Surplus:** genuinely unused code, configuration without supported variation, or wrappers that add neither a useful contract nor an independent responsibility.

Treat each as a candidate, not a verdict. Similar code may represent different rules. Caches, compatibility paths, retries, and boundary adapters can have legitimate responsibilities. Verify consumers before declaring code dead.

For each selected fix, connect the evidence to a smaller caller obligation, clearer owner, or simpler likely change. Prefer one coherent correction over repeated patches when it demonstrably helps. Compare alternatives when the boundary is consequential, including leaving the current design alone. Avoid abstractions justified only by hypothetical reuse or fewer visible branches.

## Implement and check in coherent steps

Preserve required compatibility and move one responsibility at a time where practical. Check affected callers and observable behaviour after each coherent step, rather than postponing verification until the final rewrite.

Use existing checks where they protect the contract. Add focused coverage for a meaningful uncovered risk. For async changes, test relevant event schedules and effects, not just eventual screen state. Keep test coverage during the refactor. Rewrite or remove a test only when its protected risk is understood and replacement coverage or redundancy is established.

Keep comments that explain non-obvious invariants, ordering requirements, or external constraints. Remove misleading or redundant comments when the changed code makes them unnecessary. Neither comment count nor test count is a quality target.

If a structural change reveals a behavioural defect, describe the smallest failing trace found and distinguish the proposed correction from equivalence-preserving work. Implement it only within the user's authorised scope. A failed equivalence check is evidence to investigate, not permission to silently redefine the contract.

## Account for equivalence and finish

Classify consequential changes using the evidence actually available:

| Classification | Evidence to give |
| --- | --- |
| Proven equivalent within a stated scope | Argument or proof, assumptions, observation boundary, and correspondence to the implementation. |
| Supported by checks | Tests, differential runs, or bounded exploration performed, with their limits. |
| Unresolved | The exact assumption or behavioural obligation still lacking evidence. |
| Known behaviour change | A concrete before/after trace, rationale, and authorisation. |

Passing tests or a bounded model is not proof of general implementation equivalence. A counterexample disproves equivalence within its conditions. Not finding one leaves a claim unproven. For unresolved claims, seek a small distinguishing trace and report the search limits rather than inventing a breaking input. Say "smallest found" unless minimality is established.

Resolve required in-scope behaviour and verification gaps before claiming completion. If a gap cannot be resolved with the available access or evidence, report the blocker. Report the problems resolved, why the chosen structure helps, checks and outcomes, and equivalence limits. A finding that no structural change is worthwhile is a valid result.
