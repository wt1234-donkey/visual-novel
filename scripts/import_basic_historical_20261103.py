#!/usr/bin/env python3
"""Append a small, source-reviewed 1970–1999 narrative-game batch."""
import argparse
import copy
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import import_basic_r142_r143_20261103 as prior

ROOT = Path(__file__).resolve().parents[1]
BASE = '1a826c30b36c4355364f4bc807e08426278c6903'
INPUT = ROOT / 'data/historical-narrative-intake-20261103.json'
AUDIT = ROOT / 'data/basic-historical-review-20261103-r144.json'
REPORT = ROOT / 'data/basic-historical-audit-summary-20261103.md'
REG = prior.e.REG
BATCH = 'historical-narrative-20261103-r144'


def original_registry():
    return json.loads(subprocess.check_output(
        ['git', 'show', BASE + ':' + str(REG.relative_to(ROOT))], cwd=ROOT))


def without_article(text):
    return prior.e.norm(re.sub(r'^(?:the|a|an)\s+', '', text, flags=re.I))


def build():
    source = prior.e.load(INPUT)
    assert source['schema'] == 1 and source['date'] == '2026-11-03'
    original = original_registry()
    registry = copy.deepcopy(original)
    index = prior.name_index(registry)
    refs = defaultdict(set)
    for key, values in prior.e.full_refs(registry).items():
        refs[key.casefold()].update(values)
    # The article-free lookup blocks a second identity such as "House of Seven
    # Gables" beside the existing "The House of Seven Gables".
    article_index = defaultdict(set)
    for work in prior.e.catalogue.all_works(registry):
        for name in prior.e.split_names(work):
            article_index[without_article(name)].add(
                (work['id'], int(work.get('firstYear') or work.get('year') or 0), 'full-catalogue'))
    seen_ids = set()
    reviewed = []
    for row in source['candidates']:
        mid = str(row['mobyId'])
        assert mid not in seen_ids
        seen_ids.add(mid)
        assert 1970 <= row['firstYear'] <= 1999 and row['gameplay'] == 'ADV'
        assert row['source'].startswith('https://www.mobygames.com/game/' + mid + '/')
        source_refs = ['mobygames:' + mid]
        if row['wikidataId']:
            source_refs.append('wikidata:' + row['wikidataId'])
        if row.get('additionalSource'):
            source_refs.append('source-url:' + row['additionalSource'])
        candidate = {'title': row['title'], 'aliases': row['aliases'],
                     'firstYear': row['firstYear'], 'source': row['source'],
                     'sourceRefs': source_refs}
        decision = prior.decide(candidate, index, refs)
        article_hits = set().union(*(article_index.get(without_article(name), set())
                                     for name in [row['title'], *row['aliases']]))
        status = decision or ('article-title-collision-held' if article_hits else None)
        # A same-title 2024 visual novel is demonstrably a different work from
        # Gary Kleppe's 1978 mainframe text adventure; retain the collision.
        if mid == '220274':
            assert status == 'name-year-or-multiple-identity-held'
            assert candidate['matchedWorkIds'] == ['vndb-v51225']
            assert row['firstYear'] == 1978 and row.get('additionalSource')
            status = None
            candidate['identityDisambiguation'] = (
                '与 vndb-v51225（2024）的同名冲突已核：1978 年 Gary Kleppe '
                '主机文字冒险有独立来源和不同的年代、作者及交互形式。')
        if mid == '27710':
            assert status == 'possible-title-variant-held'
            assert candidate['matchedWorkIds'] == ['mobygames-16590']
            assert row['firstYear'] == 1989
            status = None
            candidate['identityDisambiguation'] = (
                'Chrono Quest II / Explora II 是 1989 年独立续作；'
                '与 1988 年 Chrono Quest / Explora: Time Run 的前缀相似已核。')
        record = copy.deepcopy(row)
        record.update(candidate)
        if status:
            record['status'] = status
            reviewed.append(record)
            continue
        work = {
            'id': 'mobygames-' + mid,
            'indexId': 'basic-' + BATCH + '-mobygames-' + mid,
            'title': row['title'], 'aliases': row['aliases'],
            'firstYear': row['firstYear'], 'gameplay': row['gameplay'],
            'gameplayNote': '来源记载为' + row['kind'] + '；' + row['note'],
            'group': '创作主体待核', 'source': row['source'],
            'sourceRefs': source_refs, 'mainPlacement': 'promoted-basic',
            'linkedRecordId': None,
            'creditScope': '未根据发行方或平台推定开发职责。',
            'yearBasis': 'MobyGames作品页列示的最早发行年；历史别名及跨来源年份另作逐项核对。',
            'editorialScope': '仅补基础作品身份及来源；不按移植、合集、重制或平台拆分作品。',
            'batch': BATCH,
        }
        assert work['id'] not in {w['id'] for w in registry['works']}
        registry['works'].append(work)
        prior.e.reserve(work, index, refs)
        for name in prior.e.split_names(work):
            key = prior.e.norm(name)
            article_index[without_article(name)].add((work['id'], row['firstYear'], 'new'))
            if len(key) >= 8:
                index.prefixes[key[:8]].add(key)
        record.update(status='promoted-basic', workId=work['id'])
        reviewed.append(record)
    count = len(registry['works']) - len(original['works'])
    assert 0 < count <= 500
    assert registry['works'][:len(original['works'])] == original['works']
    for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
        registry['summary'][key] += count
    dispositions = Counter(r['status'] for r in reviewed)
    by_decade = Counter((r['firstYear'] // 10) * 10 for r in reviewed if r['status'] == 'promoted-basic')
    summary = {'candidates': count, 'promoted-basic': count,
               'addedToMainIdentityLayer': count,
               'scannedRecords': len(reviewed), 'newDistinctWorks': count,
               'before': len(original['works']), 'after': len(registry['works']),
               'dispositions': dict(dispositions),
               'newByDecade': {str(k): v for k, v in sorted(by_decade.items())}}
    registry['batches'].append({'id': BATCH,
        'source': ['https://www.mobygames.com/', 'https://solutionarchive.com/',
                   'https://www.wikidata.org/'],
        'review': str(AUDIT.relative_to(ROOT)), 'summary': summary})
    assert registry['summary']['accepted'] == len(registry['works'])
    audit = {'schema': 1, 'date': '2026-11-03', 'baseCommit': BASE,
             'sourceInput': str(INPUT.relative_to(ROOT)), 'summary': summary,
             'records': reviewed,
             'heldForLater': [
                 {'title': 'Lords of Karma', 'reason': 'CASA记1978，MobyGames首发记1981，未判定最早独立发行。'},
                 {'title': 'Mortville Manor', 'reason': '前轮Wikidata候选记1987，MobyGames作品页记1986，须复核首发。'},
                 {'title': 'The 11th Hour', 'reason': '来源称谜题为主体，叙事主导程度待核。'},
                 {'title': 'Tex Murphy: Overseer', 'reason': '与Mean Streets的重述和内容关系待核，不自动建立独立作品。'},
             ]}
    lines = ['# 1970—1990年代叙事作品补录：第144批', '',
             f'基线 `{BASE}`：基础身份总清单 {summary["before"]:,} 部；本批逐项审查 {len(reviewed)} 部，'
             f'新增 {count} 部，合计 {summary["after"]:,} 部。基础新增层 '
             f'{original["summary"]["promotedBasic"]:,} → {registry["summary"]["promotedBasic"]:,}。', '',
             '|年代|实际新增|', '|---|---:|']
    for decade, value in sorted(by_decade.items()):
        lines.append(f'|{decade}年代|{value}|')
    lines += ['', '来源：已冻结的逐项候选清单、MobyGames作品页及具名CASA历史页面；'
              '前轮Wikidata历史候选仅用于发现和外部ID关联。没有从VNDB、NextMoe或PC-98目录采集。',
              '仅保留名称、别名、原作年与玩法依据；来源中的平台移植和后续版本不另建作品。',
              '同名跨年案例 Underground（1978）具名人工核对；'
              'Lords of Karma、Mortville Manor 等冲突和边界案例继续隔离。',
              '每条来源URL、原作年、玩法及其处置见审计JSON。', '']
    return original, registry, audit, '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    original, expected, audit, report = build()
    if args.check:
        assert prior.e.load(REG) == expected
        assert prior.e.load(AUDIT) == audit
        assert REPORT.read_text(encoding='utf-8') == report
        print('HISTORICAL_BASIC_CHECK_OK', len(original['works']), len(expected['works']))
    else:
        assert prior.e.load(REG) in (original, expected), 'Registry changed; refusing overwrite'
        prior.e.save(REG, expected)
        prior.e.save(AUDIT, audit)
        REPORT.write_text(report, encoding='utf-8')
        print('HISTORICAL_BASIC_WRITTEN', len(original['works']), len(expected['works']))


if __name__ == '__main__':
    main()
