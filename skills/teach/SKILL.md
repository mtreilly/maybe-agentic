---
name: teach
description: Teach a concept or skill through focused explanations, practice, feedback, and an optional persistent learning workspace.
disable-model-invocation: true
---

# Teach

Ground teaching in what the user wants to be able to do. Start from their current understanding and provide a small, useful next challenge with feedback. Match the depth and format to the request: a single explanation needs no course workspace; sustained learning benefits from durable records.

## Establish the learning goal

Use the user's request and existing learning records to identify the goal, prior knowledge, constraints, and desired outcome. Ask a focused question when missing information would change the lesson. Do not require an interview when the request already establishes these facts.

For ongoing learning, use the requested workspace or a dedicated learning directory within the project. Preserve unrelated project files and existing naming conventions. Use the [mission format](MISSION-FORMAT.md) when recording the goal; confirm a material change to that goal with the user rather than silently redirecting the course.

## Teach one useful thing

Select a lesson connected to the goal and within reach of the user's current ability. Explain the minimum knowledge needed, show a concrete worked example, then give the user a chance to apply it. Adapt examples to their context instead of introducing unnecessary jargon.

Verify uncertain, niche, current, or consequential facts against trustworthy sources, preferring official documentation, original research, and primary material. Cite sources near the claims they support and label uncertainty. Use the [resources format](RESOURCES-FORMAT.md) for recurring sources; keep annotations concise and identify gaps.

Choose the simplest effective artifact. A short exchange or exercise is often enough. Use an interactive demonstration when changing inputs or observing state makes the idea clearer. For a lesson the user will revisit or share, a readable HTML artifact may be useful; follow the environment's supported tools and preserve accessibility. Reuse existing styles and components when creating a series, introducing shared assets only when they serve actual reuse.

## Practice and feedback

Ask for recall, an explanation in the user's own words, or a small realistic task before showing the answer. Make questions test understanding rather than wording tricks. Assess the response, explain mistakes concretely, and adjust the next challenge. Avoid interpreting agreement, exposure, or a completed page as demonstrated mastery.

For continuing study, revisit important ideas after a gap and mix related exercises when the user can distinguish them. Keep difficulty useful: provide hints or reduce the step size when stuck; increase the challenge when the user demonstrates understanding. Propose real-world practice or community feedback when it serves the goal and preferences, without making joining a community a prerequisite.

## Preserve learning when useful

Create records lazily, only as needed:

- `MISSION.md`: purpose, observable goals, constraints, and scope, following the mission format.
- `RESOURCES.md`: annotated sources, optional communities, and knowledge gaps.
- `learning-records/`: concise established knowledge, corrected misconceptions, or goal changes, using the [learning record format](LEARNING-RECORD-FORMAT.md). Distinguish demonstrated understanding from claimed prior knowledge.
- `lessons/` and `reference/`: reusable lessons and compact reference material when artifacts are warranted.
- `NOTES.md`: relevant learning preferences and unfinished work, without duplicating other records.

Record what changes future teaching, not a transcript of every activity. Respect existing records and supersede mistaken conclusions explicitly. End with the lesson's useful result, feedback on any practice completed, and the next exercise or question appropriate to the user's requested scope.

## Attribution

Adapted from Matt Pocock's `teach` and its mission, resources, and learning-record formats at commit `24fe0ef7737efae15c87225755e9f6f5965e4888` (1.3.1). Lesson scope, workspace behavior, source verification, and artifact guidance are maintained locally. The upstream MIT license is included in [LICENSE.txt](LICENSE.txt).
