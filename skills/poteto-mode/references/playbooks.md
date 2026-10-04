# Portable playbooks

Choose the relevant workflow and scale its depth to the task. These recipes are complete without calls to other skills or particular agent tools.

## Investigation

Trace the current code or user behavior and relevant history. Separate observed behavior from historical intent, label inference, and answer with source evidence. Do not implement a change merely to answer a read-only question.

## Bug fix

Reproduce the smallest meaningful failing behavior. Trace the cause, implement a scoped fix, and repeat the same observation. Add a focused regression check when a cheap existing test path exists. Record failing-before and passing-after evidence or state why the original environment could not be reproduced.

## Performance fix

Establish a realistic baseline and confirm correct work is being timed. Identify the limiting resource using a separate profile. Consider eliminating work, avoiding repeats, doing less, deferring work, moving it off the visible path, concurrency, and finally reducing individual costs. Measure each change and stop when the user's target is met. Report timings, variation, workload, and artifacts.

## Iterative metric improvement

Choose the metric, direction, correctness constraints, and a bounded stopping condition. Validate the measurement harness against contrasting workloads, then hold the harness and inputs stable. One hypothesis per attempt, repeated before/after measurement, and keep or revert based on change beyond noise and correct behavior. Record rejected attempts too. Do not relax the target to declare success or continue indefinitely without useful hypotheses.

## Runtime or captured-trace diagnosis

Capture the relevant CPU, heap, render, or process evidence if the request concerns a live symptom. If a trace is already supplied, inspect that artifact first. Reduce to the hot path, retainer chain, allocation, or scheduling mechanism and map it to source. Use a paired capture or scoped instrumentation to confirm a hypothesis where possible. Diagnosis does not authorize a fix or live production instrumentation.

## Feature

Establish user-visible behavior and domain data. Integrate it at the correct owner, implement in verifiable units, then exercise the real user path and meaningful failure states. Preserve accessibility and existing contracts. Name the artifact or observation proving the outcome.

## Refactoring

State the behavior that must stay unchanged. Trace relevant consumers, make a coherent structural change, and verify the contracts rather than only compilation. Migrate internal callers and remove obsolete paths when scope and public compatibility allow it.

## Prototype or visual parity

For a design choice, build the smallest disposable example that answers the question. For exact visual parity, capture comparable baseline and candidate states at the same viewport, data, theme, and interaction. Compare real screenshots or observable layout, and distinguish intended changes from regressions.

## Skill authoring or evaluation

Define the skill's trigger and the decisions it should improve. Keep instructions precise, resources local, and tool assumptions explicit. Validate names, descriptions, references, and helper behavior. For an evaluation, use realistic tasks in isolated workspaces, preserve candidate independence, and judge observable outputs against criteria withheld from candidates. Do not treat the skill's self-reported compliance as proof of improvement.

## PR status, delivery, or a stack

Determine whether the user requested status only, fixes, or landing. Check actual reviews, CI, conflicts, and change scope. A green CI result is evidence about its checks, not proof of all behavior. For authorized fixes, address concrete issues and reverify. For authorized landing, follow the repository's merge policy and dependencies and verify each unit. Do not infer merge permission from creating a PR or checking its status.

## Long task or multi-phase program

Define completion, budget or stopping conditions, phases, ownership, and evidence. Keep units independently verifiable and a decision trail. Parallelize only independent work with separate write targets and authorized delegation. Reconcile outputs and verify the integrated product. Report blocked prerequisites and do not represent partial completion as finished.

## Resume or pause

For a pickup, use the supplied handoff/history and confirm current branch, uncommitted work, processes, artifacts, and remaining goals. Do not trust a stale summary over live state. For an explicit pause, preserve work and evidence, stop owned expendable processes when appropriate, and write a concise resume note. Do not delete another worker's state.

## Worktree or simulator cleanup

Inventory candidates and establish ownership, uncommitted work, branch/PR status, and active use. Read-only inventory is distinct from deletion. Perform only the cleanup authorized by the user, preserve dirty or active work, and report what was retained and removed.
