"""Riverhill original production never overwrites publishing or later port scopes."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '73fb2c7fe6f7af48a112236e4643ef95a54e38da'
RIVER = 'entity-riverhill_soft'
RUSSELL = 'entity-name-72929f935a72'
WORKS = ['g942', 'g1178', 'g1179', 'g1180', 'g1181', 'g1182', 'g1187', 'g1191', 'g1192', 'riverhill-dora']
BELL = 'https://www.bellwood-inc.jp/'
HORI = 'https://www.gamespark.jp/article/2026/04/26/165712.html'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'e43530441600b96d854c2feb0567c5455c6a6746:{path}'], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorR2Tests(unittest.TestCase):
    def test_only_russell_identity_changes_and_riverhill_object_is_preserved(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {RUSSELL})
        self.assertEqual((be[RUSSELL]['type'], be[RUSSELL]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((ae[RUSSELL]['type'], ae[RUSSELL]['verification']), ('company', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[RUSSELL].get(field), ae[RUSSELL].get(field))
        self.assertEqual(be[RIVER], ae[RIVER])
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 75)

    def test_ten_work_credits_append_without_changing_any_existing_release_or_role(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-10], before['credits'])
        actual = [(c['entityId'], c['targetType'], c['targetId'], c['workId'], c['role'],
                   c['rawCredit'], c['status']) for c in after['credits'][-10:]]
        self.assertEqual(actual, [(RIVER, 'work', w, w, 'originalProduction', 'リバーヒルソフト', 'sourceReviewed')
                                  for w in WORKS])
        self.assertEqual([c['source'] for c in after['credits'][-10:]], [BELL] * 7 + [HORI] * 3)
        self.assertEqual(len(after['credits']), 4972)
        scoped = [c for c in after['credits'] if c['entityId'] == RIVER]
        self.assertEqual(len(scoped), 45)
        self.assertEqual(sum(c['role'] == 'publisher' for c in scoped), 35)
        self.assertEqual([c['role'] for c in after['credits'] if c['entityId'] == RUSSELL], ['publisher'])
        review = read('data/entity-creator-r2-review-20261025.json')
        changes = review['creditAdditions']
        self.assertEqual([c['expectedPlacement'] for c in changes], ['main'] * 9 + ['related'])
        self.assertEqual({c['workId'] for c in changes if c['dossierId']}, {'g1187', 'riverhill-dora'})
        self.assertNotIn('g831', [c['workId'] for c in changes])

    def test_ten_scoped_membership_changes_leave_other_members_and_core_data_unchanged(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']} for d in [before, after]]
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, {('riverhill_soft', w) for w in WORKS})
        for w in WORKS:
            key = ('riverhill_soft', w)
            expected = {**bm[key], 'roles': ['originalProduction', 'publisher'], 'group': 'original'}
            if w in ['g1187', 'riverhill-dora']:
                self.assertEqual(bm[key]['status'], 'pendingRole')
                expected.update(roles=['originalProduction'], status='existingEvidence', source=BELL if w == 'g1187' else HORI)
            self.assertEqual(am[key], expected)
        self.assertEqual(len(am), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 602)
        self.assertEqual(sum(m['status'] == 'pendingRole' and m['dossierId'] == 'riverhill_soft' for m in am.values()), 13)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_r_finishes_in_order_with_saga_next_and_related_production_not_promoted(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']), ('R', 5, 5, 237, 237, 'entity-sagaplanets'))
        self.assertEqual(p['processedEntityIds'][:-2], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-2:], [RIVER, RUSSELL])
        review = read('data/entity-creator-r2-review-20261025.json')
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 5)
        self.assertEqual([d['entityId'] for d in review['deferredReviews']], [RIVER, RUSSELL])
        self.assertEqual(len(review['reviewedEntities'][0]['workIds']), 48)
        self.assertEqual(len(review['deferredReviews'][0]['workIds']), 38)
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes[RIVER]['productionCount'], 9)
        self.assertEqual(len(nodes[RIVER]['groups']['creation']), 10)
        self.assertEqual(nodes[RUSSELL]['productionCount'], 0)
        self.assertEqual(after['works'], before['works'])
