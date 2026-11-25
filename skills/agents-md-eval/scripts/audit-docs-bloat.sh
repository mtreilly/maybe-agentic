#!/usr/bin/env bash
# Read-only audit of markdown/doc bloat and code/script/test/CI references.
set -euo pipefail

REPO="${1:-.}"
REF="${2:-HEAD}"

REPO_ABS="$(cd "$REPO" && pwd -P)"
git -C "$REPO_ABS" rev-parse --verify "$REF^{commit}" >/dev/null

python3 - "$REPO_ABS" "$REF" <<'PY'
import collections
import pathlib
import subprocess
import sys

repo = sys.argv[1]
ref = sys.argv[2]

def git(*args):
    return subprocess.check_output(["git", "-C", repo, *args], text=True, errors="replace")

ls = git("ls-tree", "-r", "-l", ref)
root_mds = []
dir_stats = collections.defaultdict(lambda: [0, 0])  # [count, bytes]
all_md_count = 0
all_md_bytes = 0

for line in ls.splitlines():
    if not line.strip():
        continue
    meta, path = line.split("\t", 1)
    parts = meta.split()
    size = int(parts[3]) if parts[3].isdigit() else 0
    if path.endswith(".md") or path.startswith(("docs/", "agents/")):
        all_md_count += 1
        all_md_bytes += size
        if "/" not in path and path.endswith(".md"):
            root_mds.append((path, size))
        else:
            segs = path.split("/")
            bucket = "/".join(segs[:2]) if len(segs) >= 2 else segs[0]
            dir_stats[bucket][0] += 1
            dir_stats[bucket][1] += size

def code_refs(pattern):
    # Count references outside markdown and the candidate itself
    proc = subprocess.run(
        [
            "git", "-C", repo, "grep", "-l", "-F", pattern, ref, "--",
            ":!*.md",
        ],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return []
    return [line.split(":", 1)[1] for line in proc.stdout.splitlines() if ":" in line]

def doc_refs(pattern, exclude_prefix):
    proc = subprocess.run(
        ["git", "-C", repo, "grep", "-l", "-F", pattern, ref, "--", "*.md"],
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        return []
    hits = []
    for line in proc.stdout.splitlines():
        if ":" not in line:
            continue
        p = line.split(":", 1)[1]
        if p == exclude_prefix or p.startswith(exclude_prefix + "/"):
            continue
        hits.append(p)
    return hits

print(f"=== Doc Audit: {repo} ({ref}) ===")
print(f"Total tracked markdown / docs / agents files: {all_md_count} ({all_md_bytes/1024:.1f} KB)\n")

print("--- Root *.md files ---")
for path, size in sorted(root_mds, key=lambda x: -x[1]):
    c_refs = code_refs(path)
    d_refs = doc_refs(path, path)
    flag = "KEEP (core)" if path in {"AGENTS.md", "CLAUDE.md", "README.md", "CHANGELOG.md", "CONTRIBUTING.md"} else (
        "ZERO-REF CANDIDATE" if not c_refs and not d_refs else "REFERENCED"
    )
    print(f"  {path:<38} {size/1024:7.1f} KB | code_refs={len(c_refs):<2} doc_refs={len(d_refs):<2} | {flag}")

print("\n--- Top folders under docs/, agents/, and nested *.md (by size) ---")
for bucket, (count, size) in sorted(dir_stats.items(), key=lambda x: -x[1][1])[:25]:
    c_refs = code_refs(bucket)
    d_refs = doc_refs(bucket, bucket)
    print(f"  {bucket:<42} {count:4d} files {size/1024:8.1f} KB | code_refs={len(c_refs):<2} doc_refs={len(d_refs):<2}")
PY
