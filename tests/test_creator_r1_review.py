"""R1 confirms publishing identities without manufacturing development credits."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '58b45245bff79731dcb9bbaa953f47e51e56ca68'
RAIN = 'entity-name-bceb1074c614'
RED = 'entity-name-128195244522'
RIGHT = 'entity-name-61e191a86b41'
IDS = [RAIN, RED, RIGHT]


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'73fb2c7fe6f7af48a112236e4643ef95a54e38da:{path}'], cwd=ROOT))
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorR1Tests(unittest.TestCase):
    def test_three_identity_corrections_preserve_names_dates_and_relationships(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(IDS))
        for eid, kind in [(RAIN, 'brand'), (RED, 'company'), (RIGHT, 'company')]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 76)
        review = read('data/entity-creator-r1-review-20261025.json')
        self.assertIs(review['identityCorrections'][0]['preserveReleaseRoles'], True)
        self.assertIn('https://info.gbiz.go.jp/hojin/ichiran?hojinBango=5010001104414', ae[RED]['sources'])
        self.assertIn('https://rightway.net/company', ae[RIGHT]['sources'])

    def test_every_existing_credit_and_membership_is_unchanged(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(before, after)
        self.assertEqual(len(after['credits']), 4962)
        self.assertEqual(len(after['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 604)
        for eid, count in [(RAIN, 2), (RED, 1), (RIGHT, 7)]:
            scoped = [c for c in after['credits'] if c['entityId'] == eid]
            self.assertEqual(len(scoped), count)
            self.assertTrue(all(c['targetType'] == 'release' and c['role'] == 'publisher' for c in scoped))
        review = read('data/entity-creator-r1-review-20261025.json')
        self.assertEqual(review['creditAdditions'], [])
        for dossier in ['minatosoft', 'hawkeye']:
            m = next(m for m in after['dossierMemberships'] if m['workId'] == 'g1265' and m['dossierId'] == dossier)
            self.assertEqual((m['roles'], m['status']), (['catalogueAssociation'], 'pendingRole'))

    def test_catalogue_placements_sources_and_migration_baselines_are_protected(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        games = read('data/games.json')
        self.assertEqual([len(games[k]) for k in ['works', 'contentVersions', 'platformReleases']], [1274, 1487, 2487])

    def test_r_order_and_evidence_gaps_are_registered_before_riverhill(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']), ('R', 3, 5, 235, 237, 'entity-riverhill_soft'))
        self.assertEqual(p['processedEntityIds'][:-3], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-3:], IDS)
        review = read('data/entity-creator-r1-review-20261025.json')
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 3 + ['pending'] * 2)
        self.assertEqual([d['entityId'] for d in review['deferredReviews']], IDS)
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual([nodes[e]['productionCount'] for e in IDS], [0, 0, 0])
        self.assertEqual(nodes[RIGHT]['stats'], {'main': 4, 'related': 0, 'bibliography': 0})
        self.assertEqual(after['works'], before['works'])
