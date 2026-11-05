#!/usr/bin/env python3
"""Append the selected MobyGames PC-88/PC-98 sheets as one two-batch group.

The user selected all unmatched and suspected-existing rows. Title, source,
year and edition similarity do not suppress their admission. Stable internal
keys and complete-group guards only prevent accidental repeated execution.
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
SOURCE = ROOT / 'data/mobygames-pc88-pc98-append-source-20261105.json.gz.b64'
MANIFEST = ROOT / 'data/mobygames-pc88-pc98-append-manifest-20261105.json'
PREFIX = 'mobygames-pc88-pc98-append-20261105-r'
DATE = '2026-11-05'
FIRST_BATCH, LAST_BATCH, BATCH_SIZE = 209, 210, 650
EXPECTED_INPUT, EXPECTED_BASE = 1261, 100943


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save_json(path, value, compact=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    options = {'separators': (',', ':')} if compact else {'indent': 2}
    temporary.write_text(json.dumps(value, ensure_ascii=False, **options) + '\n', encoding='utf-8')
    temporary.replace(path)


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def source_rows():
    manifest = read_json(MANIFEST)
    packed = SOURCE.read_bytes()
    if hashlib.sha256(packed).hexdigest() != manifest['packedSha256']:
        raise RuntimeError('Packed MobyGames snapshot checksum mismatch')
    raw = gzip.decompress(base64.b64decode(packed))
    if hashlib.sha256(raw).hexdigest() != manifest['jsonSha256']:
        raise RuntimeError('MobyGames source JSON checksum mismatch')
    rows = json.loads(raw)
    if len(rows) != EXPECTED_INPUT or manifest['sourceRecords'] != EXPECTED_INPUT:
        raise RuntimeError('Selected MobyGames source count differs')
    if Counter(r['sourceSubset'] for r in rows) != {'unmatched': 1118, 'suspected-existing': 143}:
        raise RuntimeError('MobyGames selected-sheet counts differ')
    if len({r['Moby ID'] for r in rows}) != len(rows):
        raise RuntimeError('The supplied source has repeated Moby IDs')
    for number, row in enumerate(rows, 1):
        if row['sourceSnapshotRow'] != number or not isinstance(row['Moby ID'], int) or isinstance(row['Moby ID'], bool) or row['Moby ID'] <= 0:
            raise RuntimeError('Invalid source position or Moby ID')
        if not isinstance(row['作品名称'], str) or not row['作品名称'].strip():
            raise RuntimeError('Empty MobyGames title')
        work_from(row, FIRST_BATCH + (number - 1) // BATCH_SIZE)
    return rows, manifest


def checked_year(value):
    if value is not None and (not isinstance(value, int) or isinstance(value, bool) or not 1970 <= value <= 2036):
        raise RuntimeError('Source years must remain integers or unknown')
    return value


def work_from(row, batch_number):
    uid = str(row['Moby ID'])
    url = row['MobyGames 来源 URL']
    if not re.match(r'^https://www\.mobygames\.com/game/' + re.escape(uid) + r'/', url):
        raise RuntimeError('Moby ID and source URL disagree')
    platform_years = {p: checked_year(row.get(p + ' 发行年')) for p in ('PC-88', 'PC-98')}
    original_year = checked_year(row.get('Moby 最早年（补充）'))
    known = [y for y in platform_years.values() if y is not None]
    year = original_year if original_year is not None else min(known, default=None)
    year_kind = 'source-work-earliest' if original_year is not None else 'platform-earliest-only' if known else 'unknown'
    note = '源表补充的Moby条目最早年；未重新逐作核实原作首发。' if original_year is not None else '仅采用所列PC-88/PC-98目录最早年作基础检索；不声明为原作首发年。' if known else '源目录未注明年份，保持空缺。'
    genre = row.get('目录类型（原文）') or ''
    developer = row.get('开发商关联（补充）') or ''
    publisher = row.get('发行商关联（补充）') or ''
    return {
        'id': 'mobygames-pc88-pc98-20261105-' + uid,
        'indexId': 'basic-mobygames-pc88-pc98-20261105-' + uid,
        'title': row['作品名称'], 'aliases': [], 'firstYear': year,
        'gameplay': genre or '玩法待核',
        'gameplayNote': '保留MobyGames目录类型原文；实际交互方式、叙事属性及独立作品/合集/版本关系待核。',
        'group': developer or publisher or '厂商待核',
        'source': url, 'sourceRefs': ['mobygames:' + uid],
        'mainPlacement': 'promoted-basic', 'linkedRecordId': None,
        'creditScope': '开发/发行补充列只用于条目级厂商关联检索，可能跨平台和版本；不据此创建正式制作/发行职责。',
        'yearBasis': note,
        'editorialScope': '用户指定未匹配1118条及疑似已有143条全量追加，650条一批、两批一组；保留全部源站类型，疑似已有不自动复用或合并。',
        'batch': PREFIX + str(batch_number), 'intakePolicy': 'append-without-deduplication',
        'sourceSubset': row['sourceSubset'], 'sourceMobyId': int(uid),
        'sourcePlatform': row.get('目录平台') or '', 'sourcePlatformYears': platform_years,
        'sourceEarliestYear': original_year, 'sourceYearKind': year_kind,
        'sourceGenre': genre, 'sourceDeveloperAssociations': developer, 'sourcePublisherAssociations': publisher,
        'sourceComparisonStatus': row['比对结论'], 'sourceSimilarityBasis': row['判断依据'],
        'sourcePossibleExistingId': row.get('候选基础库 ID') or '',
        'sourcePossibleExistingTitle': row.get('候选作品名称') or '',
        'sourcePossibleExistingYear': row.get('候选首发年'),
        'sourcePossibleExistingAlias': row.get('命中名称或别名') or '',
        'sourcePossibleExistingGroup': row.get('候选厂商') or '',
        'sourcePossibleExistingUrl': row.get('候选来源 URL') or '',
        'sourceOtherCandidates': row.get('其他候选') or '',
        'sourceSnapshot': str(SOURCE.relative_to(ROOT)), 'sourceSnapshotRow': row['sourceSnapshotRow'],
        'sourceWorkbookSheet': row['sourceWorkbookSheet'], 'sourceWorkbookRow': row['sourceWorkbookRow'],
    }


def check_registry(registry, manifest):
    if registry['summary']['accepted'] != len(registry['works']):
        raise RuntimeError('Registry summary and records disagree')
    if len({w['id'] for w in registry['works']}) != len(registry['works']):
        raise RuntimeError('Duplicate internal work IDs')
    if canonical_hash(registry['works'][:EXPECTED_BASE]) != manifest['baseWorksCanonicalSha256']:
        raise RuntimeError('Existing basic records changed; review the baseline before importing')


def build_batch(rows, number, before):
    offset = (number - FIRST_BATCH) * BATCH_SIZE
    block = rows[offset:offset + BATCH_SIZE]
    if not 1 <= len(block) <= BATCH_SIZE:
        raise RuntimeError('Invalid batch size')
    new = [work_from(r, number) for r in block]
    summary = {'candidates': len(block), 'promoted-basic': len(block), 'appendedRecords': len(block),
        'unmatched': sum(r['sourceSubset'] == 'unmatched' for r in block),
        'suspectedExisting': sum(r['sourceSubset'] == 'suspected-existing' for r in block),
        'before': before, 'after': before + len(block), 'unknownYear': sum(w['firstYear'] is None for w in new),
        'platformYearOnly': sum(w['sourceYearKind'] == 'platform-earliest-only' for w in new), 'deduplication': 'not-performed'}
    audit = {'schema': 1, 'date': DATE, 'batch': number, 'pair': 1, 'batchSizeLimit': BATCH_SIZE,
        'intakePolicy': 'append-without-deduplication', 'sourceSnapshot': str(SOURCE.relative_to(ROOT)),
        'sourceOffset': offset, 'summary': summary,
        'records': [{'mobyId': r['Moby ID'], 'title': w['title'], 'workId': w['id'], 'firstYear': w['firstYear'],
            'yearKind': w['sourceYearKind'], 'sourceSubset': w['sourceSubset'], 'possibleExistingId': w['sourcePossibleExistingId'],
            'sourceWorkbookSheet': w['sourceWorkbookSheet'], 'sourceWorkbookRow': w['sourceWorkbookRow']} for r, w in zip(block, new)],
        'notice': '追加基础身份记录数，不等于经过去重或逐作核实的独立新原作数。'}
    return new, summary, audit


def run(dry_run=False):
    rows, manifest = source_rows()
    registry = read_json(DB)
    check_registry(registry, manifest)
    completed = {b['id'] for b in registry.get('batches', [])}
    done = [PREFIX + str(n) in completed for n in range(FIRST_BATCH, LAST_BATCH + 1)]
    if all(done):
        verify()
        print('PAIR_ALREADY_IMPORTED', FIRST_BATCH, LAST_BATCH)
        return
    if any(done):
        raise RuntimeError('Partial group found; inspect before resuming')
    if len(registry['works']) != EXPECTED_BASE:
        raise RuntimeError('The pre-import baseline moved')
    existing = {w['id'] for w in registry['works']}
    audits = []
    for n in range(FIRST_BATCH, LAST_BATCH + 1):
        new, summary, audit = build_batch(rows, n, len(registry['works']))
        if existing.intersection(w['id'] for w in new):
            raise RuntimeError('Import internal IDs collide; no existing records were overwritten')
        existing.update(w['id'] for w in new)
        registry['works'].extend(new)
        for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
            registry['summary'][key] += len(new)
        path = ROOT / f'data/mobygames-pc88-pc98-append-review-20261105-r{n}.json'
        registry['batches'].append({'id': PREFIX + str(n), 'source': 'https://www.mobygames.com/',
            'sources': ['https://www.mobygames.com/platform/pc88/', 'https://www.mobygames.com/platform/pc98/'],
            'review': str(path.relative_to(ROOT)), 'summary': summary})
        audits.append((path, audit))
        print('BATCH', n, 'RECORDS', len(new), 'BEFORE', summary['before'], 'AFTER', summary['after'])
    registry['updated'] = DATE
    registry.setdefault('intakeOverrides', {})['mobyPc88Pc98Tables20261105'] = {
        'policy': 'append-without-deduplication', 'sourceRecords': EXPECTED_INPUT, 'importedRecords': EXPECTED_INPUT,
        'unmatched': 1118, 'suspectedExisting': 143, 'firstBatch': FIRST_BATCH, 'lastBatch': LAST_BATCH,
        'batchSize': BATCH_SIZE, 'groups': 1,
        'scope': '用户指定MobyGames PC-88/PC-98两表全量追加，保留疑似已有候选与所有目录类型；只添加基础身份。'}
    check_registry(registry, manifest)
    if not dry_run:
        for path, audit in audits:
            save_json(path, audit)
        save_json(DB, registry, compact=True)
    print('RESULT', 'DRY_RUN' if dry_run else 'WRITTEN', 'appended', sum(len(a['records']) for _, a in audits), 'final', len(registry['works']))


def verify():
    rows, manifest = source_rows()
    registry = read_json(DB)
    check_registry(registry, manifest)
    indexed = {w['id']: w for w in registry['works']}
    for i, row in enumerate(rows):
        expected = work_from(row, FIRST_BATCH + i // BATCH_SIZE)
        if indexed.get(expected['id']) != expected:
            raise RuntimeError('Imported row differs: ' + expected['id'])
    for n in range(FIRST_BATCH, LAST_BATCH + 1):
        audit = read_json(ROOT / f'data/mobygames-pc88-pc98-append-review-20261105-r{n}.json')
        _, summary, expected = build_batch(rows, n, EXPECTED_BASE + (n - FIRST_BATCH) * BATCH_SIZE)
        if audit != expected or audit['summary'] != summary:
            raise RuntimeError('Batch audit differs')
        matches = [b for b in registry['batches'] if b['id'] == PREFIX + str(n)]
        if len(matches) != 1 or matches[0]['summary'] != summary:
            raise RuntimeError('Batch registry accounting differs')
    if sum(w.get('batch', '').startswith(PREFIX) for w in registry['works']) != EXPECTED_INPUT:
        raise RuntimeError('Final selected-source count differs')
    if len(registry['works']) < EXPECTED_BASE + EXPECTED_INPUT:
        raise RuntimeError('Final registry count differs')
    print('IMPORT_CHECK_OK', EXPECTED_INPUT, 'batches', FIRST_BATCH, LAST_BATCH, 'total', len(registry['works']))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--all', action='store_true')
    mode.add_argument('--pair', type=int, choices=[1])
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    verify() if args.check else run(args.dry_run)
