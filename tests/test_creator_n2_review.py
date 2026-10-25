"""N2 keeps business divisions, historical companies and later versions distinct."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = '60d1236d386698056b473f3939fc059080347f2d'
BASE = '9f157ff14c5ed54a4eed7362d3ad46bc3c92c91c'


def read(path):
    if path in {'data/entities.json', 'data/credits.json', 'data/organizations.json'}:
        return json.loads(subprocess.check_output(['git', 'show', f'{SNAPSHOT}:{path}'], cwd=ROOT))
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorN2Tests(unittest.TestCase):
    def test_three_historical_companies_keep_names_and_unresolved_division(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be = {e['id']: e for e in before['entities']}
        ae = {e['id']: e for e in after['entities']}
        expected = {'entity-name-ef0ae286070f', 'entity-name-c4968cadbf3e', 'entity-name-417356621ac7'}
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({eid for eid in be if be[eid] != ae[eid]}, expected)
        for eid in expected:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        for eid in ['entity-name-95984e43e41f', 'entity-name-acccc0db4bce', 'entity-falcom',
                    'entity-name-46fe3a3fcf5f', 'entity-name-d7900289691e', 'entity-name-8447c5d78187']:
            self.assertEqual(be[eid], ae[eid])
        self.assertEqual(ae['entity-name-95984e43e41f']['type'], 'unknown')
        self.assertEqual(after['relations'], before['relations'])

    def test_two_scoped_productions_preserve_all_old_credits_and_memberships(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        self.assertEqual([(c['entityId'], c['workId'], c['role'], c['targetType'], c['status'])
                          for c in after['credits'][-2:]], [
            ('entity-name-95984e43e41f', 'nitroplus-extra-rusty-rabbit', 'originalProduction', 'work', 'sourceReviewed'),
            ('entity-name-417356621ac7', 'g1086', 'originalProduction', 'work', 'sourceReviewed')])
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        for dossier, wid in [('nitroplus', 'nitroplus-extra-rusty-rabbit'), ('falcom', 'g1086'), ('infocom', 'g1086')]:
            membership = next(m for m in after['dossierMemberships'] if (m['dossierId'], m['workId']) == (dossier, wid))
            self.assertEqual((membership['roles'], membership['status']), (['catalogueAssociation'], 'pendingRole'))
        self.assertFalse(any(c['role'] in ['originalProduction', 'productionBrand', 'coDeveloper', 'developer']
                             for c in after['credits'] if c['entityId'] in
                             {'entity-name-acccc0db4bce', 'entity-name-c4968cadbf3e', 'entity-name-ef0ae286070f'}))

    def test_related_production_does_not_admit_work_or_inherit_dossier_creation(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        self.assertEqual(after['works'], before['works'])
        nodes = {n['id']: n for n in after['nodes']}
        bn = {n['id']: n for n in before['nodes']}
        for eid in ['entity-nitroplus', 'entity-falcom', 'entity-infocom']:
            self.assertEqual(nodes[eid]['groups'], bn[eid]['groups'])
            self.assertEqual(nodes[eid]['productionCount'], bn[eid]['productionCount'])
        self.assertEqual([w['workId'] for w in nodes['entity-name-95984e43e41f']['groups']['creation']],
                         ['nitroplus-extra-rusty-rabbit'])
        self.assertEqual(nodes['entity-name-95984e43e41f']['productionCount'], 0)
        self.assertEqual(nodes['entity-name-417356621ac7']['productionCount'], 1)

    def test_alphabetic_progress_and_protected_source_catalogue(self):
        progress = read('data/organizations.json')['registrationProgress']
        before = old('data/organizations.json')['registrationProgress']
        review = read('data/entity-creator-n2-review-20261025.json')
        self.assertEqual((progress['letter'], progress['letterProcessed'], progress['letterTotal'],
                          len(progress['processedEntityIds']), progress['total'], progress['nextEntityId']),
                         ('N', 10, 21, 203, 214, 'entity-falcom'))
        self.assertEqual(progress['processedEntityIds'][:198], before['processedEntityIds'])
        self.assertEqual(progress['processedEntityIds'][-5:], [e['entityId'] for e in review['reviewedEntities']])
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 10 + ['pending'] * 11)
        self.assertEqual([q['name'].lower() for q in review['progress']['queue']],
                         sorted(q['name'].lower() for q in review['progress']['queue']))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
