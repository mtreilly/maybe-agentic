# Multi-Agent Orchestration in T3 Code

This reference explains how to run Stage 1 and Stage 2 ablations in parallel across multiple AI providers and models inside T3 Code without context leakage, polling waste, or tool-call runaway.

---

## 1. Discover Live Models First

Always call `orchestrator_capabilities` before building your eval panel. Provider catalogs, model slugs, and option keys change frequently.

```json
// Example tool call
{ "toolSummary": "Discover available providers and models" }
```

Select **3–4 models spanning at least 2–3 providers** so you catch provider-specific habits (for example, some models grep linter/CLI configs aggressively while others follow markdown links):

| Panel slot | Typical selection | Recommended effort/reasoning |
| --- | --- | --- |
| Frontier Anthropic | Opus / flagship Claude | `effort: "low"` |
| Mid-tier Anthropic | Sonnet | `effort: "medium"` |
| OpenAI / Codex | GPT / Codex flagship | `reasoningEffort: "low"` |
| Google / Antigravity | Gemini / Neon | `thought_level: "low"` (or provider equivalent) |

*Verify exact `driverKind`, `model`, and `options` keys against the `orchestrator_capabilities` response before dispatching.*

---

## 2. Launching Parallel Waves with `delegate_task`

Use `delegate_task` — not `create_threads` — because delegated children start with **zero parent history** (preventing any contamination from your rubric, answers, or earlier stage results).

### Required arguments per child
- `mode`: `"async"` (so all children run concurrently)
- `role`: `"research"` (read-only analysis)
- `isolation`: `"shared"` (children only read isolated `/tmp/agents-md-eval-*` snapshots; never create git worktrees for read-only snapshot evals)
- `clientRequestId`: deterministic unique key, e.g. `eval-s1-mobile-opus-low` or `eval-s2-fe-with-sol-low`
- `title`: short human-readable label, e.g. `S2 Frontend WITH — Opus (low)`
- `target`: `{ driverKind, model, options }` from `orchestrator_capabilities`
- `task`: self-contained prompt containing the exact snapshot path, rules, and questions/tasks

### Wave sizing
- **Stage 1:** Launch `1 repo × 4 models` (4 children) or `2 repos × 4 models` (8 children) in a single turn.
- **Stage 2:** Launch `1 repo × 2 arms × 4 models` (8 children) per wave. For 2 repos, run Repo 1 (8 children) then Repo 2 (8 children) — or all 16 at once if rate limits allow.

### Reactive wakeup (no polling)
After issuing all `delegate_task` calls in a wave, **end your turn with no more tool calls** (or continue unrelated local prep work). T3 Code automatically wakes you when each child finishes.
- If a completion notification includes only a truncated preview or tells you to read the result, call `task_status(taskId)` (or `t3_thread_read(threadId)` for very long responses using `itemId` + `textOffset`).
- Never spin in a shell `sleep` loop or call `task_status` repeatedly while children are still running.

---

## 3. Preventing Contamination & Leakage

Child agents are surprisingly resourceful and will break isolation unless you seal both the filesystem and the prompt:

1. **Filesystem seal (`make-eval-snapshot.sh`):**
   - Materialize snapshots via `git archive` into `/tmp/agents-md-eval-<run>/{with,without}`.
   - Never copy `.git` — otherwise a clever model runs `git log -p AGENTS.md` or `git show HEAD:AGENTS.md` and defeats the `without` arm.
   - Strip `AGENTS.md`, `CLAUDE.md`, `.claude/`, and `.cursor/` from `without`.
   - Put snapshots outside the parent monorepo so ancestor-directory auto-discovery does not pick up a parent `AGENTS.md`!
2. **Prompt seal (include verbatim in every child prompt):**
   ```text
   SANDBOX RULES (MANDATORY):
   - You may ONLY inspect files inside: <SNAPSHOT_DIR>
   - Do NOT read, search, or list any path outside <SNAPSHOT_DIR> (including the workspace root or parent folders).
   - Do NOT run git commands, network calls, or edit/create any files on disk.
   - At the end of your reply, report the exact number of tool calls you made.
   ```
3. **Arm parity in Stage 2:**
   - Never mention "ablation", "Stage 2", "rubric", or "without AGENTS.md" in the child prompt.
   - In `WITH`, add only: *"Follow the repository's normal conventions and read `AGENTS.md` first as in a standard coding session."*
   - In `WITHOUT`, omit that sentence (or say *"Follow the repository's conventions"*); keep every word of the task descriptions identical.

---

## 4. Handling Provider Quirks Observed in Practice

- **Tool-call budget adherence:** Some models batch shell commands (`cat a b c`) to stay at 4–8 calls while others make 15–24 individual file reads. Always record both **score** and **tool-call count** (and check `t3_thread_read(..., view: 'activity')` if a model forgets to self-report its tool count).
- **Truncated summaries:** `delegate_task` completion notifications truncate long responses around ~12 KB. Always save raw responses to disk (`results/` or `stage2-results/`) and fetch any truncated tail with `t3_thread_read(threadId, itemId, textOffset)` before grading — never mark a check `0` because the answer was past the truncation cutoff.
- **Inherited workspace AGENTS.md:** When a child's default CWD is inside the workspace, some harnesses auto-load the workspace's root `AGENTS.md`. Remind the child to ignore any auto-loaded workspace instructions outside `<SNAPSHOT_DIR>` and check its cited file paths during grading to verify no leakage occurred.

---

## 5. Rendering Visual Scorecards in T3 Code

When `html_preview` and `html_render` are available, always turn both Stage 1 and Stage 2 scorecards into clean inline charts:
1. Write a self-contained HTML file (inline `<style>` + `<script>`/SVG, zero fixed page background, no `vh` or `height: 100%`, using T3 CSS variables `--foreground`, `--muted`, `--card`, `--border`, `--success`, `--warning`, `--destructive`, `--chart-1`..`--chart-6`, `--radius`, `--font-sans`, `--font-mono`).
2. Call `html_preview(path=..., width=728)` to verify layout, readability, and exact `contentHeight` (and optionally `width=390` for mobile fit).
3. Call `html_render(path=..., title=..., height=<contentHeight>)` to show the finished chart inline above your summary.

---

## 6. Fallback Outside T3 Code

If T3 Code MCP tools (`orchestrator_capabilities`, `delegate_task`) are not present:
- Use `run_workflow` (Python `parallel(...)` fan-out over `agent(...)`) or `invoke_subagent` with `research` subagents pointed at the same `/tmp/agents-md-eval-*` snapshots.
- If only one model is available, still run the full Stage 1 blank-`AGENTS.md` quiz and Stage 2 `WITH` vs `WITHOUT` A/B comparison — even a single-model ablation exposes duplication, drift, poison, and proactive traps.
