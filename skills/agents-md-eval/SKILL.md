---
name: agents-md-eval
description: >-
  Evaluates, prunes, and empirically validates AGENTS.md, CLAUDE.md, and
  surrounding repository documentation using a two-stage multi-agent ablation
  (Stage 1: budgeted blank-AGENTS.md discoverability quiz; Stage 2: un-hinted
  A/B task ablation) orchestrated across multiple models in T3 Code, plus
  zero-reference scratch-doc cleanup and inline HTML scorecards. Use when
  auditing or shrinking AGENTS.md, proving whether agent instructions actually
  work, finding doc drift or misleading codebase patterns, or cleaning up stale
  repository markdown.
---

# AGENTS.md & Repo Docs Empirical Eval (`agents-md-eval`)

Measure what an `AGENTS.md` file actually does before cutting or keeping a single line. Run a two-stage multi-model ablation against isolated repository snapshots, prune duplication and stale markdown based on evidence, and prove zero regressions on un-hinted engineering tasks.

Let `SKILL_ROOT` be the directory containing this `SKILL.md`.

## When to use each stage

- **Stage 1 (Discoverability Quiz, blank `AGENTS.md`):** Fast, cheap triage pass. Answers *"What can models already recover from `README.md`, configs, linters, and scripts without `AGENTS.md`?"* Also exposes **doc drift** and **codebase poison** (stale code/strings that actively mislead models into forbidden patterns).
- **Prune & Doc Cleanup:** Apply Stage 1 verdicts — cut duplicated mechanics, split long runbooks into indexed `docs/` files, fix doc drift, verify docs-only CI skip rules, and audit zero-reference scratch/dump markdown.
- **Stage 2 (Un-Hinted A/B Task Ablation):** End-to-end proof on the newly pruned `AGENTS.md`. Compares **Arm A (`WITH`)** vs **Arm B (`WITHOUT`)** on realistic engineering tasks with **zero hints**, catching proactive traps that Stage 1's hinted quiz misses and measuring tool-call savings.

If the user only wants an audit, run Stage 1 (or Stage 2 on the current file) and stop with a scorecard + recommendations. If they want full optimization, run **Stage 1 → Prune/Fix → Stage 2**.

---

## Step 0: Inventory & Snapshot Isolation

1. **Inventory the target repo(s):**
   - Measure `AGENTS.md` / `CLAUDE.md` size (lines, bytes) and list `README.md`, `docs/`, `agents/`, hooks, linters, and CI config (`.gitlab-ci.yml`, `.github/workflows/`).
   - Map every section of `AGENTS.md` to its claimed rule, command, trap, or pointer.
2. **Never run ablations directly against a live checkout.**
   - Live checkouts contain `.git` history (agents can recover stripped `AGENTS.md` via `git log`/`git show`), parent-directory `AGENTS.md` files, and dirty edits.
   - Materialize clean, isolated snapshots outside the repo using `$SKILL_ROOT/scripts/make-eval-snapshot.sh`:

```bash
bash "$SKILL_ROOT/scripts/make-eval-snapshot.sh" \
  --repo /abs/path/to/repo \
  --ref HEAD \
  --out /tmp/agents-md-eval-<slug> \
  --mode both
```

This creates `/tmp/agents-md-eval-<slug>/with` (contains `AGENTS.md`, no `.git`) and `/tmp/agents-md-eval-<slug>/without` (strips `AGENTS.md`, `CLAUDE.md`, `.claude/`, `.cursor/`, and `.git`). Pass `--strip-secondary-agents` only if you also want `.agents/` removed in the `without` arm; keep `docs/` intact to measure `AGENTS.md`'s marginal value over repository docs.

---

## Step 1: Select a Multi-Model Panel in T3 Code

Read [references/t3-multi-agent-orchestration.md](references/t3-multi-agent-orchestration.md) before dispatching child agents.

1. Call `orchestrator_capabilities` to discover live providers, models, and effort/reasoning option IDs. **Never hardcode stale model names.**
2. Pick **3–4 diverse models across providers** (e.g., Anthropic Opus & Sonnet, OpenAI Codex/GPT, Google Gemini/Antigravity) at `low` or `medium` reasoning effort — fast, low-cost, and representative of routine coding sessions. Model diversity matters: in practice, some models dig into linter/CLI scripts while others rely heavily on markdown docs.
3. Dispatch every child in parallel via `delegate_task` with:
   - `mode: 'async'`, `role: 'research'`, `isolation: 'shared'` (children only read `/tmp` snapshots and never edit files)
   - Explicit `target: { driverKind, model, options }` from `orchestrator_capabilities`
   - Unique `clientRequestId` per `(stage, repo, arm, model)`
4. **End your turn after launching a wave.** T3 Code wakes you reactively as children finish — never poll `task_status` in a loop. Read full outputs via `task_status` (or `t3_thread_read` if truncated).
5. **Fallback outside T3 Code:** If `delegate_task` is unavailable, fan out in parallel using `run_workflow` or `invoke_subagent`.

---

## Step 2: Stage 1 — Budgeted Blank-`AGENTS.md` Discoverability Quiz

Read [references/rubrics-and-scoring.md](references/rubrics-and-scoring.md) for the exact question design and scoring templates.

