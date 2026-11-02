#!/usr/bin/env python3
"""Two 500-work batches from IFDB and reviewed PC-98 catalogues; no VNDB/NextMoe requests."""
import argparse
from collections import Counter, defaultdict
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import subprocess

import ifdb_archive_identity as ifdb
import import_basic_r22_cont_r23_20261101 as catalogue
import import_basic_r20_r21_20261101 as append

ROOT = Path(__file__).resolve().parents[1]
BASE = '1f523c70f0bcf49ba9bd412023f5aa32c95c5e3a'
DATE = '2026-11-03'
# Preserve the exact preparation and ordering used by the saved IFDB position.
IFDB_CUTOFF = dt.date(2026, 11, 2)
START = 10527
SNAPSHOT = ROOT / 'data/pc98-catalogue-snapshot-20261103.json'
REVIEW = ROOT / 'data/pc98-admission-review-20261103.json'
PC_AUDIT = ROOT / 'data/pc98-catalogue-audit-20261103.json'
REPORT = ROOT / 'data/basic-r134-r135-audit-summary-20261103.md'
REG = catalogue.REG
norm, load, save = catalogue.norm, catalogue.load, catalogue.save
EDITION = re.compile(r'(?i)(\bcollection\b|\bbundle\b|\bremaster\b|\bdemo\b|\btrial\b|\bappend\b|\bexpansion\b|コレクション|増刊|追加|体験版|完全版|リメイク|復刻|ファンディスク|スペシャルディスク|データ集|サントラ)')


def batch(number):
    return f'ifdb-pc98-bulk-20261103-r{number}'


def audit_path(number):
    return ROOT / f'data/ifdb-pc98-bulk-review-20261103-r{number}.json'


def split_names(work):
    result = []
    for name in catalogue.common.names(work):
        # Explicit bilingual separators; never split fractions such as Memory 1/4.
        result += [name, *re.split(r'\s+/\s+|／', name)]
    return list(dict.fromkeys(n.strip() for n in result if len(norm(n)) >= 3))


def full_index(registry):
    index = defaultdict(set)
    for work in catalogue.all_works(registry):
        for name in split_names(work):
            index[norm(name)].add((work['id'], int(work.get('firstYear') or work.get('year') or 0), 'full-catalogue'))
    return index


def full_refs(registry):
    refs = catalogue.identity_map(registry)
    for work in catalogue.all_works(registry):
        if work.get('source'):
            refs['source-url:' + work['source']].add(work['id'])
    return refs


def refs_for(work):
    return [*work.get('sourceRefs', []), 'source-url:' + work['source']]


def reserve(work, index, refs):
    for name in split_names(work):
        index[norm(name)].add((work['id'], work['firstYear'], 'new-or-reserved'))
    for ref in refs_for(work):
        refs[ref.casefold()].add(work['id'])


