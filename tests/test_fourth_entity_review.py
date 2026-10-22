"""Fourth batch preserves raw history and keeps sourced parser books outside main."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd5a778252b49b0b2b1de19de775692cbcd0f548a'
APPLIED = 'd8f37e90abf47af94e9285167a26b6865497e332'


def read(path):
    return json.loads((ROOT / path).read_text())


def before(path, revision=BASE):
    return json.loads(subprocess.check_output(
        ['git', 'show', f'{revision}:{path}'], cwd=ROOT, text=True))


class FourthEntityReviewTests(unittest.TestCase):
    def test_only_four_identity_types_change_without_altering_relations(self):
        old_model, model = before('data/entities.json'), before('data/entities.json', APPLIED)
        self.assertEqual(old_model['relations'], model['relations'])
        self.assertEqual(old_model['dossiers'], model['dossiers'])
        old = {x['id']: x for x in old_model['entities']}
        new = {x['id']: x for x in model['entities']}
        self.assertEqual(old.keys(), new.keys())
        expected = {'entity-name-f9e8ee919b2e', 'entity-name-f00bc453a063',
                    'entity-name-40ed6431d1a6', 'entity-name-f9dfce1ab0f0'}
        self.assertEqual({eid for eid in old if old[eid] != new[eid]}, expected)
        for eid in expected:
            self.assertEqual(new[eid]['type'], 'company')
            self.assertEqual(new[eid]['verification'], 'sourceReviewed')
            for field in old[eid].keys() - {'type', 'verification', 'sources', 'historyNote'}:
                self.assertEqual(old[eid][field], new[eid][field], (eid, field))
            self.assertTrue(set(old[eid]['sources']) <= set(new[eid]['sources']))
        self.assertEqual(new['entity-name-61e191a86b41']['verification'], 'unresolved')

    def test_only_two_book_credits_and_two_memberships_change(self):
        old_data, data = before('data/credits.json'), before('data/credits.json', APPLIED)
        old = {x['id']: x for x in old_data['credits']}
        new = {x['id']: x for x in data['credits']}
        self.assertTrue(old.keys() <= new.keys())
        for cid in old:
            self.assertEqual(old[cid], new[cid], cid)
        added = [new[cid] for cid in new.keys() - old.keys()]
        works = {'microcabin-diamond', 'microcabin-dream'}
        self.assertEqual(len(added), 2)
        self.assertEqual({(x['entityId'], x['workId'], x['role']) for x in added},
                         {('entity-microcabin', wid, 'originalProduction') for wid in works})
        for x in added:
            self.assertEqual(x['targetType'], 'work')
            self.assertEqual(x['status'], 'sourceReviewed')
            self.assertEqual(x['reviewRecord'], 'data/entity-fourth-review-20261022.md')
            self.assertTrue((ROOT / x['reviewRecord']).is_file())
        key = lambda x: (x['dossierId'], x['workId'])
        old_m = {key(x): x for x in old_data['dossierMemberships']}
        new_m = {key(x): x for x in data['dossierMemberships']}
        self.assertEqual(old_m.keys(), new_m.keys())
        self.assertEqual({k for k in new_m if new_m[k] != old_m[k]},
                         {('microcabin', wid) for wid in works})
        for k in new_m:
            self.assertEqual(old_m[k]['placement'], new_m[k]['placement'])
        for wid in works:
            self.assertEqual(new_m[('microcabin', wid)]['placement'], 'bibliography')
            self.assertEqual(new_m[('microcabin', wid)]['group'], 'original')
        self.assertEqual(len(new), 4755)
        self.assertEqual(len(new_m), 2234)
        review = before('data/entity-migration-review.json', APPLIED)
        self.assertEqual(len(review['pendingIdentities']), 183)
        self.assertEqual(review['pendingMembershipCount'], 611)

    def test_no_core_baseline_or_prior_evidence_is_rewritten(self):
        paths = ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                 'data/gameplay-catalogues.json', 'data/work-classification.json',
                 'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']
        paths += [f'data/entity-{batch}-review-20261022.{ext}'
                  for batch in ['priority', 'followup', 'third'] for ext in ['json', 'md']]
        for path in paths:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(
                ['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

    def test_book_cards_explain_source_without_becoming_main_works(self):
        page = (ROOT / 'microcabin.html').read_text()
        main = read('data/games.json')
        for wid, rid in [('microcabin-diamond', 'Q5'), ('microcabin-dream', 'Q6')]:
            self.assertNotIn(wid, {x['id'] for x in main['works']})
            self.assertFalse(any(x['workId'] == wid for x in main['contentVersions']))
            self.assertFalse(any(x['workId'] == wid for x in main['platformReleases']))
            start = page.index(f'id="{wid}"')
            wrapper = page[page.rfind('<div class="dossier-card-wrapper"', 0, start):start]
            card = page[start:page.index('</article>', start)]
            self.assertIn('data-placement="bibliography"', wrapper)
            self.assertIn('data-relation="original"', wrapper)
            self.assertIn('仅专题书目', card)
            self.assertIn(f'核查记录 {rid}', card)
            self.assertIn('entity-fourth-review-20261022.md', card)


if __name__ == '__main__':
    unittest.main()
