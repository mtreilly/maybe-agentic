---
name: maintain-verification-skill
description: Audit and repair an existing project's verification skill, feature map, and drive scripts against source and live behavior. Use when verification instructions drift or a feature map needs checking after application changes.
---

# Maintain a verification skill

Keep the reusable verification recipe accurate. This workflow edits only its skill directory, feature map, and owned helpers. Product regressions are findings, not permission to change the application.

## Find and inspect the target

Locate the requested verification skill or search the project's established skill directory for launch/drive instructions and a feature map. Resolve ambiguity before changing files. If no target exists, report that a verification skill must be created first; do not silently create a different deliverable.

Reconcile the map index with its files. For every feature, trace its current user entry points and behavior in source. Return a concise live recipe and supported drift findings with file locations. Inspect recent changes for missing user-facing features. A possible feature needs a source path before being added to the map.

Work sequentially by default. Independent source readers can help when delegation is available, authorized, and useful. They inspect source without editing or driving the application. One coordinator owns the live session and reconciliation.

## Drive and reconcile

Exercise every mapped feature using the target's own launch and isolation recipe. A healthy source review is not a substitute for this live pass.

- Check health and instance identity before driving and after surprising results. Reset a wedged UI or relaunch owned instances when a process check cannot establish usable state.
- Capture action and resulting state. Confirm artifacts remain at the named location after cleanup.
- Clean failed-iteration residue as well as successful runs. Do not kill a shared instance or delete unrelated data.
- An unreachable path needs the concrete missing prerequisite and attempted entry point. Report skipped and unreachable coverage honestly.

Classify each discrepancy:

- **Documentation drift:** the app works but the description is wrong. Update the map.
- **Automation gap:** the app works but the recipe cannot drive it. Repair the owned helper or instructions, then re-drive the affected path.
- **Product regression:** observed app behavior contradicts the intended contract. Report it separately; do not rewrite the map to conceal a defect.

Before changing intended expectations, consult available history or product documentation. If intent is unclear, keep the discrepancy open rather than choosing whichever behavior is easiest to verify.

## Deliver

Report **clean**, **changed**, or **blocked**, with source/live coverage, fixes, regression findings, evidence paths, and missing prerequisites. Changed recipes need execution, not only a text check. A blocked run can include partial verified results. Follow the user's requested delivery scope; no PR, tracker write, or schedule is required by this skill.

## Attribution

Adapted from Lauren Tan's pstack `maintain-verification-skill`, cursor/plugins commit `e43c7ee26e0038c6c1fa8380dd34ce86ff94cb2a`. See [LICENSE.txt](LICENSE.txt).
