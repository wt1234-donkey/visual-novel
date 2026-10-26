"""Produce claim-level decisions from the frozen five-phase queue.

The screening log records retrieval only; it never upgrades a dossier role.
"""
import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / 'data/entity-verification-evidence-index-20261026.json'
SCREEN = ROOT / 'data/entity-verification-source-screen-20261026.json'
REVIEW = ROOT / 'data/entity-verification-five-phase-review-20261026.json'
AUDIT = ROOT / 'data/entity-verification-five-phase-audit-20261026.json'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def baseline(tree, name):
    return json.loads(subprocess.check_output(['git', 'show', f'{tree}:data/{name}'], cwd=ROOT))


CORRECTIONS = [
    {'reviewId': 'AZR-P1-I01', 'entityId': 'entity-name-b8b1293f82fa',
     'rawName': 'Alchemist', 'type': 'company', 'status': 'sourceReviewed',
     'sources': ['https://www.comiket.co.jp/info-a/C66/C66kigyo/List_A.html'],
     'note': '同期C66企业展位原件明确列株式会社アルケミスト及《月は東に日は西に》家用版。核定历史发行署名所指为公司；直接逐作支持g265，其他原作、移植和制作职责仍各待原件。'},
    {'reviewId': 'AZR-P1-I02', 'entityId': 'entity-name-788994ba8dfb',
     'rawName': 'American Laser Games', 'type': 'company', 'status': 'sourceReviewed',
     'sources': ['https://manuals.plus/m/051d6e54fb3d36dc96349bce8efcc7244213e20623a258218df168fc34d068fc'],
     'note': '1993年Sega CD《Mad Dog McCree》原版说明书保修条款由American Laser Games, Inc.承担，版权标1990及1993；核定此历史署名为公司。续作只在同页商标清单出现，不能据此推断其制作或版本职责。'},
    {'reviewId': 'AZR-P2-I01', 'entityId': 'entity-name-3de89d1ab0a5',
     'rawName': 'IMYUIC(ALICESOFT)', 'type': 'brand', 'status': 'sourceReviewed',
     'preserveReleaseRoles': True,
     'sources': ['https://www.alicesoft.com/information/2022/entry003001.html'],
     'note': 'ALICESOFT在2022年公告明确称IMYUIC(ALICESOFT)是其管辖已发行作品的品牌／社团名称，并指名HENTAI LABYRINTH；这是后改的标记，不倒填作品原发时的品牌或开发职责。保留旧发行publisher及其角色。'},
]

DIRECT = {
    ('entity-name-b8b1293f82fa', 'g265'): 'E-P1-ALCHEMIST-C66',
    ('entity-name-788994ba8dfb', 'g1198'): 'E-P1-ALG-MANUAL',
    ('entity-name-3de89d1ab0a5', 'alicesoft-extra-hentailabyrinth'): 'E-P2-IMYUIC-2022',
}
EVIDENCE = [
    {'evidenceId': 'E-P1-ALCHEMIST-C66', 'url': CORRECTIONS[0]['sources'][0],
     'location': 'C66企业展位列表，441号株式会社アルケミスト',
     'scope': {'workId': 'g265', 'role': 'companyIdentityAndConsumerEditionPromotion'},
     'limit': '不能推定2003／2012其他作品制作，亦不证明该展位经营所有历史版本'},
    {'evidenceId': 'E-P1-ALG-MANUAL', 'url': CORRECTIONS[1]['sources'][0],
     'location': 'Sega CD说明书，90 Day Limited Warranty及版权声明',
     'scope': {'workId': 'g1198', 'role': 'historicalCompanyIdentityAndWarranty'},
     'limit': '1990街机版开发分工及g1199续作制作不能从保修与商标清单推定'},
    {'evidenceId': 'E-P2-IMYUIC-2022', 'url': CORRECTIONS[2]['sources'][0],
     'location': '2022-05-30品牌完全独立公告，已发行商品品牌表记与HENTAI LABYRINTH段落',
     'scope': {'workId': 'alicesoft-extra-hentailabyrinth', 'role': 'retrospectiveBrandIdentity'},
     'limit': '2022更名不证明旧版当时的名义或游戏内部开发'},
]


