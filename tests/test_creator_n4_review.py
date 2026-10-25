"""N4 preserves historical brand scope and resolves only one corporate membership."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '0f11656ae351157201405e6e4573eb9509274962'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorN4Tests(unittest.TestCase):
    def test_one_brand_preserves_raw_signatures_and_separate_nitro_entities(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        eid = 'entity-name-d824aa40b8bf'
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({key for key in be if be[key] != ae[key]}, {eid})
        self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('brand', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates']:
            self.assertEqual(be[eid][field], ae[eid][field])
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        review = read('data/entity-creator-n4-review-20261025.json')
        self.assertIs(review['identityCorrections'][0]['preserveReleaseRoles'], True)

    def test_twelve_credits_leave_all_old_roles_and_later_content_boundaries_intact(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-12], before['credits'])
        expected = [('entity-nitrochiral', 'nitroplus-extra-rhythm-carnival', 'productionBrand'),
                    ('entity-nitroplus', 'nitroplus-extra-rusty-rabbit', 'originalProduction')]
        expected += [('entity-nitroplus_brand', wid, 'productionBrand') for wid in
                     ['g597', 'g598', 'g599', 'g600', 'g602', 'g603', 'g605', 'g606', 'g169', 'g616']]
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in after['credits'][-12:]], expected)
        self.assertTrue(all(c['targetType'] == 'work' and c['status'] == 'sourceReviewed'
                            for c in after['credits'][-12:]))
        self.assertFalse(any(c['entityId'] == 'entity-nitroorigin' for c in after['credits']))
        nova = [c for c in after['credits'] if c['entityId'] == 'entity-name-d824aa40b8bf']
        self.assertEqual(len(nova), 3)
        self.assertTrue(all(c['targetType'] == 'release' and c['role'] == 'publisher' for c in nova))
        chiral = [c for c in after['credits'] if c['entityId'] == 'entity-nitrochiral'
                  and c['role'] == 'productionBrand']
        self.assertEqual(len(chiral), 8)
        self.assertEqual(sum(c['workId'] in {f'g{i}' for i in range(622, 629)} for c in chiral), 7)

    def test_only_rusty_company_membership_resolves_without_inheriting_brand_credits(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        key = ('nitroplus', 'nitroplus-extra-rusty-rabbit')
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, {key})
        self.assertEqual(am[key], {**bm[key], 'roles': ['originalProduction'], 'group': 'original',
                                  'status': 'existingEvidence',
                                  'source': 'https://www.neteasegames.com/jp/news/20250417/37024_1228141.html'})
        self.assertEqual(am[key]['placement'], 'related')
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 604)
        corporate = [m for m in after['dossierMemberships'] if m['dossierId'] == 'nitroplus']
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in corporate), 72)
        for wid in ['g597', 'g169', 'g622', 'nitroplus-extra-rhythm-carnival']:
            self.assertEqual(am['nitroplus', wid]['status'], 'pendingRole')

    def test_alphabetic_progress_and_protected_catalogue(self):
        org, previous = read('data/organizations.json'), old('data/organizations.json')
        progress = org['registrationProgress']
        review = read('data/entity-creator-n4-review-20261025.json')
        self.assertEqual((progress['letter'], progress['letterProcessed'], progress['letterTotal'],
                          len(progress['processedEntityIds']), progress['total'], progress['nextEntityId']),
                         ('N', 20, 21, 213, 214, 'entity-novect'))
        self.assertEqual(progress['processedEntityIds'][:208], previous['registrationProgress']['processedEntityIds'])
        self.assertEqual(progress['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 20 + ['pending'])
        self.assertEqual(org['works'], previous['works'])
        nodes = {n['id']: n for n in org['nodes']}
        self.assertEqual(nodes['entity-nitroplus']['productionCount'], 0)
        self.assertEqual(nodes['entity-nitrochiral']['productionCount'], 7)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
