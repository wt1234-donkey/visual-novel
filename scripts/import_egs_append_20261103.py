#!/usr/bin/env python3
"""Append ErogameScape unmatched + suspected-existing source entries WITHOUT title/year/source dedup.

Use in wt1234-donkey/visual-novel repo. Data source is a pinned, gzipped JSON
containing the 13,366 unpaired and 1,664 suspected-existing entries as supplied.

A source entry is NOT proof of a distinct narrative work. All additions are marked
with unverified editorial scope. Only internal primary key uniqueness is enforced.
"""
import argparse
import base64
import datetime
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/main-adv-rpg-works-20261031.json'
SOURCE = ROOT / 'data/erogamescape-append-source-20261103.json.gz.b64'
MANIFEST = ROOT / 'data/erogamescape-append-manifest-20261103.json'
PREFIX = 'erogamescape-append-20261103-r'
DATE = '2026-11-03'
FIRST_BATCH = 168
BATCH_SIZE = 500
EXPECTED_INPUT = 15030
EXPECTED_BASE = 81454


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temp.replace(path)


def rows_and_manifest():
    manifest = read_json(MANIFEST)
    packed = SOURCE.read_bytes()
    assert hashlib.sha256(packed).hexdigest() == manifest['packedSha256'], 'Source snapshot hash mismatch'
    raw = gzip.decompress(base64.b64decode(packed))
    assert hashlib.sha256(raw).hexdigest() == manifest['jsonSha256'], 'Source JSON hash mismatch'
    rows = json.loads(raw)
    assert len(rows) == EXPECTED_INPUT == manifest['sourceRecords']
    assert len({r['EGS ID'] for r in rows}) == len(rows), 'Input EGS IDs are not unique'
    assert sum(r['sourceSubset'] == 'unmatched' for r in rows) == 13366
    assert sum(r['sourceSubset'] == 'suspected-existing' for r in rows) == 1664
    return rows, manifest


def first_year(value):
    value = str(value or '').strip()
    return int(value) if len(value) == 4 and value.isdigit() else None


def work_from(row, batch_num):
    sid = row['EGS ID']
    year = first_year(row.get('发售年'))
    source_url = row['EGS链接']
    title = row['作品名']
    return {
        'id': 'erogamescape-table-20261103-' + sid,
        'indexId': 'basic-erogamescape-table-20261103-' + sid,
        'title': title,
        'aliases': [],
        'firstYear': year,
        'gameplay': '游戏类型待核',
        'gameplayNote': 'EGS目录来源：' + (row.get('EGS类型') or '未提供类型') + '；叙事属性和实际玩法未经核验。',
        'group': row.get('品牌') or '创作主体待核',
        'source': source_url,
        'sourceRefs': ['erogamescape:' + sid],
        'mainPlacement': 'promoted-basic',
        'linkedRecordId': None,
        'creditScope': 'EGS品牌字段仅用于基础检索，不确认为开发、发行或个人创作职责。',
        'yearBasis': '沿用EGS索引发售年；并非逐平台原作首发年考据。',
        'editorialScope': '用户要求两类候选全量追加且不去重；身份独立性、叙事适格性、年份和内容版次尚未核实。',
        'batch': PREFIX + str(batch_num),
        'intakePolicy': 'append-without-deduplication',
        'sourceSubset': row['sourceSubset'],
        'sourceReleased': row.get('发售日') or '',
        'sourcePlatform': row.get('平台') or '',
        'sourceGenre': row.get('EGS类型') or '',
        'sourceComparisonStatus': row.get('比对结论') or '',
        'sourcePossibleExistingId': row.get('基础库ID') or '',
        'sourcePossibleExistingTitle': row.get('基础库标题') or '',
        'sourceSimilarityBasis': row.get('匹配依据') or '',
        'sourceVersionRisk': row.get('版本风险') or '',
        'sourceSnapshot': 'data/erogamescape-append-source-20261103.json.gz.b64',
    }


def batch_numbers(rows):
    count = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
    return list(range(FIRST_BATCH, FIRST_BATCH + count))


def check_db(registry):
    assert isinstance(registry.get('works'), list)
    assert isinstance(registry.get('batches'), list)
    assert registry['summary']['accepted'] == len(registry['works']), 'Pre-existing registry summary mismatch'


def build_batch(rows, batch_num, before):
    offset = (batch_num - FIRST_BATCH) * BATCH_SIZE
    block = rows[offset:offset + BATCH_SIZE]
    assert 1 <= len(block) <= 500
    new = [work_from(r, batch_num) for r in block]
    summary = {
        'candidates': len(block),
        'promoted-basic': len(block),
        'appendedRecords': len(block),
        'unmatched': sum(r['sourceSubset'] == 'unmatched' for r in block),
        'suspectedExisting': sum(r['sourceSubset'] == 'suspected-existing' for r in block),
        'before': before,
        'after': before + len(block),
        'deduplication': 'not-performed',
        'review': 'source status preserved; not validated as independent narrative work',
        'unknownYear': sum(w['firstYear'] is None for w in new),
    }
    audit = {
        'schema': 1,
        'date': DATE,
        'intakePolicy': 'append-without-deduplication',
        'sourceSnapshot': 'data/erogamescape-append-source-20261103.json.gz.b64',
        'sourceOffset': offset,
        'summary': summary,
        'records': [{
            'EGS ID': r['EGS ID'],
            'title': r['作品名'],
            'sourceSubset': r['sourceSubset'],
            'workId': w['id'],
            'year': w['firstYear'],
            'possibleExistingId': r.get('基础库ID') or ''
        } for r, w in zip(block, new)],
        'notice': '追加条目数不等于经去重确认的独立叙事作品数。疑似已有及非叙事作品亦依用户指示保留；不能按新独立作品数统计。'
    }
    return new, summary, audit


