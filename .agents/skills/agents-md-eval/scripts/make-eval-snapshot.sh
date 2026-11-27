#!/usr/bin/env bash
# Create isolated, .git-free evaluation snapshots ("with" and/or "without" AGENTS.md)
# from any git repository ref without touching the live checkout.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: make-eval-snapshot.sh --repo <path> --out <dir> [--ref <git-ref>] [--mode both|with|without] [--strip-secondary-agents]

Options:
  --repo <path>              Path to git repository checkout (required)
  --out <dir>                Fresh output directory outside the repo, e.g. "${TMPDIR:-/tmp}/agents-md-eval-app" (required)
  --ref <git-ref>            Git ref to archive (default: HEAD)
  --mode <both|with|without> Which snapshot arms to materialize (default: both)
  --strip-secondary-agents   Also remove .agents/ from the "without" arm (default: keep .agents/ & docs/)
EOF
}

REPO=""
OUT=""
REF="HEAD"
MODE="both"
STRIP_DOT_AGENTS=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo) REPO="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --ref) REF="$2"; shift 2 ;;
    --mode) MODE="$2"; shift 2 ;;
    --strip-secondary-agents) STRIP_DOT_AGENTS=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$REPO" || -z "$OUT" ]]; then
  usage
  exit 2
fi

if [[ "$MODE" != "both" && "$MODE" != "with" && "$MODE" != "without" ]]; then
  echo "Invalid --mode: $MODE (expected both|with|without)" >&2
  exit 2
fi

REPO_ABS="$(cd "$REPO" && pwd -P)"
git -C "$REPO_ABS" rev-parse --verify "$REF^{commit}" >/dev/null
COMMIT_SHA="$(git -C "$REPO_ABS" rev-parse --short "$REF")"

# Resolve OUT without mutating the filesystem first so overlap checks happen before any write.
OUT_ABS="$(python3 -c 'import os, sys; print(os.path.realpath(sys.argv[1]))' "$OUT")"

case "$OUT_ABS" in
  "$REPO_ABS"|"$REPO_ABS"/*)
    echo "Refusing to create snapshot inside the target repository ($OUT_ABS)." >&2
    exit 2
    ;;
esac

# Validate every requested arm directory before creating or writing anything.
arms=()
if [[ "$MODE" == "both" || "$MODE" == "with" ]]; then arms+=(with); fi
if [[ "$MODE" == "both" || "$MODE" == "without" ]]; then arms+=(without); fi

for arm in "${arms[@]}"; do
  dest="$OUT_ABS/$arm"
  case "$REPO_ABS" in
    "$dest"|"$dest"/*)
      echo "Refusing to target a snapshot path that contains or equals the repository ($dest)." >&2
      exit 2
      ;;
  esac
  if [[ -e "$dest" || -L "$dest" ]]; then
    echo "Refusing to overwrite existing snapshot directory: $dest (use a fresh --out directory)." >&2
    exit 2
  fi
done

mkdir -p "$OUT_ABS"

materialize() {
  local arm="$1"
  local dest="$OUT_ABS/$arm"
  mkdir -p "$dest"
  git -C "$REPO_ABS" archive "$REF" | tar -x -C "$dest"

  # Never leak .git into snapshots
  rm -rf "$dest/.git"

  if [[ "$arm" == "without" ]]; then
    # Strip root and nested AGENTS.md / CLAUDE.md / GEMINI.md plus IDE instruction folders
    find "$dest" -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' -o -name 'GEMINI.md' \) -delete
    rm -rf "$dest/.claude" "$dest/.cursor" "$dest/.cursorrules"
    if [[ "$STRIP_DOT_AGENTS" -eq 1 ]]; then
      rm -rf "$dest/.agents"
    fi
    # Verify zero leaked instruction files
    local leaked
    leaked="$(find "$dest" -type f \( -name 'AGENTS.md' -o -name 'CLAUDE.md' -o -name 'GEMINI.md' \) | head -n 5 || true)"
    if [[ -n "$leaked" ]]; then
      echo "ERROR: leaked instruction files in $dest: $leaked" >&2
      exit 1
    fi
  fi

  local file_count
  file_count="$(find "$dest" -type f | wc -l | tr -d ' ')"
  local agents_info="stripped"
  if [[ -f "$dest/AGENTS.md" ]]; then
    local lines bytes
    lines="$(wc -l < "$dest/AGENTS.md" | tr -d ' ')"
    bytes="$(wc -c < "$dest/AGENTS.md" | tr -d ' ')"
    agents_info="AGENTS.md (${lines} lines, ${bytes} bytes)"
  fi
  printf "  %-8s %s  [ref=%s %s | files=%s | %s]\n" "$arm" "$dest" "$REF" "$COMMIT_SHA" "$file_count" "$agents_info"
}

echo "Created isolated eval snapshot(s) from $REPO_ABS ($REF @ $COMMIT_SHA):"
for arm in "${arms[@]}"; do
  materialize "$arm"
done
