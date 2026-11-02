#!/usr/bin/env python3
"""Rounds 132–133: recheck 50 VNDB + 0 NextMoe candidates, then resume three sources."""
import sys
import argparse
import datetime as dt
import json
import re
import subprocess
from collections import defaultdict

import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE = 'f1092fb405106ffe79fe7ee82cd0aa1b4b409d08'
    mixed.B60 = 'vndb-kana-bulk-20261102-r132'
    mixed.B61 = 'nextmoe-ifdb-bulk-20261102-r133'
    mixed.A60 = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r132.json'
    mixed.A61 = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r133.json'
    mixed.REPORT = mixed.e.ROOT / 'data/basic-r132-r133-diversity-20261102.json'
    mixed.SEED_VNDB = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r130.json'
    mixed.SEED_NEXTMOE = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r131.json'
    vndb = mixed.e.load(mixed.SEED_VNDB)
    nextmoe = mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd'] == 'v70299'
    assert len(vndb['deferredEligible']) == 50
    assert len(nextmoe['deferredEligible']) == 0
    assert len(vndb['deferredEligible']) + len(nextmoe['deferredEligible']) == 50
    last = next(row for row in reversed(nextmoe['summary']['paginationTrace']) if row['lane'] == 'era-keyset')
    assert last['nextCursor'] == 'cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNakk1TWpRM2ZR'
    assert (last['releasedAfter'], last['releasedBefore']) == ('2010-01-01', '2026-11-02')
    mixed.EXPECTED_VNDB_START = 'v70299'
    mixed.IFDB_START_POSITION = mixed.ifdb.resume_position(nextmoe['ifdbArchiveReview'])
    assert mixed.IFDB_START_POSITION == 9966
    assert mixed.NEXT_LIMIT == 300
    mixed.configure()


