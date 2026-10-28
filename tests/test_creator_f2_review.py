"""F2 completes F with five sourced identity corrections and no new creative credit."""
from audit_baselines import requires_baseline
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = '448276d'


def read(path):
    return load_snapshot(ROOT, path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


@requires_baseline(ROOT, BASE)
class CreatorF2Tests(unittest.TestCase):
    def test_only_separately_recorded_identity_changes(self):
        review = read('data/entity-creator-f2-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in d['entities']} for d in (before, after))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for x in review['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g1-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g2-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g3-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-h1-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-h2-review-20261024.json')['identityCorrections']})
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual([(x['rawName'], x['type']) for x in review['identityCorrections']],
                         [('Firebird', 'brand'), ('Fox Interactive', 'company'),
                          ('Fruitbat Factory', 'company'), ('FuRyu', 'company'),
                          ('フリュー', 'company')])
        for x in review['identityCorrections']:
            eid = x['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), (x['type'], 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
            self.assertTrue(x['sources'])
        self.assertTrue(review['identityCorrections'][0]['preserveReleaseRoles'])
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual([m for m in before['dossierMemberships'] if m['dossierId'] not in {'hulotte', 'hummingbird_soft'}],
                         [m for m in after['dossierMemberships'] if m['dossierId'] not in {'hulotte', 'hummingbird_soft'}])
        self.assertEqual(after['credits'][:-17], before['credits'])
        self.assertEqual(after['credits'][-17]['reviewRecord'], 'data/entity-creator-g1-review-20261024.md')
        self.assertEqual(after['credits'][-16]['reviewRecord'], 'data/entity-creator-g3-review-20261024.md')

    def test_release_scope_and_order(self):
        review = read('data/entity-creator-f2-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextName']),
                         ('H', 12, 12, 119, 119, 'IBM'))
        self.assertEqual(p['processedEntityIds'][88:94],
                         [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        old_nodes = {n['id']: n for n in before['nodes']}
        nodes = {n['id']: n for n in after['nodes']}
        for x in review['reviewedEntities']:
            eid = x['entityId']
            self.assertEqual(nodes[eid]['groups'], old_nodes[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], old_nodes[eid]['productionCount'])
        for eid in ['entity-name-9dbcd9638453', 'entity-name-00dfc4724ca6',
                    'entity-name-b5c18c410b18', 'entity-name-60381c8a73f3',
                    'entity-name-27ad495eb1bc']:
            self.assertEqual(nodes[eid]['productionCount'], 0)
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(catalogue_bytes(ROOT, path),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
