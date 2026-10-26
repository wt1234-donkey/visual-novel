# A—Z 创作登记：数字及其他六项（2026-10-26）

承接[Y组](entity-creator-y1-review-20261026.md)及按当前显示名补登的[C—F八项](entity-creator-cf-catchup-review-20261026.md)，依`sortFamilies`顺序核查5pb.、07th Expansion、GREE待核发行方、Mobage待核发行方、1988署名冲突待核实体、1982 ChampionSoft前身待核实体。原定312项之外补入八项，本批再审六项，当前326个实体均已登记审查；登记完成不表示每一项历史职责均已查明。

## 5pb.与07th Expansion

[MAGES.官方公告](https://mages.co.jp/topics/ir/20190726/post-145)说明2019年将5pb.业务品牌统一为MAGES.；既有5pb.品牌与法人节点、12作71条旧品牌发行职责保留，不将此后公司统一名称追溯替换原署名，逐作开发另核。

[07th Expansion官网联络页](https://07th-expansion.net/contact)明确自称制作同人PC游戏的同人サークル；据此将原`unknown/unresolved`核为`team/sourceReviewed`，不当作法律公司。[官方体验版介绍](https://07th-expansion.net/otameshi)列《ひぐらしのなく頃に》原作并称由该社团制作，[《うみねこのなく頃に》官方介绍](https://07th-expansion.net/umi_saku/)称该社团2007年发表原作小说游戏。只对g051、g174的原作层分别新增一条`originalProduction`；既有出版／平台发行署名照旧，竜騎士07个人工种、移植版开发和《咲》后发内容不据此追加。

## GREE、Mobage待核发行

[まどそふと2016公告](https://madosoft.net/news/303)仅说明《ナマイキデレーション》GREE与Mobage版本上线。服务页面名称不足以核定发行法律主体或移植制作方；g209-v3、g209-v2的两项占位发行主体继续为`unknown`，原`publisher`保留，内容关系仍为`unverified`且`contentVersionId:null`。

## 1988目录冲突与1982前身

[PC-88馆藏目录](https://www.gamepres.org/pc88/library/1988/1988_10.html)把两项1988作品列作アリスソフト，而[Champion Soft当事公司沿革](https://www.alicesoft.com/outline/contents.html)明确ALICESOFT品牌于1989年成立。同页另列MISTY为チャンピオンソフト。缺同期封套及原始发行材料，g594及专题作品的占位实体继续待核，不把二手目录署名直接改为后发品牌。

[FM-7馆藏](https://fm-7.com/museum/products/eut10qpw/)把1982旧标题归入ChampionSoft；[公司沿革](https://www.alicesoft.com/outline/contents.html)记1983年1月设立、3月法人化。另两项[馆藏记录](https://fm-7.com/museum/products/mttloqf5/)和[旧版记录](https://fm-7.com/museum/products/x3auvpz4/)仍需原包装、确切首发日与改题前后内容比对，故三项原始占位发行及1983重题版保持各自旧值。

## 结果与保护

本批核定一项团队身份、追加两条原作制作职责：326实体中身份待核由40减至39，职责由5011增至5013。专题引用2234项、`pendingRole`601项及80专题、1274主库作品、1487内容版本、2487平台发行、2175位置保持；原始目录、发行署名、未核内容关系和其他待核主体不变。[JSON逐项记录](entity-creator-numeric-review-20261026.json)包含审查顺序、来源、旧值约束与继续待核范围。

## 验证

运行`validate_data.py`、`validate_entity_model.py`、288项Python测试、222项Node测试及实体模型、实体页、组织索引、专题页的`--check`均通过。针对性测试核对326个ID无重漏、当前排序的末六项、07th独有的两条新职责及原始数据未改；公开部署由合并记录追踪。
