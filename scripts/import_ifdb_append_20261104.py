#!/usr/bin/env python3
"""Append all 3,370 supplied IFDB unmatched and suspected-existing rows.

No title, year, external-ID or edition deduplication is performed. Internal keys
and completed-batch guards prevent corrupt IDs or accidental reruns only.
"""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import argparse
import base64
import gzip
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/main-adv-rpg-works-20261031.json'
SOURCE = ROOT / 'data/ifdb-append-source-20261104.json.gz.b64'
MANIFEST = ROOT / 'data/ifdb-append-manifest-20261104.json'
PREFIX = 'ifdb-append-20261104-r'
DATE = '2026-11-04'
FIRST_BATCH = 199
LAST_BATCH = 205
EXPECTED_INPUT = 3370
EXPECTED_BASE = 96484
BATCH_SIZE = 500


def read_json(path):
    return read_registry_json(path)


def save_json(path, value, compact=False):
    if Path(path).name == 'main-adv-rpg-works-20261031.json':
        return write_registry_json(path, value)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    options = {'separators': (',', ':')} if compact else {'indent': 2}
    write_registry_text(temporary, json.dumps(value, ensure_ascii=False, **options) + '\n', encoding='utf-8')
    temporary.replace(path)


def source_rows():
    manifest = read_json(MANIFEST)
    packed = SOURCE.read_bytes()
    if hashlib.sha256(packed).hexdigest() != manifest['packedSha256']:
        raise RuntimeError('Packed IFDB source checksum mismatch')
    raw = gzip.decompress(base64.b64decode(packed))
    if hashlib.sha256(raw).hexdigest() != manifest['jsonSha256']:
        raise RuntimeError('IFDB JSON source checksum mismatch')
    rows = json.loads(raw)
    if len(rows) != EXPECTED_INPUT or manifest['sourceRecords'] != EXPECTED_INPUT:
        raise RuntimeError('Expected exactly 3,370 source rows')
    if Counter(r['sourceSubset'] for r in rows) != {'unmatched': 2022, 'suspected-existing': 1348}:
        raise RuntimeError('IFDB source subsets do not reconcile')
    for number, row in enumerate(rows, 1):
        row['sourceSnapshotRow'] = number
        if not re.fullmatch('[a-z0-9]{1,16}', row['IFDB_TUID']) or not row['作品名称']:
            raise RuntimeError('Invalid IFDB source identity or empty title')
    return rows, manifest


def work_from(row, batch_number):
    uid = row['IFDB_TUID']
    year = row['发行年份']
    if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
        raise RuntimeError('Year must be an integer or unknown, not an inferred value')
    refs = ['ifdb:' + uid]
    for identity in re.split(r'[,;\s]+', str(row.get('IFID') or '')):
        if identity:
            refs.append('ifid:' + identity.lower())
    return {
        'id': 'ifdb-table-20261104-' + uid,
        'indexId': 'basic-ifdb-table-20261104-' + uid,
        'title': row['作品名称'],
        'aliases': [],
        'firstYear': year,
        'gameplay': '互动小说（玩法待核）',
        'gameplayNote': 'IFDB原始类型：' + (row.get('类型_原始') or '未提供') + '；制作系统和目录类型不等同于已核实操作方式。',
        'group': row.get('作者或创作主体') or '创作主体待核',
        'source': row['IFDB页面'],
        'sourceRefs': refs,
        'mainPlacement': 'promoted-basic',
        'linkedRecordId': None,
        'creditScope': 'IFDB作者原文仅用于基础检索；未核定开发、发行或具体创作职责。',
        'yearBasis': '沿用IFDB上传快照发行年份，空缺保持未知；未逐平台考证原作首发年。',
        'editorialScope': '用户指定未匹配及疑似已有两表全部追加且不去重；独立作品、叙事属性、年份和内容版次待核。',
        'batch': PREFIX + str(batch_number),
        'intakePolicy': 'append-without-deduplication',
        'sourceSubset': row['sourceSubset'],
        'sourceReleased': row.get('发行日期_原始') or '',
        'sourceAuthor': row.get('作者或创作主体') or '',
        'sourceLanguage': row.get('语言代码') or '',
        'sourceSystem': row.get('制作系统') or '',
        'sourceGenre': row.get('类型_原始') or '',
        'sourceIFID': row.get('IFID') or '',
        'sourceVersion': row.get('版本') or '',
        'sourceRedirectId': row.get('重定向目标ID') or '',
        'sourceComparisonStatus': row.get('比对结果') or '',
        'sourcePossibleExistingId': row.get('基础库候选ID') or '',
        'sourcePossibleExistingTitle': row.get('基础库候选名称') or '',
        'sourcePossibleExistingYears': row.get('基础库候选年份') or '',
        'sourceSimilarityBasis': row.get('比对依据') or '',
        'sourceSnapshot': str(SOURCE.relative_to(ROOT)),
        'sourceSnapshotRow': row['sourceSnapshotRow'],
        'sourceWorkbookSheet': row['sourceSheet'],
        'sourceWorkbookRow': row['sourceWorksheetRow'],
    }


