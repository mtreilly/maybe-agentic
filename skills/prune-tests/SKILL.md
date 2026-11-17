---
name: prune-tests
description: Prune or rewrite low-value tests while preserving regression coverage. Use when asked to trim an existing suite or remove redundant tests.
---

# Prune tests

Use `$prune-tests [optional path]` to review tests in the requested scope. Run the affected tests before editing so you can recognize existing failures.

For each candidate, ask **what plausible production change would break intended behavior and make this test fail?** Trace the inputs, execution path, and assertions. Check which behavior a caller relies on, including forbidden outcomes and observable side effects.

- **Keep** a test that catches a distinct regression. A retired endpoint may still have a contract to reject requests. If the contract or the overlap with other tests is unclear, keep the test.
- **Rewrite** a brittle or ineffective assertion when it covers a real requirement. If an “add book” test reads a private array, check the book's identity and quantity through the public cart API. A different book at the same price would also satisfy a total-only assertion. If the expected result comes from the same production helper being exercised, use an independently known result.
- **Delete** a test when it guards no current requirement, or when a surviving test would catch the same regression. Identify that test and check how it obtains its result. For example, a checkout test that receives a precomputed total cannot catch a bug in tax calculation, even if both tests assert the same amount.

Remove a helper or production hook made obsolete by the deletion only after checking remaining uses, including setup, teardown, and public consumers.

Rerun the affected tests. For each deletion, name the surviving test that covers the regression or explain why the deleted test guarded no current requirement. Report what ran and any failures.
