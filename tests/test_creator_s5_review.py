"""S5 keeps an unresolved publisher conflict and separates creative teams."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = '5350087819ae8406336cb1dca05e83ccd0b3e001'
IDS = ['entity-name-8c9d353d6fe9', 'entity-silkys_dolce', 'entity-silkys_wasabi',
       'entity-name-b129f13b41e4']
REVIEW = 'data/entity-creator-s5-review-20261026.json'


def read(path):
    return json.loads((ROOT / path).read_text())


def applied(path):
    if path in ['data/entities.json', 'data/organizations.json']:
        return json.loads(subprocess.check_output(['git', 'show', f'5de7b25eecbf8a05f33bc4decb06b1edf6f3ab75:{path}'], cwd=ROOT))
    return read(path)


def old(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))


class CreatorS5Tests(unittest.TestCase):
    def test_publishing_division_identity_changes_without_new_release_or_brand_roles(self):
        before, after = old('data/entities.json'), applied('data/entities.json')
        be, ae = [{e['id']: e for e in d['entities']} for d in [before, after]]
        self.assertEqual(be.keys(), ae.keys())
        self.assertEqual({k for k in be if be[k] != ae[k]}, {IDS[3]})
        self.assertEqual((ae[IDS[3]]['type'], ae[IDS[3]]['verification']), ('brand', 'sourceReviewed'))
        self.assertEqual((ae[IDS[0]]['type'], ae[IDS[0]]['verification']), ('unknown', 'unresolved'))
        for field in ['id', 'name', 'aliases', 'dates', 'nameParts']:
            self.assertEqual(be[IDS[3]].get(field), ae[IDS[3]].get(field))
        self.assertEqual(before['relations'], after['relations'])
        self.assertEqual(before['dossiers'], after['dossiers'])
        self.assertEqual(sum(e['verification'] == 'unresolved' for e in ae.values()), 70)
        bc, ac = old('data/credits.json'), read('data/credits.json')
        for eid in [IDS[0], IDS[3]]:
            rows = [c for c in ac['credits'] if c['entityId'] == eid]
            self.assertEqual(rows, [c for c in bc['credits'] if c['entityId'] == eid])
            self.assertEqual([c['role'] for c in rows], ['publisher'])
        self.assertTrue(read(REVIEW)['identityCorrections'][0]['preserveReleaseRoles'])

    def test_two_scoped_team_credits_preserve_parent_memberships_and_catalogue(self):
        before, after = old('data/credits.json'), read('data/credits.json')
        self.assertEqual(after['credits'][:-2], before['credits'])
        self.assertEqual(len(after['credits']), 4986)
        self.assertEqual([(c['entityId'], c['targetType'], c['targetId'], c['role'])
                          for c in after['credits'][-2:]],
                         [(IDS[1], 'work', 'g475', 'productionBrand'),
                          (IDS[2], 'work', 'g468', 'productionBrand')])
        for c in after['credits'][-2:]:
            self.assertEqual(c['reviewRecord'], REVIEW.replace('.json', '.md'))
        self.assertEqual(after['dossierMemberships'], before['dossierMemberships'])
        self.assertEqual(len(after['dossierMemberships']), 2234)
        self.assertEqual(sum(m['status'] == 'pendingRole' for m in after['dossierMemberships']), 602)
        for wid in ['g468', 'g475']:
            self.assertEqual(next(m for m in after['dossierMemberships']
                                  if m['dossierId'] == 'silkys_plus' and m['workId'] == wid)['status'], 'pendingRole')
        for path in ['data/games.json', 'data/company-coverage.json', 'data/taxonomy.json',
                     'data/gameplay-catalogues.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(read(path), old(path), path)

    def test_four_consecutive_entities_advance_to_sinclair(self):
        before, after = old('data/organizations.json'), applied('data/organizations.json')
        p = after['registrationProgress']
        self.assertEqual((p['letter'], p['letterProcessed'], p['letterTotal'],
                          len(p['processedEntityIds']), p['total'], p['nextEntityId']),
                         ('S', 19, 42, 256, 279, 'entity-sinclair'))
        self.assertEqual(p['processedEntityIds'][:-4], before['registrationProgress']['processedEntityIds'])
        self.assertEqual(p['processedEntityIds'][-4:], IDS)
        r = read(REVIEW)
        self.assertEqual([x['entityId'] for x in r['reviewedEntities']], IDS)
        self.assertEqual([x['entityId'] for x in r['deferredReviews']], IDS)
        self.assertEqual([q['status'] for q in r['progress']['queue']], ['reviewed'] * 19 + ['pending'] * 23)
        self.assertEqual(after['works'], before['works'])
