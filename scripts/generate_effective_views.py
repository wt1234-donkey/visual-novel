"""Regenerate disposable views from the current source and correction layers."""
import subprocess
import sys
from pathlib import Path


def generate(root):
    root = Path(root).resolve()
    subprocess.run(['node', str(root/'scripts/build_field_evidence.mjs'), '--export'], cwd=root, check=True)
    subprocess.run(['node', str(root/'scripts/build_audit_ledger.mjs')], cwd=root, check=True)
    for name in ('sync_versions_csv.py', 'export_content_csv.py', 'export_interaction_csv.py', 'build_company_pages.py', 'build_source_downloads.py'):
        subprocess.run([sys.executable, str(root/'scripts'/name)], cwd=root, check=True)


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1])
