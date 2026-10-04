#!/usr/bin/env python3
"""Read-only installed-skill and profile health check. Never installs or repairs."""
import sys
sys.dont_write_bytecode = True
import argparse
import json
import os
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


def paths(scope):
    """Expected installer roots for the pinned skills CLI 1.7.0."""
    home = Path.home()
    canonical = (home if scope == 'global' else ROOT) / '.agents' / 'skills'
    if scope == 'global':
        claude = Path(os.environ.get('CLAUDE_CONFIG_DIR', '').strip() or home / '.claude') / 'skills'
        codex = Path(os.environ.get('CODEX_HOME', '').strip() or home / '.codex') / 'skills'
        opencode = Path(os.environ.get('XDG_CONFIG_HOME', '').strip() or home / '.config') / 'opencode' / 'skills'
        pi = home / '.pi' / 'agent' / 'skills'
        state_home = os.environ.get('XDG_STATE_HOME', '').strip()
        lock = Path(state_home) / 'skills' / '.skill-lock.json' if state_home else home / '.agents' / '.skill-lock.json'
        roots = {'codex': canonical, 'opencode': canonical, 'claude-code': claude, 'pi': pi}
        candidates = {'codex': [canonical, codex], 'opencode': [canonical, opencode],
                      'claude-code': [claude], 'pi': [pi, canonical]}
    else:
        lock = ROOT / 'skills-lock.json'
        roots = {agent: ROOT / directory / 'skills' for agent, directory in AGENTS.items()}
        candidates = {agent: [directory] for agent, directory in roots.items()}
    return canonical, lock, roots, candidates


def candidate(path):
    state, source = 'missing', None
    try:
        if path.is_symlink() and not path.exists():
            state = 'broken'
        elif (path / 'SKILL.md').is_file():
            state, source = 'present', str(path.resolve())
        elif path.exists():
            state = 'invalid'
    except (OSError, RuntimeError):
        state = 'broken'
    return {'path': str(path), 'state': state, 'resolved_source': source}


def check(profiles, agents, scope):
    errors, warnings = [], []
    entries = manifest()
    selected = select(profiles)
    for profile in sorted((ROOT / 'profiles').glob('*.json')):
        select([profile.stem])
    canonical, lock_path, roots, candidate_roots = paths(scope)
    if lock_path.is_file():
        lock = json.loads(lock_path.read_text())
        if not isinstance(lock, dict) or not isinstance(lock.get('skills'), dict):
            raise ValueError(f'invalid lockfile structure: {lock_path}')
        locked = lock['skills']
    else:
        locked = {}
        if scope == 'local' or any(not source.startswith('./') for source in selected.values()):
            errors.append(f'missing {scope} lockfile: {lock_path}')
    for name, source in entries.items():
        if source.startswith('./'):
            errors.extend(skill_checks(ROOT / source, name))
    installed = {entry.name for entry in canonical.iterdir()} if canonical.is_dir() else set()
    unmanaged = sorted(installed - set(entries))
    for name in sorted(installed & set(entries)):
        directory = canonical / name
        info = candidate(directory)
        if info['state'] != 'present':
            errors.append(f'{name}: broken canonical skill or unexpected file')
            continue
        errors.extend(skill_checks(directory, name))
        if entries[name].startswith('./') and files(ROOT / entries[name]) != files(directory):
            errors.append(f'{name}: installed copy differs from maintained source; refresh {scope} setup')
    resolutions = {agent: {} for agent in agents}
    for name in selected:
        if name not in installed:
            errors.append(f'{name}: selected skill is not installed in {scope} scope')
        # CLI 1.7.0 records global remote sources, but intentionally omits
        # local-source installs. Their installed bytes are compared above.
        if name not in locked and (scope == 'local' or not selected[name].startswith('./')):
            errors.append(f'{name}: missing {scope} lockfile entry')
        expected = candidate(canonical / name)
        for agent in agents:
            installation = candidate(roots[agent] / name)
            locations = [candidate(directory / name) for directory in candidate_roots[agent]]
            sources = {item['resolved_source'] for item in locations if item['state'] == 'present'}
            ambiguous = len(sources) > 1
            resolutions[agent][name] = {'installation_path': installation['path'],
                                       'resolved_source': installation['resolved_source'],
                                       'candidates': locations, 'ambiguous': ambiguous}
            if installation['state'] != 'present' or installation['resolved_source'] != expected['resolved_source']:
                errors.append(f'{name}: {agent} link missing, broken, or points to a different owner ({installation["path"]})')
            for location in locations:
                if location['state'] in ['broken', 'invalid']:
                    errors.append(f'{name}: {agent} discovery entry is {location["state"]}: {location["path"]}')
            if ambiguous:
                warnings.append(f'{name}: {agent} has competing discovery sources; runtime precedence is not inferred')
    # Only this manifest's entries are required; foreign installations are left alone.
    for directory in set(roots[agent] for agent in agents) - {canonical}:
        if directory.is_dir():
            for entry in directory.iterdir():
                if entry.is_symlink() and not entry.exists():
                    message = f'{directory}: broken skill link {entry.name}'
                    (errors if entry.name in entries else warnings).append(message)
    tools = {tool: bool(shutil.which(tool)) for tool in ['python3', 'node', 'npm', 'npx', 'git', 'codex', 'claude', 'opencode', 'pi']}
    for tool in ['node', 'npm', 'npx', 'git']:
        if not tools[tool]:
            warnings.append(f'{tool}: missing; required for installation, not doctor')
    for agent in agents:
        command = 'claude' if agent == 'claude-code' else agent
        if not tools[command]:
            warnings.append(f'{command}: client CLI unavailable; discovery cannot be exercised')
    return {'status': 'fail' if errors else 'pass', 'scope': scope, 'root': str(ROOT),
            'canonical_root': str(canonical), 'lockfile': str(lock_path),
            'profiles': profiles or ['core'], 'agents': agents, 'selected': list(selected),
            'extra_installed': sorted(installed - set(selected)), 'unmanaged_installed': unmanaged,
            'unlocked_local': [name for name, source in selected.items() if scope == 'global' and source.startswith('./') and name not in locked],
            'resolutions': resolutions, 'tools': tools, 'errors': errors, 'warnings': warnings,
            'limits': 'Reports filesystem resolution in the selected scope using installer 1.7.0 paths. Does not infer runtime precedence, project overrides during global checks, custom client skill paths, live client loading, full YAML semantics, upstream freshness, or skill behavior.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', default=[])
    parser.add_argument('--agent', action='append', choices=AGENTS, default=[])
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument('--global', dest='scope', action='store_const', const='global')
    scope.add_argument('--local', dest='scope', action='store_const', const='local')
    parser.set_defaults(scope='global')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        report = check(args.profile, args.agent or list(AGENTS), args.scope)
    except (OSError, ValueError, RuntimeError) as error:
        report = {'status': 'fail', 'errors': [str(error)], 'warnings': []}
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Doctor ({args.scope}): {report['status'].upper()}")
        for kind in ['errors', 'warnings']:
            for message in report[kind]:
                print(f"{kind[:-1].upper()}: {message}")
        if 'selected' in report:
            print(f"Selected: {len(report['selected'])}; extra installed: {len(report['extra_installed'])} (retained)")
            for agent, skills in report['resolutions'].items():
                for name, resolution in skills.items():
                    print(f"SOURCE {agent}/{name}: {resolution['resolved_source'] or 'missing'}" + (' (competing sources)' if resolution['ambiguous'] else ''))
            print(report['limits'])
    return 1 if report['status'] == 'fail' else 0


if __name__ == '__main__':
    raise SystemExit(main())
