#!/usr/bin/env python3
"""One-time sourced ELF additions, October 2026; idempotent on existing data."""
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
gamefile = root / "data/games.json"
covfile = root / "data/company-coverage.json"
data = json.loads(gamefile.read_text(encoding="utf-8"))
cov = json.loads(covfile.read_text(encoding="utf-8"))
elf = next(c for c in cov["companies"] if c["id"] == "elf")
assert not any(w["id"] in {"g1274", "g1275"} for w in data["works"]), "Already applied"
assert len(elf["workIds"]) == 38 and len(elf["relatedGames"]) == 22
dk = next(g for g in elf["relatedGames"] if g["id"] == "elf-r14")
nk = next(g for g in data["works"] if g["id"] == "g325")

dk_guide = "https://www.neoseeker.com/dragon-knight-iv/faqs/153624-walkthrough.html"
dk_review = "https://takarikaruga.com/2019/10/03/dk4/"
nk_detail = "https://www.erosou.com/revew/1273.html"
nk_review = "https://hmx9900.wordpress.com/2010/08/26/%E5%AA%9A%E8%82%89%E3%81%AE%E9%A6%99%E3%82%8A-%E3%83%8D%E3%82%A4%E3%82%AD%E3%83%83%E3%83%89/"
w1 = "https://www.ymgal.games/ga21575"
w2 = "https://www.ymgal.games/ga21557"
command1 = "https://gamedaradara.doorblog.jp/archives/61422975.html"
command2 = "https://blog.livedoor.jp/myonkui/archives/6422428.html"

dk["contentVersions"].append({
    "id": "elf-r14-c-2007-windows-remake", "workId": "elf-r14",
    "label": "2007 Windows 3D重制版", "firstYear": 2007, "basis": "added",
    "comparedTo": "elf-r14-c-original",
    "evidence": "2007-06-29 Windows重制，城镇和战场从2D改建为3D；通关后新增16关Challenge Mode，敌人及道具配置有别于主线。保留原1994年作品身份，不能称为全新主线。",
    "source": dk_guide, "evidenceReleaseIds": ["elf-r14-v-2007-remake"],
    "addedContent": [
        {"description": "重制版将城镇及战斗场面改为新建3D场景，替换原版2D演出与操作方式。", "source": dk_review},
        {"description": "追加16关Challenge Mode，挑战关有不同敌人与道具配置，构成新增可玩关卡。", "source": dk_guide}
    ]
})
dk["platformReleases"].append({
    "id": "elf-r14-v-2007-remake", "workId": "elf-r14", "year": 2007,
    "platform": "Windows", "publisher": "ELF", "kind": "3D重制版",
    "voice": "有（部分）", "differences": "2007-06-29，3D城镇和战场、部分事件配音、战斗音乐调整；通关后16关Challenge Mode为新增关卡。未确认全程有声或新主线。",
    "source": dk_guide, "contentVersionId": "elf-r14-c-2007-windows-remake",
    "contentRelation": "added", "contentNote": "已核实3D美术资源和16关挑战模式，不重复建新作。",
    "releaseRole": "contentDebut"
})
dk["notes"] = "跨类型策略RPG；2007年Windows 3D重制与1994年原版属于同一作品，新增3D场景与16关挑战模式。其他旧移植待核。"
dk["interactionNote"] = "原作战术部署与战斗指令；2007重制将城镇与战场改为3D，并增加挑战关卡。跨版本概览不意味着原作也使用3D。"
dk["interactionSources"] = [dk["source"], dk_review, dk_guide]

data["contentVersions"].append({
    "id": "g325-c-2010-naked", "workId": "g325",
    "label": "2010 原型剧本版『ネイキッド』", "firstYear": 2010, "basis": "added",
    "comparedTo": "g325-c-original",
    "evidence": "2010-03-26发行早期原型脚本版本，主人公选项措辞、人物反馈对白和部分情节细节与2008正式版不同；主线框架相似。本篇无配音及原版3D室内移动，随盘捆绑两篇此前已经发行的有声番外，不重复计新作。",
    "source": nk_detail, "evidenceReleaseIds": ["g325-v-2010-naked"],
    "addedContent": [
        {"description": "首次商业发行不同于2008正式版的早期原型脚本，含不同主人公选项、人物反馈对白和部分细节流程；不认定为新主线。", "source": nk_detail},
        {"description": "早期脚本的若干人物台词和细节事件与2008版不同；取消3D移动属于系统删改，不能视为新增地图。", "source": nk_review}
    ]
})
data["platformReleases"].append({
    "id": "g325-v-2010-naked", "workId": "g325", "year": 2010,
    "platform": "Windows", "publisher": "ELF", "publisherCompanies": ["ELF"],
    "kind": "原型脚本内容版", "voice": "有（部分）",
    "differences": "2010-03-26《媚肉の香り ネイキッド》；采用有别于2008年原作的早期脚本及人物回应，取消3D屋内移动；本篇无配音，但盘内有两篇先前已发行的有声番外。",
    "source": nk_detail, "contentVersionId": "g325-c-2010-naked",
    "contentRelation": "added", "contentNote": "首次商业发行原型脚本，区别于旧番外；其主线与正式版仍大致相似。",
    "releaseRole": "contentDebut"
})
nk["notes"] = "2008年正式版与2010年《ネイキッド》原型脚本版共用作品身份；后者的选项和台词存在差异，未证实有全新主线；已发行番外不重复录入。"

