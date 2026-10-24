"""D2 identity corrections preserve the historical release and creation records."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'c6c136c'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorD2Tests(unittest.TestCase):
    def test_scoped_corrections_and_unchanged_credits(self):
        review = read('data/entity-creator-d2-review-20261023.json')
        before, after = ({e['id']: e for e in data['entities']} for data in
                         [old('data/entities.json'), read('data/entities.json')])
        ids = {entry['entityId'] for entry in review['identityCorrections']}
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         ids | {c['entityId'] for c in read('data/entity-creator-d3-review-20261023.json')['identityCorrections']} | {c['entityId'] for batch in ['e1-review-20261023', 'e2-review-20261024', 'e3-review-20261024', 'f1-review-20261024', 'f2-review-20261024', 'g1-review-20261024', 'g2-review-20261024'] for c in read(f'data/entity-creator-{batch}.json')['identityCorrections']})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((before[eid]['type'], before[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((after[eid]['type'], after[eid]['verification']),
                             (correction['type'], 'sourceReviewed'))
            self.assertEqual((after[eid]['aliases'], after[eid]['dates']),
                             (before[eid]['aliases'], before[eid]['dates']))
        self.assertEqual(after['entity-name-16c097f224f4'], before['entity-name-16c097f224f4'])
        self.assertTrue(next(c for c in review['identityCorrections']
                             if c['rawName'] == 'DMM GAMES')['preserveReleaseRoles'])
        self.assertEqual(review['creditAdditions'], [])
        prior = {c['id']: c for c in old('data/credits.json')['credits']}
        self.assertEqual(prior, {c['id']: c for c in read('data/credits.json')['credits'] if c['id'] in prior})

    def test_contiguous_progress_and_original_placement(self):
        current, previous = read('data/organizations.json'), old('data/organizations.json')
        p = current['registrationProgress']
        review = read('data/entity-creator-d2-review-20261023.json')
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total']), ('G', 10, 13, 104, 107))
        self.assertEqual(p['processedEntityIds'][60:68], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextName'], 'Double Fine Productions')
        self.assertEqual(current['works'], previous['works'])
        nodes, prior = ({n['id']: n for n in data['nodes']} for data in [current, previous])
        for entry in review['reviewedEntities']:
            eid = entry['entityId']
            self.assertEqual(nodes[eid]['groups'], prior[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], 0)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/entity-creator-d1-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
