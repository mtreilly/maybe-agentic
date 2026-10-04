---
name: automate-me
description: Create or revise a personal agent working-style skill from repeated preferences and explicit user choices. Use when the user asks to capture how they work, personalize agent conventions, or update their personal mode.
---

# Capture a personal working style

Create a concise skill that reflects this user's choices. Do not copy an upstream author's mode or infer a durable preference from one task.

## Find the evidence and target

Locate an existing personal-mode skill in the explicitly relevant project or personal skill directory. Preserve its location and identity when updating. Use the active conversation and user-provided examples first. Search additional history only within the user's requested workspace and time range, using known transcript locations; no Cursor layout is assumed.

Identify repeated response preferences, autonomy boundaries, verification expectations, code/prose conventions, process habits, and actual tool choices. Multiple independent examples support a durable preference. Explicit user preferences can establish it directly. Show contradictions instead of silently choosing one.

Ask concise questions only for choices that materially affect the skill and cannot be inferred. In update mode, focus on what changed and preserve existing preferences the user has not revoked.

## Draft the skill

Use a lowercase name such as `<handle>-mode` matching its directory and standard frontmatter with name and description. Trigger on the chosen mode name and requests to work in that style, not generic coding keywords. Follow the project's skill convention, defaulting to `skills/<handle>-mode/` for maintained source and `.agents/skills/` for project discovery where appropriate.

Include only specific choices that change behavior. Common sections are response style, autonomy, verification, tools/process, and code discipline, but omit sections without evidence. Use generic terms such as "the user" inside instructions. Preserve user intent, permissions, and the current task scope; a style skill is not blanket authorization for external actions.

Write complete, plain instructions with concrete triggers. Avoid filler, copied catalogs, speculative requirements, or an exhaustive personal manual. If supporting templates are useful, bundle them with the skill. No external mode, prose-cleanup skill, or authoring tool is required.

## Validate and deliver

Check frontmatter, naming, unfinished content, and links. Explain which choices came from explicit statements, repeated evidence, or unresolved interpretation. Present the resulting draft for feedback; subjective fit is best established by the user's response and later actual tasks. A request to create/update the skill authorizes that local work, not a commit, PR, or publication unless separately requested.

## Attribution

Adapted from Lauren Tan's pstack `automate-me`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Personal-mode authoring is self-contained and tool-neutral. See [LICENSE.txt](LICENSE.txt).
