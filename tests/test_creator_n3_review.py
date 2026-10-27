"""N3 separates historical dossiers, legal identities and collaborative creation."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '0f11656ae351157201405e6e4573eb9509274962'
BASE = '60d1236d386698056b473f3939fc059080347f2d'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT))
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorN3Tests(unittest.TestCase):
    def test_four_companies_preserve_separate_signatures_and_history_dossier(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {'entity-name-c9d832d41604', 'entity-name-0bee31ac676c',
                    'entity-name-bb40df899e7f', 'entity-name-198d8c1fcfbe'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({eid for eid in be if be[eid] != ae[eid]}, expected)
        for eid in expected:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(ae['entity-falcom'], be['entity-falcom'])
        self.assertEqual(ae['entity-name-417356621ac7'], be['entity-name-417356621ac7'])
        self.assertEqual(after['relations'], before['relations'])
        self.assertEqual(after['dossiers'], before['dossiers'])

    def test_five_scoped_credits_preserve_all_old_credits(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-5], before['credits'])
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in after['credits'][-5:]], [
            ('entity-falcom', 'ascii-dragon-slayer', 'originalProduction'),
            ('entity-falcom', 'falcom-romancia', 'originalProduction'),
            ('entity-name-0bee31ac676c', 'g1058', 'originalProduction'),
            ('entity-name-bb40df899e7f', 'g1209', 'coDeveloper'),
            ('entity-name-bb40df899e7f', 'square-mario-rpg', 'coDeveloper')])
        self.assertTrue(all(c['targetType'] == 'work' and c['status'] == 'sourceReviewed'
                            for c in after['credits'][-5:]))
        self.assertFalse(any(c['entityId'] in {'entity-name-c9d832d41604', 'entity-name-198d8c1fcfbe'}
                             for c in after['credits'][-5:]))

    def test_only_romancia_own_group_changes_without_inheriting_partner_credits(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, {('falcom', 'falcom-romancia')})
        key = ('falcom', 'falcom-romancia')
        expected = {**bm[key], 'roles': ['originalProduction', 'publisher'], 'group': 'original'}
        self.assertEqual(am[key], expected)
        for dossier, wid in [('ascii', 'ascii-dragon-slayer'), ('square', 'g1209'),
                             ('square', 'square-mario-rpg'), ('koei', 'g1058'), ('falcom', 'g1086')]:
            self.assertEqual(am[dossier, wid]['status'], 'pendingRole')
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 605)

    def test_progress_and_protected_catalogue(self):
        org = read('data/organizations.json')
        p = org['registrationProgress']
        previous = old('data/organizations.json')
        review = read('data/entity-creator-n3-review-20261025.json')
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('N', 15, 21, 208, 214, 'entity-nitrochiral'))
        self.assertEqual(p['processedEntityIds'][:203], previous['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 15 + ['pending'] * 6)
        self.assertEqual(org['works'], previous['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
