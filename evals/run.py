#!/usr/bin/env python3
"""Prepare isolated paired tasks, run a client command, grade outputs, and validate routing cases."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from catalog import manifest  # noqa: E402
from doctor import parse_frontmatter  # noqa: E402

DATA = json.loads((ROOT / 'evals/cases.json').read_text())
CASES = DATA['cases']
ROUTING_CASES = DATA.get('routing_cases', [])


def digest(root):
    return {str(file.relative_to(root)): hashlib.sha256(file.read_bytes()).hexdigest()
            for file in root.rglob('*') if file.is_file()}


def prepare(case_id, variant, output):
    case = next((case for case in CASES if case['id'] == case_id), None)
    if not case:
        raise ValueError(f'unknown case: {case_id}')
    output = output.resolve()
    if output.is_relative_to(ROOT.resolve()):
        raise ValueError('keep evaluation runs outside the toolkit to avoid inherited project skills')
    if output.exists():
        raise ValueError('output already exists; use a fresh run directory')
    workspace = output / 'workspace'
    shutil.copytree(ROOT / 'evals/fixtures' / case['fixture'], workspace)
    task = case['prompt']
    if variant == 'skill':
        source = ROOT / 'skills' / case['skill']
        shutil.copytree(source, output / 'candidate-skill')
        task = f"Read and use {output / 'candidate-skill/SKILL.md'} for this task.\n\n" + task
    task += '\n\nWork only in the supplied isolated workspace. Do not publish, deploy, send messages, or modify global configuration.'
    (output / 'prompt.txt').write_text(task + '\n')
    metadata = {'case': case_id, 'variant': variant, 'skill': case['skill'],
                'candidate_hashes': digest(output / 'candidate-skill') if variant == 'skill' else {},
                'initial_files': digest(workspace), 'created_at': time.time(),
                'workspace': str(workspace)}
    (output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    print(output)


def contained(workspace, name):
    if not isinstance(name, str) or not name:
        raise ValueError('artifact path must be a nonempty string')
    result = (workspace / name).resolve()
    if not result.is_relative_to(workspace.resolve()):
        raise ValueError('artifact path escapes workspace')
    return result


def execute(run, command, timeout, model):
    if command and command[0] == '--':
        command = command[1:]
    if not command:
        raise ValueError('provide a client command after --')
    meta = json.loads((run / 'metadata.json').read_text())
    if (run / 'execution.json').exists():
        raise ValueError('this run already executed; prepare a fresh run')
    started = time.monotonic()
    timed_out = False
    # Logs remain outside the task workspace; the client receives the task on stdin.
    with (run / 'prompt.txt').open('rb') as prompt, (run / 'stdout.log').open('wb') as stdout, (run / 'stderr.log').open('wb') as stderr:
        process = subprocess.Popen(command, cwd=meta['workspace'], stdin=prompt,
                                   stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    result = {'command': command, 'model': model, 'duration_seconds': time.monotonic() - started,
              'exit_code': process.returncode, 'timed_out': timed_out, 'tokens': None,
              'limits': 'Token use is unknown unless obtained from the client. Global client instructions and tools may influence both variants.'}
    (run / 'execution.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 1 if timed_out or process.returncode else 0


def workspace_only_added(workspace, initial_files, allowed_extra):
    current = digest(workspace)
    unchanged = all(current.get(file) == value for file, value in initial_files.items())
    unexpected = sorted(set(current) - set(initial_files) - set(allowed_extra))
    return unchanged and not unexpected, unexpected


def grade(run):
    meta = json.loads((run / 'metadata.json').read_text())
    workspace = run / 'workspace'
    case = next(case for case in CASES if case['id'] == meta['case'])
    results = []

    def check(name, passed, evidence):
        results.append({'check': name, 'passed': bool(passed), 'evidence': evidence})

    def report(file):
        return json.loads((workspace / file).read_text())

    try:
        if case['id'] == 'debugging':
            program = """from pricing import discounted_total
