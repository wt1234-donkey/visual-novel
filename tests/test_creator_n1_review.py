"""N1 scopes original brands without inheriting cooperation or later names."""
import json
import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'f7ddbcc5de7eda9850b4433cf84dcdcb79d83f06'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorN1Tests(unittest.TestCase):
    def test_exact_three_companies_without_merging_nec_signatures(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {'entity-name-78226abfa58b', 'entity-name-0b22f68e63fb', 'entity-name-46fe3a3fcf5f'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, expected)
        for eid in expected:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates']:
                self.assertEqual(be[eid][field], ae[eid][field])
        self.assertEqual(ae['entity-name-ef0ae286070f'], be['entity-name-ef0ae286070f'])
        self.assertEqual(ae['entity-name-ef0ae286070f']['type'], 'unknown')
        self.assertEqual(ae['entity-nec_he'], be['entity-nec_he'])
        self.assertEqual(after['relations'], before['relations'])
        # Cross-dossier regeneration changes only the three reviewed type labels.
        for page in ['banpresto.html', 'elf.html', 'hokubu.html', 'jhv.html', 'taito.html']:
            previous = subprocess.check_output(['git', 'show', f'{BASE}:{page}'], cwd=ROOT, text=True)
            for eid in expected:
                previous = re.sub(
                    rf'(href="entities.html#{eid}">[^<]*<span class="entity-type">)身份待核(</span>)',
                    r'\g<1>公司／组织\g<2>', previous)
            self.assertEqual((ROOT / page).read_text(), previous, page)

    def test_ten_original_brand_credits_preserve_all_existing_participation(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-10], before['credits'])
        additions = after['credits'][-10:]
        self.assertEqual([(c['entityId'], c['workId'], c['role']) for c in additions],
                         [('entity-nanawind', f'g{i}', 'productionBrand') for i in range(885, 895)])
        self.assertTrue(all(c['targetType'] == 'work' and c['status'] == 'sourceReviewed'
                            and c['rawCredit'] == 'NanaWind' for c in additions))
        self.assertFalse({'g895', 'g896', 'g897', 'g898'} & {c['workId'] for c in additions})

    def test_only_own_ten_memberships_change_and_cooperation_remains_pending(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm = {(m['dossierId'], m['workId']): m for m in before['dossierMemberships']}
        am = {(m['dossierId'], m['workId']): m for m in after['dossierMemberships']}
        self.assertEqual(bm.keys(), am.keys())
        changed = {k for k in bm if bm[k] != am[k]}
        self.assertEqual(changed, {('nanawind', f'g{i}') for i in range(885, 895)})
        for key in bm:
            self.assertEqual(am[key]['placement'], bm[key]['placement'])
            self.assertEqual(am[key]['status'], bm[key]['status'])
        for key in changed:
            self.assertEqual((bm[key]['group'], am[key]['group']), ('release', 'original'))
        for work in ['g895', 'g896', 'g897', 'g898']:
            self.assertEqual(am['nanawind', work]['status'], 'pendingRole')
        self.assertEqual(am['nec_he', 'g918']['status'], 'pendingRole')

    def test_n_letter_transition_and_protected_catalogue(self):
        p = read('data/organizations.json')['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('N', 5, 21, 198, 214, 'entity-name-ef0ae286070f'))
        review = read('data/entity-creator-n1-review-20261025.json')
        self.assertEqual(p['processedEntityIds'][:193], old('data/organizations.json')['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        queue = review['progress']['queue']
        self.assertEqual([e['name'].lower() for e in queue], sorted(e['name'].lower() for e in queue))
        self.assertEqual([e['status'] for e in queue], ['reviewed'] * 5 + ['pending'] * 16)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(read('data/organizations.json')['works'], old('data/organizations.json')['works'])
