#!/usr/bin/env python3
"""Rounds 132–133: recheck 50 VNDB + 0 NextMoe candidates, then resume three sources."""
import sys

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


if __name__ == '__main__':
    configure()
    mixed.main()
    output = mixed.e.ROOT / 'data/basic-r132-r133-audit-summary-20261102.md'
    result = report_text()
    if '--check' in sys.argv:
        assert output.read_text(encoding='utf-8') == result
    else:
        output.write_text(result, encoding='utf-8')
