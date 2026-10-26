"""Review the frozen A dossiers together, reusing each original across claims."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRIOR = ROOT / 'data/entity-verification-five-phase-audit-20261026.json'
REVIEW = ROOT / 'data/entity-role-adventure-alice-review-20261027.json'
AUDIT = ROOT / 'data/entity-role-adventure-alice-audit-20261027.json'
MARKDOWN = ROOT / 'data/entity-role-adventure-alice-audit-20261027.md'
DOSSIERS = ('adventure_international', 'alicesoft')
BASE_TREE = '99d54acbeda8976b27df552ecc0709718cc7b600'
SUPPORT = 'https://www.alicesoft.com/support/sys39v549.html'
NOR = 'https://noir.alicesoft.com/nor/index.htm'
HENTAI = 'https://www.alicesoft.com/information/2020/entry002611.html'

# Explicit brand product rows. The parent dossier is not resolved by these rows.
BRANDS = {
    'alicesoft-extra-oujisamalv1': ('entity-alice_blue', '王子さまＬｖ１(Alice Blue)', SUPPORT, 'System 3.9 list, 王子さまLv1', 'related'),
    'g545': ('entity-alice_blue', '王子さまＬｖ１．５(Alice Blue)', SUPPORT, 'System 3.9 list, 王子さまLv1.5', 'main'),
    'g546': ('entity-alice_blue', '隠れ月 (Alice Blue)', SUPPORT, 'System 3.8 list, 隠れ月', 'main'),
    'g547': ('entity-alice_blue', '楽園行(Alice Blue)', SUPPORT, 'System 3.9 list, 楽園行', 'main'),
    'alicesoft-extra-orenoshitadeagake': ('entity-alice_blue', '俺の下であがけ(Alice Blue)', SUPPORT, 'System 3.9 list, 俺の下であがけ', 'related'),
    'g574': ('entity-alice_noir', 'ＡｌｉｃｅＮｏｉｒ第一弾「Ｎｏｒ」', NOR, 'original Nor product page, heading and development diary', 'main'),
}

EVIDENCE = [
    ('E-A-AI-SAGA', 'https://www.mocagh.org/ai/saga-manual.pdf',
     'original 1981 Graphic Adventure manual, p.2 credits',
     'Graphic Adventure graphic engines name Scott Adams, Penguin Software, Mark Pelczarski and Adventure International separately; this later edition is not the 1978 original.'),
    ('E-A-AI-DEATH', 'https://www.mocagh.org/ai/deathplanet-manual.pdf',
     'Death Planet original manual, p.1',
     'Adventure International is listed as publisher; Lance Micklus is author and Charles Paul de Young is credited for the Color Computer conversion.'),
    ('E-A-ALICE-HISTORY', 'https://www.alicesoft.com/outline/contents.html',
     'company outline, 1983 establishment and 1989 brand start',
     'Alicesoft brand started in 1989, so Champion Soft products in 1982–88 cannot be relabelled as contemporary Alicesoft-branded development.'),
    ('E-A-ALICE-FREE', 'https://www.alicesoft.com/about/',
     'free-distribution list, three named Showa Champion Soft products',
     'Little Princess, Little Vampire and Gakuen Senki are explicitly Champion Soft brand products; the text does not assign the later Alicesoft brand development.'),
    ('E-A-ALICE-SUPPORT', SUPPORT,
     'official System 3.8/3.9 compatibility list, five Alice Blue titles and Nor',
     'The page names Alice Blue and Alice Noir on individual titles; it is a product/engine list, not evidence that the parent brand independently made all components.'),
    ('E-A-ALICE-NOR', NOR,
     'Nor contemporary product page and development diary',
     'The product identifies AliceNoir as its first release; this does not resolve a parent Alicesoft production credit.'),
    ('E-A-ALICE-HENTAI', HENTAI,
     '2020-07-22 original director announcement, introduction and new-brand paragraphs',
     'The director calls IMYUIC an Alicesoft-produced new brand for this specific game; credits are limited to production collaboration, not independent engine/programming.'),
    ('E-A-ALICE-INDEPENDENCE', 'https://www.alicesoft.com/information/2022/entry003001.html',
     '2022-05-30 separation announcement, name and ongoing sale paragraphs',
     'Later IMYUIC(ALICESOFT) sale name and independence cannot be projected backward as sole original development.'),
]


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def build():
    old = [d for d in read(PRIOR)['decisions'] if d.get('dossierId') in DOSSIERS]
    old.sort(key=lambda d: (DOSSIERS.index(d['dossierId']), d['claimId']))
    assert Counter(d['dossierId'] for d in old) == {'adventure_international': 36, 'alicesoft': 75}
    assert len({d['claimId'] for d in old}) == 111
    additions = []
    decisions = []
    for d in old:
        wid, dossier = d['workId'], d['dossierId']
        decision = {**d, 'previousDecision': d['decision'], 'batchDecision': 'deferred',
                    'decision': 'deferred', 'reviewedEvidenceIds': [],
                    'batchFinding': '现有专题目录不能证明该作品具体版本的母专题直接创作职责。'}
        if dossier == 'adventure_international':
            decision['reviewedEvidenceIds'] = ['E-A-AI-SAGA']
            decision['batchFinding'] = '同期 Graphic Adventure 说明书将作者、各平台图形制作和发行分列；不能套用到本条原版／其他游戏。'
            if wid == 'ai-death-planet':
                decision['reviewedEvidenceIds'] = ['E-A-AI-DEATH']
                decision['batchFinding'] = '原说明书列 AI 为发行、Lance Micklus 为作者、Charles Paul de Young 为 Color Computer 移植者；未证明 AI 原作开发。'
                decision['missingEvidence'] = '原版或各移植版片尾／合约中 Adventure International 具体创作工种的具名原件；现有说明书仅支持发行。'
            elif wid == 'g089':
                decision['batchFinding'] = '1976/1977 大型机原版及现存 Microsoft 后发发行均不能由 AI 1981 图形版说明书追认公司开发。'
            elif wid == 'g091':
                decision['batchFinding'] = '1978 Scott Adams 初期自行销售记录与 1981 AI 图形版是不同发行；后者的引擎分工不能倒填原版。'
        else:
            decision['reviewedEvidenceIds'] = ['E-A-ALICE-HISTORY', 'E-A-ALICE-FREE']
            decision['batchFinding'] = '官网说明品牌沿革和少量产品归属；本项仍缺对应原版的 Alicesoft 母品牌具体制作署名。'
            if wid in BRANDS:
                eid, raw, src, loc, place = BRANDS[wid]
                decision['reviewedEvidenceIds'] = ['E-A-ALICE-NOR' if src == NOR else 'E-A-ALICE-SUPPORT']
                decision['batchFinding'] = f'官方逐作将此项署为 {eid.removeprefix("entity-")} 品牌产品；仅追加该子品牌制作品牌，母专题职责继续待核。'
                decision['missingEvidence'] = f'《{d["title"]}》原版制作名单中 Alicesoft 母品牌与 {eid.removeprefix("entity-")} 子品牌的分工原件。'
                additions.append({'reviewId': f'AAB-A-{len(additions)+1:02d}', 'entityId': eid,
                                  'dossierId': None, 'workId': wid, 'targetType': 'work',
                                  'role': 'productionBrand', 'rawCredit': raw,
                                  'status': 'sourceReviewed', 'expectedPlacement': place,
                                  'beforeWorkRoles': ['originalPublishingBrand'], 'source': src,
                                  'note': f'同期官方页面具名 {eid.removeprefix("entity-")} 作品／引擎支持，限原版制作品牌；不把子品牌职责倒填 Alicesoft 母专题。{loc}'})
            elif wid == 'alicesoft-extra-hentailabyrinth':
                decision.update(decision='confirmed', batchDecision='confirmed',
                                reviewedEvidenceIds=['E-A-ALICE-HENTAI', 'E-A-ALICE-INDEPENDENCE'],
                                evidenceIds=['E-A-ALICE-HENTAI'], source=HENTAI,
                                sourceLocation='2020-07-22 director announcement, Alicesoft-produced new brand',
                                confirmedRole='coDeveloper', missingEvidence=None,
                                batchFinding='2020年当事导演明确 IMYUIC 为 Alicesoft 企划制作的新品牌；仅确认此作品牌企划制作协力，不声称公司独立程序开发。')
                additions.append({'reviewId': 'AAB-A-01', 'entityId': 'entity-alicesoft',
                                  'dossierId': 'alicesoft', 'workId': wid, 'targetType': 'work',
                                  'role': 'coDeveloper', 'rawCredit': 'アリスソフト・プロデュースの新ブランド「IMYUIC」',
                                  'status': 'sourceReviewed', 'expectedPlacement': d['placement'],
                                  'beforeWorkRoles': [],
                                  'before': {'roles': ['catalogueAssociation'], 'group': 'unresolved', 'status': 'pendingRole'},
                                  'source': HENTAI,
                                  'note': '2020年原作品牌企划制作协力，IMAYUI/IMYUIC负责个人品牌创作；不表示 Alicesoft 完成全部程序或后续独立期作品。'})
            elif wid in {'g576', 'g577', 'g578'}:
                decision['batchFinding'] = '官网逐作明确归于昭和时期 Champion Soft 品牌；1989年才启用的 Alicesoft 品牌身份不能倒填原版。'
                decision['missingEvidence'] = f'《{d["title"]}》同期原版职员表若有 Alicesoft 名义的直接制作证据；目前官方仅列 Champion Soft。'
        decisions.append(decision)
    assert len(additions) == 7 and sum(d['batchDecision'] == 'confirmed' for d in decisions) == 1
    review = {'schemaVersion': 1, 'reviewedAt': '2026-10-27', 'baseTree': BASE_TREE,
              'audit': 'data/entity-role-adventure-alice-audit-20261027.json',
              'policy': 'A段一次审查Adventure International 36条及Alicesoft 75条。只升级一项明确具名企划制作协力，六项子品牌制作记录不解除母专题待核；其余110条保留待核。',
              'identityCorrections': [], 'creditAdditions': additions,
              'deferredReviews': [], 'reviewedEntities': []}
    evidence = [{'evidenceId': eid, 'url': url, 'location': loc, 'limit': limit}
                for eid, url, loc, limit in EVIDENCE]
    audit = {'schemaVersion': 1, 'reviewedAt': '2026-10-27', 'baselineTree': BASE_TREE,
             'dossiers': list(DOSSIERS), 'claimCount': len(decisions),
             'confirmedWorkClaims': 1, 'deferredWorkClaims': 110,
             'separateBrandCredits': 6, 'sourceCount': len(evidence),
             'evidence': evidence, 'decisions': decisions,
             'counts': dict(Counter(d['batchDecision'] for d in decisions))}
    return review, audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    review, audit = build()
    for path, data in ((REVIEW, review), (AUDIT, audit)):
        value = json.dumps(data, ensure_ascii=False, indent=2) + '\n'
        if args.check:
            assert path.read_text(encoding='utf-8') == value, f'{path.name} not synchronized'
        else:
            path.write_text(value, encoding='utf-8')
        print(path.relative_to(ROOT))
    lines = ['# A 段专题职责集中核查（2026-10-27）', '',
             '依冻结索引顺序一次审查 **111 条**：Adventure International 36 条、Alicesoft 75 条。',
             '复用 8 份当事方原件。Alicesoft 2020 年《HENTAI LABYRINTH》的品牌企划制作协力有具名来源，',
             '另有 6 部作品仅确认 Alice Blue／AliceNoir 子品牌制作归属；父专题的对应职责仍待核。',
             '其余 110 条维持待核，全库待核专题职责 590 → 589。审计中的查阅不等于逐作开发已证。', '',
             '## 原件包与限度', '']
    for eid, url, loc, limit in EVIDENCE:
        lines.append(f'- [{eid}]({url})：{loc}。{limit}')
    lines += ['', '## 逐项结论', '', '| 冻结问题 | 作品 | 结论 | 依据／仍缺的原件 |', '|---|---|---|---|']
    for d in audit['decisions']:
        src = ', '.join(d['reviewedEvidenceIds'])
        finding = d['batchFinding'] if d['batchDecision'] == 'confirmed' else d['missingEvidence']
        lines.append(f"| {d['claimId']} | {d['title']} | {d['batchDecision']} | {src}；{finding} |")
    lines += ['', '子品牌逐作追加记录及其旧值／版本见[结构化审计](entity-role-adventure-alice-audit-20261027.json)'
              '和[追加规则](entity-role-adventure-alice-review-20261027.json)。作品、内容、旧发行与原出版署名未改。', '']
    value = '\n'.join(lines)
    if args.check:
        assert MARKDOWN.read_text(encoding='utf-8') == value, f'{MARKDOWN.name} not synchronized'
    else:
        MARKDOWN.write_text(value, encoding='utf-8')
    print(MARKDOWN.relative_to(ROOT))


if __name__ == '__main__':
    main()
