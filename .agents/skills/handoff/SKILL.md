---
name: handoff
description: Save a concise handoff so a fresh agent or session can continue the current task using existing artifacts and verified state.
disable-model-invocation: true
---

# Handoff

Write a continuation record for the next agent, tailored to the user's stated next task. Preserve enough context to resume correctly without repeating completed work or guessing at permissions.

## Capture the continuation

Inspect the current work and existing artifacts before writing. Include:

- **Objective and scope:** the intended outcome, constraints, preferences, and success criteria.
- **Authorization:** actions explicitly requested or approved, unresolved decisions, and actions still requiring approval. Separate actual authorization from assumptions.
- **Workspace:** absolute project path, relevant branch and revision if Git exists, and any uncommitted changes or isolated workspaces the next agent must preserve.
- **Completed work:** concise outcomes with pointers to files, commits, issues, specs, or decisions. Reference authoritative artifacts rather than duplicating their contents.
- **Verification:** checks actually run, what state they cover, results, unresolved failures, and checks that were unavailable. Do not turn an earlier passing check into evidence for later edits.
- **Next action:** the first useful step, pending work in dependency order, blockers, and hypotheses that remain unverified.

Add suggested skills only when relevant and available. Describe how to load them through the next harness's actual mechanism; do not assume a particular Skill tool exists.

Redact credentials and sensitive payloads. Record how authorized tooling can obtain access rather than embedding secrets. Distinguish observed facts from recollection or an agent's unverified report.

## Save and deliver

Use the requested location or the project's existing convention. For durable continuation, prefer an appropriate task or notes directory. Use the OS temporary directory for a disposable transfer when suitable, and identify that location as temporary. Choose a unique filename and preserve existing records.

Read the saved record back, check artifact pointers, and report its absolute path and intended next task. Writing a handoff does not stop, replace, or delegate the active task unless the user requested that transition. The next agent should reconcile the record with the actual tree before continuing.

## Attribution

Adapted from Matt Pocock's `handoff` at commit `24fe0ef7737efae15c87225755e9f6f5965e4888` (1.3.1). State, authorization, verification, and storage guidance are maintained locally. The upstream MIT license is included in [LICENSE.txt](LICENSE.txt).
