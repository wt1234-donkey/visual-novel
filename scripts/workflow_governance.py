"""Verify frozen workflow identities and materialize reproducible isolated audits."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def check_scripts(root):
    root=Path(root)
    policy=json.loads((root/'config/script-policy.json').read_text())
    items=policy['scripts']
    actual={p.relative_to(root).as_posix() for p in (root/'scripts').iterdir() if p.suffix in {'.py','.mjs'}}
    if policy.get('schemaVersion')!=1 or len({s['path'] for s in items})!=len(items) or {s['path'] for s in items}!=actual:
        raise ValueError('Script inventory differs from registered policy')
    for item in items:
        if item['role'] not in {'active','historical','tool'}:
            raise ValueError('Unknown script role')
        if item['role']=='historical' and hashlib.sha256((root/item['path']).read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Frozen historical script changed: '+item['path'])
    return {role:sum(s['role']==role for s in items) for role in ('active','historical','tool')}


def registry(root=ROOT):
    value = json.loads((Path(root) / 'config/historical-tasks.json').read_text())
    if value.get('schemaVersion') != 1:
        raise ValueError('Unknown historical task registry')
    tasks = value['tasks']
    if len({t['id'] for t in tasks}) != len(tasks):
        raise ValueError('Duplicate historical task ID')
    return {t['id']: t for t in tasks}


def check(root=ROOT):
    root = Path(root)
    tasks = registry(root)
    active = json.loads((root / 'config/workflow-policy.json').read_text())['activeWorkflows']
    actual = {p.name for p in (root / '.github/workflows').iterdir() if p.suffix in {'.yml','.yaml'}}
    if actual != set(active):
        raise ValueError('Active workflows differ from registered policy: ' + str(actual ^ set(active)))
    expected = set()
    for task in tasks.values():
        original, archived = root / task['originalWorkflow'], root / task['archivedWorkflow']
        if task['state'] != 'frozen' or original.exists() or not task['archivedWorkflow'].startswith('archive/workflows/'):
            raise ValueError('Historical workflow is active or outside archive: ' + task['id'])
        if hashlib.sha256(archived.read_bytes()).hexdigest() != task['workflowSha256']:
            raise ValueError('Frozen workflow changed: ' + task['id'])
        expected.add(archived.name)
    if expected != {p.name for p in (root / 'archive/workflows').glob('*.yml')}:
        raise ValueError('Unregistered archived workflow')
    scripts=check_scripts(root)
    vendors=json.loads((root/'config/runtime-vendors.json').read_text())
    if vendors.get('schemaVersion')!=1:
        raise ValueError('Invalid runtime vendor registry')
    for vendor in vendors['vendors']:
        if hashlib.sha256((root/vendor['path']).read_bytes()).hexdigest()!=vendor['sha256']:
            raise ValueError('Runtime vendor changed without provenance update')
    return {'frozenTasks': len(tasks), 'activeWorkflows': len(active),'scripts':scripts}


def replay(task_id, output, execute=False, root=ROOT):
    root, output = Path(root).resolve(), Path(output).resolve()
    check(root)
    task = registry(root)[task_id]
    if output == root or output.is_relative_to(root) or output.exists():
        raise ValueError('Replay requires a new directory outside the working repository')
    # Detached worktree preserves the historical Git objects used by audit
    # fixtures, while changing neither main nor the caller working directory.
    subprocess.run(['git', 'worktree', 'add', '--detach', str(output), task['snapshot']], cwd=root, check=True)
    env = {k: v for k, v in os.environ.items() if k not in {'GH_TOKEN', 'GITHUB_TOKEN', 'GIT_ASKPASS', 'SSH_ASKPASS'}}
    env.update({'GIT_TERMINAL_PROMPT': '0', 'GIT_NO_LAZY_FETCH': '1', 'GIT_CONFIG_COUNT': '0'})
    report = {'task': task_id, 'snapshot': task['snapshot'], 'executed': [], 'directory': str(output)}
    for ref in task['scriptRefs']:
        if hashlib.sha256((output / ref['path']).read_bytes()).hexdigest() != ref['sha256']:
            raise ValueError('Frozen script digest mismatch: ' + ref['path'])
    if execute:
        for command in task['checks']:
            # The registry is declarative, not a shell script. Only registered
            # Python verifiers run; original collectors and push steps stay inert.
            if command[:4] != ['python3', '-m', 'unittest', 'discover'] and command != ['python3', 'scripts/validate_data.py'] and not (len(command) == 3 and command[0] == 'python3' and command[1].startswith('scripts/') and command[2] == '--check'):
                raise ValueError('Not an isolated verifier: ' + str(command))
            subprocess.run(command, cwd=output, env=env, check=True)
            report['executed'].append(command)
    status = subprocess.check_output(['git', 'status', '--porcelain'], cwd=output, text=True)
    report['workingTreeChanged'] = bool(status.strip())
    if status.strip():
        raise ValueError('Historical verifier changed its isolated source snapshot')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--task')
    parser.add_argument('--output')
    parser.add_argument('--execute-checks', action='store_true')
    parser.add_argument('--report', help='Write structured JSON separately from verifier logs')
    args = parser.parse_args()
    result = replay(args.task, args.output, args.execute_checks) if args.task else check()
    content = json.dumps(result, ensure_ascii=False, indent=2)+'\n'
    if args.report:
        Path(args.report).write_text(content)
    print(content)
