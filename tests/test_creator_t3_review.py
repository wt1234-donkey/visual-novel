"""T3 separates a label, corporate production and technical development."""
import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import build_entity_model as builder
BASE = 'deafc7f5a6e551367b6d06012e6a7afc3337d920'
REVIEW = 'data/entity-creator-t3-review-20261026.json'
IDS = ['entity-tinmachine', 'entity-name-0b5ee01c0e65',
       'entity-toho', 'entity-name-9832231b6baa']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'700c5f0c055bd9be328bf7000dc6f004d9162d76:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorT3Tests(unittest.TestCase):
    def test_only_label_and_intermedia_identity_change_without_mergers_or_dates(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[1], IDS[3]})
        for eid, kind in [(IDS[1], 'brand'), (IDS[3], 'company')]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 52))

    def test_exact_one_production_preserves_all_credits_and_other_subjects(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-1], before['credits'])
        self.assertEqual(len(after['credits']), 5003)
        c = after['credits'][-1]
        self.assertEqual((c['entityId'], c['targetType'], c['targetId'], c['role']),
                         (IDS[2], 'work', 'toho-phanpara', 'originalProduction'))
        self.assertEqual(c['status'], 'sourceReviewed')
        self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])
        for eid in [IDS[0], IDS[1], IDS[3], 'entity-name-ccdf9b616bf6']:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid],
                             [c for c in before['credits'] if c['entityId'] == eid])
        label = [c for c in after['credits'] if c['entityId'] == IDS[1]]
        self.assertEqual(len(label), 2)
        self.assertTrue(all(c['role'] == 'publisher' for c in label))
        self.assertFalse(any(c['entityId'] == IDS[2] and c['role'] == 'developer' for c in after['credits']))

    def test_only_own_phantom_parade_membership_is_resolved_and_catalogue_is_preserved(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(len(before['dossierMemberships']), len(after['dossierMemberships']))
        diffs = [(b, a) for b, a in zip(before['dossierMemberships'], after['dossierMemberships']) if b != a]
        self.assertEqual(len(diffs), 1)
        b, a = diffs[0]
        self.assertEqual((b['dossierId'], b['workId'], b['roles'], b['group'], b['status']),
                         ('toho', 'toho-phanpara', ['catalogueAssociation'], 'unresolved', 'pendingRole'))
        self.assertEqual(a, {**b, 'roles': ['originalProduction'], 'group': 'original',
                            'status': 'existingEvidence', 'source': read(REVIEW)['creditAdditions'][0]['source']})
        self.assertEqual((len(after['dossierMemberships']), sum(m['status'] == 'pendingRole'
                          for m in after['dossierMemberships'])), (2234, 601))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_four_consecutive_entities_advance_t_to_tokuma_parent(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('T', 12, 19, 291, 298, 'entity-tokuma'))
        self.assertEqual(p['nextName'], 'Tokuma Shoten（徳間書店）')
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        queue = review['progress']['queue']
        self.assertEqual([q['status'] for q in queue], ['reviewed'] * 12 + ['pending'] * 7)
        script = """import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(execFileSync('git',['show','700c5f0c055bd9be328bf7000dc6f004d9162d76:data/entities.json'],{encoding:'utf8',maxBuffer:4*1024*1024})).entities;
process.stdout.write(JSON.stringify(sortFamilies(es.filter(e=>e.name.toLowerCase().startsWith('t'))
 .map(e=>({id:e.id,title:e.name}))).map(e=>e.id)));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in queue], actual)

    def test_dossier_resolution_rejects_old_state_mismatch_and_wrong_subject(self):
        original_read = builder.read
        for mutation in [dict(before=dict(roles=['publisher'], group='release', status='existingEvidence')),
                         dict(entityId=IDS[1]), dict(dossierId='taito'),
                         dict(beforeWorkRoles=['publisher']), dict(expectedPlacement='main')]:
            with self.subTest(mutation=mutation):
                review = copy.deepcopy(read(REVIEW))
                review['creditAdditions'][0].update(mutation)
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
