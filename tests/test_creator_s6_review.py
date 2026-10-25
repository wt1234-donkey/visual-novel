"""Historical company identities never generate new production or release roles."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '5de7b25eecbf8a05f33bc4decb06b1edf6f3ab75'
IDS = ['entity-sinclair', 'entity-name-12a802d7d9bd', 'entity-smee', 'entity-name-ce72ada6adcb']
REVIEW = 'data/entity-creator-s6-review-20261026.json'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS6Tests(unittest.TestCase):
    def test_only_two_historical_company_identities_change_without_dates_or_relationships(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[1], IDS[3]})
        for eid in [IDS[1], IDS[3]]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 68)

    def test_all_credits_and_catalogue_objects_remain_exactly_unchanged(self):
        for path in ['data/credits.json', 'data/games.json', 'data/company-coverage.json',
                     'data/taxonomy.json', 'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        credits = read('data/credits.json')
        self.assertEqual(len(credits['credits']), 4986)
        self.assertEqual(len(credits['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in credits['dossierMemberships']), 602)
        for eid, expected in [(IDS[0], 2), (IDS[1], 7), (IDS[3], 1)]:
            rows = [c for c in credits['credits'] if c['entityId'] == eid]
            self.assertEqual(len(rows), expected)
            self.assertTrue(all(c['role'] == 'publisher' and c['targetType'] == 'release' for c in rows))
        self.assertEqual(sum(c['entityId'] == IDS[2] and c['role'] == 'productionBrand'
                             for c in credits['credits']), 25)
        self.assertEqual(read(REVIEW)['creditAdditions'], [])

    def test_four_consecutive_entities_advance_to_sol_press(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 23, 42, 260, 279, 'entity-name-539be8af5be9'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        r = read(REVIEW)
        self.assertEqual([x['entityId'] for x in r['reviewedEntities']], IDS)
        self.assertEqual([x['entityId'] for x in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 23 + ['pending'] * 19)
        self.assertEqual(after['works'], before['works'])
