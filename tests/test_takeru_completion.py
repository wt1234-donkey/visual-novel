"""TAKERU channel completion: identity preservation and content admission boundaries."""
import copy
import json
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASE = 'a4cdcae0cc5cba9ab93f2f475ca8ea74768b4eef'

def current(path):
    return json.loads((ROOT / path).read_text())

def prior(path):
    return json.loads(subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT))

def completed(path):
    """Freeze the scope comparison at the reviewed TAKERU publication."""
    return json.loads(subprocess.check_output(['git', 'show', f'cde23e0121b2458e986cff9eaa519b4ef591d843:{path}'], cwd=ROOT))

class TakeruCompletionTests(unittest.TestCase):
    def test_old_main_objects_and_migration_baselines_are_preserved(self):
        before, after = prior('data/games.json'), completed('data/games.json')
        for key in ['works', 'contentVersions', 'platformReleases']:
            lookup = {x['id']: x for x in after[key]}
            self.assertTrue(all(lookup[x['id']] == x for x in before[key]), key)
        self.assertEqual({w['id'] for w in after['works']} - {w['id'] for w in before['works']}, {'g1307','g1308','g1309'})
        for path in ['data/entity-migration-baseline.json', 'data/content-migration-baseline.json']:
            self.assertEqual(current(path), prior(path))

    def test_narrative_admission_and_later_publisher_scope(self):
        data = current('data/games.json')
        works = {w['id']: w for w in data['works']}
        self.assertEqual(works['g1308']['interactionModes'], ['菜单指令'])
        self.assertIn('截图', works['g1308']['interactionNote'])
        self.assertNotIn('战斗指令', works['g1307']['interactionModes'])
        releases = [r for r in data['platformReleases'] if r['workId'] == 'g1309']
        self.assertEqual([(r['year'],r['publisher']) for r in releases], [(1991,'TAKERU'),(2023,'D4 Enterprise')])
        content = next(c for c in data['contentVersions'] if c['id']=='g1309-c-refined')
        self.assertEqual(content['comparedTo'], 'g1309-c-original')
        self.assertIn('九话', content['addedContent'][0]['description'])

    def test_sorcerian_is_one_old_work_with_seven_new_content_records(self):
        old_cov, cov = prior('data/company-coverage.json'), current('data/company-coverage.json')
        def sor(c):
            return next(w for co in c['companies'] for w in co.get('relatedGames',[]) if w['id']=='sierra-on-line-sorcerian')
        old, new = sor(old_cov), sor(cov)
        self.assertEqual({k:v for k,v in new.items() if k not in {'contentVersions','platformReleases'}}, {k:v for k,v in old.items() if k not in {'contentVersions','platformReleases'}})
        self.assertEqual(new['contentVersions'][:len(old['contentVersions'])], old['contentVersions'])
        self.assertEqual(new['platformReleases'][:len(old['platformReleases'])], old['platformReleases'])
        self.assertEqual(len(new['contentVersions'])-len(old['contentVersions']), 7)
        self.assertEqual(len(new['platformReleases'])-len(old['platformReleases']), 10)
        for c in new['contentVersions'][len(old['contentVersions']):]:
            self.assertEqual(c['basis'], 'added')
            self.assertTrue(c['addedContent'])
        self.assertFalse(any(w['originalTitle']=='Sorcerian' for w in current('data/games.json')['works']))

    def test_catalogue_rows_link_shared_identities_and_do_not_admit_tools(self):
        cov = current('data/company-coverage.json')
        t = next(c for c in cov['companies'] if c['id']=='takeru')
        self.assertEqual(len(t['workIds']), 8)
        self.assertEqual(len(t['relatedGames']), 3)
        self.assertEqual(t['dossierOnlyWorks'][0]['id'], 'takeru-madeline')
        self.assertEqual(t['dossierOnlyWorks'][0]['interactionModes'], ['文字输入'])
        groups = current('data/gameplay-catalogues.json')['companies']['takeru']['groups']
        self.assertEqual([len(g['rows']) for g in groups], [8,3,7,31,15,1])
        page = (ROOT/'takeru.html').read_text()
        self.assertIn('sierra_on_line.html#sierra-on-line-sorcerian',page)
        self.assertIn('microcabin.html#microcabin-xak2',page)
        self.assertEqual(page.count('<article class="card"'),12)
        self.assertIn('65个清单项目',page)
        self.assertFalse(any('データバンク' in w['title'] for w in current('data/games.json')['works']))

    def test_no_other_dossier_data_changed(self):
        before, after = prior('data/company-coverage.json'), completed('data/company-coverage.json')
        b = {c['id']:c for c in before['companies']}
        a = {c['id']:c for c in after['companies']}
        self.assertEqual(set(a),set(b))
        for cid in set(b)-{'takeru','sierra_on_line'}:
            self.assertEqual(a[cid],b[cid],cid)
        old_gameplay = prior('data/gameplay-catalogues.json')
        new_gameplay = copy.deepcopy(completed('data/gameplay-catalogues.json'))
        new_gameplay['companies'].pop('takeru')
        self.assertEqual(new_gameplay,old_gameplay)
