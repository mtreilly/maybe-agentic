#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cli_version="1.7.0"
agents=()
profiles=()
skills=()
dry_run=false
update=false
scope=global

usage() {
  cat <<'EOF'
Usage: ./setup.sh [--global | --local] [--profile NAME]... [--skill NAME]... [--agent NAME]... [--update] [--dry-run]

Install selected skills globally for the current user using Vercel's skills CLI.
Default agents: codex, claude-code, opencode, pi.

  --profile NAME  Select core (default), frontend, backend, research, or all. Repeat to combine.
  --skill NAME  Select a manifest skill; repeat for several. Filters profiles when supplied.
  --agent NAME  Select an agent; repeat to select several.
  --global      Install, update, and list user-level skills (default).
  --local       Install, update, and list project-level skills in maybe-agentic.
  --update      Refresh selected skills from declared sources, including missing installs and client links.
  --dry-run     Print commands without installing or changing files.
  -h, --help    Show this help.

Profiles select installation/update entries; existing extra skills are retained.
Requires Python 3, Node.js, npm/npx, Git, and network access for installation or updates.
EOF
}

while (($#)); do
  case "$1" in
    --profile)
      if (($# < 2)); then printf "Missing name after --profile\n" >&2; exit 2; fi
      profiles+=(--profile "$2")
      shift 2
      ;;
    --skill)
      if (($# < 2)); then printf "Missing name after --skill\n" >&2; exit 2; fi
      skills+=(--skill "$2")
      shift 2
      ;;
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
    --global) scope=global; shift ;;
    --local) scope=local; shift ;;
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

# Validate the entire selection before any CLI invocation; no partial installation
# when a profile is malformed. Command substitution preserves parser exit status.
selection="$(python3 -B "$repo_dir/scripts/catalog.py" "${profiles[@]}" "${skills[@]}")"

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

install_args=()
if [[ "$scope" == global ]]; then
  install_args=(--global)
fi

if "$update"; then printf 'Refreshing selected skills from declared sources.\n'; fi

printf 'Skill source: %s\nInstallation scope: %s\n' "$repo_dir" "$scope"
while read -r source skill extra; do
  [[ -z "$source" || "$source" == \#* ]] && continue
  if [[ -z "$skill" || -n "$extra" ]]; then
    printf 'Invalid skills.txt entry: expected SOURCE SKILL\n' >&2
    exit 2
  fi
  # Reinstall from the manifest so updates also repair links and install missing
  # skills. Both modes refresh upstream content and our maintained local sources.
  run npx --yes "skills@$cli_version" add "$source" --skill "$skill" --agent "${agents[@]}" "${install_args[@]}" --yes
done <<< "$selection"

run npx --yes "skills@$cli_version" list --agent "${agents[@]}" "${install_args[@]}"
