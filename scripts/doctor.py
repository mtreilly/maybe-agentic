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


def parse_frontmatter(block):
    """Parse flat YAML frontmatter including folded/literal multiline scalars."""
    fields = {}
    errors = []
    lines = block.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith('#'):
            index += 1
            continue
        if line[0] in ' \t':
            errors.append(f'unexpected indentation in frontmatter: {line.strip()!r}')
            index += 1
            continue
        match = re.match(r'^([\w-]+):(?:[ \t]+(.*)|[ \t]*)$', line)
        if not match:
            errors.append(f'malformed frontmatter line: {line!r}')
            index += 1
            continue
        key, raw = match.group(1), (match.group(2) or '').strip()
        if raw in ('>', '>-', '|', '|-'):
            collected = []
            index += 1
            while index < len(lines):
                nxt = lines[index]
                if nxt == '' or nxt[0] in ' \t':
                    collected.append(nxt.strip())
                    index += 1
                else:
                    break
            joiner = '\n' if raw.startswith('|') else ' '
            fields[key] = joiner.join(part for part in collected if part).strip()
            continue
        if (raw.startswith('"') and not raw.endswith('"')) or (raw.startswith("'") and not raw.endswith("'")):
            errors.append(f'unterminated quoted value for frontmatter key {key!r}')
        elif len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in ('"', "'"):
            raw = raw[1:-1]
        fields[key] = raw.strip()
        index += 1
    return fields, errors


def is_executable_entrypoint(path):
    """Return True if a file under scripts/ should have the executable bit set."""
    if path.suffix == '.sh':
        return True
    if path.suffix == '':
        return True
    try:
        head = path.read_bytes()[:64]
    except OSError:
        return False
    return head.startswith(b'#!')


def skill_checks(directory, name, local_source=False):
    issues = []
    file = directory / 'SKILL.md'
    if not file.is_file():
        return [f'{name}: missing {file}']
    text = file.read_text()
    header = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
    if not header:
        return [f'{name}: SKILL.md requires YAML frontmatter']
    fields, fm_errors = parse_frontmatter(header.group(1))
    for error in fm_errors:
        issues.append(f'{name}: {error}')
    if fields.get('name', '') != name:
        issues.append(f'{name}: frontmatter name does not match directory')
    description = fields.get('description', '').strip()
    if not description:
        issues.append(f'{name}: missing description')
    # Check invocation-policy parity between SKILL.md and agents/openai.yaml on local sources.
    if local_source:
        disable_model = fields.get('disable-model-invocation', '').lower() == 'true'
        openai_yaml = directory / 'agents' / 'openai.yaml'
        openai_disables = False
        if openai_yaml.is_file():
            openai_text = openai_yaml.read_text()
            openai_disables = bool(re.search(r'^\s*allow_implicit_invocation:\s*false\b', openai_text, re.M | re.I))
        if disable_model and not openai_disables:
            issues.append(f'{name}: disable-model-invocation is true but agents/openai.yaml does not set allow_implicit_invocation: false')
        elif openai_disables and not disable_model:
            issues.append(f'{name}: agents/openai.yaml sets allow_implicit_invocation: false but SKILL.md omits disable-model-invocation: true')
        scripts_dir = directory / 'scripts'
        if scripts_dir.is_dir():
            for script in sorted(scripts_dir.iterdir()):
                if script.is_file() and is_executable_entrypoint(script) and not os.access(script, os.X_OK):
                    issues.append(f'{name}: script is not executable: scripts/{script.name}')
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


def lock_entry_issues(name, entry, declared_source, scope):
    issues = []
    if not isinstance(entry, dict):
        return [f'{name}: invalid {scope} lockfile entry']
    source = entry.get('source')
    if not isinstance(source, str) or not source.strip():
        issues.append(f'{name}: {scope} lockfile entry missing source')
    elif declared_source.startswith('./'):
        if scope == 'local' and not (source == declared_source or source == './skills'):
            issues.append(f'{name}: {scope} lockfile source {source!r} does not match manifest {declared_source!r}')
    else:
        if source != declared_source:
            issues.append(f'{name}: {scope} lockfile source {source!r} does not match manifest {declared_source!r}')
    digest = entry.get('computedHash') or entry.get('skillFolderHash')
    if not isinstance(digest, str) or not re.fullmatch(r'[0-9a-fA-F]{40,64}', digest):
        issues.append(f'{name}: {scope} lockfile entry has missing or invalid hash')
    return issues


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
            errors.extend(skill_checks(ROOT / source, name, local_source=True))
    installed = {entry.name for entry in canonical.iterdir()} if canonical.is_dir() else set()
    unmanaged = sorted(installed - set(entries))
    if scope == 'global' and unmanaged:
        preview = ', '.join(unmanaged[:5]) + (f' and {len(unmanaged) - 5} more' if len(unmanaged) > 5 else '')
        warnings.append(f'{len(unmanaged)} unmanaged installed skill(s) outside skills.txt may compete for routing: {preview}')
    for name in sorted(installed & set(entries)):
        directory = canonical / name
        info = candidate(directory)
        if info['state'] != 'present':
            errors.append(f'{name}: broken canonical skill or unexpected file')
            continue
        errors.extend(skill_checks(directory, name, local_source=False))
        if entries[name].startswith('./') and files(ROOT / entries[name]) != files(directory):
            errors.append(f'{name}: installed copy differs from maintained source; refresh {scope} setup')
    resolutions = {agent: {} for agent in agents}
    for name in selected:
        if name not in installed:
            errors.append(f'{name}: selected skill is not installed in {scope} scope')
        # CLI 1.7.0 records global remote sources, but intentionally omits
        # local-source installs. Their installed bytes are compared above.
        if name not in locked:
            if scope == 'local' or not selected[name].startswith('./'):
                errors.append(f'{name}: missing {scope} lockfile entry')
        else:
            errors.extend(lock_entry_issues(name, locked[name], selected[name], scope))
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
