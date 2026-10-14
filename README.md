# maybe-agentic

Selected skills managed with Vercel's skills CLI. CLI commands use version 1.7.0 so setup tooling changes are explicit.

## Installed

Selected skills from [emilkowalski/skills](https://github.com/emilkowalski/skills), including their supporting files:

- [animate](.agents/skills/animate/SKILL.md)
- [animate-expo](.agents/skills/animate-expo/SKILL.md)
- [animation-vocabulary](.agents/skills/animation-vocabulary/SKILL.md)
- [break-ui](.agents/skills/break-ui/SKILL.md)
- [emil-design-eng](.agents/skills/emil-design-eng/SKILL.md)
- [find-animation-opportunities](.agents/skills/find-animation-opportunities/SKILL.md)
- [improve-animations](.agents/skills/improve-animations/SKILL.md)
- [mobile-native](.agents/skills/mobile-native/SKILL.md)
- [prototype](.agents/skills/prototype/SKILL.md)
- [review-animations](.agents/skills/review-animations/SKILL.md)
- [write-swift](.agents/skills/write-swift/SKILL.md)

From [warpdotdev/common-skills](https://github.com/warpdotdev/common-skills):

- [skill-doctor](.agents/skills/skill-doctor/SKILL.md): grade skills by scoring recent local agent conversations, then draft skill edits and a local HTML report. Invoke with `/skill-doctor`. Included in the `research` profile (`./setup.sh --profile research`).

Our own skills:

- [ui-performance](skills/ui-performance/SKILL.md): diagnose rendering, animation, and scrolling bottlenecks using guidance adapted from Emil's performance cheatsheet.
- [systematic-debugging](skills/systematic-debugging/SKILL.md): investigate bugs, test and build failures, flaky behavior, and integrations using guidance adapted from Superpowers and Matt Pocock.
- [codebase-design](skills/codebase-design/SKILL.md): improve interfaces and concentrate complexity, changes, and verification using guidance adapted from Matt Pocock.
- [handoff](skills/handoff/SKILL.md): save scope, authorization, verified state, artifact pointers, and next actions for another session.
- [teach](skills/teach/SKILL.md): teach through focused lessons, practice, feedback, and optional persistent learning records.
- [wait-what](skills/wait-what/SKILL.md): re-explain a confusing message in plain language with the missing context.

`handoff`, `teach`, and `wait-what` preserve upstream's explicit invocation settings for Codex and Claude Code. Invoke them by name, such as `$teach` in Codex or `/teach` in Claude Code. Pi and OpenCode may handle invocation settings differently; request the named skill through the client's supported mechanism. The other maintained skills allow automatic selection when relevant.

Setup installs globally for the current user by default, with a canonical copy under `~/.agents/skills/` and client links in their user-level skill directories. This targets Codex, Claude Code, OpenCode, and Pi across projects. Use `--local` to install under this repository’s `.agents/skills/` instead. The skill links above refer to the existing repository-local copies.

## Portable pstack and cleanup skills

These locally maintained adaptations are self-contained. Supporting references and scripts are bundled; they do not require sibling skills, Cursor plugins, named models, or Cursor transcript paths. Delegation is optional and follows the active session authorization.

- [create-verification-skill](skills/create-verification-skill/SKILL.md)
- [maintain-verification-skill](skills/maintain-verification-skill/SKILL.md)
- [benchmark-checklist](skills/benchmark-checklist/SKILL.md)
- [correct](skills/correct/SKILL.md)
- [blast-radius](skills/blast-radius/SKILL.md)
- [show-me-your-work](skills/show-me-your-work/SKILL.md)
- [how](skills/how/SKILL.md)
- [why](skills/why/SKILL.md)
- [architect](skills/architect/SKILL.md)
- [interrogate](skills/interrogate/SKILL.md)
- [reflect](skills/reflect/SKILL.md)
- [automate-me](skills/automate-me/SKILL.md)
- [poteto-mode](skills/poteto-mode/SKILL.md)
- [deslop-code](skills/deslop-code/SKILL.md)
- [deslop-writing](skills/deslop-writing/SKILL.md)

`deslop-code` adapts Cursor Team Kit’s `deslop`; `deslop-writing` adapts pstack’s `unslop`. `poteto-mode` is a smaller portable edition, activated by a request to use that mode. Provenance and upstream licenses are included in each skill folder. Upstream refreshes do not automatically replace these adaptations.

## Project quality skills

Locally maintained skills inspired by the executable checks in `withcontext`:

- [project-quality-setup](skills/project-quality-setup/SKILL.md): Recommend or implement a proportionate code-quality setup after inspecting a project’s stack, existing checks, and failure risks.
- [architecture-guardrails](skills/architecture-guardrails/SKILL.md): Make established project architecture rules enforceable through types, import boundaries, contract checks, or small static checks.
- [quality-gate-audit](skills/quality-gate-audit/SKILL.md): Audit whether a project’s lint, type, test, and validation gates check the intended inputs and report trustworthy results.
- [artifact-integrity](skills/artifact-integrity/SKILL.md): Recommend or implement deterministic integrity checks for documentation, schemas, configuration, localization, datasets, or agent setup artifacts.

## Install or refresh client links

Run the setup script from this directory (or invoke it by absolute path from anywhere):

```sh
./setup.sh                         # core profile
./setup.sh --profile frontend
./setup.sh --profile backend --profile research
./setup.sh --profile all             # complete manifest
./setup.sh --dry-run
./setup.sh --local
./setup.sh --agent codex --agent claude-code
```

The default profile is `core` (eight skills); the default clients are Codex, Claude Code, OpenCode, and Pi. Profiles select what is installed or updated. Existing extra skills remain discoverable until explicitly removed; profile selection does not uninstall skills. Installation requires Python 3, Node.js, npm/npx, Git, and network access. Use `--profile frontend`, `--profile backend`, or `--profile research` to extend the default core selection; repeat `--profile` to combine profiles, or use `--profile all` for the full catalog. Add repository/skill pairs to `skills.txt` to expand the selection. Setup installs the latest upstream content and refreshes client links; it does not restore a historical snapshot from the lockfile. Repeated runs may replace upstream-managed files.

Maintain our own skills in `skills/<name>/` and add `./skills/<name> <name>` to `skills.txt`. Setup installs a discoverable copy and client links through the CLI. Edit the source under `skills/`, then rerun setup to refresh the installed copy.

## Updates

```sh
./setup.sh --update --profile all
./setup.sh --local --update
./setup.sh --update --skill blast-radius  # refresh one skill for all default clients
```

Updates are on demand; no automatic schedule is configured. Global installs track upstream provenance and content hashes in `~/.agents/.skill-lock.json`; local installs use `skills-lock.json` in this repository. Review changes to locally installed files and the project lockfile before committing an update. Updates and the final listing use the selected scope. Keep personal customizations separate from upstream-managed files, which can be replaced during updates.

Both setup and `--update` reinstall the selected entries from their declared sources, refreshing content, creating missing installs, and repairing selected client links. Local skills come from our maintained `skills/` directories; upstream skills come from their repositories. `--update` makes the refresh intent explicit; a normal setup run also refreshes content.

Use repeated `--skill NAME` flags to refresh specific manifest entries. Without `--profile`, names are selected from the entire manifest; with profiles, names must belong to the combined profile selection. All names are validated before installation starts.

`--agent` selects client links during setup and updates and filters the final listing. Refreshing shared skill content affects every client linked to that copy.

## Profiles and doctor

Profiles live in `profiles/*.json` and select names from `skills.txt`. `frontend`,
`backend`, and `research` inherit `core`; repeat `--profile` to combine them.
`all` selects the complete manifest. Selection is validated before installation.
Update runs respect the selected profile too.

```sh
./doctor.sh
./doctor.sh --global --profile all
./doctor.sh --local --profile all
./doctor.sh --profile frontend --agent codex --agent claude-code --json
```

Doctor defaults to the global installation, matching setup. Use `--local` to
inspect this repository's installed copies. It needs only Python 3 and is
read-only. It checks profile/manifest validity,
required frontmatter, bundled Markdown links, local source/install drift,
the selected scope's lock entries, client links, and executable availability.
Global checks use `~/.agents/skills` and `~/.agents/.skill-lock.json`
(or `$XDG_STATE_HOME/skills/.skill-lock.json` when configured). The pinned CLI
omits global lock records for local-source installs; doctor compares those copies
to our source files and requires lock records for upstream selections.
Claude's link directory honors `CLAUDE_CONFIG_DIR`; additional Codex/OpenCode
discovery candidates honor `CODEX_HOME` and `XDG_CONFIG_HOME`. Codex/OpenCode
use the shared canonical root under the pinned installer; Pi's installer links
live under `~/.pi/agent/skills`.

Text output names each selected skill's resolved filesystem source per client.
JSON includes expected installation paths, present/missing/broken discovery
candidates, and competing-source warnings. Competing copies are reported without
inferring runtime precedence. Global checks do not model project overrides or
custom skill paths configured inside a client. Extra installed
skills are reported and preserved. It never installs, repairs, or contacts a
provider. Passing validates the selected scope and filesystem resolution, not live client loading, full YAML
semantics, upstream freshness, or behavioral usefulness.

## Skill evaluations

[The evaluation suite](evals/README.md) contains paired baseline/skill tasks for
debugging, project quality setup, handoff, and CLI verification. It prepares
isolated workspaces, snapshots the selected skill, captures client output and
elapsed time, and grades concrete outputs. Human review covers judgment and
execution evidence that the objective checks cannot establish. Routing prompts
include requests where these skills should stay inactive.

```sh
python3 -B -m unittest discover -s tests -v
```

These regressions validate the toolkit and graders. Live model comparisons are
separate experiments; fixture passes do not prove that a skill improves results.

## Inspect

```sh
DO_NOT_TRACK=1 npx --yes skills@1.7.0 list --global --agent codex claude-code opencode pi
```

Start an agent in any project after a global installation and ask it to use `break-ui` on a specific component or screen. Existing sessions may need a new turn or restart to discover the installation.

## License

MIT, see `LICENSE`. Vendored third-party material keeps its original license; see `THIRD_PARTY_NOTICES.md`.