def pc98_preflight(registry):
    snapshot, review = load(SNAPSHOT), load(REVIEW)
    raw = snapshot['records']
    keyed = {(r['catalogue'], r['sourceId']): r for r in raw}
    assert len(keyed) == len(raw) == snapshot['summary']['rawRecords']
    index, refs = full_index(registry), full_refs(registry)
    approved, resolution = [], {}
    for item in review['approved']:
        witnesses = [keyed[tuple(k)] for k in item['catalogueRows']]
        assert {r['catalogue'] for r in witnesses} == {'ikachi-igdb', 'pc9801-archive'}
        assert {r['catalogueYear'] for r in witnesses} == {item['firstYear']}
        assert item['source'].startswith(('https://www.gamepres.org/', 'https://d4e.co.jp/'))
        assert item['evidenceLevel'] == 'primary-supported-year-and-cross-catalogue-identity'
        work = {'id': 'pc98-igdb-' + item['igdbId'], 'indexId': 'basic-pc98-20261103-' + item['igdbId'],
            'title': item['title'], 'aliases': item['aliases'], 'firstYear': item['firstYear'],
            'gameplay': item['gameplay'], 'group': item['group'], 'source': item['source'],
            'sourceRefs': item['sourceRefs'], 'mainPlacement': 'promoted-basic', 'linkedRecordId': None,
            'creditScope': '目录品牌关联，仅作检索；未建立开发／发行或个人创作者正式职责。',
            'yearBasis': item['yearBasis'], 'editorialScope': '基础身份、原作年及来源；不按移植、合售或复刻建立独立作品。'}
        hits = set().union(*(index.get(norm(n), set()) for n in split_names(work)))
        ref_hits = set().union(*(refs.get(ref, set()) for ref in refs_for(work)))
        status = 'reviewed-candidate'
        if hits or ref_hits:
            status = 'reviewed-existing-identity'
        else:
            approved.append({'work': work, 'sourceKind': 'pc98', 'evidence': item,
                'catalogueWitnesses': witnesses, 'intakeOrigin': 'reviewed-pc98'})
            reserve(work, index, refs)
        for key in item['catalogueRows']:
            resolution[tuple(key)] = {'status': status, 'candidateWorkId': work['id'],
                'matches': sorted(hits), 'matchedWorkIds': sorted(ref_hits)}
    # Evaluate remaining raw catalogue rows against the pre-intake catalogue only.
    index, refs = full_index(registry), full_refs(registry)
    manual = {r['igdbId']: r for r in review.get('manualAliasReuse', [])}
    dispositions = []
    for row in raw:
        key = row['catalogue'], row['sourceId']
        result = {'catalogue': row['catalogue'], 'sourceId': row['sourceId'],
            'title': row['title'], 'catalogueYear': row['catalogueYear'], 'source': row['source']}
        names = [row['title'], row['latin']]
        hits = set().union(*(index.get(norm(n), set()) for n in names if n))
        if key in resolution:
            result.update(resolution[key])
        elif not re.search('AVG|RPG|アドベンチャー|ビジュアルノベル', row['genre']):
            result['status'] = 'outside-narrative-adv-rpg-scope'
        elif row['catalogue'] == 'ikachi-igdb' and row['sourceId'] in manual:
            decision = manual[row['sourceId']]
            assert decision['matchedWorkId'] in {w['id'] for w in catalogue.all_works(registry)}
            result.update(status='reviewed-alias-reuse', matchedWorkIds=[decision['matchedWorkId']], basis=decision['basis'])
        elif EDITION.search(' '.join(names)):
            result['status'] = 'possible-edition-or-dependent-content-held'
        elif hits:
            result['matches'] = sorted(hits)
            result['status'] = ('reused-title-alias-and-year' if
                len({h[0] for h in hits}) == 1 and {h[1] for h in hits} == {row['catalogueYear']}
                else 'name-year-or-multiple-identity-held')
        elif not row['catalogueYear']:
            result['status'] = 'missing-year-held'
        else:
            result['status'] = 'needs-primary-year-and-alias-review'
        dispositions.append(result)
    counts = dict(Counter(r['status'] for r in dispositions))
    audit = {'schema': 1, 'date': DATE, 'baseCommit': BASE,
        'snapshotSha256': hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),
        'reviewSha256': hashlib.sha256(REVIEW.read_bytes()).hexdigest(),
        'summary': {'rawRecords': len(raw), 'reviewedNewWorks': len(approved), 'dispositions': counts},
        'records': dispositions,
        'scope': 'Two catalogue rows may refer to one work. Raw-row dispositions are separate from the number of new work identities.',
        'caveat': 'Unreviewed primary years/aliases and suspected editions are held; no source row is promoted solely from an ADV/RPG genre label.'}
    save(PC_AUDIT, audit)
    return sorted(approved, key=lambda r: (r['work']['firstYear'], r['work']['id']))


