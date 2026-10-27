"""The branch ledger changes presentation evidence, never formal identity or credits."""
import hashlib
import json
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='fb69d2f381a483c6214f7807c551149b6264f6f7'

class OrganizationRound16Tests(unittest.TestCase):
    def test_all_formal_catalogues_and_previous_evidence_are_preserved(self):
        for path in ['data/entities.json','data/credits.json','data/games.json','data/company-coverage.json',
                     'data/gameplay-catalogues.json','data/work-notes.json','data/taxonomy.json',
                     'data/work-classification.json','data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json','data/organization-verification-20261027.json',
                     'data/organization-context-20261027.json','data/relationships-preview-config.json','index.html']:
            self.assertEqual((ROOT/path).read_bytes(),subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path)
    def test_revision_chain_and_historical_events_have_specific_evidence(self):
        baseline=ROOT/'data/organization-verification-20261027.json'
        delta=json.loads((ROOT/'data/organization-verification-round16-20261027.json').read_text())
        self.assertEqual(delta['baselineSha256'],hashlib.sha256(baseline.read_bytes()).hexdigest())
        self.assertEqual(len(delta['records']),195)
        context=json.loads((ROOT/'data/organization-context-round16-20261027.json').read_text())
        self.assertEqual(len(context['nodeNotes']),22)
        self.assertEqual(len(context['events']),12)
        self.assertEqual(context['edgeReviews'],[])
        self.assertTrue(all(r['recordIds'] and r['note'] for r in context['nodeNotes']+context['events']))
