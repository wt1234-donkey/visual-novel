"""G3 completes G with one bounded original brand creation credit."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '4dfab7f'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorG3Tests(unittest.TestCase):
    def test_recorded_identity_and_scoped_creation(self):
        review = read('data/entity-creator-g3-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in d['entities']} for d in (before, after))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {c['entityId'] for c in review['identityCorrections']} | {c['entityId'] for c in read('data/entity-creator-h1-review-20261024.json')['identityCorrections']} | {c['entityId'] for c in read('data/entity-creator-h2-review-20261024.json')['identityCorrections']})
        self.assertEqual(before['relations'], after['relations'])
        for c in review['identityCorrections']:
            eid = c['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), (c['type'], 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        brand = 'entity-name-4d8bc5606e40'
        self.assertTrue(next(c for c in review['identityCorrections'] if c['entityId'] == brand)['preserveReleaseRoles'])

        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-12], before['credits'])
        self.assertEqual([m for m in after['dossierMemberships'] if m['dossierId'] != 'hulotte'],
                         [m for m in before['dossierMemberships'] if m['dossierId'] != 'hulotte'])
        c = after['credits'][-12]
        self.assertEqual((c['entityId'], c['workId'], c['targetType'], c['role'],
                          c['source'], c['reviewId'], c['reviewRecord']),
                         (brand, 'g650', 'work', 'productionBrand',
                          review['creditAdditions'][0]['source'], 'AZG3-C01', review['audit']))
        self.assertEqual([(x['targetId'], x['role']) for x in after['credits']
                          if x['entityId'] == brand and x['targetType'] == 'release'],
                         [('g650-v1', 'publisher')])
        self.assertEqual([x['role'] for x in after['credits']
                          if x['entityId'] == 'entity-name-7c36813da51c'],
                         ['publisher', 'publisher'])
        self.assertTrue(all(x['role'] == 'publisher' for x in after['credits']
                            if x['entityId'] == 'entity-name-5bae781ea87d'))

    def test_order_and_core_preservation(self):
        review = read('data/entity-creator-g3-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId'], p['nextName']),
                         ('H', 10, 12, 117, 119, 'entity-hummingbird_soft', 'HummingBird Soft（ハミングバードソフト）'))
        self.assertEqual(p['processedEntityIds'][104:107],
                         [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        node = next(n for n in after['nodes'] if n['id'] == 'entity-name-4d8bc5606e40')
        self.assertEqual((node['productionCount'], [x['workId'] for x in node['groups']['creation']]), (1, ['g650']))
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
