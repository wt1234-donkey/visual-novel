"""L3 scopes seven originals and completes L without inheriting dossier roles."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = 'a0d9a6fc5a282dc3c437c17b93479f82ff24890e'
BASE = '2abb28f54941fb4a34418303ad0ed26302238026'
LUCAS = 'entity-name-57509c825879'
LUNA = 'entity-name-a548db0984af'


def read(path):
    if path in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorL3Tests(unittest.TestCase):
    def test_two_categories_and_no_new_identity_or_relation(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {LUCAS, LUNA})
        for eid, kind in [(LUCAS, 'company'), (LUNA, 'team')]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(be[eid][field], ae[eid][field])
        self.assertEqual(after['relations'], before['relations'])

    def test_seven_originals_preserve_all_releases_and_memberships(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-7], before['credits'])
        additions = after['credits'][-7:]
        self.assertEqual({(c['entityId'], c['workId']) for c in additions},
                         {(LUCAS, w) for w in ['g975', 'g976', 'g977']} |
                         {(LUNA, w) for w in ['g895', 'g896', 'g897', 'g898']})
        self.assertTrue(all((c['role'], c['targetType'], c['status']) ==
                            ('originalProduction', 'work', 'sourceReviewed') for c in additions))
        self.assertTrue(all(c['reviewRecord'] == 'data/entity-creator-l3-review-20261025.md'
                            for c in additions))
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])

    def test_complete_l_and_preserve_catalogue(self):
        orgs = read('data/organizations.json')
        p = orgs['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('L', 12, 12, 163, 163, 'entity-macadamia'))
        review = read('data/entity-creator-l3-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-2:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertTrue(all(e['status'] == 'reviewed' for e in queue))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(orgs['works'], old('data/organizations.json')['works'])
