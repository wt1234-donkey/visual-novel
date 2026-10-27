"""M2 separates present/historical companies, a brand and a composite credit."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = 'c88ede63da5767fcd562eaa69abc1c83c976d54c'
BASE = 'c1932b1c879f15bfd411d4782a9f183f1baff929'


def read(path):
    if path in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorM2Tests(unittest.TestCase):
    def test_exact_three_categories_and_no_identity_merge_or_relation(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {'entity-name-35ae58bf892b': 'company',
                    'entity-name-ff103df997b5': 'company',
                    'entity-name-170de3c8b237': 'brand'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(expected))
        for eid, kind in expected.items():
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(be[eid][field], ae[eid][field])
        for eid in ['entity-name-85a1fd56da66', 'entity-name-770b8bb9bcbc', 'entity-name-fec7ac8f12b1']:
            self.assertEqual(ae[eid], be[eid])
        self.assertEqual(after['relations'], before['relations'])

    def test_no_credit_or_membership_change_after_brand_correction(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after, before)
        masaya = [c for c in after['credits'] if c['entityId'] == 'entity-name-170de3c8b237']
        self.assertEqual([(c['role'], c['targetType'], c['rawCredit']) for c in masaya],
                         [('publisher', 'release', 'メサイヤ')])
        review = read('data/entity-creator-m2-review-20261025.json')
        self.assertEqual(review['creditAdditions'], [])
        self.assertTrue(review['identityCorrections'][-1]['preserveReleaseRoles'])

    def test_alphabetic_progress_and_catalogue_preservation(self):
        orgs = read('data/organizations.json')
        p = orgs['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('M', 10, 30, 173, 193, 'entity-name-fec7ac8f12b1'))
        review = read('data/entity-creator-m2-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 10 + ['pending'] * 20)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(orgs['works'], old('data/organizations.json')['works'])
