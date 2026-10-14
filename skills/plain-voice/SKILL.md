---
name: plain-voice
description: Write or rewrite prose in Micheál's plain, direct voice with Simplified Technical English clarity. Use for code-review replies, Jira and GitLab comments, release notes, hand-over notes, Slack posts, PR descriptions and any explanation a colleague will read. Triggers - "in my voice", "plain voice", "sounds too technical", "doesn't sound like me", "make this clearer", "rewrite this comment".
---

# Write it the way I would say it

Write for a colleague who is busy and reading on the first pass. Say the point, say why, say what happens next. Sound like a person talking, not a system reporting.

Read [references/voice.md](references/voice.md) for the voice and [references/clarity-rules.md](references/clarity-rules.md) for the sentence rules. Both apply at once. The voice decides what the text sounds like. The rules decide how each sentence is built.

## The three questions

Before you write, answer these in your head:

1. What is the one thing the reader needs to know?
2. Why should they believe it, or why does it matter?
3. What do they do next, or what will I do next?

Lead with the answer to question 1. Most texts need one paragraph per question and nothing else.

## Voice in short

- First person, present tense where true. "I checked", "I think", "we should".
- Plain words. Say "fix", "check", "start", "stop", not "remediate", "validate", "spin up", "deprecate".
- Give the opinion and the reason. "This is a real problem, because a parent can take over another family's application." Not "this may potentially represent a concern".
- Be honest about confidence. "I think", "I'm fairly sure", "I haven't checked". Never upgrade a guess to a fact to sound cleaner.
- Concrete over abstract. Name the thing that happens to a person. "The parent sees a 404" beats "the request is rejected at the authorisation layer".
- Short paragraphs, one idea each. Lists for three or more parallel items. Headers only in long documents.
- British and Irish spelling. Colour, organise, programme, licence as a noun.
- No corporate filler, no stock openers or closers, no "I hope this helps". Stop when the content stops.
- A wry aside is fine once. Twice is a tic.

## Sentence rules in short

From Simplified Technical English, structural rules only:

- One idea per sentence. Around 20 words, 25 at most.
- Active voice. Name who does the thing.
- Simple tenses. "We fixed it", not "we have fixed it", unless the "still true now" meaning matters.
- No semicolons. Split the sentence.
- No phrasal verbs where one plain verb exists. "Start", not "spin up". "Contact", not "reach out".
- No noun piles. "The handler that sets queue priority", not "the queue priority handler logic".
- Verbs, not nouns made from verbs. "Check the log", not "perform a check of the log".
- Keep every hedge, number, condition and scope qualifier. Cutting them changes the claim.

## How much technical detail

Match the reader. A reviewer on a merge request wants the commit, the rule that was broken and what the fix does to a user. A QA tester wants where to click and what they should see. A manager wants the outcome and the risk. Nobody wants a method name in prose unless they have to go and open that file. One identifier per sentence at most, two per paragraph.

Replace internal names with what they do. "The attachment guard" or "the generic update endpoint", then the identifier once in backticks if the reader needs it.

## Short comments

For a reply on a merge request, Jira or Slack, aim for two to five sentences:

1. The verdict. "Confirmed, this is real." or "Not a bug, here is why."
2. What was done, with the commit or link.
3. What it means for the user or the reviewer.
4. Anything still open.

See [examples/before-after.md](examples/before-after.md) for rewrites of real comments.

## Mechanical check

Run `scripts/clarity-lint.py` on the draft (stdin or a file). It flags semicolons, long sentences, phrasal verbs, nominalisations, marketing adjectives and synonym rotation, and warns on passive voice and compound tenses. It never flags hedges. Fix what it finds, then read the text aloud once. If you would not say a sentence to a colleague across a desk, rewrite it.

## Boundaries

- Keep the meaning, the facts, the uncertainty and the numbers. Rewrite form, not substance.
- Do not add a cause, a frequency or a promise the source did not state.
- Do not rewrite code, commands, quoted error text, URLs or citations.
- Do not apply this to marketing copy or to someone else's quoted words.
- If the text has nothing to say, say that instead of polishing it.

## Attribution

The sentence rules and the linter come from Dustin Yuchen Teng's `asd-ste100-skill` (MIT). That skill encodes the rule categories of ASD-STE100 Issue 9 without the official dictionary. See [LICENSE.txt](LICENSE.txt). The voice guide is Micheál Reilly's own.
