---
name: deslop-code
description: Clean unnecessary agent-generated code patterns from a specified diff while preserving behavior and local conventions. Use when the user asks to deslop code, simplify a branch, or remove redundant comments, checks, casts, or nesting.
---

# Clean up code

Review the requested files or branch diff against the repository's correct base. Read surrounding code to establish conventions and whether the suspicious pattern actually serves a contract. Keep cleanup focused on the changed code.

## Inspect

- Comments that repeat the code or conflict with local style. Preserve non-obvious rationale, protocol constraints, licenses, and useful public API documentation.
- Defensive checks and try/catch blocks that mask broken invariants or add nothing in a genuinely trusted path. Keep validation and error handling at external boundaries and where callers can violate assumptions.
- `any` casts or equivalent type escapes used only to silence modeling errors. Prefer the real type or an explicit boundary parse without inventing a large type framework.
- Deep nesting that can become clearer with an equivalent early return. Check cleanup/finally behavior and side-effect ordering before changing control flow.
- Pass-through wrappers, duplicate helpers, extra abstractions, and style inconsistent with nearby maintained code, when removing them earns its cost.

## Edit and verify

Apply minimal edits when cleanup is requested; a review-only request produces findings. Preserve public contracts, observable behavior, exceptions, and unrelated user changes. A discovered functional bug needs a clearly stated fix within the authorized scope, not a silent change disguised as style cleanup.

Inspect the resulting diff and run the relevant existing checks. For control-flow or error-path changes, verify the affected behavior rather than relying only on formatting. Do not add tests that just mirror the cleanup.

Report what was simplified and how behavior was checked in a short summary. Leave justified defensive code and comments intact.

## Attribution

Adapted from Cursor Team Kit's `deslop`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, renamed `deslop-code`. See [LICENSE.txt](LICENSE.txt).
