"""Validate catalogue relationships and the exported CSV."""

import csv
import json
from pathlib import Path
from source_urls import source_url_valid

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'data/games.json').read_text(encoding='utf-8'))
taxonomy = json.loads((ROOT / 'data/taxonomy.json').read_text(encoding='utf-8'))
coverage = json.loads((ROOT / 'data/company-coverage.json').read_text(encoding='utf-8'))
command_work_ids = {wid for company in coverage['companies']
                    if company['id'] in {'alicesoft', 'nitroplus'} and company.get('includeCommandGames') is True
                    for wid in company['workIds']}
command_work_ids.update(wid for company in coverage['companies']
                        for wid in company.get('legacyCommandWorkIds', []))
command_work_ids.update(wid for company in coverage['companies']
                        for wid in company.get('authorizedCommandWorkIds', []))
from content_model import validate_content_model
validate_content_model(data, coverage)
works, versions = data['works'], data['platformReleases']

def validate_edition_credits(work):
    credits = work.get('editionCredits', [])
    assert len(credits) == len({(x['year'], x['platform'], x['publisher']) for x in credits}), '发行关系重复'
    assert all(work['firstYear'] <= x['year'] <= 2026 and x['platform'] and x['publisher']
               and x['reason'] and source_url_valid(x['source']) for x in credits), '发行关系字段不完整或早于原作'

work_ids = {work['id'] for work in works}
version_ids = {version['id'] for version in versions}
assert len(work_ids) == len(works) and len(version_ids) == len(versions), '重复 ID'
assert {work['category'] for work in works} == {'文字冒险', '视觉小说', '互动动画', 'Galgame'}
assert set(taxonomy['subcategories']) == {work['category'] for work in works}
assert all(work['subcategory'] in taxonomy['subcategories'][work['category']] for work in works)
assert all(work['subcategory'] not in {'纯文本指令', '图文指令'}
           for work in works if int(work['id'][1:]) >= 152 and work['id'] not in command_work_ids), '新增指令冒险须有具名授权或已授权完整目录范围'
assert all(any(work['subcategory'] == value for work in works) for category in taxonomy['subcategories']
           for value in taxonomy['subcategories'][category]), '存在空的细分类'
assert all(1976 <= version['year'] <= 2026 and version['workId'] in work_ids for version in versions)
assert all(version['publisher'] and version['platform'] and source_url_valid(version['source'])
           and version['voice'] in {'有', '无', '未核实', '有（部分）', '有（主角部分）'} for version in versions)
for version in versions:
    companies = version['publisherCompanies']
    assert isinstance(companies, list) and all(isinstance(c, str) and c for c in companies)
    assert len(companies) == len(set(companies))
    raw = version['publisher']
    if raw in taxonomy['nonCompanyCredits']:
        assert companies == [], f'{version["id"]} 作者传播不应归入商业厂商'
    elif raw in taxonomy['jointCredits']:
        assert companies == taxonomy['jointCredits'][raw], f'{version["id"]} 联名发行厂商不一致'
    else:
        assert companies == [taxonomy['publisherAliases'].get(raw, raw)], f'{version["id"]} 厂商别名不一致'
assert all(source_url_valid(work['source']) and isinstance(work['characters'], list)
           and work['characters'] and all(name and '待核实' not in name for name in work['characters'])
           and work['genre'] for work in works), '每部作品必须有可显示的角色或原作身份'
assert all(not work.get('charactersNote', '').find('待核实') >= 0 for work in works)
assert all(isinstance(work.get('chineseTitle', ''), str) and
           isinstance(work.get('titleAliases', []), list) for work in works)
assert all(work.get('chineseTitleType', '通行译名') in {'通行译名', '站内编辑译名'}
           and (not work.get('chineseTitleType') or work.get('chineseTitle')) for work in works)
for work in works:
    validate_edition_credits(work)
    if 'releaseContext' in work:
        assert work['releaseContext'] in {'standalone', 'bundledSample', 'associatedPublisher'}
        assert bool(work.get('bundledWith')) == (work['releaseContext'] == 'bundledSample'), '附带小说缺少所属产品或身份不一致'
    years = [version['year'] for version in versions if version['workId'] == work['id']]
    assert years and min(years) == work['firstYear'], f"{work['title']} 首发年份与平台版本冲突"

with (ROOT / 'data/versions.csv').open(encoding='utf-8-sig', newline='') as file:
    rows = list(csv.DictReader(file))
