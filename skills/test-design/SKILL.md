---
name: test-design
description: Design and write high-signal behavioral tests for new features, bug fixes, or uncovered contracts. Use when planning test strategy or adding coverage; to remove or rewrite redundant tests in an existing suite, use prune-tests.
---

# Design high-signal tests

Write the smallest set of tests that would catch real regressions at the boundary callers actually depend on. Coverage percentage and test count are not quality goals.

## Choose the boundary and contract

Inspect the code under test, its callers, existing test conventions, and available test harnesses first. For every test you plan to add, answer: **what plausible production bug would break intended behavior and make this test fail?**

- Prefer testing observable behavior at the public boundary (HTTP handler, CLI entrypoint, exported module interface, rendered UI interaction) rather than calling private helpers or asserting internal state shapes.
- Test what callers rely on: outputs, persisted state, emitted side effects, error contracts, and forbidden outcomes (such as unauthorized access or invalid inputs being rejected).
- Avoid re-deriving expected values with the same production helper under test; assert independently known results.

## Choose real collaborators versus substitutes

- Use real in-process collaborators by default; do not mock internal modules solely to achieve unit isolation.
- Substitute only at genuine external or nondeterministic boundaries (network APIs, clocks, randomness, email/payment gateways). Keep fakes contract-faithful and explicitly note what they cannot prove (for example, an in-memory store does not prove SQL locks, migrations, or concurrency).
- Do not add production methods, flags, or exports whose sole purpose is test access.

## Cover high-value failure modes

Prioritize cases that actually fail in production over repetitive happy-path variations:

- **Boundaries and edge inputs:** Empty, zero, missing, duplicate, malformed, and out-of-range values.
- **State and ordering:** Retries, idempotency, cancellation, concurrent updates, and stale completions.
- **Error propagation:** Upstream failures, timeouts, and partial failures leave state consistent rather than silently succeeding.
- **Async determinism:** Wait on observable conditions or controlled clocks; never rely on arbitrary sleeps.

## Implement and verify

Keep fixtures minimal, readable, and isolated per test so execution order never matters. Run the new tests and confirm they fail for the intended reason when the guarded behavior is broken (or explain why fault injection was skipped), then confirm the full relevant suite passes cleanly.

Report the contracts covered, chosen boundaries, test commands run, and remaining risks that require integration, live, or manual verification.
