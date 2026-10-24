"""G2 identities have their own evidence and preserve every historical role."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '3458c01'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorG2Tests(unittest.TestCase):
    def test_only_documented_identity_changes(self):
        review = read('data/entity-creator-g2-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in d['entities']} for d in (before, after))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for x in review['identityCorrections']})
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(review['creditAdditions'], [])
        self.assertEqual(old('data/credits.json'), read('data/credits.json'))
        for x in review['identityCorrections']:
            eid = x['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), (x['type'], 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        self.assertEqual((a['entity-name-0956fc2c3ad0']['type'],
                          a['entity-name-0956fc2c3ad0']['verification']), ('unknown', 'unresolved'))
        gigas = 'entity-name-c30e25476da0'
        self.assertEqual(a[gigas]['type'], 'brand')
        self.assertTrue(next(x for x in review['identityCorrections'] if x['entityId'] == gigas)['preserveReleaseRoles'])
        self.assertEqual([x['role'] for x in after_credits()['credits'] if x['entityId'] == gigas], ['publisher'])

    def test_contiguous_order_and_main_database(self):
        review = read('data/entity-creator-g2-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextName']),
                         ('G', 10, 13, 104, 107, 'Good Smile Company'))
        self.assertEqual(p['processedEntityIds'][99:104],
                         [x['entityId'] for x in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


def after_credits():
    return read('data/credits.json')


if __name__ == '__main__':
    unittest.main()
