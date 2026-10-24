"""F1 verifies two brand identities and keeps later-edition credits in scope."""
import json
import subprocess
import unittest
from pathlib import Path
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ebff3e6'


def read(path):
    return load_snapshot(ROOT, path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorF1Tests(unittest.TestCase):
    def test_sourced_identity_only_and_existing_release_roles(self):
        review = read('data/entity-creator-f1-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in data['entities']} for data in (before, after))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {x['entityId'] for x in review['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-f2-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g1-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g2-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-g3-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-h1-review-20261024.json')['identityCorrections']} | {x['entityId'] for x in read('data/entity-creator-h2-review-20261024.json')['identityCorrections']})
        self.assertEqual(before['relations'], after['relations'])
        for x in review['identityCorrections']:
            eid = x['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), ('brand', 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
            self.assertTrue(x['preserveReleaseRoles'])
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual([m for m in before['dossierMemberships'] if m['dossierId'] not in {'hulotte', 'hummingbird_soft'}],
                         [m for m in after['dossierMemberships'] if m['dossierId'] not in {'hulotte', 'hummingbird_soft'}])
        self.assertEqual(after['credits'][:-17], before['credits'])
        self.assertEqual(after['credits'][-17]['reviewRecord'], 'data/entity-creator-g1-review-20261024.md')
        self.assertEqual(after['credits'][-16]['reviewRecord'], 'data/entity-creator-g3-review-20261024.md')
        credits = read('data/credits.json')['credits']
        expected = {'entity-name-d8351a6222ea': {'g777-v5', 'g777-v6'},
                    'entity-name-4bbd70f3b821': {'g306-v6'}}
        for eid, release_ids in expected.items():
            entries = [c for c in credits if c['entityId'] == eid]
            self.assertEqual({c['targetId'] for c in entries}, release_ids)
            self.assertTrue(all(c['targetType'] == 'release' and c['role'] == 'publisher' for c in entries))

    def test_progress_and_content_boundaries(self):
        review = read('data/entity-creator-f1-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextName']),
                         ('H', 12, 12, 119, 119, 'IBM'))
        self.assertEqual(p['processedEntityIds'][83:88], [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        old_nodes, nodes = ({n['id']: n for n in data['nodes']} for data in (before, after))
        for eid in review['progress']['processedEntityIds']:
            self.assertEqual(nodes[eid]['groups'], old_nodes[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], old_nodes[eid]['productionCount'])
        self.assertEqual(nodes['entity-favorite']['productionCount'], 14)
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
