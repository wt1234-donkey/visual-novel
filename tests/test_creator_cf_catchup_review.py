"""The eight renamed C–F entities are audited before the numeric queue."""
import json
import subprocess
import unittest
from pathlib import Path
from catalogue_snapshot import catalogue_bytes

ROOT = Path(__file__).resolve().parents[1]
BASE = 'd261b71bc00c3e3632f0e20a8cbc54abd1cd9a6b'
IDS = ['entity-champion_soft', 'entity-cocktailsoft', 'entity-jast_crest',
       'entity-dramaticcreate', 'entity-fairytale_x', 'entity-fairytale_ethix',
       'entity-fairytale', 'entity-fairytale_hana']
REVIEW = 'data/entity-creator-cf-catchup-review-20261026.json'


def read(path):
    return json.loads(catalogue_bytes(ROOT, path).decode())


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json',
                'data/entity-migration-review.json']:
        return json.loads(subprocess.check_output(
            ['git', 'show', f'7be9bd94fd8b0b3cd3c964bdd7d6c43bc8ee4a2e:{path}'], cwd=ROOT))
    return read(path)


class CreatorCFCatchupTests(unittest.TestCase):
    def test_only_hunex_brand_activity_is_added_to_entities(self):
        before, after = [dict((e['id'], e) for e in d['entities']) for d in
                         [old('data/entities.json'), applied('data/entities.json')]]
        self.assertEqual(before.keys(), after.keys())
        self.assertEqual({eid for eid in before if before[eid] != after[eid]}, {'entity-dramaticcreate'})
        eid = 'entity-dramaticcreate'
        fact, = read(REVIEW)['dateFacts']
        self.assertEqual((fact['entityId'], fact['kind'], fact['value'], fact['precision']),
                         (eid, 'brandActivityStarted', '2014', 'year'))
        self.assertEqual(before[eid]['dates'], fact['before'])
        self.assertEqual(after[eid]['dates'], [{key: fact[key] for key in
                                               ['kind', 'value', 'precision', 'source', 'status']}])
        self.assertEqual(after[eid]['sources'], before[eid]['sources'] + [fact['source']])
        self.assertEqual({k: v for k, v in after[eid].items() if k not in ('dates', 'sources')},
                         {k: v for k, v in before[eid].items() if k not in ('dates', 'sources')})
        self.assertEqual([(after[i]['type'], after[i]['verification']) for i in IDS],
                         [(before[i]['type'], before[i]['verification']) for i in IDS])

    def test_credits_catalogue_and_older_unknowns_stay_unchanged(self):
        for path in ['data/credits.json', 'data/games.json', 'data/company-coverage.json',
                     'data/taxonomy.json', 'data/gameplay-catalogues.json',
                     'data/work-classification.json', 'data/entity-migration-review.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(applied(path), old(path), path)
        cs = applied('data/credits.json')
        self.assertEqual((len(cs['credits']), len(cs['dossierMemberships']),
                          sum(m['status'] == 'pendingRole' for m in cs['dossierMemberships'])),
                         (5011, 2234, 601))
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        for key in ['edges', 'works', 'credits', 'families']:
            self.assertEqual(after[key], before[key], key)
        bn, an = [{n['id']: n for n in d['nodes']} for d in [before, after]]
        self.assertEqual({eid for eid in bn if bn[eid] != an[eid]}, {'entity-dramaticcreate'})

    def test_missing_eight_are_processed_in_current_sort_order(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('C—F', 8, 8, 320, 320, 'entity-5pb'))
        self.assertEqual(p['processedEntityIds'][:-8], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-8:], IDS)
        self.assertEqual(len(p['processedEntityIds']), len(set(p['processedEntityIds'])))
        review = read(REVIEW)
        self.assertEqual(review['identityCorrections'], [])
        self.assertEqual(review['creditAdditions'], [])
        self.assertEqual([r['entityId'] for r in review['reviewedEntities']], IDS)
        self.assertEqual([r['entityId'] for r in review['deferredReviews']], IDS)
        script = """import {execFileSync} from 'node:child_process';
import {sortFamilies} from './relationships-preview.mjs';
const es=JSON.parse(execFileSync('git',['show','7be9bd94fd8b0b3cd3c964bdd7d6c43bc8ee4a2e:data/entities.json'],{encoding:'utf8'})).entities;
const seen=new Set(JSON.parse(process.argv[1]));
const missing=sortFamilies(es.map(e=>({id:e.id,title:e.name}))).filter(e=>!seen.has(e.id));
process.stdout.write(JSON.stringify(missing.map(e=>e.id)));"""
        actual = json.loads(subprocess.check_output(
            ['node', '--input-type=module', '-e', script, json.dumps(before['registrationProgress']['processedEntityIds'])], cwd=ROOT))
        self.assertEqual(actual[:8], IDS)
        self.assertEqual(actual[8], p['nextEntityId'])


if __name__ == '__main__':
    unittest.main()
