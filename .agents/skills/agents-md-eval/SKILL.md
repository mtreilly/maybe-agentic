---
name: agents-md-eval
description: Empirically evaluate AGENTS.md, CLAUDE.md, and repository instruction docs with a two-stage multi-model ablation (discoverability quiz and un-hinted A/B task adherence). Use only when explicitly requested to benchmark, audit, or ablate AGENTS.md effectiveness.
disable-model-invocation: true
---

# AGENTS.md & Repo Docs Empirical Eval

Measure what an `AGENTS.md` file actually adds before cutting or keeping a single line. Run a two-stage ablation against fresh isolated snapshots, report evidence-backed recommendations, and apply edits only when the user explicitly approves them.

Let `SKILL_ROOT` be the directory containing this `SKILL.md`.

## Operating defaults and cost guardrails

- **Explicit invocation only:** This workflow fans out multiple child agents and models; invoke it explicitly rather than on routine markdown chores.
- **Report-only by default:** Running an evaluation produces scorecards and concrete recommendations. Do not prune `AGENTS.md`, delete scratch markdown, or modify CI configuration unless the user explicitly authorizes those edits.
- **Confirm panel budget before fan-out:** State the planned model count and wave size (for example, 3–4 models × 1 arm in Stage 1, or × 2 arms in Stage 2) and stay within any user-set budget.
- **Honest verification limits:** Dry-run A/B task grading measures proposed-patch adherence to repository rules, not live runtime execution or full regression proof. State that limit in every scorecard.

## When to use each stage

- **Stage 1 (Discoverability Quiz, blank `AGENTS.md`):** Fast triage pass. Tests what models can already recover from `README.md`, manifests, linters, and scripts without `AGENTS.md`, and exposes doc drift and stale patterns ("codebase poison") that mislead models.
- **Prune & Doc Cleanup (only when approved):** Apply Stage 1 verdicts — remove duplicated mechanics, split lengthy runbooks into indexed `docs/` files, fix doc drift, and list zero-reference scratch markdown for review.
- **Stage 2 (Un-Hinted A/B Task Ablation):** Compares **Arm A (`with`)** vs **Arm B (`without`)** on realistic engineering tasks with zero hints, measuring proactive rule adherence and tool-call savings.

---

## Step 0: Inventory & Snapshot Isolation

1. **Inventory the target repo(s):**
   - Measure `AGENTS.md` / `CLAUDE.md` size (lines, bytes) and list `README.md`, `docs/`, hooks, linters, and CI config.
   - Map every section of `AGENTS.md` to its claimed rule, command, trap, or pointer.
2. **Never run ablations directly against a live checkout.**
   - Live checkouts contain `.git` history (agents can recover stripped `AGENTS.md` via `git log`/`git show`), ancestor `AGENTS.md` files, and dirty edits.
   - Materialize fresh, isolated snapshots in a new directory under `${TMPDIR:-/tmp}` using `$SKILL_ROOT/scripts/make-eval-snapshot.sh`:

```bash
EVAL_OUT="$(mktemp -d "${TMPDIR:-/tmp}/agents-md-eval-XXXXXX")"
bash "$SKILL_ROOT/scripts/make-eval-snapshot.sh" \
  --repo /abs/path/to/repo \
  --ref HEAD \
  --out "$EVAL_OUT" \
  --mode both
```

The script refuses existing `with`/`without` directories and refuses any path overlapping the target repository. It strips `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.claude/`, `.cursor/`, `.cursorrules`, and `.git` from `without` (add `--strip-secondary-agents` to strip `.agents/` too). Keep `docs/` intact to measure `AGENTS.md`'s marginal value over ordinary repo docs.

---

## Step 1: Select a Multi-Model Panel

Read [references/t3-multi-agent-orchestration.md](references/t3-multi-agent-orchestration.md) before dispatching child agents.

1. When running inside an orchestrator such as T3 Code, call `orchestrator_capabilities` to discover live providers, models, and effort/reasoning option IDs. Never hardcode stale model names.
2. Pick **3–4 diverse models across providers** at `low` or `medium` reasoning effort to reflect routine coding sessions.
3. Dispatch children in parallel as read-only research workers pointed only at their assigned snapshot directory, using unique `clientRequestId` values per `(stage, repo, arm, model)`. End your turn to wait reactively rather than polling in a loop.
4. **Outside T3 Code:** Use the active harness's parallel subagent mechanism, or run the same snapshot-isolated Stage 1 and Stage 2 prompts sequentially with the available model(s).

---

## Step 2: Stage 1 — Budgeted Blank-`AGENTS.md` Discoverability Quiz

Read [references/rubrics-and-scoring.md](references/rubrics-and-scoring.md) for question design and scoring rules.

