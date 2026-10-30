"""V1 distinguishes an historical publisher company from an existing brand family."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd4370f1cf0fc8984ff5dab3bd458fec81f93b0f8'
VIRGIN = 'entity-name-317db6dbff30'
VISUAL = 'entity-visualarts'
KEY = 'entity-key'
REVIEW = 'data/entity-creator-v1-review-20261026.json'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json', 'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'7fd9b99d705fcbd62e47bdc5fb02b8fc4e419208:{path}'], cwd=ROOT))
    return read(path)


class CreatorV1Tests(unittest.TestCase):
    def test_one_identity_only_with_names_dossiers_relations_dates_unchanged(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({eid for eid in be if be[eid] != ae[eid]}, {VIRGIN})
        self.assertEqual((be[VIRGIN]['type'], be[VIRGIN]['verification']), ('unknown', 'unresolved'))
        self.assertEqual((ae[VIRGIN]['type'], ae[VIRGIN]['verification']), ('company', 'sourceReviewed'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[VIRGIN].get(field), ae[VIRGIN].get(field))
        self.assertEqual((ae[VISUAL]['type'], ae[KEY]['type']), ('company', 'brand'))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual((len(ae), sum(e['verification'] == 'unresolved' for e in ae.values())), (326, 44))

    def test_all_credits_memberships_original_catalogue_unchanged(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(before, after)
        self.assertEqual((len(after['credits']), len(after['dossierMemberships']),
                          sum(m['status'] == 'pendingRole' for m in after['dossierMemberships'])),
                         (5009, 2234, 601))
        self.assertEqual(read(REVIEW)['creditAdditions'], [])
        virgin = [c for c in after['credits'] if c['entityId'] == VIRGIN]
        visual = [c for c in after['credits'] if c['entityId'] == VISUAL]
        self.assertEqual([(c['targetType'], c['targetId'], c['role']) for c in virgin],
                         [('release', 'g1203-v-original', 'publisher')])
        self.assertEqual((len(visual), {c['role'] for c in visual}), (46, {'publisher'}))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        self.assertEqual(applied('data/organizations.json')['works'], old('data/organizations.json')['works'])
        self.assertEqual(next(w['firstYear'] for w in read('data/games.json')['works'] if w['id'] == 'g1203'), 1987)

    def test_complete_v_order_and_next_wfs(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('V', 2, 2, 302, 302, 'entity-name-a7663faeee46'))
        self.assertEqual(p['nextName'], 'WFS（WRIGHT FLYER STUDIOS）')
        self.assertEqual(p['processedEntityIds'][:-2], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-2:], [VIRGIN, VISUAL])
        review = read(REVIEW)
        self.assertEqual([e['entityId'] for e in review['reviewedEntities']], [VIRGIN, VISUAL])
        self.assertEqual([e['entityId'] for e in review['deferredReviews']], [VIRGIN, VISUAL])
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse((await import('node:child_process')).execFileSync('git',['show','7fd9b99d705fcbd62e47bdc5fb02b8fc4e419208:data/entities.json']).toString()).entities;
const sorted=sortFamilies(es.map(e=>({id:e.id,title:e.name})));
process.stdout.write(JSON.stringify({v:sorted.filter(e=>/^v/i.test(e.title)).map(e=>e.id),
 next:sorted[sorted.findIndex(e=>e.id==='entity-visualarts')+1].id}));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual(actual['v'], [VIRGIN, VISUAL])
        self.assertEqual(p['nextEntityId'], actual['next'])


if __name__ == '__main__':
    unittest.main()
