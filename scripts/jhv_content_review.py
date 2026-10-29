"""Validate the six explicitly reviewed JHV content links without rebasing history."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEW = json.loads((ROOT / 'data/jhv-content-review-20261029.json').read_text())
FIELDS = {'contentVersionId', 'contentRelation', 'contentNote'}
MAIN_IDS = {'g830-v6', 'g831-v6', 'g830-v9', 'g831-v9'}
RELATED_IDS = {'jhv-star2-v2', 'jhv-star2-v3'}
RECORDS = {r['releaseId']: r for r in REVIEW['releaseReviews']}
assert set(RECORDS) == MAIN_IDS | RELATED_IDS and len(RECORDS) == len(REVIEW['releaseReviews'])


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


def historical_record(field, row):
    """Restore only reviewed link fields when checking the unchanged historical hash."""
    if field != 'platformReleases' or row['id'] not in RECORDS:
        return row
    record = RECORDS[row['id']]
    assert set(record['before']) == set(record['after']) == FIELDS
    assert record['source'] and record['reason'] and row['workId'] == record['workId']
    assert {k: row[k] for k in FIELDS} == record['after'], 'JHV内容关联偏离具名审核'
    restored = {**row, **record['before']}
    assert digest(restored) == record['beforeObjectSha256'], 'JHV历史发行原文或署名被改写'
    return restored


def validate_review(data, coverage):
    releases = {r['id']: r for r in data['platformReleases']}
    contents = {c['id']: c for c in data['contentVersions']}
    jhv = next(c for c in coverage['companies'] if c['id'] == 'jhv')
    for work in jhv['relatedGames']:
        releases.update((r['id'], r) for r in work['platformReleases'])
        contents.update((c['id'], c) for c in work['contentVersions'])
    for rid, record in RECORDS.items():
        historical_record('platformReleases', releases[rid])
        content = contents[record['after']['contentVersionId']]
        assert content['workId'] == record['workId']
        assert record['scope'] == ('main' if rid in MAIN_IDS else 'related')
        if record['after']['contentRelation'] == 'added':
            assert content['basis'] == 'added' and rid in content['evidenceReleaseIds']
            assert content['source'] == record['source']
        else:
            assert record['after']['contentRelation'] == 'same' and content['basis'] == 'original'
