"""Attach the frozen round-ten evidence ledger without promoting scoped credits."""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def attach_verification(result):
    read = lambda name: json.loads((ROOT / 'data' / name).read_text())
    ledger = read('organization-verification-20261027.json')
    context = read('organization-context-20261027.json')
    nodes = {n['id']: n for n in result['nodes']}
    records = {r['recordId']: r for r in ledger['records']}
    assert len(records) == len(ledger['records']), '重复台账记录'
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
        'reviewedAt': ledger['reviewedAt'], 'source': ledger['source'],
        'policy': ledger['policy'], 'records': records,
        'counts': dict(Counter(r['status'] for r in records.values())),
        'entityCount': sum(bool(rows) for rows in by_entity.values()), 'total': len(records),
        'audit': 'data/organization-verification-20261027.md'}
    result['updated'] = ledger['reviewedAt']
    return result
