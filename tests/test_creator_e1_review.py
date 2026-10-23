"""E1 checks source scoped identity changes without assigning new creation roles."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '889cf8a'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorE1Tests(unittest.TestCase):
    def test_only_two_source_reviewed_identity_corrections(self):
        review = read('data/entity-creator-e1-review-20261023.json')
        before, after = ({e['id']: e for e in data['entities']} for data in
                         [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {c['entityId'] for c in review['identityCorrections']} | {c['entityId'] for c in read('data/entity-creator-e2-review-20261024.json')['identityCorrections']})
        for correction in review['identityCorrections']:
            eid = correction['entityId']
            self.assertEqual((before[eid]['type'], before[eid]['verification']),
                             ('unknown', 'unresolved'))
            self.assertEqual((after[eid]['type'], after[eid]['verification']),
                             (correction['type'], 'sourceReviewed'))
            self.assertEqual((after[eid]['aliases'], after[eid]['dates']),
                             (before[eid]['aliases'], before[eid]['dates']))
        self.assertEqual((after['entity-name-fb6db91d6827']['type'],
                          after['entity-name-fb6db91d6827']['verification']),
                         ('unknown', 'unresolved'))
        self.assertEqual(after['entity-name-f9dfce1ab0f0'], before['entity-name-f9dfce1ab0f0'])
        self.assertTrue(review['identityCorrections'][1]['preserveReleaseRoles'])
        self.assertEqual(review['creditAdditions'], [])

    def test_progress_and_unchanged_creative_scope(self):
        current, before = read('data/organizations.json'), old('data/organizations.json')
        progress = current['registrationProgress']
        review = read('data/entity-creator-e1-review-20261023.json')
        self.assertEqual((progress['letter'], progress['letterProcessed'], progress['letterTotal'],
                          len(progress['processedEntityIds']), progress['total']), ('E', 8, 13, 78, 83))
        self.assertEqual(progress['processedEntityIds'][70:74], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextName'], 'Electronic Arts')
        self.assertEqual(progress['nextName'], 'Enterbrain（エンターブレイン）')
        self.assertEqual(current['works'], before['works'])
        old_nodes = {n['id']: n for n in before['nodes']}
        nodes = {n['id']: n for n in current['nodes']}
        for eid in review['progress']['processedEntityIds']:
            self.assertEqual(nodes[eid]['groups'], old_nodes[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], 0)
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
