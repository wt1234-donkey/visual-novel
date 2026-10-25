"""P3 separates original PSK/Purple work from current brands and reissues."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '172ad9c4edd2e7e5459f02fa9055381ecd8cb9f9'
PSK = 'entity-psk'
PURPLE = 'entity-name-fb321fae98fc'
OLD_PURPLE = 'entity-jast_purple'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'5e51901e0d03ab96a712051913d6df99fcdfac7b:{path}'], cwd=ROOT))
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorP3Tests(unittest.TestCase):
    def test_only_current_purple_identity_changes_without_merging_historical_brand(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {PURPLE})
        self.assertEqual((be[PURPLE]['type'], be[PURPLE]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((ae[PURPLE]['type'], ae[PURPLE]['verification']), ('brand', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[PURPLE].get(field), ae[PURPLE].get(field))
        for eid in [PSK, OLD_PURPLE]:
            self.assertEqual(be[eid], ae[eid])
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 80)
        review = read('data/entity-creator-p3-review-20261025.json')
        self.assertIs(review['identityCorrections'][0]['preserveReleaseRoles'], True)

    def test_two_original_credits_preserve_all_old_publishing_and_release_scopes(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        actual = [(c['entityId'], c['targetType'], c['targetId'], c['workId'], c['role'],
                   c['rawCredit'], c['status']) for c in after['credits'][-2:]]
        self.assertEqual(actual, [
            (PSK, 'work', 'g1096', 'g1096', 'originalProduction', 'PSK', 'sourceReviewed'),
            (OLD_PURPLE, 'work', 'g673', 'g673', 'productionBrand', 'Purple', 'sourceReviewed')])
        self.assertEqual(len(after['credits']), 4960)
        self.assertEqual([c['source'] for c in after['credits'][-2:]], [
            'https://prtimes.jp/main/html/rd/p/000000104.000069696.html',
            'https://www.blackrainbow.jp/dvdpg/006/index.html'])
        current = [c for c in after['credits'] if c['entityId'] == PURPLE]
        self.assertEqual(len(current), 1)
        self.assertEqual((current[0]['role'], current[0]['targetType']), ('publisher', 'release'))
        self.assertEqual(sum(c['entityId'] == PSK and c['role'] == 'publisher' for c in after['credits']), 5)
        self.assertEqual(sum(c['entityId'] == OLD_PURPLE and c['role'] in {'publishingBrand', 'originalPublishingBrand'}
                             for c in after['credits']), 12)

    def test_only_psk_hospital_membership_changes_and_catalogue_objects_are_protected(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']}
                  for d in [before, after]]
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, {('psk', 'g1096')})
        expected = {**bm[('psk', 'g1096')], 'roles': ['originalProduction', 'publisher'], 'group': 'original'}
        self.assertEqual(am[('psk', 'g1096')], expected)
        self.assertEqual(am[('jast', 'g673')]['status'], 'pendingRole')
        self.assertEqual(am[('jast', 'g673')]['roles'], ['catalogueAssociation'])
        self.assertEqual(len(am), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 604)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_p_completed_in_order_with_deferred_scopes_and_quest_next(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']),
                         ('P', 13, 13, 231, 231, 'entity-name-5c50162a1fac'))
        self.assertEqual(p['processedEntityIds'][:-3], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-3:], [PSK, PURPLE, OLD_PURPLE])
        review = read('data/entity-creator-p3-review-20261025.json')
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 13)
        self.assertEqual([d['entityId'] for d in review['deferredReviews']], [PSK, PURPLE, OLD_PURPLE])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual([nodes[e]['productionCount'] for e in [PSK, PURPLE, OLD_PURPLE]], [1, 0, 1])
        self.assertEqual(after['works'], before['works'])
