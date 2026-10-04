#!/usr/bin/env python3
"""Prepare isolated paired tasks, run a client command, and grade concrete outputs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
CASES = json.loads((ROOT / 'evals/cases.json').read_text())['cases']


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
            check('review preserved project files', all(digest(workspace).get(file) == value for file, value in meta['initial_files'].items()), 'Initial fixture hashes compared')
        elif case['id'] == 'handoff':
            data = report('handoff.json')
            check('historical verification stays historical', data.get('verification', {}).get('covers_current_state') is False, 'handoff.json')
            check('authoritative plan resolves', contained(workspace, data.get('plan_path')).is_file(), data.get('plan_path'))
            check('scope and continuation recorded', all(data.get(key) for key in ['objective', 'authorized', 'completed', 'pending', 'next_action']), 'handoff.json')
        else:
            data = report('recipe.json')
            skill = workspace / '.agents/skills/verify-notes/SKILL.md'
            check('verification skill exists', skill.is_file(), str(skill))
            evidence = contained(workspace, data.get('evidence_path'))
            scratch = contained(workspace, data.get('scratch_path'))
            check('evidence survives cleanup', evidence.is_file() and evidence.stat().st_size > 0 and not scratch.exists(), 'Evidence exists; original scratch removed')
            # Re-execute the submitted real CLI recipe with fresh state. Evidence of
            # the candidate's earlier execution remains a separate manual criterion.
            with tempfile.TemporaryDirectory(prefix='maybe-eval-state-') as temporary:
                state = str(Path(temporary) / 'state.json')
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
                    commands.append(subprocess.run([sys.executable, '-B', 'notes.py', *args], cwd=workspace,
                                    capture_output=True, text=True, timeout=10))
                check('real CLI persists across processes', all(command.returncode == 0 for command in commands) and commands[-1].stdout.rstrip('\n') == data['expected'], commands[-1].stdout + commands[-1].stderr)
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
        else:
            compare([run.resolve() for run in args.runs])
    except (OSError, ValueError, KeyError) as error:
        parser.exit(2, f'evals: {error}\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
