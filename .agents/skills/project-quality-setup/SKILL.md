---
name: project-quality-setup
description: Recommend or implement a proportionate code-quality setup after inspecting a project’s stack, existing checks, and failure risks. Use for baseline tooling, missing quality gates, or standardizing project check commands.
---

# Set up project quality checks

Inventory before prescribing. A useful setup protects actual project contracts and makes failures easy to diagnose; the number of tools is not a quality metric.

## Discover the project

Read repository instructions, package/workspace manifests, lockfiles, CI, hooks, generated-code configuration, and existing check commands. Identify maintained source roots, runtimes, public boundaries, and known failure classes. Distinguish commands found in source from commands successfully executed. Preserve existing tooling and contributor changes.

Read [references/stack-profiles.md](references/stack-profiles.md) for the relevant stack. Select mechanisms already supported by the repository first. Verify current official documentation before recommending unfamiliar tools or changing version-sensitive configuration.

## Recommend the smallest useful setup

Map each material risk to its existing protection or a gap. Consider formatting/lint, types, unused code, module boundaries, contract drift, configuration, dependencies, and behavioral verification. Exclude layers that do not address a demonstrated risk. Static analysis does not establish runtime correctness, hydration, authorization, or database concurrency.

Prefer architecture or types that remove an invalid state over adding a scanner for it. Use standard rules before custom checks. Scope generated code, fixtures, framework entrypoints, and exceptions explicitly; avoid blanket exclusions and arbitrary file-size limits.

Provide a proposal with: risk or invariant, current protection, proposed change, exact command, scope, prerequisites, expected cost, and remaining limitation. Prioritize changes by useful failure detection and maintenance cost. Recommend incremental no-new-violation baselines where existing debt would otherwise prevent adoption; keep exceptions specific and reviewed.

## Implement when requested

A request for recommendations produces a proposal. A request to set up the checks authorizes relevant config, scripts, and documentation changes. Use the project's lockfile and runtime conventions; do not upgrade unrelated dependencies or install global tools.

Provide a cheap development command and a comprehensive command where the project needs both. Have hooks, CI, and agent adapters call shared executable owners rather than duplicate check logic. Document what each mode actually covers, whether it changes files, and whether it needs services or network access. Required missing tools and missing input must not become a pass.

Execute relevant checks and demonstrate that newly introduced guards reject a credible violation and accept a valid case. Use isolated fixtures where possible. Preserve nonzero exit status through wrappers; report skipped or blocked checks explicitly.

Deliver changed paths or the proposal, commands, verification results, and outstanding prerequisites. Publishing, committing, or writing to external trackers follows the user's requested scope.
