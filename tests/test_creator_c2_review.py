"""C2 assigns only historically scoped Chunsoft originals and Coktel identity."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '6dd8261'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class CreatorC2Tests(unittest.TestCase):
    def test_only_sourced_identity_and_work_credits(self):
        review = read('data/entity-creator-c2-review-20261023.json')
        before, after = ({e['id']: e for e in x['entities']} for x in [old('data/entities.json'), read('data/entities.json')])
        self.assertEqual({eid for eid in before if before[eid] != after[eid]},
                         {c['entityId'] for batch in [review, read('data/entity-creator-c3-review-20261023.json')]
                          for c in batch['identityCorrections']})
        coktel = 'entity-name-8c31b0298459'
        self.assertEqual((before[coktel]['type'], before[coktel]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((after[coktel]['type'], after[coktel]['verification']), ('company', 'sourceReviewed'))
        self.assertEqual(after[coktel]['aliases'], before[coktel]['aliases'])
        b, a = ({c['id']: c for c in x['credits']} for x in [old('data/credits.json'), read('data/credits.json')])
        self.assertEqual({cid: a[cid] for cid in b}, b)
        additions = [a[cid] for cid in a.keys() - b.keys()]
        self.assertEqual({(c['entityId'], c['workId'], c['role'], c['targetType']) for c in additions},
                         {('entity-name-21365baf366d', wid, 'originalProduction', 'work') for wid in ['g021', 'g022', 'g170']})
        self.assertEqual({c['reviewId'] for c in additions}, {c['reviewId'] for c in review['creditAdditions']})
        self.assertEqual(read('data/credits.json')['dossierMemberships'], old('data/credits.json')['dossierMemberships'])

    def test_progress_scopes_and_core_preservation(self):
        current, prior = read('data/organizations.json'), old('data/organizations.json')
        p = current['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']), p['total']),
                         ('C', 15, 18, 57, 60))
        self.assertEqual(read('data/entity-creator-c2-review-20261023.json')['progress']['nextEntityId'], 'entity-name-3e85e8c3e1f3')
        self.assertEqual(current['works'], prior['works'])
        nodes, previous = [{n['id']: n for n in x['nodes']} for x in [current, prior]]
        self.assertEqual({r['workId'] for r in nodes['entity-name-21365baf366d']['groups']['creation']},
                         {'g021', 'g022', 'g170'})
        for eid in ['entity-cinematronics', 'entity-clochette', 'entity-name-8c31b0298459', 'entity-comptiq']:
            self.assertEqual(nodes[eid]['groups'], previous[eid]['groups'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                     'data/entity-creator-c1-review-20261023.json']:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
