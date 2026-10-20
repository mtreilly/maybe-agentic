#!/usr/bin/env python3
"""Install the MCP servers in mcp/servers.json and register them with each client.

Only servers named in the manifest are touched; other client entries are kept.
"""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tomllib

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ['codex', 'claude-code', 'opencode', 'pi']
NAME = re.compile(r'^[a-z0-9][a-z0-9-]*$')


def load(root):
    data = json.loads((root / 'mcp/servers.json').read_text())
    if not isinstance(data, dict) or set(data) - {'servers', 'tools'}:
        raise ValueError('servers.json: expected "servers" and optional "tools" objects')
    return data


def tools(root=ROOT):
    """CLIs agents call directly, checked and installed alongside the servers."""
    entries = load(root).get('tools', {})
    for name, spec in entries.items():
        if not NAME.match(name) or not isinstance(spec, dict) or set(spec) - {'description', 'brew', 'npm', 'url'}:
            raise ValueError(f'servers.json: invalid tool {name!r}')
    return entries


def manifest(root=ROOT):
    servers = load(root).get('servers')
    if not isinstance(servers, dict) or not servers:
        raise ValueError('servers.json: expected a non-empty "servers" object')
    allowed = {'description', 'source', 'command', 'url', 'args', 'env', 'requires', 'optional', 'note',
               'startup_timeout_sec', 'tool_timeout_sec'}
    for name, spec in servers.items():
        if not NAME.match(name):
            raise ValueError(f'servers.json: invalid server name {name!r}')
        if not isinstance(spec, dict) or set(spec) - allowed:
            raise ValueError(f'{name}: unsupported keys {sorted(set(spec) - allowed)}')
        if sum(key in spec for key in ['source', 'command', 'url']) != 1:
            raise ValueError(f'{name}: needs exactly one of "source", "command" or "url"')
        if 'url' in spec and ({'args', 'env', 'requires'} & set(spec) or not spec['url'].startswith('https://')):
            raise ValueError(f'{name}: remote servers take an https url and no args, env or requires')
        if 'source' in spec and set(spec['source']) - {'git', 'ref', 'build', 'env', 'entry'}:
            raise ValueError(f'{name}: unsupported source keys')
        if 'source' in spec and not all(spec['source'].get(key) for key in ['git', 'ref', 'entry']):
            raise ValueError(f'{name}: source needs git, ref and entry')
        if not all(isinstance(arg, str) for arg in spec.get('args', [])):
            raise ValueError(f'{name}: args must be strings')
    skip = local(root).get('skip', [])
    unknown = set(skip) - servers.keys()
    if unknown:
        raise ValueError('local.json: skip names unknown servers: ' + ', '.join(sorted(unknown)))
    return {name: spec for name, spec in servers.items() if name not in skip}


def local(root=ROOT):
    """Untracked per-machine settings, e.g. {"skip": ["chrome-devtools"]} where another tool owns a server."""
    path = root / 'mcp/local.json'
    data = json.loads(path.read_text()) if path.exists() else {}
    if not isinstance(data, dict) or set(data) - {'skip'} or not all(isinstance(n, str) for n in data.get('skip', [])):
        raise ValueError('local.json: expected {"skip": [server names]}')
    return data


def home():
    return Path(os.environ.get('HOME', Path.home()))


def install_dir(name, spec):
    agents_home = Path(os.environ.get('AGENTS_HOME', home() / '.agents'))
    return agents_home / 'mcp' / name / spec['source']['ref']


def config_paths():
    claude_dir = Path(os.environ['CLAUDE_CONFIG_DIR']) if os.environ.get('CLAUDE_CONFIG_DIR') else home()
    return {
        'codex': Path(os.environ.get('CODEX_HOME', home() / '.codex')) / 'config.toml',
        'claude-code': claude_dir / '.claude.json',
        'opencode': Path(os.environ.get('XDG_CONFIG_HOME', home() / '.config')) / 'opencode/opencode.json',
        'pi': Path(os.environ.get('PI_CODING_AGENT_DIR', home() / '.pi/agent')) / 'mcp.json',
    }


def build(name, spec, log):
    source = spec['source']
    target = install_dir(name, spec)
    if (target / source['entry']).is_file():
        log(f'{name}: {source["ref"]} already built at {target}')
        return
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--quiet', '--depth', '1', '--branch', source['ref'], source['git'], str(target)],
                       check=True, env={**os.environ, 'GIT_CONFIG_PARAMETERS': "'advice.detachedHead=false'"})
    for step in source.get('build', []):
        log(f'{name}: {" ".join(step)}')
        subprocess.run(step, cwd=target, check=True, env={**os.environ, **source.get('env', {})})
    if not (target / source['entry']).is_file():
        raise RuntimeError(f'{name}: build finished without {source["entry"]}')


