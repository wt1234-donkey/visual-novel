"""JHV content backfill reuses work and release identities and keeps attribution scoped."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from jhv_content_review import historical_record, validate_review

BASE = 'c91cb9841d664813130616598cf4e43e0992679e'
def read(path): return json.loads((ROOT / path).read_text())
def old(path): return json.loads(subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT))


class JHVCompletionTests(unittest.TestCase):
    def test_no_duplicate_work_or_release_and_only_reviewed_links_change(self):
        before, after = old('data/games.json'), read('data/games.json')
        self.assertEqual(before['works'], after['works'])
        self.assertEqual(before['platformReleases'], [historical_record('platformReleases', r) for r in after['platformReleases']])
        additions = [c for c in after['contentVersions'] if c['id'] not in {c['id'] for c in before['contentVersions']}]
        self.assertEqual({c['id'] for c in additions}, {'g830-c-final', 'g831-c-special'})
        self.assertEqual([c for c in after['contentVersions'] if c not in additions], before['contentVersions'])
        for path in ['data/content-migration-baseline.json', 'data/entity-migration-baseline.json', 'data/entities.json', 'data/credits.json']:
            self.assertEqual(read(path), old(path), path)

    def test_review_rejects_unreviewed_publisher_or_content_edits(self):
        row = next(r for r in read('data/games.json')['platformReleases'] if r['id'] == 'g830-v6')
        for field, value in [('publisher', 'JHV'), ('year', 1995), ('contentVersionId', 'g830-c-original')]:
            bad = {**row, field: value}
            with self.assertRaises(AssertionError): historical_record('platformReleases', bad)
        validate_review(read('data/games.json'), read('data/company-coverage.json'))

    def test_compilation_reuses_two_originals_and_cd_platforms_share_one_content(self):
        data, coverage = read('data/games.json'), read('data/company-coverage.json')
        for wid in ['g830', 'g831']:
            release = next(r for r in data['platformReleases'] if r['id'] == wid + '-v9')
            self.assertEqual((release['contentRelation'], release['contentVersionId']), ('same', wid + '-c-original'))
            self.assertEqual(release['publisherCompanies'], ['IRIコマース&テクノロジー'])
        before = old('data/company-coverage.json')
        self.assertEqual([c for c in coverage['companies'] if c['id'] != 'jhv'], [c for c in before['companies'] if c['id'] != 'jhv'])
        jhv = next(c for c in coverage['companies'] if c['id'] == 'jhv')
        self.assertEqual(jhv['workIds'], ['g830', 'g831', 'g832', 'g833', 'g834'])
        self.assertEqual(len(jhv['relatedGames']), 4)
        star = next(w for w in jhv['relatedGames'] if w['id'] == 'jhv-star2')
        self.assertEqual(len(star['contentVersions']), 2)
        self.assertEqual(len(star['platformReleases']), 3)
        self.assertEqual({r['contentVersionId'] for r in star['platformReleases'][1:]}, {'jhv-star2-c-cd'})
        self.assertEqual([historical_record('platformReleases', r) for r in star['platformReleases']], next(w for c in before['companies'] if c['id'] == 'jhv' for w in c['relatedGames'] if w['id'] == 'jhv-star2')['platformReleases'])

    def test_visible_page_and_recovered_list_report_actual_scope(self):
        page = (ROOT / 'jhv.html').read_text()
        self.assertEqual(page.count('<article class="card"'), 9)
        for cid in ['g830-c-final', 'g831-c-special', 'jhv-star2-c-cd']: self.assertIn(cid, page)
        review = read('data/jhv-content-review-20261029.json')
        self.assertEqual(sum(r['decision'] == 'reuse' for r in review['rows']), 9)
        self.assertEqual({r['decision'] for r in review['rows']}, {'reuse', 'defer', 'referenceOnly', 'noAutomaticAttribution'})
        self.assertIn('未取得原始表格', review['sourceListRecovery'])
