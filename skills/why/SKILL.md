---
name: why
description: Investigate historical motivation and constraints behind code or a design decision using commits, reviews, tickets, documents, and relevant operational evidence. Use for rationale, regression history, thresholds, or tradeoffs that source alone cannot explain.
---

# Investigate why it exists

Code establishes behavior, not its author's motivation. Seek the contemporaneous record and distinguish evidence from plausible explanations.

## Anchor the question

Identify the relevant paths, symbols, current behavior, and the user's proposed rationale if any. Treat their hypothesis as a candidate, not a conclusion. Use blame, rename-aware file history, and recent patches to locate the substantive introduction or redesign, not only the latest touch. Extract relevant PRs and ticket references from commits and read their discussions when available.

## Search relevant evidence

Start with repository history and linked sources. Expand to the available issue tracker, design documents, chat, observability, error tracking, or analytics only when the target or discovered evidence makes that category relevant. A retry, timeout, guard, or threshold may need incident evidence. Do not query every connector merely because it is installed.

Searches and investigators are read-only. Use available tools directly; optional independent readers must have a bounded question and source scope and require authorized delegation. Record searched sources and meaningful null results. Missing tools are evidence gaps, not reasons to fabricate a record. Confine private context to the requested topic.

## Calibrate the conclusion

Read [references/epistemics.md](references/epistemics.md) before synthesizing. Keep direct statements, supported conclusions, inference, speculation, and unknowns distinct. Reconcile contradictory sources openly. Current plausibility does not prove original intent, and absence of a record does not prove there was no reason.

## Deliver

Answer the rationale question with citations near each claim. Include reasonable inferences with their reasoning, credible alternatives, unresolved questions, and the actual sources searched. Use the confidence distinctions only where useful rather than adding empty sections.

If this investigation informs a requested change, turn the findings into concrete constraints: preserve established requirements, change obsolete mechanisms, avoid past failed approaches, and identify remaining risks. Do not modify the code as a side effect of answering why.

## Attribution

Adapted from Lauren Tan's pstack `why`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. The confidence reference is retained; Cursor models and mandatory connector fan-out were removed. See [LICENSE.txt](LICENSE.txt).
