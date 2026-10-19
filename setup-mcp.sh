#!/usr/bin/env bash
# Install the MCP servers in mcp/servers.json and register them with
# Codex, Claude Code, OpenCode and Pi. See README "MCP servers".
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 -B "$repo_dir/scripts/mcp.py" "$@"
