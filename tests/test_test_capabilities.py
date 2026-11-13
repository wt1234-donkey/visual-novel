import ast
import json
from pathlib import Path
import unittest
from history_contracts import contracts

ROOT = Path(__file__).resolve().parents[1]


class TestCapabilitiesTests(unittest.TestCase):
    def test_historical_modules_are_explicit_existing_frozen_audits(self):
        policy = json.loads((ROOT/'config/test-capabilities.json').read_text())
        modules = policy['historicalModules']
        self.assertEqual(len({row['module'] for row in modules}), len(modules))
        for row in modules:
            source = ROOT/'tests'/(row['module']+'.py')
            parsed = ast.parse(source.read_text())
            tests = [node for node in ast.walk(parsed) if isinstance(node, ast.FunctionDef) and node.name.startswith('test_')]
            self.assertEqual(len(tests), row['tests'], row['module'])
            self.assertEqual(row['capability'], 'historical-exact-delta')
        for row in policy['conditionalSkips']:
            self.assertTrue(row['ref'])
            self.assertTrue(row['limitation'])
            for name in row['alternative']:
                self.assertTrue((ROOT/name).is_file())

    def test_compact_evidence_covers_anchors_scoped_archive_and_queue(self):
        value = contracts()
        self.assertEqual(value['schemaVersion'], 1)
        self.assertEqual(len(value['dossierAnchors']), 80)
        self.assertEqual(len(value['pendingRoleClaims']['claims']), 601)
        self.assertTrue(value['retainedCatalogue']['html'])
        for descriptor in value['dossierAnchors'].values():
            self.assertEqual(len(descriptor['source']['commit']), 40)
            self.assertEqual(len(descriptor['source']['sha256']), 64)

    def test_history_downloads_and_real_device_gaps_are_not_silent_passes(self):
        policy = json.loads((ROOT/'config/test-capabilities.json').read_text())
        required = {row['id'] for row in policy['capabilities'] if row['required']}
        self.assertTrue({'current-contracts', 'audit-capacity', 'chromium-browser'} <= required)
        real = next(row for row in policy['capabilities'] if row['id'] == 'android-real-device')
        self.assertFalse(real['required'])
        self.assertIn('不等同', real['limitation'])
        runner = (ROOT/'scripts/run_python_tests.py').read_text()
        self.assertIn('args.fetch_history and not args.historical', runner)
        self.assertIn("all(row['registered'] for row in skipped)", runner)
