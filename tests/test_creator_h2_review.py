"""H2 adds only independently sourced HULOTTE brand production and two Human identities."""
from audit_baselines import requires_baseline
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from creator_snapshot import load_snapshot

ROOT = Path(__file__).resolve().parents[1]
BASE = '6bccaa7'


def read(path):
    return load_snapshot(ROOT, path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


@requires_baseline(ROOT, BASE)
class CreatorH2Tests(unittest.TestCase):
    def test_two_identity_corrections_preserve_distinct_publishers(self):
        review = read('data/entity-creator-h2-review-20261024.json')
        before, after = old('data/entities.json'), read('data/entities.json')
        b, a = ({e['id']: e for e in d['entities']} for d in (before, after))
        self.assertEqual({eid for eid in b if b[eid] != a[eid]},
                         {c['entityId'] for c in review['identityCorrections']})
        self.assertEqual(before['relations'], after['relations'])
        for c in review['identityCorrections']:
            eid = c['entityId']
            self.assertEqual((b[eid]['type'], b[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((a[eid]['type'], a[eid]['verification']), ('company', 'sourceReviewed'))
            self.assertEqual((a[eid]['aliases'], a[eid]['dates']), (b[eid]['aliases'], b[eid]['dates']))
        self.assertNotEqual(review['identityCorrections'][0]['entityId'], review['identityCorrections'][1]['entityId'])

    def test_exact_brand_work_additions_and_unresolved_hudson(self):
        review = read('data/entity-creator-h2-review-20261024.json')
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-15], before['credits'])
        self.assertEqual([(c['reviewId'], c['entityId'], c['workId'], c['role'], c['source'])
                          for c in after['credits'][-15:-4]],
                         [(c['reviewId'], c['entityId'], c['workId'], c['role'], c['source'])
                          for c in review['creditAdditions']])
        self.assertTrue(all(c['reviewRecord'] == review['audit'] and c['targetType'] == 'work'
                            for c in after['credits'][-15:-4]))
        old_members = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        members = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(old_members.keys(), members.keys())
        changed = {k for k in members if old_members[k] != members[k]}
        self.assertEqual(changed, {('hummingbird_soft', wid) for wid in ['g101', 'g102', 'g105']} |
                         {('hulotte', c['workId']) for c in review['creditAdditions']
                                   if c['entityId'] == 'entity-hulotte'})
        self.assertEqual(members['hulotte', 'g850'], old_members['hulotte', 'g850'])
        self.assertEqual(members['hulotte', 'g850']['status'], 'pendingRole')
        hudson = [m for m in after['dossierMemberships'] if m['dossierId'] == 'hudson' and m['status'] == 'pendingRole']
        self.assertEqual({m['workId'] for m in hudson}, {'hudson-dezeni-world', 'hudson-orientalblue', 'g1167'})
        for eid, wid in [('entity-name-53708cc2d758', 'g916-v2'),
                         ('entity-name-4f1d0851948b', 'g1015-v1')]:
            self.assertEqual([(c['targetId'], c['role']) for c in after['credits'] if c['entityId'] == eid],
                             [(wid, 'publisher')])

    def test_alphabetical_order_and_core_preservation(self):
        review = read('data/entity-creator-h2-review-20261024.json')
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId'], p['nextName']),
                         ('H', 12, 12, 119, 119, 'entity-ibm', 'IBM'))
        self.assertEqual(p['processedEntityIds'][112:117],
                         [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual(after['works'], before['works'])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual((nodes['entity-hulotte']['productionCount'],
                          nodes['entity-hulotte_roi']['productionCount']), (10, 1))
        self.assertEqual(nodes['entity-hudson']['productionCount'], 0)
        self.assertEqual({x['workId'] for x in nodes['entity-hulotte']['groups']['pending']}, {'g850'})
        for path in ['data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(catalogue_bytes(ROOT, path),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)


if __name__ == '__main__':
    unittest.main()
