"""E2 registers only two sourced identities and two original productions."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'be3d2a5'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorE2Tests(unittest.TestCase):
    def test_scoped_identity_and_work_additions(self):
        review = read('data/entity-creator-e2-review-20261024.json')
        before, after = ({e['id']: e for e in data['entities']} for data in
                         [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {x['entityId'] for x in review['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-e3-review-20261024.json')['identityCorrections']})
        for correction in review['identityCorrections']:
            b, a = before[correction['entityId']], after[correction['entityId']]
            self.assertEqual((b['type'], b['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a['type'], a['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((a['aliases'], a['dates']), (b['aliases'], b['dates']))
        b, a = ({c['id']: c for c in data['credits']} for data in
                [old('data/credits.json'), read('data/credits.json')])
        self.assertEqual({cid: a[cid] for cid in b}, b)
        added = [a[cid] for cid in a.keys() - b.keys()]
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in added},
                         {('entity-elf', 'g320', 'originalProduction'),
                          ('entity-enix', 'g984', 'originalProduction'), ('entity-name-49d0968e137f', 'nitroplus-extra-blasterz', 'coDeveloper')})
        self.assertEqual({(c['reviewId'], c['source']) for c in added},
                         {(c['reviewId'], c['source']) for batch in [review, read('data/entity-creator-e3-review-20261024.json')] for c in batch['creditAdditions']})
        self.assertTrue(all(c['targetType'] == 'work' and c['reviewRecord'] in {review['audit'], 'data/entity-creator-e3-review-20261024.md'} for c in added))
        self.assertEqual(old('data/entities.json')['relations'], read('data/entities.json')['relations'])

    def test_classification_and_baseline(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        review = read('data/entity-creator-e2-review-20261024.json')
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total']), ('E', 13, 13, 83, 83))
        self.assertEqual(p['processedEntityIds'][74:78], [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual(p['nextName'], 'F&C')
        self.assertEqual(after['works'], before['works'])
        nodes = {n['id']: n for n in after['nodes']}
        for eid, wid in [('entity-elf', 'g320'), ('entity-enix', 'g984')]:
            self.assertIn(wid, {r['workId'] for r in nodes[eid]['groups']['creation']})
        for eid in ['entity-name-328b53003a80', 'entity-name-bd6862a41912']:
            self.assertEqual(nodes[eid]['productionCount'], 0)
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
