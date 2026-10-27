"""T5 completes T while preserving historical publishers and work identities."""
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
BASE = '41aa48d6c62b67c30cf6f516f33dc5aa59e1cdc3'
REVIEW = 'data/entity-creator-t5-review-20261026.json'
IDS = ['entity-name-679a14238228', 'entity-name-8039f82ef72c', 'entity-name-77c5d6e9dcc8']


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'62f913e8fccbbdec5fe2d7c14ef8fdca72cde2b0:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorT5Tests(unittest.TestCase):
    def test_three_identities_change_without_alias_mergers_or_new_dates(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(IDS))
        for eid, kind in zip(IDS, ['brand', 'company', 'brand']):
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), (kind, 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 47))

    def test_four_scoped_production_brands_preserve_every_old_credit_and_publisher(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-4], before['credits'])
        self.assertEqual(len(after['credits']), 5009)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-4:]],
                         [(IDS[2], 'work', wid, 'productionBrand') for wid in ['g031', 'g036', 'g155', 'g156']])
        for c in after['credits'][-4:]:
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])
        for eid, count in zip(IDS, [1, 2, 7]):
            publishers = [c for c in after['credits'] if c['entityId'] == eid and c['role'] == 'publisher']
            self.assertEqual(len(publishers), count)
            self.assertFalse(any(c['entityId'] == eid and c['role'] in
                                 ['publishingBrand', 'originalPublishingBrand', 'developer', 'originalProduction']
                                 for c in after['credits']))

    def test_all_parent_memberships_and_original_work_content_release_objects_stay_exact(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(before['dossierMemberships'], after['dossierMemberships'])
        self.assertEqual((len(after['dossierMemberships']), sum(m['status'] == 'pendingRole'
                          for m in after['dossierMemberships'])), (2234, 601))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        games = read('data/games.json')
        remake = next(w for w in games['works'] if w['id'] == 'g036')
        self.assertEqual(remake['firstYear'], 2021)
        for rid in ['g036-v2', 'g031-v4', 'g031-v5']:
            r = next(r for r in games['platformReleases'] if r['id'] == rid)
            self.assertIsNone(r['contentVersionId'])
            self.assertEqual(r['contentRelation'], 'unverified')
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])

    def test_three_consecutive_entities_complete_t_and_advance_to_ultra_games(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('T', 19, 19, 298, 298, 'entity-name-c87c2b9662fc'))
        self.assertEqual(p['nextName'], 'Ultra Games')
        self.assertEqual(p['processedEntityIds'][:-3], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-3:], IDS)
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], IDS)
        queue = review['progress']['queue']
        self.assertEqual([q['status'] for q in queue], ['reviewed'] * 19)
        script = """import fs from 'node:fs';
import {execFileSync} from 'node:child_process';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(execFileSync('git',['show','62f913e8fccbbdec5fe2d7c14ef8fdca72cde2b0:data/entities.json'],{encoding:'utf8',maxBuffer:4*1024*1024})).entities;
const sorted=sortFamilies(es.map(e=>({id:e.id,title:e.name})));
process.stdout.write(JSON.stringify({t:sorted.filter(e=>/^t/i.test(e.title)).map(e=>e.id),
 next:sorted[sorted.findIndex(e=>e.id==='entity-name-77c5d6e9dcc8')+1].id}));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([q['entityId'] for q in queue], actual['t'])
        self.assertEqual(p['nextEntityId'], actual['next'])

    def test_both_brand_corrections_require_explicit_preservation_of_release_roles(self):
        original_read = builder.read
        for index in [0, 2]:
            for value in [False, None]:
                with self.subTest(index=index, preserveReleaseRoles=value):
                    review = copy.deepcopy(read(REVIEW))
                    review['identityCorrections'][index]['preserveReleaseRoles'] = value
                    with patch.object(builder, 'read', side_effect=lambda path:
                                      review if path == REVIEW else original_read(path)):
                        with self.assertRaises(AssertionError):
                            builder.build()
