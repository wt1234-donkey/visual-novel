"""Apply reviewed management packages to an isolated Git branch, with optimistic locking.

No file paths, executable code or Git commands are accepted in a package.
"""
import argparse
import copy
import datetime as dt
import json
import os
import re
from pathlib import Path

from source_urls import source_url_valid

ROOT = Path(__file__).resolve().parents[1]
PATHS = {'editorial': 'discovery-editorial.json', 'notes': 'work-notes.json',
         'people': 'creator-credits.json', 'credits': 'creator-credits.json'}
FIELDS = ('position', 'style', 'theme', 'structure')
ROLES = {'writer', 'artist', 'musician'}
ID = re.compile(r'[a-z0-9][a-z0-9_-]{1,119}\Z')


def read(name, root=ROOT):
    return json.loads((root / 'data' / name).read_text(encoding='utf-8'))


def load(root=ROOT):
    return {'editorial': read(PATHS['editorial'], root), 'notes': read(PATHS['notes'], root),
            'creators': read(PATHS['people'], root)}


def value(data, resource, key):
    if resource in ('editorial', 'notes'):
        return data[resource]['works'].get(key)
    return next((row for row in data['creators'][resource] if row['id'] == key), None)


def assign(data, resource, key, row):
    if resource in ('editorial', 'notes'):
        if row is None:
            data[resource]['works'].pop(key, None)
        else:
            data[resource]['works'][key] = copy.deepcopy(row)
    else:
        rows = data['creators'][resource]
        pos = next((i for i, item in enumerate(rows) if item['id'] == key), None)
        if pos is not None:
            if row is None:
                rows.pop(pos)
            else:
                rows[pos] = copy.deepcopy(row)
        elif row is not None:
            rows.append(copy.deepcopy(row))


def restore_historical(data, history):
    restored = copy.deepcopy(data)
    for batch in reversed(history['batches']):
        for op in reversed(batch['operations']):
            assert value(restored, op['resource'], op['key']) == op['after'], '管理历史与现行记录不一致'
            assign(restored, op['resource'], op['key'], op['before'])
    return restored


def text(s, minimum=1, maximum=20000):
    return isinstance(s, str) and minimum <= len(s.strip()) <= maximum


def sources(rows):
    return isinstance(rows, list) and 0 < len(rows) <= 30 and all(source_url_valid(s) for s in rows)


def validate_editorial(row):
    assert isinstance(row, dict), '编目必须为对象'
    allowed = set(FIELDS) | {'basis', 'sources', 'status', 'reviewedAt', 'evidenceStatus',
                             'fieldEvidence', 'openQuestions', 'cover', 'externalChecks', 'narrativeApplicability',
                             'scopeNote', 'externalResearch', 'missingFields'}
    assert set(row) <= allowed, '编目包含未知字段'
    assert text(row.get('basis'), 15) and sources(row.get('sources')), '编目缺少具体依据或有效来源'
    present = []
    for field in FIELDS:
        v = row.get(field)
        if not v:
            continue
        labels = [v] if field == 'position' else v
        assert isinstance(labels, list) and labels and all(text(x, maximum=200) for x in labels)
        assert len(set(labels)) == len(labels), '编目标签重复'
        assert not {'待核实', '待编目', '未知', '资料不足'} & set(labels), '占位词不计入完成'
        e = row.get('fieldEvidence', {}).get(field, {})
        assert text(e.get('basis'), 8) and text(e.get('evidenceText'), 5), '各字段需具体理由和资料摘记'
        assert sources(e.get('sources')) and e.get('sourceFields'), '各字段需来源与证据范围'
        present.append(field)
    assert row.get('status') == ('editorialObservation' if len(present) == 4 else 'partial')
    if len(present) < 4:
        assert isinstance(row.get('openQuestions'), list) and all(text(x) for x in row['openQuestions']) and row['openQuestions'], '未完成编目须写待核问题'
    date = dt.date.fromisoformat(row['reviewedAt'])
    assert dt.date(2026, 10, 29) <= date <= dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date(), '核查日期无效'


