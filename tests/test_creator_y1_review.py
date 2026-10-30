"""Y1 records sourced entity dates without changing historic credits or works."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = '1d1d898595e9979cf7e3f15733777f58ccac029b'
YONAGO, SOUR, YUZU = 'entity-yonago_gainax', 'entity-yuzusoft_sour', 'entity-yuzusoft'
IDS = [YONAGO, SOUR, YUZU]
REVIEW = 'data/entity-creator-y1-review-20261026.json'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json',
                'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(
            ['git', 'show', f'd261b71bc00c3e3632f0e20a8cbc54abd1cd9a6b:{path}'], cwd=ROOT))
    return read(path)


class CreatorY1Tests(unittest.TestCase):
    def test_two_sourced_dates_are_the_only_entity_changes(self):
        before, after = [dict((e['id'], e) for e in d['entities']) for d in
                         [old('data/entities.json'), applied('data/entities.json')]]
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual({eid for eid in before if before[eid] != after[eid]}, {YONAGO, SOUR})
        review = read(REVIEW)
        self.assertEqual(review['identityCorrections'], [])
        self.assertEqual(review['creditAdditions'], [])
        for record in review['dateFacts']:
            eid = record['entityId']
            self.assertEqual(before[eid]['dates'], record['before'])
            self.assertEqual(after[eid]['dates'], [{key: record[key] for key in
                                                    ['kind', 'value', 'precision', 'source', 'status']}])
            self.assertEqual(after[eid]['sources'], before[eid]['sources'] + [record['source']])
            self.assertEqual({k: v for k, v in after[eid].items() if k not in ('dates', 'sources')},
                             {k: v for k, v in before[eid].items() if k not in ('dates', 'sources')})
        self.assertEqual([(r['entityId'], r['kind'], r['value'], r['precision']) for r in review['dateFacts']],
                         [(YONAGO, 'established', '2014-05', 'month'),
                          (SOUR, 'brandActivityStarted', '2021-07', 'month')])
        self.assertEqual((after[YUZU]['type'], after[SOUR]['type'], after[YONAGO]['type']),
                         ('brand', 'brand', 'company'))

    def test_scope_and_historical_objects_remain_unchanged(self):
        for path in ['data/credits.json', 'data/games.json', 'data/company-coverage.json',
                     'data/taxonomy.json', 'data/gameplay-catalogues.json',
                     'data/work-classification.json', 'data/entity-migration-review.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(applied(path), old(path), path)
        cs = applied('data/credits.json')
        by = lambda eid: [c for c in cs['credits'] if c['entityId'] == eid]
        self.assertEqual([(c['targetType'], c['targetId'], c['role']) for c in by(YONAGO)],
                         [('content', 'g821-c-regeneration', 'addedAnimation')])
        self.assertEqual((len(by(SOUR)), len(by(YUZU))), (6, 28))
        self.assertEqual({c['role'] for c in by(SOUR)},
                         {'productionBrand', 'originalPublishingBrand', 'publishingBrand'})
        self.assertEqual({c['role'] for c in by(YUZU)},
                         {'originalPublishingBrand', 'publishingBrand'})
        self.assertEqual((len(cs['credits']), len(cs['dossierMemberships']),
                          sum(m['status'] == 'pendingRole' for m in cs['dossierMemberships'])),
                         (5011, 2234, 601))
        g = read('data/games.json')
        for release in [r for r in g['platformReleases'] if r['workId'] == 'g232' and r['id'] != 'g232-v1']:
            self.assertEqual((release['contentRelation'], release['contentVersionId']),
                             ('unverified', None))
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        for field in ['edges', 'works', 'credits', 'families']:
            self.assertEqual(after[field], before[field], field)
        by_id = lambda d: {n['id']: n for n in d['nodes']}
        bn, an = by_id(before), by_id(after)
        self.assertEqual(bn.keys(), an.keys())
        self.assertEqual({eid for eid in bn if bn[eid] != an[eid]}, {YONAGO, SOUR})

    def test_y_queue_completes_then_moves_to_numeric_group(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('Y', 3, 3, 312, 312, 'entity-5pb'))
        self.assertEqual(p['processedEntityIds'][:-3], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-3:], IDS)
        review = read(REVIEW)
        self.assertEqual([r['entityId'] for r in review['reviewedEntities']], IDS)
        script = """import fs from 'node:fs';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(fs.readFileSync('data/entities.json')).entities;
const sorted=sortFamilies(es.map(e=>({id:e.id,title:e.name})));
process.stdout.write(JSON.stringify({y:sorted.filter(e=>/^y/i.test(e.title)).map(e=>e.id),
 next:sorted[sorted.findIndex(e=>e.id==='entity-yuzusoft')+1].id}));"""
        actual = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', script], cwd=ROOT))
        self.assertEqual([eid for eid in actual['y'] if eid in set(IDS)], IDS)
        self.assertGreaterEqual(len(actual['y']), len(IDS))
        self.assertNotIn(actual['next'], IDS)
        self.assertIn(p['nextEntityId'], {e['id'] for e in read('data/entities.json')['entities']})


if __name__ == '__main__':
    unittest.main()
