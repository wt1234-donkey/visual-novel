"""U1 separates a publishing mark from a historical company and modern homonyms."""
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
BASE = '62f913e8fccbbdec5fe2d7c14ef8fdca72cde2b0'
REVIEW = 'data/entity-creator-u1-review-20261026.json'
IDS = ['entity-name-c87c2b9662fc', 'entity-name-810ea95a0ca4']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'd4370f1cf0fc8984ff5dab3bd458fec81f93b0f8:{path}'], cwd=ROOT))
    return read(path)


class CreatorU1Tests(unittest.TestCase):
    def test_only_two_identities_change_without_modern_homonym_mergers_or_dates(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(IDS))
        for eid, kind in zip(IDS, ['brand', 'company']):
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertNotIn('https://union-p.jp/about_cp.html', ae[IDS[1]]['sources'])
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 45))

    def test_every_credit_and_membership_remains_exact_with_publisher_only_subjects(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after, before)
        self.assertEqual(len(after['credits']), 5009)
        self.assertEqual((len(after['dossierMemberships']), sum(m['status'] == 'pendingRole'
                          for m in after['dossierMemberships'])), (2234, 601))
        self.assertEqual(read(REVIEW)['creditAdditions'], [])
        for eid, rid in zip(IDS, ['g1029-v1', 'g1176-v-original']):
            cs = [c for c in after['credits'] if c['entityId'] == eid]
            self.assertEqual([(c['targetType'], c['targetId'], c['role']) for c in cs],
                             [('release', rid, 'publisher')])
            node = next(n for n in applied('data/organizations.json')['nodes'] if n['id'] == eid)
            self.assertEqual(node['groups']['creation'], [])
            self.assertEqual(node['productionCount'], 0)

    def test_all_original_catalogue_objects_and_distinct_nightshade_work_stay_exact(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        games = read('data/games.json')
        self.assertEqual(next(w['firstYear'] for w in games['works'] if w['id'] == 'g1029'), 1992)
        self.assertEqual(next(w['firstYear'] for w in games['works'] if w['id'] == 'g1176'), 1984)
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_two_consecutive_entities_complete_u_and_advance_to_virgin_games(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('U', 2, 2, 300, 300, 'entity-name-317db6dbff30'))
        self.assertEqual(p['nextName'], 'Virgin Games Ltd')
        self.assertEqual(p['processedEntityIds'][:-2], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-2:], IDS)
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        queue = review['progress']['queue']
        self.assertEqual([q['status'] for q in queue], ['reviewed'] * 2)
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse((await import('node:child_process')).execFileSync('git',['show','d4370f1cf0fc8984ff5dab3bd458fec81f93b0f8:data/entities.json']).toString()).entities;
const sorted=sortFamilies(es.map(e=>({id:e.id,title:e.name})));
process.stdout.write(JSON.stringify({u:sorted.filter(e=>/^u/i.test(e.title)).map(e=>e.id),
 next:sorted[sorted.findIndex(e=>e.id==='entity-name-810ea95a0ca4')+1].id}));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in queue], actual['u'])
        self.assertEqual(p['nextEntityId'], actual['next'])

    def test_trademark_identity_requires_explicit_release_role_preservation(self):
        original_read = builder.read
        for value in [False, None]:
            with self.subTest(preserveReleaseRoles=value):
                review = copy.deepcopy(read(REVIEW))
                review['identityCorrections'][0]['preserveReleaseRoles'] = value
                with patch.object(builder, 'read', side_effect=lambda path:
                                  review if path == REVIEW else original_read(path)):
                    with self.assertRaises(AssertionError):
                        builder.build()
