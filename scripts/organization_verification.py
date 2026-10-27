"""Attach versioned evidence ledgers without promoting scoped credits."""
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def attach_verification(result):
    read = lambda name: json.loads((ROOT / 'data' / name).read_text())
    baseline_path = ROOT / 'data/organization-verification-20261027.json'
    ledger = read(baseline_path.name)
    baseline_source = ledger['source']
    delta = read('organization-verification-round16-20261027.json')
    assert hashlib.sha256(baseline_path.read_bytes()).hexdigest() == delta['baselineSha256']
    context = read('organization-context-20261027.json')
    supplement = read('organization-context-round16-20261027.json')
    for key in ['nodeNotes', 'edgeReviews', 'events', 'cooperations']:
        context[key].extend(supplement[key])
        context[key].extend(read('organization-context-round20-20261027.json')[key])
    nodes = {n['id']: n for n in result['nodes']}
    records = {r['recordId']: r for r in ledger['records']}
    assert len(records) == len(ledger['records']), '重复台账记录'
    histories = {}
    for row in delta['records']:
        ref = row['recordId']
        assert ref in records and ref not in histories, '新增台账引用或重复更新'
        previous = records[ref]
        frozen = ['category', 'id', 'topic', 'game', 'placement', 'need', 'oldUrl',
                  'recordId', 'entityId', 'workId']
        assert all(row[key] == previous[key] for key in frozen), '冻结作品或主体引用变更'
        assert previous['status'] == '仍待核' and row['sources']
        assert 11 <= row['newRound'] <= delta['source']['round']
        histories[ref] = {'round': baseline_source['round'], **{
            key: previous[key] for key in ['status', 'detail', 'sources', 'strength']}}
        records[ref] = row
    series = {ref: [entry] for ref, entry in histories.items()}
    revision = read('organization-verification-round20-20261027.json')
    for name, sha in revision['baselineFiles'].items():
        assert hashlib.sha256((ROOT / 'data' / name).read_bytes()).hexdigest() == sha
    changed = []
    for row in revision['records']:
        ref = row['recordId']
        assert ref in records and ref not in changed
        previous = records[ref]
        assert all(row[key] == previous[key] for key in frozen), '冻结主体或作品发生变化'
        assert row['sources'], '修订须保留逐项来源，包括仍待核的检索记录'
        entry = {'round': delta['source']['round'], **{
            key: previous[key] for key in ['status', 'detail', 'sources', 'strength']}}
        series.setdefault(ref, []).append(entry)
        histories[ref] = entry
        records[ref] = row
        changed.append(ref)
    by_entity = defaultdict(lambda: defaultdict(list))
    for r in records.values():
        assert r['entityId'] in nodes and r['workId'] in result['works']
        by_entity[r['entityId']][r['workId']].append(r['recordId'])
    for eid, node in nodes.items():
        if node.get('previewOnly'):
            continue
        node['groups']['verification'] = [
            {'workId': wid, 'recordIds': refs, 'creditIds': [], 'pendingRefs': []}
            for wid, refs in sorted(by_entity[eid].items(), key=lambda item: (
                result['works'][item[0]]['year'], item[0]))]
        node['verificationNotes'] = []
    for note in context['nodeNotes']:
        assert note['entityId'] in nodes
        assert note['recordIds'] and all(ref in records for ref in note['recordIds'])
        nodes[note['entityId']]['verificationNotes'].append(note)
    for review in context['edgeReviews']:
        edge = next(e for e in result['edges'] if
                    e['parent'] == review['parent'] and e['child'] == review['child'])
        assert all(ref in records for ref in review['recordIds'])
        edge.update({k: v for k, v in review.items() if k not in ['parent', 'child']})
        edge.update(status='sourceReviewed', basis='roundTenEvidence',
                    source=records[review['recordIds'][0]]['sources'][0]['url'])
    for cooperation in context['cooperations']:
        assert all(eid in nodes for eid in cooperation['entityIds'])
        assert all(ref in records for ref in cooperation['recordIds'])
    for event in context['events']:
        assert all(eid in nodes for eid in event['entityIds'])
        assert all(ref in records for ref in event['recordIds'])
    result['organizationEvents'] = context['events']
    result['cooperations'] = context['cooperations']
    result['verificationLedger'] = {
        'reviewedAt': revision['reviewedAt'], 'source': revision['source'],
        'previousSource': delta['source'], 'policy': revision['policy'], 'records': records,
        'changedRecordIds': changed, 'changedCount': len(changed),
        'recordHistory': histories, 'recordHistories': series,
        'counts': dict(Counter(r['status'] for r in records.values())),
        'entityCount': sum(bool(rows) for rows in by_entity.values()), 'total': len(records),
        'audit': revision['audit']}
    result['updated'] = revision['reviewedAt']
    return result
