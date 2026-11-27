---
name: verification-skill
description: Create, audit, or repair a project-specific verification skill, feature map, and drive scripts that launch and exercise a real UI, CLI, API, or library and capture durable evidence. Use when a project needs reusable live verification instructions or when an existing verification skill or feature map has drifted after application changes.
---

# Create or maintain a verification skill

Build or repair instructions another agent can execute without knowing this project. Prove the recipe on the running application rather than trusting source inspection alone.

## Choose mode

- **Create mode:** Use when the project has no verification skill for the requested app or surface. Discover the real workflow from the repository, write the self-contained skill and feature map, and execute at least one mapped feature end to end before handing back.
- **Maintain mode:** Use when a verification skill already exists and needs auditing or repair after application changes. Locate the target verification skill first; if none exists and the user asked only to audit or maintain one, report that a verification skill must be created first instead of silently creating a different deliverable. Maintain mode edits only the verification skill directory, feature map, and owned helpers — product regressions are findings, not permission to modify application code.

## Create mode: discover and author

Inspect documented commands, tests, routes, commands, seed data, and configuration to establish:

- What users interact with (browser, desktop app, CLI, service, mobile app, or library).
- How to build or launch it, its prerequisites, and the observable readiness condition.
- How to drive it using existing automation first (browser tools, terminal session, HTTP requests, or a small executable caller). No particular control plugin is required.
- What proves the result (screenshots, terminal output and exit codes, responses, persisted state, or logs).
- How to isolate ports, profiles, data, and sessions from other work.

Ask only for necessary facts unavailable in the repo or runtime. If the checkout does not run, report the precise failure rather than writing an untested recipe.

Follow the project's existing skill convention (for example, `skills/<name>/` in a skill-toolkit repository, or `.agents/skills/verify-<app>/SKILL.md` in an application repository) with a matching lowercase `name` and a concrete `description`. Include concrete commands (no placeholders) for:

- **Launch:** build/start commands, prerequisites, owned instance identity, and readiness checks. Short-lived CLIs use a fresh isolated session per drive.
- **Doctor:** read-only check of health, expected build, authentication, and instance ownership.
- **Drive:** actual selectors, requests, or terminal commands. Prefer accessible names and stable handles to coordinates.
- **Evidence:** capture the action and resulting state, verify side effects, and name the artifact directory. A success toast alone does not prove persistence; verify dry-run effects rather than trusting the flag's name.
- **Cleanup:** remove only processes and scratch state created by this run. Keep evidence outside deleted scratch directories and confirm it survives cleanup.
- **Helpers:** make bundled scripts executable and document their invocation.

Read [references/feature-map.md](references/feature-map.md) for the map format. Create `features/README.md` and feature files derived from real user-facing surfaces in the app.

## Maintain mode: audit and reconcile

Reconcile `features/README.md` with its feature files, trace each feature's current user entry points in source, and inspect recent changes for unmapped user-facing features. Scope live replay to affected paths when requested, or all mapped features for a full audit.

Classify every discrepancy:

- **Documentation drift:** the app works, but the feature map or instructions are wrong. Update the map.
- **Automation gap:** the app works, but the recipe cannot drive it. Repair the owned helper or instructions and re-drive the affected path.
- **Product regression:** observed app behavior contradicts the intended contract. Report it separately; never rewrite the map to conceal a defect.

Consult history or product documentation before changing intended expectations. If intent is unclear, keep the discrepancy open.

## Shared live execution and isolation rules

- Exercise actual user entry points; internal setters and test-only endpoints cannot stand in for user-visible behavior.
- Exercise external integrations only through safe test boundaries; never send real messages or perform production writes merely to obtain proof.
- Check health and instance identity before driving and after surprising results. Reset or relaunch only instances owned by this run; never kill shared instances or delete unrelated data.
- Clean up failed-attempt scratch residue as well as successful runs, and confirm retained evidence still exists after cleanup.
- Report skipped or unreachable paths honestly with the concrete missing prerequisite and attempted entry point.

## Deliver

Execute launch, doctor, the scoped mapped feature(s), evidence capture, and cleanup before handing back. Changed or newly created recipes require live execution, not only a text check. If environment limits block execution, deliver an explicitly unverified draft with the missing prerequisite.

Report status (**created**, **clean**, **changed**, or **blocked**), skill path, features actually proved versus only documented, fixes applied, regression findings, evidence locations, and verification limits.

## Attribution

Adapted from Lauren Tan's pstack `create-verification-skill` and `maintain-verification-skill`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`, consolidated into one portable self-contained skill. See [LICENSE.txt](LICENSE.txt).