assert len(rows) == len(versions), 'CSV 与 JSON 条数不一致'
assert len({row['发行ID'] for row in rows}) == len(rows), 'CSV 中版本 ID 重复'
for version, row in zip(versions, rows):
    assert row['内容版本ID'] == (version['contentVersionId'] or '')
    assert row['内容关系'] == version['contentRelation']
    assert row['内容核对说明'] == version['contentNote']
    work = next(work for work in works if work['id'] == version['workId'])
    assert row['作品ID'] == work['id'] and row['发行ID'] == version['id']
    assert row['作品名称'] == work['title'] and row['主分类'] == work['category']
    assert row['中文名称'] == work.get('chineseTitle', '')
    assert row['细分类'] == work['subcategory']
    assert row['游戏类型'] == work['genre']
    assert row['发行厂商归档'] == ('、'.join(version['publisherCompanies']) or '非商业／未署商业厂商')
    assert row['主要角色'] == '、'.join(work['characters'])
    assert str(version['year']) == row['发行年份']
    assert row['角色配音标注'] == ('无角色配音' if version['voice'] == '无' else '')
    for key, field in [('platform', '平台'), ('publisher', '发行公司'),
                       ('kind', '发行类型'),
                       ('differences', '发行备注'), ('source', '来源')]:
        assert version[key] == row[field], f"{version['id']} 的 {field} 与 JSON 不一致"
for company in coverage['companies']:
    profile = company['creativeProfile']
    assert profile['thesis'] and len(profile['phases']) >= 2
    assert all(p['period'] and p['heading'] and p['analysis'] and
               p['basis'] in {'厂商说明', '编辑观察'} and source_url_valid(p['source'])
               for p in profile['phases'])
    ids = company['workIds']
    assert len(ids) == len(set(ids)) and set(ids) <= work_ids, '厂商专题作品 ID 不正确'
    for field, context in [('bundledSampleWorkIds', 'bundledSample'),
                           ('associatedPublisherWorkIds', 'associatedPublisher')]:
        if field in company:
            scoped = company[field]
            assert len(scoped) == len(set(scoped)) and set(scoped) <= set(ids)
            assert set(scoped) == {w['id'] for w in works if w['id'] in ids and w.get('releaseContext') == context}, '厂商作品身份分组不一致'
    if 'publisherWorkIds' in company:
        credited = {version['workId'] for version in versions
                    if company['name'] in version['publisherCompanies'] and version['workId'] in ids}
        assert set(company['publisherWorkIds']) == credited, '厂商专题发行署名计数与版本记录不一致'
    related = company.get('relatedGames', [])
    related_ids = {game['id'] for game in related}
    assert len(related_ids) == len(related) and not related_ids & work_ids, '跨类型作品 ID 冲突'
    legacy_anchors = company.get('legacyAnchors', {})
    assert set(legacy_anchors.values()) <= set(ids), '旧作品链接缺少主库记录'
    assert not set(legacy_anchors) & (work_ids | related_ids), '转入主库的作品仍保留重复副本'
    for game in related:
        validate_edition_credits(game)
        assert source_url_valid(game['source']) and game['genre'] and game['characters']
        assert all(name and '待核实' not in name for name in game['characters'])
        assert game['category'] not in taxonomy['subcategories'], '跨类型游戏应放在四类主目录之外'
        assert game['platformReleases'] and min(v['year'] for v in game['platformReleases']) == game['firstYear']
        assert all(v['platform'] and v['publisher'] and v['differences'] and
                   source_url_valid(v['source']) and v['voice'] in {'有', '无', '未核实', '有（部分）'}
                   for v in game['platformReleases'])
    assert company['catalogueEntryCount'] <= len(company['entries'])
    covered, related_covered = set(), set()
    for entry in company['entries']:
        assert source_url_valid(entry['source']) and entry['reason']
        assert set(entry['workIds']) <= set(ids), '核对清单与专题作品不一致'
        assert set(entry.get('relatedIds', [])) <= related_ids, '核对清单的跨类型作品不存在'
        covered.update(entry['workIds'])
        related_covered.update(entry.get('relatedIds', []))
    assert covered == set(ids) and related_covered == related_ids, '专题存在缺少核对来源的作品'
    # Keep new, explicitly authorized command works separate from legacy references.
    authorized = company.get('authorizedCommandWorkIds', [])
    assert len(authorized) == len(set(authorized)), '具名指令冒险授权存在重复ID'
    assert set(authorized) <= set(ids), '具名指令冒险授权必须对应专题作品'
    assert not set(authorized) & set(company.get('legacyCommandWorkIds', [])), '新增授权与旧记录例外不能混用'
    if authorized:
        assert company.get('commandAuthorizationNote'), '具名指令冒险授权缺少范围说明'
        assert all(work['subcategory'] in {'纯文本指令', '图文指令'}
                   for work in works if work['id'] in set(authorized)), '授权清单应只包含指令冒险'
    if company['id'] in {'alicesoft', 'nitroplus'} and company.get('includeCommandGames') is True:
        allowed_command_ids = set(ids)
    else:
        allowed_command_ids = set(company.get('legacyCommandWorkIds', []))
        assert allowed_command_ids <= set(ids), '旧指令冒险例外必须对应专题已有作品'
        allowed_command_ids.update(authorized)
    assert all(work['subcategory'] not in {'纯文本指令', '图文指令'}
               for work in works if work['id'] in set(ids) - allowed_command_ids)
print(f"校验通过：{len(works)} 部作品，{len(data['contentVersions'])} 个内容版本，{len(versions)} 条平台发行；厂商专题引用一致")
