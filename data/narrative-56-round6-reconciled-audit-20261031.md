# 第六轮叙事编目：56部冻结清单与PR187并行更新后的安全合并审计（2026-10-31）

最初审计基线为56部未完成、139个未填字段，主库共1,587部。因另一工作分支PR #187在本轮进行时先合并五条同一作品更新，最新main已经**先完成3部作品全部四项，同时补了另2部的部分字段**。为避免覆盖或重复统计，本轮从最新main的53部缺项重新冻结字段基线，仅向其中19部写入**尚未填的字段**。完整结果为22部涉及更新（其中3部由PR187先完成），整体从56部降至35部。

## 核实统计

| 指标 | 最初审计 | PR187合并后main | 本轮合并后的预期状态 |
|---|---:|---:|---:|
| 完成四项的作品 | 1,531 | 1,534 | **1,552** |
| 四项仍有缺项 | 56 | 53 | **35** |
| 未填单字段数 | 139 | 121 | **76** |
| 已部分完成作品 | 33 | 35 | **26** |
| 四项皆空作品 | 23 | 18 | **9** |

## 并发修改对账

- 已于PR187完成，不在本轮重复写入：g1504 TRianThology，g1509 月姬，g1526 The Mr. Rabbit Magic Show。
- PR187已经填写三项、此处只补剩余叙事结构：g1559 HoneyComing、g1560 Strawberry Nauts。
- 其他17部依原PC游戏、原厂产品说明和明确标注的历史资料类型补写原有缺项；其中16部完整、g1419《そらうた》保留原PC版结构缺项。
- 补丁的填入字段必须属于最新main冻结清单的missing字段，不得覆盖已存在的position/style/theme/structure。

## PR187之后冻结的53部逐项审核表

