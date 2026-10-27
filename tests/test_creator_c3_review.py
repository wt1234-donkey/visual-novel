"""C3 updates three company identities without creating inferred game credits."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = '4a321fa'


def read(path):
    return load_snapshot(ROOT, path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorC3Tests(unittest.TestCase):
    def test_scoped_identity_and_credit_diff(self):
        review = read('data/entity-creator-c3-review-20261023.json')
        before, after = ({e['id']: e for e in x['entities']} for x in [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {entry['entityId'] for batch in [review, read('data/entity-creator-c4-review-20261023.json'), read('data/entity-creator-d1-review-20261023.json'), read('data/entity-creator-d2-review-20261023.json'), read('data/entity-creator-d3-review-20261023.json'), read('data/entity-creator-e1-review-20261023.json'), read('data/entity-creator-e2-review-20261024.json'), read('data/entity-creator-e3-review-20261024.json'), read('data/entity-creator-f1-review-20261024.json'), read('data/entity-creator-f2-review-20261024.json'), read('data/entity-creator-g1-review-20261024.json'), read('data/entity-creator-g2-review-20261024.json'), read('data/entity-creator-g3-review-20261024.json'), read('data/entity-creator-h1-review-20261024.json'), read('data/entity-creator-h2-review-20261024.json')]
                          for entry in batch['identityCorrections']})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((before[eid]['type'], before[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((after[eid]['type'], after[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((after[eid]['aliases'], after[eid]['dates']),
                             (before[eid]['aliases'], before[eid]['dates']))
        prior = {c['id']: c for c in old('data/credits.json')['credits']}
        self.assertEqual(prior, {c['id']: c for c in read('data/credits.json')['credits'] if c['id'] in prior})
        self.assertEqual(review['creditAdditions'], [])
        self.assertEqual(after['entity-name-21dcd9c9c1e7'], before['entity-name-21dcd9c9c1e7'])

    def test_contiguous_progress_and_creation_count(self):
        current, previous = read('data/organizations.json'), old('data/organizations.json')
        progress = current['registrationProgress']
        review = read('data/entity-creator-c3-review-20261023.json')
        self.assertEqual((progress['letter'], progress['letterProcessed'], progress['letterTotal'],
                          len(progress['processedEntityIds']), progress['total']), ('H', 12, 12, 119, 119))
        self.assertEqual(review['progress']['nextEntityId'], 'entity-cuffs')
        self.assertEqual(progress['processedEntityIds'][42:57], review['progress']['processedEntityIds'])
        nodes = {n['id']: n for n in current['nodes']}
        prior = {n['id']: n for n in previous['nodes']}
        for eid in review['progress']['processedEntityIds'][10:]:
            self.assertEqual(nodes[eid]['groups'], prior[eid]['groups'])
        self.assertEqual(nodes['entity-cube']['productionCount'], 11)
        self.assertEqual(current['works'], previous['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/entity-creator-c2-review-20261023.json']:
            self.assertEqual(catalogue_bytes(ROOT, path),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
