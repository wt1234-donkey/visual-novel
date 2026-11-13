"""Run current Python and Node contracts in an isolated source tree with no Git objects."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    root = Path(root)
    paths = subprocess.check_output(['git', 'ls-files', '-z'], cwd=root).decode().split('\0')
    paths = {name for name in paths if name}
    # A trusted command may have just generated new immutable archive objects.
    paths.update(str(p.relative_to(root)) for p in (root/'data/audit-ledger').rglob('*.json'))
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