def expand(value):
    return str(home() / value[2:]) if value.startswith('~/') else value


def resolve(name, spec, node):
    """Return the launch command, or a reason it is unavailable."""
    if 'url' in spec:
        return {'url': spec['url']}, None
    for required in map(expand, spec.get('requires', [])):
        if not Path(required).exists():
            return None, f'{required} not found'
    args = [expand(arg) for arg in spec.get('args', [])]
    if 'source' in spec:
        entry = install_dir(name, spec) / spec['source']['entry']
        if not entry.is_file():
            return None, f'not built at {entry.parent}'
        if not node:
            return None, 'node not found; pass --node'
        command, args = node, [str(entry), *args]
    else:
        command = expand(spec['command'])
        if os.sep not in command:
            # Clients started from the desktop do not inherit the shell PATH.
            command = node if command == 'node' and node else shutil.which(command) or command
        if not Path(command).is_file():
            return None, f'{spec["command"]} not installed'
    return {'command': command, 'args': args, 'env': dict(spec.get('env', {}))}, None


def remote_entry(agent, url):
    return {'claude-code': {'type': 'http', 'url': url},
            'opencode': {'type': 'remote', 'url': url, 'enabled': True}}.get(agent, {'url': url})


def client_entry(agent, launch, spec):
    if 'url' in launch:
        return remote_entry(agent, launch['url'])
    launch = {**launch, 'args': [arg.replace('{agent}', agent) for arg in launch['args']]}
    if agent == 'claude-code':
        return {'type': 'stdio', **launch}
    if agent == 'opencode':
        entry = {'type': 'local', 'command': [launch['command'], *launch['args']], 'enabled': True}
        if launch['env']:
            entry['environment'] = launch['env']
        if 'startup_timeout_sec' in spec:
            entry['timeout'] = spec['startup_timeout_sec'] * 1000
        return entry
    if agent == 'pi':
        entry = {'command': launch['command'], 'args': launch['args']}
        if launch['env']:
            entry['env'] = launch['env']
        return entry
    entry = {'command': launch['command'], 'args': launch['args']}
    for key in ['startup_timeout_sec', 'tool_timeout_sec']:
        if key in spec:
            entry[key] = float(spec[key])
    if launch['env']:
        entry['env'] = launch['env']
    return entry


BARE_KEY = re.compile(r'^[A-Za-z0-9_-]+$')
HEADER = re.compile(r'^\s*\[\[?\s*([^\]]+?)\s*\]\]?\s*(#.*)?$')


def toml_path(header):
    return [part.strip().strip('"\'') for part in header.split('.')]


def toml_value(value):
    if isinstance(value, bool):
        return 'true' if value else 'false'
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, list):
        return '[' + ', '.join(toml_value(item) for item in value) + ']'
    return json.dumps(value)


def codex_apply(text, name, entry):
    """Replace [mcp_servers.NAME] and its env table; keep tool approval subtables."""
    owned = [['mcp_servers', name], ['mcp_servers', name, 'env']]
    lines = text.splitlines(keepends=True)
    kept, insert_at, skipping = [], None, False
    for line in lines:
        match = HEADER.match(line)
        if match:
            skipping = toml_path(match.group(1)) in owned
            if skipping and insert_at is None:
                insert_at = len(kept)
        if not skipping:
            kept.append(line)
    key = name if NAME.match(name) else json.dumps(name)
    block = [f'[mcp_servers.{key}]\n']
    block += [f'{field} = {toml_value(value)}\n' for field, value in entry.items() if field != 'env']
    if entry.get('env'):
        block += ['\n', f'[mcp_servers.{key}.env]\n']
        block += [f'{field if BARE_KEY.match(field) else json.dumps(field)} = {toml_value(value)}\n'
                  for field, value in entry['env'].items()]
    block.append('\n')
    if insert_at is None:
        if kept and not kept[-1].endswith('\n'):
            kept[-1] += '\n'
        if kept and kept[-1].strip():
            kept.append('\n')
        insert_at = len(kept)
    result = ''.join(kept[:insert_at] + block + kept[insert_at:])
    tomllib.loads(result)
    return result


def codex_current(text, name):
    server = tomllib.loads(text).get('mcp_servers', {}).get(name)
    if server is None:
        return None
    return {key: value for key, value in server.items() if key != 'tools'}


def json_current(agent, data, name):
    return data.get('mcpServers' if agent in ['claude-code', 'pi'] else 'mcp', {}).get(name)


