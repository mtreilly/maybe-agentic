---
name: show-me-your-work
description: Keep an evidence-linked decision log for long-running, unattended, or multi-phase work. Use when a user needs to review decisions, rejected attempts, verification, and outcomes after the work completes.
---

# Show the decision trail

Maintain a compact append-only TSV log of meaningful decisions and checkpoints. Evidence is a path, URL, commit, or tool-result pointer, not a paragraph of justification. Avoid logging every routine command.

## Start and append

Choose a task-scoped working-artifact path such as `.audit/<task>.tsv`, respecting the project's artifact convention. Keep it out of commits unless the requested deliverable needs the trail. Record the run identity and scope at its start. When continuing an existing log, read the latest entries and identify which earlier work belongs to this run.

Use the bundled executable helper:

```sh
bash scripts/log.sh <logfile> <phase> <decision> <why> <evidence> <result>
```

Resolve `scripts/log.sh` relative to this skill's directory. It creates the header, stamps UTC time, keeps cells single-line, and escapes spreadsheet-formula prefixes. The columns are timestamp, phase, decision, why, evidence, and result.

Log a design choice, accepted unit, failed verification, pivot, revert, or blocker when it happens. Record negative and inconclusive results alongside successes. If an entry is wrong, append a correction that identifies the earlier row; do not silently rewrite history.

## Own the writes

The helper does not lock concurrent writes. Use a single coordinator writer or separate logs per worker and combine them at the reporting boundary. Do not assume an append-only convention prevents races.

## Audit before handoff

Compare this run's rows with available session/tool history and produced artifacts. Follow evidence pointers and confirm they support the claim. If the environment does not expose a transcript, use the available history and disclose the limit rather than searching unrelated workspaces.

Add missing decisions that shaped the outcome, supersede inaccurate entries, and retain both verified and unverified states. An independent reviewer may add confidence when available and authorized, but it is not required to use the log. A reviewer reads evidence and does not re-execute external actions.

Report the log path, outcome, and any decisions needing attention because evidence is weak, verification is missing, or a tradeoff remains unresolved. Do not log secrets or publish private artifacts as a side effect of maintaining the trail.

## Attribution

Adapted from Lauren Tan's pstack `show-me-your-work`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. The logger is retained; Cursor transcript and mandatory model dependencies were removed. See [LICENSE.txt](LICENSE.txt).
