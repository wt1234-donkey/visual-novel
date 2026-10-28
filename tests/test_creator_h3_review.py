"""H3 closes H with four scoped production records and intact legacy roles."""
from audit_baselines import requires_baseline
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = '1b17dbd'


def read(path):
    return load_snapshot(ROOT, path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


@requires_baseline(ROOT, BASE)
class CreatorH3Tests(unittest.TestCase):
    def test_four_work_roles_do_not_rewrite_historical_release_or_identity(self):
        review = read('data/entity-creator-h3-review-20261024.json')
        self.assertEqual(review['identityCorrections'], [])
        self.assertEqual(old('data/entities.json'), read('data/entities.json'))
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-4], before['credits'])
        self.assertEqual([(c['reviewId'], c['entityId'], c['workId'], c['role'], c['source'])
                          for c in after['credits'][-4:]],
                         [(c['reviewId'], c['entityId'], c['workId'], c['role'], c['source'])
                          for c in review['creditAdditions']])
        self.assertTrue(all(c['targetType'] == 'work' and c['reviewRecord'] == review['audit']
                            for c in after['credits'][-4:]))
        b = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        a = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(b.keys(), a.keys())
        self.assertEqual({key for key in a if a[key] != b[key]},
                         {('hummingbird_soft', w) for w in ['g101', 'g102', 'g105']})
        pending = {m['workId'] for m in after['dossierMemberships']
                   if m['dossierId'] == 'hummingbird_soft' and m['status'] == 'pendingRole'}
        self.assertEqual(len(pending), 8)
        self.assertEqual({m['workId'] for m in after['dossierMemberships']
                          if m['dossierId'] == 'hudson' and m['status'] == 'pendingRole'},
                         {'g1167', 'hudson-dezeni-world', 'hudson-orientalblue'})

    def test_completed_h_order_and_main_database(self):
        review = read('data/entity-creator-h3-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId'], p['nextName']),
                         ('H', 12, 12, 119, 119, 'entity-ibm', 'IBM'))
        self.assertEqual(p['processedEntityIds'][117:119],
                         [x['entityId'] for x in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes['entity-hummingbird_soft']['productionCount'], 3)
        self.assertEqual(nodes['entity-hunex']['productionCount'], 1)
        self.assertEqual({r['workId'] for r in nodes['entity-hummingbird_soft']['groups']['pending']},
                         {m['workId'] for m in read('data/credits.json')['dossierMemberships']
                          if m['dossierId'] == 'hummingbird_soft' and m['status'] == 'pendingRole'})
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(catalogue_bytes(ROOT, path),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
