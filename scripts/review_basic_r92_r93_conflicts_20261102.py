#!/usr/bin/env python3
"""Apply the explicit 61-identity review, preserving earlier catalogue evidence."""
import argparse
from collections import Counter
import hashlib
import json
import subprocess

import import_basic_r22_cont_r23_20261101 as source

ROOT = source.ROOT
AUDIT = ROOT / 'data/basic-r92-r93-conflict-review-20261102.json'
BASE = 'd26ec776be86dd2ab73e61bc39661cc51ab5a854'
BATCH = 'r92-r93-conflict-identities-20261102'


def original(path):
    return subprocess.check_output(['git', 'show', BASE + ':' + path], cwd=ROOT)


def review():
    audit = source.load(AUDIT)
    assert audit['baseCommit'] == BASE and audit['batchId'] == BATCH
    positions = []
    for path, digest in audit['inputAudits'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    for row in audit['decisions']:
        assert row['reason'] and row['sourceUrls']
        for locator in row['originalRows']:
            item = source.load(ROOT / locator['audit'])['heldForIdentityReview'][locator['index']]
            assert item == locator['row']
            key = 'vndb:' + item['vndbId'] if item.get('vndbId') else 'ifdb:' + item['sourceId']
            assert row['sourceIdentity'] == key
            positions.append((locator['audit'], locator['index']))
    expected = {(p, i) for p in audit['inputAudits']
                for i in range(len(source.load(ROOT / p)['heldForIdentityReview']))}
    assert len(positions) == len(set(positions)) == 79 and set(positions) == expected
    rows = audit['decisions']
    assert len(rows) == len({r['sourceIdentity'] for r in rows}) == 61
    assert Counter(r['status'] for r in rows) == {
        'registered-distinct': 56, 'reuse-existing': 2, 'held': 3}
    return audit


def additions(audit):
    result = []
    for row in audit['decisions']:
        if row['status'] != 'registered-distinct':
            continue
        kind, sid = row['sourceIdentity'].split(':')
        item = audit['sourceSnapshots'][kind][sid]
        if kind == 'vndb':
            assert source.previous.vndb_year(item) == row['firstYear']
            names = source.previous.vndb_names(item)
            refs = ['vndb:' + sid]
            url = 'https://vndb.org/' + sid
            gameplay = '视觉小说'
            year_basis = 'VNDB VN-level released 年份；按逐项身份复核保留，原始地区及具体发行批次待核。'
            if sid == 'v44020':
                year_basis += '2025为完整发行年；2023年抢先体验不冒充完整版首发。'
        else:
            assert item['firstYear'] == row['firstYear'] == int(item['published'][:4])
            names = [item['title'], *item['aliases']]
            refs = item['sourceRefs']
            url = 'https://ifdb.org/viewgame?id=' + sid
            gameplay = '互动小说（玩法待核）'
            year_basis = 'IFDB pinned public archive published字段作品年；原版区域及完整发行史待核。'
            assert not item['linkedVndbIds']
        assert names[0] == row['title'] and row['registryId'] == kind + '-' + sid
        result.append({
            'id': row['registryId'], 'indexId': BATCH + '-' + sid,
            'title': names[0], 'aliases': names[1:], 'firstYear': row['firstYear'],
            'gameplay': gameplay, 'group': '创作品牌待核', 'source': url,
            'sourceRefs': refs, 'mainPlacement': 'promoted-basic', 'linkedRecordId': None,
            'creditScope': '作者及开发主体信号仅存来源审计，不推断正式创作或发行职责。',
            'yearBasis': year_basis,
            'editorialScope': '基础身份；已复核同名碰撞或标题关键词误报，完整叙事、玩法及内容版本待核。',
            'identityReview': str(AUDIT.relative_to(ROOT)), 'batch': BATCH})
    return result


def apply():
    audit = review()
    registry = source.load(source.REG)
    if any(b['id'] == BATCH for b in registry['batches']):
        check()
        return
    before = json.loads(original(str(source.REG.relative_to(ROOT))))
    assert registry == before, 'Rebase and review concurrent catalogue changes before applying'
    new = additions(audit)
    index = source.common.existing_index(registry)
    refs = source.identity_map(registry)
    approved = {r['registryId']: r for r in audit['decisions']}
    for work in new:
        row = approved[work['id']]
        hits = set().union(*(index.get(source.norm(n), set())
                            for n in [work['title'], *work['aliases']]))
        assert sorted(map(list, hits)) == row['currentNameMatches'], work['id']
        assert not any(refs.get(ref) for ref in work['sourceRefs']), work['id']
    registry['works'].extend(new)
    for key in ('candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'):
        registry['summary'][key] += len(new)
    registry['updated'] = audit['date']
    registry['batches'].append({
        'id': BATCH, 'source': ['https://api.vndb.org/kana', audit['snapshotProvenance']['ifdbArchiveUrl']],
        'review': str(AUDIT.relative_to(ROOT)),
        'summary': {'candidates': len(new), 'promoted-basic': len(new),
                    'reviewedIdentities': 61, 'reusedExisting': 2, 'remainingHeld': 3}})
    source.save(source.REG, registry)
    check()


def check():
    audit = review()
    before = json.loads(original(str(source.REG.relative_to(ROOT))))
    current = source.load(source.REG)
    new = additions(audit)
    protected = before['works'] + new
    assert current['works'][:len(protected)] == protected, 'Existing work objects must remain exact'
    assert [w for w in current['works'] if w.get('batch') == BATCH] == new
    boundary = len(before['batches'])
    assert current['batches'][:boundary] == before['batches']
    assert current['batches'][boundary]['id'] == BATCH
    later = current['works'][len(protected):]
    later_batches = current['batches'][boundary + 1:]
    for key in before:
        if key not in {'works', 'batches', 'summary', 'updated'}:
            assert current[key] == before[key]
    for key, value in before['summary'].items():
        delta = len(new) if key in {'candidates', 'accepted', 'promotedBasic', 'addedToMainIdentityLayer'} else 0
        if key == 'candidates':
            delta += sum(b['summary']['candidates'] for b in later_batches)
        elif key == 'accepted':
            delta += len(later)
        elif key == 'promotedBasic':
            delta += sum(w['mainPlacement'] == 'promoted-basic' for w in later)
        elif key == 'promotedDossier':
            delta += sum(w['mainPlacement'] == 'promoted-dossier' for w in later)
        elif key == 'addedToMainIdentityLayer':
            delta += sum(w['mainPlacement'] in {'promoted-basic', 'promoted-dossier'} for w in later)
        assert current['summary'][key] == value + delta
    assert len(current['works']) >= 45841
    assert len(current['works']) == len({w['id'] for w in current['works']}) == len({w['indexId'] for w in current['works']})
    all_ids = {w['id'] for w in source.all_works(current)}
    old_refs = {r.casefold() for w in before['works'] for r in w.get('sourceRefs', [])}
    new_refs = [r.casefold() for w in new for r in w['sourceRefs']]
    assert len(new_refs) == len(set(new_refs)) and not old_refs.intersection(new_refs)
    for row in audit['decisions']:
        if row['status'] == 'held':
            kind, sid = row['sourceIdentity'].split(':')
            assert kind + '-' + sid not in all_ids
        elif row['status'] == 'reuse-existing':
            assert row['registryId'] in all_ids
    for path in source.PROTECTED + list(audit['inputAudits']):
        assert (ROOT / path).read_bytes() == original(path), path
    # Historical queues/cursors and all other round audits must remain byte-identical.
    for path in ('data/basic-r92-r93-diversity-20261102.json',):
        assert (ROOT / path).read_bytes() == original(path)
    print('CONFLICT_REVIEW_OK 79 rows / 61 identities: +56, reuse 2, held 3; 45785 -> 45841')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    check() if args.check else apply()