| ID | 作品 | 原批次 | 新补字段 | 复核后仍未填 | 具名证据／下一步 |
|---|---|---|---|---|
| g139 | 桃太郎 | 历史作品 | 无 | structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g140 | 浦岛太郎 | 历史作品 | 无 | structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g328 | 我的女友是劳动者 | 历史作品 | 无 | style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g329 | 麻吕的患者是劳动者 | 历史作品 | 无 | style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g330 | 麻吕的患者是劳动者2 | 历史作品 | 无 | style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g331 | 麻吕的患者是劳动者3 完结篇 | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g533 | これD.P.S.？ | 历史作品 | 无 | style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g566 | 婦警さんDA | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g579 | ハニワ闇開発室ぷち | 历史作品 | 无 | style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g589 | フェアリーズレジデンス スペシャル クラブ編 | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g591 | フェアリーズレジデンス スペシャル 学園編 | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g638 | ちびママ | 历史作品 | 无 | structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g705 | ANGEL | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g745 | 娘娘台风 | 历史作品 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g749 | ほっとMILK | 历史作品 | 无 | style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g759 | うろつき童子 | 历史作品 | 无 | style、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g769 | アラベスク | 历史作品 | 无 | style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g772 | バーチャコール2.2 | 历史作品 | 无 | style、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g774 | ProjectVC | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g810 | セーラー服美少女図鑑 其の五 | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g811 | セーラー服美少女図鑑 其の六 | 历史作品 | 无 | style | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1348 | SHUFFLE! | 早期18组 | structure | 全部完成 | [出处](https://sagaoz.net/foolmaker/game/s/shuffle.html)；证据类别 `contemporary-original-pc-walkthrough`。注明Navel原PC版1.0～1.1、2004年2月的同期攻略有五位人物的分支和普莉姆拉解锁条件；不混入Essence+或PS2后期增添角色线。 |
| g1353 | 初音岛 | 早期18组 | structure | 全部完成 | [出处](https://happygolucky.jp/impression/519.html)；证据类别 `contemporary-original-pc-review`。2003年前后原PC版长篇实玩评价逐项讨论音梦、樱、琴里、赖子、真子、美春、萌各自剧情；2003年首发移植公告证明PS2新增人物，不应混入2002原版。 |
| g1356 | 初音岛4 | 早期18组 | structure | 全部完成 | [出处](https://kannagi35.com/content/da-capo-4-walkthrough)；证据类别 `contemporary-original-pc-walkthrough`。2019年6月原版首发后同步发表的攻略列出PC各女主角色与开放条件，页面明确PS4/Switch版额外新增SEQUEL部分。 |
| g1357 | 初音岛5 | 早期18组 | structure | 全部完成 | [出处](https://kannagi35.com/content/da-capo-5-walkthrough)；证据类别 `contemporary-original-pc-walkthrough`。2023年1月首发次日的原PC攻略清楚列出五人分歧、EPILOGUE、三篇后日谈与D.C.的依次开放条件。 |
| g1366 | PARADISE LOST | 早期18组 | structure | 全部完成 | [出处](https://w.atwiki.jp/god14/pages/155.html)；证据类别 `historical-title-structure`。作品专题保存原2004年版每章具体标题，确认两位主人公交替叙述、分歧及主要结局；仅记录共同事件与原版角色线，不与后发新装版差异混淆。 |
| g1368 | 神咒神威神乐 | 早期18组 | structure | 全部完成 | [出处](https://w.atwiki.jp/god14/pages/139.html)；证据类别 `historical-original-version-structure`。正田崇作品专题按2011年原版记录共同篇、四路分歧、汇总终章，另明确2013年《曙之光》移植新增如月、弥生、箱根等五个章。 |
| g1415 | カナリア ～この想いを歌に乗せて～ | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://mediaworld.co.jp/products/10360385001)；证据类别 `licensed-original-premise-plus-pc-guide`。NEC授权Dreamcast版发行文案明确原PC前提（迁居香川、组团、三个月学园祭演出），同时注明DC版新增人物与原创情节；PC原版攻略验证地点选项与人物分支。 |
| g1416 | 魔女のお茶会 | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://consoledictionary.com/games/16216)；证据类别 `secondary-later-genre-story`。2026年游戏资料站对2002年PC版及2003年DC版整理指出魔女曾因受迫害移居魔法世界、后来尝试重新与人类交流，且有共同部分后分流个人故事；来源是后世二级资料，需与原版说明书复核。 |
| g1417 | 私立アキハバラ学園 | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://w.atwiki.jp/aniwotawiki/pages/7934.html)；证据类别 `historical-title-retrospective-and-credits`。2010年保存的作品级回顾说明2003年Frontwing原PC版男主冬馬荘一郎打算从宅文化毕业，却进入秋叶原学园，并明确其御宅交流ADV喜剧定位。原版staff名单印证发行与剧本，路线数量没有充分原流程证据而不推断。 |
| g1418 | 魔界天使ジブリール | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1419 | そらうた | 六组厂商 | position、style、theme | structure | [出处](https://w.atwiki.jp/aniwotawiki/pages/9057.html)；证据类别 `historical-title-retrospective-limited`。2010年起的作品级历史回顾指出2004年原PC游戏讲述主人公幼年车祸失去父母，被伯母收留并与表妹霊子一同生活，之后经历有关少女与超常现象的故事；2008年Vista版攻略说明它有隐藏人物线路，但未证明2004年原PC版存在相同路线，因此本次不填structure。 |
| g1420 | 魔界天使ジブリール -episode2- | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1421 | ボーイミーツガール | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1423 | アイドル魔法少女 ちるちる☆みちる 前編 | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://store.steampowered.com/app/377710/)；证据类别 `developer-official-store`。Frontwing自行发布的Steam页面明说前篇7集，后篇6集，且提供美知留遇到使魔黑猫的起始剧情。 |
| g1424 | アイドル魔法少女 ちるちる☆みちる 後編 | 六组厂商 | structure | 全部完成 | [出处](https://store.steampowered.com/app/377710/)；证据类别 `developer-official-store`。开发方Frontwing原前篇Steam正式商店介绍明确全系列13集、前篇7集、后篇其余6集。此前仅能确认前情，此次补充后篇自身的集数边界。 |
| g1448 | 君と目覚める幾つかの方法 | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1451 | Princess × Princess | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://project-navel.com/pripri/story.html)；证据类别 `developer-story-and-original-playthrough`。Navel官网Story直接写明莉西亚成为赖斗恋人后寻觅侧室、学园出现飞机和失忆少女；2021年游戏攻略证实本作分人物线与后宫结局。 |
| g1452 | 最終試験くじら | 六组厂商 | 无 | structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1453 | ホームメイド -Home maid- | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://www.ymgal.games/ga10239)；证据类别 `title-specific-original-credits-database`。原作档案记载2004年CIRCUS PC版背景位于英国领地下的日式文化贵族学校，原作脚本作者たけうちこうた负责共通与枫路线，其他多名剧作者分别参与本篇，PS2《终之馆》系另一次改编与扩展。该站是二次作品档案。 |
| g1455 | 恋夏 ～れんげ～ | 六组厂商 | 无 | position、style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1457 | uni. | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://newikis.com/ja/Uni.)；证据类别 `historical-encyclopedic-retrospective`。保存版游戏介绍说明2010年CIRCUS全年龄ADV不以恋爱分支为核心，星空綺麗々进入学风联合团体，官方设定采用29则独立短篇连续描写日常；页面为后世二次整理，故列为次级证据。 |
| g1462 | てんぷれっ!! | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1464 | キュアフル！ | 六组厂商 | 无 | position、style、theme | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1474 | フルキス | 六组厂商 | structure | 全部完成 | [出处](https://kannagi35.com/x/furukiss-walkthrough)；证据类别 `contemporary-original-pc-walkthrough`。2017年3月25日原PC版攻略逐一列出四名主人公的攻略线、共同路线分歧和不满足好感条件的普通结局。 |
| g1482 | モエかん | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1488 | Dear My Friend | 六组厂商 | position、style、theme、structure | 全部完成 | [出处](https://d.hatena.ne.jp/keyword/Dear%20My%20Friend)；证据类别 `historical-original-synopsis-and-version-guard`。2004年原作Story文案保存于旧Hatena词条，叙述冬日、孤儿麻衣与森川家新生活；同期/后世原PC实玩记录独立人物路线；2005年Complete版说明确实加入PS2追加剧本，不能回填2004原版。 |
| g1490 | Imitation Lover | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1492 | Soranica Ele | 六组厂商 | 无 | position、style、theme、structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1500 | 虚空のバロック | 六组厂商 | 无 | structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1505 | Ciconia When They Cry - Phase 1 | 推荐厂商 | 无 | structure | 缺作品级原版剧情、可追溯游戏流程或人物剧本说明；保留缺项，不能凭厂商目录自动生成。 |
| g1559 | HoneyComing | 推荐厂商 | structure | 全部完成 | [出处](https://www.kadokawa.co.jp/product/200976000044/)；证据类别 `licensed-adaptation-and-contemporary-pc-review`。原HOOKSOFT授权漫画出版社KADOKAWA明确原游戏男主厌恶恋爱、就读设有恋爱授课的学园；2007年7月原版实玩评价说明多位女主角的分线及结局后故事，不以漫画情节作为原游戏独有章节。 |
| g1560 | Strawberry Nauts | 推荐厂商 | structure | 全部完成 | [出处](https://www.hook-net.jp/htm/product.htm)；证据类别 `developer-product-and-original-pc-guide`。HOOKSOFT原作产品页面注明2011年纯爱学园ADV，并明确2011首发原版；其游戏更新公告显示1.04新增六角雀路线；原作攻略证实共通章节与多个既有角色篇章。 |

## 最终验证

本轮使用`data/narrative-evidence-rebased-r6-20261031.json`及`data/narrative-53-pre-merge-r6-audit-20261031.json`进行逐字段复核。经GitHub Actions运行`scripts/complete_narrative_fields_rebased_r6_20261031.py`、`scripts/audit_narrative_pending_20261030.py`、叙事/实体/主库数据验证、完整Python和Node回归、公司页一致性。

严禁混淆2000《月姬》与2021重制版；2002《D.C.》和后续P.S./P.C.增补；2019《D.C.4》首发PC与后续SEQUEL；2004《SHUFFLE!》与Essence+扩充；2011《Strawberry Nauts》首发与Ver1.04补丁新增路线。

不更改`data/games.json`的作品、内容版本和发行记录，不更改作者、原画、配乐或组织署名，不修改原冻结八部编辑基线。证据不足的后发改编资料只用于共同剧情背景，不冒充原版篇章。
