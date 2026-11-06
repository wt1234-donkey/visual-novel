#!/usr/bin/env python3
"""Append all selected Lemon Amiga/AGDB rows without bibliographic deduplication."""
import argparse
import base64
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/main-adv-rpg-works-20261031.json'
SOURCE = ROOT / 'data/lemon-amiga-agdb-append-source-20261106.json.gz.b64'
MANIFEST = ROOT / 'data/lemon-amiga-agdb-append-manifest-20261106.json'
PREFIX = 'lemon-amiga-agdb-append-20261106-r'
FIRST_BATCH, LAST_BATCH, BATCH_SIZE = 222, 222, 500
EXPECTED_BASE, EXPECTED_INPUT = 107684, 489


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(path, value, compact=False):
    text = json.dumps(value, ensure_ascii=False, **({'separators': (',', ':')} if compact else {'indent': 2})) + '\n'
    if path == DB and len(text.encode()) >= 100 * 1024 * 1024:
        raise RuntimeError('Registry exceeds GitHub 100 MiB limit; no changes written')
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(text, encoding='utf-8')
    temp.replace(path)


def source_rows():
    manifest = read(MANIFEST)
    packed = SOURCE.read_bytes()
    if hashlib.sha256(packed).hexdigest() != manifest['packedSha256']:
        raise RuntimeError('Packed source checksum mismatch')
    raw = gzip.decompress(base64.b64decode(packed))
    if hashlib.sha256(raw).hexdigest() != manifest['jsonSha256']:
        raise RuntimeError('Source JSON checksum mismatch')
    rows = json.loads(raw)
    if len(rows) != EXPECTED_INPUT or manifest['sourceRecords'] != EXPECTED_INPUT:
        raise RuntimeError('Selected source count differs')
    if Counter(r['sourceSubset'] for r in rows) != {'unmatched': 308, 'suspected-existing': 181}:
        raise RuntimeError('Selected sheet counts differ')
    if len({(r['sourceWorkbookSheet'], r['sourceWorkbookRow']) for r in rows}) != EXPECTED_INPUT:
        raise RuntimeError('Repeated snapshot row position')
    for i, row in enumerate(rows):
        if row['sourceSnapshotRow'] != i + 1:
            raise RuntimeError('Snapshot row order differs')
        work_from(row, FIRST_BATCH + i // BATCH_SIZE)
    return rows, manifest


def work_from(row, batch):
    uid = 'lemon-amiga-agdb-20261106-' + str(row['sourceSnapshotRow']).zfill(4)
    title = row['title']
    year = row['directoryYear']
    urls = row['sourceUrls']
    if not isinstance(title, str) or not title.strip():
        raise RuntimeError('Empty title')
    if not urls or any(not isinstance(u, str) or not u.startswith('https://') for u in urls):
        raise RuntimeError('Missing source URL')
    if year is not None and (not isinstance(year, int) or isinstance(year, bool) or not 1970 <= year <= 2036):
        raise RuntimeError('Invalid directory year')
    return {
        'id': uid, 'indexId': 'basic-' + uid,
        'title': title, 'aliases': row['originalNames'], 'firstYear': year,
        'gameplay': row['gameplay'] or '玩法待核',
        'gameplayNote': row['scope'] + '；目录分类，精确交互及独立作品和版本关系待核。',
        'group': row['group'] or '厂商待核',
        'source': urls[0], 'additionalSources': urls[1:],
        'sourceRefs': ['lemon-amiga-agdb-snapshot:20261106-row' + str(row['sourceSnapshotRow'])],
        'mainPlacement': 'promoted-basic', 'linkedRecordId': None,
        'creditScope': '目录主体原文；不据此建立正式创作或发行职责。',
        'yearBasis': '原表目录年；Amiga为平台发行年，AGDB为目录年，均未核定为跨平台原作首发。',
        'editorialScope': '用户指定表格全量追加、不查重；保留混合玩法候选与版本关系待核。',
        'batch': PREFIX + str(batch), 'intakePolicy': 'append-without-deduplication',
        'sourceSubset': row['sourceSubset'], 'sourcePlatform': row['sourcePlatform'],
        'sourceScope': row['scope'], 'sourceGenre': row['genre'],
        'sourcePlatformCandidates': row['platformCandidates'], 'sourcePlotTags': row['plotTags'],
        'sourceComparisonStatus': '未匹配' if row['sourceSubset'] == 'unmatched' else '疑似已有，需复核',
        'sourcePossibleExistingId': row['possibleExistingId'],
        'sourcePossibleExistingTitle': row['possibleExistingTitle'],
        'sourcePossibleExistingUrl': row['possibleExistingUrl'],
        'sourceNote': row['sourceNote'], 'sourceCoverage': row['sourceCoverage'],
        'sourceSnapshot': str(SOURCE.relative_to(ROOT)), 'sourceSnapshotRow': row['sourceSnapshotRow'],
        'sourceWorkbookSheet': row['sourceWorkbookSheet'], 'sourceWorkbookRow': row['sourceWorkbookRow'],
        'originalWorkbookLocations': row['originalWorkbookLocations'],
    }


def check_registry(registry, manifest):
    if registry['summary']['accepted'] != len(registry['works']):
        raise RuntimeError('Summary count differs')
    if canonical_hash(registry['works'][:EXPECTED_BASE]) != manifest['baseWorksCanonicalSha256']:
        raise RuntimeError('Existing records changed')
    if len({w['id'] for w in registry['works']}) != len(registry['works']):
        raise RuntimeError('Duplicate internal IDs')


def build_batch(rows, number, before):
    offset = (number - FIRST_BATCH) * BATCH_SIZE
    block = rows[offset:offset + BATCH_SIZE]
    works = [work_from(r, number) for r in block]
    summary = {'candidates': len(block), 'promoted-basic': len(block), 'appendedRecords': len(block),
        'unmatched': sum(r['sourceSubset'] == 'unmatched' for r in block),
        'suspectedExisting': sum(r['sourceSubset'] == 'suspected-existing' for r in block),
        'narrativeMain': sum(r['scope'] == '叙事主表' for r in block),
        'mixedGameplayCandidates': sum(r['scope'] == '混合玩法候选' for r in block),
        'unknownYear': sum(w['firstYear'] is None for w in works),
        'before': before, 'after': before + len(block), 'deduplication': 'not-performed'}
    audit = {'schema': 1, 'date': '2026-11-06', 'batch': number, 'batchSizeLimit': BATCH_SIZE,
        'intakePolicy': 'append-without-deduplication', 'sourceSnapshot': str(SOURCE.relative_to(ROOT)),
        'sourceOffset': offset, 'summary': summary,
        'records': [{'workId': w['id'], 'title': w['title'], 'directoryYear': w['firstYear'],
            'sourceSnapshotRow': w['sourceSnapshotRow'], 'sourceSubset': w['sourceSubset'],
            'sourcePlatform': w['sourcePlatform']} for w in works],
        'notice': '追加来源记录数，不代表去重后的独立作品数。'}
    return works, summary, audit


def run(dry_run=False):
    rows, manifest = source_rows()
    registry = read(DB)
    check_registry(registry, manifest)
    complete = {b['id'] for b in registry.get('batches', [])}
    done = [PREFIX + str(n) in complete for n in range(FIRST_BATCH, LAST_BATCH + 1)]
    if all(done):
        verify()
        print('ALREADY_IMPORTED', EXPECTED_INPUT)
        return
    if any(done) or len(registry['works']) != EXPECTED_BASE:
        raise RuntimeError('Partial import or moved baseline; inspect before resuming')
    ids = {w['id'] for w in registry['works']}
    audits = []
    for n in range(FIRST_BATCH, LAST_BATCH + 1):
        works, summary, audit = build_batch(rows, n, len(registry['works']))
        if ids.intersection(w['id'] for w in works):
            raise RuntimeError('Internal ID collision; existing records not overwritten')
        ids.update(w['id'] for w in works)
        registry['works'].extend(works)
        for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
            registry['summary'][key] += len(works)
        path = ROOT / f'data/lemon-amiga-agdb-append-review-20261106-r{n}.json'
        registry['batches'].append({'id': PREFIX + str(n), 'source': 'https://www.lemonamiga.com/',
            'sources': ['https://www.lemonamiga.com/', 'https://www.adventuregamedb.com/'],
            'review': str(path.relative_to(ROOT)), 'summary': summary})
        audits.append((path, audit))
        print('BATCH', n, 'RECORDS', len(works), 'AFTER', summary['after'])
    registry['updated'] = '2026-11-06'
    registry.setdefault('intakeOverrides', {})['lemonAmigaAgdbTables20261106'] = {
        'policy': 'append-without-deduplication', 'sourceRecords': EXPECTED_INPUT,
        'importedRecords': EXPECTED_INPUT, 'unmatched': 308, 'suspectedExisting': 181,
        'narrativeMain': 400, 'mixedGameplayCandidates': 89, 'firstBatch': FIRST_BATCH, 'lastBatch': LAST_BATCH, 'batchSize': BATCH_SIZE}
    check_registry(registry, manifest)
    size = len((json.dumps(registry, ensure_ascii=False, separators=(',', ':')) + '\n').encode())
    if size >= 100 * 1024 * 1024:
        raise RuntimeError('Registry would exceed 100 MiB; no files written')
    if not dry_run:
        for path, audit in audits:
            save(path, audit)
        save(DB, registry, compact=True)
    print('RESULT', 'DRY_RUN' if dry_run else 'WRITTEN', 'appended', EXPECTED_INPUT, 'total', len(registry['works']), 'bytes', size)


def verify():
    rows, manifest = source_rows()
    registry = read(DB)
    check_registry(registry, manifest)
    indexed = {w['id']: w for w in registry['works']}
    for i, row in enumerate(rows):
        expected = work_from(row, FIRST_BATCH + i // BATCH_SIZE)
        if indexed.get(expected['id']) != expected:
            raise RuntimeError('Imported row differs: ' + expected['id'])
    for n in range(FIRST_BATCH, LAST_BATCH + 1):
        _, summary, expected = build_batch(rows, n, EXPECTED_BASE + (n - FIRST_BATCH) * BATCH_SIZE)
        audit = read(ROOT / f'data/lemon-amiga-agdb-append-review-20261106-r{n}.json')
        matches = [b for b in registry['batches'] if b['id'] == PREFIX + str(n)]
        if audit != expected or len(matches) != 1 or matches[0]['summary'] != summary:
            raise RuntimeError('Batch audit or accounting differs')
    if sum(w.get('batch', '').startswith(PREFIX) for w in registry['works']) != EXPECTED_INPUT:
        raise RuntimeError('Imported source row count differs')
    print('IMPORT_CHECK_OK', EXPECTED_INPUT, 'total', len(registry['works']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--all', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    verify() if args.check else run(args.dry_run)