new_works = [
    dict(
        id="g1274", title="エルフ イン ワンダーランド",
        originalTitle="エルフ イン ワンダーランド", firstYear=2011,
        category="文字冒险", subcategory="纯文本指令",
        genre="复古文字指令／ELF角色跨作品联动",
        characters=["ELF历代游戏人物（群像）"], charactersNote="",
        synopsis="由ELF自主推出的短篇复古文字冒险，将该品牌其他作品中的角色引入同一冒险舞台；使用行动指令推进游戏，并非旧游戏合集。",
        notes="2011-08-12 Windows免费独立发行；输入命令式玩法有玩家实际体验佐证。完整命令词表、具体登场角色和声音状态仍待核实。",
        source=w1, interactionModes=["文字输入"],
        interactionBasis="游戏发行目录与玩家实玩",
        interactionNote="实玩反馈明确称「コマンドタイピング方式」，区别于菜单选择与输入存档名；具体全部动作词尚未实机穷尽。",
        interactionSources=[command1,w1],
        titleAliases=["Elf in Wonderland", "élf in Wonderland"]
    ),
    dict(
        id="g1275", title="エルフ イン ワンダーランド2",
        originalTitle="エルフ イン ワンダーランド２", firstYear=2012,
        category="文字冒险", subcategory="纯文本指令",
        genre="复古文字指令／ELF角色跨作品联动",
        characters=["ELF历代游戏人物（群像）"], charactersNote="",
        synopsis="ELF继首作之后另行发行的复古文字冒险续作，以1980年代游戏式片假名指令输入展开独立可玩流程；并非首作的重制或移植。",
        notes="2012-07-19 Windows独立商业发行，有同期购买及游玩记录；具体人物名单、角色语音和全套命令待核。",
        source=w2, interactionModes=["文字输入"],
        interactionBasis="发行目录、同期玩家实玩",
        interactionNote="2012年同期反馈显示键入片假名动作指令；有独立续篇游戏过程，不与首作并成单一内容版本。",
        interactionSources=[command2,"https://www.hikarinagi.org/galgames/14084/revisions"],
        titleAliases=["Elf in Wonderland 2","élf in Wonderland 2"]
    )
]
for w in new_works:
    data["works"].append(w)
    ri = w["id"] + "-v-original"
    ci = w["id"] + "-c-original"
    data["contentVersions"].append(dict(
        id=ci, workId=w["id"], label="原作／首批内容",
        firstYear=w["firstYear"], basis="original",
        evidence=f"{w['firstYear']}年ELF独立发布的Windows复古文字冒险，与另一部系列作品分别建立原作身份。",
        source=w["source"], evidenceReleaseIds=[ri], addedContent=[]
    ))
    data["platformReleases"].append(dict(
        id=ri, workId=w["id"], year=w["firstYear"], platform="Windows",
        publisher="ELF", publisherCompanies=["ELF"],
        kind="独立首发", voice="未核实",
        differences=("2011-08-12免费提供" if w["firstYear"]==2011 else "2012-07-19独立发行") + "的指令输入ADV；配音未核实。",
        source=w["source"], contentVersionId=ci, contentRelation="original",
        contentNote="独立游戏首次发行，不是系列前作的内容版本。",
        releaseRole="contentDebut"
    ))
    elf["workIds"].append(w["id"])
    elf["publisherWorkIds"].append(w["id"])

