"""Exact delta for the third independent review, including retained prior batches."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'b9a5a7e7f10568e005c58bdc346e04b7e8cec399'
APPLIED = 'd5a778252b49b0b2b1de19de775692cbcd0f548a'


def read(path):
    return json.loads((ROOT / path).read_text())


def before(path, revision=BASE):
    return json.loads(subprocess.check_output(
        ['git', 'show', f'{revision}:{path}'], cwd=ROOT, text=True))


class ThirdEntityReviewTests(unittest.TestCase):
    def test_five_types_change_without_merging_names_or_relations(self):
        old_model, model = before('data/entities.json'), before('data/entities.json', APPLIED)
        self.assertEqual(old_model['relations'], model['relations'])
        self.assertEqual(old_model['dossiers'], model['dossiers'])
        old = {x['id']: x for x in old_model['entities']}
        new = {x['id']: x for x in model['entities']}
        self.assertEqual(old.keys(), new.keys())
        expected = {'entity-name-5c51b719b1bb', 'entity-name-06aeb9d01fbe',
                    'entity-name-7554e19bb041', 'entity-name-8a3d38d0d11f',
                    'entity-name-22015689e48e'}
        self.assertEqual({eid for eid in old if old[eid] != new[eid]}, expected)
        for eid in expected:
            self.assertEqual(new[eid]['type'], 'company')
            self.assertEqual(new[eid]['verification'], 'sourceReviewed')
            for field in old[eid].keys() - {'type', 'verification', 'sources', 'historyNote'}:
                self.assertEqual(old[eid][field], new[eid][field], (eid, field))
            self.assertTrue(set(old[eid]['sources']) <= set(new[eid]['sources']))

    def test_only_three_credits_and_one_scoped_membership_change(self):
        old_data, data = before('data/credits.json'), before('data/credits.json', APPLIED)
        old = {x['id']: x for x in old_data['credits']}
        new = {x['id']: x for x in data['credits']}
        self.assertTrue(old.keys() <= new.keys())
        for cid in old:
            self.assertEqual(old[cid], new[cid], cid)
        added = [new[cid] for cid in new.keys() - old.keys()]
        self.assertEqual(len(added), 3)
        self.assertEqual({(x['entityId'], x['workId'], x['role']) for x in added}, {
            ('entity-overdrive', 'g647', 'originalProduction'),
            ('entity-nitroplus_brand', 'g163', 'productionBrand'),
            ('entity-nitroplus_brand', 'g614', 'productionBrand')})
        for x in added:
            self.assertEqual(x['targetType'], 'work')
            self.assertEqual(x['status'], 'sourceReviewed')
            self.assertEqual(x['reviewRecord'], 'data/entity-third-review-20261022.md')
            self.assertTrue((ROOT / x['reviewRecord']).is_file())
        key = lambda x: (x['dossierId'], x['workId'])
        old_m = {key(x): x for x in old_data['dossierMemberships']}
        new_m = {key(x): x for x in data['dossierMemberships']}
        self.assertEqual(old_m.keys(), new_m.keys())
        self.assertEqual({k for k in new_m if new_m[k] != old_m[k]}, {('overdrive', 'g647')})
        for k in new_m:
            self.assertEqual(old_m[k]['placement'], new_m[k]['placement'])
        for wid in ['g163', 'g614', 'g622']:
            self.assertEqual(new_m[('nitroplus', wid)]['status'], 'pendingRole')
        self.assertEqual(new_m[('overdrive', 'g647')]['group'], 'original')
        self.assertEqual(len(new), 4753)
        self.assertEqual(len(new_m), 2234)
        review = before('data/entity-migration-review.json', APPLIED)
        self.assertEqual(len(review['pendingIdentities']), 187)
        self.assertEqual(review['pendingMembershipCount'], 613)

    def test_core_catalogues_baselines_and_prior_evidence_remain_byte_identical(self):
        paths = ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                 'data/gameplay-catalogues.json', 'data/work-classification.json',
                 'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']
        paths += [f'data/entity-{batch}-review-20261022.{ext}'
                  for batch in ['priority', 'followup'] for ext in ['json', 'md']]
        for path in paths:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(
                ['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

    def test_cards_show_review_scope_without_promoting_the_company(self):
        for path, wid, rid, group in [('overdrive.html', 'g647', 'T6', 'original'),
                                       ('nitroplus.html', 'g163', 'T7', 'unresolved'),
                                       ('nitroplus.html', 'g614', 'T8', 'unresolved')]:
            page = subprocess.check_output(['git', 'show', f'{APPLIED}:{path}'], cwd=ROOT, text=True)
            start = page.index(f'id="{wid}"')
            wrapper = page[page.rfind('<div class="dossier-card-wrapper"', 0, start):start]
            card = page[start:page.index('</article>', start)]
            self.assertIn(f'data-relation="{group}"', wrapper)
            self.assertIn(f'核查记录 {rid}', card)
            self.assertIn('entity-third-review-20261022.md', card)


if __name__ == '__main__':
    unittest.main()
