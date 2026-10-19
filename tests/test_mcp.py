import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
import mcp  # noqa: E402

CODEX = '''model = "gpt"

[mcp_servers.other]
command = "other"

[mcp_servers.demo]
command = "old"
args = ["--old"]

[mcp_servers.demo.env]
OLD = "1"

[mcp_servers.demo.tools.click]
approval_mode = "approve"

[projects."/tmp"]
trust_level = "trusted"
'''


class CodexTomlTests(unittest.TestCase):
    def test_replaces_owned_tables_and_keeps_the_rest(self):
        entry = {'command': '/bin/node', 'args': ['a.js', '--x'], 'tool_timeout_sec': 180.0, 'env': {'NEW': '1'}}
        result = mcp.codex_apply(CODEX, 'demo', entry)
        data = tomllib.loads(result)
        self.assertEqual(data['mcp_servers']['demo']['command'], '/bin/node')
        self.assertEqual(data['mcp_servers']['demo']['env'], {'NEW': '1'})
        self.assertEqual(data['mcp_servers']['demo']['tools'], {'click': {'approval_mode': 'approve'}})
        self.assertEqual(data['mcp_servers']['other'], {'command': 'other'})
        self.assertEqual(data['projects'], {'/tmp': {'trust_level': 'trusted'}})
        self.assertEqual(mcp.codex_apply(result, 'demo', entry), result)
        self.assertEqual(mcp.codex_current(result, 'demo'), entry)

    def test_appends_to_a_file_without_the_server(self):
        result = mcp.codex_apply('model = "gpt"', 'demo', {'command': 'x', 'args': []})
        self.assertEqual(tomllib.loads(result)['mcp_servers']['demo'], {'command': 'x', 'args': []})


class SetupTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='maybe-mcp-test-')
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'toolkit'
        shutil.copytree(ROOT / 'scripts', self.root / 'scripts', ignore=shutil.ignore_patterns('__pycache__'))
        self.home = self.base / 'home'
        tool = self.base / 'bin/demo-tool'
        tool.parent.mkdir(parents=True)
        tool.write_text('#!/bin/sh\n')
        tool.chmod(0o755)
        entry = self.home / '.agents/mcp/built/v1/out/server.js'
        entry.parent.mkdir(parents=True)
        entry.write_text('')
        # Records Claude CLI calls and keeps a user-scope config like the real CLI.
        claude = self.base / 'bin/claude'
        claude.write_text(f'''#!{sys.executable}
import json, sys
path = {str(self.home / '.claude.json')!r}
try: data = json.load(open(path))
except FileNotFoundError: data = {{}}
servers = data.setdefault('mcpServers', {{}})
if sys.argv[2] == 'remove': servers.pop(sys.argv[-1], None)
else: servers[sys.argv[-2]] = json.loads(sys.argv[-1])
json.dump(data, open(path, 'w'))
''')
        claude.chmod(0o755)
        (self.root / 'mcp').mkdir()
        (self.root / 'mcp/servers.json').write_text(json.dumps({'servers': {
            'built': {'source': {'git': 'unused', 'ref': 'v1', 'entry': 'out/server.js'},
                      'args': ['--flag'], 'env': {'A': '1'}, 'startup_timeout_sec': 30},
            'binary': {'command': str(tool), 'args': ['mcp']},
            'absent': {'command': str(self.base / 'missing'), 'optional': True},
        }}))
        opencode = self.home / '.config/opencode/opencode.json'
        opencode.parent.mkdir(parents=True)
        opencode.write_text(json.dumps({'plugin': ['keep'], 'mcp': {'mine': {'type': 'remote'}}}))

    def run_setup(self, *args):
        env = {**os.environ, 'HOME': str(self.home), 'PATH': f'{self.base / "bin"}:/usr/bin:/bin',
               'PYTHONDONTWRITEBYTECODE': '1'}
        for key in ['CODEX_HOME', 'CLAUDE_CONFIG_DIR', 'XDG_CONFIG_HOME', 'PI_CODING_AGENT_DIR', 'AGENTS_HOME']:
            env.pop(key, None)
        return subprocess.run([sys.executable, str(self.root / 'scripts/mcp.py'), '--node', '/bin/node', *args],
                              capture_output=True, text=True, env=env, timeout=20)

    def test_registers_every_client_idempotently_and_preserves_other_entries(self):
        dry = self.run_setup('--dry-run')
        self.assertEqual(dry.returncode, 0, dry.stdout + dry.stderr)
        self.assertFalse((self.home / '.codex').exists())
        self.assertEqual(self.run_setup('--check').returncode, 1)

        first = self.run_setup()
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertIn('absent: skipped', first.stdout)
        launch = str(self.home / '.agents/mcp/built/v1/out/server.js')

        codex = tomllib.loads((self.home / '.codex/config.toml').read_text())['mcp_servers']
        self.assertEqual(codex['built'], {'command': '/bin/node', 'args': [launch, '--flag'],
                                          'startup_timeout_sec': 30.0, 'env': {'A': '1'}})
        opencode = json.loads((self.home / '.config/opencode/opencode.json').read_text())
        backup = json.loads((self.home / '.config/opencode/opencode.json.maybe-agentic.bak').read_text())
        self.assertEqual(backup, {'plugin': ['keep'], 'mcp': {'mine': {'type': 'remote'}}})
        self.assertEqual(opencode['plugin'], ['keep'])
        self.assertEqual(opencode['mcp']['mine'], {'type': 'remote'})
        self.assertEqual(opencode['mcp']['built'], {'type': 'local', 'command': ['/bin/node', launch, '--flag'],
                                                    'enabled': True, 'environment': {'A': '1'}, 'timeout': 30000})
        pi = json.loads((self.home / '.pi/agent/mcp.json').read_text())['mcpServers']
        self.assertEqual(pi['binary']['args'], ['mcp'])
        claude = json.loads((self.home / '.claude.json').read_text())['mcpServers']
        self.assertEqual(claude['built']['type'], 'stdio')
        self.assertNotIn('absent', claude)

        second = self.run_setup()
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertNotIn('added', second.stdout)
        self.assertNotIn('updated', second.stdout)
        self.assertEqual(self.run_setup('--check').returncode, 0)

    def test_rejects_unknown_server(self):
        result = self.run_setup('--server', 'nope')
        self.assertEqual(result.returncode, 2)
        self.assertIn('unknown servers', result.stderr)

    def test_repository_manifest_is_valid(self):
        self.assertIn('chrome-devtools', mcp.manifest(ROOT))


if __name__ == '__main__':
    unittest.main()
