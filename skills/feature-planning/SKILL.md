---
name: feature-planning
description: Scope an ambiguous feature or multi-step change into a concrete implementation plan with invariants, non-goals, riskiest-unknown-first milestones, and verifiable slices before coding. Planning-only unless implementation is also requested.
---

# Plan a feature or multi-step change

Turn an ambiguous request into an actionable, grounded plan before writing production code. A planning request produces a plan; do not start implementing unless the user explicitly authorizes implementation.

## Ground in the existing system

Inspect the relevant codebase entry points, data owners, existing patterns, configuration, and tests before proposing work. Do not design against guessed file paths or assumed abstractions.

Identify:

- **Goal and users:** The concrete problem solved and observable user-visible outcome.
- **Non-goals and boundaries:** What stays explicitly out of scope to prevent drift.
- **Invariants and constraints:** Compatibility requirements, auth/security boundaries, migration constraints, performance budgets, or external API contracts the change must preserve.
- **Open decisions:** Only the missing product or architectural choices that would materially change the plan. Ask concise questions when blocked; otherwise state reasonable assumptions clearly.

## Sequence into verifiable slices

Decompose the work into a short sequence of coherent, independently reviewable units (or stacked PRs):

1. **Tackle the riskiest unknown first** (hard contract, data model, external integration, or concurrency boundary) before building boilerplate around it.
2. **Make each slice leave the repo green:** Name the exact files/modules owned by the slice, its public contract change, and any temporary compatibility bridge needed until a later slice lands.
3. **Define concrete completion evidence per slice:** Specify the exact command, test, or real user-path observation that proves the slice works — never treat compilation or a green linter as feature proof.
4. **Account for rollout and cleanup:** Note feature flags, migrations, docs updates, or obsolete paths to delete once the final slice ships.

## Deliver the plan

Keep the plan concise and scannable:

- **Objective & non-goals**
- **Grounded context** (actual files, owners, and constraints)
- **Key decisions & assumptions**
- **Ordered slices** (scope, touched boundaries, verification proof per slice)
- **Risks & unresolved questions**

Write the plan to a file only when the user or repository convention requests a saved plan artifact; otherwise deliver it directly and wait for approval before implementing.
