#!/usr/bin/env python3
"""Append all 1,089 supplied IF Archive unmatched and suspected-existing rows.

No title, year, external-ID or edition deduplication is performed. Internal keys
and completed-batch guards prevent corrupt IDs or accidental reruns only.
"""
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
SOURCE = ROOT / 'data/ifarchive-append-source-20261104.json.gz.b64'
MANIFEST = ROOT / 'data/ifarchive-append-manifest-20261104.json'
PREFIX = 'ifarchive-append-20261104-r'
DATE = '2026-11-04'
FIRST_BATCH = 206
LAST_BATCH = 208
EXPECTED_INPUT = 1089
EXPECTED_BASE = 99854
BATCH_SIZE = 500


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    options = {'separators': (',', ':')} if compact else {'indent': 2}
    temporary.write_text(json.dumps(value, ensure_ascii=False, **options) + '\n', encoding='utf-8')
    temporary.replace(path)


def source_rows():
    manifest = read_json(MANIFEST)
    packed = SOURCE.read_bytes()
    if hashlib.sha256(packed).hexdigest() != manifest['packedSha256']:
        raise RuntimeError('Packed IF Archive source checksum mismatch')
    raw = gzip.decompress(base64.b64decode(packed))
    if hashlib.sha256(raw).hexdigest() != manifest['jsonSha256']:
        raise RuntimeError('IF Archive JSON source checksum mismatch')
    rows = json.loads(raw)
    if len(rows) != EXPECTED_INPUT or manifest['sourceRecords'] != EXPECTED_INPUT:
        raise RuntimeError('Expected exactly 1,089 source rows')
    if Counter(r['sourceSubset'] for r in rows) != {'unmatched': 601, 'suspected-existing': 488}:
        raise RuntimeError('IF Archive source subsets do not reconcile')
    for number, row in enumerate(rows, 1):
        row['sourceSnapshotRow'] = number
        if not re.fullmatch('[a-z0-9]{1,16}', row['IFDB_TUID']) or not row['作品名称']:
            raise RuntimeError('Invalid IF Archive source identity or empty title')
    return rows, manifest


def work_from(row, batch_number):
    uid = row['IFDB_TUID']
    year = row['发行年份']
    if year is not None and (not isinstance(year, int) or isinstance(year, bool)):
        raise RuntimeError('Year must remain an integer or unknown')
    raw_paths = str(row.get('Archive文件路径清单') or '')
    paths = [p.strip() for p in raw_paths.replace('\\n','\n').splitlines() if p.strip()]
    if not paths or any(not p.startswith('if-archive/') for p in paths):
        raise RuntimeError('Missing or invalid Archive path evidence')
    archive_urls = ['https://ifarchive.org/' + p for p in paths]
    ifdb_url = row['IFDB页面']
    return {
        'id': 'ifarchive-table-20261104-' + uid,
        'indexId': 'basic-ifarchive-table-20261104-' + uid,
        'title': row['作品名称'], 'aliases': [], 'firstYear': year,
        'gameplay': '互动小说（玩法待核）',
        'gameplayNote': 'IF Archive作品关联目录；制作系统和文件类别不作为实际操作方式或叙事属性的确证。',
        'group': row.get('作者或创作主体') or '创作主体待核',
        'source': archive_urls[0],
        'sourceRefs': ['ifdb:' + uid, *['ifarchive:' + p for p in paths]],
        'additionalSources': [ifdb_url, *archive_urls[1:]],
        'mainPlacement': 'promoted-basic', 'linkedRecordId': None,
        'creditScope': '沿用关联IFDB快照作者原文用于基础检索；不推定正式开发、发行或具体创作职责。',
        'yearBasis': '沿用IFDB关联快照发行年份，未知保持空缺；Archive文件时间不作为作品首发日期。',
        'editorialScope': '用户指定IF Archive未匹配及疑似已有两表全量追加且不去重；独立作品、版本、叙事属性和文件可玩性待核。',
        'batch': PREFIX + str(batch_number), 'intakePolicy': 'append-without-deduplication',
        'sourceSubset': row['sourceSubset'],
        'sourceTuid': uid, 'sourceIFDBPage': ifdb_url,
        'sourceReleased': row.get('发行日期_IFDB原始值') or '',
        'sourceAuthor': row.get('作者或创作主体') or '',
        'sourceLanguage': row.get('语言代码') or '',
        'sourceSystem': row.get('制作系统') or '',
        'sourceArchivePaths': paths,
        'sourceArchiveFileCount': row['Archive关联文件数'],
        'sourceArchiveAssociationBasis': row.get('关联依据') or '',
        'sourceArchiveVerification': row.get('核查说明') or '',
        'sourceComparisonStatus': row.get('比对结果') or ('待核实' if row['sourceSubset']=='suspected-existing' else '未匹配'),
        'sourcePossibleExistingId': row.get('基础库候选ID') or '',
        'sourcePossibleExistingTitle': row.get('基础库候选名称') or '',
        'sourcePossibleExistingYears': row.get('基础库候选年份') or '',
        'sourceSimilarityBasis': row.get('比对依据') or '',
        'sourceSnapshot': str(SOURCE.relative_to(ROOT)),
        'sourceSnapshotRow': row['sourceSnapshotRow'],
        'sourceWorkbookSheet': row['sourceSheet'], 'sourceWorkbookRow': row['sourceWorksheetRow'],
        'sourceArchiveWorkbookRow': row['Archive原表行号'],
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
            raise RuntimeError('Pair must be 1..2')
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
            path = ROOT / f'data/ifarchive-append-review-20261104-r{number}.json'
            registry['batches'].append({'id': PREFIX + str(number), 'source': 'https://ifdb.org/',
                'review': str(path.relative_to(ROOT)), 'summary': summary})
            audits.append((path, audit))
            completed.add(PREFIX + str(number))
            print('BATCH', number, 'RECORDS', len(new), 'BEFORE', summary['before'], 'AFTER', summary['after'])
    registry['updated'] = DATE
    registry.setdefault('intakeOverrides', {})['ifarchiveTables20261104'] = {
        'policy': 'append-without-deduplication', 'sourceRecords': EXPECTED_INPUT,
        'importedRecords': sum(w.get('batch', '').startswith(PREFIX) for w in registry['works']),
        'unmatched': 601, 'suspectedExisting': 488, 'firstBatch': FIRST_BATCH, 'lastBatch': LAST_BATCH,
        'scope': '仅用户指定的IF Archive未匹配及疑似已有1089条；不按名称、年份、来源或版本去重。',
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
        audit = read_json(ROOT / f'data/ifarchive-append-review-20261104-r{number}.json')
        expected = min(BATCH_SIZE, EXPECTED_INPUT - (number - FIRST_BATCH) * BATCH_SIZE)
        if audit['summary']['appendedRecords'] != len(audit['records']) or len(audit['records']) != expected:
            raise RuntimeError('Batch accounting differs')
    if sum(w.get('batch', '').startswith(PREFIX) for w in registry['works']) != EXPECTED_INPUT:
        raise RuntimeError('Final IF Archive intake differs')
    if len(registry['works']) < EXPECTED_BASE + EXPECTED_INPUT:
        raise RuntimeError('Final registry total differs')
    print('IMPORT_CHECK_OK', EXPECTED_INPUT, 'batches', LAST_BATCH - FIRST_BATCH + 1, 'total', len(registry['works']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--pair', type=int, help='Import one two-batch group, 1..2; group 2 has the final 89 rows')
    modes.add_argument('--all', action='store_true')
    modes.add_argument('--check', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if args.check:
        verify()
    else:
        run(args.pair, args.dry_run)
