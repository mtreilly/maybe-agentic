---
name: wait-what
description: Restate the previous explanation in plain language with the missing context when the user says it did not make sense.
disable-model-invocation: true
---

# Wait what

Re-explain the message the user did not understand. Use the specific passage they identify, or the last substantive explanation when that is clear from context.

Start with the point they need to understand, then supply the missing context: what we are trying to do, what changed or was discovered, and why that matters. Use short sentences, familiar words, and one concrete example when it helps. Define necessary technical terms on first use. Use established project vocabulary when available, explaining unfamiliar glossary terms rather than replacing ordinary language with jargon.

Preserve the original meaning, conditions, uncertainty, and verification limits. Simplifying a hypothesis must not make it sound proven. If the earlier message was incorrect or skipped a material step, state the correction plainly.

Keep the restatement focused on the misunderstanding. Do not merely repeat the same wording, add a long preamble, create documents, or restart the workflow. Answer a specific question if the user supplied one; ask a focused clarification only when the target is genuinely ambiguous.

## Attribution

Adapted from Matt Pocock's `wait-what` at commit `24fe0ef7737efae15c87225755e9f6f5965e4888` (1.3.1). Plain-language explanation and evidence-preservation guidance are maintained locally. The upstream MIT license is included in [LICENSE.txt](LICENSE.txt).
