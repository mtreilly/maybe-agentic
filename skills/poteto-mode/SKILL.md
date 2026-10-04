---
name: poteto-mode
description: Apply the locally adapted pstack engineering workflow when the user requests poteto-mode or explicitly asks to work in that style. Select a task-sized playbook with concrete completion evidence, simple design, and scoped autonomy.
---

# Poteto mode, portable edition

This is our smaller adaptation of the pstack workflow. It preserves evidence-driven engineering without requiring pstack's other skills, Cursor tools, named models, or a shipping stack. Apply it when the user requests this mode. It does not make itself a requirement for unrelated turns.

## Frame and choose

Name the requested outcome, affected system, and observable completion condition. Match the task to [references/playbooks.md](references/playbooks.md) and read the relevant section. For an unfamiliar multi-part task, write a short sequence of independently verifiable units, tackling the riskiest unknown first.

Ground the work in real behavior and ownership. Derive domain data and interfaces before writing complex orchestration. Compare genuinely different designs when the shape is uncertain, but do not force multi-model design for every function boundary.

## Engineering judgment

- Prefer the smallest coherent change. Delete unnecessary work and obsolete paths when compatibility and scope permit it.
- Keep state ownership clear. Parse external data at boundaries and preserve internal invariants. Do not add defensive layers solely to silence an unexplained failure.
- Prefer types, checks, and repeatable scripts to reminders for recurring mistakes.
- Measure the actual workload before claiming an optimization. Confirm timed work and correct output, compare fair configurations, and distinguish improvements from noise.
- Prove behavior through the real artifact or user path. A successful build or a worker's summary alone is not feature verification.
- Use focused regression checks when a practical path exists. Avoid elaborate tests that mostly exercise mocks or implementation details.
- Revisit repeated workaround patterns as evidence about a design assumption. One awkward case alone does not justify a rewrite.

## Execute and review

Keep reviews and investigations read-only unless changes are requested. Complete authorized reversible work without unnecessary checkpoints. A mode invocation does not authorize messages, tracker writes, production mutation, deployment, merge, or deletion beyond the user's scope.

Work directly by default. Use independent agents only when delegation is available and authorized and its benefit warrants the cost. Give each a bounded goal and owned working area. Inspect actual outputs and integrate a coherent result rather than trusting self-reports or concatenating alternatives.

For long or unattended work, keep a task-scoped decision log with timestamp, choice, reason, evidence, and result. One writer or separate worker logs prevent shared-write races. Keep failed attempts and verification gaps visible. No logger skill is required; an append-only file with those fields is sufficient.

Before handing back, inspect the diff for accidental scope, redundant comments/checks, type escape hatches, duplicated ownership, and avoidable complexity. Preserve behavior when cleaning up. Write a direct report of outcome, evidence, accepted tradeoffs, and remaining uncertainty without hype or invented sources.

## Attribution

Adapted from Lauren Tan's pstack `poteto-mode` and playbooks, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. This local edition is intentionally not a drop-in copy of all upstream orchestration. See [LICENSE.txt](LICENSE.txt).
