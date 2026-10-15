import copy
import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from content_model import validate_collection, validate_content_model

DATA = json.loads((ROOT / 'data/games.json').read_text())
COVERAGE = json.loads((ROOT / 'data/company-coverage.json').read_text())
BASELINE = json.loads((ROOT / 'data/content-migration-baseline.json').read_text())


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


class ContentModelTests(unittest.TestCase):
    def test_all_historical_fields_and_sources_survive(self):
        current = {w['id']: digest(w) for w in DATA['works']}
        self.assertEqual({wid: current.get(wid) for wid in BASELINE['works']}, BASELINE['works'])
        self.assertTrue(set(BASELINE['releases']) <= {r['id'] for r in DATA['platformReleases']})
        for r in DATA['platformReleases']:
            if r['id'] not in BASELINE['releases']:
                continue
            b = BASELINE['releases'][r['id']]
            self.assertEqual(digest({key: r[key] for key in b['keys']}), b['sha256'], r['id'])
        for company in COVERAGE['companies']:
            for work in company.get('relatedGames', []):
                old = {k: v for k, v in work.items() if k not in {'contentVersions', 'platformReleases'}}
                if work['id'] in BASELINE['relatedWorks']:
                    self.assertEqual(digest(old), BASELINE['relatedWorks'][work['id']])
                for r in work['platformReleases']:
                    if r['id'] not in BASELINE['relatedReleases']:
                        continue
                    b = BASELINE['relatedReleases'][r['id']]
                    self.assertEqual(digest({key: r[key] for key in b['keys']}), b['sha256'], r['id'])

    def test_entire_model_has_no_dangling_or_cross_work_links(self):
        validate_content_model(DATA, COVERAGE)
        for c in DATA['contentVersions']:
            self.assertFalse({'platform', 'publisher', 'publisherCompanies'} & c.keys())

    def test_multi_platform_new_content_counts_once(self):
        for ids in [('g055-v2', 'g055-v3', 'g055-v4'),
                    ('g054-v20', 'g054-v21', 'g054-v22', 'g054-v23'),
                    ('g901-v5', 'g901-v6', 'g901-v7')]:
            rows = [r for r in DATA['platformReleases'] if r['id'] in ids]
            self.assertEqual(len(rows), len(ids))
            self.assertEqual(len({r['contentVersionId'] for r in rows}), 1)
            self.assertIsNotNone(rows[0]['contentVersionId'])

    def test_unknown_port_is_not_asserted_identical_or_new(self):
        r = next(r for r in DATA['platformReleases'] if r['id'] == 'g211-v2')
        self.assertEqual(r['contentRelation'], 'unverified')
        self.assertIsNone(r['contentVersionId'])

    def sample(self):
        wid = 'g089'
        return copy.deepcopy(([w for w in DATA['works'] if w['id'] == wid],
                              [c for c in DATA['contentVersions'] if c['workId'] == wid],
                              [r for r in DATA['platformReleases'] if r['workId'] == wid]))

    def test_new_unverified_release_cannot_claim_legacy_exception(self):
        works, contents, releases = self.sample()
        new = copy.deepcopy(releases[-1]);new['id'] = 'new-port';releases.append(new)
        with self.assertRaises(AssertionError):
            validate_collection(works, contents, releases, BASELINE['releases'])

    def test_new_later_port_cannot_be_a_content_debut(self):
        works, contents, releases = self.sample()
        new = copy.deepcopy(releases[0])
        new.update(id='new-port', year=2026, releaseRole='contentDebut')
        releases.append(new)
        with self.assertRaises(AssertionError):
            validate_collection(works, contents, releases, BASELINE['releases'])

    def test_new_content_requires_concrete_delta_and_comparison(self):
        works, contents, releases = self.sample()
        contents[1]['addedContent'] = []
        with self.assertRaises(AssertionError):
            validate_collection(works, contents, releases, BASELINE['releases'])

    def test_separate_csv_exports_match_json(self):
        from export_content_csv import content_rows, csv_text
        self.assertEqual((ROOT / 'data/content-versions.csv').read_text(encoding='utf-8-sig'),
                         csv_text(content_rows(DATA)))
        self.assertEqual((ROOT / 'data/platform-releases.csv').read_bytes(),
                         (ROOT / 'data/versions.csv').read_bytes())


if __name__ == '__main__':
    unittest.main()
