#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

git -C "$repo_dir" pull --ff-only
exec "$repo_dir/setup.sh" --global --update --profile all
