# Skill evaluations

Four small tasks exercise outcomes that matter:

| Case | Candidate skill | Objective checks | Human review |
| --- | --- | --- | --- |
| debugging | systematic-debugging | Zero-percent coupon works; invalid percentages still fail | Reproduction, causal diagnosis, focused edits |
| quality | project-quality-setup | Existing command and omitted workspace identified; proposal present; project preserved | Recommendation is runnable, proportionate, and justified |
| handoff | handoff | Plan resolves; scope/continuation recorded; old passing check stays historical | Faithful authorization, useful next action, accuracy |
| verification | create-verification-skill | Skill/evidence exist; scratch removed; submitted CLI recipe proves persistence across processes | Actionable skill/map and evidence that the candidate actually executed it |

Objective passes are partial evidence. The grader leaves manual criteria pending
and never turns them into an overall quality verdict. It re-executes the CLI
recipe independently; this does not establish that the candidate ran it earlier.
The fixtures are intentionally small, so improvement here needs confirmation on
real projects. `cases.json` also contains positive and negative routing prompts;
check those through each client's real skill-discovery mechanism separately.
Explicit skill injection in the task runner does not test automatic discovery.

## Prepare an isolated pair

Run from the toolkit root. Keep runs outside `maybe-agentic` so its project skill
installation does not contaminate the baseline. Use a durable external directory
for retained experiments, or a temporary one for a trial:

```sh
eval_root="$(mktemp -d "${TMPDIR:-/tmp}/maybe-evals.XXXXXX")"
python3 -B evals/run.py prepare --case debugging --variant baseline --output "$eval_root/baseline"
python3 -B evals/run.py prepare --case debugging --variant skill --output "$eval_root/skill"
```

Each run has a `workspace`, `prompt.txt`, and `metadata.json`. Assisted runs also
have a snapshotted `candidate-skill` with hashes. The baseline gets the same task
and starting project without that injected skill. Preparation refuses to overwrite
an existing run. Treat each execution as disposable; prepare a new run to retry.

## Execute with a client

The runner passes the task on stdin and executes the command in the run's
workspace. It captures stdout/stderr and elapsed time outside that workspace.
Use a noninteractive client command that reads stdin. For the locally available
Codex CLI:

```sh
python3 -B evals/run.py run --run "$eval_root/baseline" --timeout 300 -- \
  codex exec --skip-git-repo-check --sandbox workspace-write --ephemeral -
python3 -B evals/run.py run --run "$eval_root/skill" --timeout 300 -- \
  codex exec --skip-git-repo-check --sandbox workspace-write --ephemeral -
```

Other clients can be used through their documented noninteractive command;
verify their flags and stdin behavior first. The runner supplies an isolated
workspace and process timeout, not an OS sandbox: use the client's appropriate
sandbox and permission configuration. It does not modify client configuration.

Use the same client, model, tool access, and settings in each pair. Record the
actual model with the runner's `--model` option; that label records metadata and
does not change the model used by the client. Capture the client version/settings
alongside the results. Global instructions, plugins, and skills may still affect
both variants. Token use defaults to unknown; obtain it from actual client usage
rather than estimating it from log length.

## Grade and compare

```sh
python3 -B evals/run.py grade --run "$eval_root/baseline"
python3 -B evals/run.py grade --run "$eval_root/skill"
python3 -B evals/run.py compare "$eval_root/baseline" "$eval_root/skill"
```

Failed objective checks return nonzero. Inspect `grading.json`, the workspace,
and execution logs to resolve each manual criterion; update its status to `pass`
or `fail` and add the supporting evidence. A missing execution record is not proof
of execution. Compare correctness and scope first, then timing/cost. Repeat pairs
before attributing a difference to the skill; a single win is an observation.

The quality case is recommendations only. The debugging and verification cases
require actual execution. Handoff is explicitly requested, reflecting its normal
invocation policy. No task authorizes publication, deployment, messages, or changes
to the user's global setup.

## Check the evaluation machinery

```sh
python3 -B -m unittest discover -s tests -v
```

The tests prove graders reject the fixture bug, invalid persistence, stale
verification claims, and unauthorized project edits; they also check skill
snapshotting, execution status, and timeout handling. They do not measure model
behavior. No live model comparisons have been bundled as results.
