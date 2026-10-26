"""S11 separates localized releases from original creation and completes S."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_entity_model as builder
BASE = '8f186829271a10bbd50a23740836523a8152501f'
REVIEW = 'data/entity-creator-s11-review-20261026.json'
IDS = ['entity-name-b1b599d0fabf', 'entity-name-389c2f591e55']


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS11Tests(unittest.TestCase):
    def test_unresolved_identities_dates_and_relationships_remain_exact(self):
        self.assertEqual(read('data/entities.json'), old('data/entities.json'))
        self.assertEqual(read('data/entity-migration-review.json'), old('data/entity-migration-review.json'))
        e = {e['id']: e for e in read('data/entities.json')['entities']}
        for eid in IDS:
            self.assertEqual((e[eid]['type'], e[eid]['verification']), ('unknown', 'unresolved'))
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in e.values()), 58)
        self.assertEqual(read(REVIEW)['identityCorrections'], [])

    def test_exact_release_localizer_and_original_creator_preserve_all_old_credits(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        self.assertEqual(len(after['credits']), 4999)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-2:]],
                         [(IDS[0], 'release', 'g855-v3', 'localizer'),
                          (IDS[1], 'work', 'ibm-yellow-brick-road', 'originalProduction')])
        for c in after['credits'][-2:]:
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        localized = [c for c in after['credits'] if c['entityId'] == IDS[0] and c['role'] != 'publisher']
        self.assertEqual(len(localized), 1)
        self.assertEqual((localized[0]['targetType'], localized[0]['targetId']), ('release', 'g855-v3'))
        self.assertEqual([c for c in after['credits'] if c['role'] == 'publisher'],
                         [c for c in before['credits'] if c['role'] == 'publisher'])
        model = read('data/organizations.json')
        node = next(n for n in model['nodes'] if n['id'] == IDS[0])
        self.assertEqual(node['groups']['creation'], [])
        self.assertEqual(node['productionCount'], 0)
        self.assertNotIn('localizer', model['creationRoles'])

    def test_memberships_and_all_original_catalogue_objects_stay_exact(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        m = next(m for m in after['dossierMemberships'] if m['dossierId'] == 'ibm'
                 and m['workId'] == 'ibm-yellow-brick-road')
        self.assertEqual(m['status'], 'pendingRole')
        self.assertEqual((len(after['dossierMemberships']), sum(m['status'] == 'pendingRole'
                          for m in after['dossierMemberships'])), (2234, 602))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_two_consecutive_entities_complete_s_and_advance_to_t_and_e_soft(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 42, 42, 279, 279, 'entity-te_soft'))
        self.assertEqual(p['nextName'], 'T&E SOFT')
        self.assertEqual(p['processedEntityIds'][:-2], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-2:], IDS)
        r = read(REVIEW)
        self.assertEqual([e['entityId'] for e in r['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 42)
        self.assertEqual(after['works'], before['works'])

    def test_localizer_rejects_wrong_release_work_scope_and_dossier_shortcuts(self):
        original_read = builder.read
        mutations = [dict(workId='g037'), dict(targetId='missing-release'),
                     dict(beforeTargetRoles=[]), dict(dossierId='laplacian'),
                     dict(targetType='work'), dict(targetType='content'), dict(role='publisher')]
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(read(REVIEW))
                review['creditAdditions'][0].update(mutation)
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
