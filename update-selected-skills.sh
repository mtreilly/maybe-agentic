#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

exec "$repo_dir/setup.sh" --global --update \
  --skill untangle-codebase \
  --skill find-state-machines \
  --skill plain-voice
