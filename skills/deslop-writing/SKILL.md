---
name: deslop-writing
description: Edit prose to remove filler, vague claims, repetitive phrasing, and formulaic agent writing while preserving meaning and tone. Use for requests to deslop writing or polish documentation, PR descriptions, reports, and drafts.
---

# Clean up writing

Edit the requested text for a reader who needs the point on the first pass. Preserve meaning, technical names, factual uncertainty, citations, and the user's chosen voice. Do not make this skill a requirement for every unrelated response.

## Rewrite patterns that add no information

- Filler such as "it is important to note" and "in order to". Delete it or use the direct construction.
- Vague attribution such as "experts believe". Name a supported source, qualify the claim, or remove it. Never invent an authority or strengthen a claim to make it sound cleaner.
- Hype, flattery, generic conclusions, stock chatbot offers, and commentary about how helpful the response is. State the result or relevant next action.
- Abstract vocabulary and metaphor when a concrete word explains the mechanism. Use "use", "help", "move", "is", and "has" when accurate. Preserve established technical terms and proper names.
- Participial phrases that imply importance without adding evidence. Explain the real consequence or omit them.
- Contrast slogans, forced groups of three, false ranges, and unnecessary synonym changes. Use the natural structure and call one thing by one name.
- Dense sentences and over-compressed fragments. Keep complete sentences and split when clauses make the reader backtrack. Vary length when a longer sentence carries one useful thought.
- Excessive hedging that obscures the statement. Preserve uncertainty justified by the evidence; removing "perhaps" must not turn an inference into fact.
- Overused bold labels, decorative headings, emojis, and punctuation used to create drama. Prefer sentence-case headings and ordinary prose, retaining formatting that helps the intended audience.

## Preserve the task

Work only on the requested draft or file. Do not rewrite code, literal commands, source quotations, URLs, or citations as if they were prose. Protect product terminology and legal meaning. Match the user's style rather than enforcing arbitrary punctuation bans.

Read the result once for meaning and once for readability. Each sentence should tell the reader something concrete to know or do. Cut words without cutting evidence, tradeoffs, limitations, or required sections. A phrase that could fit any project's conclusion usually needs a specific fact or deletion.

Return the edited text in the requested format. If editing a file, summarize the meaningful changes briefly. If an unsupported factual claim remains, flag it instead of silently fabricating support.

## Attribution

Adapted from Lauren Tan's pstack `unslop`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, renamed `deslop-writing`. Pattern guidance is retained with locally scoped triggers and flexible punctuation. See [LICENSE.txt](LICENSE.txt).
