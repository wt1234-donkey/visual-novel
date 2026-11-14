"""One maintained validation sequence for releases and new batch candidates."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKS = [
    ['node', 'scripts/seal_catalogue_write.mjs', '--check'],
    ['python3', 'scripts/historical_rules.py', '--check'],
    ['python3', 'scripts/validate_public_entries.py'],
    ['python3', 'scripts/generate_effective_views.py'],
    ['python3', 'scripts/validate_data.py'],
    ['python3', 'scripts/validate_entity_model.py'],
    ['python3', 'scripts/manage_catalogue.py', '--check'],
    ['python3', 'scripts/verify_current_contracts.py'],
    ['node', 'scripts/migrate_basic_storage.mjs', '--check'],
    ['node', 'scripts/migrate_formal_history.mjs', '--check'],
    ['node', 'scripts/migrate_source_identities.mjs', '--check'],
    ['node', 'scripts/build_field_evidence.mjs', '--check'],
    ['node', 'scripts/build_audit_ledger.mjs', '--check'],
    ['python3', 'scripts/registry_store.py', '--check'],
    ['python3', 'scripts/workflow_governance.py', '--check'],
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
