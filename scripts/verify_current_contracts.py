"""Run current Python and Node contracts in an isolated source tree with no Git objects."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def _git_paths(root, *arguments):
    """Read the Git index/worktree in NUL-delimited form (including staged changes)."""
    output = subprocess.check_output(['git', 'ls-files', '-z', *arguments], cwd=root)
    return {path for path in output.decode().split('\\0') if path}


def candidate_sources(root):
    """Snapshot the *post-command* candidate worktree, not the old Git index.

    A trusted save can replace an event segment and add receipts/audit objects
    before promotion. Allow only those new data files into the isolated test
    copy, and do not silently forgive unrelated missing tracked files.
    """
    root = Path(root)
    tracked = _git_paths(root, '--cached')
    untracked = _git_paths(root, '--others', '--exclude-standard')
    journal = 'data/basic-catalogue-journal/events/'
    receipt = 'data/command-receipts/'
    audit = 'data/audit-ledger/'
    created = {
        name for name in untracked
        if name.endswith('.json') and (
            name.startswith(journal) or name.startswith(receipt)
            or name.startswith(audit)
        )
    }
    missing = {name for name in tracked if not (root / name).exists()}
    # Only a journal segment rotation may remove a previously tracked file.
    # A replacement segment must be present (staged or untracked).
    has_replacement = any(name.startswith(journal) for name in created)
    if missing and (any(not name.startswith(journal) or not name.endswith('.json')
                        for name in missing) or not has_replacement):
        raise ValueError('Missing tracked candidate source without a replacement journal segment: '
                         + ', '.join(sorted(missing)))
    return sorted((tracked - missing) | created)


def verify(root=ROOT):
    root = Path(root)
    paths = candidate_sources(root)
    report_root = root/'test-results';report_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='atlas-current-no-history-') as directory:
        target = Path(directory)
        for name in sorted(paths):
            source = root/name
            if source.is_symlink() or not source.is_file():
                raise ValueError('Current contract source must be a regular tracked file: '+name)
            destination = target/name;destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        git = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=target,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if git.returncode == 0 or (target/'.git').exists():
            raise ValueError('Current contract proof unexpectedly contains Git metadata')
        commands = [[sys.executable, 'scripts/run_python_tests.py'],
                    ['node', '--test', *sorted(str(p.relative_to(target)) for p in (target/'tests').glob('*.test.mjs'))]]
        results = []
        for command in commands:
            result = subprocess.run(command, cwd=target)
            results.append({'command': command[:3], 'returncode': result.returncode})
            if result.returncode:
                break
        for source in (target/'test-results').glob('*.json'):
            shutil.copyfile(source, report_root/source.name)
        report = {'schemaVersion': 1, 'gitMetadataPresent': False, 'historicalObjectsAvailable': False,
                  'networkHistoryFetches': 0, 'sourceFiles': len(paths), 'results': results}
        (report_root/'current-checkout-proof.json').write_text(json.dumps(report, indent=2)+'\n')
        if len(results) != 2 or any(result['returncode'] for result in results):
            raise SystemExit('Current contracts failed without Git history; see test-results/current-checkout-proof.json')
        print(json.dumps(report))


if __name__ == '__main__':
    verify()