def check_registry(registry):
    if registry['summary']['accepted'] != len(registry['works']):
        raise RuntimeError('Registry accepted count differs from records')
    if len({w['id'] for w in registry['works']}) != len(registry['works']):
        raise RuntimeError('Duplicate internal primary keys')


def original_works_unchanged(registry, manifest):
    original = registry['works'][:EXPECTED_BASE]
    raw = json.dumps(original, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()
    if hashlib.sha256(raw).hexdigest() != manifest['baseWorksCanonicalSha256']:
        raise RuntimeError('Existing basic records changed; review before importing')


def build_batch(rows, number, before):
    offset = (number - FIRST_BATCH) * BATCH_SIZE
    block = rows[offset:offset + BATCH_SIZE]
    if not 1 <= len(block) <= BATCH_SIZE:
        raise RuntimeError('Invalid batch size')
    new = [work_from(row, number) for row in block]
    summary = {
        'candidates': len(block), 'promoted-basic': len(block), 'appendedRecords': len(block),
        'unmatched': sum(r['sourceSubset'] == 'unmatched' for r in block),
        'suspectedExisting': sum(r['sourceSubset'] == 'suspected-existing' for r in block),
        'before': before, 'after': before + len(block),
        'unknownYear': sum(w['firstYear'] is None for w in new),
        'deduplication': 'not-performed',
    }
    audit = {
        'schema': 1, 'date': DATE, 'batch': number, 'pair': (number - FIRST_BATCH) // 2 + 1,
        'intakePolicy': 'append-without-deduplication', 'sourceSnapshot': str(SOURCE.relative_to(ROOT)),
        'sourceOffset': offset, 'summary': summary,
        'records': [{
            'IFDB_TUID': r['IFDB_TUID'], 'title': r['作品名称'], 'workId': w['id'],
            'firstYear': w['firstYear'], 'sourceSubset': r['sourceSubset'],
            'possibleExistingId': r.get('基础库候选ID') or '',
            'sourceSnapshotRow': r['sourceSnapshotRow'],
        } for r, w in zip(block, new)],
        'notice': '追加记录数不等于经过去重或人工核实的独立作品数。',
    }
    return new, summary, audit


def run(pair=None, dry_run=False):
    rows, manifest = source_rows()
    registry = read_json(DB)
    check_registry(registry)
    original_works_unchanged(registry, manifest)
    completed = {b['id'] for b in registry['batches']}
    if PREFIX + str(FIRST_BATCH) not in completed and len(registry['works']) != EXPECTED_BASE:
        raise RuntimeError('The pre-import baseline moved; inspect before starting')
    groups = [list(range(n, min(n + 2, LAST_BATCH + 1))) for n in range(FIRST_BATCH, LAST_BATCH + 1, 2)]
    if pair is not None:
        if not 1 <= pair <= len(groups):
            raise RuntimeError('Pair must be 1..4')
        groups = [groups[pair - 1]]
    existing_ids = {w['id'] for w in registry['works']}
    audits = []
    for group in groups:
        done = [PREFIX + str(n) in completed for n in group]
        if all(done):
            print('PAIR_ALREADY_IMPORTED', (group[0] - FIRST_BATCH) // 2 + 1, group)
            continue
        if any(done):
            raise RuntimeError('Partial pair exists; inspect its records before resuming')
        if group[0] != FIRST_BATCH and PREFIX + str(group[0] - 1) not in completed:
            raise RuntimeError('Previous pair is not complete')
        for number in group:
            new, summary, audit = build_batch(rows, number, len(registry['works']))
            if existing_ids.intersection(w['id'] for w in new):
                raise RuntimeError('Internal import IDs collide; records were not overwritten')
            existing_ids.update(w['id'] for w in new)
            registry['works'].extend(new)
            for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
                registry['summary'][key] += len(new)
            path = ROOT / f'data/ifdb-append-review-20261104-r{number}.json'
            registry['batches'].append({'id': PREFIX + str(number), 'source': 'https://ifdb.org/',
                'review': str(path.relative_to(ROOT)), 'summary': summary})
            audits.append((path, audit))
            completed.add(PREFIX + str(number))
            print('BATCH', number, 'RECORDS', len(new), 'BEFORE', summary['before'], 'AFTER', summary['after'])
    registry['updated'] = DATE
    registry.setdefault('intakeOverrides', {})['ifdbTables20261104'] = {
        'policy': 'append-without-deduplication', 'sourceRecords': EXPECTED_INPUT,
        'importedRecords': sum(w.get('batch', '').startswith(PREFIX) for w in registry['works']),
        'unmatched': 2022, 'suspectedExisting': 1348, 'firstBatch': FIRST_BATCH, 'lastBatch': LAST_BATCH,
        'scope': '仅用户指定的IFDB未匹配及疑似已有3370条；不按名称、年份、来源或版本去重。',
    }
    check_registry(registry)
    if not dry_run and audits:
        for path, audit in audits:
            save_json(path, audit)
        # Keep the growing single-file registry below GitHub's 100 MiB limit.
        # This changes JSON whitespace only; the original objects are checked above.
        save_json(DB, registry, compact=True)
    print('RESULT', 'DRY_RUN' if dry_run else 'WRITTEN', 'appended', sum(len(a['records']) for _, a in audits), 'final', len(registry['works']))


def verify():
    rows, manifest = source_rows()
    registry = read_json(DB)
    check_registry(registry)
    original_works_unchanged(registry, manifest)
    indexed = {w['id']: w for w in registry['works']}
    for i, row in enumerate(rows):
        expected = work_from(row, FIRST_BATCH + i // BATCH_SIZE)
        if indexed.get(expected['id']) != expected:
            raise RuntimeError('Imported source row differs: ' + expected['id'])
    for number in range(FIRST_BATCH, LAST_BATCH + 1):
        audit = read_json(ROOT / f'data/ifdb-append-review-20261104-r{number}.json')
        expected = min(BATCH_SIZE, EXPECTED_INPUT - (number - FIRST_BATCH) * BATCH_SIZE)
        if audit['summary']['appendedRecords'] != len(audit['records']) or len(audit['records']) != expected:
            raise RuntimeError('Batch accounting differs')
    if sum(w.get('batch', '').startswith(PREFIX) for w in registry['works']) != EXPECTED_INPUT:
        raise RuntimeError('Final IFDB intake differs')
    if len(registry['works']) < EXPECTED_BASE + EXPECTED_INPUT:
        raise RuntimeError('Final registry total differs')
    print('IMPORT_CHECK_OK', EXPECTED_INPUT, 'batches', LAST_BATCH - FIRST_BATCH + 1, 'total', len(registry['works']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--pair', type=int, help='Import one two-batch group, 1..4; group 4 has the final 370 rows')
    modes.add_argument('--all', action='store_true')
    modes.add_argument('--check', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.check:
        verify()
    else:
        run(args.pair, args.dry_run)
