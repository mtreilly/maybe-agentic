---
name: blast-radius
description: Review what a code change could break beyond its diff and direct callers. Use for change-impact analysis, subtle lifecycle or compatibility risks, and requests to prove a change's safety assumptions before shipping.
---

# Review the blast radius

Trace the non-obvious effects of the change. Focus on the facts that make it safe or unsafe and seek executable evidence rather than a convincing narrative.

## Establish scope and intent

Read the requested diff or files and the surrounding contracts. Determine the intended behavior from the request, commits, and available PR discussion. Use the repository's actual base branch; do not assume it is main. Git history, blame, and rename-aware logs can show context. Read relevant discussions if available without making a separate investigation skill a prerequisite.

## Trace where symbol search stops

Check pinned dependency behavior and local patches, wire formats, serialized data, database readers, other languages consuming the same bytes, feature flags, caches, asynchronous ordering, unmount/teardown, retries, and downstream integrations where relevant. Cite actual consumers and reachable execution paths; do not invent callers.

Identify the small set of invariants or assumptions on which safety depends. A change can have several independent risks; one proven invariant does not automatically clear all of them.

## Seek evidence for each important assumption

Distinguish:

1. An unsupported claim.
2. A source citation or pinned-library implementation.
3. A traced argument showing why the bad case is unreachable.
4. A focused executable check against the real code.
5. A reproduction through the actual application.

Choose the cheapest meaningful proof. Run focused checks when possible within the review's scope; keep temporary artifacts isolated and do not mutate production to prove a theory. Additional independent reviews are optional when available, authorized, and justified by the change. Trace their findings yourself before accepting them.

## Deliver the review

- Explain the behavior change, including effects the diff hides.
- State each safety assumption and its evidence level. Mark unproved assumptions explicitly.
- Give confirmed risks with reachable mechanism, source location, likely impact, and a check or mitigation. Do not invent numerical probabilities.
- List checked-and-cleared concerns separately.
- Identify the cheapest remaining verification before shipping.

A review request produces findings. Apply fixes only when requested. Keep the report direct, distinguish observation from inference, and do not expose private evidence publicly.

## Attribution

Adapted from Lauren Tan's pstack `blast-radius`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. History lookup, evidence calibration, and reporting are included locally. See [LICENSE.txt](LICENSE.txt).
