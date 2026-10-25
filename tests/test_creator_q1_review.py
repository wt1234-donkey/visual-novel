"""Quest originals stay distinct from later ports, content and corporate transfers."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '5e51901e0d03ab96a712051913d6df99fcdfac7b'
QUEST = 'entity-name-5c50162a1fac'
WORKS = ['riverhill-ogre', 'riverhill-tactics']


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorQ1Tests(unittest.TestCase):
    def test_only_quest_identity_changes_without_new_dates_relations_or_dossiers(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {QUEST})
        self.assertEqual((be[QUEST]['type'], be[QUEST]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((ae[QUEST]['type'], ae[QUEST]['verification']), ('company', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[QUEST].get(field), ae[QUEST].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 79)
        self.assertIn('https://www.hd.square-enix.com/jpn/ir/pdf/0402-200305220000-01.pdf', ae[QUEST]['sources'])

    def test_two_original_production_credits_leave_all_existing_roles_unchanged(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        actual = [(c['entityId'], c['targetType'], c['targetId'], c['workId'], c['role'],
                   c['rawCredit'], c['status']) for c in after['credits'][-2:]]
        self.assertEqual(actual, [(QUEST, 'work', w, w, 'originalProduction', 'クエスト', 'sourceReviewed')
                                  for w in WORKS])
        self.assertEqual(len(after['credits']), 4962)
        self.assertTrue(all(c['source'] == 'https://www.4gamer.net/games/116/G011621/20110426090/'
                            for c in after['credits'][-2:]))
        scoped = [c for c in after['credits'] if c['entityId'] == QUEST]
        self.assertEqual(len(scoped), 4)
        releases = [c for c in scoped if c['targetType'] == 'release']
        self.assertEqual([c['role'] for c in releases], ['publisher'] * 2)
        self.assertEqual([c['targetId'] for c in releases], [w + '-v-original' for w in WORKS])
        review = read('data/entity-creator-q1-review-20261025.json')
        self.assertEqual([c['expectedPlacement'] for c in review['creditAdditions']], ['related'] * 2)
        self.assertTrue(all(c['dossierId'] is None for c in review['creditAdditions']))

    def test_all_memberships_placements_and_catalogue_objects_are_unchanged(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(before['dossierMemberships'], after['dossierMemberships'])
        self.assertEqual(len(after['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 604)
        for w in WORKS:
            m = next(m for m in after['dossierMemberships'] if m['workId'] == w)
            self.assertEqual((m['dossierId'], m['placement'], m['roles'], m['group']),
                             ('riverhill_soft', 'related', ['publisher'], 'release'))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_q_finishes_in_order_without_promoting_related_works_and_rainbird_next(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']),
                         ('Q', 1, 1, 232, 232, 'entity-name-bceb1074c614'))
        self.assertEqual(p['processedEntityIds'][:-1], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-1], QUEST)
        review = read('data/entity-creator-q1-review-20261025.json')
        self.assertEqual(review['progress']['queue'], [dict(entityId=QUEST, name='Quest（クエスト）', status='reviewed')])
        self.assertEqual([d['entityId'] for d in review['deferredReviews']], [QUEST])
        node = next(n for n in after['nodes'] if n['id'] == QUEST)
        self.assertEqual((node['type'], node['productionCount']), ('company', 0))
        self.assertEqual({w['workId'] for w in node['groups']['creation']}, set(WORKS))
        self.assertEqual(node['stats'], {'main': 0, 'related': 2, 'bibliography': 0})
        self.assertEqual(after['works'], before['works'])