def validate_rows(data, games, dossiers, changed):
    works = {w['id'] for w in games['works']}
    people = {p['id']: p for p in data['creators']['people']}
    credits = data['creators']['credits']
    assert len(people) == len(data['creators']['people']), '个人 ID 重复'
    assert len({c['id'] for c in credits}) == len(credits), '署名 ID 重复'
    for resource, key in changed:
        row = value(data, resource, key)
        if resource == 'editorial':
            assert key in works, '编目必须引用主库作品'
            validate_editorial(row)
        elif resource == 'people':
            assert set(row) == {'id', 'name', 'alias', 'mark', 'roles'}, '个人字段不正确'
            assert row['id'] == key and ID.fullmatch(key) and text(row['name'], maximum=150)
            assert isinstance(row['roles'], list) and row['roles'] and set(row['roles']) <= ROLES
            assert len(row['roles']) == len(set(row['roles'])) and text(row['mark']) and isinstance(row['alias'], str)
        elif resource == 'credits':
            assert set(row) == {'id', 'workId', 'personId', 'role', 'label', 'source', 'note', 'status', 'scopeLabel', 'scope'}, '署名字段不正确'
            assert row['id'] == key and ID.fullmatch(key)
            assert row['workId'] in works and row['personId'] in people
            assert row['role'] in ROLES and row['role'] in people[row['personId']]['roles']
            assert row['status'] == 'sourceReviewed' and source_url_valid(row['source'])
            assert all(text(row[f]) for f in ('label', 'note', 'scopeLabel'))
            scope = row['scope']
            assert isinstance(scope, dict) and scope.get('type') in {'release', 'documentedWork', 'externalEdition'}
            if scope['type'] == 'release':
                assert set(scope) == {'type', 'releaseId'}
                assert any(r['id'] == scope['releaseId'] and r['workId'] == row['workId'] for r in games['platformReleases']), '署名引用其他作品发行'
            elif scope['type'] == 'externalEdition':
                assert set(scope) == {'type', 'year', 'platform', 'label'}
                first_year = next(w['firstYear'] for w in games['works'] if w['id'] == row['workId'])
                assert type(scope['year']) is int and first_year <= scope['year'] <= dt.date.today().year
                assert text(scope['platform']) and text(scope['label'])
            else:
                assert set(scope) == {'type', 'label'} and text(scope['label'])
        else:
            assert key in works and isinstance(row, list) and row, '说明必须引用主库作品'
            assert len({n['title'] for n in row}) == len(row), '说明标题重复'
            for n in row:
                assert set(n) == {'title', 'text', 'source', 'dossierId', 'anchor'}
                assert text(n['title']) and text(n['text'], 10) and source_url_valid(n['source'])
                assert n['dossierId'] in dossiers and re.fullmatch(r'[a-zA-Z0-9_-]+', n['anchor'])
    for c in credits:
        assert c['personId'] in people and c['role'] in people[c['personId']]['roles'], '个人职责与已有署名不一致'


