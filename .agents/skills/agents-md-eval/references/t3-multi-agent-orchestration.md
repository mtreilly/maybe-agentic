# Multi-Agent Orchestration in T3 Code

This reference explains how to run Stage 1 and Stage 2 ablations in parallel across multiple AI providers and models inside T3 Code without context leakage, polling waste, or tool-call runaway.

---

## 1. Discover Live Models First

Always call `orchestrator_capabilities` before building your eval panel. Provider catalogs, model slugs, and option keys change frequently.

Select **3–4 models spanning at least 2–3 providers** so you catch provider-specific habits (for example, some models grep linter/CLI configs aggressively while others follow markdown links):

| Panel slot | Typical selection | Recommended effort/reasoning |
| --- | --- | --- |
| Frontier Anthropic | Flagship Claude | `effort: "low"` |
| Mid-tier Anthropic | Mid-tier Claude | `effort: "medium"` |
| OpenAI / Codex | Flagship GPT/Codex | `reasoningEffort: "low"` |
| Google / Antigravity | Flagship Gemini | `thought_level: "low"` (or provider equivalent) |

*Verify exact `driverKind`, `providerInstanceId`, `model`, and `options` keys against the `orchestrator_capabilities` response before dispatching. State the planned wave size and confirm cost expectations with the user before fanning out.*

---

## 2. Launching Parallel Waves with `delegate_task`

Use `delegate_task` — not `create_threads` — because delegated children start with **zero parent history** (preventing contamination from your rubric, answers, or earlier stage results).

### Required arguments per child
- `mode`: `"async"` (so all children run concurrently)
- `role`: `"research"` (read-only analysis)
- `isolation`: `"shared"` (children only read isolated `${TMPDIR:-/tmp}/agents-md-eval-*` snapshots; never create git worktrees for read-only snapshot evals)
- `clientRequestId`: deterministic unique key, e.g. `eval-s1-app-opus-low` or `eval-s2-fe-with-sol-low`
- `title`: short human-readable label, e.g. `S2 Frontend with — Opus (low)`
- `target`: `{ providerInstanceId, model, options }` from `orchestrator_capabilities`
- `task`: self-contained prompt containing the exact snapshot path, rules, and questions/tasks

### Wave sizing
- **Stage 1:** Launch `1 repo × 3–4 models` in a single turn.
- **Stage 2:** Launch `1 repo × 2 arms × 3–4 models` (6–8 children) per wave.

### Reactive wakeup (no polling)
After issuing all `delegate_task` calls in a wave, end your turn with no more tool calls (or continue unrelated local prep work). T3 Code wakes you when each child finishes.
- If a completion notification truncates a response, call `task_status(taskId)` (or `t3_thread_read(threadId)` using `itemId` + `textOffset`).
- Never spin in a shell `sleep` loop or poll `task_status` while children are still running.

---

## 3. Preventing Contamination & Leakage

Child agents can break isolation unless you seal both the filesystem and the prompt:

1. **Filesystem seal (`make-eval-snapshot.sh`):**
   - Materialize snapshots via `git archive` into a fresh directory created with `mktemp -d "${TMPDIR:-/tmp}/agents-md-eval-XXXXXX"`.
   - Never copy `.git` — otherwise a model can run `git log -p AGENTS.md` or `git show HEAD:AGENTS.md` and defeat the `without` arm.
   - Strip `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.claude/`, `.cursor/`, and `.cursorrules` from `without`.
   - Put snapshots outside the parent repository so ancestor-directory auto-discovery does not pick up a parent `AGENTS.md`.
2. **Prompt seal (include verbatim in every child prompt):**
   ```text
   SANDBOX RULES (MANDATORY):
   - You may ONLY inspect files inside: <SNAPSHOT_DIR>
   - Ignore any workspace-level or global repository instructions outside <SNAPSHOT_DIR>.
   - Do NOT read, search, or list any path outside <SNAPSHOT_DIR> (including the workspace root or parent folders).
   - Do NOT run git commands, network calls, or edit/create any files on disk.
   - At the end of your reply, report the exact number of tool calls you made.
   ```
3. **Strict arm parity in Stage 2:**
   - Never mention "ablation", "Stage 2", "rubric", or "without AGENTS.md" in the child prompt.
   - Keep `with` and `without` prompts **byte-for-byte identical** except for `<SNAPSHOT_DIR>`. Use the same neutral framing in both arms (*"Inspect the repository at `<SNAPSHOT_DIR>` and follow its documented conventions"*) so `with` is not artificially coached to open `AGENTS.md` while `without` is not.
   - Check cited file paths during grading: if any child cites a file outside `<SNAPSHOT_DIR>` or an ambient workspace instruction, mark the run contaminated and exclude it.

---

## 4. Handling Provider Quirks Observed in Practice

- **Tool-call budget adherence:** Some models batch shell commands while others make individual file reads. Record both score and tool-call count (and check `t3_thread_read(..., view: 'activity')` if a model omits its count).
- **Truncated summaries:** Completion notifications truncate long responses. Save raw responses to disk and fetch any truncated tail with `t3_thread_read(threadId, itemId, textOffset)` before grading — never mark a check `0` because the answer was past the cutoff.
- **Ambient workspace instructions:** Because `isolation: "shared"` starts in the workspace CWD, a harness may preload workspace-level instructions. Remind children to ignore instructions outside `<SNAPSHOT_DIR>` and audit cited paths during grading.

---

## 5. Rendering Visual Scorecards

When `html_preview` and `html_render` are available, turn Stage 1 and Stage 2 scorecards into inline charts:
1. Write a self-contained HTML file (inline `<style>` and `<script>`/SVG, no fixed page background or `vh` heights).
2. Call `html_preview(path=..., width=728)` to verify layout and `contentHeight`.
3. Call `html_render(path=..., title=..., height=<contentHeight>)` to display the finished chart.

---

## 6. Fallback Outside T3 Code

If T3 Code orchestration tools are not present:
- Use the active harness's parallel subagent mechanism pointed at the same isolated snapshot directories.
- If only one model is available, run Stage 1 and Stage 2 sequentially against the isolated snapshots — even a single-model ablation exposes duplication, drift, poison, and proactive traps.
