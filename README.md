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

Our own skills:

- [ui-performance](skills/ui-performance/SKILL.md): diagnose rendering, animation, and scrolling bottlenecks using guidance adapted from Emil's performance cheatsheet.
- [systematic-debugging](skills/systematic-debugging/SKILL.md): investigate bugs, test and build failures, flaky behavior, and integrations using a root-cause workflow adapted from Superpowers.

The CLI keeps a canonical copy under `.agents/skills/`, with project-local links for clients that use another directory. This installation targets Codex, Claude Code, OpenCode, and Pi. It is local to this directory; global agent configuration has not been changed.

## Install or refresh client links

Run the setup script from this directory (or invoke it by absolute path from anywhere):

```sh
./setup.sh
./setup.sh --dry-run
./setup.sh --agent codex --agent claude-code
```

The default targets are Codex, Claude Code, OpenCode, and Pi. Installation requires Node.js, npm/npx, Git, and network access. Add repository/skill pairs to `skills.txt` to expand the selection. Setup installs the latest upstream content and refreshes client links; it does not restore a historical snapshot from the lockfile. Repeated runs may replace upstream-managed files.

Maintain our own skills in `skills/<name>/` and add `./skills/<name> <name>` to `skills.txt`. Setup installs a discoverable copy and client links through the CLI. Edit the source under `skills/`, then rerun setup to refresh the installed copy.

## Updates

```sh
./setup.sh --update
```

Updates are on demand; no automatic schedule is configured. The CLI records upstream provenance and content hashes in `skills-lock.json`. Review changes to the installed files and lockfile before committing an update. Keep personal customizations separate from upstream-managed files, which can be replaced during updates.

During updates, local skills are reinstalled from our maintained `skills/` directories, preserving the source files rather than replacing them with upstream content.

`--agent` selects client links during installation and filters the final listing. Updates change the shared skill content for every linked client; newly selected clients need a normal setup run to create their links.

## Inspect

```sh
DO_NOT_TRACK=1 npx --yes skills@1.7.0 list --agent codex claude-code opencode pi
```

Start an agent in this directory and ask it to use `break-ui` on a specific component or screen. Existing sessions may need a new turn or restart to discover the installation.
