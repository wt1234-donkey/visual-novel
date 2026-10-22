# A—Z创作登记第四批：AQUAPLUS至ASa Project

核查日期：2026-10-23。基准提交：`f6f53b6faa6bc3ce2091e8cc67c782967fc2a303`。独立机器记录：[entity-creator-a4-review-20261023.json](entity-creator-a4-review-20261023.json)。承接[A3审计](entity-creator-a3-review-20261022.md)。

本批连续处理队列第21—25项，累计25／32个A主体完成证据分流，下一项ASCII。这里的“已核查”包括保留待核的结论，不表示其所有作品、年份或法律沿革均已确认。

## 可直接确认并应用

| 主体／作品 | 核查证据 | 最小修改及边界 |
| --- | --- | --- |
| AQUAPLUS公司：g037《ToHeart（重制版）》 | [Steam授权商店](https://store.steampowered.com/app/3380520/ToHeart/)明确Developer为AQUAPLUS，发行者另列；[公司发布稿](https://prtimes.jp/main/html/rd/p/000000169.000046382.html)具名株式会社及2025产品；[官网](https://aquaplus.jp/toheart/)直接链接[制作人／导演访谈](https://www.famitsu.com/article/202502/34702)，说明企划、开发与3D制作；[公司页](https://aquaplus.jp/outline/)供主体核对。 | `AZD-C01`仅增加该既有2025作品的公司`originalProduction`。不是由版权或母公司关系推断；不回填1997作品g026，不改变Steam发行的`unverified`内容关系，不宣称全部工序独立完成。 |
| AQUAPLUS品牌：g159《ToHeart2》 | [2004官方产品页](https://aquaplus.jp/th2/html/products.html)同时给出原PS2产品与制作人员，包括制作人、导演、原画、剧本及音乐。 | `AZD-C02`增加本作`productionBrand`。保留2005 Leaf XRATED及后发内容的独立记录，Leaf专题不继承该职责。 |
| AQUAPLUS品牌：g037《ToHeart（重制版）》 | 2025官网产品、商店具名开发及官网所链[制作人／导演第一手访谈](https://www.famitsu.com/article/202502/34702)共同支持该品牌创作。 | `AZD-C03`增加制作品牌。与公司原作制作分别显示，两条职责只对应一部作品；不推定其他历史作品或DLC具体分工。 |
| ARIA：entity-name-5ba1ee4df514 | [官网关于页](https://aria-soft.com/about)明确称其为制作家用机软件的品牌，且区分发行商客服。 | `AZD-I01`：unknown／unresolved → brand／sourceReviewed。稳定ID、名称、别名和7条原发行职责不变；`preserveReleaseRoles: true`禁止身份订正自动追加发行品牌／原作品牌，不新增与AUGUST的关系。 |
| ASa Project：g282—g303共22个既有创作条目 | [品牌介绍](https://www.asa-pro.com/about.html)、[官方目录](https://www.asa-pro.com/products.html)对应原作及后日谈；[恋爱借用中后日谈](https://www.asa-pro.com/koikari/fd/)、[恋爱罗亚尔后日谈](https://www.asa-pro.com/koirowa/af/)、[两头恋爱后日谈](https://www.asa-pro.com/futakoi/af/)区分各分卷；[王样恋爱](https://www.asa-pro.com/ousama/)列导演、原画与剧本。 | 记录`existingRegistrationRetained`，不增加重复职责，不批量升级旧`existingDossier`核查状态。本次为目录归属复核，不声称重验每一平台与全体职员。目录的“2026年秋”与具体产品页的发售公告粒度不同，本批不改核心日期。 |

新增共3条作品层职责，涉及2部主库作品；品牌和公司计数不可相加当作游戏数。ASa Project的22条属于旧登记，本批新增数为0。

## 需要补充来源

**Arsys Software／jhv-star2《Star Cruiser II》**：已读既有JHV专题数据及[实物目录](https://retroblues.sakura.ne.jp/regeokiba/jhv/jhv.htm)，其说明原Arsys发行与后发JHV CD版，CD版另列プロシードユニ／JHV。既有[MAME机种档案](https://github.com/mamedev/mame/blob/master/hash/pc98.xml)承担发行证据，不能单独证明全部制作职责。[MobyGames](https://www.mobygames.com/game/58696/star-cruiser-ii-the-odysseus-project/)搜索摘要列开发者，但正文访问403，未把摘要当作原始职员证据。[D4官方发布稿](https://www.value-press.com/pressrelease/88636)对应前作《Star Cruiser》，不能移用于II。

缺口是II原版说明书、结束职员或直接参与者的具名制作记述，以及可确认法人身份的原始资料。保留unknown身份、现有发行和JHV专题待核；不把后发CD开发、前作开发或同一系列关系转为II原版制作，不改1993／1994年月异文。待取得证据后另建独立审核记录。

## 暂不宜判断的范围

- **AQUAPLUS公司其他历史作品**：当前公司介绍、品牌家族与版权声明不能替代逐作职责。只登记g037，不沿Leaf或同名品牌关系批量继承制作。
- **AQUAPLUS品牌／g039《WHITE ALBUM2》**：原署名`Leaf / AQUAPLUS`仍保留。[原来源](https://blog.aquaplus.jp/archives/2352)实际是2012原声盘公告，提及2010／2011游戏但没有明确原作制作品牌分工；[Leaf原站入口](https://leaf.aquaplus.jp/product/wa2ic/)本轮只返回年龄确认；[全年龄官网](https://aquaplus.jp/wa2/)对应后发内容，不能代替2010 PC原作证据。需原版职员／产品档案支持原作范围，或另核具体后发内容层；本批不追加制作，也不静默删除旧原作发行品牌。
- **AQUAPLUS品牌另外6部后发发行作品**：g026、g150、g166、g151、g334、g337仍只保留各自已登记发行关系，未因同域名、同名或家族关系新增原作制作。
- **ARIA三部作品的创作职责**：[产品目录](https://aria-soft.com/product)明确2006《夜明》扩充、2015《大图书馆》Library Party以及2017《千桃》主机范围。已有内容ID分别包括g267-c-2、g271-c-2，而g274后发内容仍未核。品牌身份可确认，不等于2005／2013／2016 PC原作创作归属。需逐版职员表和内容范围核定后，单独处理内容／发行层制作；当前仅订正身份，不用作品层制作填补。

## 修改文件及保护边界

1. 人工证据仅写本批JSON／Markdown；`scripts/build_entity_model.py`追加批次读取，不编辑迁移基线或原始对象。
2. `scripts/build_organizations.py`追加进度批次；`data/organizations.json`及`organizations.html`由生成器同步，主库`index.html`、脚本与样式保持不变。
3. 派生更新`entities.json`、`entity-migration-review.json`、`credits.json`、`entity-catalogue.json`、`entity-credits.csv`与实际受影响页面。所有专题成员、位置、关系边及旧职责必须完全保留；Leaf专题不新增继承职责。
4. `tests/test_creator_a4_review.py`验证当前相对基准的精确差异；A3精确差异固定到已合并快照，A首批历史计数亦使用其已应用快照，保留当前核心数据不变断言。

预期待核身份182→181；专题职责待核611→611。主库1274、内容1487、发行2487不变。不新增作品、内容、发行或亲属关系。

## 验证

执行实体及页面生成、两项数据校验、Python／Node全套测试、五个生成器一致性检查、JavaScript语法和`git diff --check`。本次全部通过：53项Python测试、217项Node测试，合计270项；实体校验为326主体／4817职责／181身份待核／611专题职责待核。主库具名创作覆盖按作品去重为321／1274。
