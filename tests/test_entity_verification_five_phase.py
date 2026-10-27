"""The completed review must preserve old data and make every gap explicit."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
TREE = '025762765317e2e71b1889fb4f95e164d8588b75'
FIVE_PHASE_TREE = '8a520a639b38bd38b8eb11aae16fdb2dd6eb201d'


def read(path):
    if path in {"data/entities.json", "data/organizations.json"}:
        return json.loads(subprocess.check_output(["git", "show", f"{FIVE_PHASE_TREE}:{path}"], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def prior(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{TREE}:{path}'], cwd=ROOT))


class FivePhaseReviewTests(unittest.TestCase):
    def test_claims_have_separate_decisions_and_originals_are_preserved(self):
        audit = read('data/entity-verification-five-phase-audit-20261026.json')
        decisions = audit['decisions']
        self.assertEqual(len(decisions), len({d['claimId'] for d in decisions}))
        self.assertEqual(audit['counts'], {'deferred': 653, 'confirmed': 3})
        self.assertEqual(sum(d['claimId'].startswith('role:') for d in decisions), 601)
        self.assertTrue(all(d['missingEvidence'] and not d['evidenceIds']
                            for d in decisions if d['decision'] == 'deferred'))
        self.assertEqual([p['phase'] for p in audit['phaseResults']], ['P1', 'P2', 'P3', 'P4', 'P5'])
        five_phase_credits = json.loads(subprocess.check_output(
            ['git', 'show', f'{FIVE_PHASE_TREE}:data/credits.json'], cwd=ROOT))
        self.assertEqual(five_phase_credits, prior('data/credits.json'))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), prior(path))

    def test_only_three_identities_change_and_review_progress_is_ordered(self):
        correction = read('data/entity-verification-five-phase-review-20261026.json')['identityCorrections']
        before = {e['id']: e for e in prior('data/entities.json')['entities']}
        after = {e['id']: e for e in read('data/entities.json')['entities']}
        self.assertEqual({eid for eid in after if after[eid] != before[eid]},
                         {r['entityId'] for r in correction})
        self.assertEqual([r['type'] for r in correction], ['company', 'company', 'brand'])
        progress = read('data/organizations.json')['recheckProgress']
        self.assertEqual(progress['processedEntityIds'],
                         [x['entityId'] for x in progress['baselineQueue']])
        self.assertIsNone(progress['nextEntityId'])
        self.assertEqual(progress['total'], 39)


if __name__ == '__main__':
    unittest.main()
