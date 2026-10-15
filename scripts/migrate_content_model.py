"""One-time, conservative migration of the published v1 catalogue.

Run only against schema v1. Content relationships are explicit editorial decisions,
not inferred from platform names, the word 'remake', or unreviewed keyword matches.
Unresolved historical releases remain searchable without inflating content counts.
"""
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode()).hexdigest()


# Reviewed existing difference notes: each group is ONE content increment.
# Platform copies and subsequent ports of the SAME increment share its ID.
ADDED_GROUPS = """
g089-v2
g085-v2
g040-v2
g038-v2
g039-v3
g055-v2 g055-v3 g055-v4
g056-v3 g056-v4 g056-v5
g047-v2 g047-v3 g047-v4
g012-v3
g046-v4 g046-v5
g146-v2
g156-v2 g156-v4
g162-v2
g166-v2
g183-v3
g148-v5
g147-v4 g147-v5
g192-v3
g205-v2
g206-v3 g206-v4
g207-v3 g207-v4
g205-v10
g206-v5
g207-v5
g222-v2
g233-v3
g233-v4
g239-v5
g240-v5
g241-v4
g242-v4
g267-v2
g271-v2
g277-v2 g277-v4
g286-v2
g334-v2
g334-v3 g334-v4
g024-v3
g025-v3
g159-v4
g395-v4
g430-v2
g450-v1
g306-v6
g501-v2
g510-v2
g545-v2
g597-v6
g618-v3
g054-v20 g054-v21 g054-v22 g054-v23
g600-v3 g600-v4
g625-v2
g646-v2 g646-v3
g647-v3
g651-v3 g651-v4
g673-v2
g689-v4
g714-v3
g815-v4 g815-v5
g823-v2
g825-v3
g830-v3
g830-v4
g830-v8
g837-v4
g840-v2 g840-v3
g869-v4
g876-v2 g876-v3
g878-v2
g886-v2
g887-v2
g889-v2 g889-v6
g886-v3
g887-v3
g888-v3
g889-v3
g886-v4
g886-v5
g887-v4
g888-v4 g888-v5
g900-v3
g900-v6
g900-v12
g901-v5 g901-v6 g901-v7
g904-v3
g904-v4
g904-v5
g913-v2
g915-v2
g916-v2
g918-v2
g920-v2
g921-v2
g921-v3
g923-v2
g928-v2
g934-v2
g135-v2
g135-v3
g936-v3
g937-v2
g937-v3
g938-v2
g939-v2
g940-v2
g940-v3
g940-v4
g940-v5
g940-v6
g940-v7
g940-v8
g941-v2
g941-v3
g941-v4
g023-v4
g177-v2
g177-v3
g177-v4
g177-v5
g942-v2
g948-v2
g959-v2
g959-v3
g959-v4
g010-v2
g963-v2
g963-v3
g963-v4
g965-v2
g965-v3
g971-v2
g971-v3
g971-v4
g971-v5
g972-v2
g987-v2
g990-v2
g992-v2
g993-v2
g993-v3
g995-v2
g995-v3
g995-v4
g995-v5
g995-v6
g995-v7
g995-v8
g995-v9
g995-v10
g113-v4
g1040-v2
g1040-v3
g1041-v2
g1042-v2
g1042-v3
g1042-v4
g1042-v5
g1042-v6
g1042-v7
g1042-v8
g1042-v9
g1042-v10
g1042-v11
g1042-v12
g1042-v13
g1042-v14
g1043-v2
g1045-v2
g1046-v2
g1047-v2
g1047-v3
g1049-v2
g1050-v2
g1050-v3
g1050-v4
g1053-v2
g1053-v3
g1056-v2
g1056-v3
g1056-v4
g1056-v5
g1057-v2
g1057-v3
g1057-v4
melbournehouse-kknd-v2
koei-ange-v2
koei-ange-v3
koei-ange-v4
koei-trois-v2
koei-c2-v2
koei-c2-v3
koei-c2-v4
koei-c2-v5
koei-cencore-v2
koei-c3-v2
koei-c3-v3
koei-c3-v4
koei-c4-v2
koei-c4-v3
koei-gitaroo-v2
"""

# Explicitly established content identities, independent of release year/platform.
SAME_GROUPS = """
g170-v1 g170-v2
g619-v1 g619-v2
key-rpg-hbr-v1 key-rpg-hbr-v2
key-card-mission-v1 key-card-mission-v2
key-collection-v1 key-collection-v2
key-operation-wars-v1 key-operation-wars-v2
key-ignis-v1 key-ignis-v2
sprite-eternal-sky-v1 sprite-eternal-sky-v2
"""


