"""Project-list completion preserves history and separates narrative admission."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = 'cde23e0121b2458e986cff9eaa519b4ef591d843'

def read(path):
    return json.loads((ROOT / path).read_text())

def before(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))

class TokumaCompletionTests(unittest.TestCase):
    def test_append_only_main_objects_and_original_batches(self):
        old, now = before('data/games.json'), read('data/games.json')
        ids = {f'g{i}' for i in range(1310, 1320)}
        for key, suffix in [('works', ''), ('contentVersions', '-c-original'), ('platformReleases', '-v1')]:
            baseline = {w['id']: w for w in old[key]}
            current = {w['id']: w for w in now[key]}
            self.assertEqual({i: current[i] for i in baseline}, baseline)
            self.assertEqual(set(current) - set(baseline), {i + suffix for i in ids})
        added = [r for r in now['platformReleases'] if r['workId'] in ids]
        self.assertTrue(all(r['contentRelation'] == 'original' and r['releaseRole'] == 'contentDebut' for r in added))
        self.assertEqual({r['publisher'] for r in added if int(r['workId'][1:]) >= 1314}, {'徳間書店'})

    def test_types_and_source_uncertainties_survive_rendering(self):
        works = {w['id']: w for w in read('data/games.json')['works']}
        self.assertEqual(works['g1311']['interactionModes'], ['直接移动'])
        self.assertEqual(works['g1312']['interactionModes'], ['菜单指令'])
        for i in range(1314, 1320):
            w = works[f'g{i}']
            self.assertEqual(w['subcategory'], '互动漫画')
            self.assertIn('阅读推进', w['interactionModes'])
            self.assertNotIn('选项分支', w['interactionModes'])
            self.assertNotIn('战术策略', w['interactionModes'])
        page = (ROOT / 'tokuma_intermedia.html').read_text()
        self.assertEqual(page.count('<article class="card"'), 26)
        self.assertIn('tokuma.html#tokuma-filena', page)
        self.assertIn('1998为日期异文', page)
        self.assertIn('id="gameplay-catalogue"', page)

    def test_shared_identities_reference_only_tools_and_bibliography(self):
        d = next(c for c in read('data/company-coverage.json')['companies'] if c['id'] == 'tokuma_intermedia')
        self.assertEqual(len(d['workIds']), 18)
        self.assertEqual(len(d['relatedGames']), 7)
        b = d['dossierOnlyWorks'][0]
        self.assertEqual(b['firstYear'], 1984)
        self.assertNotIn('platformReleases', b)
        rows = [r for g in read('data/gameplay-catalogues.json')['companies']['tokuma_intermedia']['groups'] for r in g['rows']]
        self.assertEqual(len(rows), 73)
        shared = [r for r in rows if r.get('catalogueDossierId') == 'tokuma']
        self.assertEqual({r['catalogueWorkId'] for r in shared}, {'tokuma-filena', 'tokuma-lovequest', 'tokuma-littlemaster3'})
        for r in rows:
            if 'workId' not in r:
                self.assertNotIn('platformReleases', r)
                self.assertNotIn('contentVersions', r)

    def test_no_rewriting_old_entities_relations_or_company_development(self):
        old, now = before('data/entities.json'), read('data/entities.json')
        expected = old['entities']
        intermedia = next(e for e in expected if e['id'] == 'entity-name-9832231b6baa')
        intermedia['aliases'].insert(2, 'テクノポリスソフト')
        self.assertEqual(now['entities'], expected)
        self.assertEqual(now['relations'], old['relations'])
        old, now = before('data/credits.json'), read('data/credits.json')
        baseline = {c['id']: c for c in old['credits']}
        current = {c['id']: c for c in now['credits']}
        self.assertEqual({i: current[i] for i in baseline}, baseline)
        added = [c for i, c in current.items() if i not in baseline]
        self.assertTrue(added)
        self.assertEqual({c['role'] for c in added}, {'publisher'})
