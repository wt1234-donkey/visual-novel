"""Reproduce the completed organization audit at its published merge.

The subsequent Leland catalogue expansion has its own current preservation check.
"""
import json
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BASE = 'e05836e6a4b5989dc3e7a03343ae7ee0b19fd61f'
SNAPSHOT = '8c16099af18e77b618f747223952d4e140e67b8f'

def completed(path):
    return subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT)

class OrganizationVerificationTests(unittest.TestCase):
    def test_catalogue_credits_relationships_and_baselines_are_unchanged(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/credits.json', 'data/work-classification.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/gameplay-catalogues.json', 'index.html']:
            self.assertEqual(completed(path), subprocess.check_output(
                ['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)
        before=json.loads(subprocess.check_output(['git','show',f'{BASE}:data/entities.json'],cwd=ROOT))
        after=json.loads(completed('data/entities.json'))
        prior={e['id']:e for e in before['entities']};current={e['id']:e for e in after['entities']}
        self.assertEqual(prior.keys(),current.keys())
        self.assertEqual({eid for eid in prior if prior[eid]!=current[eid]}, {'entity-name-21dcd9c9c1e7'})
        eid='entity-name-21dcd9c9c1e7'
        self.assertEqual({k for k in prior[eid] if prior[eid][k]!=current[eid][k]},
                         {'type','verification','historyNote'})
        self.assertEqual(after['relations'],before['relations'])
        self.assertEqual(after['dossiers'],before['dossiers'])
