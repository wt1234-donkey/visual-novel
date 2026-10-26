"""Freeze a claim-preserving, work-deduplicated plan for the second review pass."""
import argparse
import hashlib
import json
import subprocess
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data/entity-verification-evidence-index-20261026.json'
BASE_COMMIT = '27e7339c4ceb2e7ea2a42fc95b8cd2ab0c166cec'
BASE_TREE = '025762765317e2e71b1889fb4f95e164d8588b75'


def read(name):
    # The evidence queue is an immutable pre-review snapshot. Later corrections
    # must not erase the original claim IDs or make the queue self-fulfilling.
    raw = subprocess.check_output(['git', 'show', f'{BASE_TREE}:data/{name}'], cwd=ROOT)
    return json.loads(raw)


def phase_for_dossier(name):
    folded = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode().lower()
    initial = folded[:1]
    if initial and initial in 'ab':
        return 'P1'
    if initial and initial in 'cdefghi':
        return 'P2'
    if initial and initial in 'jklm':
        return 'P3'
    if initial and initial in 'nopqrs':
        return 'P4'
    return 'P5'


def build():
    model, credits, org, games, coverage = [read(name) for name in
                                            ['entities.json', 'credits.json', 'organizations.json',
                                             'games.json', 'company-coverage.json']]
    entities = {e['id']: e for e in model['entities']}
    dossiers = {d['id']: d for d in model['dossiers']}
    unknown = {eid for eid, e in entities.items() if e['verification'] == 'unresolved'}
    queue = org['recheckProgress']['baselineQueue']
    assert len(queue) == 39 and len(unknown) == 36
    assert org['recheckProgress']['processedEntityIds'] == [e['entityId'] for e in queue[:5]]
    windows = [('P1', 'A—B', 5, 11), ('P2', 'C—I', 11, 20),
               ('P3', 'J—M', 20, 28), ('P4', 'N—S', 28, 33),
               ('P5', 'T—X、数字及其他', 33, 39)]
    phase_identity = {phase: [e['entityId'] for e in queue[start:end]]
                      for phase, _, start, end in windows}
    # Already reviewed but unresolved: include in the first evidence sweep without
    # resetting or reordering the published 5/39 progress.
    phase_identity['P1'] = [e['entityId'] for e in queue[2:4]] + phase_identity['P1']
    assert set().union(*(set(ids) for ids in phase_identity.values())) == unknown
    identity_phase = {eid: phase for phase, ids in phase_identity.items() for eid in ids}

    release_ids = defaultdict(set)
    for r in games['platformReleases']:
        release_ids[r['workId']].add(r['id'])
    for company in coverage['companies']:
        for field in ('relatedGames', 'dossierOnlyWorks'):
            for work in company.get(field, []):
                for r in work.get('platformReleases', []):
                    release_ids[r['workId']].add(r['id'])

    identity_credits = defaultdict(list)
    for credit in credits['credits']:
        if credit['entityId'] in unknown:
            identity_credits[(credit['entityId'], credit['workId'])].append(credit)
    roles = [m for m in credits['dossierMemberships'] if m['status'] == 'pendingRole']
    assert len(roles) == len({(m['dossierId'], m['workId']) for m in roles}) == 601
    identity_by_work, role_by_work = defaultdict(list), defaultdict(list)
    source_claims = defaultdict(lambda: {'identityClaimIds': set(), 'roleClaimIds': set(), 'workIds': set()})

    for (eid, wid), rows in sorted(identity_credits.items()):
        cid = f'identity:{eid}:{wid}'
        leads = sorted(set(entities[eid]['sources']) | {c['source'] for c in rows})
        claim = {'claimId': cid, 'entityId': eid, 'name': entities[eid]['name'],
                 'phase': identity_phase[eid], 'currentType': 'unknown',
                 'question': '当期署名对应的公司、品牌、团队或出版名义；分别核对具体参与职责',
                 'currentCredits': [{'creditId': c['id'], 'targetType': c['targetType'],
                                     'targetId': c['targetId'], 'role': c['role'],
                                     'rawCredit': c['rawCredit']} for c in rows],
                 'sourceLeads': leads, 'decision': 'unreviewed'}
        identity_by_work[wid].append(claim)
        for url in leads:
            source_claims[url]['identityClaimIds'].add(cid)
            source_claims[url]['workIds'].add(wid)

    for m in sorted(roles, key=lambda x: (x['workId'], x['dossierId'])):
        wid, dossier = m['workId'], dossiers[m['dossierId']]
        cid = f"role:{m['dossierId']}:{wid}"
        claim = {'claimId': cid, 'dossierId': m['dossierId'], 'dossierName': dossier['name'],
                 'entityIds': dossier['entityIds'], 'phase': phase_for_dossier(dossier['name']),
                 'placement': m['placement'], 'currentRoles': m['roles'],
                 'question': '本专题在此作品的具名职责及原作、增补内容或具体发行的适用范围',
                 'sourceLead': m['source'], 'decision': 'unreviewed'}
        role_by_work[wid].append(claim)
        source_claims[m['source']]['roleClaimIds'].add(cid)
        source_claims[m['source']]['workIds'].add(wid)

    identity_works, role_works = set(identity_by_work), set(role_by_work)
    works = []
    for wid in sorted(identity_works | role_works):
        info = org['works'][wid]
        identity_claims, role_claims = identity_by_work.get(wid, []), role_by_work.get(wid, [])
        claims = identity_claims + role_claims
        works.append({'workId': wid, 'title': info['title'], 'originalTitle': info.get('originalTitle'),
                      'placement': info['placement'], 'year': info['year'],
                      'releaseContextIds': sorted(release_ids[wid]),
                      'identityClaims': identity_claims, 'roleClaims': role_claims,
                      'phaseIds': sorted({c['phase'] for c in claims}),
                      'sourceLeadUrls': sorted(set(url for c in claims for url in
                                                  (c.get('sourceLeads') or [c['sourceLead']]))),
                      'decision': 'unreviewed'})

    ledger = [{'sourceId': 'lead-' + hashlib.sha256(url.encode()).hexdigest()[:12],
               'url': url, 'identityClaimIds': sorted(refs['identityClaimIds']),
               'roleClaimIds': sorted(refs['roleClaimIds']), 'workIds': sorted(refs['workIds']),
               'status': 'leadOnly', 'warning': '既有URL仅供定位原件；未逐项证明身份、工种或发行范围'}
              for url, refs in sorted(source_claims.items())]
    phases = []
    for phase, label, start, end in windows:
        phase_roles = [m for m in roles if phase_for_dossier(dossiers[m['dossierId']]['name']) == phase]
        affected = [w for w in works if phase in w['phaseIds']]
        phases.append({'id': phase, 'label': label, 'newIdentityIds': [x['entityId'] for x in queue[start:end]],
                       'carryoverIdentityIds': [x['entityId'] for x in queue[2:4]] if phase == 'P1' else [],
                       'pendingRoleClaims': len(phase_roles), 'affectedWorkIds': [w['workId'] for w in affected],
                       'sourceLeadIds': [s['sourceId'] for s in ledger if any(wid in s['workIds'] for wid in
                                                                              (w['workId'] for w in affected))]})
    counts = (len(identity_by_work), len(identity_credits), len(role_by_work),
              len(identity_works & role_works), len(works))
    assert counts == (53, 55, 586, 21, 618), counts
    assert len({m['source'] for m in roles}) == 47
    assert sum(x['pendingRoleClaims'] for x in phases) == 601
    return {'schemaVersion': 1, 'snapshotDate': '2026-10-26',
            'baselineCommit': BASE_COMMIT, 'baselineTree': BASE_TREE,
            'policy': '核查计划快照，不是新事实或已核证据。去重仅用于一次读取原件；每项身份／职责仍有独立决定。',
            'counts': {'initialIdentityQueue': 39, 'alreadyReviewed': 5, 'unresolvedIdentityEntities': 36,
                       'unresolvedIdentityClaims': 55, 'unresolvedIdentityWorks': 53,
                       'pendingRoleClaims': 601, 'pendingRoleWorks': 586,
                       'overlapWorks': 21, 'uniqueWorks': 618,
                       'existingPendingRoleSourceLeads': 47, 'combinedSourceLeads': len(ledger)},
            'phases': phases, 'sourceLedger': ledger, 'works': works}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output = json.dumps(build(), ensure_ascii=False, indent=2) + '\n'
    if args.check:
        assert OUTPUT.read_text(encoding='utf-8') == output, f'{OUTPUT.name} 未同步'
    else:
        OUTPUT.write_text(output, encoding='utf-8')
    print(OUTPUT.relative_to(ROOT))


if __name__ == '__main__':
    main()
