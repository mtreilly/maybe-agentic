#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cli_version="1.7.0"
agents=()
dry_run=false
update=false

usage() {
  cat <<'EOF'
Usage: ./setup.sh [--agent NAME]... [--update] [--dry-run]

Install selected skills locally in maybe-agentic using Vercel's skills CLI.
Default agents: codex, claude-code, opencode, pi.

  --agent NAME  Select an agent; repeat to select several.
  --update      Update selected installed skills to the latest upstream content.
  --dry-run     Print commands without installing or changing files.
  -h, --help    Show this help.

Requires Node.js, npm/npx, Git, and network access for installation or updates.
EOF
}

while (($#)); do
  case "$1" in
    --agent)
      if (($# < 2)); then
        printf 'Missing name after --agent\n' >&2
        exit 2
      fi
      case "$2" in
        codex|claude-code|opencode|pi) agents+=("$2") ;;
        *) printf 'Unsupported agent: %s\n' "$2" >&2; exit 2 ;;
      esac
      shift 2
      ;;
    --update) update=true; shift ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if ((${#agents[@]} == 0)); then
  agents=(codex claude-code opencode pi)
fi

cd -- "$repo_dir"
export DO_NOT_TRACK=1

run() {
  if "$dry_run"; then
    printf 'DO_NOT_TRACK=1 '
    printf '%q ' "$@"
    printf '\n'
  else
    # Keep the CLI from consuming subsequent entries from skills.txt.
    "$@" < /dev/null
  fi
}

if ! "$dry_run"; then
  for executable in node npm npx git; do
    if ! command -v "$executable" >/dev/null 2>&1; then
      printf 'Required executable not found: %s\n' "$executable" >&2
      exit 1
    fi
  done
fi

printf 'Skill workspace: %s\n' "$repo_dir"
while read -r source skill extra; do
  [[ -z "$source" || "$source" == \#* ]] && continue
  if [[ -z "$skill" || -n "$extra" ]]; then
    printf 'Invalid skills.txt entry: expected SOURCE SKILL\n' >&2
    exit 2
  fi
  if "$update" && [[ "$source" != ./* ]]; then
    run npx --yes "skills@$cli_version" update "$skill" --project --yes
  else
    # Local skills are refreshed from our maintained source even during updates.
    run npx --yes "skills@$cli_version" add "$source" --skill "$skill" --agent "${agents[@]}" --yes
  fi
done < "$repo_dir/skills.txt"

run npx --yes "skills@$cli_version" list --agent "${agents[@]}"
