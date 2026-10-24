"""D1 changes only D3's identity and preserves the previous creator index."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'e1a432f'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorD1Tests(unittest.TestCase):
    def test_one_identity_correction_and_no_new_credits(self):
        review = read('data/entity-creator-d1-review-20261023.json')
        before, after = ({e['id']: e for e in x['entities']} for x in [old('data/entities.json'), read('data/entities.json')])
        eid = 'entity-name-96d2374d7b76'
        self.assertEqual({i for i in before if before[i] != after[i]}, {eid} | {c['entityId'] for c in read('data/entity-creator-d2-review-20261023.json')['identityCorrections']} | {c['entityId'] for c in read('data/entity-creator-d3-review-20261023.json')['identityCorrections']} | {c['entityId'] for batch in ['e1-review-20261023', 'e2-review-20261024', 'e3-review-20261024', 'f1-review-20261024', 'f2-review-20261024', 'g1-review-20261024', 'g2-review-20261024', 'g3-review-20261024', 'h1-review-20261024', 'h2-review-20261024'] for c in read(f'data/entity-creator-{batch}.json')['identityCorrections']})
        self.assertEqual((before[eid]['type'], before[eid]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((after[eid]['type'], after[eid]['verification']), ('company', 'sourceReviewed'))
        self.assertEqual((after[eid]['aliases'], after[eid]['dates']), (before[eid]['aliases'], before[eid]['dates']))
        self.assertEqual(review['identityCorrections'][0]['entityId'], eid)
        self.assertEqual(review['creditAdditions'], [])
        prior = {c['id']: c for c in old('data/credits.json')['credits']}
        self.assertEqual(prior, {c['id']: c for c in read('data/credits.json')['credits'] if c['id'] in prior})

    def test_d_progress_and_original_placement(self):
        current, previous = read('data/organizations.json'), old('data/organizations.json')
        p = current['registrationProgress']
        review = read('data/entity-creator-d1-review-20261023.json')
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']), p['total']),
                         ('H', 12, 12, 119, 119))
        self.assertEqual(p['processedEntityIds'][60:64], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextName'], 'Digital Leisure')
        self.assertEqual(current['works'], previous['works'])
        nodes, before = ({n['id']: n for n in x['nodes']} for x in [current, previous])
        for eid in review['progress']['processedEntityIds']:
            self.assertEqual(nodes[eid]['groups'], before[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], 0)
        self.assertEqual(len(nodes['entity-dataeast']['groups']['pending']), 1)
        self.assertEqual(len(nodes['entity-db_soft']['groups']['pending']), 3)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/entity-creator-c4-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
