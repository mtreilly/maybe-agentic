---
name: systematic-debugging
description: Investigate bugs, failing tests, build failures, flaky behavior, and broken integrations before proposing fixes. Use when observed behavior differs from expectations or previous fixes have failed; for frontend rendering bottlenecks, combine with ui-performance when available.
---

# Systematic debugging

Establish what fails and why, test a specific explanation, and repair the cause with evidence. Scale the investigation to the problem: a clear error may need only a short reproduction and check; an intermittent integration failure needs evidence across component boundaries.

Follow the requested scope. A diagnosis produces findings and proposed fixes; a request to fix includes implementation and verification. Use existing project tools and instructions. This skill requires no particular harness, plugin, or companion skill.

## Establish the failure

- Read the complete relevant error and stack trace. Record the failing command or interaction, expected behavior, actual behavior, and environment.
- Reproduce with the smallest realistic input. For intermittent failures, record frequency and conditions; gather observations rather than inventing a reliable reproduction.
- Inspect recent changes, dependency versions, configuration, and environment differences. Identify pre-existing failures so later checks can distinguish them from regressions.
- In a system spanning components, find the boundary where expected input, output, configuration, or state first diverges. Use existing logs or narrow temporary instrumentation. Record secret presence or redacted metadata rather than credentials or sensitive payloads.

If reproduction is unavailable, state that limit and use code, logs, or configuration to narrow hypotheses. Do not report a suspected cause as established.

## Trace and compare

Trace an invalid value or operation backward through its callers until you identify where it originated. Check initialization, lifecycle, ownership, and environment assumptions rather than patching only the final error site.

Find a working example in the same codebase where possible. Compare inputs, interfaces, configuration, and dependency behavior, reading the relevant implementation and contract. For UI rendering and animation problems, use ui-performance when available to distinguish layout, paint, compositing, JavaScript, and React work.

## Test one hypothesis

State the explanation and its evidence: “X fails because Y; observing Z would confirm or contradict that.” Choose a small diagnostic or reversible change that distinguishes it from alternatives. Change one relevant variable at a time and inspect the actual result.

When contradicted, record what the attempt ruled out and update the hypothesis. Remove your unsuccessful experimental changes without discarding the user's work. Avoid stacking speculative fixes or repeatedly trying the same change with different wording.

Repeated failures are a signal to reconsider the model: inspect shared state, coupling, incorrect interfaces, or missing observations. Continue useful investigation within the authorized scope. Ask for missing information or a decision when it materially blocks progress; an attempt count alone is not evidence of a faulty architecture or a reason to stop.

## Repair and verify

Make the smallest coherent repair at the cause. Add boundary validation only where it protects a distinct contract; avoid unrelated refactoring and redundant checks at every layer.

For a behavioral bug, prefer a focused regression test and demonstrate that it fails on the original behavior for the intended reason, then passes after the repair. Follow the project's test policy. For a narrow style or configuration change, use a relevant browser interaction, command, or existing check rather than creating tests that merely mirror source text.

For asynchronous failures, wait for the actual event or state with a bounded timeout, using the framework's existing waiters where possible. Increasing arbitrary sleeps hides races. When timing itself is the behavior under test, use controlled time or a justified interval and verify the triggering condition first.

Repeat the original failing interaction or command, then run checks covering affected behavior and interfaces. Run required project gates. Evidence must apply to the final relevant code state; rerun checks when subsequent changes invalidate it. Passing lint alone does not prove a build, and a code edit alone does not prove a performance improvement.

If the cause is external or still uncertain, explain what was ruled out and distinguish mitigation from repair. Retries, timeouts, or monitoring should address an observed failure mode, not replace investigation.

## Report

State the failure, established cause or remaining hypothesis, proposed or applied repair, and verification results. Include relevant file locations, unresolved failures, and unavailable checks. Claim the issue is fixed only when the evidence supports that claim.

## Attribution

Adapted from obra/superpowers' `systematic-debugging` skill and its root-cause tracing, condition-based waiting, and defense-in-depth references at commit `8ca22dba9a94f28898bbce59f2537ff4d87c747d` (v6.4.2). Scope, proportional verification, redacted diagnostics, and escalation guidance are maintained locally. The upstream MIT license is included in [LICENSE.txt](LICENSE.txt).
