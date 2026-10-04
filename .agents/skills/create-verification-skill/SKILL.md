---
name: create-verification-skill
description: Create a project-specific skill that launches and drives a real UI, CLI, API, or library and captures evidence of working behavior. Use when a project needs reusable verification instructions or its current manual checks are hard for agents to reproduce.
---

# Create a verification skill

Generate instructions another agent can execute without knowing this project. Discover the recipe from the repository and prove it on the running application.

## Discover the actual workflow

Inspect the project's documented commands, existing tests, routes, commands, seed data, and configuration. Establish:

- What users interact with: browser, desktop app, CLI, service, mobile app, or library.
- How to build or launch it, its prerequisites, and the observable readiness condition.
- How to drive it using existing automation first. Use available browser tools, a terminal session, HTTP requests, or a small executable caller as appropriate. No particular control plugin is required.
- What demonstrates the result: screenshots, terminal output and exit codes, responses, persisted state, or logs.
- How to isolate ports, profiles, data, and sessions from other work.

Ask only for necessary facts that cannot be found in the repo or observed. If the base does not run, report the precise failure; resolve startup problems only within the authorized scope. Do not write a working recipe based on assumptions about a broken checkout.

## Generate a self-contained skill

Follow the project's existing skill convention. Otherwise write `.agents/skills/verify-<app>/SKILL.md` with matching lowercase name and a description naming the app, interaction, and trigger. Include these sections with concrete commands rather than unfinished placeholders:

- **Launch:** build/start commands, prerequisites, owned instance identity, and readiness checks. Short-lived CLIs use a fresh isolated session per drive.
- **Doctor:** a read-only check of health, expected build, authentication, and instance ownership. Repeat after unexpected behavior before continuing.
- **Drive:** actual selectors, requests, or terminal commands. Prefer accessible names and stable handles to coordinates.
- **Evidence:** capture the action and resulting state, verify side effects, and name the artifact directory. A success toast alone does not prove persistence. Verify dry-run effects rather than trusting the flag's name.
- **Cleanup:** remove only processes and scratch state created by this run. Keep evidence outside deleted scratch directories and check it survives cleanup.
- **Helpers:** make bundled scripts executable and document their invocation.

Use actual user entry points. Internal setters and test-only endpoints cannot stand in for the behavior being verified. Exercise external integrations through existing safe test boundaries; do not send real messages or perform production writes merely to obtain proof.

## Create a feature map

Read [references/feature-map.md](references/feature-map.md) for the entry format. Add `features/README.md` and files for a useful initial selection of user-facing features. Derive them from the app rather than inventing features. Document entry points, prerequisites, actions, observable results, and known traps.

## Execute before handing back

Run the generated launch, doctor, one mapped feature, evidence capture, and cleanup. Fix recipe errors and retry within scope. Clean up failed attempts too. Confirm evidence still exists. Distinguish the feature actually proved from features merely documented. If the environment prevents execution, deliver an explicitly unverified draft with the missing prerequisite.

Report the skill path, interaction proved, evidence location, and verification limits. Recommend auditing the feature map when the application changes.

## Attribution

Adapted from Lauren Tan's pstack `create-verification-skill`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. Cursor paths and companion-skill calls were replaced with portable instructions. See [LICENSE.txt](LICENSE.txt).
