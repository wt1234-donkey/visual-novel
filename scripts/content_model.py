"""Shared validation for content identities and their platform releases."""
import json
from pathlib import Path
from source_urls import source_url_valid

ROOT = Path(__file__).resolve().parents[1]


def validate_collection(works, contents, releases, legacy_ids=()):
    work_map = {w['id']: w for w in works}
    content_map = {c['id']: c for c in contents}
    release_map = {r['id']: r for r in releases}
    assert len(content_map) == len(contents), '内容版本 ID 重复'
    assert len(release_map) == len(releases), '平台发行 ID 重复'
    for c in contents:
        assert c['workId'] in work_map and c['label'] and source_url_valid(c['source'])
        assert c['basis'] in {'original', 'added'}
        assert isinstance(c['firstYear'], int) and work_map[c['workId']]['firstYear'] <= c['firstYear'] <= 2026
        assert c['evidence'] and c['evidenceReleaseIds'], '内容版本必须有证据与首次发行依据'
        assert all(rid in release_map and release_map[rid]['workId'] == c['workId']
                   and release_map[rid]['contentVersionId'] == c['id'] for rid in c['evidenceReleaseIds']), '内容证据指向其他作品或版本'
        linked = [r for r in releases if r['contentVersionId'] == c['id']]
        assert linked and min(r['year'] for r in linked) == c['firstYear'], '内容首次年份不能取后发移植年份'
        if c['basis'] == 'added':
            prior = content_map.get(c.get('comparedTo'))
            assert prior and prior['workId'] == c['workId'] and prior['id'] != c['id'] and prior['firstYear'] <= c['firstYear'], '新增内容必须指定同作品比较对象'
            assert c['addedContent'] and all(len(a['description'].strip()) >= 10 and source_url_valid(a['source'])
                                             for a in c['addedContent']), '新增内容必须具体说明增量与来源'
        else:
            assert c['firstYear'] == work_map[c['workId']]['firstYear'] and not c['addedContent']
    for w in works:
        assert sum(c['workId'] == w['id'] and c['basis'] == 'original' for c in contents) == 1, '每部作品只建一个原作内容记录'
    for r in releases:
        assert r['workId'] in work_map and r['contentRelation'] in {'original', 'added', 'same', 'unverified'}
        assert r['contentNote'] and r['releaseRole'] in {'legacy', 'contentDebut'}
        cid = r['contentVersionId']
        if cid is None:
            assert r['contentRelation'] == 'unverified', '未核关系不能自动当作同内容'
        else:
            c = content_map.get(cid)
            assert c and c['workId'] == r['workId'] and r['year'] >= c['firstYear'], '平台发行引用不存在、跨作品或未来内容'
            assert r['contentRelation'] != 'unverified'
            if r['contentRelation'] in {'original', 'added'}:
                assert c['basis'] == r['contentRelation']
        if r['id'] not in legacy_ids:
            assert cid and r['releaseRole'] == 'contentDebut', '以后只录原作／新增内容的首次发行批次，不补纯平台移植'
            assert r['year'] == content_map[cid]['firstYear'], '后发同内容平台发行不应新增为内容首发'


def validate_content_model(data, coverage):
    baseline = json.loads((ROOT / 'data/content-migration-baseline.json').read_text())
    assert data['meta']['schemaVersion'] == 2 and 'versions' not in data
    assert data['meta']['repository'] == 'wt1234-donkey/visual-novel'
    validate_collection(data['works'], data['contentVersions'], data['platformReleases'], baseline['releases'])
    all_ids = {r['id'] for r in data['platformReleases']}
    for company in coverage['companies']:
        for work in company.get('relatedGames', []):
            assert 'versions' not in work
            validate_collection([work], work['contentVersions'], work['platformReleases'], baseline['relatedReleases'])
            ids = {r['id'] for r in work['platformReleases']}
            assert not ids & all_ids, '主库与专题发行ID冲突'
            all_ids.update(ids)
