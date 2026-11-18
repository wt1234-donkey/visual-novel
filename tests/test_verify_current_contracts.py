"""Regression coverage for the post-save Git worktree snapshot."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'verify_current_contracts', ROOT / 'scripts/verify_current_contracts.py'
)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

OLD = 'data/basic-catalogue-journal/events/r31-r50.json'
NEW = 'data/basic-catalogue-journal/events/r31-r51.json'
RECEIPT = 'data/command-receipts/new-operation.json'
AUDIT = 'data/audit-ledger/objects/abc123.json'
OTHER = 'docs/keep.txt'


def git(root, *arguments):
    subprocess.run(['git', '-C', str(root), *arguments], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def write(root, path, value='{}'):
    target = root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(value)


class CandidateSourcesTests(unittest.TestCase):
    def fixture(self, root):
        git(root, 'init', '-q')
        write(root, OLD)
        write(root, OTHER, 'keep')
        git(root, 'add', OLD, OTHER)

    def test_rotated_event_and_new_receipt_audit_are_included(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / OLD).unlink()
            for path in (NEW, RECEIPT, AUDIT):
                write(root, path)
            write(root, 'unrelated.json')
            sources = MODULE.candidate_sources(root)
            self.assertNotIn(OLD, sources)
            self.assertIn(NEW, sources)
            self.assertIn(RECEIPT, sources)
            self.assertIn(AUDIT, sources)
            self.assertIn(OTHER, sources)
            self.assertNotIn('unrelated.json', sources)

    def test_staged_replacement_segment_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / OLD).unlink()
            write(root, NEW)
            git(root, 'add', NEW)
            sources = MODULE.candidate_sources(root)
            self.assertNotIn(OLD, sources)
            self.assertIn(NEW, sources)

    def test_missing_unrelated_tracked_file_still_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / OLD).unlink()
            (root / OTHER).unlink()
            write(root, NEW)
            with self.assertRaisesRegex(ValueError, 'docs/keep.txt'):
                MODULE.candidate_sources(root)

    def test_missing_journal_without_replacement_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            (root / OLD).unlink()
            with self.assertRaisesRegex(ValueError, 'r31-r50.json'):
                MODULE.candidate_sources(root)


if __name__ == '__main__':
    unittest.main()
