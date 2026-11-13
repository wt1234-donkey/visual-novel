"""One maintained validation sequence for releases and new batch candidates."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = [
    ['python3', 'scripts/generate_effective_views.py'],
    ['python3', 'scripts/validate_data.py'],
    ['python3', 'scripts/validate_entity_model.py'],
    ['python3', 'scripts/run_python_tests.py'],
    ['node', 'scripts/migrate_basic_storage.mjs', '--check'],
    ['node', 'scripts/migrate_formal_history.mjs', '--check'],
    ['node', 'scripts/migrate_source_identities.mjs', '--check'],
    ['python3', 'scripts/registry_store.py', '--check'],
    ['python3', 'scripts/workflow_governance.py', '--check'],
    ['node', '--test'],
    ['python3', 'scripts/build_company_pages.py', '--check'],
    ['python3', 'scripts/build_entity_model.py', '--check'],
    ['python3', 'scripts/build_entity_pages.py', '--check'],
]


def validate(root=ROOT):
    root = Path(root)
    for args in CHECKS:
        command = args + sorted(str(p.relative_to(root)) for p in (root / 'tests').glob('*.test.mjs')) if args == ['node', '--test'] else args
        subprocess.run(command, cwd=root, check=True)


if __name__ == '__main__':
    validate()
