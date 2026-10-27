"""O1 keeps original production, localization and later remakes scoped separately."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '155fac06ae47a7e20f2c5a3cf3bae0d3c75d3016'
BASE = '868d8ceac5575abd8144c4572d4de4c230954553'
ORIGIN = 'entity-name-a59a367044e7'
OTAKU = 'entity-name-4abb165f3e1e'
OVERFLOW = 'entity-name-8d45e971c1f6'
OVERDRIVE_WORKS = ['g641', 'g642', 'g643', 'g644', 'g645', 'g646', 'g648', 'g649', 'g651']


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorO1Tests(unittest.TestCase):
    def test_three_identity_categories_keep_names_dates_relations_and_publisher_roles(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in doc['entities']} for doc in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {ORIGIN, OTAKU, OVERFLOW})
        for eid, kind in [(ORIGIN, 'company'), (OTAKU, 'team'), (OVERFLOW, 'brand')]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        credits = read('data/credits.json')['credits']
        for eid, count in [(OVERFLOW, 2), (OTAKU, 1)]:
            scoped = [c for c in credits if c['entityId'] == eid]
            self.assertEqual(len(scoped), count)
            self.assertTrue(all(c['role'] == 'publisher' and c['targetType'] == 'release' for c in scoped))
        self.assertEqual(next(c for c in credits if c['entityId'] == OTAKU)['rawCredit'],
                         'mirai works / OTAKU Plan')

    def test_ten_credits_do_not_inherit_groover_or_overwrite_go_go_nippon(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-10], before['credits'])
        added = after['credits'][-10:]
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in added],
                         [(ORIGIN, 'toho-times-of-lore', 'originalProduction')] +
                         [('entity-overdrive', wid, 'productionBrand') for wid in OVERDRIVE_WORKS])
        self.assertEqual(len(after['credits']), 4956)
        self.assertTrue(all(c['targetType'] == 'work' and c['status'] == 'sourceReviewed' for c in added))
        green = [c for c in after['credits'] if c['entityId'] == 'entity-overdrive' and c['workId'] == 'g650']
        self.assertEqual([(c['targetType'], c['role']) for c in green], [('release', 'publishingBrand')])
        nippon = [c for c in after['credits'] if c['entityId'] == 'entity-overdrive' and c['workId'] == 'g647']
        self.assertEqual(len(nippon), 1)
        self.assertEqual(nippon[0]['role'], 'originalProduction')

    def test_only_nine_own_dossier_groups_change_toho_stays_pending_and_related(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']}
                  for d in [before, after]]
        expected = {('overdrive', wid) for wid in OVERDRIVE_WORKS}
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, expected)
        for key in expected:
            self.assertEqual(am[key], {**bm[key], 'roles': sorted(bm[key]['roles'] + ['productionBrand']),
                                      'group': 'original'})
            self.assertEqual((am[key]['placement'], am[key]['status']), ('main', 'existingEvidence'))
        self.assertEqual(am['toho', 'toho-times-of-lore'], bm['toho', 'toho-times-of-lore'])
        self.assertEqual((am['toho', 'toho-times-of-lore']['status'], am['toho', 'toho-times-of-lore']['placement']),
                         ('pendingRole', 'related'))
        self.assertEqual(len(am), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 604)

    def test_o_order_completion_deferred_evidence_and_protected_catalogue(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        ids = [ORIGIN, OTAKU, 'entity-overdrive', OVERFLOW]
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('O', 4, 4, 218, 218, 'entity-palette'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], ids)
        review = read('data/entity-creator-o1-review-20261025.json')
        self.assertEqual([q['entityId'] for q in review['progress']['queue']], ids)
        self.assertTrue(all(q['status'] == 'reviewed' for q in review['progress']['queue']))
        self.assertEqual([d['entityId'] for d in review['deferredReviews']], [OVERFLOW, OTAKU])
        self.assertIs(review['identityCorrections'][-1]['preserveReleaseRoles'], True)
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes['entity-overdrive']['productionCount'], 10)
        self.assertEqual(nodes[ORIGIN]['productionCount'], 0)
        self.assertEqual(after['works'], before['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
