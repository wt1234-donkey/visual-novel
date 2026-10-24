"""C4 finishes C without transferring brand or publisher credits into development."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ec95229'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorC4Tests(unittest.TestCase):
    def test_exact_identity_diff_and_unchanged_credits(self):
        review = read('data/entity-creator-c4-review-20261023.json')
        before, after = ({e['id']: e for e in x['entities']} for x in [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {entry['entityId'] for batch in [review, read('data/entity-creator-d1-review-20261023.json'), read('data/entity-creator-d2-review-20261023.json'), read('data/entity-creator-d3-review-20261023.json'), read('data/entity-creator-e1-review-20261023.json'), read('data/entity-creator-e2-review-20261024.json'), read('data/entity-creator-e3-review-20261024.json'), read('data/entity-creator-f1-review-20261024.json'), read('data/entity-creator-f2-review-20261024.json'), read('data/entity-creator-g1-review-20261024.json'), read('data/entity-creator-g2-review-20261024.json'), read('data/entity-creator-g3-review-20261024.json'), read('data/entity-creator-g3-review-20261024.json'), read('data/entity-creator-h1-review-20261024.json'), read('data/entity-creator-h2-review-20261024.json')] for entry in batch['identityCorrections']})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((before[eid]['type'], before[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((after[eid]['type'], after[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((after[eid]['aliases'], after[eid]['dates']),
                             (before[eid]['aliases'], before[eid]['dates']))
        self.assertEqual(after['entity-cuffs'], before['entity-cuffs'])
        prior = {c['id']: c for c in old('data/credits.json')['credits']}
        self.assertEqual(prior, {c['id']: c for c in read('data/credits.json')['credits'] if c['id'] in prior})
        self.assertEqual(review['creditAdditions'], [])

    def test_contiguous_completion_and_unchanged_core(self):
        current, previous = read('data/organizations.json'), old('data/organizations.json')
        p = current['registrationProgress']
        review = read('data/entity-creator-c4-review-20261023.json')
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']), p['total']),
                         ('H', 12, 12, 119, 119))
        self.assertEqual(review['progress']['nextEntityId'], 'entity-name-96d2374d7b76')
        self.assertEqual(p['processedEntityIds'][42:60], review['progress']['processedEntityIds'])
        self.assertEqual(current['works'], previous['works'])
        nodes, before = ({n['id']: n for n in x['nodes']} for x in [current, previous])
        for eid in [e['entityId'] for e in review['reviewedEntities']]:
            self.assertEqual(nodes[eid]['groups'], before[eid]['groups'])
        self.assertEqual(nodes['entity-cuffs']['productionCount'], 6)
        self.assertEqual(nodes['entity-name-42a2c095c251']['productionCount'], 0)
        self.assertEqual(nodes['entity-name-c65fb9857dc9']['productionCount'], 0)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/entity-creator-c3-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
