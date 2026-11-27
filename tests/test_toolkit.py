import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ToolkitTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='maybe-toolkit-test-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def command(self, *args, cwd=ROOT, env=None):
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=20,
                              env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', **(env or {})})

    def toolkit(self):
        root = self.root / 'toolkit'
        root.mkdir()
        for file in ['doctor.sh', 'setup.sh', 'skills.txt', 'skills-lock.json']:
            shutil.copy2(ROOT / file, root / file)
        for directory in ['scripts', 'profiles', 'skills', '.agents']:
            shutil.copytree(ROOT / directory, root / directory, ignore=shutil.ignore_patterns('__pycache__'))
        for agent in ['.claude', '.pi']:
            (root / agent / 'skills').mkdir(parents=True)
            for skill in (root / '.agents/skills').iterdir():
                (root / agent / 'skills' / skill.name).symlink_to(Path('../../.agents/skills') / skill.name)
        return root

    def snapshot(self, root):
        return {str(file.relative_to(root)): ('link', os.readlink(file)) if file.is_symlink() else ('file', file.read_bytes())
                for file in root.rglob('*') if file.is_symlink() or file.is_file()}

    def test_doctor_read_only_and_detects_drift_links_and_resources(self):
        root = self.toolkit()
        before = self.snapshot(root)
        clean = self.command('bash', str(root / 'doctor.sh'), '--local', '--json')
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertEqual(self.snapshot(root), before)
        source = root / 'skills/systematic-debugging/SKILL.md'
        source.write_text(source.read_text() + '\n[Missing](references/missing.md)\n')
        (root / '.pi/skills/handoff').unlink()
        (root / '.pi/skills/handoff').symlink_to('missing')
        broken = self.command('bash', str(root / 'doctor.sh'), '--local', '--json')
        self.assertEqual(broken.returncode, 1)
        errors = json.loads(broken.stdout)['errors']
        self.assertTrue(any('missing linked resource' in error for error in errors))
        self.assertTrue(any('differs' in error for error in errors))
        self.assertTrue(any('pi link' in error for error in errors))

    def test_doctor_validates_frontmatter_policy_parity_scripts_and_lockfile(self):
        root = self.toolkit()
        # Malformed frontmatter line fails instead of passing silently.
        bad_fm = root / 'skills/deslop-code/SKILL.md'
        bad_fm.write_text('---\nname: deslop-code\ndescription: >-\n  Valid multiline\nbroken line without colon\n---\nBody\n')
        # Invocation parity mismatch fails.
        (root / 'skills/handoff/agents/openai.yaml').unlink()
        # Non-executable script fails.
        (root / 'skills/agents-md-eval/scripts/make-eval-snapshot.sh').chmod(0o644)
        # Corrupted lockfile source and hash fail.
        lock_file = root / 'skills-lock.json'
        lock = json.loads(lock_file.read_text())
        lock['skills']['blast-radius'] = {'source': 'wrong/repo', 'sourceType': 'local', 'computedHash': 'not-a-hash'}
        lock_file.write_text(json.dumps(lock, indent=2))
        res = self.command('bash', str(root / 'doctor.sh'), '--local', '--profile', 'all', '--json')
        self.assertEqual(res.returncode, 1)
        errors = json.loads(res.stdout)['errors']
        self.assertTrue(any('malformed frontmatter' in e for e in errors), errors)
        self.assertTrue(any('agents/openai.yaml' in e for e in errors), errors)
        self.assertTrue(any('not executable' in e for e in errors), errors)
        self.assertTrue(any('lockfile source' in e for e in errors), errors)
        self.assertTrue(any('invalid hash' in e for e in errors), errors)

    def test_global_doctor_resolves_overrides_and_reports_competing_sources_without_writes(self):
        root = self.toolkit()
        global_home = self.root / 'user'
        canonical = global_home / '.agents/skills'
        canonical.parent.mkdir(parents=True)
        shutil.copytree(root / '.agents/skills', canonical)
        lock = global_home / 'custom-state/skills/.skill-lock.json'
        lock.parent.mkdir(parents=True)
        shutil.copy2(root / 'skills-lock.json', lock)
        overrides = {'CODEX_HOME': str(global_home / 'custom-codex'),
                     'CLAUDE_CONFIG_DIR': str(global_home / 'custom-claude'),
                     'XDG_CONFIG_HOME': str(global_home / 'custom-config'),
                     'XDG_STATE_HOME': str(global_home / 'custom-state')}
        for directory in [global_home / 'custom-claude/skills', global_home / '.pi/agent/skills']:
            directory.mkdir(parents=True)
            for skill in canonical.iterdir():
                (directory / skill.name).symlink_to(skill)
        launcher = f"""import runpy, sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, {str(root / 'scripts')!r})
sys.argv = [{str(root / 'scripts/doctor.py')!r}, *sys.argv[1:]]
with patch('pathlib.Path.home', return_value=Path({str(global_home)!r})):
    runpy.run_path({str(root / 'scripts/doctor.py')!r}, run_name='__main__')
"""
        before = self.snapshot(global_home)
        result = self.command(sys.executable, '-B', '-c', launcher, '--json', env=overrides)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['scope'], 'global')
        self.assertEqual(data['lockfile'], str(lock))
        for agent in ['codex', 'opencode', 'claude-code', 'pi']:
            self.assertEqual(data['resolutions'][agent]['handoff']['resolved_source'],
                             str((canonical / 'handoff').resolve()))
        self.assertEqual(self.snapshot(global_home), before)
        shadow = global_home / 'custom-codex/skills/handoff'
        shutil.copytree(canonical / 'handoff', shadow)
        result = self.command(sys.executable, '-B', '-c', launcher, '--global', '--json', env=overrides)
        data = json.loads(result.stdout)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertTrue(data['resolutions']['codex']['handoff']['ambiguous'])
        self.assertEqual(len(data['resolutions']['codex']['handoff']['candidates']), 2)
        self.assertTrue(any('competing' in warning for warning in data['warnings']))
        link = global_home / 'custom-claude/skills/handoff'
        link.unlink()
        link.symlink_to(shadow)
        failed = self.command(sys.executable, '-B', '-c', launcher, '--json', env=overrides)
        self.assertEqual(failed.returncode, 1)
        self.assertTrue(any('claude-code link' in error for error in json.loads(failed.stdout)['errors']))
        link.unlink()
        link.symlink_to(canonical / 'handoff')
        lock.unlink()
        local_only = self.command(sys.executable, '-B', '-c', launcher, '--json', env=overrides)
        self.assertEqual(local_only.returncode, 0, local_only.stdout)
        self.assertIn('handoff', json.loads(local_only.stdout)['unlocked_local'])
        failed = self.command(sys.executable, '-B', '-c', launcher, '--profile', 'all', '--json', env=overrides)
        self.assertEqual(failed.returncode, 1)
        self.assertTrue(any('missing global lockfile' in error for error in json.loads(failed.stdout)['errors']))

    def test_setup_profiles_combine_and_system_bash_empty_arrays_succeed(self):
        root = self.toolkit()
        # Verify system /bin/bash (Bash 3.2 on macOS) does not fail with unbound variable on empty arrays.
        system_bash = '/bin/bash' if Path('/bin/bash').is_file() else 'bash'
        core = self.command(system_bash, str(root / 'setup.sh'), '--dry-run')
        self.assertEqual(core.returncode, 0, core.stderr)
        self.assertIn('--skill blast-radius ', core.stdout)
        self.assertIn('--skill verification-skill ', core.stdout)
        self.assertNotIn('--skill animate ', core.stdout)
        self.assertNotIn('--skill teach ', core.stdout)
        explicit_core = self.command(system_bash, str(root / 'setup.sh'), '--dry-run', '--profile', 'core')
        self.assertEqual(explicit_core.returncode, 0, explicit_core.stderr)
        result = self.command(system_bash, str(root / 'setup.sh'), '--dry-run', '--profile', 'frontend', '--profile', 'backend', '--profile', 'mobile', '--profile', 'personal')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--skill animate ', result.stdout)
        self.assertIn('--skill architecture-guardrails ', result.stdout)
        self.assertIn('--skill write-swift ', result.stdout)
        self.assertIn('--skill poteto-mode ', result.stdout)
        self.assertIn('--skill db-migrations ', result.stdout)
        self.assertIn('--skill incident-triage ', result.stdout)
        self.assertNotIn('--skill emil-design-eng ', result.stdout)
        self.assertNotIn('--skill statechart ', result.stdout)
        self.assertEqual(result.stdout.count('--skill systematic-debugging '), 1)
        (root / 'profiles/core.json').write_text('{"extends":["core"],"skills":[]}')
        broken = self.command(system_bash, str(root / 'setup.sh'), '--dry-run')
        self.assertNotEqual(broken.returncode, 0)
        self.assertIn('cycle', broken.stderr)
        self.assertNotIn('npx', broken.stdout)

    def test_setup_refreshes_selected_sources_and_links_without_consuming_manifest(self):
        root = self.toolkit()
        binary = self.root / 'bin'
        binary.mkdir()
        log = self.root / 'cli.jsonl'
        stub = binary / 'npx'
        stub.write_text(f"#!{sys.executable}\n" + """import json, os, sys
with open(os.environ['SETUP_TEST_LOG'], 'a') as output:
    output.write(json.dumps({'args': sys.argv[1:], 'stdin': sys.stdin.read()}) + '\\n')
""")
        stub.chmod(0o755)
        env = {'PATH': str(binary) + os.pathsep + os.environ['PATH'], 'SETUP_TEST_LOG': str(log)}
        result = self.command('bash', str(root / 'setup.sh'), '--update', '--skill', 'blast-radius',
                              '--skill', 'animate', '--skill', 'blast-radius', '--agent', 'pi', env=env)
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual(len(calls), 3)
        self.assertEqual({call['args'][3] for call in calls[:2]},
                         {'emilkowalski/skills', './skills/blast-radius'})
        for call in calls[:2]:
            self.assertEqual(call['args'][2], 'add')
            self.assertIn('--global', call['args'])
            self.assertEqual(call['args'][call['args'].index('--agent') + 1], 'pi')
            self.assertEqual(call['stdin'], '')
        self.assertEqual(calls[-1]['args'][2], 'list')
        before = log.read_bytes()
        rejected = self.command('bash', str(root / 'setup.sh'), '--update', '--profile', 'core',
                                '--skill', 'architecture-guardrails', env=env)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(log.read_bytes(), before)
        missing = self.command('bash', str(root / 'setup.sh'), '--skill', 'does-not-exist', env=env)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(log.read_bytes(), before)
        local = self.command('bash', str(root / 'setup.sh'), '--local', '--update',
                             '--skill', 'blast-radius', env=env)
        self.assertEqual(local.returncode, 0, local.stderr)
        calls = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertNotIn('--global', calls[-2]['args'])
        self.assertIn('./skills/blast-radius', calls[-2]['args'])

    def test_snapshot_script_refuses_existing_arms_and_repo_named_with(self):
        script = ROOT / 'skills/agents-md-eval/scripts/make-eval-snapshot.sh'
        parent = self.root / 'repos'
        repo = parent / 'with'
        repo.mkdir(parents=True)
        (repo / 'README.md').write_text('hello\n')
        (repo / 'AGENTS.md').write_text('rule\n')
        self.command('git', 'init', cwd=repo)
        self.command('git', 'config', 'user.email', 'test@example.com', cwd=repo)
        self.command('git', 'config', 'user.name', 'Test', cwd=repo)
        self.command('git', 'add', '.', cwd=repo)
        self.command('git', 'commit', '-m', 'init', cwd=repo)
        # Passing the parent of a repo named "with" must refuse and never delete the repo.
        danger = self.command('bash', str(script), '--repo', str(repo), '--out', str(parent), '--mode', 'both')
        self.assertNotEqual(danger.returncode, 0)
        self.assertTrue((repo / 'README.md').is_file())
        # Fresh destination succeeds once, then refuses overwrite on second run.
        out = self.root / 'snap'
        ok = self.command('bash', str(script), '--repo', str(repo), '--out', str(out), '--mode', 'both')
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertTrue((out / 'with/AGENTS.md').is_file())
        self.assertFalse((out / 'without/AGENTS.md').exists())
        again = self.command('bash', str(script), '--repo', str(repo), '--out', str(out), '--mode', 'both')
        self.assertNotEqual(again.returncode, 0)

    def prepare(self, case, variant='baseline'):
        output = self.root / f'{case}-{variant}'
        result = self.command(sys.executable, '-B', str(ROOT / 'evals/run.py'), 'prepare', '--case', case, '--variant', variant, '--output', str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        return output

    def grade(self, run):
        return self.command(sys.executable, '-B', str(ROOT / 'evals/run.py'), 'grade', '--run', str(run))

    def test_eval_pairs_snapshot_skill_and_reject_real_bug_until_fixed(self):
        baseline = self.prepare('debugging')
        assisted = self.prepare('debugging', 'skill')
        self.assertEqual(self.snapshot(baseline / 'workspace'), self.snapshot(assisted / 'workspace'))
        self.assertFalse((baseline / 'candidate-skill').exists())
        self.assertTrue((assisted / 'candidate-skill/SKILL.md').is_file())
        workspace = baseline / 'workspace'
        (workspace / 'result.json').write_text('{"root_cause":"zero rejected","checks":["boundaries"]}')
        self.assertEqual(self.grade(baseline).returncode, 1)
        source = workspace / 'pricing.py'
        source.write_text(source.read_text().replace('not percent or ', ''))
        self.assertEqual(self.grade(baseline).returncode, 0)
        grading = json.loads((baseline / 'grading.json').read_text())
        self.assertTrue(all(item['status'] == 'pending' for item in grading['manual_review']))

    def test_verification_grader_requires_body_feature_map_and_real_persistence(self):
        run = self.prepare('verification')
        workspace = run / 'workspace'
        skill = workspace / '.agents/skills/verify-notes'
        skill.mkdir(parents=True)
        # Frontmatter-only skill without feature map must fail.
        (skill / 'SKILL.md').write_text('---\nname: verify-notes\ndescription: Verify notes\n---\n')
        (workspace / 'evidence.txt').write_text('Captured CLI output')
        data = {'put': ['--state', 'scratch/state.json', 'put', 'note', 'hello'],
                'get': ['--state', 'scratch/state.json', 'get', 'note'], 'expected': 'hello',
                'evidence_path': 'evidence.txt', 'scratch_path': 'scratch/state.json'}
        (workspace / 'recipe.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 1)
        # Adding actionable body and feature map makes it pass.
        (skill / 'SKILL.md').write_text('---\nname: verify-notes\ndescription: Verify notes\n---\n\n# Verify notes\n\nRun python3 notes.py with isolated --state and clean up scratch state.\n')
        (skill / 'features').mkdir()
        (skill / 'features/README.md').write_text('# Features\n\n- Put and get note persistence\n')
        self.assertEqual(self.grade(run).returncode, 0)
        data['get'][-1] = 'other-note'
        (workspace / 'recipe.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 1)

    def test_handoff_quality_and_new_graders(self):
        run = self.prepare('handoff')
        workspace = run / 'workspace'
        data = {'objective': 'Fix coupon', 'authorized': 'Pricing/tests only', 'plan_path': 'docs/plan.md',
                'completed': ['Changed validation'], 'pending': ['Rerun tests'], 'next_action': 'Check rounding',
                'verification': {'covers_current_state': False}}
        (workspace / 'handoff.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 0)
        data['verification']['covers_current_state'] = True
        (workspace / 'handoff.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 1)

        run = self.prepare('quality')
        workspace = run / 'workspace'
        data = {'existing_commands': ['npm run check'], 'gaps': [{'risk': 'scope', 'affected_paths': ['packages/web']}],
                'recommendations': [{'command': 'node scripts/check.mjs', 'scope': 'all workspace members', 'rationale': 'coverage'}]}
        (workspace / 'proposal.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 0)
        # Extra unexpected file in quality workspace must fail.
        (workspace / 'extra.txt').write_text('stray')
        self.assertEqual(self.grade(run).returncode, 1)
        (workspace / 'extra.txt').unlink()
        (workspace / 'package.json').write_text('{}')
        self.assertEqual(self.grade(run).returncode, 1)

        # Blast-radius grader
        br = self.prepare('blast-radius')
        bw = br / 'workspace'
        (bw / 'impact.json').write_text(json.dumps({
            'summary': 'Share link bypasses revocation',
            'confirmed_risks': [{'path': 'share_link.py', 'mechanism': 'never checks revoked_at', 'impact': 'revoked user reads cached export'}],
            'unproved_assumptions': ['Cache TTL invalidation behavior'],
            'verification_limits': ['Static inspection only']
        }))
        self.assertEqual(self.grade(br).returncode, 0)

        # Prune-tests grader
        pt = self.prepare('prune-tests')
        pw = pt / 'workspace'
        (pw / 'test_cart.py').write_text("""import unittest
from cart import Cart

class CartTests(unittest.TestCase):
    def test_add_item_public_api(self):
        cart = Cart()
        cart.add_item('book-1', 1000, 2)
        self.assertEqual(cart.items(), [{'sku': 'book-1', 'price_cents': 1000, 'qty': 2}])

    def test_total_with_tax(self):
        cart = Cart(tax_rate=0.1)
        cart.add_item('book-1', 1000, 2)
        self.assertEqual(cart.total_cents(), 2200)

    def test_rejects_non_positive_qty(self):
        cart = Cart()
        with self.assertRaises(ValueError):
            cart.add_item('book-1', 1000, 0)
""")
        (pw / 'pruned.json').write_text(json.dumps({
            'kept': ['test_total_with_tax', 'test_rejects_non_positive_qty'],
            'rewritten': ['test_add_item_internal_array'],
            'deleted': [{'test': 'test_total_with_tax_duplicate', 'surviving_test': 'test_total_with_tax'}]
        }))
        self.assertEqual(self.grade(pt).returncode, 0)

        # Design-review grader
        dr = self.prepare('design-review')
        dw = dr / 'workspace'
        (dw / 'review.json').write_text(json.dumps({
            'mode': 'quick',
            'findings': [
                {'id': 'DR-01', 'evidence_label': 'Verified observation', 'location': '.close-btn', 'principle': 'WCAG 4.1.2', 'severity': 'P1', 'recommendation': 'Add aria-label="Close"'},
                {'id': 'DR-02', 'evidence_label': 'Verified observation', 'location': '.error-msg', 'principle': 'WCAG 1.4.3', 'severity': 'P2', 'recommendation': 'Darken error text contrast'}
            ],
            'strengths': ['Clear warning copy'],
            'not_evaluated': ['Screen reader announcement', 'Live focus trap behavior']
        }))
        self.assertEqual(self.grade(dr).returncode, 0)

    def test_routing_validation_passes(self):
        result = self.command(sys.executable, '-B', str(ROOT / 'evals/run.py'), 'routing', '--json')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['status'], 'pass')
        self.assertGreaterEqual(data['total_cases'], 20)

    def test_eval_execution_records_actual_exit_and_timeout(self):
        for variant, program, expected in [('baseline', 'print("fixture")', 0), ('skill', 'import time; time.sleep(30)', 1)]:
            run = self.prepare('quality', variant)
            result = self.command(sys.executable, '-B', str(ROOT / 'evals/run.py'), 'run', '--run', str(run), '--timeout', '1', '--', sys.executable, '-c', program)
            self.assertEqual(result.returncode, expected, result.stderr)
            execution = json.loads((run / 'execution.json').read_text())
            self.assertEqual(execution['timed_out'], expected == 1)
            self.assertGreater(execution['duration_seconds'], 0)


if __name__ == '__main__':
    unittest.main()
