"""Keep the second sourced batch additive and bounded to its reviewed objects."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'ee0694de5dc51cc773bf9e76ae72a375da82211d'


def read(path):
    return json.loads((ROOT / path).read_text())


def before(path):
    return json.loads(subprocess.check_output(
        ['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))


class FollowupEntityReviewTests(unittest.TestCase):
    def test_only_five_identity_types_change_and_relations_are_preserved(self):
        prior, current = before('data/entities.json'), read('data/entities.json')
        self.assertEqual(prior['relations'], current['relations'])
        self.assertEqual(prior['dossiers'], current['dossiers'])
        old = {e['id']: e for e in prior['entities']}
        new = {e['id']: e for e in current['entities']}
        expected = {'entity-name-85a1fd56da66': 'brand',
                    'entity-name-acccc0db4bce': 'company',
                    'entity-name-5b146b15540c': 'company',
                    'entity-name-959a8e1f98f6': 'company',
                    'entity-name-21365baf366d': 'company'}
        self.assertEqual(old.keys(), new.keys())
        self.assertEqual({eid for eid in old if old[eid] != new[eid]}, set(expected))
        for eid, kind in expected.items():
            self.assertEqual(new[eid]['type'], kind)
            self.assertEqual(new[eid]['verification'], 'sourceReviewed')
            for field in old[eid].keys() - {'type', 'verification', 'sources', 'historyNote'}:
                self.assertEqual(old[eid][field], new[eid][field], (eid, field))
            self.assertTrue(set(old[eid]['sources']) <= set(new[eid]['sources']))

    def test_three_credits_are_added_without_rewriting_publisher_or_parent_credits(self):
        prior, current = before('data/credits.json'), read('data/credits.json')
        old = {c['id']: c for c in prior['credits']}
        new = {c['id']: c for c in current['credits']}
        self.assertTrue(old.keys() <= new.keys())
        for cid, credit in old.items():
            self.assertEqual(credit, new[cid], cid)
        added = [new[cid] for cid in new.keys() - old.keys()]
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in added}, {
            ('entity-minatosoft', 'g1252', 'originalProduction'),
            ('entity-minatosoft', 'g1254', 'originalProduction'),
            ('entity-yuzusoft_sour', 'g232', 'productionBrand')})
        self.assertEqual(len(added), 3)
        for credit in added:
            self.assertEqual(credit['targetType'], 'work')
            self.assertEqual(credit['status'], 'sourceReviewed')
            self.assertEqual(credit['reviewRecord'], 'data/entity-followup-review-20261022.md')
            self.assertTrue((ROOT / credit['reviewRecord']).is_file())
        # A type correction must not silently generate historical publishing-brand roles.
        mg = [c for c in new.values() if c['entityId'] == 'entity-name-85a1fd56da66']
        self.assertEqual(len(mg), 24)
        self.assertEqual({c['role'] for c in mg}, {'publisher'})
        key = lambda m: (m['dossierId'], m['workId'])
        old_members = {key(m): m for m in prior['dossierMemberships']}
        members = {key(m): m for m in current['dossierMemberships']}
        self.assertEqual(old_members.keys(), members.keys())
        self.assertEqual({k for k in members if members[k] != old_members[k]},
                         {('minatosoft', 'g1252'), ('minatosoft', 'g1254')})
        for k in members:
            self.assertEqual(old_members[k]['placement'], members[k]['placement'])
        for k in [('hawkeye', 'g1252'), ('hawkeye', 'g1254'),
                  ('yuzusoft', 'g232'), ('alicesoft', 'g545')]:
            self.assertEqual(members[k]['status'], 'pendingRole', k)
        self.assertEqual(len(new), 4750)
        self.assertEqual(len(members), 2234)
        review = read('data/entity-migration-review.json')
        self.assertEqual(review['pendingMembershipCount'], 614)
        self.assertEqual(len(review['pendingIdentities']), 192)

    def test_original_catalogues_and_both_migration_baselines_stay_byte_identical(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json', 'data/work-classification.json',
                     'data/entity-priority-review-20261022.json',
                     'data/entity-priority-review-20261022.md']:
            self.assertEqual((ROOT / path).read_bytes(), subprocess.check_output(
                ['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

    def test_minato_cards_explain_separate_production_evidence(self):
        page = (ROOT / 'minatosoft.html').read_text()
        for wid, rid in [('g1252', 'F6'), ('g1254', 'F7')]:
            start = page.index(f'id="{wid}"')
            wrapper = page[page.rfind('<div class="dossier-card-wrapper"', 0, start):start]
            card = page[start:page.index('</article>', start)]
            self.assertIn('data-relation="original"', wrapper)
            self.assertIn('data-placement="main"', wrapper)
            self.assertIn(f'核查记录 {rid}', card)
            self.assertIn('entity-followup-review-20261022.md', card)


if __name__ == '__main__':
    unittest.main()
