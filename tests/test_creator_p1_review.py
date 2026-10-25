"""P1 distinguishes a related production brand from company publishing identities."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '155fac06ae47a7e20f2c5a3cf3bae0d3c75d3016'
COMPANIES = {'entity-name-906fa9d6b292', 'entity-name-db9995981277',
             'entity-name-84c58ec33dac', 'entity-name-fb8b690c85a0'}


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorP1Tests(unittest.TestCase):
    def test_four_companies_preserve_names_relations_and_distinct_pony_nodes(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, COMPANIES)
        for eid in COMPANIES:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(ae['entity-name-e8f2daf6c0f9'], be['entity-name-e8f2daf6c0f9'])
        self.assertEqual(ae['entity-name-e8f2daf6c0f9']['verification'], 'unresolved')
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])

    def test_one_related_brand_addition_keeps_eighteen_existing_productions_and_publishers(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-1], before['credits'])
        c = after['credits'][-1]
        self.assertEqual((c['entityId'], c['workId'], c['targetType'], c['role'], c['rawCredit'], c['status']),
                         ('entity-palette', 'palette-extra-honey', 'work', 'productionBrand', 'ぱれっと', 'sourceReviewed'))
        productions = [c for c in after['credits'] if c['entityId'] == 'entity-palette' and c['role'] == 'productionBrand']
        self.assertEqual(len(productions), 19)
        self.assertEqual({c['workId'] for c in productions if c['status'] == 'existingDossier'},
                         {f'g{i}' for i in range(423, 441)})
        self.assertEqual(len(after['credits']), 4957)
        scoped = [c for c in after['credits'] if c['entityId'] in COMPANIES]
        self.assertEqual(len(scoped), 10)
        self.assertTrue(all(c['targetType'] == 'release' and c['role'] == 'publisher' for c in scoped))

    def test_only_honey_membership_gains_production_stays_related_with_old_source(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']}
                  for d in [before, after]]
        key = ('palette', 'palette-extra-honey')
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, {key})
        self.assertEqual(am[key], {**bm[key], 'roles': ['originalPublishingBrand', 'productionBrand', 'publishingBrand'],
                                  'group': 'original'})
        self.assertEqual((am[key]['placement'], am[key]['status']), ('related', 'existingEvidence'))
        self.assertEqual(len(am), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 604)

    def test_first_five_p_entities_are_ordered_and_core_catalogue_is_unchanged(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        expected = ['entity-palette', 'entity-name-906fa9d6b292', 'entity-name-db9995981277',
                    'entity-name-84c58ec33dac', 'entity-name-fb8b690c85a0']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']),
                         ('P', 5, 13, 223, 231, 'entity-name-e8f2daf6c0f9'))
        self.assertEqual(p['processedEntityIds'][:-5], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-5:], expected)
        review = read('data/entity-creator-p1-review-20261025.json')
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 5 + ['pending'] * 8)
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual(nodes['entity-palette']['productionCount'], 18)
        self.assertEqual(after['works'], before['works'])
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