def report_text():
    """Reconcile every audit outcome and list all held source identities."""
    audits = [mixed.e.load(mixed.A60), mixed.e.load(mixed.A61)]
    groups = {}
    metrics = []
    for number, path, audit in zip((132, 133), (mixed.A60, mixed.A61), audits):
        summary = audit['summary']
        ifdb = audit.get('ifdbArchiveReview', {})
        scanned = summary['pendingInput'] + summary['liveScanned'] + ifdb.get('scanned', 0)
        reused = len(audit['reusedExisting'])
        held = len(audit['heldForIdentityReview'])
        deferred = len(audit['deferredEligible'])
        new = summary['newDistinctWorks']
        skipped = scanned - reused - held - deferred - new
        assert skipped >= 0
        assert len(audit['pendingQueueReview']) == summary['pendingInput']
        metrics.append((number, scanned, reused, new, held, skipped, deferred))
        for i, row in enumerate(audit['heldForIdentityReview']):
            key = 'vndb:' + row['vndbId'] if row.get('vndbId') else 'ifdb:' + row['sourceId']
            groups.setdefault(key, []).append((number, path.name, i, row))
    def cell(value):
        return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '\\|').replace('\n', ' ')
    def table_row(values):
        return '| ' + ' | '.join(cell(v) for v in values) + ' |'
    lines = ['# 第132、133批采集与隔离审计', '',
        '扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。', '',
        '| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |',
        '|---|---:|---:|---:|---:|---:|---:|']
    lines += [table_row(row) for row in metrics]
    first, second = audits
    selected = sum(a['summary']['selectedFromDeferred'] for a in audits)
    assert sum(a['summary']['pendingInput'] for a in audits) == 50
    lines += ['', '## 50条暂存处理', '', 
        f"VNDB输入50条、NextMoe输入0条；本轮从旧暂存入选{selected}条。逐条处理状态保存在两个审计文件的pendingQueueReview中。", '',
        f"基础身份库：{first['summary']['before']:,} → {second['summary']['after']:,}。", '',
        '## 新续采位置', '',
        '- VNDB：`' + first['summary']['cursorEnd'] + '`',
        '- NextMoe：`' + second['summary']['paginationTrace'][-1]['nextCursor'] + '`',
        '- IFDB：`' + str(second['ifdbArchiveReview']['nextPosition']) + '`（固定档案及原排序不变）', '',
        '## 年份、身份与疑似版本隔离清单', '',
        f"共{sum(len(a['heldForIdentityReview']) for a in audits)}条原始记录，按来源ID合并为{len(groups)}个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。", '',
        '| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |',
        '|---|---|---|---|---|---|---|']
    for key, entries in groups.items():
        rows = [entry[3] for entry in entries]
        reasons = list(dict.fromkeys(r.get('reason') or r.get('basis', '待核') for r in rows))
        category = '疑似版本/依赖内容' if any('edition' in r or 'dependent' in r for r in reasons) else '来源日期冲突' if any(r.get('nextmoeSourceReleased') for r in rows) else '名称/年份/身份冲突'
        dates = list(dict.fromkeys(str(r.get('sourceReleased') or r.get('published') or r.get('firstYear') or '原审计未提供') for r in rows))
        matches = list(dict.fromkeys(m[0] + ' (' + str(m[1]) + ')' for r in rows for m in r.get('matches', [])))
        matches += list(dict.fromkeys('NextMoe: ' + str(r['nextmoeSourceReleased']) for r in rows if r.get('nextmoeSourceReleased')))
        locators = [f"[{n}: {r['sourceId']} / held[{i}]]({p})" for n, p, i, r in entries]
        lines.append(table_row((category, key, rows[0].get('title', '名称未提供'), '; '.join(dates), '; '.join(matches) or '内容关系待核', '; '.join(reasons), '; '.join(locators))))

    lines += ['', '## NextMoe 连续批次有效产出评估', '',
        '下表仅统计NextMoe实时扫描，不混入IFDB档案扫描和旧暂存。入选不等于扫描候选总数。',
        '',
        '| 批次 | NextMoe扫描 | 新合格候选 | 合格率 | 最终选中NextMoe | IFDB补录 | 主要排除原因 |',
        '|---|---:|---:|---:|---:|---:|---|']
    for number, path in ((129, mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r129.json'),
                         (131, mixed.SEED_NEXTMOE), (133, mixed.A61)):
        audit = mixed.e.load(path)
        x = audit['summary']
        counts = x['nextmoeDispositions']
        source = x['sourceCounts']
        assert source['nextmoe'] + source['ifdb'] == 500
        scanned = x['liveScanned']
        eligible = x['liveEligible']
        assert scanned == eligible + sum(counts.values())
        major = ', '.join(f'{k}: {v}' for k, v in sorted(counts.items(), key=lambda z: -z[1])[:3])
        lines.append(table_row((number, scanned, eligible,
            f'{eligible / scanned * 100:.2f}%' if scanned else '未扫描',
            source['nextmoe'], source['ifdb'], major)))
    lines += ['', '注意：合格率指可进入候选池的比例，不是网站总作品质量评价。若NextMoe连续低产出，后续可调整扫描窗口或减少无效扫描，但不能跳过来源去重及历史游标。', '']
    lines += ['', '## 原始证据', '',
        '- [第132批审计](vndb-kana-bulk-review-20261102-r132.json)',
        '- [第133批审计](nextmoe-ifdb-bulk-review-20261102-r133.json)',
        '- [两批汇总](basic-r132-r133-diversity-20261102.json)', '',
        '测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。']
    return '\n'.join(lines) + '\n'



def flexible_check():
    """Validate an append-only batch when the VNDB cursor reaches its current end."""
    old = json.loads(subprocess.check_output(
        ['git', 'show', mixed.BASE + ':' + str(mixed.e.REG.relative_to(mixed.e.ROOT))],
        cwd=mixed.e.ROOT))
    current = mixed.e.load(mixed.e.REG)
    assert current['works'][:len(old['works'])] == old['works']
    assert current['batches'][:len(old['batches'])] == old['batches']
    assert current['updated'] == mixed.DATE
    for key in old:
        if key not in {'works', 'batches', 'summary', 'updated'}:
            assert current[key] == old[key]
    for path in mixed.e.source.PROTECTED:
        original = subprocess.check_output(['git', 'show', mixed.BASE + ':' + path], cwd=mixed.e.ROOT)
        assert original == (mixed.e.ROOT / path).read_bytes(), path
    assert subprocess.check_output(['git', 'show', mixed.BASE + ':data/vn-seven-source-date-review-20261101.json'],
        cwd=mixed.e.ROOT) == (mixed.e.ROOT / 'data/vn-seven-source-date-review-20261101.json').read_bytes()
    added = current['works'][len(old['works']):]
    audits = [mixed.e.load(mixed.A60), mixed.e.load(mixed.A61)]
    sizes = [a['summary']['newDistinctWorks'] for a in audits]
    assert all(0 < size <= 500 for size in sizes), sizes
    assert sum(sizes) == len(added)
    assert len(current['works']) == len({w['id'] for w in current['works']})
    assert len(current['works']) == len({w['indexId'] for w in current['works']})
    index = mixed.e.source.common.existing_index(old)
    refs = mixed.e.source.identity_map(old)
    folded = defaultdict(set)
    for ref, ids in refs.items():
        folded[ref.casefold()].update(ids)
    registered = {w['id'] for w in current['works']}
    deferred_ids = {r['work']['id'] for a in audits for r in a['deferredEligible']}
    for batch, audit in zip((mixed.B60, mixed.B61), audits):
        stats = audit['summary']
        rows = [w for w in added if w.get('batch') == batch]
        assert len(rows) == stats['newDistinctWorks'] == len(audit['records'])
        assert stats['selectedFromDeferred'] + stats['selectedFromLive'] == len(rows)
        assert len(audit['pendingQueueReview']) == stats['pendingInput']
        assert stats['selectedFromDeferred'] == sum(
            r['status'] == 'selected-from-deferred' for r in audit['pendingQueueReview'])
        assert stats['selectedFromDeferred'] == stats['pendingEligible']
        source_counts = stats.get('sourceCounts', {'vndb':len(rows)})
        assert sum(source_counts.values()) == len(rows)
        selected_next = source_counts.get('nextmoe', 0) if batch == mixed.B61 else len(rows)
        assert stats['pendingEligible'] + stats['liveEligible'] == (
            selected_next + len(audit['deferredEligible']))
        for event in audit['reusedExisting']:
            hits = set(event.get('matchedWorkIds', [])) | {
                x[0] for x in event.get('matches', [])}
            assert hits and hits <= registered | deferred_ids
        evidence = {r['id']:r for r in audit['records']}
        for work in rows:
            assert work['id'] in evidence
            row = evidence[work['id']]
            assert all(work[k] == row[k] for k in work)
            if row.get('sourceKind') == 'ifdb':
                assert work['id'] == 'ifdb-' + row['sourceId']
                assert re.fullmatch('[a-z0-9]{16}', row['sourceId'])
                assert 'ifdb:' + row['sourceId'] in work['sourceRefs']
                assert work['firstYear'] == dt.date.fromisoformat(row['ifdbPublished'][:10]).year
                assert row['archiveSha256'] == mixed.ifdb.ARCHIVE_SHA256
                assert not any(ref.startswith('vndb:') for ref in work['sourceRefs'])
            else:
                assert work['id'] == 'vndb-' + row['vndbId']
                assert 'vndb:' + row['vndbId'] in work['sourceRefs']
                assert work['firstYear'] == mixed.e.previous.vndb_year({
                    'released':row['sourceReleased'],'devstatus':row['sourceDevstatus']})
            assert not any(folded.get(ref.casefold()) for ref in work['sourceRefs'])
            assert all(mixed.e.norm(n) and not index.get(mixed.e.norm(n)) for n in
                [work['title'], *work['aliases']])
            for n in [work['title'], *work['aliases']]:
                index[mixed.e.norm(n)].add((work['id'], work['firstYear'], 'new'))
            for ref in work['sourceRefs']:
                folded[ref.casefold()].add(work['id'])
        if batch == mixed.B61:
            review = audit['ifdbArchiveReview']
            assert review['selected'] == source_counts['ifdb']
            assert review['sha256'] == mixed.ifdb.ARCHIVE_SHA256
            assert review['startPosition'] == mixed.IFDB_START_POSITION
            assert review['nextPosition'] == review['startPosition'] + review['scanned']
            assert review['scanned'] == review['selected'] + sum(review['dispositions'].values())
    for audit in audits:
        for row in audit['deferredEligible']:
            work = row['work']
            assert all(not index.get(mixed.e.norm(n)) for n in [work['title'],*work['aliases']])
            assert not any(folded.get(ref.casefold()) for ref in work['sourceRefs'])
            for n in [work['title'],*work['aliases']]:
                index[mixed.e.norm(n)].add((work['id'], work['firstYear'], 'deferred'))
            for ref in work['sourceRefs']:
                folded[ref.casefold()].add(work['id'])
    summary = mixed.e.load(mixed.REPORT)['summary']
    assert summary['newDistinctWorks'] == len(added)
    assert summary['uniqueVndbIds'] + summary['uniqueIfdbTuids'] == len(added)
    assert current['summary']['accepted'] == len(current['works'])
    print('BASIC_PARTIAL_CHECK_OK',len(old['works']),'+',len(added),'=',len(current['works']),
        json.dumps(summary),flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--archive', default='/tmp/ifdb-archive-20260901.zip')
    args = parser.parse_args()
    configure()
    if not args.check:
        registry, index, refs = mixed.e.source.state()
        c0 = mixed.e.context('vndb', mixed.B60, mixed.SEED_VNDB, mixed.A60)
        c1 = mixed.e.context('nextmoe', mixed.B61, mixed.SEED_NEXTMOE, mixed.A61)
        if not mixed.e.source.already_exists(registry, mixed.B60, mixed.A60):
            mixed.e.drain(c0, index, refs)
            mixed.e.drain(c1, index, refs)
            mixed.e.fetch_vndb(c0, index, refs)
            # Strict upper bound, not a requirement to invent 500 VNDB records.
            assert 0 < len(c0['pending']) + len(c0['fresh'])
            mixed.e.append(c0, registry)
        registry, index, refs = mixed.e.source.state()
        mixed.e.reserve(mixed.e.load(mixed.A60)['deferredEligible'], index, refs)
        if not mixed.e.source.already_exists(registry, mixed.B61, mixed.A61):
            if 'pendingInput' not in c1:
                mixed.e.drain(c1, index, refs)
            else:
                mixed.e.reserve(c1['pending'], index, refs)
            mixed.e.fetch_nextmoe(c1, index, refs)
            mixed.append_mixed(c1, registry, index, refs, args.archive)
        mixed.report()
    flexible_check()
    output = mixed.e.ROOT / 'data/basic-r132-r133-audit-summary-20261102.md'
    report = report_text()
    if args.check:
        assert output.read_text(encoding='utf-8') == report
    else:
        output.write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
