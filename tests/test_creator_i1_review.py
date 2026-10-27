"""I1 changes only two historical identities and one scoped production credit."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '37a7d92010796ef272b69985bb7c514fdfdd0769'
SNAPSHOT = '142723dfcfc155e16f3eccbdefbdeca0649706d7'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorI1Tests(unittest.TestCase):
    def test_identity_and_credit_are_exactly_scoped(self):
        review = read('data/entity-creator-i1-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b = {e['id']: e for e in before['entities']}
        a = {e['id']: e for e in after['entities']}
        self.assertEqual(b.keys(), a.keys())
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for x in review['identityCorrections']})
        self.assertEqual(after['relations'], before['relations'])
        prior, current = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(current['credits'][:-1], prior['credits'])
        c = current['credits'][-1]
        self.assertEqual((c['entityId'], c['workId'], c['targetType'], c['role'], c['reviewId'], c['reviewRecord']),
                         ('entity-name-b72187fd26e6', 'nitroplus-extra-sonipro', 'work',
                          'originalProduction', 'AZI1-C01', review['audit']))
        self.assertEqual(current['dossierMemberships'], prior['dossierMemberships'])
        self.assertFalse(any(x['entityId'] == 'entity-ibm' and x['role'] in
                             {'originalProduction', 'developer', 'productionBrand'}
                             for x in current['credits']))
        self.assertFalse(any(x['entityId'] == c['entityId'] and
                             x['workId'] == 'alicesoft-extra-toushin2' and x['targetType'] == 'work'
                             for x in current['credits']))

    def test_order_and_original_data_are_preserved(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId'], p['nextName']),
                         ('I', 3, 13, 122, 132, 'entity-imel', 'iMel'))
        self.assertEqual(p['processedEntityIds'][-3:],
                         [x['entityId'] for x in read('data/entity-creator-i1-review-20261024.json')['reviewedEntities']])
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(catalogue_bytes(ROOT, path),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
