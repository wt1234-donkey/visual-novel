"""B1 audit: no inherited creator credit from Bandai Namco publishing."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '5124a2045af2ed9536a39acfd02ba620a72e4c29'

def read(path):
    return json.loads((ROOT / path).read_text())

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

class CreatorB1Tests(unittest.TestCase):
    def test_single_sourced_identity_correction(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = {e['id']: e for e in before['entities']}, {e['id']: e for e in after['entities']}
        self.assertTrue({'entity-name-4b075a5bed09'} <= {eid for eid in b if b[eid] != a[eid]})
        self.assertEqual(a['entity-name-4b075a5bed09']['type'], 'company')
        self.assertEqual(a['entity-name-4b075a5bed09']['verification'], 'sourceReviewed')
        self.assertEqual(a['entity-banpresto'], b['entity-banpresto'])
        previous, current = old('data/credits.json'), read('data/credits.json')
        self.assertEqual({c['id']: c for c in previous['credits']},
                         {c['id']: c for c in current['credits'] if c['id'] in {x['id'] for x in previous['credits']}})

    def test_progress_and_no_creator_inheritance(self):
        p = read('data/organizations.json')['registrationProgress']
        review = read('data/entity-creator-b1-review-20261023.json')
        self.assertIn(p['letter'], ['B', 'C', 'D', 'E'])
        self.assertEqual((review['progress']['total'], len(review['progress']['processedEntityIds'])), (10, 3))
        self.assertEqual(p['processedEntityIds'][32:35], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextEntityId'], 'entity-name-c45d1636d3b0')
        self.assertEqual([r['entityId'] for r in p['reviewedEntities']], p['processedEntityIds'])
        org = read('data/organizations.json')
        nodes = {n['id']: n for n in org['nodes']}
        prior = {n['id']: n for n in old('data/organizations.json')['nodes']}
        for eid in review['progress']['processedEntityIds']:
            self.assertEqual(nodes[eid]['groups'], prior[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], prior[eid]['productionCount'])
        self.assertEqual(org['works'], old('data/organizations.json')['works'])

    def test_core_and_prior_reviews_unchanged(self):
        paths = ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                 'data/gameplay-catalogues.json', 'data/work-classification.json',
                 'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                 'index.html', 'app.mjs', 'filter.mjs', 'styles.css', 'banpresto.html',
                 'data/entity-creator-a6-review-20261023.json',
                 'data/entity-creator-a6-review-20261023.md']
        for path in paths:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

if __name__ == '__main__':
    unittest.main()
