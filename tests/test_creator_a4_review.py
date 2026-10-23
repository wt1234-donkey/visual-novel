"""A4 changes only sourced duties and ARIA's type, retaining historical scope."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f6f53b6faa6bc3ce2091e8cc67c782967fc2a303'

def read(path):
    return json.loads((ROOT / path).read_text())

def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True))

class CreatorA4ReviewTests(unittest.TestCase):
    def test_three_additions_preserve_every_old_credit_and_membership(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        b = {c['id']: c for c in before['credits']}
        a = {c['id']: c for c in after['credits']}
        self.assertTrue(b.keys() <= a.keys())
        for cid in b:
            self.assertEqual(a[cid], b[cid], cid)
        review = read('data/entity-creator-a4-review-20261023.json')
        added = [a[cid] for cid in a.keys() - b.keys() if a[cid].get('reviewRecord') == review['audit']]
        expected = {('entity-aquaplus', 'g037', 'originalProduction'),
                    ('entity-aquaplus_brand', 'g037', 'productionBrand'),
                    ('entity-aquaplus_brand', 'g159', 'productionBrand')}
        self.assertEqual(len(added), 3)
        self.assertEqual({(c['entityId'], c['workId'], c['role']) for c in added}, expected)
        self.assertEqual({(c['entityId'], c['workId'], c['source']) for c in added},
                         {(c['entityId'], c['workId'], c['source']) for c in review['creditAdditions']})
        for c in added:
            self.assertEqual(c['targetType'], 'work')
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], review['audit'])
        after_members = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        for member in before['dossierMemberships']:
            if member['dossierId'] == 'ascii' and member['workId'] in {'g1003', 'g1004', 'ascii-chaos-angels'}:
                continue
            self.assertEqual(after_members[(member['dossierId'], member['workId'])], member)

    def test_only_aria_type_changes_without_automatic_release_roles_or_relationships(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        b = {e['id']: e for e in before['entities']}
        a = {e['id']: e for e in after['entities']}
        aria = 'entity-name-5ba1ee4df514'
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual(a.keys(), b.keys())
        self.assertEqual(a[aria]['type'], 'brand')
        self.assertEqual(a[aria]['verification'], 'sourceReviewed')
        for field in ['id', 'name', 'aliases', 'dates']:
            self.assertEqual(a[aria][field], b[aria][field])
        for field in ['relations', 'dossiers']:
            self.assertEqual(before[field], after[field])
        before, after = old('data/entity-migration-review.json'), read('data/entity-migration-review.json')
        self.assertNotIn(aria, {e['entityId'] for e in after['pendingIdentities']})
        self.assertEqual(after['pendingMembershipCount'], 611)
        for field in before.keys() - {'pendingIdentities'}:
            self.assertEqual(before[field], after[field])

    def test_core_baselines_main_page_old_reviews_and_placement_unchanged(self):
        paths = ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                 'data/gameplay-catalogues.json', 'data/work-classification.json',
                 'data/entity-migration-baseline.json', 'data/content-migration-baseline.json',
                 'index.html', 'app.mjs', 'filter.mjs', 'styles.css']
        paths += [f'data/entity-{batch}-review-20261022.{ext}'
                  for batch in ['priority', 'followup', 'third', 'fourth', 'creator-a', 'creator-a2', 'creator-a3']
                  for ext in ['json', 'md']]
        for path in paths:
            self.assertEqual((ROOT / path).read_bytes(),
                             subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT), path)

    def test_contiguous_progress_and_no_parent_or_version_inheritance(self):
        org = read('data/organizations.json')
        progress = org['registrationProgress']
        self.assertEqual(progress['processedEntityIds'][:25], [q['entityId'] for q in progress['queue'][:25]])
        self.assertEqual([e['entityId'] for e in progress['reviewedEntities'][:25]], progress['processedEntityIds'][:25])
        self.assertEqual(progress['nextEntityId'], 'entity-august')
        self.assertEqual(len(progress['audits']), 5)
        ns = {n['id']: n for n in org['nodes']}
        old_ns = {n['id']: n for n in old('data/organizations.json')['nodes']}
        for eid in ['entity-leaf', 'entity-name-5ba1ee4df514', 'entity-name-7f11db7a66f2', 'entity-asaproject']:
            self.assertEqual(ns[eid]['groups'], old_ns[eid]['groups'])
        for eid, works in [('entity-aquaplus', {'g037'}), ('entity-aquaplus_brand', {'g037', 'g159'})]:
            self.assertEqual({w['workId'] for w in ns[eid]['groups']['creation']}, works)
            self.assertEqual(ns[eid]['productionCount'], len(works))
        self.assertEqual(ns['entity-asaproject']['productionCount'], 22)
        self.assertEqual(org['works'], old('data/organizations.json')['works'])
