---
name: correct
description: Prevent recurring agent or contributor mistakes by changing architecture, types, checks, or automation. Use when the user asks to correct a repeated failure pattern or make an established repository rule enforceable.
---

# Correct recurring mistakes

Make an evidenced recurring mistake harder to repeat. A typo or one-time correction is not a mandate for a repository-wide rule.

## Establish the pattern

Read the relevant corrections, commits, reverts, reviews, and existing instructions. Group incidents by mechanism. Cite actual examples; two independent occurrences are a useful signal, while a stated recurring problem may already establish intent. If no repeated pattern is supported, fix or report the local issue without inventing a universal constraint.

Assume contributors often copy the nearest example and inspect only part of the repository. Prefer designs in which a locally reasonable edit preserves global invariants.

## Choose the strongest proportionate fix

- **Architecture:** give state a clear owner, expose one supported path, hide internals, or derive hand-synced lists from one source. Respect public compatibility requirements.
- **Types:** make invalid combinations unrepresentable and parse external data at boundaries.
- **Lint, build, or automation:** reject the recurring pattern with a diagnostic naming the supported alternative. For widespread existing violations, a check that prevents new violations can be a practical migration step.
- **Behavioral verification:** assert the observable contract through an existing executable path. Avoid checks that only reproduce implementation details.
- **Instructions:** document decisions needing judgment when a structural mechanism cannot express the rule.

Choose the smallest intervention that actually prevents the class. Do not add all five layers for every correction. Prove a new check rejects a real past failure and accepts a valid case. Run it through the actual local command and inspect the CI integration if CI changes are in scope.

## Preserve and report

Keep unrelated edits, user changes, and authorized exceptions intact. If updating agent instructions, pair each retained rule with its enforcing mechanism where one exists. Remove redundant reminders only when the structural guarantee is established.

Report the mistake class and evidence, chosen mechanism, why a stronger intervention was unnecessary or unavailable, failing/passing proof, and remaining gaps. Commit, open a PR, or change policy only when included in the requested work.

## Attribution

Adapted from Lauren Tan's pstack `correct`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. See [LICENSE.txt](LICENSE.txt).
