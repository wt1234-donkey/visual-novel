"""Regression boundaries for the first sourced corrections, not a new migration baseline."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
REVIEW_BASE = 'f146070527470017120c08973ada0fca398c00ee'
REVIEW_APPLIED = 'ee0694de5dc51cc773bf9e76ae72a375da82211d'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def previous(path, revision=REVIEW_BASE):
    return json.loads(subprocess.check_output(
        ['git', 'show', f'{revision}:{path}'], cwd=ROOT, text=True))


class PriorityEntityReviewTests(unittest.TestCase):
    def test_historical_sources_baselines_and_identity_relationships_are_preserved(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/entity-migration-baseline.json',
                     'data/content-migration-baseline.json']:
            self.assertEqual(catalogue_bytes(ROOT, path), subprocess.check_output(
                ['git', 'show', f'{REVIEW_BASE}:{path}'], cwd=ROOT), path)
        before = previous('data/entities.json')
        after = previous('data/entities.json', REVIEW_APPLIED)
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        old = {e['id']: e for e in before['entities']}
        new = {e['id']: e for e in after['entities']}
        self.assertEqual(old.keys(), new.keys())
        changed = {eid for eid in old if old[eid] != new[eid]}
        self.assertEqual(changed, {'entity-name-8a871cf93bfd', 'entity-name-5caee77c6090'})
        for eid in changed:
            self.assertEqual(old[eid]['aliases'], new[eid]['aliases'])
            self.assertEqual(old[eid]['name'], new[eid]['name'])
            self.assertEqual(old[eid]['dates'], new[eid]['dates'])
            self.assertTrue(set(old[eid]['sources']) <= set(new[eid]['sources']))
        self.assertEqual(new['entity-name-8a871cf93bfd']['type'], 'company')
        self.assertEqual(new['entity-name-5caee77c6090']['type'], 'team')

    def test_only_four_scoped_contributions_are_added_and_four_memberships_resolved(self):
        before = previous('data/credits.json')
        after = previous('data/credits.json', REVIEW_APPLIED)
        old = {c['id']: c for c in before['credits']}
        new = {c['id']: c for c in after['credits']}
        self.assertTrue(old.keys() <= new.keys())
        for cid in old:
            self.assertEqual(old[cid], new[cid], cid)
        added = [new[cid] for cid in new.keys() - old.keys()]
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in added}, {
            ('entity-key', 'key-rpg-hbr', 'coDeveloper'),
            ('entity-august', 'august-rpg-imys', 'coDeveloper'),
            ('entity-minatosoft', 'g1251', 'originalProduction'),
            ('entity-minatosoft', 'minatosoft-climax', 'supervisor'),
        })
        self.assertEqual(len(added), 4)
        for credit in added:
            self.assertEqual(credit['targetType'], 'work')
            self.assertEqual(credit['status'], 'sourceReviewed')
            self.assertTrue((ROOT / credit['reviewRecord']).is_file())
            self.assertTrue(credit['note'])
        key = lambda m: (m['dossierId'], m['workId'])
        old_members = {key(m): m for m in before['dossierMemberships']}
        members = {key(m): m for m in after['dossierMemberships']}
        self.assertEqual(old_members.keys(), members.keys())
        self.assertEqual({k for k in members if members[k] != old_members[k]}, {
            ('key', 'key-rpg-hbr'), ('august', 'august-rpg-imys'),
            ('minatosoft', 'g1251'), ('minatosoft', 'minatosoft-climax'),
        })
        for k in members:
            self.assertEqual(old_members[k]['placement'], members[k]['placement'])
        self.assertEqual(members[('hawkeye', 'g1251')]['status'], 'pendingRole')
        self.assertEqual(members[('nitroplus', 'g622')]['status'], 'pendingRole')
        self.assertEqual(members[('alicesoft', 'g545')]['status'], 'pendingRole')
        self.assertEqual(previous('data/entity-migration-review.json', REVIEW_APPLIED)['pendingMembershipCount'], 616)
        self.assertEqual(len(previous('data/entity-migration-review.json', REVIEW_APPLIED)['pendingIdentities']), 197)

    def test_corrections_explain_their_scope_on_the_existing_dossier_cards(self):
        cases = [('key.html', 'key-rpg-hbr', 'cooperation', 'related', 'A3'),
                 ('august.html', 'august-rpg-imys', 'cooperation', 'related', 'A4'),
                 ('minatosoft.html', 'g1251', 'original', 'main', 'A5'),
                 ('minatosoft.html', 'minatosoft-climax', 'licensed', 'related', 'A6')]
        for path, wid, group, placement, review_id in cases:
            page = catalogue_bytes(ROOT, path).decode()
            start = page.index(f'id="{wid}"')
            wrapper = page[page.rfind('<div class="dossier-card-wrapper"', 0, start):start]
            card = page[start:page.index('</article>', start)]
            self.assertIn(f'data-relation="{group}"', wrapper)
            self.assertIn(f'data-placement="{placement}"', wrapper)
            self.assertIn(f'核查记录 {review_id}', card)
            self.assertIn('本轮来源核对', card)


if __name__ == '__main__':
    unittest.main()
