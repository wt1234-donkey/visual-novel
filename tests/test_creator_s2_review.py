"""S2 preserves publisher evidence and confines Plus development to its content."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '8d86229a9f65735f0fe68ab8bd67e362eff8a759'
SEIKAISHA, SEKAI, SERENITY, SHALL = IDS = [
    'entity-name-7c9d766b5702', 'entity-name-06aeb9d01fbe',
    'entity-name-22015689e48e', 'entity-name-13bcad90dc83']
REVIEW = 'data/entity-creator-s2-review-20261025.json'


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/credits.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'af8d34d953350633ef3975aae99384ae01c7a0a6:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS2Tests(unittest.TestCase):
    def test_only_two_company_identities_change_without_dates_relations_or_name_changes(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {SEIKAISHA, SHALL})
        for eid in [SEIKAISHA, SHALL]:
            self.assertEqual((be[eid]['type'], be[eid]['verification']), ('unknown', 'unresolved'))
            self.assertEqual((ae[eid]['type'], ae[eid]['verification']), ('company', 'sourceReviewed'))
            for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
                self.assertEqual(be[eid].get(field), ae[eid].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(len(ae), 326)
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 72)

    def test_two_precise_credits_preserve_all_existing_records_and_release_roles(self):
        before, after = old('data/credits.json'), applied('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        actual = [(c['entityId'], c['targetType'], c['targetId'], c['workId'], c['role'], c['status'])
                  for c in after['credits'][-2:]]
        self.assertEqual(actual, [
            (SEIKAISHA, 'work', 'g613', 'g613', 'originalProduction', 'sourceReviewed'),
            (SERENITY, 'content', 'g056-c-3', 'g056', 'developer', 'sourceReviewed')])
        self.assertEqual(len(after['credits']), 4979)
        self.assertEqual([sum(c['entityId'] == eid and c['role'] == 'publisher'
                                  for c in after['credits']) for eid in IDS], [1, 11, 5, 1])
        for eid in [SEKAI, SHALL]:
            self.assertFalse(any(c['entityId'] == eid and c['targetType'] != 'release' for c in after['credits']))
        self.assertFalse(any(c['entityId'] == SERENITY and c['targetType'] == 'work' for c in after['credits']))
        for c in after['credits'][-2:]:
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual(before['dossierMemberships'], after['dossierMemberships'])
        self.assertEqual(len(after['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 602)

    def test_original_catalogue_content_unknown_mobile_and_gba_releases_stay_unchanged(self):
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)
        d = read('data/games.json')
        self.assertEqual([len(d[f]) for f in ['works', 'contentVersions', 'platformReleases']], [1274, 1487, 2487])
        releases = {r['id']: r for r in d['platformReleases']}
        for rid in ['g056-v6', 'g056-v7', 'g777-v3']:
            self.assertIsNone(releases[rid]['contentVersionId'])
            self.assertEqual(releases[rid]['contentRelation'], 'unverified')
        self.assertEqual([r['id'] for r in releases.values() if r['contentVersionId'] == 'g056-c-3'],
                         ['g056-v3', 'g056-v4', 'g056-v5'])

    def test_s_order_advances_four_consecutive_entities_to_sharrock(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'], len(p['processedEntityIds']),
                          p['total'], p['nextEntityId']), ('S', 7, 42, 244, 279, 'entity-sharrock'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        review = read(REVIEW)
        self.assertEqual([q['status'] for q in review['progress']['queue']], ['reviewed'] * 7 + ['pending'] * 35)
        self.assertEqual([x['entityId'] for x in review['reviewedEntities']], IDS)
        self.assertEqual([x['entityId'] for x in review['deferredReviews']], IDS)
        nodes = {n['id']: n for n in after['nodes']}
        self.assertEqual([nodes[e]['productionCount'] for e in IDS], [1, 0, 1, 0])
        self.assertEqual(after['works'], before['works'])
