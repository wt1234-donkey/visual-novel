"""The evidence queue deduplicates retrieval without collapsing claims."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EntityVerificationPlanTests(unittest.TestCase):
    def test_all_claims_are_independent_and_phases_cover_them_once(self):
        queue = json.loads((ROOT / 'data/entity-verification-evidence-index-20261026.json').read_text())
        work_ids = [w['workId'] for w in queue['works']]
        self.assertEqual((len(work_ids), len(set(work_ids))), (618, 618))
        identity = [c for w in queue['works'] for c in w['identityClaims']]
        roles = [c for w in queue['works'] for c in w['roleClaims']]
        self.assertEqual((len(identity), len(roles)), (55, 601))
        self.assertEqual(len({c['claimId'] for c in identity + roles}), 656)
        self.assertEqual(len({c['entityId'] for c in identity}), 36)
        self.assertEqual(len({w['workId'] for w in queue['works'] if w['identityClaims'] and w['roleClaims']}), 21)
        self.assertEqual([len(p['newIdentityIds']) for p in queue['phases']], [6, 9, 8, 5, 6])
        self.assertEqual(sum(p['pendingRoleClaims'] for p in queue['phases']), 601)
        self.assertEqual(set(work_ids), {wid for p in queue['phases'] for wid in p['affectedWorkIds']})
        self.assertEqual({c['claimId'] for c in roles},
                         {f"role:{m['dossierId']}:{m['workId']}" for m in
                          json.loads(subprocess.check_output(['git', 'show',
                              queue['baselineTree'] + ':data/credits.json'], cwd=ROOT))['dossierMemberships']
                          if m['status'] == 'pendingRole'})

    def test_leads_are_not_evidence_and_release_scope_stays_explicit(self):
        queue = json.loads((ROOT / 'data/entity-verification-evidence-index-20261026.json').read_text())
        self.assertEqual(len(queue['sourceLedger']), 109)
        self.assertTrue(all(s['status'] == 'leadOnly' for s in queue['sourceLedger']))
        self.assertTrue(all(c['decision'] == 'unreviewed' for w in queue['works']
                            for c in w['identityClaims'] + w['roleClaims']))
        self.assertEqual(len([w for w in queue['works'] if not w['releaseContextIds']]), 126)
        self.assertTrue(all(w['placement'] == 'bibliography' for w in queue['works']
                            if not w['releaseContextIds']))
        mobile = next(w for w in queue['works'] if w['workId'] == 'g209')
        names = {c['name'] for c in mobile['identityClaims']}
        self.assertEqual(names, {'发行方待核实（GREE）', '发行方待核实（Mobage）'})
        self.assertEqual(len({c['claimId'] for c in mobile['identityClaims']}), 2)


if __name__ == '__main__':
    unittest.main()
