"""S1 keeps remaster development at content scope and related works outside main."""
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
BASE = 'e43530441600b96d854c2feb0567c5455c6a6746'
SAGA = 'entity-sagaplanets'
SCREAM = 'entity-name-d05eacc25c69'
SEGA = 'entity-sega'
REVIEW = 'data/entity-creator-s1-review-20261025.json'


def read(path):
    return json.loads((ROOT / path).read_text())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS1Tests(unittest.TestCase):
    def test_only_screaming_villains_company_identity_changes(self):
        before, after = old('data/entities.json'), read('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {SCREAM})
        self.assertEqual((be[SCREAM]['type'], be[SCREAM]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((ae[SCREAM]['type'], ae[SCREAM]['verification']), ('company', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[SCREAM].get(field), ae[SCREAM].get(field))
        for eid in [SAGA, SEGA]:
            self.assertEqual(be[eid], ae[eid])
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 74)

    def test_five_credits_preserve_old_records_and_limit_remaster_to_added_content(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-5], before['credits'])
        actual = [(c['entityId'], c['targetType'], c['targetId'], c['workId'], c['role'], c['status'])
                  for c in after['credits'][-5:]]
        self.assertEqual(actual, [
            (SAGA, 'work', 'sagaplanets-r01', 'sagaplanets-r01', 'productionBrand', 'sourceReviewed'),
            (SAGA, 'work', 'sagaplanets-r02', 'sagaplanets-r02', 'productionBrand', 'sourceReviewed'),
            (SCREAM, 'content', 'g934-c-2', 'g934', 'developer', 'sourceReviewed'),
            (SEGA, 'work', 'sega-roommania', 'sega-roommania', 'originalProduction', 'sourceReviewed'),
            (SEGA, 'work', 'sega-new-sakura', 'sega-new-sakura', 'originalProduction', 'sourceReviewed')])
        self.assertEqual(len(after['credits']), 4977)
        self.assertEqual(sum(c['entityId'] == SAGA and c['role'] == 'productionBrand' for c in after['credits']), 26)
        self.assertEqual(sum(c['entityId'] == SEGA and c['role'] == 'publisher' for c in after['credits']), 26)
        self.assertFalse(any(c['entityId'] == SCREAM and c['targetType'] == 'work' for c in after['credits']))
        scoped = [c for c in after['credits'] if c['entityId'] == SCREAM]
        self.assertEqual(len(scoped), 2)
        self.assertEqual([c['role'] for c in scoped], ['publisher', 'developer'])

    def test_four_related_membership_changes_preserve_pending_and_catalogue_objects(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']} for d in [before, after]]
        keys = {('sagaplanets', 'sagaplanets-r01'), ('sagaplanets', 'sagaplanets-r02'),
                ('sega', 'sega-roommania'), ('sega', 'sega-new-sakura')}
        self.assertEqual(bm.keys(), am.keys())
        self.assertEqual({k for k in bm if bm[k] != am[k]}, keys)
        for key in keys:
            role = 'productionBrand' if key[0] == 'sagaplanets' else 'originalProduction'
            self.assertEqual(am[key], {**bm[key], 'roles': sorted(bm[key]['roles'] + [role]), 'group': 'original'})
            self.assertEqual(am[key]['placement'], 'related')
        self.assertEqual(len(am), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in am.values()), 602)
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_s_order_and_next_seikaisha_do_not_promote_related_works(self):
        before, after = old('data/organizations.json'), read('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']), ('S', 3, 42, 240, 279, 'entity-name-7c9d766b5702'))
        self.assertEqual(p['processedEntityIds'][:-3], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-3:], [SAGA, SCREAM, SEGA])
        review = read(REVIEW)
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 3 + ['pending'] * 39)
        self.assertEqual([d['entityId'] for d in review['deferredReviews']], [SAGA, SCREAM, SEGA])
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual([nodes[e]['productionCount'] for e in [SAGA, SCREAM, SEGA]], [24, 1, 0])
        self.assertEqual(after['works'], before['works'])

    def test_content_review_rejects_originals_wrong_works_and_dossier_shortcuts(self):
        original_read = builder.read
        for mutation in [dict(targetId='g934-c-original'), dict(workId='g935'),
                         dict(dossierId='sega'), dict(beforeTargetRoles=['publisher'])]:
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(read(REVIEW))
                review['creditAdditions'][2].update(mutation)
                with patch.object(builder, 'read', side_effect=lambda path: review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
