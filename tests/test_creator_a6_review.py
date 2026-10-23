"""A6 completes the A queue with one identity-only correction and no new credits."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '638d68ce70afc044f3fa000de64911cfbfda0dcb'

def read(path):
    return json.loads((ROOT / path).read_text())

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

class CreatorA6ReviewTests(unittest.TestCase):
    def test_no_new_credits_and_azarashi_identity_only(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        additions = [c for c in after['credits'] if c['id'] not in {x['id'] for x in before['credits']}]
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in additions},
                         {('entity-name-53ec4c5b9afc', wid, 'productionBrand') for wid in ['g639', 'g640']})
        self.assertEqual({c['id']: c for c in before['credits']},
                         {c['id']: c for c in after['credits'] if c['id'] in {x['id'] for x in before['credits']}})
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = {e['id']: e for e in before['entities']}, {e['id']: e for e in after['entities']}
        self.assertEqual(a.keys(), b.keys())
        changed = {eid for eid in b if b[eid] != a[eid]}
        expected = {c['entityId'] for filename in ['a6', 'b1', 'b2', 'b3', 'c1']
                    for c in read(f'data/entity-creator-{filename}-review-20261023.json')['identityCorrections']}
        self.assertEqual(changed, expected)
        e = a['entity-name-a7f6066af4b9']
        self.assertEqual(e['type'], 'brand')
        self.assertEqual(e['verification'], 'sourceReviewed')
        self.assertEqual(e['aliases'], b['entity-name-a7f6066af4b9']['aliases'])
        self.assertEqual(e['dates'], b['entity-name-a7f6066af4b9']['dates'])

    def test_progress_completes_a_and_preserves_work_objects(self):
        org, review = read('data/organizations.json'), read('data/entity-creator-a6-review-20261023.json')
        p = org['registrationProgress']
        self.assertEqual(p['processedEntityIds'][:32], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextEntityId'], 'entity-name-40ed6431d1a6')
        self.assertEqual(review['progress']['nextName'], 'Bandai Namco Games')
        self.assertEqual([e['entityId'] for e in p['reviewedEntities']], p['processedEntityIds'])
        self.assertIn(review['audit'], p['audits'])
        self.assertEqual(org['works'], old('data/organizations.json')['works'])
        node = next(n for n in org['nodes'] if n['id'] == 'entity-name-a7f6066af4b9')
        old_node = next(n for n in old('data/organizations.json')['nodes'] if n['id'] == 'entity-name-a7f6066af4b9')
        self.assertEqual(node['groups'], old_node['groups'])
        self.assertEqual(node['productionCount'], 0)

    def test_core_baselines_unchanged(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                     'index.html', 'app.mjs', 'filter.mjs', 'styles.css']:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))

if __name__ == '__main__':
    unittest.main()