def migrate(data, coverage):
    assert 'versions' in data and 'contentVersions' not in data, '仅可对 v1 执行一次迁移'
    manifest = {'schemaVersion': 2, 'sourceRepository': 'wt1234-donkey/visual-novel',
                'sourceCommit': '9505ca75ab27280bd559354f82ea8d83f8553a7c',
                'works': {}, 'releases': {}, 'relatedWorks': {}, 'relatedReleases': {}}
    all_rows, collections = {}, []
    for work in data['works']:
        manifest['works'][work['id']] = digest(work)
    groups = [(data, data['works'], data.pop('versions'), 'releases')]
    for company in coverage['companies']:
        for work in company.get('relatedGames', []):
            rows = work.pop('versions')
            manifest['relatedWorks'][work['id']] = digest(work)
            groups.append((work, [work], rows, 'relatedReleases'))
    for container, works, rows, manifest_key in groups:
        for index, row in enumerate(rows, 1):
            wid = row.get('workId', works[0]['id'])
            rid = row.get('id', f'{wid}-v{index}')
            assert rid not in all_rows, f'发行 ID 冲突: {rid}'
            manifest[manifest_key][rid] = {'keys': list(row), 'sha256': digest(row)}
            row.setdefault('id', rid)
            row.setdefault('workId', wid)
            row['contentVersionId'] = None
            row['contentRelation'] = 'unverified'
            row['contentNote'] = '旧资料未完成逐版内容对照；保留发行证据，不推定新增内容或与原版完全相同。'
            row['releaseRole'] = 'legacy'
            all_rows[rid] = row
        container['platformReleases'] = rows
        container['contentVersions'] = []
        collections.append((container, works))
    used = set()
    def content(container, work, members, basis):
        seed = min(members, key=lambda v: (v['year'], v['id']))
        cid = f"{work['id']}-c-{seed['id'].rsplit('-v', 1)[-1]}" if basis == 'added' else f"{work['id']}-c-original"
        c = {'id': cid, 'workId': work['id'], 'label': seed['kind'] if basis == 'added' else '原作／首批内容',
             'firstYear': min(v['year'] for v in members), 'basis': basis,
             'evidence': seed['differences'], 'source': seed['source'],
             'evidenceReleaseIds': [v['id'] for v in members],
             'addedContent': ([{'description': seed['differences'], 'source': seed['source']}]
                              if basis == 'added' else [])}
        if basis == 'added':
            c['comparedTo'] = f"{work['id']}-c-original"
        container['contentVersions'].append(c)
        for row in members:
            row['contentVersionId'] = cid
            row['contentRelation'] = 'original' if basis == 'original' else 'added'
            row['contentNote'] = '原作／首批已核内容。' if basis == 'original' else '内容差异见所关联内容版本及原发行依据；多平台不重复计数。'
            used.add(row['id'])
    for container, works in collections:
        for work in works:
            rows = [r for r in container['platformReleases'] if r['workId'] == work['id']]
            first = min(rows, key=lambda v: (v['year'], rows.index(v)))
            content(container, work, [first], 'original')
    for line in ADDED_GROUPS.strip().splitlines():
        members = [all_rows[rid] for rid in line.split()]
        wid = members[0]['workId']
        assert all(r['workId'] == wid for r in members)
        # A row may be the earliest known original rather than an increment.
        if any(r['id'] in used for r in members):
            assert len(members) == 1
            continue
        container, works = next((c, ws) for c, ws in collections if any(w['id'] == wid for w in ws))
        content(container, next(w for w in works if w['id'] == wid), members, 'added')
    for line in SAME_GROUPS.strip().splitlines():
        members = [all_rows[rid] for rid in line.split()]
        cid = members[0]['contentVersionId']
        assert cid and all(m['workId'] == members[0]['workId'] for m in members)
        for row in members[1:]:
            row['contentVersionId'] = cid
            row['contentRelation'] = 'same'
            row['contentNote'] = '既有资料明确同一内容／服务；仅记录平台发行，不新增内容版本。'
    data['meta']['schemaVersion'] = 2
    data['meta']['updated'] = '2026-10-15'
    data['meta']['repository'] = 'wt1234-donkey/visual-novel'
    data['meta']['versionPolicy'] = {
        'effectiveFrom': '2026-10-15',
        'rule': '作品、内容版本与平台发行分层。每部新作保留原作内容；后续只有明确新增剧情、角色、路线、关卡、美术、音乐或配音才新增内容版本，必须给出具体增量、比较对象与来源。',
        'platformRule': '同内容跨平台、商店上架、翻译、普通移植、再版、合集包装、兼容更新与仅提高分辨率不新增内容版本。以后不主动补录纯平台发行，只记录原作或新增内容的首次发行批次；同批平台关联同一内容ID。',
        'legacyHandling': '历史发行资料完整保留。内容关系未核的发行标记unverified、contentVersionId为空，不计为新增内容版本，也不擅自视为与原版相同。',
        'repository': '以后所有修改、补充、合并及发布仅在wt1234-donkey/visual-novel进行。'}
    coverage['schemaVersion'] = 2
    coverage['recordPolicy'] = data['meta']['versionPolicy']
    return manifest


if __name__ == '__main__':
    data = json.loads((ROOT / 'data/games.json').read_text())
    coverage = json.loads((ROOT / 'data/company-coverage.json').read_text())
    manifest = migrate(data, coverage)
    for path, value in [('data/games.json', data), ('data/company-coverage.json', coverage),
                        ('data/content-migration-baseline.json', manifest)]:
        (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')
    print(Counter(r['contentRelation'] for r in data['platformReleases']))
    print('内容版本', len(data['contentVersions']), '平台发行', len(data['platformReleases']))