assert discounted_total(1000, 0) == 1000
assert discounted_total(1000, 50) == 500
assert discounted_total(1000, 100) == 0
for invalid in [-1, 101]:
    try: discounted_total(1000, invalid)
    except ValueError: pass
    else: raise AssertionError('invalid discount accepted')
"""
            result = subprocess.run([sys.executable, '-B', '-c', program], cwd=workspace,
                                    capture_output=True, text=True, timeout=10)
            check('original case and discount boundaries', result.returncode == 0, result.stderr or 'Behavioral cases passed')
            data = report('result.json')
            check('diagnosis and check record', bool(data.get('root_cause')) and bool(data.get('checks')), 'result.json')
        elif case['id'] == 'quality':
            data = report('proposal.json')
            check('existing command identified', 'npm run check' in data.get('existing_commands', []), 'proposal.json')
            paths = [path for gap in data.get('gaps', []) for path in gap.get('affected_paths', [])]
            check('omitted workspace identified', any('packages/web' in path for path in paths), str(paths))
            check('recommendation has command/scope/rationale', any(all(rec.get(key) for key in ['command', 'scope', 'rationale']) for rec in data.get('recommendations', [])), 'proposal.json')
            clean, unexpected = workspace_only_added(workspace, meta['initial_files'], ['proposal.json'])
            check('review preserved project files without extra files', clean, f'unexpected={unexpected}')
        elif case['id'] == 'handoff':
            data = report('handoff.json')
            check('historical verification stays historical', data.get('verification', {}).get('covers_current_state') is False, 'handoff.json')
            check('authoritative plan resolves', contained(workspace, data.get('plan_path')).is_file(), data.get('plan_path'))
            check('scope and continuation recorded', all(data.get(key) for key in ['objective', 'authorized', 'completed', 'pending', 'next_action']), 'handoff.json')
        elif case['id'] == 'verification':
            data = report('recipe.json')
            skill_dir = workspace / '.agents/skills/verify-notes'
            skill = skill_dir / 'SKILL.md'
            skill_text = skill.read_text() if skill.is_file() else ''
            body = re.sub(r'\A---\r?\n.*?\r?\n---\r?\n?', '', skill_text, count=1, flags=re.S).strip()
            check('verification skill exists with actionable body', skill.is_file() and len(body) >= 40, str(skill))
            feature_maps = list((skill_dir / 'features').glob('*.md')) if (skill_dir / 'features').is_dir() else []
            check('feature map exists', bool(feature_maps), str([p.name for p in feature_maps]))
            evidence = contained(workspace, data.get('evidence_path'))
            scratch = contained(workspace, data.get('scratch_path'))
            check('evidence survives cleanup', evidence.is_file() and evidence.stat().st_size > 0 and not scratch.exists(), 'Evidence exists; original scratch removed')
            # Re-execute the submitted CLI recipe against a fresh grader-owned copy of notes.py
            # so candidate edits to notes.py cannot forge persistence.
            with tempfile.TemporaryDirectory(prefix='maybe-eval-state-') as temporary:
                temp_dir = Path(temporary)
                grader_notes = temp_dir / 'notes.py'
                shutil.copy2(ROOT / 'evals/fixtures/verification/notes.py', grader_notes)
                state = str(temp_dir / 'state.json')
                commands = []
                for key in ['put', 'get']:
                    args = data[key]
                    if not isinstance(args, list) or any(not isinstance(arg, str) for arg in args):
                        raise ValueError('recipe arguments must be lists of strings')
                    index = args.index('--state') + 1
                    if contained(workspace, args[index]) != scratch:
                        raise ValueError('recipe must use the declared scratch state')
                    args = list(args)
                    args[index] = state
                    commands.append(subprocess.run([sys.executable, '-B', str(grader_notes), *args], cwd=temp_dir,
                                    capture_output=True, text=True, timeout=10))
                check('real CLI persists across processes', all(command.returncode == 0 for command in commands) and commands[-1].stdout.rstrip('\n') == data['expected'], commands[-1].stdout + commands[-1].stderr)
        elif case['id'] == 'blast-radius':
            data = report('impact.json')
            risks = data.get('confirmed_risks', [])
            found_share = any('share_link.py' in str(r.get('path', '')) + str(r.get('mechanism', '')) for r in risks if isinstance(r, dict))
            check('identifies alternate share_link caller bypass', found_share, str(risks))
            check('records unproved assumptions and limits', bool(data.get('unproved_assumptions')) and bool(data.get('verification_limits')), 'impact.json')
            clean, unexpected = workspace_only_added(workspace, meta['initial_files'], ['impact.json'])
            check('read-only review preserved workspace', clean, f'unexpected={unexpected}')
        elif case['id'] == 'prune-tests':
            data = report('pruned.json')
            check('cart.py untouched', digest(workspace).get('cart.py') == meta['initial_files']['cart.py'], 'cart.py hash')
            test_text = (workspace / 'test_cart.py').read_text()
            check('removed brittle private _items access', '_items' not in test_text, 'test_cart.py')
            run_tests = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_cart.py'], cwd=workspace, capture_output=True, text=True, timeout=10)
            check('pruned test suite passes', run_tests.returncode == 0, run_tests.stderr or run_tests.stdout)
            # Mutation check: suite must still catch negative qty and broken tax calculation.
            mutated_ok = True
            with tempfile.TemporaryDirectory(prefix='maybe-eval-mut-') as temp:
                tdir = Path(temp)
                shutil.copy2(workspace / 'test_cart.py', tdir / 'test_cart.py')
                cart_src = (workspace / 'cart.py').read_text()
                for target, repl in [('qty <= 0 or ', ''), ('self.subtotal_cents() * self._tax_rate', '0')]:
                    (tdir / 'cart.py').write_text(cart_src.replace(target, repl))
                    mres = subprocess.run([sys.executable, '-B', '-m', 'unittest', 'test_cart.py'], cwd=tdir, capture_output=True, text=True, timeout=10)
                    if mres.returncode == 0:
                        mutated_ok = False
            check('surviving suite catches regressions', mutated_ok, 'mutation checks')
            deleted = data.get('deleted', [])
            check('each deletion cites surviving test or reason', isinstance(deleted, list) and len(deleted) >= 1 and all(isinstance(d, dict) and (d.get('surviving_test') or d.get('reason')) for d in deleted), str(deleted))
        elif case['id'] == 'design-review':
            data = report('review.json')
            clean, unexpected = workspace_only_added(workspace, meta['initial_files'], ['review.json'])
            check('review preserved design artifact', clean, f'unexpected={unexpected}')
            valid_labels = {'Verified observation', 'Assumption', 'Hypothesis', 'Not evaluated'}
            findings = data.get('findings', [])
            check('findings use explicit evidence labels', isinstance(findings, list) and len(findings) >= 2 and all(isinstance(f, dict) and f.get('evidence_label') in valid_labels and f.get('severity') and f.get('recommendation') for f in findings), str(len(findings)))
            check('records not_evaluated limits', isinstance(data.get('not_evaluated'), list) and len(data.get('not_evaluated')) >= 1, 'review.json')
        else:
            raise ValueError(f'no grader for case: {case["id"]}')
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        check('required output is valid and executable', False, str(error))
    execution = json.loads((run / 'execution.json').read_text()) if (run / 'execution.json').exists() else None
    if execution:
        check('client completed successfully', execution['exit_code'] == 0 and not execution['timed_out'], 'execution.json')
    result = {'case': case['id'], 'variant': meta['variant'], 'objective_checks': results,
              'objective_pass': bool(results) and all(item['passed'] for item in results),
              'manual_review': [{'criterion': criterion, 'status': 'pending'} for criterion in case['manual_review']],
              'execution': execution, 'limits': 'Objective checks are partial. Pending manual review prevents an overall quality verdict.'}
    (run / 'grading.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
    return 0 if result['objective_pass'] else 1


def compare(runs):
    rows = []
    for run in runs:
        data = json.loads((run / 'grading.json').read_text())
        rows.append({'run': str(run), 'case': data['case'], 'variant': data['variant'],
                     'objective_pass': data['objective_pass'],
                     'manual_pending': sum(item['status'] == 'pending' for item in data['manual_review']),
                     'manual_failed': sum(item['status'] == 'fail' for item in data['manual_review']),
                     'execution': data['execution']})
    print(json.dumps(rows, indent=2))


def routing(as_json=False):
    """Validate routing_cases against the live manifest and skill frontmatter metadata."""
    entries = manifest(ROOT)
    meta = {}
    for name, source in entries.items():
        skill_dir = (ROOT / source) if source.startswith('./') else (ROOT / '.agents/skills' / name)
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.is_file():
            continue
        text = skill_md.read_text()
        header = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)', text, re.S)
        fields, _ = parse_frontmatter(header.group(1)) if header else ({}, [])
        meta[name] = {
            'description': fields.get('description', ''),
            'explicit_only': fields.get('disable-model-invocation', '').lower() == 'true',
        }
    errors = []
    clusters = {}
    for index, case in enumerate(ROUTING_CASES, 1):
        prompt = case.get('prompt', '').strip()
        expected = case.get('expected', [])
        cluster = case.get('cluster', 'general')
        explicit_case = bool(case.get('explicit', False))
        clusters.setdefault(cluster, 0)
        clusters[cluster] += 1
        if not prompt:
            errors.append(f'routing_cases[{index}]: empty prompt')
        for skill in expected:
            if skill not in entries:
                errors.append(f'routing_cases[{index}]: expected skill {skill!r} absent from skills.txt')
            elif skill not in meta:
                errors.append(f'routing_cases[{index}]: expected skill {skill!r} missing SKILL.md')
            else:
                if meta[skill]['explicit_only'] and not explicit_case:
                    errors.append(f'routing_cases[{index}]: {skill!r} has disable-model-invocation: true but routing case omits explicit: true')
                if not meta[skill]['description']:
                    errors.append(f'routing_cases[{index}]: {skill!r} has empty description')
    report_data = {
        'status': 'fail' if errors else 'pass',
        'total_cases': len(ROUTING_CASES),
        'negative_cases': sum(1 for c in ROUTING_CASES if not c.get('expected')),
        'explicit_cases': sum(1 for c in ROUTING_CASES if c.get('explicit')),
        'clusters': clusters,
        'errors': errors,
        'limits': 'Validates routing prompt definitions against manifest and invocation policy. Live client routing still requires executing prompts against target clients.'
    }
    if as_json:
        print(json.dumps(report_data, indent=2))
    else:
        print(f"Routing cases: {report_data['status'].upper()} ({report_data['total_cases']} cases, {report_data['negative_cases']} negative, {report_data['explicit_cases']} explicit-only)")
        for err in errors:
            print(f'ERROR: {err}')
    return 1 if errors else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    p = sub.add_parser('prepare')
    p.add_argument('--case', required=True, choices=[case['id'] for case in CASES])
    p.add_argument('--variant', choices=['baseline', 'skill'], required=True)
    p.add_argument('--output', type=Path, required=True)
    p = sub.add_parser('run')
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--timeout', type=int, default=300)
    p.add_argument('--model', default='unspecified')
    p.add_argument('command', nargs=argparse.REMAINDER)
    p = sub.add_parser('grade')
    p.add_argument('--run', type=Path, required=True)
    p = sub.add_parser('compare')
    p.add_argument('runs', type=Path, nargs='+')
    p = sub.add_parser('routing')
    p.add_argument('--json', action='store_true')
    args = parser.parse_args()
    try:
        if args.action == 'prepare':
            prepare(args.case, args.variant, args.output)
        elif args.action == 'run':
            if args.timeout <= 0:
                raise ValueError('timeout must be positive')
            return execute(args.run.resolve(), args.command, args.timeout, args.model)
        elif args.action == 'grade':
            return grade(args.run.resolve())
        elif args.action == 'routing':
            return routing(args.json)
        else:
            compare([run.resolve() for run in args.runs])
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'evals: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
