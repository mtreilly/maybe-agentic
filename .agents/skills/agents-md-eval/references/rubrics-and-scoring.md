# Rubrics, Scoring & Doc-Bloat Classification

---

## 1. Stage 1: Discoverability Quiz Design & Scoring

### Designing the 10–12 questions
Walk through `AGENTS.md` top to bottom and turn every major section or rule cluster into one crisp, specific question:
1. **Runtime & core commands** (language/runtime versions, package manager, dev/test/lint/typecheck/build gates)
2. **Git hooks, branch/commit/PR/ticket workflow** (naming conventions, publish triggers, review gates)
3. **Architecture & routing boundaries** (layer boundaries, legacy wrappers, proxy rules, cross-repo ownership)
4. **Approved vs. forbidden stack / components** (UI primitives, state management, date libs, escape hatches)
5. **Known runtime traps & pinned dependencies** (render loops, ABI flags, exact dependency pins)
6. **Domain / localization glossaries & intentional quirks** (canonical terms, forbidden variants, deliberate exceptions)
7. **Security, credentials & environment boundaries** (QA vs staging vs prod bans, auth scripts)
8. **Governance & escalation** (who owns routing/dependency/schema approvals, doc style rules)

Keep each question answerable in 2–5 bullet points so grading is objective and fast.

### Scoring scale (`0 / 1 / 2`)
| Score | Definition |
| --- | --- |
| **2** | Accurate and complete — caught the key commands, paths, and gotchas. |
| **1** | Partial — found the general area or half the rule, but missed a key trap, escape hatch, or exact detail. |
| **0** | Missed, returned `NOT_FOUND`, or inferred a **forbidden/wrong** rule from stale codebase files. |

### Decision bands (average across panel models)
These bands partition `[0.00, 2.00]` continuously so every panel size (3, 4, or more models) classifies cleanly with no gaps:

| Avg Score | Band | Action on `AGENTS.md` |
| --- | --- | --- |
| **≥ 1.75** | **Prune / Trim** | Already trivially discoverable from `README.md`, configs, linters, or scripts. Remove duplicated prose; keep at most a 1-line safety guardrail or pointer. |
| **0.76 – 1.74** | **Condense / Split** | Partially discoverable. Trim mechanics already in code/linters; keep only the specific non-discoverable gotcha, and split multi-paragraph runbooks into indexed `docs/` files. |
| **≤ 0.75** | **Must Keep** | Genuine institutional knowledge, cross-repo contracts, governance, or traps where models actively infer forbidden conventions. Keep prominent in `AGENTS.md`. |

### Always log two Stage 1 side-discoveries
1. **Codebase poison:** Stale files, legacy strings, or old patterns still in the repo that caused ≥ 1 model to output a *forbidden* answer. File a follow-up cleanup ticket — `AGENTS.md` should not have to fight active poison forever.
2. **Doc drift:** Places where `README.md`, `docs/`, or scripts contradict `AGENTS.md` or link to removed anchors. Fix these alongside any approved `AGENTS.md` prune.

---

## 2. Stage 2: Un-Hinted A/B Task Ablation Design

### Why Stage 1 is not enough
In Stage 1, asking *"Is any dependency pinned?"* or *"What causes a table freeze?"* tells the model where to look — so models score `2/2` on things they would miss in a real task where nobody mentions the trap.

Stage 2 removes all hints and measures proactive compliance on realistic tasks.

### Designing 3–4 zero-hint tasks (12–16 binary checks)
Write each task as a realistic engineering ticket that naturally crosses 3–5 guardrails **without naming any of them**:

| Good zero-hint task | Bad hinted task (avoid) |
| --- | --- |
| *"Add a new `/admin/orders/exports` React page with a paginated table and status toggle, plus ticket `PROJ-412` commit and verification commands."* | *"Add a React page using `EMPTY_ARRAY`, `autoResetPageIndex: false`, Query v4 `isLoading`, and `excludedRoutes.ts`."* |
| *"A teammate wants to bump `rich-editor` from `3.6.0` to `3.7.0` and add a new localized label for 'billing cycle'. Review the bump and write the locale edits."* | *"Check if `rich-editor` is pinned at `3.6.0` and use the glossary term for 'billing cycle'."* |
| *"Build and run the mobile app on local emulator `emulator-5554`, sign in with a test account, and note what to do if login returns `rejected-credentials`."* | *"Do not run `yarn android`; use the Gradle ABI flag and `scripts/dev-login.sh`."* |

### Dry-run output contract
Tell every child agent:
- Do not modify files on disk or run mutating, git, or network commands.
- Output exact file paths to create/edit, ready-to-apply code snippets, exact CLI commands to run, commit message format, and any escalations or blocks.

### Binary grading (`0` or `1`)
Break each task into 3–5 atomic, objective binary checks (`T1a`..`T4c`):
- **`1` (Pass):** Explicitly satisfied the guardrail accurately with no violation.
- **`0` (Fail):** Omitted the guardrail, used a forbidden pattern/term/version, failed to block a prohibited action, or gave wrong verification/commit steps.

### Interpreting A/B results
| `with` | `without` | Interpretation |
| --- | --- | --- |
| **100%** | **0% – 50%** | **High-value guardrail.** `AGENTS.md` is doing critical work (`+50%` to `+100%` lift). Keep concise and prominent. |
| **100%** | **75%** | **Protective backstop.** Catches weaker/faster models or edge cases. Worth keeping as a 1-liner. |
| **100%** | **100%** | **Redundant or enforced elsewhere.** Safe to keep only if it is a cheap 1-line safety ban; otherwise candidate for further trimming. |
| **< 100%** | any | **Regression or unclear instruction in pruned `AGENTS.md`.** Tighten wording or restore the missing guardrail and re-run that task before shipping. |

Also compare **average tool calls (`with` vs `without`)**: a concise, well-indexed `AGENTS.md` often cuts exploratory tool calls while raising rule adherence. Note explicitly that dry-run task grading measures proposed-patch adherence rather than live execution.

---

## 3. Doc-Bloat & Zero-Ref Scratch Cleanup Criteria

Run `bash "$SKILL_ROOT/scripts/audit-docs-bloat.sh" /abs/path/to/repo` and classify markdown outside active product docs into three buckets:

1. **Candidate to prune (report for approval before deleting):**
   - Root scratch markdown (`report.md`, `GOAL.md`, `TIMELINE.md`, `*_fixes.md`, `*_PROGRESS.md`) with **0 references** in code, tests, scripts, or CI.
   - Completed ticket dumps, old agent session logs, historical review matrices, and superseded plan folders (`docs/notes/`, `docs/releases/<old-ticket>/`, `agents/plans/`).
   - Obsolete helper scripts from closed investigations (verify `git grep` shows zero active callers).
2. **Keep, but consolidate/rename if confusing:**
   - Paused programme folders whose name collides with active agent docs — update every script, test, hook, skill, and CI reference, then run the full test suite.
3. **Never delete blindly:**
   - Anything referenced by scripts, quality budgets, accessibility registries, performance baselines, or CI contract tests.
   - Active plan directories (`docs/plans/active/`) unless explicitly signed off by the owner.

Always `git grep` for deleted filenames/paths across remaining tracked docs and update stale links before committing.
