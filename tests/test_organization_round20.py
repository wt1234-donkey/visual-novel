import json
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE='6f69f7e505a2330b9068ec1a31687331f9aea0d6'
class OrganizationRound20Tests(unittest.TestCase):
    def test_formal_records_and_published_evidence_remain_unchanged(self):
        for path in ['data/entities.json','data/credits.json','data/games.json','data/company-coverage.json',
                     'data/taxonomy.json','data/work-classification.json','data/work-notes.json',
                     'data/entity-migration-baseline.json','data/content-migration-baseline.json',
                     'data/organization-verification-20261027.json','data/organization-verification-round16-20261027.json',
                     'data/organization-context-20261027.json','data/organization-context-round16-20261027.json',
                     'data/relationships-preview-config.json','index.html']:
            self.assertEqual(subprocess.check_output(['git','show',f'f733af9f4295471570106d88487c4608d0cb78aa:{path}'],cwd=ROOT),subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT),path)
    def test_delta_preserves_the_single_pending_claim_without_forcing_resolution(self):
        delta=json.loads((ROOT/'data/organization-verification-round20-20261027.json').read_text())
        self.assertEqual(len(delta['records']),37)
        pending=[r for r in delta['records'] if r['status']=='仍待核']
        self.assertEqual([r['recordId'] for r in pending],['duty-558'])
        self.assertTrue(pending[0]['sources'])
        context=json.loads((ROOT/'data/organization-context-round20-20261027.json').read_text())
        self.assertEqual(len(context['nodeNotes']),16);self.assertEqual(len(context['events']),8)
        self.assertEqual(context['edgeReviews'],[])
