"""I2 records two historical company identities without creating works or roles."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '142723dfcfc155e16f3eccbdefbdeca0649706d7'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorI2Tests(unittest.TestCase):
    def test_two_identity_changes_and_no_credit_change(self):
        review = read('data/entity-creator-i2-review-20261024.json')
        self.assertEqual(review['creditAdditions'], [])
        before, after = old('data/entities.json'), read('data/entities.json')
        b = {e['id']: e for e in before['entities']}
        a = {e['id']: e for e in after['entities']}
        self.assertEqual(b.keys(), a.keys())
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for x in review['identityCorrections']})
        self.assertEqual(after['relations'], before['relations'])
        self.assertEqual(read('data/credits.json'), old('data/credits.json'))
        self.assertEqual(a['entity-name-3de89d1ab0a5'], b['entity-name-3de89d1ab0a5'])
        self.assertEqual(a['entity-imel'], b['entity-imel'])
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_order_and_protected_files(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId'], p['nextName']),
                         ('I', 7, 13, 126, 132, 'entity-infocom', 'Infocom'))
        self.assertEqual(p['processedEntityIds'][-4:],
                         [x['entityId'] for x in read('data/entity-creator-i2-review-20261024.json')['reviewedEntities']])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
