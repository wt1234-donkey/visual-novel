"""Build a read-only creator catalogue, preserving formal entity and credit indexes."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
from build_relationships_preview import build as preview_build
ROOT = Path(__file__).resolve().parents[1]
CREATION_ROLES = {'originalProduction', 'developer', 'coDeveloper', 'productionBrand'}
UNRESOLVED = {'pendingRole', 'unresolved', 'pending'}


def build():
    read = lambda name: json.loads((ROOT / f'data/{name}.json').read_text())
    model, credits, games, coverage = [read(n) for n in ['entities', 'credits', 'games', 'company-coverage']]
    result = preview_build()
    reviews = [read(name) for name in ['entity-creator-a-review-20261022', 'entity-creator-a2-review-20261022', 'entity-creator-a3-review-20261022']]
    review = reviews[-1]
    reviewed_entities = [entry for batch in reviews for entry in batch['reviewedEntities']]
    assert len({entry['entityId'] for entry in reviewed_entities}) == len(reviewed_entities)
    assert [entry['entityId'] for entry in reviewed_entities] == review['progress']['processedEntityIds']
    result['registrationProgress'] = {**review['progress'], 'reviewedAt': review['reviewedAt'], 'audit': review['audit'], 'reviewedEntities': reviewed_entities, 'audits': [batch['audit'] for batch in reviews]}
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
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--check', action='store_true'); args = parser.parse_args()
    target = ROOT / 'data/organizations.json'
    content = json.dumps(build(), ensure_ascii=False, separators=(',', ':')) + '\n'
    if args.check:
        assert target.read_text() == content, '组织与沿革目录需要重新生成'
    else:
        target.write_text(content)
    print(target.relative_to(ROOT))
