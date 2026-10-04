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

    def command(self, *args, cwd=ROOT):
        return subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=20,
                              env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})

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
        clean = self.command('bash', str(root / 'doctor.sh'), '--json')
        self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
        self.assertEqual(self.snapshot(root), before)
        source = root / 'skills/systematic-debugging/SKILL.md'
        source.write_text(source.read_text() + '\n[Missing](references/missing.md)\n')
        (root / '.pi/skills/handoff').unlink()
        (root / '.pi/skills/handoff').symlink_to('missing')
        broken = self.command('bash', str(root / 'doctor.sh'), '--json')
        self.assertEqual(broken.returncode, 1)
        errors = json.loads(broken.stdout)['errors']
        self.assertTrue(any('missing linked resource' in error for error in errors))
        self.assertTrue(any('differs' in error for error in errors))
        self.assertTrue(any('pi link' in error for error in errors))

    def test_setup_profiles_combine_and_invalid_profiles_do_not_invoke_cli(self):
        root = self.toolkit()
        result = self.command('bash', str(root / 'setup.sh'), '--dry-run', '--profile', 'frontend', '--profile', 'backend')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--skill animate ', result.stdout)
        self.assertIn('--skill architecture-guardrails ', result.stdout)
        self.assertEqual(result.stdout.count('--skill systematic-debugging '), 1)
        core = self.command('bash', str(root / 'setup.sh'), '--dry-run')
        self.assertNotIn('--skill animate ', core.stdout)
        self.assertNotIn('--skill teach ', core.stdout)
        (root / 'profiles/core.json').write_text('{"extends":["core"],"skills":[]}')
        broken = self.command('bash', str(root / 'setup.sh'), '--dry-run')
        self.assertNotEqual(broken.returncode, 0)
        self.assertIn('cycle', broken.stderr)
        self.assertNotIn('npx', broken.stdout)

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

    def test_verification_grader_executes_cli_recipe_and_rejects_bad_persistence(self):
        run = self.prepare('verification')
        workspace = run / 'workspace'
        skill = workspace / '.agents/skills/verify-notes'
        skill.mkdir(parents=True)
        (skill / 'SKILL.md').write_text('---\nname: verify-notes\ndescription: Verify notes\n---\n')
        (workspace / 'evidence.txt').write_text('Captured CLI output')
        data = {'put':['--state','scratch/state.json','put','note','hello'],
                'get':['--state','scratch/state.json','get','note'], 'expected':'hello',
                'evidence_path':'evidence.txt', 'scratch_path':'scratch/state.json'}
        (workspace / 'recipe.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 0)
        data['get'][-1] = 'other-note'
        (workspace / 'recipe.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 1)

    def test_handoff_and_quality_graders_reject_historical_evidence_and_unrequested_edits(self):
        run = self.prepare('handoff')
        workspace = run / 'workspace'
        data = {'objective':'Fix coupon', 'authorized':'Pricing/tests only', 'plan_path':'docs/plan.md',
                'completed':['Changed validation'], 'pending':['Rerun tests'], 'next_action':'Check rounding',
                'verification':{'covers_current_state':False}}
        (workspace / 'handoff.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 0)
        data['verification']['covers_current_state'] = True
        (workspace / 'handoff.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 1)
        run = self.prepare('quality')
        workspace = run / 'workspace'
        data = {'existing_commands':['npm run check'], 'gaps':[{'risk':'scope','affected_paths':['packages/web']}],
                'recommendations':[{'command':'node scripts/check.mjs','scope':'all workspace members','rationale':'coverage'}]}
        (workspace / 'proposal.json').write_text(json.dumps(data))
        self.assertEqual(self.grade(run).returncode, 0)
        (workspace / 'package.json').write_text('{}')
        self.assertEqual(self.grade(run).returncode, 1)

    def test_eval_execution_records_actual_exit_and_timeout(self):
        for variant, program, expected in [('baseline', 'print("fixture")', 0), ('skill','import time; time.sleep(30)',1)]:
            run = self.prepare('quality', variant)
            result = self.command(sys.executable, '-B', str(ROOT / 'evals/run.py'), 'run', '--run', str(run), '--timeout', '1', '--', sys.executable, '-c', program)
            self.assertEqual(result.returncode, expected, result.stderr)
            execution = json.loads((run / 'execution.json').read_text())
            self.assertEqual(execution['timed_out'], expected == 1)
            self.assertGreater(execution['duration_seconds'], 0)


if __name__ == '__main__':
    unittest.main()
