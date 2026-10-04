#!/usr/bin/env python3
"""Read-only installed-skill and profile health check. Never installs or repairs."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import re
import shutil
from pathlib import Path
from urllib.parse import unquote
from catalog import ROOT, manifest, select

AGENTS = {'codex': '.agents', 'opencode': '.agents', 'claude-code': '.claude', 'pi': '.pi'}


def skill_checks(directory, name):
    issues = []
    file = directory / 'SKILL.md'
    if not file.is_file():
        return [f'{name}: missing {file}']
    text = file.read_text()
    header = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not header:
        return [f'{name}: SKILL.md requires YAML frontmatter']
    fields = dict(re.findall(r'^([\w-]+):[ \t]*(.*)$', header.group(1), re.M))
    if fields.get('name', '').strip('"\' ') != name:
        issues.append(f'{name}: frontmatter name does not match directory')
    description = fields.get('description', '').strip()
    if not description or description in ['""', "''"]:
        issues.append(f'{name}: missing description')
    # Check local Markdown resource links, not prose/backticks or external URLs.
    for document in directory.rglob('*.md'):
        for target in re.findall(r'\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)', document.read_text()):
            target = unquote(target.strip('<>').split('#', 1)[0])
            if not target or target.startswith('/') or re.match(r'^[\w+.-]+:', target):
                continue
            resource = (document.parent / target).resolve()
            if not resource.is_relative_to(directory.resolve()):
                issues.append(f'{name}: resource link leaves skill bundle: {target}')
            elif not resource.exists():
                issues.append(f'{name}: missing linked resource: {target}')
    return issues


def files(directory):
    return {str(file.relative_to(directory)): file.read_bytes() for file in directory.rglob('*') if file.is_file()}


def check(profiles, agents):
    errors, warnings = [], []
    entries = manifest()
    selected = select(profiles)
    for profile in sorted((ROOT / 'profiles').glob('*.json')):
        select([profile.stem])
    lock = json.loads((ROOT / 'skills-lock.json').read_text())
    locked = lock.get('skills', {})
    for name, source in entries.items():
        if source.startswith('./'):
            errors.extend(skill_checks(ROOT / source, name))
    canonical = ROOT / '.agents' / 'skills'
    installed = {entry.name for entry in canonical.iterdir()} if canonical.is_dir() else set()
    for name in sorted(installed):
        directory = canonical / name
        if not directory.is_dir():
            errors.append(f'{name}: broken canonical skill or unexpected file')
            continue
        errors.extend(skill_checks(directory, name))
        if name not in entries:
            warnings.append(f'{name}: installed outside the managed manifest')
        elif entries[name].startswith('./') and files(ROOT / entries[name]) != files(directory):
            errors.append(f'{name}: installed copy differs from maintained source; refresh setup')
    for name in selected:
        if name not in installed:
            errors.append(f'{name}: selected skill is not installed')
        if name not in locked:
            errors.append(f'{name}: missing lockfile entry')
        for agent in agents:
            if AGENTS[agent] == '.agents':
                continue
            link = ROOT / AGENTS[agent] / 'skills' / name
            if not link.is_symlink() or link.resolve() != (canonical / name).resolve():
                errors.append(f'{name}: {agent} link missing, broken, or points to a different owner')
    for directory_name in set(AGENTS.values()) - {'.agents'}:
        directory = ROOT / directory_name / 'skills'
        if directory.is_dir():
            for entry in directory.iterdir():
                if entry.is_symlink() and not entry.exists():
                    errors.append(f'{directory_name}: broken skill link {entry.name}')
                elif entry.name not in entries:
                    warnings.append(f'{directory_name}/{entry.name}: unmanaged entry; preserved')
    tools = {tool: bool(shutil.which(tool)) for tool in ['python3', 'node', 'npm', 'npx', 'git', 'codex', 'claude', 'opencode', 'pi']}
    for tool in ['node', 'npm', 'npx', 'git']:
        if not tools[tool]:
            warnings.append(f'{tool}: missing; required for installation, not doctor')
    for agent in agents:
        command = 'claude' if agent == 'claude-code' else agent
        if not tools[command]:
            warnings.append(f'{command}: client CLI unavailable; discovery cannot be exercised')
    return {'status': 'fail' if errors else 'pass', 'scope': 'project', 'root': str(ROOT), 'profiles': profiles or ['core'], 'agents': agents,
            'selected': list(selected), 'extra_installed': sorted(installed - set(selected)),
            'tools': tools, 'errors': errors, 'warnings': warnings,
            'limits': 'Checks files and expected discovery paths, not live client loading, full YAML semantics, upstream freshness, or skill behavior.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', default=[])
    parser.add_argument('--agent', action='append', choices=AGENTS, default=[])
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        report = check(args.profile, args.agent or list(AGENTS))
    except (OSError, ValueError) as error:
        report = {'status': 'fail', 'errors': [str(error)], 'warnings': []}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Doctor: {report['status'].upper()}")
        for kind in ['errors', 'warnings']:
            for message in report[kind]:
                print(f"{kind[:-1].upper()}: {message}")
        if 'selected' in report:
            print(f"Selected: {len(report['selected'])}; extra installed: {len(report['extra_installed'])} (retained)")
            print(report['limits'])
    return 1 if report['status'] == 'fail' else 0


if __name__ == '__main__':
    raise SystemExit(main())
