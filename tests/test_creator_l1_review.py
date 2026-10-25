"""L1 scopes five brand credits and one historical company category."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'cf0d917d25c2dd281c91b80df851130e63263e0d'
WORKS = {'g854', 'g855', 'g856', 'g860', 'g861'}


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorL1Tests(unittest.TestCase):
    def test_one_category_and_exact_five_brand_credits(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {'entity-name-7482e374b5bd'})
        self.assertEqual(ae['entity-name-7482e374b5bd']['type'], 'company')
        self.assertEqual(after['relations'], before['relations'])
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-5], before['credits'])
        additions = after['credits'][-5:]
        self.assertEqual({c['workId'] for c in additions}, WORKS)
        self.assertTrue(all((c['entityId'], c['targetType'], c['role'], c['status']) ==
                            ('entity-laplacian', 'work', 'productionBrand', 'sourceReviewed')
                            for c in additions))
        self.assertTrue(all(c['reviewRecord'] == 'data/entity-creator-l1-review-20261025.md'
                            for c in additions))

    def test_only_five_laplacian_memberships_change(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, {('laplacian', w) for w in WORKS})
        for wid in WORKS:
            self.assertEqual(am['laplacian', wid]['group'], 'original')
        for wid in ['g114', 'legend-uk-great-space-race']:
            self.assertEqual(am['legend_uk', wid]['status'], 'pendingRole')
        for wid in ['g857', 'g858', 'g859']:
            self.assertFalse(any(c['entityId'] == 'entity-laplacian' and c['workId'] == wid
                                 and c['role'] == 'productionBrand' for c in after['credits']))

    def test_alphabetic_progress_and_protected_catalogue(self):
        orgs = read('data/organizations.json')
        p = orgs['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('L', 5, 12, 156, 163, 'entity-name-547f933b0469'))
        review = read('data/entity-creator-l1-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 5 + ['pending'] * 7)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(orgs['works'], old('data/organizations.json')['works'])
