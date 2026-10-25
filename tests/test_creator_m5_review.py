"""M5 scopes brands without promoting their parents or merging namesakes."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '26e4b64b4faaae75f09aa2dfc512feb053b41ae2'
STATION = 'entity-name-297835568b98'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorM5Tests(unittest.TestCase):
    def test_one_brand_category_without_identity_merges_or_publisher_conversion(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {STATION})
        self.assertEqual((be[STATION]['type'], be[STATION]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((ae[STATION]['type'], ae[STATION]['verification']), ('brand', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates']:
            self.assertEqual(be[STATION][field], ae[STATION][field])
        self.assertEqual(after['relations'], before['relations'])
        self.assertEqual(ae['entity-name-5963707789d1']['type'], 'unknown')
        credits = read('data/credits.json')['credits']
        station = [c for c in credits if c['entityId'] == STATION]
        self.assertEqual(len(station), 4)
        self.assertTrue(all(c['targetType'] == 'release' and c['role'] == 'publisher' for c in station))

    def test_exact_seven_production_brands_preserve_all_old_credits(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-7], before['credits'])
        additions = after['credits'][-7:]
        expected = [('entity-minatosoft', w, 'productionBrand')
                    for w in ['g1242', 'g1243', 'g1253', 'g1256']]
        expected += [('entity-mirai', w, 'productionBrand') for w in ['g1268', 'g1269', 'g1270']]
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in additions], expected)
        self.assertTrue(all(c['targetType'] == 'work' and c['status'] == 'sourceReviewed'
                            for c in additions))
        self.assertTrue(all(c['rawCredit'] == ('みなとそふと' if c['entityId'] == 'entity-minatosoft'
                                               else 'mirai') for c in additions))

    def test_only_four_own_dossier_groups_change_without_clearing_parent_pending(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(), am.keys())
        changed = {k for k in bm if bm[k] != am[k]}
        self.assertEqual(changed, {('minatosoft', w) for w in ['g1242', 'g1243', 'g1253', 'g1256']})
        for key in bm:
            self.assertEqual(am[key]['placement'], bm[key]['placement'])
            self.assertEqual(am[key]['status'], bm[key]['status'])
        for key in changed:
            self.assertEqual((bm[key]['group'], am[key]['group']), ('release', 'original'))
        for work in ['g1242', 'g1243', 'g1253', 'g1256', 'g1268', 'g1269', 'g1270']:
            self.assertEqual(am['hawkeye', work]['status'], 'pendingRole')

    def test_alphabetic_progress_and_protected_catalogue(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('M', 25, 30, 188, 193, 'entity-name-935c3bc35045'))
        review = read('data/entity-creator-m5-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        self.assertTrue(review['identityCorrections'][0]['preserveReleaseRoles'])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 25 + ['pending'] * 5)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])
