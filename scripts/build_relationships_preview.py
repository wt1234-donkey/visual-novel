"""Read-only, small presentation snapshot; no entity/credit migration is applied."""
import argparse
import json
from collections import defaultdict
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def build():
    model = json.loads((ROOT / 'data/entities.json').read_text())
    credits = json.loads((ROOT / 'data/credits.json').read_text())
    games = json.loads((ROOT / 'data/games.json').read_text())
    coverage = json.loads((ROOT / 'data/company-coverage.json').read_text())
    config = json.loads((ROOT / 'data/relationships-preview-config.json').read_text())
    entities = {e['id']: e for e in model['entities']}
    works = {w['id']: w for w in games['works']}
    placements = {w['id']: 'main' for w in games['works']}
    for c in coverage['companies']:
        for field, placement in [('relatedGames', 'related'), ('dossierOnlyWorks', 'bibliography')]:
            for w in c.get(field, []):
                works.setdefault(w['id'], w)
                placements.setdefault(w['id'], placement)
    byentity = defaultdict(list)
    for c in credits['credits']:
        byentity[c['entityId']].append(c)
    ids = {eid for family in config['families'] for eid in family['entityIds']}
    preview_ids = {node['id'] for node in config['previewNodes']}
    assert ids <= entities.keys() | preview_ids, '关系家族引用了不存在的节点'
    nodes = []
    for eid in sorted(ids - preview_ids):
        entity = entities[eid]
        direct = byentity[eid]
        workids = {c['workId'] for c in direct}
        production = {c['workId'] for c in direct if c['role'] in
                      {'originalProduction', 'developer', 'coDeveloper', 'productionBrand'}}
        featured = sorted((works[wid] for wid in workids if placements[wid] == 'main'),
                          key=lambda w: (w['firstYear'], w['id']))[:4]
        nodes.append({**entity,
                      'stats': {p: sum(placements[wid] == p for wid in workids)
                                for p in ['main', 'related', 'bibliography']},
                      'productionCount': sum(placements[wid] == 'main' for wid in production),
                      'dossiers': [{'id': d['id'], 'name': d['name']} for d in model['dossiers']
                                   if eid in d['entityIds']],
                      'works': [{'id': w['id'], 'title': w.get('chineseTitle') or w['title'],
                                 'year': w['firstYear']} for w in featured]})
    nodes += config['previewNodes']
    edges = []
    for i, r in enumerate(model['relations']):
        if {r['from'], r['to']} <= ids:
            edges.append({'id': f'existing-{i}', 'parent': r['to'], 'child': r['from'],
                          'kind': 'brand' if r['type'] == 'operatedBy' else 'family',
                          'label': '品牌运营' if r['type'] == 'operatedBy' else '品牌家族',
                          'status': r['status'], 'source': r['source'], 'note': r['note'],
                          'dateLabel': (str(r['period']['from']) + '起；终点未核')
                          if r['period'].get('from') else '起止时间未核',
                          'basis': 'existingIndex'})
    edges += config['previewEdges']
    return {'schemaVersion': 1, 'updated': '2026-10-22', 'mode': 'presentationPreview',
            'families': config['families'], 'nodes': nodes, 'edges': edges,
            'nameHistory': config['nameHistory'], 'reference': config['reference']}


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--check', action='store_true')
    args = p.parse_args()
    target = ROOT / 'data/relationships-preview.json'
    rendered = json.dumps(build(), ensure_ascii=False, indent=2) + '\n'
    if args.check:
        assert target.read_text() == rendered, '关系预览快照需要重新生成'
    else:
        target.write_text(rendered)
    print(target.relative_to(ROOT))
