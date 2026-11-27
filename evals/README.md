# Skill evaluations

Seven small tasks exercise outcomes that matter:

| Case | Candidate skill | Objective checks | Human review |
| --- | --- | --- | --- |
| debugging | systematic-debugging | Zero-percent coupon works; invalid percentages still fail | Reproduction, causal diagnosis, focused edits |
| quality | project-quality-setup | Existing command and omitted workspace identified; proposal present; project preserved with no extra files | Recommendation is runnable, proportionate, and justified |
| handoff | handoff | Plan resolves; scope/continuation recorded; old passing check stays historical | Faithful authorization, useful next action, accuracy |
| verification | verification-skill | Skill body and feature map exist; scratch removed; grader-owned CLI replay proves persistence across processes | Actionable skill/map and evidence that the candidate actually executed it |
| blast-radius | blast-radius | Identifies alternate `share_link.py` revocation bypass; records unproved assumptions; read-only | Traces beyond diff and names cheapest check |
| prune-tests | prune-tests | Removes private `_items` assertion; deletes duplicate; surviving tests pass and catch mutations | Preserves distinct regression coverage |
| design-review | design-review | Quick-mode review preserves HTML, uses valid evidence labels, catches real defects, records `not_evaluated` limits | Calibrated severity and honest medium limits |

Objective passes are partial evidence. The grader leaves manual criteria pending
and never turns them into an overall quality verdict. The verification grader
re-executes the CLI recipe against a fresh grader-owned copy of `notes.py`; this
does not establish that the candidate ran it earlier.
The fixtures are intentionally small, so improvement here needs confirmation on
real projects.

`cases.json` also contains 22 routing prompts covering collision clusters,
explicit-only skills, and negative controls. Validate routing definitions with:

```sh
python3 -B evals/run.py routing
```

Live client routing still requires exercising those prompts through each
client's real skill-discovery mechanism separately. Explicit skill injection in
the task runner does not test automatic discovery.

## Prepare an isolated pair

Run from the toolkit root. Keep runs outside `maybe-agentic` so its project skill
installation does not contaminate the baseline:

```sh
eval_root="$(mktemp -d "${TMPDIR:-/tmp}/maybe-evals.XXXXXX")"
python3 -B evals/run.py prepare --case debugging --variant baseline --output "$eval_root/baseline"
python3 -B evals/run.py prepare --case debugging --variant skill --output "$eval_root/skill"
```

Each run has a `workspace`, `prompt.txt`, and `metadata.json`. Assisted runs also
have a snapshotted `candidate-skill` with hashes. The baseline gets the same task
and starting project without that injected skill. Preparation refuses to overwrite
an existing run.

## Execute with a client

```sh
python3 -B evals/run.py run --run "$eval_root/baseline" --timeout 300 -- \
  codex exec --skip-git-repo-check --sandbox workspace-write --ephemeral -
python3 -B evals/run.py run --run "$eval_root/skill" --timeout 300 -- \
  codex exec --skip-git-repo-check --sandbox workspace-write --ephemeral -
```

## Grade and compare

```sh
python3 -B evals/run.py grade --run "$eval_root/baseline"
python3 -B evals/run.py grade --run "$eval_root/skill"
python3 -B evals/run.py compare "$eval_root/baseline" "$eval_root/skill"
```

## Check the evaluation machinery

```sh
python3 -B -m unittest discover -s tests -v
```
