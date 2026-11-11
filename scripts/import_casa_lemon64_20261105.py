#!/usr/bin/env python3
"""Append all selected CASA/Lemon64 rows without bibliographic deduplication."""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import argparse
import base64
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/main-adv-rpg-works-20261031.json'
SOURCE = ROOT / 'data/casa-lemon64-append-source-20261105.json.gz.b64'
MANIFEST = ROOT / 'data/casa-lemon64-append-manifest-20261105.json'
PREFIX = 'casa-lemon64-append-20261105-r'
FIRST_BATCH, LAST_BATCH, BATCH_SIZE = 211, 221, 500
EXPECTED_BASE, EXPECTED_INPUT = 102204, 5480


def read(path):
    return read_registry_json(path)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(path, value, compact=False):
    if Path(path).name == 'main-adv-rpg-works-20261031.json':
        return write_registry_json(path, value)
    text = json.dumps(value, ensure_ascii=False, **({'separators': (',', ':')} if compact else {'indent': 2})) + '\n'
    if path == DB and len(text.encode()) >= 100 * 1024 * 1024:
        raise RuntimeError('Registry exceeds GitHub 100 MiB limit; no changes written')
    temp = path.with_suffix(path.suffix + '.tmp')
    write_registry_text(temp, text, encoding='utf-8')
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
    if Counter(r['sourceSubset'] for r in rows) != {'unmatched': 2381, 'suspected-existing': 3099}:
        raise RuntimeError('Selected sheet counts differ')
    if Counter(r['来源平台'] for r in rows) != {'CASA': 5028, 'Lemon64': 452}:
        raise RuntimeError('Platform counts differ')
    if len({(r['sourceWorkbookSheet'], r['sourceWorkbookRow']) for r in rows}) != EXPECTED_INPUT:
        raise RuntimeError('Repeated snapshot row position')
    for i, row in enumerate(rows):
        if row['sourceSnapshotRow'] != i + 1:
            raise RuntimeError('Snapshot row order differs')
        work_from(row, FIRST_BATCH + i // BATCH_SIZE)
    return rows, manifest


def work_from(row, batch):
    casa = row['来源平台'] == 'CASA'
    if not casa and row['来源平台'] != 'Lemon64':
        raise RuntimeError('Unknown platform')
    uid = str(row['CASA ID']) if casa else 'row' + str(row['原表行号'])
    stem = ('casa-table-20261105-' if casa else 'lemon64-table-20261105-') + uid
    url = row['作品/列表链接']
    if not isinstance(row['作品原名'], str) or not row['作品原名'].strip():
        raise RuntimeError('Empty title')
    if not isinstance(url, str) or not url.startswith('https://'):
        raise RuntimeError('Missing source URL')
    year = row['目录年份']
    if year is not None and (not isinstance(year, int) or isinstance(year, bool) or not 1970 <= year <= 2036):
        raise RuntimeError('Invalid directory year')
    if casa and (not uid.isdigit() or ('id%2C' + uid + '/') not in url):
        raise RuntimeError('CASA source ID and URL disagree')
    if not casa and not url.startswith('https://www.lemon64.com/games/list.php?'):
        raise RuntimeError('Unexpected Lemon64 list source')
    return {
        'id': stem, 'indexId': 'basic-' + stem,
        'title': row['作品原名'], 'aliases': [], 'firstYear': year,
        'gameplay': '冒险（玩法待核）' if casa else row['玩法/目录口径'],
        'gameplayNote': ('未匹配候选' if row['sourceSubset'] == 'unmatched' else '疑似已有，需复核') + '；独立作品和版本关系待核。',
        'group': row['发行主体/公司原文'] or row['作者原文'] or '厂商待核',
        'source': url,
        'sourceRefs': ['casa:' + uid] if casa else ['lemon64-snapshot:20261104-' + uid],
        'mainPlacement': 'promoted-basic', 'linkedRecordId': None,
        'creditScope': '目录主体原文；不据此建立正式创作或发行职责。',
        'yearBasis': 'CASA目录年，未核定为原作首发。' if casa else 'C64目录年，非跨平台原作首发核定。',
        'editorialScope': '用户指定全量追加、不去重；独立作品及内容版本关系待核。',
        'batch': PREFIX + str(batch), 'intakePolicy': 'append-without-deduplication',
        'sourceSubset': row['sourceSubset'], 'sourcePlatform': row['来源平台'],
        'sourceAuthor': row['作者原文'] or '', 'sourceLanguage': row['语言'] or '',
        'sourceGenre': row['原始分类/收录口径'] or '',
        'sourceComparisonStatus': '未匹配' if row['sourceSubset'] == 'unmatched' else '疑似已有，需复核',
        'sourceSnapshot': str(SOURCE.relative_to(ROOT)), 'sourceSnapshotRow': row['sourceSnapshotRow'],
        'sourceWorkbookSheet': row['sourceWorkbookSheet'], 'sourceWorkbookRow': row['sourceWorkbookRow'],
        'originalWorkbookSheet': row['原表工作表'], 'originalWorkbookRow': row['原表行号'],
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
        'CASA': sum(r['来源平台'] == 'CASA' for r in block),
        'Lemon64': sum(r['来源平台'] == 'Lemon64' for r in block),
        'unknownYear': sum(w['firstYear'] is None for w in works),
        'before': before, 'after': before + len(block), 'deduplication': 'not-performed'}
    audit = {'schema': 1, 'date': '2026-11-05', 'batch': number, 'batchSizeLimit': BATCH_SIZE,
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
        path = ROOT / f'data/casa-lemon64-append-review-20261105-r{n}.json'
        registry['batches'].append({'id': PREFIX + str(n), 'source': 'https://solutionarchive.com/',
            'sources': ['https://solutionarchive.com/', 'https://www.lemon64.com/'],
            'review': str(path.relative_to(ROOT)), 'summary': summary})
        audits.append((path, audit))
        print('BATCH', n, 'RECORDS', len(works), 'AFTER', summary['after'])
    registry['updated'] = '2026-11-05'
    registry.setdefault('intakeOverrides', {})['casaLemon64Tables20261105'] = {
        'policy': 'append-without-deduplication', 'sourceRecords': EXPECTED_INPUT,
        'importedRecords': EXPECTED_INPUT, 'unmatched': 2381, 'suspectedExisting': 3099,
        'CASA': 5028, 'Lemon64': 452, 'firstBatch': FIRST_BATCH, 'lastBatch': LAST_BATCH, 'batchSize': BATCH_SIZE}
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
        audit = read(ROOT / f'data/casa-lemon64-append-review-20261105-r{n}.json')
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
