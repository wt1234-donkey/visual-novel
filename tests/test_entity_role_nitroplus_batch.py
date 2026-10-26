"""Check that the larger dossier batch changes only its evidenced scopes."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE_TREE = '8a520a639b38bd38b8eb11aae16fdb2dd6eb201d'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def base(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE_TREE}:{path}'], cwd=ROOT))


class NitroplusRoleBatchTests(unittest.TestCase):
    def test_all_claims_have_decisions_and_only_supported_credits_are_added(self):
        audit = read('data/entity-role-nitroplus-audit-20261027.json')
        review = read('data/entity-role-nitroplus-review-20261027.json')
        self.assertEqual((audit['claimCount'], audit['counts']),
                         (72, {'confirmed': 11, 'deferred': 61}))
        self.assertEqual(len({d['claimId'] for d in audit['decisions']}), 72)
        self.assertEqual(len(review['creditAdditions']), 12)
        self.assertEqual({d['workId'] for d in audit['decisions'] if d['batchDecision'] == 'confirmed'},
                         {c['workId'] for c in review['creditAdditions'] if c['targetType'] == 'work'})
        self.assertTrue(all(d['source'] and d['sourceLocation'] and d['evidenceIds']
                            for d in audit['decisions'] if d['batchDecision'] == 'confirmed'))

        current = read('data/credits.json')
        before = base('data/credits.json')
        previous = {c['id']: c for c in before['credits']}
        additions = [c for c in current['credits'] if c['id'] not in previous]
        self.assertEqual(len(additions), 12)
        self.assertEqual({c['id']: c for c in current['credits'] if c['id'] in previous}, previous)
        self.assertEqual({c['reviewId'] for c in additions},
                         {a['reviewId'] for a in review['creditAdditions']})
        self.assertEqual([(c['targetType'], c['targetId'], c['role'])
                          for c in additions if c['targetType'] == 'release'],
                         [('release', 'g054-v2', 'developer')])

        old_members = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        new_members = {(m['dossierId'], m['workId']): m for m in current['dossierMemberships']}
        changed = {key for key in old_members if old_members[key] != new_members[key]}
        self.assertEqual(changed,
                         {('nitroplus', a['workId']) for a in review['creditAdditions']
                          if a['targetType'] == 'work'})
        self.assertTrue(all(old_members[k]['status'] == 'pendingRole' and
                            new_members[k]['status'] == 'existingEvidence' for k in changed))
        self.assertEqual(read('data/entity-migration-review.json')['pendingMembershipCount'], 590)

    def test_catalogue_and_historical_releases_are_preserved(self):
        for path in ('data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json'):
            self.assertEqual(read(path), base(path))


if __name__ == '__main__':
    unittest.main()
