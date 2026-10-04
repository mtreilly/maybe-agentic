#!/usr/bin/env python3
"""Shared manifest/profile parsing; no dependencies or filesystem mutations."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def manifest(root=ROOT):
    entries = {}
    for number, line in enumerate((root / 'skills.txt').read_text().splitlines(), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(f'skills.txt:{number}: expected SOURCE SKILL')
        source, name = parts
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):
            raise ValueError(f'skills.txt:{number}: invalid skill name {name!r}')
        if name in entries:
            raise ValueError(f'skills.txt:{number}: duplicate skill {name}')
        if source.startswith('./'):
            resolved = (root / source).resolve()
            if not resolved.is_relative_to(root.resolve()):
                raise ValueError(f'{name}: local source escapes repository')
        entries[name] = source
    if not entries:
        raise ValueError('skills.txt is empty')
    return entries


def select(profiles, root=ROOT):
    entries = manifest(root)
    selected = set()
    completed = set()

    def visit(name, chain):
        if name == 'all':
            selected.update(entries)
            return
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789-' for c in name):
            raise ValueError(f'invalid profile name {name!r}')
        if name in chain:
            raise ValueError('profile inheritance cycle: ' + ' -> '.join([*chain, name]))
        if name in completed:
            return
        file = root / 'profiles' / f'{name}.json'
        if not file.is_file():
            raise ValueError(f'unknown profile: {name}')
        profile = json.loads(file.read_text())
        if not isinstance(profile, dict) or set(profile) - {'description', 'extends', 'skills'}:
            raise ValueError(f'{file.name}: unsupported profile structure')
        for key in ['extends', 'skills']:
            values = profile.get(key, [])
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                raise ValueError(f'{file.name}: {key} must be a list of names')
        for parent in profile.get('extends', []):
            visit(parent, [*chain, name])
        for skill in profile.get('skills', []):
            if skill not in entries:
                raise ValueError(f'{file.name}: skill absent from manifest: {skill}')
            selected.add(skill)
        completed.add(name)

    for profile in profiles or ['core']:
        visit(profile, [])
    if not selected:
        raise ValueError('selected profiles contain no skills')
    return {name: source for name, source in entries.items() if name in selected}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', action='append', default=[])
    parser.add_argument('--skill', action='append', default=[])
    args = parser.parse_args()
    try:
        entries = select(args.profile) if args.profile or not args.skill else manifest()
        if args.skill:
            unknown = set(args.skill) - entries.keys()
            if unknown:
                raise ValueError('skills absent from selected profiles or manifest: ' + ', '.join(sorted(unknown)))
            entries = {name: source for name, source in entries.items() if name in args.skill}
        for name, source in entries.items():
            print(source, name)
    except (ValueError, OSError) as error:
        parser.exit(2, f'catalog: {error}\n')
