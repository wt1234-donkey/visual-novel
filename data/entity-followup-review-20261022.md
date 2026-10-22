# 第二批主体与专题职责核查及实施记录

核查日期：2026-10-22（北京时间）。基准：[ee0694de5dc51cc773bf9e76ae72a375da82211d](https://github.com/wt1234-donkey/visual-novel/commit/ee0694de5dc51cc773bf9e76ae72a375da82211d)，即首批核查PR #50合并后的main。

本批继续读取主体档案、专题卡片、原始publisher、参与记录及来源。优先处理高频发行主体的身份，以及前批已发现线索但缺单作证明的制作职责。它是独立订正，不覆盖10月21日迁移基线或首批记录。

## 可直接确认：8项（5项身份、3条职责）

下列“来源”均为2026-10-22核对的原始机构／官方站点。结论仅限所述主体类型或作品职责；不能将其扩大到各时期合同、逐作本地化、母公司开发或其他平台内容。

### F1：MangaGamer

- 定位：`entity-name-85a1fd56da66`。
- 旧值：unknown／unresolved；最小修正：brand／sourceReviewed，保持ID、别名、日期。
- 证据及边界：隐私政策1.1明确将MangaGamer称为品牌并说明Japan Animation Contents的运营身份；条款页亦列出该法人。身份足够，逐作合同、开发和本地化职责仍缺。旧24条publisher保留，不建立新运营关系。
- 来源：[1](https://www.mangagamer.com/privacy_policy.php)；[2](https://www.mangagamer.com/terms.php)。
- 应改文件：独立JSON本项、生成器；`data/entities.json`、`data/entity-migration-review.json`、主体目录与主体页。

### F2：NekoNyan Ltd.

- 定位：`entity-name-acccc0db4bce`。
- 旧值：unknown／unresolved；最小修正：company／sourceReviewed，保持ID、别名、日期。
- 证据及边界：官方PDF为2018年3月5日更新的服务条款，协议主体为NekoNyan Ltd.；Companies House登记10729116为NEKONYAN LTD私人有限公司。只确认公司类型，不补写历史地址、法人延续或逐作开发分工。
- 来源：[1](https://nekonyansoft.com/uploads/terms_and_conditions.pdf)；[2](https://find-and-update.company-information.service.gov.uk/company/10729116)。
- 应改文件：独立JSON本项、生成器；`data/entities.json`、`data/entity-migration-review.json`、主体目录与主体页。

### F3：aNCHOR

- 定位：`entity-name-5b146b15540c`。
- 旧值：unknown／unresolved；最小修正：company／sourceReviewed，保持ID、别名、日期。
- 证据及边界：官方公司概要明确株式会社aNCHOR／aNCHOR Inc.。2011年成立时间不等于现名启用时间，旧平台发行字符串不倒改。
- 来源：[1](https://ancr.jp/company/)。
- 应改文件：独立JSON本项、生成器；`data/entities.json`、`data/entity-migration-review.json`、主体目录与主体页。

### F4：D4 Enterprise

- 定位：`entity-name-959a8e1f98f6`。
- 旧值：unknown／unresolved；最小修正：company／sourceReviewed，保持ID、别名、日期。
- 证据及边界：官方公司概要明确株式会社D4エンタープライズ。复刻配信、版权管理和原作开发须分别取证，不能由Project EGG发行推导制作。
- 来源：[1](https://d4e.co.jp/company)。
- 应改文件：独立JSON本项、生成器；`data/entities.json`、`data/entity-migration-review.json`、主体目录与主体页。

### F5：Chunsoft

- 定位：`entity-name-21365baf366d`。
- 旧值：unknown／unresolved；最小修正：company／sourceReviewed，保持ID、别名、日期。
- 证据及边界：Spike Chunsoft官方沿革明确1984年成立株式会社チュンソフト、2012年与Spike合并。Chunsoft、Spike及Spike Chunsoft继续使用不同ID，不追加前身／归并关系。
- 来源：[1](https://www.spike-chunsoft.co.jp/company/outline/)。
- 应改文件：独立JSON本项、生成器；`data/entities.json`、`data/entity-migration-review.json`、主体目录与主体页。

### F6：g1252

- 定位：`entity-minatosoft`／`g1252`。
- 最小修正：仅追加作品层 `originalProduction`；该专题由职责待核改为原作制作。
- 证据及边界：官方第一季第六卷商品页的搜索可检索文本具名PC游戏Ⅱ《结城友奈S》，并列企划タカヒロ、制作みなとそふと；2018年官方下载公告正文再次明确Minato版S。官方Pony Canyon宣传视频的可检索说明也列相同署名。本轮商品页全文请求503（另一通道403），视频全文打开受限：未声称已观看视频或读取完整商品页。判断使用官方可检索的具名制作署名与可完整读取的官方公告交叉核对。既有2017下载卡不是新内容，Hawk Eye仍待核。
- 来源：[1](https://yuyuyu.tv/season1/bddvd/bddvd_06.php)；[2](https://yuyuyu.tv/news/archives/1563)；[3](https://www.youtube.com/watch?v=PwN4La5-sgQ)。
- 应改文件：独立JSON本项、生成器；`data/credits.json`、主体目录、参与CSV与主体页；`minatosoft.html`及专题索引。

### F7：g1254

- 定位：`entity-minatosoft`／`g1254`。
- 最小修正：仅追加作品层 `originalProduction`；该专题由职责待核改为原作制作。
- 证据及边界：TBS・MBS官方商店商品页完整可读，商品为2018《勇者之章》BD，特典PC游戏《结城友奈A》段明确企划タカヒロ、制作みなとそふと。Studio五组图像制作另列，不把动画BD当作游戏平台发行。原动画官网商品页本轮503，保留为旧来源但不单独依赖它。
- 来源：[1](https://animaru.jp/anmr/product/P0084939)；[2](https://yuyuyu.tv/season2/product/bd/yusha.php)。
- 应改文件：独立JSON本项、生成器；`data/credits.json`、主体目录、参与CSV与主体页；`minatosoft.html`及专题索引。

### F8：g232

- 定位：`entity-yuzusoft_sour`／`g232`。
- 最小修正：仅追加作品层 `productionBrand`；不改任何父品牌专题职责。
- 证据及边界：Steam商店开发者字段为YUZUSOFTSOUR，发行方另列NekoNyan与HIKARI FIELD，正文也说明由Sour制作；官方Google Play介绍明确SOUR姊妹品牌首作。旧originalPublishingBrand与发行层publishingBrand全部保留，仅追加productionBrand。父品牌Yuzusoft的g232专题引用仍pendingRole。
- 来源：[1](https://store.steampowered.com/app/1662840/PARQUET/)；[2](https://play.google.com/store/apps/details?hl=ja&id=com.yuzusoft.sour.parquet)。
- 应改文件：独立JSON本项、生成器；`data/credits.json`、主体目录、参与CSV与主体页；父专题保留待核。

## 需要补充来源／暂不宜判断

这些记录只存证据缺口，不作为生成器的身份或职责规则；首批原始建议保留，状态进展以本批为准。

| 首批项 | 本批状态 | 证据缺口与最小方案 |
| --- | --- | --- |
| B1 | identityResolvedScopeStillLimited | 本批F1确认品牌身份；各时期合同与逐作本地化仍未扩核。 |
| B6 | childProductionConfirmedParentPending | F8只确认SOUR制作品牌；父品牌直接职责仍待核。 |
| B8 | needsMoreSources | 新增官方System3.9支持页可确认Alice Blue作品使用该引擎；不能据引擎使用推定整作开发协力，原始职员表仍缺。 |
| B3 | needsMoreSources | Legend同期采访及目录支持英国语境；仍缺逐版原始署名，本批不合并两个Legend ID。 |
| B4 | needsMoreSources | Mosaic三份既有原厂手册链接本轮均未成功读取，不以旧审核摘要替代重验。 |
| B2 | needsMoreSources | 国际JAST现行官方自述与日本旧JAST未取得完整历史连续性证明，保持独立。 |
| B5 | needsMoreSources | 复合发行署名及个人贡献仍不等于Minato品牌开发职责。 |
| B7 | needsMoreSources | CHiRAL品牌制作与Nitroplus公司职责继续分开。 |
| C1 | notReadyToJudge | Mobage／GREE实际发行者和内容证据未齐。 |
| C2 | notReadyToJudge | 1988目录署名与品牌年代冲突缺原证，继续待核。 |

Alice Blue《王子殿下Lv1.5》新增读取的[官方System3.9支持页](https://www.alicesoft.com/support/sys39v545.html)支持引擎关联；引擎支持不足以独立证明整作开发协力。维持g545的Alicesoft专题待核，继续找原版职员表／手册。

## 文件入口和最小实施边界

- 人工输入：`data/entity-followup-review-20261022.json`，生成器按顺序读取首批及本批；原始旧值与范围不符即拒绝应用。
- `scripts/build_entity_model.py`：允许具名品牌身份订正但显式保留旧发行角色；可给子品牌追加制作职责且不指定父专题。不是按名字后缀或母子关系推断。
- 派生输出：`data/entities.json`、`data/credits.json`、`data/entity-migration-review.json`、`data/entity-catalogue.json`、`data/entity-credits.csv`、`entities.html`、受影响主体页和专题页。
- 完整保留：四份原始核心JSON、实体关系与专题对象、全部旧参与记录、作品／内容／平台发行ID、位置、两个迁移基线、首批证据文件。没有新作品、新内容版本或平台发行。
- 回归覆盖：本批只改变5个实体，保留旧别名与全部旧职责，只增加3条作品职责，只解除Minato的S与A两条专题待核；Hawk Eye、Yuzusoft父品牌、Alicesoft例子的待核保持。首批精确差异仍对照首批合并快照，当前数据又与该快照精确比较，确保前批不被改写。

## 结果与验证

| 项目 | 本批前 | 本批后 |
| --- | ---: | ---: |
| 实体 | 326 | 326 |
| 参与记录 | 4747 | 4750 |
| 专题引用 | 2234 | 2234 |
| 待核身份 | 197 | 192 |
| 职责待核专题引用 | 616 | 614 |
| 主库作品／内容版本／平台发行 | 1274／1487／2487 | 1274／1487／2487 |

实体校验、数据库校验均通过；Python回归26项、Node回归205项全部通过。三个生成器的 `--check` 与 `git diff --check` 均通过，CSV已重新生成。未进行真实浏览器画面验收；使用生成器一致性、HTML卡片与数据库回归检查。