elf.setdefault("authorizedCommandWorkIds", []).extend(["g1274", "g1275"])
elf["checkedAt"] = "2026-10-21"
elf["description"] = "日本 ELF 历史作品专题：40 部叙事作品、22 部跨类型作品、重制版本与文字指令游戏核查。"
elf["publisherWorkText"] = '<p class="scope-note"><strong>叙事作品 40 部，其中 ELF 原创 35 部、ELF 发行的 Silky’s 原作 5 部。</strong></p>'
elf["scope"] = "ELF原创及ELF实际发行的Silky’s改编版分开署名。2026-10-08已收七部菜单／点击冒险；按2026-10-21本次具名补录要求，对两部《エルフ イン ワンダーランド》允许独立输入式叙事进入主库，例外不自动推广。RPG、模拟、麻将及动作仍在跨类型区；后发重制只录可证实的新内容版本，不重复计独立原作。"
elf["versionScope"] = "2026-10-21增补《Dragon Knight 4》2007 Windows 3D重制及挑战关卡、《媚肉の香り》2010年原型脚本版，另将2011、2012年独立文字指令续作分别建档。两篇2008年旧番外不当作2010年新增作品。早期其他移植日期、声音及内容未核实状态不改写。"
elf["auditLabel"] = "62 项历史核对＋7 项2026-10-08补录＋4 项2026-10-21更新；核对行不等于独立游戏数。"
elf["auditNote"] = "历史核对判断保留，2026-10-21经复核修订其中两项版本差异和两部独立指令游戏的收录状态；原作与移植公司署名、未核实项目仍按证据分开记录。详见 data/elf-20261021-audit.md。"
elf["catalogueEntryCount"] = 73
prior = next(e for e in elf["entries"] if e["title"] == "エルフ イン ワンダーランド／2")
prior["status"] = "历史待核（现已复核）"
prior["reason"] = "2026-10-08暂未收录；2026-10-21已核实为两部独立的文字指令ADV，最新处理见本表尾新增两行。"
elf["entries"].extend([
    dict(title="Dragon Knight 4 Windows版（2007）", status="已补充内容版本",
         workIds=[], relatedIds=["elf-r14"], source=dk_guide,
         reason="2007-06-29新增3D城镇与战场资源、16关Challenge Mode，归原作的新增内容版本，不单独新建游戏。"),
    dict(title="媚肉の香り ネイキッド（2010）", status="已补充内容版本",
         workIds=["g325"], source=nk_detail,
         reason="采用与2008年版不同的原型脚本和人物回应；原有两篇番外仍归旧作品，不重复计作新剧情。"),
    dict(title="エルフ イン ワンダーランド（2011）", status="已新增独立文字输入游戏",
         workIds=["g1274"], source=w1,
         reason="2011-08-12 Windows免费冒险游戏，复古键入式操作有实玩证据；与续篇分别建立作品。"),
    dict(title="エルフ イン ワンダーランド2（2012）", status="已新增独立文字输入游戏",
         workIds=["g1275"], source=w2,
         reason="2012-07-19 Windows独立发行的指令输入续篇，有同期玩家购买与游玩证据；非原作移植。")
])
data["meta"]["scope"] += " 2026-10-21 ELF具名补录：两部《エルフ イン ワンダーランド》指令输入独立游戏进入主库，仅此品牌本次指定，不自动更改其他厂商准入；2007《龙骑士4》重制与2010《媚肉之香》原型剧本归入旧作品的内容版本。"

assert len(elf["workIds"]) == 40 and len(elf["relatedGames"]) == 22
assert len(elf["entries"]) == 73 and len(data["works"]) == 1272
assert len(dk["contentVersions"]) == 2 and len(dk["platformReleases"]) == 2
assert len([v for v in data["platformReleases"] if v["workId"] in {"g1274", "g1275"}]) == 2

for path, obj in [(gamefile, data), (covfile, cov)]:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

(root/"data/elf-20261021-audit.md").write_text(f"""# ELF 内容与作品核查 · 2026-10-21

仅更新 wt1234-donkey/visual-novel；历史数据及其证据原样保留。

## Dragon Knight 4
- 1994年原作 \`elf-r14\` 保留；2007-06-29重制并入新内容版 \`elf-r14-c-2007-windows-remake\`。
- [实际攻略]({dk_guide})确认重制版通关后新增16关Challenge Mode，独立敌人及道具配置；[新旧版评测]({dk_review})确认城镇与战场2D改为3D，操作亦有所不同。
- 这些是新增可玩关卡与场景素材，不代表新增完整主线。部分配音，未推定全程配音。

## 媚肉の香り ネイキッド
- 2010-03-26发表；[同期实玩]({nk_detail})和[另一评论]({nk_review})区分未公开的原型脚本与2008正式版：主人公回应、人物反馈和局部文字不同，但主线框架类似。
- 新内容版 \`g325-c-2010-naked\` 是早期剧本首次独立发行；无3D宅邸移动属系统变化而不是新增关卡；主线无语音，旧有两篇番外有声并收录，不重复计数。

## ELF in Wonderland（独立作品）
- [第一作目录]({w1})记2011-08-12 Windows独立发行（免费），[玩家实玩]({command1})记键入动作命令玩法。
- [第二作目录]({w2})记2012-07-19 Windows独立发行，[同期购买／实玩讨论]({command2})记其为可单独游玩的复古命令ADV续篇。
- 作品各建一个原作内容及首次Windows发行：\`g1274\`、\`g1275\`。角色具体名单与音声待证，不能凭类型推断；此次具名输入式叙事准入不自动放宽其他厂商。

增量：主库2部新游戏、3个内容版本及3次首次发行；ELF关联区1个内容版本及一次首次发行。专题40部主库＋22部跨类型，合计62部。
""", encoding="utf-8")
print("ELF patch applied: works 1272, ELF 40+22, 4 content identities, 4 release identities.")