def report_text():
    audits = [load(audit_path(n)) for n in (134, 135)]
    pc = load(PC_AUDIT)
    lines = ['# 第134、135批：IFDB与PC-98历史目录补录', '',
        '本轮不请求VNDB或NextMoe。PC-98先核对原始年份与别名，合格身份均分两批；余下名额由IFDB补足。', '',
        '| 批次 | PC-98新增 | IFDB扫描 | IFDB去重复用 | IFDB隔离 | IFDB新增 | 总新增 |',
        '|---|---:|---:|---:|---:|---:|---:|']
    for a in audits:
        s, r = a['summary'], a['ifdbArchiveReview']
        lines.append(f"| {a['round']} | {s['sourceCounts']['pc98']} | {r['scanned']} | {len(a['reusedExisting'])} | {len(a['heldForIdentityReview'])} | {s['sourceCounts']['ifdb']} | {s['newDistinctWorks']} |")
    lines += ['', f"基础身份库：{audits[0]['summary']['before']:,} → {audits[-1]['summary']['after']:,}。两批各500，合计1000。", '',
        '## PC-98目录逐条审核', '',
        f"两份目录共{pc['summary']['rawRecords']}条原始记录；经目录交叉核对、原作年证据和全库别名检查，新增{pc['summary']['reviewedNewWorks']}个作品身份。原始目录记录数不当作独立作品数。", '',
        '| 处理状态 | 原始记录数 |', '|---|---:|']
    lines += [f'| {k} | {v} |' for k, v in sorted(pc['summary']['dispositions'].items())]
    lines += ['', '两份目录的全部逐条结果见[PC-98目录审计](pc98-catalogue-audit-20261103.json)。待核项保留原始标题、目录ID和年份，不作为已合格暂存或新增数。', '',
        '| 本次PC-98新增作品 | 原作年 | 证据 |', '|---|---:|---|']
    for a in audits:
        for row in a['records']:
            if row['sourceKind'] == 'pc98':
                lines.append(f"| {row['title']} | {row['firstYear']} | [来源]({row['source']}) |")
    lines += ['', '## IFDB续采位置', '',
        f"固定档案SHA-256：`{ifdb.ARCHIVE_SHA256}`；筛选截止日期继续使用2026-11-02，排序不变。", '',
        f"起点：{START}；第134批后：{audits[0]['ifdbArchiveReview']['nextPosition']}；第135批后：{audits[1]['ifdbArchiveReview']['nextPosition']}。", '',
        '本轮IFDB无已合格剩余暂存；PC-98待核项目独立保留，不能用未核年份或平台移植凑数。', '',
        '## IFDB名称／年份／身份隔离清单', '',
        '| 批次 | IFDB来源ID | 标题 | 来源日期 | 匹配已有身份及年份 |', '|---|---|---|---|---|']
    for a in audits:
        for r in a['heldForIdentityReview']:
            vals = [a['round'], r['sourceId'], r['title'], r.get('published', ''),
                '; '.join(f'{x[0]} ({x[1]})' for x in r.get('matches', []))]
            lines.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in vals) + ' |')
    lines += ['', '## 验证范围', '',
        '全库包含基础身份、完整主库、创作者补充与专题关联；检查来源ID、大小写不敏感IFID、标题／别名、显式中日英合写名称及两批之间的重复。',
        '已有对象、内容版本、平台发行、正式职责及旧批次保持不变。测试与PR／Pages实际状态另见工作流，不预先声明发布成功。', '']
    return '\n'.join(lines)


