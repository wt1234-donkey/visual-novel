"""Leland reuses its historical release and keeps asset succession scoped."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_company_pages import build_dossier_navigation
from catalogue_snapshot import PRE_LELAND


def read(path):
    return json.loads(subprocess.check_output(['git','show',f'fb69d2f381a483c6214f7807c551149b6264f6f7:{path}'],cwd=ROOT))


class LelandDossierTests(unittest.TestCase):
    def test_completed_catalogue_expansion_preserved_published_organization_results(self):
        published = '8c16099af18e77b618f747223952d4e140e67b8f'
        completed = 'fb69d2f381a483c6214f7807c551149b6264f6f7'
        def before(path):
            return subprocess.check_output(['git', 'show', f'{published}:{path}'], cwd=ROOT)
        def at_completion(path):
            return subprocess.check_output(['git', 'show', f'{completed}:{path}'], cwd=ROOT)
        for path in ['data/games.json', 'data/credits.json', 'data/organizations.json',
                     'data/organization-context-20261027.json',
                     'data/organization-verification-20261027.json',
                     'data/entity-organization-review-20261027.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(at_completion(path), before(path), path)
        prior = json.loads(before('data/entities.json'))
        current = json.loads(at_completion('data/entities.json'))
        self.assertEqual(current['entities'], prior['entities'])
        self.assertEqual(current['relations'], prior['relations'])
        self.assertEqual([d for d in current['dossiers'] if d['id'] != 'leland'],
                         [d for d in prior['dossiers'] if d['id'] != 'leland'])

    def test_existing_catalogue_objects_and_main_navigation_are_preserved(self):
        def before(path):
            return subprocess.check_output(['git', 'show', f'{PRE_LELAND}:{path}'], cwd=ROOT)
        for path in ['data/games.json', 'data/taxonomy.json', 'data/work-classification.json',
                     'data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(subprocess.check_output(['git','show',f'fb69d2f381a483c6214f7807c551149b6264f6f7:{path}'],cwd=ROOT), before(path), path)
        coverage = read('data/company-coverage.json')
        self.assertEqual([c['id'] for c in coverage['companies'] if c['id'] == 'leland'], ['leland'])
        coverage['companies'] = [c for c in coverage['companies'] if c['id'] != 'leland']
        self.assertEqual(coverage, json.loads(before('data/company-coverage.json')))
        gameplay = read('data/gameplay-catalogues.json')
        gameplay['companies'].pop('leland')
        self.assertEqual(gameplay, json.loads(before('data/gameplay-catalogues.json')))
        from unittest.mock import patch
        import build_company_pages as pages
        historical_dossiers = {d['id']: d for d in read('data/entities.json')['dossiers']}
        with patch.object(pages, 'coverage', read('data/company-coverage.json')), patch.object(pages, 'DOSSIERS', historical_dossiers):
            index = subprocess.check_output(['git','show','fb69d2f381a483c6214f7807c551149b6264f6f7:index.html'],cwd=ROOT).decode()
            self.assertEqual(index, build_dossier_navigation(before('index.html').decode()))

    def test_single_existing_main_work_and_publisher_are_reused(self):
        dossier = next(x for x in read('data/company-coverage.json')['companies'] if x['id'] == 'leland')
        self.assertEqual(dossier['workIds'], ['g045'])
        self.assertEqual(dossier['publisherWorkIds'], ['g045'])
        data = read('data/games.json')
        self.assertEqual([w['id'] for w in data['works'] if w['id'] == 'g045'], ['g045'])
        self.assertEqual([r['id'] for r in data['platformReleases'] if r['workId'] == 'g045'], ['g045-v1'])
        self.assertEqual([c['id'] for c in data['contentVersions'] if c['workId'] == 'g045'], ['g045-c-original'])
        self.assertEqual(next(r for r in data['platformReleases'] if r['id'] == 'g045-v1')['publisher'], 'Leland')
        page = (ROOT / 'leland.html').read_text(encoding='utf-8')
        self.assertEqual(page.count('<article class="card"'), 1)
        self.assertIn('id="g045"', page)

    def test_existing_company_id_and_release_only_role_survive(self):
        model = read('data/entities.json')
        prior = json.loads(subprocess.check_output(['git', 'show', f'{PRE_LELAND}:data/entities.json'], cwd=ROOT))
        old_entities = {e['id']: e for e in prior['entities']}
        current_entities = {e['id']: e for e in model['entities']}
        self.assertEqual(old_entities.keys(), current_entities.keys())
        self.assertEqual({eid for eid in old_entities if old_entities[eid] != current_entities[eid]},
                         {'entity-name-547f933b0469', 'entity-name-21dcd9c9c1e7'})
        self.assertEqual(model['relations'], prior['relations'])
        self.assertEqual([d for d in model['dossiers'] if d['id'] != 'leland'], prior['dossiers'])
        entity = next(e for e in model['entities'] if e['id'] == 'entity-name-547f933b0469')
        self.assertEqual((entity['name'], entity['type']), ('Leland', 'company'))
        self.assertFalse(any(e['id'] == 'entity-leland' for e in model['entities']))
        self.assertEqual(next(d for d in model['dossiers'] if d['id'] == 'leland')['entityIds'], [entity['id']])
        credits = read('data/credits.json')
        old_credits = json.loads(subprocess.check_output(['git', 'show', f'{PRE_LELAND}:data/credits.json'], cwd=ROOT))
        self.assertEqual(credits['credits'], old_credits['credits'])
        self.assertEqual([m for m in credits['dossierMemberships'] if m['dossierId'] != 'leland'],
                         old_credits['dossierMemberships'])
        self.assertEqual([(c['workId'], c['role']) for c in credits['credits'] if c['entityId'] == entity['id']], [('g045', 'publisher')])
        self.assertEqual(next(m for m in credits['dossierMemberships'] if m['dossierId'] == 'leland')['group'], 'release')

    def test_succession_is_source_linked_and_does_not_inherit_old_games(self):
        data = read('data/organizations.json')
        edge = next(e for e in data['edges'] if e['id'] == 'leland-business-succession-1987')
        self.assertEqual((edge['parent'], edge['child'], edge['kind']),
                         ('entity-cinematronics', 'entity-name-547f933b0469', 'succession'))
        leland = next(n for n in data['nodes'] if n['id'] == edge['child'])
        self.assertEqual(leland['stats']['main'], 1)
        self.assertEqual(leland['productionCount'], 0)
        self.assertFalse({'g010', 'g044'} & {c['workId'] for c in read('data/credits.json')['credits'] if c['entityId'] == edge['child']})


if __name__ == '__main__':
    unittest.main()
