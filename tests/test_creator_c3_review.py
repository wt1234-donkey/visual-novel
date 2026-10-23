"""C3 updates three company identities without creating inferred game credits."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '4a321fa'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorC3Tests(unittest.TestCase):
    def test_scoped_identity_and_credit_diff(self):
        review = read('data/entity-creator-c3-review-20261023.json')
        before, after = ({e['id']: e for e in x['entities']} for x in [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {entry['entityId'] for entry in review['identityCorrections']})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((before[eid]['type'], before[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((after[eid]['type'], after[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((after[eid]['aliases'], after[eid]['dates']),
                             (before[eid]['aliases'], before[eid]['dates']))
        self.assertEqual(read('data/credits.json'), old('data/credits.json'))
        self.assertEqual(review['creditAdditions'], [])
        self.assertEqual(after['entity-name-21dcd9c9c1e7'], before['entity-name-21dcd9c9c1e7'])

    def test_contiguous_progress_and_creation_count(self):
        current, previous = read('data/organizations.json'), old('data/organizations.json')
        progress = current['registrationProgress']
        review = read('data/entity-creator-c3-review-20261023.json')
        self.assertEqual((progress['letter'], progress['letterProcessed'], progress['letterTotal'],
                          len(progress['processedEntityIds']), progress['total']), ('C', 15, 18, 57, 60))
        self.assertEqual(progress['nextEntityId'], 'entity-cuffs')
        self.assertEqual(progress['processedEntityIds'][42:], review['progress']['processedEntityIds'])
        nodes = {n['id']: n for n in current['nodes']}
        prior = {n['id']: n for n in previous['nodes']}
        for eid in review['progress']['processedEntityIds'][10:]:
            self.assertEqual(nodes[eid]['groups'], prior[eid]['groups'])
        self.assertEqual(nodes['entity-cube']['productionCount'], 11)
        self.assertEqual(current['works'], previous['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/entity-creator-c2-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
