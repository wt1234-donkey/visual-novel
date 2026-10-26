"""Build a scoped, source-led Nitroplus dossier review from the frozen claim IDs."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'data/entity-verification-five-phase-audit-20261026.json'
REVIEW = ROOT / 'data/entity-role-nitroplus-review-20261027.json'
AUDIT = ROOT / 'data/entity-role-nitroplus-audit-20261027.json'
ENTITY = 'entity-nitroplus'
DOSSIER = 'nitroplus'

# One original may support several works; each tuple specifies its actual work,
# role and period. "CoDeveloper" here denotes only the creative work in the note.
PROOFS = {
    'g054': ('coDeveloper', '開発：5pb./ニトロプラス',
             'https://www.nitroplus.co.jp/works/consumer-game',
             'STEINS;GATE 2009 Xbox 360 entry',
             '2009原版共同开发；另据PC目录限定2010 Windows移植开发。5pb.为另一方，不将PC版责任倒填至所有后续平台。'),
    'g611': ('originalProduction', '開発を進めて参りましたWindows用ソフト『ソニコミ』',
             'https://www.nitroplus.co.jp/news/2010/1719.php',
             '2010-10-01 release delay notice, development paragraph',
             '当事方以本社口吻说明正在开发2011年Windows原版；不推广到后发PS3的移植开发。'),
    'g612': ('originalProduction', '開発/発売：ニトロプラス',
             'https://www.nitroplus.co.jp/game/lost_x/',
             '2012 Windows product information, development/sales and staff',
             '2012 Windows原版直接列开发与发行；动画原作权利方另列，不转写为游戏独立原作。'),
    'g613': ('coDeveloper', '企画/開発：星海社/ニトロプラス',
             'https://www.nitroplus.co.jp/game/phenomeno/',
             '2012 download page, works/staff section',
             '2012视觉小说改编的企划／开发由星海社与Nitroplus共同具名，原小说作者等另列。'),
    'g614': ('originalProduction', '当社の開発',
             'https://www.nitroplus.co.jp/game/totono/interview/03.php',
             'contemporary producer and writer interview, opening and development paragraphs',
             '2013年原作制作人员叙述本社制作流程及具体内外分工；外部设计协作不归为本社单独完成。'),
    'g617': ('originalProduction', 'ニトロプラス『みにくいモジカの子』開発・宣伝スタッフ',
             'https://www.nitroplus.co.jp/news/2017/8250.php',
             '2017-12-29 release delay notice, sign-off',
             '当事方延期公告由本作开发与宣传人员联名，确认本社参与2018年PC原作开发；不据此判断后发版本。'),
    'g618': ('originalProduction', '開発・発売：ニトロプラス',
             'https://www.nitroplus.co.jp/pc/lineup/into_15/top.php',
             'original 2008 CHAOS;HEAD product row and staff',
             '2008 Windows原版具名开发／发行；5pb.的剧本及画师另列，后发Xbox版未归为本社移植。'),
    'g619': ('coDeveloper', '協力：ニトロプラス／メカニックデザイン：石渡マコト',
             'https://www.nitroplus.co.jp/works/consumer-game',
             'ROBOTICS;NOTES 2012 console entry',
             '2012原版的联合制作仅指公司具名协力及机械设计，不声称完整程序开发或后发移植。'),
    'g621': ('coDeveloper', '脚本プロデュース：ニトロプラス',
             'https://www.nitroplus.co.jp/works/consumer-game',
             'PSYCHO-PASS 2015 Xbox One entry',
             '2015原作层的联合制作限于脚本企划制作；5pb.Games仍为实际发行，不能推定本社负责程序。'),
    'g630': ('coDeveloper', 'ニトロプラス＆Production I.G制作',
             'https://www.nitroplus.co.jp/news/2012/3287.php',
             '2012-11-30 mini ADV episode 2 announcement',
             '官方将原版系列小游戏称为Nitroplus与Production I.G共同制作；限定iOS应用内小游戏，不并入动画的制作责任。'),
    'nitroplus-extra-dolls-nest': ('originalProduction', '制作：ニトロプラス',
             'https://www.nitroplus.co.jp/game/Dolls_Nest/product',
             '2025 Steam original product information',
             '2025 Steam原作列本社制作、Nitro Arts图形开发；不把图形组独立署名抹去。'),
}

PORT = {'reviewId': 'AZB-N-12', 'entityId': ENTITY, 'dossierId': None,
        'workId': 'g054', 'targetType': 'release', 'targetId': 'g054-v2',
        'role': 'developer', 'rawCredit': '開発・発売：ニトロプラス',
        'status': 'sourceReviewed', 'expectedPlacement': 'main', 'beforeTargetRoles': [],
        'source': 'https://www.nitroplus.co.jp/works/',
        'note': '官网逐作列2010年PC移植版由Nitroplus开发、发行；仅命中g054-v2，不传播至2009年5pb.原版或2011及以后其他平台。'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build():
    prior = read(PRIOR)
    old = [d for d in prior['decisions'] if d.get('dossierId') == DOSSIER]
    assert len(old) == 72
    assert len({d['workId'] for d in old}) == 72
    assert set(PROOFS) <= {d['workId'] for d in old}
    additions, decisions = [], []
    for d in old:
        wid = d['workId']
        if wid not in PROOFS:
            decisions.append({**d, 'previousDecision': d['decision'], 'decision': 'deferred', 'batchDecision': 'deferred',
                              'batchFinding': '已对照当事方逐作目录；目录中的品牌、剧本职员或版权字段不足以证明本公司在该版本的直接制作工种。',
                              'additionalSource': 'https://www.nitroplus.co.jp/works/'})
            continue
        role, raw, url, location, note = PROOFS[wid]
        eid = f'E-N-{wid}'
        additions.append({'reviewId': f'AZB-N-{len(additions)+1:02d}',
                          'entityId': ENTITY, 'dossierId': DOSSIER,
                          'workId': wid, 'targetType': 'work', 'role': role,
                          'rawCredit': raw, 'status': 'sourceReviewed',
                          'expectedPlacement': d['placement'], 'beforeWorkRoles': [],
                          'before': {'roles': ['catalogueAssociation'], 'group': 'unresolved',
                                     'status': 'pendingRole'}, 'source': url, 'note': note})
        decisions.append({**d, 'previousDecision': d['decision'], 'decision': 'confirmed', 'batchDecision': 'confirmed', 'evidenceIds': [eid],
                          'batchFinding': note, 'confirmedRole': role,
                          'source': url, 'sourceLocation': location,
                          'missingEvidence': None})
    assert len(additions) == 11 and sum(d['batchDecision'] == 'confirmed' for d in decisions) == 11
    additions.append(PORT)
    evidence = [{'evidenceId': f'E-N-{wid}', 'url': entry[2], 'location': entry[3],
                 'workId': wid, 'role': entry[0], 'scopeNote': entry[4]} for wid, entry in PROOFS.items()]
    evidence.append({'evidenceId': 'E-N-g054-v2', 'url': PORT['source'],
                     'location': 'STEINS;GATE 2010 PC移植版，開発・発売',
                     'workId': 'g054', 'releaseId': 'g054-v2',
                     'role': 'developer', 'scopeNote': PORT['note']})
    review = {'schemaVersion': 1, 'reviewedAt': '2026-10-27',
              'baseTree': '8a520a639b38bd38b8eb11aae16fdb2dd6eb201d',
              'audit': 'data/entity-role-nitroplus-audit-20261027.json',
              'policy': '提高单次核实量：整包检查72条Nitroplus专题待核；仅直接具名的11部作品升级，并单独限定2010 PC移植开发。其余继续待核。',
              'identityCorrections': [], 'creditAdditions': additions,
              'deferredReviews': [], 'reviewedEntities': []}
    audit = {'schemaVersion': 1, 'reviewedAt': '2026-10-27',
             'baselineTree': review['baseTree'], 'dossierId': DOSSIER,
             'claimCount': 72, 'confirmedWorkClaims': 11, 'deferredWorkClaims': 61,
             'separateReleaseCredits': 1, 'sourceCount': len({e['url'] for e in evidence}),
             'evidence': evidence, 'decisions': decisions,
             'counts': dict(Counter(d['batchDecision'] for d in decisions))}
    return review, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, data in zip((REVIEW, AUDIT), build()):
        value = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if args.check:
            assert path.read_text(encoding='utf-8') == value, f'{path.name} not synchronized'
        else:
            path.write_text(value, encoding='utf-8')
        print(path.relative_to(ROOT))


if __name__ == '__main__':
    main()
