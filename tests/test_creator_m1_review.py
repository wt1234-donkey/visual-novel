"""M1 scopes two originals without inheriting parent dossier roles."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'a0d9a6fc5a282dc3c437c17b93479f82ff24890e'
MAGICAL = 'entity-name-1cc39c9db973'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorM1Tests(unittest.TestCase):
    def test_one_brand_category_without_changing_identity_or_relations(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {MAGICAL})
        self.assertEqual((ae[MAGICAL]['type'], ae[MAGICAL]['verification']), ('brand', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates']:
            self.assertEqual(be[MAGICAL][field], ae[MAGICAL][field])
        self.assertEqual(after['relations'], before['relations'])

    def test_exact_two_credits_and_unchanged_memberships_and_releases(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in after['credits'][-2:]],
                         [('entity-mages', 'g636', 'originalProduction'),
                          (MAGICAL, 'ascii-screamer', 'productionBrand')])
        self.assertTrue(all(c['status'] == 'sourceReviewed' and c['targetType'] == 'work'
                            for c in after['credits'][-2:]))
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])
        membership = next(m for m in after['dossierMemberships']
                          if (m['dossierId'], m['workId']) == ('ascii', 'ascii-screamer'))
        self.assertEqual((membership['placement'], membership['status']), ('related', 'pendingRole'))
        review = read('data/entity-creator-m1-review-20261025.json')
        self.assertTrue(review['identityCorrections'][0]['preserveReleaseRoles'])

    def test_alphabetic_progress_and_protected_catalogue(self):
        orgs = read('data/organizations.json')
        p = orgs['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('M', 5, 30, 168, 193, 'entity-name-85a1fd56da66'))
        review = read('data/entity-creator-m1-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 5 + ['pending'] * 25)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(orgs['works'], old('data/organizations.json')['works'])
