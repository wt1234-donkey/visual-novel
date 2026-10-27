"""A-dossier batch must keep parents, creators and historical releases distinct."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '99d54acbeda8976b27df552ecc0709718cc7b600'


def read(path):
    if path in {'data/credits.json','data/entity-migration-review.json'}:
        return json.loads(subprocess.check_output(['git','show',f'0f2d278e17d631b85ed7e34e7dd378a361ff4695:{path}'],cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class AdventureAliceBatchTests(unittest.TestCase):
    def test_frozen_claims_and_scoped_credits(self):
        audit = read('data/entity-role-adventure-alice-audit-20261027.json')
        review = read('data/entity-role-adventure-alice-review-20261027.json')
        self.assertEqual(audit['counts'], {'deferred': 110, 'confirmed': 1})
        self.assertEqual([sum(d['dossierId'] == key for d in audit['decisions'])
                          for key in audit['dossiers']], [36, 75])
        self.assertEqual(len({d['claimId'] for d in audit['decisions']}), 111)
        self.assertTrue(all(d['missingEvidence'] for d in audit['decisions']
                            if d['decision'] == 'deferred'))

        current = read('data/credits.json')
        before = old('data/credits.json')
        prior = {c['id']: c for c in before['credits']}
        self.assertEqual({c['id']: c for c in current['credits'] if c['id'] in prior}, prior)
        added = [c for c in current['credits'] if c['id'] not in prior]
        self.assertEqual(len(added), 7)
        self.assertEqual({c['reviewId'] for c in added},
                         {a['reviewId'] for a in review['creditAdditions']})
        self.assertEqual({c['entityId'] for c in added},
                         {'entity-alicesoft', 'entity-alice_blue', 'entity-alice_noir'})
        self.assertEqual([(c['workId'], c['role']) for c in added
                          if c['entityId'] == 'entity-alicesoft'],
                         [('alicesoft-extra-hentailabyrinth', 'coDeveloper')])
        self.assertTrue(all(c['role'] == 'productionBrand' and c['targetType'] == 'work'
                            for c in added if c['entityId'] != 'entity-alicesoft'))

        prior_members = {(x['dossierId'], x['workId']): x for x in before['dossierMemberships']}
        after_members = {(x['dossierId'], x['workId']): x for x in current['dossierMemberships']}
        self.assertEqual({key for key in prior_members if prior_members[key] != after_members[key]},
                         {('alicesoft', 'alicesoft-extra-hentailabyrinth')})
        self.assertEqual(after_members[('alicesoft', 'alicesoft-extra-hentailabyrinth')]['group'], 'cooperation')
        self.assertEqual(after_members[('alicesoft', 'g545')]['status'], 'pendingRole')
        self.assertEqual(after_members[('adventure_international', 'ai-death-planet')]['status'], 'pendingRole')
        self.assertEqual(read('data/entity-migration-review.json')['pendingMembershipCount'], 589)

    def test_original_catalogues_are_untouched(self):
        for path in ('data/games.json', 'data/company-coverage.json',
                     'data/entity-migration-baseline.json'):
            self.assertEqual(read(path), old(path))


if __name__ == '__main__':
    unittest.main()