def read_json(path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as error:
        raise ValueError(f'{path}: not plain JSON ({error}); edit it by hand') from error


BACKED_UP = set()


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Keep the file as it was before this run, not after an earlier server in it.
    if path.exists() and path not in BACKED_UP:
        shutil.copy2(path, path.with_name(path.name + '.maybe-agentic.bak'))
        BACKED_UP.add(path)
    temporary = path.with_name(path.name + '.maybe-agentic.tmp')
    temporary.write_text(text)
    if path.exists():
        shutil.copymode(path, temporary)
    temporary.replace(path)


def current(agent, path, name):
    if not path.exists():
        return None
    if agent == 'codex':
        return codex_current(path.read_text(), name)
    return json_current(agent, read_json(path), name)


def register(agent, path, name, entry, claude):
    if agent == 'claude-code':
        # Claude rewrites ~/.claude.json while running; its CLI owns that file.
        subprocess.run([claude, 'mcp', 'remove', '--scope', 'user', name], capture_output=True)
        subprocess.run([claude, 'mcp', 'add-json', '--scope', 'user', name, json.dumps(entry)],
                       check=True, capture_output=True, text=True)
    elif agent == 'codex':
        write(path, codex_apply(path.read_text() if path.exists() else '', name, entry))
    else:
        data = read_json(path)
        if agent == 'opencode':
            data.setdefault('$schema', 'https://opencode.ai/config.json')
        data.setdefault('mcpServers' if agent == 'pi' else 'mcp', {})[name] = entry
        write(path, json.dumps(data, indent=2) + '\n')


def ensure_tool(name, spec, read_only):
    """Return True when the CLI is on PATH, installing it with brew or npm unless read-only."""
    if shutil.which(name):
        print(f'{name}: tool ok')
        return True
    installers = [(['brew', 'install', spec['brew']], 'brew') if 'brew' in spec else None,
                  (['npm', 'install', '--global', spec['npm']], 'npm') if 'npm' in spec else None]
    available = [step for step, tool in filter(None, installers) if shutil.which(tool)]
    if read_only or not available:
        print(f'{name}: tool missing' + ('' if available else f'; install it from {spec.get("url", "its docs")}'))
        return False
    print(f'{name}: {" ".join(available[0])}')
    subprocess.run(available[0], check=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', action='append', choices=AGENTS, default=[])
    parser.add_argument('--server', action='append', default=[])
    parser.add_argument('--node', default=os.environ.get('MCP_NODE') or shutil.which('node'))
    parser.add_argument('--check', action='store_true', help='report drift without installing or writing')
    parser.add_argument('--dry-run', action='store_true', help='show changes without installing or writing')
    parser.add_argument('--no-tools', action='store_true', help='skip the CLI tools in the manifest')
    args = parser.parse_args()
    try:
        servers = manifest()
        unknown = set(args.server) - servers.keys()
        if unknown:
            raise ValueError('unknown servers: ' + ', '.join(sorted(unknown)))
        selected = {name: spec for name, spec in servers.items() if not args.server or name in args.server}
        agents = args.agent or AGENTS
        paths = config_paths()
        claude = shutil.which('claude')
        read_only = args.check or args.dry_run
        problems = 0
        if not args.no_tools and not args.server:
            for name, spec in tools().items():
                problems += not ensure_tool(name, spec, read_only) and args.check
        for name, spec in selected.items():
            changed = False
            if 'source' in spec and not read_only:
                build(name, spec, print)
            launch, reason = resolve(name, spec, args.node)
            if launch is None:
                if spec.get('optional'):
                    print(f'{name}: skipped ({reason})')
                    continue
                print(f'{name}: unavailable ({reason})')
                problems += 1
                continue
            for agent in agents:
                if agent == 'claude-code' and not claude and not read_only:
                    print(f'{name}: claude-code skipped (claude CLI not on PATH)')
                    problems += 1
                    continue
                entry = client_entry(agent, launch, spec)
                state = current(agent, paths[agent], name)
                if state == entry:
                    print(f'{name}: {agent} ok')
                    continue
                verb = 'missing' if state is None else 'differs'
                if read_only:
                    print(f'{name}: {agent} {verb}' + (f' -> would write {paths[agent]}' if args.dry_run else ''))
                    problems += args.check
                    continue
                register(agent, paths[agent], name, entry, claude)
                changed = True
                print(f'{name}: {agent} {"added" if state is None else "updated"} ({paths[agent]})')
            if changed and spec.get('note'):
                print(f'{name}: note: {spec["note"]}')
        return 1 if problems else 0
    except (ValueError, OSError, RuntimeError, subprocess.CalledProcessError, tomllib.TOMLDecodeError) as error:
        detail = getattr(error, 'stderr', None)
        parser.exit(2, f'mcp: {error}\n' + (detail or ''))


if __name__ == '__main__':
    raise SystemExit(main())