def build():
    queue, screen = read(QUEUE), read(SCREEN)
    assert queue['baselineTree'] == '025762765317e2e71b1889fb4f95e164d8588b75'
    old_org = baseline(queue['baselineTree'], 'organizations.json')
    old_review = read(ROOT / 'data/entity-creator-a-recheck1-review-20261026.json')
    original = {r['entityId']: r for r in old_org['registrationProgress']['reviewedEntities']}
    original.update({r['entityId']: r for r in old_review['reviewedEntities']})
    correction = {c['entityId']: c for c in CORRECTIONS}
    queue_rows = old_review['recheckProgress']['baselineQueue']
    all_ids = [q['entityId'] for q in queue_rows]
    assert all_ids[:5] == old_review['recheckProgress']['processedEntityIds']
    reviewed, deferred = [], []
    for q in queue_rows[5:]:
        eid = q['entityId']
        item = original[eid]
        resolved = eid in correction
        reviewed.append({'entityId': eid, 'name': q['name'],
                         'status': 'identityResolved' if resolved else 'identityDeferred',
                         'sources': correction[eid]['sources'] if resolved else item['sources'],
                         'reason': correction[eid]['note'] if resolved else item['reason'],
                         'workIds': item['workIds']})
    for q in queue_rows[2:]:
        eid = q['entityId']
        if eid in correction:
            continue
        item = original[eid]
        deferred.append({'entityId': eid, 'status': 'awaitOriginalIdentityAndVersionScope',
                         'sources': item['sources'], 'reason': item['reason'],
                         'missingEvidence': f"{q['name']}在相应时期的原版版权页／法人登记及逐版本署名",
                         'workIds': item['workIds']})
    review = {'schemaVersion': 1, 'reviewedAt': '2026-10-26',
              'baseCommit': queue['baselineCommit'], 'audit': 'data/entity-verification-five-phase-audit-20261026.json',
              'previousReview': 'data/entity-creator-a-recheck1-review-20261026.md',
              'policy': '按冻结字母队列完成五段证据审查；处理不等于证实。仅有直接原件者改身份，发行与专题职责独立。',
              'identityCorrections': [{**c, 'before': {'type': 'unknown', 'verification': 'unresolved'}} for c in CORRECTIONS],
              'creditAdditions': [], 'deferredReviews': deferred, 'reviewedEntities': reviewed,
              'recheckProgress': {**old_review['recheckProgress'],
                                  'letter': '全部五段', 'processedEntityIds': all_ids,
                                  'nextEntityId': None, 'nextName': None}}
    lead = {x['url']: x for x in screen['sources']}
    assert len(lead) == 47
    decisions = []
    for phase in queue['phases']:
        for w in queue['works']:
            for c in w['identityClaims'] + w['roleClaims']:
                if c['phase'] != phase['id']:
                    continue
                wid, rels = w['workId'], w['releaseContextIds']
                if 'entityId' in c:
                    item = original[c['entityId']]
                    evidence = DIRECT.get((c['entityId'], wid))
                    decisions.append({'claimId': c['claimId'], 'phase': phase['id'],
                                      'workId': wid, 'title': w['title'],
                                      'releaseContextIds': rels, 'decision': 'confirmed' if evidence else 'deferred',
                                      'evidenceIds': [evidence] if evidence else [],
                                      'finding': '历史主体类型获原件直接支持；未新增逐作开发职责' if evidence else item['reason'],
                                      'missingEvidence': None if evidence else
                                      f"《{w['title']}》当期版本版权页、手册或发行公告，需明确「{c['name']}」的历史主体及职责"})
                else:
                    url = c['sourceLead']
                    decisions.append({'claimId': c['claimId'], 'phase': phase['id'],
                                      'workId': wid, 'title': w['title'],
                                      'dossierId': c['dossierId'], 'dossierName': c['dossierName'],
                                      'placement': c['placement'], 'releaseContextIds': rels,
                                      'decision': 'deferred', 'evidenceIds': [],
                                      'screenedLead': url, 'leadAccess': lead[url]['status'],
                                      'finding': '既有目录／馆藏／沿革链接未证明本专题在该作品及版本的具体制作职责',
                                      'missingEvidence': f"《{w['title']}》原版包装／说明书／片尾职员表（{'、'.join(rels) if rels else '书目所指原版，尚无发行ID'}）中「{c['dossierName']}」的具名职责与适用版本"})
    assert len(decisions) == 656 and len({d['claimId'] for d in decisions}) == 656
    assert [d['phase'] for d in decisions] == sorted(d['phase'] for d in decisions)
    by_phase = defaultdict(Counter)
    for d in decisions:
        by_phase[d['phase']][d['decision']] += 1
    audit = {'schemaVersion': 1, 'reviewedAt': '2026-10-26',
             'baselineCommit': queue['baselineCommit'], 'baselineTree': queue['baselineTree'],
             'scope': '五段逐claim审查；检索线索检查不等于逐作核实。保留未经原件支持的身份和专题职责。',
             'sourceScreen': 'data/entity-verification-source-screen-20261026.json',
             'sourceScreenCounts': dict(Counter(x['status'] for x in screen['sources'])),
             'evidence': EVIDENCE,
             'phaseResults': [{'phase': p['id'], 'newIdentityEntities': len(p['newIdentityIds']),
                               'carryoverIdentityEntities': len(p['carryoverIdentityIds']),
                               'decisions': dict(by_phase[p['id']])} for p in queue['phases']],
             'counts': dict(Counter(d['decision'] for d in decisions)),
             'decisions': decisions}
    return review, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, data in zip((REVIEW, AUDIT), build()):
        content = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if args.check:
            assert path.read_text(encoding='utf-8') == content, f'{path.name} not synchronized'
        else:
            path.write_text(content, encoding='utf-8')
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
