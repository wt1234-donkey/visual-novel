"""H1 registers one documented company identity without extending creation roles."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f61b8d9'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorH1Tests(unittest.TestCase):
    def test_sourced_company_identity_does_not_create_work_credit(self):
        review = read('data/entity-creator-h1-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in data['entities']} for data in (before, after))
        eid = 'entity-name-2f2c43ae71dc'
        self.assertEqual({i for i in b if b[i] != a[i]}, {eid} | {x['entityId'] for x in read('data/entity-creator-h2-review-20261024.json')['identityCorrections']})
        self.assertEqual([c['entityId'] for c in review['identityCorrections']], [eid])
        self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((a[eid]['type'], a[eid]['verification']), ('company', 'sourceReviewed'))
        self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(review['creditAdditions'], [])
        self.assertEqual(read('data/credits.json')['credits'][:-15], old('data/credits.json')['credits'])
        self.assertEqual([m for m in read('data/credits.json')['dossierMemberships'] if m['dossierId'] not in {'hulotte', 'hummingbird_soft'}],
                         [m for m in old('data/credits.json')['dossierMemberships'] if m['dossierId'] not in {'hulotte', 'hummingbird_soft'}])
        publisher = [c for c in read('data/credits.json')['credits'] if c['entityId'] == eid]
        self.assertEqual([(c['targetId'], c['role']) for c in publisher], [('g1167-v-original', 'publisher')])

    def test_alphabetical_progress_and_preserved_catalogue(self):
        review = read('data/entity-creator-h1-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId'], p['nextName']),
                         ('H', 12, 12, 119, 119, 'entity-ibm', 'IBM'))
        self.assertEqual(p['processedEntityIds'][107:112],
                         [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes['entity-harukaze']['productionCount'], 4)
        self.assertEqual(nodes['entity-hawkeye']['productionCount'], 0)
        self.assertEqual(nodes['entity-name-2f2c43ae71dc']['productionCount'], 0)
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