def run(selected_pair=None, dry_run=False, no_base_check=False, complete=False):
    rows, manifest = rows_and_manifest()
    reg = read_json(DB)
    check_db(reg)
    numbers = batch_numbers(rows)
    completed = {b['id'] for b in reg['batches']}
    all_pairs = [(numbers[i], numbers[i+1:i+2]) for i in range(0, len(numbers), 2)]
    pair_count = len(all_pairs)
    if selected_pair is not None:
        assert 1 <= selected_pair <= pair_count
        all_pairs = [all_pairs[selected_pair - 1]]
    expected_previous = PREFIX + str(FIRST_BATCH - 1)
    first_pair = PREFIX + str(FIRST_BATCH)
    if not no_base_check and first_pair not in completed and len(reg['works']) != EXPECTED_BASE:
        raise RuntimeError(f'Baseline changed: current={len(reg["works"])} expected={EXPECTED_BASE}. Inspect before import or use --no-base-check after review.')
    existing_ids = {w['id'] for w in reg['works']}
    changed_batches = []
    pending_audits = []
    for first, second in all_pairs:
        group = [first, *second]
        done = [PREFIX + str(n) in completed for n in group]
        if all(done):
            print('PAIR_ALREADY_IMPORTED', (first - FIRST_BATCH) // 2 + 1, group)
            continue
        if any(done):
            raise RuntimeError(f'Partial pair already exists: {group}; manually inspect and resume')
        if first != FIRST_BATCH and PREFIX + str(first - 1) not in completed:
            raise RuntimeError(f'Previous batch missing: {first-1}')
        for num in group:
            new, summary, audit = build_batch(rows, num, len(reg['works']))
            collisions = existing_ids.intersection(w['id'] for w in new)
            if collisions:
                raise RuntimeError(f'Internal ID collision (data cannot be appended safely): {sorted(collisions)[:3]}')
            existing_ids.update(w['id'] for w in new)
            reg['works'].extend(new)
            for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
                reg['summary'][key] += len(new)
            path = ROOT / f'data/erogamescape-append-review-20261103-r{num}.json'
            reg['batches'].append({
                'id': PREFIX + str(num),
                'source': 'https://erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki/',
                'review': str(path.relative_to(ROOT)),
                'summary': summary
            })
            changed_batches.append(num)
            pending_audits.append((path, audit))
            completed.add(PREFIX + str(num))
            print('BATCH', num, 'RECORDS', len(new), 'BEFORE', summary['before'], 'AFTER', summary['after'])
    reg['updated'] = DATE
    overrides = reg.setdefault('intakeOverrides', {})
    overrides['erogameScape20261103'] = {
        'policy': 'append-without-deduplication',
        'sourceRecords': EXPECTED_INPUT,
        'importedRecords': sum(w.get('batch', '').startswith(PREFIX) for w in reg['works']),
        'firstBatch': FIRST_BATCH,
        'lastBatch': numbers[-1],
        'scope': 'EGS未匹配与疑似已有两表全量追加；不执行作品、年份、来源或版本去重。',
    }
    check_db(reg)
    assert len({w['id'] for w in reg['works']}) == len(reg['works']), 'Duplicate internal primary IDs'
    if not dry_run:
        for path, audit in pending_audits:
            save_json(path, audit)
        if changed_batches:
            save_json(DB, reg)
    print('RESULT', 'DRY_RUN' if dry_run else 'WRITTEN', 'new', sum(len(a['records']) for _, a in pending_audits), 'final', len(reg['works']), 'batches', changed_batches)
    if complete:
        all_done = {PREFIX + str(n) for n in numbers} <= completed
        assert all_done
        assert overrides['erogameScape20261103']['importedRecords'] == EXPECTED_INPUT
        print('COMPLETE_CHECK_OK', EXPECTED_INPUT, EXPECTED_BASE + EXPECTED_INPUT if not no_base_check else len(reg['works']))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--pair', type=int, help='import exactly one two-batch group, 1..16')
    mode.add_argument('--all', action='store_true', help='import all 16 two-batch groups in one invocation')
    mode.add_argument('--check', action='store_true', help='verify all imported records and batches')
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--no-base-check', action='store_true', help='use only after reviewing repository baseline changes')
    a = p.parse_args()
    if a.check:
        rows, _ = rows_and_manifest()
        reg = read_json(DB)
        check_db(reg)
        indexed = {w['id']: w for w in reg['works']}
        nums = batch_numbers(rows)
        for i, row in enumerate(rows):
            num = FIRST_BATCH + i // BATCH_SIZE
            expected = work_from(row, num)
            assert indexed.get(expected['id']) == expected, 'Imported row mismatch: ' + expected['id']
        for num in nums:
            audit = read_json(ROOT / f'data/erogamescape-append-review-20261103-r{num}.json')
            assert audit['summary']['appendedRecords'] == len(audit['records']) == min(BATCH_SIZE, len(rows) - (num - FIRST_BATCH) * BATCH_SIZE)
        assert sum(w.get('batch', '').startswith(PREFIX) for w in reg['works']) == EXPECTED_INPUT
        print('IMPORT_CHECK_OK', len(rows), len(nums), len(reg['works']))
    else:
        run(a.pair, a.dry_run, a.no_base_check, a.all)


if __name__ == '__main__':
    main()
