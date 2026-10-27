"""Original production does not absorb external studios or child-brand credits."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '902fcc101e8495cdf72449e904b1972ca1b36e65'
IDS = ['entity-sierra_company', 'entity-silkys', 'entity-silkys_plus', 'entity-silkys_a5']
REVIEW = 'data/entity-creator-s4-review-20261026.json'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'5350087819ae8406336cb1dca05e83ccd0b3e001:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS4Tests(unittest.TestCase):
    def test_four_credits_preserve_all_earlier_credits_and_identities(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-4], before['credits'])
        self.assertEqual(len(after['credits']), 4984)
        actual = [(c['entityId'], c['targetType'], c['targetId'], c['role'])
                  for c in after['credits'][-4:]]
        self.assertEqual(actual, [
            (IDS[0], 'work', 'g001', 'originalProduction'),
            (IDS[0], 'work', 'g060', 'originalProduction'),
            (IDS[0], 'work', 'g061', 'originalProduction'),
            (IDS[3], 'work', 'g473', 'productionBrand')])
        for c in after['credits'][-4:]:
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
            self.assertEqual(c['status'], 'sourceReviewed')
        self.assertEqual(applied('data/entities.json'), old('data/entities.json'))
        for eid in IDS[:3]:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid and c['targetType'] == 'release'],
                             [c for c in before['credits'] if c['entityId'] == eid and c['targetType'] == 'release'])

    def test_only_three_sierra_memberships_change_and_parent_brand_remains_pending(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']}
                  for d in [before, after]]
        self.assertEqual(bm.keys(), am.keys())
        expected = {('sierra', 'g001'), ('sierra', 'g060'), ('sierra_on_line', 'g061')}
        self.assertEqual({k for k in bm if bm[k] != am[k]}, expected)
        for key in expected:
            self.assertEqual(bm[key]['roles'], ['publisher'])
            self.assertEqual(am[key]['roles'], ['originalProduction', 'publisher'])
            self.assertEqual(am[key]['group'], 'original')
            self.assertEqual(am[key]['placement'], bm[key]['placement'])
        self.assertEqual(am[('silkys_plus', 'g473')], bm[('silkys_plus', 'g473')])
        self.assertEqual(am[('silkys_plus', 'g473')]['status'], 'pendingRole')
        self.assertEqual(am[('ibm', 'g060')], bm[('ibm', 'g060')])
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 602)
        self.assertEqual(len(am), 2234)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-review.json', 'data/content-migration-baseline.json',
                     'data/entity-migration-baseline.json']:
            self.assertEqual(applied(path), old(path), path)

    def test_order_advances_four_entities_to_alpha_without_catalogue_admission_changes(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 15, 42, 252, 279, 'entity-name-8c9d353d6fe9'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        r = read(REVIEW)
        self.assertEqual([x['entityId'] for x in r['reviewedEntities']], IDS)
        self.assertEqual([x['entityId'] for x in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 15 + ['pending'] * 27)
        self.assertEqual(after['works'], before['works'])
