"""List explicit unresolved states and missing registrations without changing them."""
from collections import Counter, defaultdict


def attach_unfinished(data, model, credits):
    kinds = {
        'identity': {'label': '主体身份待核', 'description': '正式档案尚未区分法人、品牌或联合署名。', 'action': '补原版版权页、同期公司公告或登记材料，核定主体类型。'},
        'duty': {'label': '正式专题职责待核', 'description': '专题仍是关联记录；已有台账证据不自动等于正式职责已写入。', 'action': '对照已整理证据，逐作品／内容／发行ID核定职责与适用范围，再完成正式审核。'},
        'creation': {'label': '创作依据尚未登记', 'description': '主库作品尚无已登记的直接原作制作、开发、联合制作或制作品牌记录。', 'action': '补原作职员表、制作方公告或具名创作资料，区分原作开发与发行、移植。'},
        'evidence': {'label': '台账证据待补或有限定', 'description': '仍待核、证据冲突、部分证据、限版确认分别保留，不统一解释为全无证据。', 'action': '按本条具体问题与版次限制补证。'},
        'relation': {'label': '组织关系待核', 'description': '页面已有待核连线，尚不能确认其法律或人员沿革。', 'action': '补当事方原公告、人员独立及组织连续性材料，核定关系类型与时间。'},
        'chronology': {'label': '沿革时间待补', 'description': '已登记关系或更名的起止时间仍未核；未知终点不代表持续至今。', 'action': '补品牌启用、运营起止或更名的原始公告；仅核实已取得证据的时段。'},
    }
    actions = {'仍待核': '取得能直接对应这部作品和版次的原件；未取得前保留待核。',
               '证据冲突': '并列冲突来源，查原版版权页／当期资料，解决主体、日期或职责差异。',
               '部分证据': '补足具体法人、开发工种、发行版次或原版版权页，不把关联线索视作完整确认。',
               '限版确认': '将证据映射到已指明的平台／地区／年代；冻结范围中其余版次继续逐项核对。'}
    nodes = {n['id']: n for n in data['nodes']}
    dossiers = {d['id']: d for d in model['dossiers']}
    claims = defaultdict(list)
    for ref, record in data['verificationLedger']['records'].items():
        claims[record['entityId'], record['workId']].append(ref)
    items = []
    for node in data['nodes']:
        if not node.get('previewOnly') and node.get('verification') == 'unresolved':
            items.append({'id': 'identity:' + node['id'], 'kind': 'identity',
                          'entityIds': [node['id']], 'status': '身份待核'})
    for membership in credits['dossierMemberships']:
        if membership['status'] != 'pendingRole' and membership['group'] != 'unresolved':
            continue
        dossier = dossiers[membership['dossierId']]
        refs = sorted({ref for eid in dossier['entityIds'] for ref in claims[eid, membership['workId']]})
        items.append({'id': 'duty:' + membership['dossierId'] + ':' + membership['workId'],
                      'kind': 'duty', 'entityIds': dossier['entityIds'], 'workId': membership['workId'],
                      'dossierId': dossier['id'], 'dossierName': dossier['name'],
                      'recordIds': refs, 'source': membership['source'], 'status': '正式职责待核'})
    created = {row['workId'] for node in data['nodes'] for row in node.get('groups', {}).get('creation', [])}
    participants = defaultdict(set)
    for row in credits['credits']:
        participants[row['workId']].add(row['entityId'])
    for wid, work in data['works'].items():
        if work['placement'] == 'main' and wid not in created:
            items.append({'id': 'creation:' + wid, 'kind': 'creation', 'workId': wid,
                          'entityIds': sorted(participants[wid]), 'status': '未登记直接创作依据'})
    for ref, record in data['verificationLedger']['records'].items():
        if record['status'] in actions:
            items.append({'id': 'evidence:' + ref, 'kind': 'evidence', 'recordId': ref,
                          'entityIds': [record['entityId']], 'workId': record['workId'],
                          'status': record['status']})
    for edge in data['edges']:
        if edge['status'] in ['pending', 'unresolved']:
            kind, status = 'relation', '关系待核'
        elif '未核' in edge['dateLabel'] or '待核' in edge['dateLabel']:
            kind, status = 'chronology', '起止时间待补'
        else:
            continue
        items.append({'id': 'edge:' + edge['id'], 'kind': kind, 'edgeId': edge['id'],
                      'entityIds': [edge['parent'], edge['child']], 'status': status})
    for history in data['nameHistory']:
        if '未核' in history['dateLabel'] or '待核' in history['dateLabel']:
            items.append({'id': 'history:' + history['id'], 'kind': 'chronology',
                          'historyId': history['id'], 'entityIds': sorted({history['fromId'], history['toId']}),
                          'status': '更名时间待补'})
    assert len({row['id'] for row in items}) == len(items)
    for row in items:
        assert all(eid in nodes for eid in row['entityIds'])
        assert not row.get('workId') or row['workId'] in data['works']
    data['unfinished'] = {'kinds': kinds, 'statusActions': actions, 'items': items,
                          'counts': dict(Counter(row['kind'] for row in items)),
                          'totalItems': len(items), 'sourceRound': data['verificationLedger']['source']['round'],
                          'note': '不同清单可能涉及同一作品，数量不能相加作为未完成作品总数。台账状态、正式身份／职责与未登记记录分别统计。'}
    return data