def apply_package(package, current, games, baseline, dossiers):
    assert isinstance(package, dict) and set(package) == {'schemaVersion', 'createdAt', 'reason', 'operations'}, '更新包结构无效'
    assert package['schemaVersion'] == 1 and text(package['reason'], maximum=2000), '需要修改说明'
    dt.date.fromisoformat(package['createdAt'])
    ops = package['operations']
    assert isinstance(ops, list) and 0 < len(ops) <= 30, '一次提交1至30项记录'
    changed = []
    result = copy.deepcopy(current)
    for op in ops:
        assert isinstance(op, dict) and set(op) == {'resource', 'key', 'before', 'after'}, '更新项字段无效'
        resource, key = op['resource'], op['key']
        assert resource in PATHS and isinstance(key, str) and ID.fullmatch(key), '不允许的资源或记录 ID'
        assert (resource, key) not in changed, '同一记录不能重复修改'
        assert op['after'] is not None, '不支持删除历史记录'
        assert value(current, resource, key) == op['before'], f'{resource}/{key}: 数据库已变化，请重新载入并核对'
        if resource == 'editorial':
            assert key not in baseline['works'], '最初八部编目须走独立审查，请添加补充说明'
        elif resource == 'credits':
            assert op['before'] is None, '已有署名订正须走独立审查，请添加补充说明'
        elif resource == 'notes':
            old = op['before'] or []
            assert isinstance(op['after'], list) and op['after'][:len(old)] == old and len(op['after']) > len(old), '只允许追加说明，不覆盖历史说明'
        elif resource == 'people' and op['before']:
            assert {k: v for k, v in op['before'].items() if k != 'roles'} == {k: v for k, v in op['after'].items() if k != 'roles'}, '已有个人身份不可覆盖'
            assert set(op['before']['roles']) <= set(op['after']['roles']), '不能移除已有职责'
        assign(result, resource, key, op['after'])
        changed.append((resource, key))
    validate_rows(result, games, dossiers, changed)
    return result


def apply_file(path, root=ROOT):
    raw = Path(path).read_text(encoding='utf-8')
    assert len(raw) <= 60000, '更新包超过60000字符，请分批'
    package = json.loads(raw)
    current = load(root)
    games = read('games.json', root)
    baseline = read('narrative-editorial-baseline-20261029.json', root)
    dossiers = {d['id'] for d in read('entity-catalogue.json', root)['model']['dossiers']}
    result = apply_package(package, current, games, baseline, dossiers)
    history = read('management-history.json', root)
    restore_historical(current, history)  # Detect unexpected edits to a managed record.
    history['batches'].append({**package, 'actor': os.environ.get('GITHUB_ACTOR', 'local-review')})
    today = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date().isoformat()
    result['editorial']['updatedAt'] = today
    result['creators']['updated'] = today
    result['notes']['updated'] = today
    outputs = {PATHS['editorial']: result['editorial'], PATHS['notes']: result['notes'],
               PATHS['people']: result['creators'], 'management-history.json': history}
    # Keep the frozen review scope while updating its live completion counts.
    report = read('narrative-cataloguing-20261030.json', root)
    counts = dict(complete=0, partial=0, missing=0)
    for wid in report['countedWorkIds']:
        row = result['editorial']['works'].get(wid, {})
        n = sum(bool(row.get(f)) for f in FIELDS)
        counts['complete' if n == 4 else 'partial' if n else 'missing'] += 1
    report['counts'] = counts
    outputs['narrative-cataloguing-20261030.json'] = report
    for name, content in outputs.items():
        (root / 'data' / name).write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Applied {len(package['operations'])} reviewed changes; complete repository checks are still required.")


def validate_history(root=ROOT):
    current = load(root)
    history = read('management-history.json', root)
    assert set(history) == {'schemaVersion', 'batches'} and history['schemaVersion'] == 1
    restored = restore_historical(current, history)
    games = read('games.json', root)
    baseline = read('narrative-editorial-baseline-20261029.json', root)
    dossiers = {d['id'] for d in read('entity-catalogue.json', root)['model']['dossiers']}
    for batch in history['batches']:
        assert text(batch['actor'])
        restored = apply_package({k: v for k, v in batch.items() if k != 'actor'}, restored, games, baseline, dossiers)
    for resource in PATHS:
        keys = {op['key'] for b in history['batches'] for op in b['operations'] if op['resource'] == resource}
        for key in keys:
            assert value(restored, resource, key) == value(current, resource, key)
    print(f"Management history validated: {len(history['batches'])} batches")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('package', nargs='?')
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        validate_history()
    elif args.package:
        apply_file(args.package)
    else:
        parser.error('Provide a package path, or --check')
