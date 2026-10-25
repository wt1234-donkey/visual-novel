"""NOVECT review preserves original identities, credits and later-version boundaries."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '868d8ceac5575abd8144c4572d4de4c230954553'
BASE = '902e28791d2d8e4eceabd765416a2089ea0992d8'
WORKS = [f'g{i}' for i in range(191, 200)]


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT))
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorN5Tests(unittest.TestCase):
    def test_nine_original_credits_preserve_all_historical_release_signatures(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-9], before['credits'])
        added = after['credits'][-9:]
        self.assertEqual([c['workId'] for c in added], WORKS)
        for c in added:
            self.assertEqual((c['entityId'], c['targetType'], c['targetId'], c['role'],
                              c['rawCredit'], c['status']),
                             ('entity-novect', 'work', c['workId'], 'originalProduction',
                              'Novectacle', 'sourceReviewed'))
        self.assertEqual(len(after['credits']), 4946)
        self.assertEqual(sum(c['entityId'] == 'entity-novect' and c['targetType'] == 'release'
                             for c in after['credits']), 14)
        self.assertEqual(read('data/entities.json'), old('data/entities.json'))

    def test_only_nine_memberships_gain_original_role_without_changing_placement(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        expected = {('novect', wid) for wid in WORKS}
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, expected)
        for key in expected:
            self.assertEqual(am[key], {**bm[key], 'roles': ['originalProduction', 'publisher'],
                                      'group': 'original'})
            self.assertEqual((am[key]['placement'], am[key]['status']), ('main', 'existingEvidence'))
        self.assertEqual(len(am), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 604)

    def test_complete_n_queue_then_origin_without_reordering_previous_reviews(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId'], p['nextName']),
                         ('N', 21, 21, 214, 214, 'entity-name-a59a367044e7', 'Origin Systems'))
        self.assertEqual(p['processedEntityIds'][:-1], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-1], 'entity-novect')
        review = read('data/entity-creator-n5-review-20261025.json')
        self.assertTrue(all(q['status'] == 'reviewed' for q in review['progress']['queue']))
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes['entity-novect']['productionCount'], 9)
        self.assertEqual(after['works'], before['works'])

    def test_date_discrepancy_stays_explicit_and_catalogue_baselines_stay_intact(self):
        review = read('data/entity-creator-n5-review-20261025.json')
        self.assertEqual(review['identityCorrections'], [])
        self.assertEqual([(d['workId'], d['status']) for d in review['deferredReviews']],
                         [('g196', 'dateDiscrepancyNotApplied'), ('g199', 'pollAndGameDatesSeparated')])
        sources = {c['workId']: c['source'] for c in review['creditAdditions']}
        self.assertEqual(sources['g196'], 'https://novect.net/ranking2.html')
        self.assertEqual(sources['g199'], 'https://novect.net/rankingpart2.html')
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