1. **Write 10–12 concrete questions** covering every major section of `AGENTS.md` (runtime/commands, hooks/CI, architecture/routing, forbidden patterns, domain glossaries, cross-repo contracts, governance).
2. **Launch panel models in parallel against the `without` snapshot.** Every prompt must enforce:
   - Strict sandbox: only inspect files inside `<WITHOUT_SNAPSHOT>`; never read ancestor directories, the real workspace, or git history; make zero edits.
   - Tool-call budget: at most 3 read/search calls per question (~25 total); answer `NOT_FOUND` rather than guessing.
   - Required output: answers per question, cited snapshot-relative file paths, and total tool-call count.
3. **Score every answer (`0 / 1 / 2`) across all models** using exhaustive, gap-free average bands:
   - **`avg ≥ 1.75` — Prune / Trim:** Already self-documented in `README.md`, manifests, linters, or scripts. Cut verbatim duplication; keep at most a 1-line guardrail or pointer.
   - **`0.76 ≤ avg < 1.75` — Condense / Split:** Partially discoverable. Keep only the specific non-discoverable trap; move lengthy procedures into indexed `docs/` files.
   - **`avg ≤ 0.75` — Must Keep:** True institutional knowledge, cross-repo boundaries, governance, or traps where models infer the wrong rule.
4. **Harvest bonus findings:**
   - **Codebase poison:** Stale files or patterns that caused models to infer a forbidden convention.
   - **Doc drift & dangling links:** Contradictions between `AGENTS.md` and secondary docs.
5. **Save & present:** Save `rubric.md`, raw model outputs, and `stage1-scorecard.md` in the user's chosen output folder (outside the repo unless requested). If visual rendering tools (`html_preview` / `html_render`) are available, render a clean scorecard chart.

---

## Step 3: Prune `AGENTS.md` & Audit Stale Docs (Explicit Approval Required)

Stop after Step 2 unless the user explicitly requested applying edits. When edits are approved:

1. **Prune `AGENTS.md`:**
   - Keep every `avg ≤ 0.75` item and every high-severity proactive guardrail (safety/credential bans, pinned dependency traps, publish triggers, framework quirks, governance).
   - Move multi-screen runbooks into concise, indexed `docs/` files linked from a short lookup table.
   - Delete verbatim duplication of `README.md`, manifests, and self-documenting scripts/linters; fix doc drift in secondary docs.
2. **Audit docs bloat across the repo:**
   - Run `bash "$SKILL_ROOT/scripts/audit-docs-bloat.sh" /abs/path/to/repo` to list root scratch markdown and `docs/`/`agents/` folders with sizes and live code/script/test/CI reference counts.
   - Separate safe zero-reference cleanup candidates from tool-referenced docs and active plans. Before deleting any approved file, `git grep` remaining docs and fix broken links.
3. **Optional CI advisory check:** Inspect CI path filters and note if docs-only edits (`*.md`, `docs/**`, `.agents/**`) would trigger expensive builds. Do not modify CI files unless the user explicitly includes CI changes in scope.

---

## Step 4: Stage 2 — Un-Hinted A/B Task Ablation

Stage 1 hints at traps; Stage 2 measures proactive compliance when nobody names the trap.

1. **Build fresh `with` and `without` snapshots** into a new `${TMPDIR:-/tmp}` directory from the commit under test.
2. **Design 3–4 realistic, zero-hint engineering tasks** (12–16 binary `0/1` checks total):
   - Write each task as a normal developer ticket without naming pinned versions, forbidden imports, publish flags, glossary terms, or internal file names.
   - Instruct workers to return exact file paths, ready-to-apply code/commands, and verification/commit steps without editing files on disk.
3. **Maintain strict arm parity:**
   - Keep `Arm A (with)` and `Arm B (without)` prompts **byte-for-byte identical** except for the snapshot path. Do **not** add an extra instruction telling only the `with` arm to read `AGENTS.md`; both arms receive the exact same neutral instruction (*"Inspect the repository at `<SNAPSHOT_DIR>` and follow its documented conventions"*).
   - Verify cited paths during grading so ambient workspace instructions outside the snapshot did not leak into either arm; discard or flag any contaminated run.
4. **Grade every binary check (`1` = met, `0` = missed or violated) and tool-call count:**
   - **`with` arm gate:** Investigate any `< 100%` check as a possible over-pruned rule or unclear instruction.
   - **Marginal lift (`with` vs `without`):** Highlight `+50%` to `+100%` lift checks (rules earning their token budget) and average tool-call reduction.
   - **Zero-lift checks (`100%` on both arms):** Candidates for future trimming unless they are cheap 1-line safety backstops.
5. **Present & clean up:**
   - Write `stage2-scorecard.md`, noting explicitly that dry-run grading validates proposed-patch rule adherence rather than executed runtime tests.
   - Remove only the temporary snapshot directory (`"$EVAL_OUT"`) created by this run once raw outputs and scorecards are saved.
