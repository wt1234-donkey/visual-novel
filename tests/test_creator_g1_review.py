"""G1 registers original Zeliard creation without moving a related work into the main catalogue."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '3d78a32'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorG1Tests(unittest.TestCase):
    def test_sourced_identity_changes_and_one_scoped_credit(self):
        review = read('data/entity-creator-g1-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in d['entities']} for d in (before, after))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for batch in [review, read('data/entity-creator-g2-review-20261024.json')]
                          for x in batch['identityCorrections']})
        self.assertEqual(before['relations'], after['relations'])
        for x in review['identityCorrections']:
            eid = x['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        old_credits, new_credits = old('data/credits.json'), read('data/credits.json')
        b, a = ({c['id']: c for c in d['credits']} for d in (old_credits, new_credits))
        self.assertEqual({cid: a[cid] for cid in b}, b)
        added = [a[cid] for cid in a.keys() - b.keys()]
        self.assertEqual(len(added), 1)
        c = added[0]
        self.assertEqual((c['entityId'], c['workId'], c['targetType'], c['role'],
                          c['source'], c['reviewId'], c['reviewRecord']),
                         ('entity-name-acf6175f07fb', 'sierra-on-line-zeliard',
                          'work', 'originalProduction', review['creditAdditions'][0]['source'],
                          'AZG1-C01', review['audit']))
        self.assertEqual(old_credits['dossierMemberships'], new_credits['dossierMemberships'])

    def test_order_and_original_database_preservation(self):
        review = read('data/entity-creator-g1-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextName']),
                         ('G', 10, 13, 104, 107, 'Good Smile Company'))
        self.assertEqual(p['processedEntityIds'][94:99],
                         [x['entityId'] for x in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes['entity-gainax']['productionCount'], 15)
        self.assertEqual(nodes['entity-gaina']['productionCount'], 0)
        game_arts = nodes['entity-name-acf6175f07fb']
        self.assertEqual(game_arts['productionCount'], 0)
        self.assertEqual([r['workId'] for r in game_arts['groups']['creation']],
                         ['sierra-on-line-zeliard'])
        self.assertEqual(after['works']['sierra-on-line-zeliard']['placement'], 'related')
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
