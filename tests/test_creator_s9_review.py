"""S9 preserves American/Japanese identities, historical periods and content scope."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'a5c6f50f4f6aa62752f328003af9ba13dbd62477'
REVIEW = 'data/entity-creator-s9-review-20261026.json'
IDS = ['entity-name-8a3d38d0d11f', 'entity-name-6d2a66d8a91c',
       'entity-name-e92deef78c89', 'entity-square']
SQUARE_WORKS = ['g1210', 'square-chronotrigger', 'square-xenogears', 'square-chronocross']


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'498f6f9af8414b8e1d900f306382d1dc27887f8a:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS9Tests(unittest.TestCase):
    def test_two_company_corrections_do_not_merge_signatures_or_backfill_dates(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, set(IDS[1:3]))
        for eid in IDS[1:3]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(len(ae), 326)
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 61)
        self.assertEqual([x['rawName'] for x in read(REVIEW)['identityCorrections']],
                         ['スクウェア・エニックス', 'Square Soft, Inc.'])

    def test_exactly_five_original_productions_preserve_all_earlier_credits(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-5], before['credits'])
        self.assertEqual(len(after['credits']), 4994)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-5:]],
                         [(IDS[2], 'work', 'square-evermore', 'originalProduction')]
                         + [(IDS[3], 'work', wid, 'originalProduction') for wid in SQUARE_WORKS])
        for c in after['credits'][-5:]:
            self.assertEqual(c['status'], 'sourceReviewed')
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual([c for c in after['credits'] if c['targetType'] == 'release'],
                         [c for c in before['credits'] if c['targetType'] == 'release'])
        for eid in IDS[:2]:
            self.assertEqual([c for c in after['credits'] if c['entityId'] == eid],
                             [c for c in before['credits'] if c['entityId'] == eid])
        self.assertFalse(any(c['entityId'] == IDS[3] and c['workId'] == 'square-evermore'
                             for c in after['credits']))
        self.assertFalse(any(c['entityId'] == IDS[2] and c['workId'] == 'square-ffusa'
                             and c['role'] == 'originalProduction' for c in after['credits']))

    def test_only_four_square_memberships_change_and_american_work_stays_pending(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        bm, am = [{(m['dossierId'], m['workId']): m for m in d['dossierMemberships']}
                  for d in [before, after]]
        self.assertEqual(bm.keys(), am.keys())
        expected = {('square', wid) for wid in SQUARE_WORKS}
        self.assertEqual({k for k in bm if bm[k] != am[k]}, expected)
        for k in expected:
            self.assertEqual(bm[k]['roles'], ['publisher'])
            self.assertEqual(am[k]['roles'], ['originalProduction', 'publisher'])
            self.assertEqual((bm[k]['group'], am[k]['group']), ('release', 'original'))
            for field in ['dossierId', 'workId', 'placement', 'source', 'status']:
                self.assertEqual(bm[k][field], am[k][field])
        self.assertEqual(am[('square', 'square-evermore')], bm[('square', 'square-evermore')])
        self.assertEqual(am[('square', 'square-evermore')]['status'], 'pendingRole')
        self.assertEqual((len(am), sum(m['status'] == 'pendingRole' for m in am.values())), (2234, 602))
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/content-migration-baseline.json', 'data/entity-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_four_consecutive_entities_advance_to_starcraft_without_admission_changes(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 36, 42, 273, 279, 'entity-name-a3d00ecbbdcb'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        r = read(REVIEW)
        self.assertEqual([e['entityId'] for e in r['reviewedEntities']], IDS)
        self.assertEqual([e['entityId'] for e in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 36 + ['pending'] * 6)
        self.assertEqual(after['works'], before['works'])
