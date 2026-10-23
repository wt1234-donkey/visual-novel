"""Verify B3 correction evidence and absence of inferred creation credits."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'fa95711de1b628a7e34bf4bf01f596ec8dff925d'

def read(path):
    return json.loads((ROOT / path).read_text())

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

class CreatorB3Tests(unittest.TestCase):
    def test_scoped_changes_and_no_new_creators(self):
        review = read('data/entity-creator-b3-review-20261023.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = {e['id']: e for e in before['entities']}, {e['id']: e for e in after['entities']}
        corrected = {x['entityId'] for x in review['identityCorrections']}
        self.assertEqual(corrected, {'entity-name-cb3c445f13f2', 'entity-name-e0c32a99a906'})
        self.assertTrue(corrected <= {eid for eid in b if b[eid] != a[eid]})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
            self.assertTrue(correction['sources'])
        self.assertEqual(a['entity-name-8b16f2bf500e'], b['entity-name-8b16f2bf500e'])
        self.assertEqual(a['entity-name-f00bc453a063'], b['entity-name-f00bc453a063'])
        previous, current = old('data/credits.json'), read('data/credits.json')
        prior = {c['id']: c for c in previous['credits']}
        self.assertEqual(prior, {c['id']: c for c in current['credits'] if c['id'] in prior})

    def test_progress_and_core_immutability(self):
        org = read('data/organizations.json')
        p = org['registrationProgress']
        snapshot = read('data/entity-creator-b3-review-20261023.json')['progress']
        self.assertEqual((snapshot['letter'], len(snapshot['processedEntityIds']), snapshot['total']), ('B', 10, 10))
        self.assertEqual((snapshot['nextEntityId'], snapshot['nextName']), ('entity-cabbage', 'Cabbage Soft（きゃべつそふと）'))
        self.assertEqual(p['processedEntityIds'][:42], p['processedEntityIds'][:32] + snapshot['processedEntityIds'])
        self.assertEqual([r['entityId'] for r in p['reviewedEntities']], p['processedEntityIds'])
        self.assertEqual(org['works'], old('data/organizations.json')['works'])
        nodes = {n['id']: n for n in org['nodes']}
        prior = {n['id']: n for n in old('data/organizations.json')['nodes']}
        for eid in read('data/entity-creator-b3-review-20261023.json')['progress']['processedEntityIds'][6:]:
            self.assertEqual((nodes[eid]['groups'], nodes[eid]['productionCount']), (prior[eid]['groups'], prior[eid]['productionCount']))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                     'data/entity-creator-b2-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

if __name__ == '__main__':
    unittest.main()