1. **Write 10–12 concrete questions** covering every major section of `AGENTS.md` (runtime/commands, hooks/CI, architecture/routing, forbidden libraries/patterns, domain/localization glossaries, cross-repo contracts, governance/escalation).
2. **Launch all panel models in parallel against the `without` snapshot.** Every prompt must enforce:
   - **Strict sandbox:** *"ONLY read files inside `<WITHOUT_SNAPSHOT>`. Never inspect parent directories, the real workspace, or run git commands. Make zero edits."*
   - **Strict tool-call budget:** *"Budget: at most 3 file-read/search calls per question (~25 total). Answer `NOT_FOUND` rather than guessing."*
   - **Required output:** Exact answers per question, cited file paths inside the snapshot, and final tool-call count.
3. **Score every answer (`0 / 1 / 2`) across all models** and compute per-question averages:
   - **`avg ≥ 1.75` → Prune / Trim:** Already self-documented in `README.md`, manifests, linters, or scripts. Delete verbatim copies; keep at most a 1-line guardrail or pointer.
   - **`avg 1.00–1.50` → Condense / Split:** Partially discoverable. Keep only the specific non-discoverable trap; move lengthy procedures into indexed `docs/` files.
   - **`avg ≤ 0.75` → Must Keep:** True institutional knowledge, cross-repo boundaries, governance, or traps where models actively infer the wrong rule.
4. **Harvest bonus findings:**
   - **Codebase poison:** Note every case where models inferred a *forbidden* convention from stale code/strings still in the repo. File a cleanup ticket.
   - **Doc drift & dangling links:** Note contradictions between `AGENTS.md` and `docs/` or dead anchors exposed when `AGENTS.md` was stripped.
5. **Save & visualize:** Save `rubric.md`, raw model outputs, and `stage1-scorecard.md` in the user's chosen output folder (or `proposal/agents-md-eval/`). Build a clean HTML scorecard chart, check it with `html_preview`, and display it inline with `html_render`.

---

## Step 3: Prune `AGENTS.md`, Fix Drift & Audit Stale Docs

Wait for user confirmation if they asked for recommendations first; otherwise apply the Stage 1 plan:

1. **Prune `AGENTS.md`:**
   - Keep every `avg ≤ 0.75` item and every high-severity proactive guardrail (safety/credential bans, pinned dependency traps, commit/publish triggers, framework version quirks, governance).
   - Move multi-screen runbooks (emulator setup, large glossaries, QA cohort checklists) into concise, indexed `docs/` files and link them from a short lookup table in `AGENTS.md`.
   - Delete verbatim duplication of `README.md`, `package.json`, and self-documenting scripts/linters.
   - Fix doc drift in secondary docs (`docs/`) so agents navigating without `AGENTS.md` still land on accurate guidance.
2. **Audit docs bloat across the repo:**
   - Run `$SKILL_ROOT/scripts/audit-docs-bloat.sh /abs/path/to/repo` to list root scratch markdown, old plan/report dumps, and `agents/`/`docs/` folders with sizes and live code/script/test/CI reference counts.
   - Separate **safe zero-ref cleanup candidates** (stale root scratch notes, shipped ticket dumps) from **tool-referenced docs** (referenced by `cli_utils/`, CI, or quality budgets) and **active plans**.
   - Before deleting anything, `git grep` all remaining docs and update any broken relative links.
3. **Check CI docs-only skip rules before pushing:**
   - Inspect `.gitlab-ci.yml` / `.github/workflows/`. Ensure docs-only changes (`*.md`, `docs/**`, `.agents/**`) do not trigger expensive builds (especially mobile EAS/Expo or release pipelines). Add `workflow:rules` / path filters + contract tests if missing.

---

## Step 4: Stage 2 — Un-Hinted A/B Task Ablation

Stage 1's quiz *hints* at traps ("is any dependency pinned?"). Stage 2 proves whether the **pruned `AGENTS.md`** proactively prevents real-world mistakes when **nobody hints at the trap**.

1. **Build fresh `with` and `without` snapshots** from the pruned commit (`make-eval-snapshot.sh --mode both`).
2. **Design 3–4 realistic, zero-hint engineering tasks per repo** (12–16 binary `0/1` checks total):
   - Write tasks as a real developer/PM ticket (e.g., *"Migrate `/x` to a React table page"*, *"Upgrade `pkg-foo` to 3.7 and add a new Irish label"*, *"Run on Android emulator and debug a login failure"*).
   - **Never name the trap in the prompt** (no mention of pinned versions, forbidden imports, `#publish` flags, glossary words, or internal file names).
   - Instruct children to return exact file paths, ready-to-apply code/commands, and verification/commit steps **without editing files on disk**.
3. **Fan out `models × 2 arms` in parallel via T3 Code `delegate_task`:**
   - Keep `Arm A (WITH)` and `Arm B (WITHOUT)` prompts **byte-for-byte identical** except for the snapshot path (and tell `WITH` to read `AGENTS.md` as a normal session would, without mentioning any ablation).
   - Wait reactively for all children to complete.
4. **Grade every binary check (`1` = fully met, `0` = missed or violated) and tool-call count:**
   - **Primary gate (`WITH` arm):** Target ~100% pass rate. Any failure on `WITH` is either an over-pruned rule or an unclear instruction — fix `AGENTS.md` and re-run that task.
   - **Value proof (`WITH` vs `WITHOUT`):** Highlight `+50%` to `+100%` lift checks (the rules genuinely earning their token budget) and average tool-call reduction (`WITH` vs `WITHOUT`).
   - **Zero-lift checks (`100%` on both arms):** Candidates for future trimming — unless they are low-cost 1-line safety backstops.
5. **Present & clean up:**
   - Write `stage2-scorecard.md` and render an inline A/B comparison chart via `html_preview` → `html_render`.
   - Delete temporary `/tmp/agents-md-eval-*` snapshots once all raw outputs and scorecards are saved.
