---
name: interrogate
description: Adversarially review a specified change or design against its intent and synthesize actionable findings. Use for requests to challenge an approach, find blind spots, or conduct independent code review; review does not automatically authorize fixes.
---

# Challenge the change

Find reachable correctness and structural problems, then apply pragmatic judgment. A reviewer's confidence, quantity of findings, or model identity is not evidence.

## Prepare the review

Determine the exact files or diff and the correct base branch. State the intended result from the request, history, or PR description. Resolve uncertainty that would materially change the verdict. Gather enough callers, types, and surrounding code to make the review meaningful.

Read [references/rubric.md](references/rubric.md). Use the relevant lenses without forcing every category onto a narrow change. Review source and execution paths, not just the diff. Focus each finding on a concrete mechanism and its observable consequence.

## Independent perspectives when useful

Review directly by default. If multiple reviewers are requested or authorized, give each the same intent, scope, and rubric, with access to the necessary context. Keep them read-only. Use available reviewers without prescribed model slugs. Avoid sharing early findings in ways that make subsequent reviewers copy the first answer.

Deduplicate findings, note disagreements, and distinguish independent agreement from shared assumptions. A single concrete correctness or security finding can outweigh several approvals. Verify claims against actual callers, types, and pinned library behavior before accepting them.

## Lead judgment

Read [references/lead-judgment.md](references/lead-judgment.md) when filtering a broad review or several reviewers' findings. Categorize supported findings as:

- **Act on:** a concrete issue affecting the stated contract or a justified maintainability requirement.
- **Consider:** a credible tradeoff needing a decision.
- **Noted:** relevant context with no justified immediate action.
- **Dismissed:** an unsupported, incorrect, stylistic, or out-of-scope concern, with the reason.

Do not manufacture consensus or assign numerical confidence without evidence. Do not force a fixed finding count. A clean review is valid.

## Deliver

Lead with the verdict and important findings. Each actionable finding names the location, triggering path, consequence, evidence, and practical next step. When several reviewers participated, disclose who reviewed and where they agreed or differed. Mark verification limits and unresolved assumptions. Do not auto-apply edits, open issues, or block unrelated work as a side effect of a review request.

## Attribution

Adapted from Lauren Tan's pstack `interrogate`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Rubric and lead-judgment references are retained; model and Task-tool requirements were removed. See [LICENSE.txt](LICENSE.txt).
