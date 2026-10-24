"""E3 completes E with two separately sourced identities and one related work credit."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'e63a3fd'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorE3Tests(unittest.TestCase):
    def test_only_recorded_entity_and_credit_changes(self):
        review = read('data/entity-creator-e3-review-20261024.json')
        prior, current = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in x['entities']} for x in (prior, current))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for x in review['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-f1-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-f2-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g1-review-20261024.json')['identityCorrections']})
        for x in review['identityCorrections']:
            eid = x['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        self.assertEqual(prior['relations'], current['relations'])
        for eid in ['entity-entergram', 'entity-name-b06c3e4e3ae1', 'entity-name-5f2bf730e86e']:
            self.assertEqual(b[eid], a[eid])
        before, after = old('data/credits.json'), read('data/credits.json')
        b, a = ({c['id']: c for c in x['credits']} for x in (before, after))
        self.assertEqual({cid: a[cid] for cid in b}, b)
        self.assertEqual(before['dossierMemberships'], after['dossierMemberships'])
        additions = [a[cid] for cid in a.keys() - b.keys()]
        self.assertEqual(len(additions), 2)
        c = next(x for x in additions if x["reviewRecord"] == review["audit"])
        self.assertEqual((c['entityId'], c['workId'], c['targetType'], c['role'], c['source'],
                          c['reviewId'], c['reviewRecord']),
                         ('entity-name-49d0968e137f', 'nitroplus-extra-blasterz', 'work',
                          'coDeveloper', review['creditAdditions'][0]['source'], 'AZE3-C01', review['audit']))

    def test_related_placement_and_progress(self):
        review = read('data/entity-creator-e3-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextName']),
                         ('G', 5, 13, 99, 107, 'General Products'))
        self.assertEqual(p['processedEntityIds'][78:83], [x['entityId'] for x in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        node = next(n for n in after['nodes'] if n['id'] == 'entity-name-49d0968e137f')
        self.assertEqual(node['productionCount'], 0)
        self.assertIn('nitroplus-extra-blasterz', {r['workId'] for r in node['groups']['creation']})
        self.assertEqual(after['works']['nitroplus-extra-blasterz']['placement'], 'related')
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
