"""M4 keeps publishing brands and parent dossiers separate from production."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '26e4b64b4faaae75f09aa2dfc512feb053b41ae2'
BASE = '8a0b1e68e43718f929cdc1d1e8f502766db86d14'


def read(path):
    if path in {"data/entities.json", "data/credits.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{SNAPSHOT}:{path}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorM4Tests(unittest.TestCase):
    def test_exact_three_subbrand_credits_without_rewriting_any_old_credit(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-3], before['credits'])
        additions = after['credits'][-3:]
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in additions],
                         [('entity-minato_carnival', w, 'productionBrand')
                          for w in ['g1258', 'g1260', 'g1262']])
        self.assertTrue(all(c['status'] == 'sourceReviewed' and c['targetType'] == 'work'
                            and c['rawCredit'] == 'みなとカーニバル' for c in additions))
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        for dossier in ['minatosoft', 'hawkeye']:
            for work in ['g1258', 'g1260', 'g1262']:
                membership = next(m for m in after['dossierMemberships']
                                  if (m['dossierId'], m['workId']) == (dossier, work))
                self.assertEqual(membership['status'], 'pendingRole')

    def test_identity_and_catalogue_stability_with_explicit_deferred_scope(self):
        for path in ['data/entities.json', 'data/games.json', 'data/company-coverage.json',
                     'data/taxonomy.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        review = read('data/entity-creator-m4-review-20261025.json')
        self.assertEqual(review['identityCorrections'], [])
        self.assertEqual(len(review['reviewedEntities']), 5)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']],
                         ['entity-microsoft', 'entity-microsoft_home', 'entity-microsoft_studios',
                          'entity-minato_carnival_world', 'entity-minato_carnival'])
        self.assertTrue(all(c['dossierId'] is None for c in review['creditAdditions']))
        world = review['reviewedEntities'][3]
        self.assertEqual(world['workIds'], [])
        self.assertIn('正文获取失败', world['reason'])
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_continuous_alphabetic_progress(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('M', 20, 30, 183, 193, 'entity-minatosoft'))
        review = read('data/entity-creator-m4-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 20 + ['pending'] * 10)