def check():
    def original(path):
        return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)
    old = json.loads(original(str(REG.relative_to(ROOT))))
    current = load(REG)
    assert current['works'][:len(old['works'])] == old['works']
    assert current['batches'][:len(old['batches'])] == old['batches']
    for key in old:
        if key not in {'works', 'batches', 'summary', 'updated'}:
            assert current[key] == old[key]
    for path in catalogue.PROTECTED + ['data/vn-seven-source-date-review-20261101.json']:
        assert original(path) == (ROOT / path).read_bytes(), path
    added = current['works'][len(old['works']):]
    assert len(added) == 1000
    assert len({w['id'] for w in current['works']}) == len(current['works'])
    assert len({w['indexId'] for w in current['works']}) == len(current['works'])
    index, refs = full_index(old), full_refs(old)
    folded = defaultdict(set)
    for ref, hits in refs.items():
        folded[ref.casefold()].update(hits)
    pc_ids = set()
    position = START
    all_ids = {w['id'] for w in catalogue.all_works(current)}
    for n in (134, 135):
        a = load(audit_path(n))
        works = [w for w in added if w['batch'] == batch(n)]
        assert len(works) == len(a['records']) == a['summary']['newDistinctWorks'] == 500
        assert sum(a['summary']['sourceCounts'].values()) == 500
        evidence = {r['id']: r for r in a['records']}
        for w in works:
            r = evidence[w['id']]
            assert all(w[k] == r[k] for k in w)
            assert all(not index.get(norm(name)) for name in split_names(w)), w['id']
            assert not any(folded.get(ref.casefold()) for ref in refs_for(w)), w['id']
            if r['sourceKind'] == 'ifdb':
                assert w['id'] == 'ifdb-' + r['sourceId']
                assert w['firstYear'] == dt.date.fromisoformat(r['ifdbPublished'][:10]).year
                assert dt.date.fromisoformat(r['ifdbPublished'][:10]) <= IFDB_CUTOFF
                assert r['archiveSha256'] == ifdb.ARCHIVE_SHA256
                assert r['archiveUrl'] == ifdb.ARCHIVE_URL
                assert not any(ref.startswith(('vndb:', 'nextmoe:')) for ref in w['sourceRefs'])
            else:
                assert r['sourceKind'] == 'pc98' and w['id'] not in pc_ids
                assert r['evidence']['firstYear'] == w['firstYear']
                assert r['evidence']['source'] == w['source']
                assert len(r['catalogueWitnesses']) >= 2
                assert not EDITION.search(' '.join([w['title'], *w['aliases']]))
                pc_ids.add(w['id'])
            reserve(w, index, folded)
        review = a['ifdbArchiveReview']
        assert review['startPosition'] == position
        assert review['nextPosition'] == position + review['scanned']
        assert review['selected'] == a['summary']['sourceCounts']['ifdb']
        assert review['selected'] + sum(review['dispositions'].values()) == review['scanned']
        assert len(a['reusedExisting']) + len(a['heldForIdentityReview']) + review['selected'] == review['scanned']
        assert review['sha256'] == ifdb.ARCHIVE_SHA256 and review['preparationCutoff'] == IFDB_CUTOFF.isoformat()
        assert all(set(r['matchedWorkIds']) <= all_ids for r in a['reusedExisting'])
        assert not a['deferredEligible']
        position = review['nextPosition']
    pc = load(PC_AUDIT)
    assert len(pc_ids) == pc['summary']['reviewedNewWorks']
    assert pc['snapshotSha256'] == hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
    assert pc['reviewSha256'] == hashlib.sha256(REVIEW.read_bytes()).hexdigest()
    assert len(pc['records']) == pc['summary']['rawRecords'] == sum(pc['summary']['dispositions'].values())
    assert current['summary']['accepted'] == len(current['works']) == len(old['works']) + 1000
    for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
        assert current['summary'][key] == old['summary'][key] + 1000
    assert current['updated'] == DATE
    assert REPORT.read_text() == report_text()
    print('IFDB_PC98_FULL_CHECK_OK', len(old['works']), '+1000 =', len(current['works']), 'PC98', len(pc_ids), 'IFDB_NEXT', position, flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--archive', default='/tmp/ifdb-archive-20260901.zip')
    args = parser.parse_args()
    if args.check:
        check()
        return
    registry = load(REG)
    if all(any(b['id'] == batch(n) for b in registry['batches']) for n in (134, 135)):
        check()
        return
    assert not any(b['id'] == batch(n) for n in (134, 135) for b in registry['batches']), 'Partial import requires review; never repeat a completed batch'
    previous = load(ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r133.json')['ifdbArchiveReview']
    assert ifdb.resume_position(previous) == START
    prepared, rejected = ifdb.prepare(ifdb.read_archive(args.archive), IFDB_CUTOFF)
    assert len(prepared) == previous['eligibleArchiveCandidates']
    pc_rows = pc98_preflight(registry)
    index, refs = full_index(registry), full_refs(registry)
    for r in pc_rows:
        reserve(r['work'], index, refs)
    position = START
    for offset, number in enumerate((134, 135)):
        pc = copy.deepcopy(pc_rows[offset::2])
        for row in pc:
            row['work']['batch'] = batch(number)
        selected, review = ifdb.choose(prepared, 500 - len(pc), index, refs, norm, batch(number), start_position=position)
        rows = pc + selected
        records = [{**r['work'], **{k: v for k, v in r.items() if k != 'work'}} for r in rows]
        held = review.pop('heldForIdentityReview')
        reused = review.pop('reusedExisting')
        stats = {'sourceCounts': {'pc98': len(pc), 'ifdb': len(selected)},
            'ifdbScanned': review['scanned'], 'ifdbReused': len(reused), 'ifdbHeld': len(held),
            'remainingDeferred': 0, 'newDistinctWorks': 500}
        append.append_batch(registry, [r['work'] for r in rows], batch(number),
            [ifdb.ARCHIVE_URL, 'https://www.ikachi.org/pc9801/', 'https://pc-9801.com/'],
            audit_path(number), stats, records, held,
            ['https://ifdb.org/api/', 'https://www.gamepres.org/dbsearch/'],
            'Minimal factual metadata with per-record source provenance; no descriptions or game files copied.', intake_date=DATE)
        a = load(audit_path(number))
        a.update({'round': number, 'priorBaseCommit': BASE, 'reusedExisting': reused,
            'deferredEligible': [], 'pendingQueueReview': [],
            'pc98PreflightAudit': str(PC_AUDIT.relative_to(ROOT)),
            'ifdbArchiveReview': {'url': ifdb.ARCHIVE_URL, 'sha256': ifdb.ARCHIVE_SHA256,
                'preparationCutoff': IFDB_CUTOFF.isoformat(), 'cataloguePreparationDispositions': rejected, **review},
            'sourcePolicy': 'No VNDB or NextMoe requests. Reviewed PC-98 identities first, then deterministic IFDB archive continuation.',
            'caveats': ['IFDB work dates are catalogue dates, not independently verified global original-region release evidence.',
                'PC-98 catalogue rows are not independent works. Only the named primary-supported review is admitted; platform ports, compilations and unresolved dates remain held.']})
        save(audit_path(number), a)
        position = review['nextPosition']
    REPORT.write_text(report_text())
    check()


if __name__ == '__main__':
    main()
