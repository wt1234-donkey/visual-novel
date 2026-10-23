"""D3 registers only the sourced Broken Age original and DreamWorks identity."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '46f5c48'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorD3Tests(unittest.TestCase):
    def test_single_identity_and_original_credit(self):
        review = read('data/entity-creator-d3-review-20261023.json')
        b, a = ({e['id']: e for e in data['entities']} for data in
                [old('data/entities.json'), read('data/entities.json')])
        dream = 'entity-name-4c4c2f63075a'
        double = 'entity-name-f9e8ee919b2e'
        self.assertEqual({eid for eid in b if b[eid] != a[eid]}, {dream} | {c['entityId'] for batch in ['e1-review-20261023', 'e2-review-20261024'] for c in read(f'data/entity-creator-{batch}.json')['identityCorrections']})
        self.assertEqual((b[dream]['type'], b[dream]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((a[dream]['type'], a[dream]['verification']), ('company', 'sourceReviewed'))
        self.assertEqual((a[dream]['aliases'], a[dream]['dates']), (b[dream]['aliases'], b[dream]['dates']))
        self.assertEqual(a[double], b[double])
        before, after = old('data/credits.json'), read('data/credits.json')
        old_credits = {c['id']: c for c in before['credits']}
        new_credits = {c['id']: c for c in after['credits']}
        self.assertEqual({cid: new_credits[cid] for cid in old_credits}, old_credits)
        added = [new_credits[cid] for cid in new_credits.keys() - old_credits.keys()]
        self.assertEqual(len(added), 3)
        added = [c for c in added if c['reviewRecord'] == review['audit']]
        self.assertEqual(len(added), 1)
        self.assertEqual((added[0]['entityId'], added[0]['workId'], added[0]['targetType'],
                          added[0]['role'], added[0]['reviewRecord']),
                         (double, 'g978', 'work', 'originalProduction', review['audit']))
        self.assertEqual(added[0]['source'], review['creditAdditions'][0]['source'])
        self.assertEqual([m for m in after['dossierMemberships'] if (m['dossierId'], m['workId']) not in {('elf', 'g320'), ('enix', 'g984')}],
                         [m for m in before['dossierMemberships'] if (m['dossierId'], m['workId']) not in {('elf', 'g320'), ('enix', 'g984')}])

    def test_completion_without_backfilling_remasters(self):
        current, previous = read('data/organizations.json'), old('data/organizations.json')
        progress = current['registrationProgress']
        review = read('data/entity-creator-d3-review-20261023.json')
        self.assertEqual((progress['letter'], progress['letterProcessed'], progress['letterTotal'],
                          len(progress['processedEntityIds']), progress['total']), ('E', 8, 13, 78, 83))
        self.assertEqual(progress['processedEntityIds'][60:70], review['progress']['processedEntityIds'])
        self.assertEqual(review['progress']['nextName'], 'E3 Staff（イースリースタッフ）')
        self.assertEqual(current['works'], previous['works'])
        nodes = {n['id']: n for n in current['nodes']}
        old_nodes = {n['id']: n for n in previous['nodes']}
        double = 'entity-name-f9e8ee919b2e'
        self.assertEqual({w['workId'] for w in nodes[double]['groups']['creation']}, {'g978'})
        self.assertEqual({w['workId'] for w in nodes[double]['groups']['other']}, {'g975', 'g976', 'g977'})
        self.assertEqual(nodes['entity-name-4c4c2f63075a']['groups'],
                         old_nodes['entity-name-4c4c2f63075a']['groups'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/entity-creator-d2-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
