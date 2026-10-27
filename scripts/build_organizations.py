"""Build a read-only creator catalogue, preserving formal entity and credit indexes."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
from build_relationships_preview import build as preview_build
from organization_verification import attach_verification
from organization_unfinished import attach_unfinished
ROOT = Path(__file__).resolve().parents[1]
CREATION_ROLES = {'originalProduction', 'developer', 'coDeveloper', 'productionBrand'}
UNRESOLVED = {'pendingRole', 'unresolved', 'pending'}


def build():
    read = lambda name: json.loads((ROOT / f'data/{name}.json').read_text())
    model, credits, games, coverage = [read(n) for n in ['entities', 'credits', 'games', 'company-coverage']]
    result = preview_build()
    reviews = [read(name) for name in ['entity-creator-a-review-20261022', 'entity-creator-a2-review-20261022', 'entity-creator-a3-review-20261022', 'entity-creator-a4-review-20261023', 'entity-creator-a5-review-20261023', 'entity-creator-a6-review-20261023', 'entity-creator-b1-review-20261023', 'entity-creator-b2-review-20261023', 'entity-creator-b3-review-20261023', 'entity-creator-c1-review-20261023', 'entity-creator-c2-review-20261023', 'entity-creator-c3-review-20261023', 'entity-creator-c4-review-20261023', 'entity-creator-d1-review-20261023', 'entity-creator-d2-review-20261023', 'entity-creator-d3-review-20261023', 'entity-creator-e1-review-20261023', 'entity-creator-e2-review-20261024', 'entity-creator-e3-review-20261024', 'entity-creator-f1-review-20261024', 'entity-creator-f2-review-20261024', 'entity-creator-g1-review-20261024', 'entity-creator-g2-review-20261024', 'entity-creator-g3-review-20261024', 'entity-creator-h1-review-20261024', 'entity-creator-h2-review-20261024', 'entity-creator-h3-review-20261024', 'entity-creator-i1-review-20261024', 'entity-creator-i2-review-20261024', 'entity-creator-i3-review-20261024', 'entity-creator-i4-review-20261024', 'entity-creator-j1-review-20261024', 'entity-creator-k1-review-20261024', 'entity-creator-k2-review-20261024', 'entity-creator-k3-review-20261025', 'entity-creator-l1-review-20261025', 'entity-creator-l2-review-20261025', 'entity-creator-l3-review-20261025', 'entity-creator-m1-review-20261025', 'entity-creator-m2-review-20261025', 'entity-creator-m3-review-20261025', 'entity-creator-m4-review-20261025', 'entity-creator-m5-review-20261025', 'entity-creator-m6-review-20261025', 'entity-creator-n1-review-20261025', 'entity-creator-n2-review-20261025', 'entity-creator-n3-review-20261025', 'entity-creator-n4-review-20261025', 'entity-creator-n5-review-20261025', 'entity-creator-o1-review-20261025', 'entity-creator-p1-review-20261025', 'entity-creator-p2-review-20261025', 'entity-creator-p3-review-20261025', 'entity-creator-q1-review-20261025', 'entity-creator-r1-review-20261025', 'entity-creator-r2-review-20261025', 'entity-creator-s1-review-20261025', 'entity-creator-s2-review-20261025', 'entity-creator-s3-review-20261026', 'entity-creator-s4-review-20261026', 'entity-creator-s5-review-20261026', 'entity-creator-s6-review-20261026', 'entity-creator-s7-review-20261026', 'entity-creator-s8-review-20261026', 'entity-creator-s9-review-20261026', 'entity-creator-s10-review-20261026', 'entity-creator-s11-review-20261026', 'entity-creator-t1-review-20261026', 'entity-creator-t2-review-20261026', 'entity-creator-t3-review-20261026', 'entity-creator-t4-review-20261026', 'entity-creator-t5-review-20261026', 'entity-creator-u1-review-20261026', 'entity-creator-v1-review-20261026', 'entity-creator-w1-review-20261026', 'entity-creator-x1-review-20261026', 'entity-creator-y1-review-20261026', 'entity-creator-cf-catchup-review-20261026']]
    reviews.append(read('entity-creator-numeric-review-20261026'))
    review = reviews[-1]
    reviewed_entities = [entry for batch in reviews for entry in batch['reviewedEntities']]
    assert len({entry['entityId'] for entry in reviewed_entities}) == len(reviewed_entities)
    current = review['progress']
    completed_letters = {}
    for batch in reviews[:-1]:
        if batch['progress']['letter'] != current['letter']:
            completed_letters[batch['progress']['letter']] = batch['progress']
    prior_processed = [eid for p in completed_letters.values() for eid in p['processedEntityIds']]
    prior_queue = [entry for p in completed_letters.values() for entry in p['queue']]
    assert [entry['entityId'] for entry in reviewed_entities] == prior_processed + current['processedEntityIds']
    previous_letter = next((batch['progress'] for batch in reversed(reviews[:-1]) if batch['progress']['letter'] == current['letter']), None)
    preceding = previous_letter['processedEntityIds'] if previous_letter else []
    assert current['processedEntityIds'][:len(preceding)] == preceding
    assert [entry['entityId'] for entry in review['reviewedEntities']] == current['processedEntityIds'][len(preceding):]
    assert current['processedEntityIds'] == [q['entityId'] for q in current['queue'][:len(current['processedEntityIds'])]]
    assert len(current['queue']) == current['total']
    progress = {**current, 'letterTotal': current['total'], 'letterProcessed': len(current['processedEntityIds']),
                'total': sum(p['total'] for p in completed_letters.values()) + current['total'], 'processedEntityIds': prior_processed + current['processedEntityIds'],
                'queue': prior_queue + current['queue']}
    result['registrationProgress'] = {**progress, 'reviewedAt': review['reviewedAt'], 'audit': review['audit'], 'reviewedEntities': reviewed_entities, 'audits': [batch['audit'] for batch in reviews]}
    recheck = read('entity-creator-a-recheck1-review-20261026')
    five_phase = read('entity-verification-five-phase-review-20261026')
    second = five_phase['recheckProgress']
    queue_ids = [entry['entityId'] for entry in second['baselineQueue']]
    assert len(queue_ids) == second['total'] == len(set(queue_ids))
    assert second['processedEntityIds'] == queue_ids[:len(second['processedEntityIds'])]
    assert second['nextEntityId'] == (queue_ids[len(second['processedEntityIds'])]
                                      if len(second['processedEntityIds']) < second['total'] else None)
    assert [entry['entityId'] for entry in recheck['reviewedEntities']] + [entry['entityId'] for entry in five_phase['reviewedEntities']] == second['processedEntityIds']
    result['recheckProgress'] = {**second, 'reviewedAt': five_phase['reviewedAt'],
                                 'audit': five_phase['audit']}
    works = {}
    for w in games['works']:
        works[w['id']] = (w, 'main', 'index.html?query=' + quote(w.get('chineseTitle') or w['title']) + '#catalogue')
    for company in coverage['companies']:
        for field, placement in [('relatedGames', 'related'), ('dossierOnlyWorks', 'bibliography')]:
            for w in company.get(field, []):
                works.setdefault(w['id'], (w, placement, company['id'] + '.html#' + w['id']))
    dossiers = {d['id']: d for d in model['dossiers']}
    byentity, pending = defaultdict(lambda: defaultdict(list)), defaultdict(lambda: defaultdict(list))
    for credit in credits['credits']:
        byentity[credit['entityId']][credit['workId']].append(credit)
    for membership in credits['dossierMemberships']:
        if membership['status'] == 'pendingRole' or membership['group'] == 'unresolved':
            for eid in dossiers[membership['dossierId']]['entityIds']:
                pending[eid][membership['workId']].append(membership)
    nodes = []
    for entity in model['entities']:
        eid = entity['id']
        grouped = {key: [] for key in ['creation', 'originalBrand', 'pending', 'other']}
        for wid in sorted(set(byentity[eid]) | set(pending[eid]), key=lambda wid: (works[wid][0]['firstYear'], wid)):
            cs = byentity[eid][wid]
            usable = [c for c in cs if c['status'] not in UNRESOLVED]
            if any(c['role'] in CREATION_ROLES for c in usable):
                group = 'creation'
            elif pending[eid][wid]:
                group = 'pending'
            elif any(c['role'] == 'originalPublishingBrand' for c in usable):
                group = 'originalBrand'
            else:
                group = 'other'
            # Refer to the original credit IDs; evidence remains available without duplicating release rows.
            grouped[group].append({'workId': wid, 'creditIds': [c['id'] for c in cs],
                                   'pendingRefs': [{'dossierId': m['dossierId'], 'source': m['source']} for m in pending[eid][wid]]})
        workids = {wid for wid, cs in byentity[eid].items() if cs}
        featured = [works[wid][0] for wid in sorted(workids, key=lambda wid: (works[wid][0]['firstYear'], wid)) if works[wid][1] == 'main'][:4]
        nodes.append({**entity, 'groups': grouped,
                      'stats': {p: sum(works[wid][1] == p for wid in workids) for p in ['main', 'related', 'bibliography']},
                      'productionCount': sum(works[r['workId']][1] == 'main' for r in grouped['creation']),
                      'dossiers': [{'id': d['id'], 'name': d['name']} for d in model['dossiers'] if eid in d['entityIds']],
                      'works': [{'id': w['id'], 'title': w.get('chineseTitle') or w['title'], 'year': w['firstYear']} for w in featured]})
    nodes += [n for n in result['nodes'] if n.get('previewOnly')]
    ids = {n['id'] for n in nodes}
    edges = []
    for i, r in enumerate(model['relations']):
        edges.append({'id': f'existing-{i}', 'parent': r['to'], 'child': r['from'],
                      'kind': 'brand' if r['type'] == 'operatedBy' else 'family',
                      'label': '品牌运营' if r['type'] == 'operatedBy' else '品牌家族',
                      'status': r['status'], 'source': r['source'], 'note': r['note'],
                      'dateLabel': str(r['period']['from']) + '起；终点未核' if r['period'].get('from') else '起止时间未核', 'basis': 'existingIndex'})
    edges += [e for e in result['edges'] if not e['id'].startswith('existing-')]
    # Expand only through already registered relationships. Unconnected entities stay independent.
    adjacency = defaultdict(set)
    for e in edges:
        adjacency[e['parent']].add(e['child']); adjacency[e['child']].add(e['parent'])
    def component(seeds):
        seen, todo = set(seeds), list(seeds)
        while todo:
            for other in adjacency[todo.pop()] - seen:
                seen.add(other); todo.append(other)
        return seen
    assigned = set()
    for family in result['families']:
        members = component([family['root'], *family['entityIds']])
        family['entityIds'] = sorted(members)
        assigned |= members
    names = {n['id']: n for n in nodes}
    for eid in sorted(ids - assigned):
        if eid in assigned:
            continue
        members = component([eid]); assigned |= members
        incoming = {e['child'] for e in edges if e['parent'] in members}
        root = sorted(members - incoming or members)[0]
        result['families'].append({'id': root, 'title': names[root]['name'],
                                   'subtitle': '已登记组织关系' if len(members) > 1 else '独立主体档案',
                                   'root': root, 'focus': root, 'entityIds': sorted(members)})
    result.update({'mode': 'organizationCatalogue', 'nodes': nodes, 'edges': edges,
                   'roleLabels': model['roleLabels'], 'creationRoles': sorted(CREATION_ROLES),
                   'credits': {c['id']: {k: c[k] for k in ['entityId', 'workId', 'role', 'targetType', 'targetId', 'rawCredit', 'status', 'source', 'note']} for c in credits['credits']},
                   'works': {wid: {'id': wid, 'title': w.get('chineseTitle') or w['title'], 'originalTitle': w.get('originalTitle', ''),
                                   'year': w['firstYear'], 'placement': placement, 'href': href, 'category': w.get('category', '')}
                             for wid, (w, placement, href) in works.items()}})
    result = attach_verification(result)
    # New sourced milestones do not rewrite the frozen verification ledger.
    milestones = [event for name in ['takeru-history-20261027','tokuma-intermedia-history-20261027','sega-history-20261027','chunsoft-history-20261027','jhv-history-20261027'] for event in read(name)['events']]
    for event in milestones:
        assert set(event['entityIds']) <= ids and event['sources'] and not event['recordIds']
    result['organizationEvents'] += milestones
    assert len({event['id'] for event in result['organizationEvents']}) == len(result['organizationEvents'])
    return attach_unfinished(result, model, credits)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    target = ROOT / 'data/organizations.json'
    content = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if args.check:
        assert target.read_text() == content, '组织与沿革目录需要重新生成'
    else:
        target.write_text(content)
    print(target.relative_to(ROOT))
