---
name: quality-gate-audit
description: Audit whether a project’s lint, type, test, and validation gates check the intended inputs and report trustworthy results. Use for stale check runners, local/CI divergence, false passes, incomplete scope, or checking-system reviews.
---

# Audit the checking system

Audit executable behavior, not the presence of a script or a green badge. A check can be installed yet cover the wrong files, swallow failure, or never run.

## Trace owners and consumers

Read repository instructions, canonical check scripts, CI, hooks, package commands, workspace definitions, and agent adapters. Map entrypoint to checks to input scope. Note runtime/tool versions, network or service prerequisites, mutation, timeouts, and missing-tool handling.

Look for stale paths after cutovers, root-only commands missing nested modules, sampled files presented as complete coverage, generated or framework entrypoints excluded incorrectly, and wrappers duplicating obsolete commands. Compare documented coverage with actual quick/full behavior.

## Inspect result integrity

Exit codes or documented machine-readable results determine success. Searching logs for words like “error” is not a reliable substitute. Required checks skipped, absent artifacts, execution errors, timeouts, and cancellation must remain distinguishable from passing validation. Inspect output truncation and whether captured evidence survives cleanup.

For staged-file hooks, determine whether content is read from the index or the working tree. For generator checks, confirm stale output really fails. For scanners, inspect exclusions and positive controls. Distinguish reproducible pinned gates from deliberately live advisory tools; neither should claim the other's guarantees.

## Probe the credible failures

Use existing regression coverage first. Where meaningful proof is missing, exercise the actual public script or registered tool in an isolated fixture. Choose supported risks: a nonzero process with innocuous logs, a clean process mentioning “0 errors”, a missing required script, a newly added workspace member, or a violation outside a sampled subset.

Do not run destructive setup or expensive live suites merely to inspect them. Run relevant checks within scope and report prerequisites blocking broader execution. Avoid tests matching private function names or exact prose when observable behavior suffices.

## Report or repair

For review requests, report evidence-backed findings with affected entrypoints, false-pass/failure mechanism, severity, and a proposed fix. When repair is requested, change the shared owner, update consumers, and prove the before/after failure case. Preserve unrelated work and legitimate policy choices.

Deliver observed versus inferred findings, commands actually run, scope covered, remaining gaps, and the small number of changes that most improve confidence. Do not claim the application works merely because its static gates pass.
