"""L2 changes categories without generating creative or release roles."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '2abb28f54941fb4a34418303ad0ed26302238026'
BASE = '3ba7861557bd5c59b7a0b2142c41b405343c5ca3'


def read(path):
    if path in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorL2Tests(unittest.TestCase):
    def test_exact_three_categories_and_unchanged_relations(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {'entity-name-547f933b0469': 'company',
                    'entity-name-8ce25297971d': 'company',
                    'entity-name-a2534654b05f': 'brand'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(expected))
        for eid, kind in expected.items():
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(be[eid][field], ae[eid][field])
        self.assertEqual(after['relations'], before['relations'])
        self.assertEqual(ae['entity-name-9ba14a4f9578'], be['entity-name-9ba14a4f9578'])

    def test_credit_index_unchanged_including_brand_publisher(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after, before)
        brand = [c for c in after['credits'] if c['entityId'] == 'entity-name-a2534654b05f']
        self.assertEqual([(c['role'], c['targetType'], c['rawCredit']) for c in brand],
                         [('publisher', 'release', 'ログインソフト')])
        review = read('data/entity-creator-l2-review-20261025.json')
        self.assertEqual(review['creditAdditions'], [])
        self.assertTrue(review['identityCorrections'][-1]['preserveReleaseRoles'])

    def test_progress_and_catalogue_preservation(self):
        orgs = read('data/organizations.json')
        p = orgs['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('L', 10, 12, 161, 163, 'entity-name-57509c825879'))
        review = read('data/entity-creator-l2-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 10 + ['pending'] * 2)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(orgs['works'], old('data/organizations.json')['works'])
