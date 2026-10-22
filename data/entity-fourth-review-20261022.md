# 第四批主体与专题职责核查

核查日期：2026-10-22。基准：[d5a778252b49b0b2b1de19de775692cbcd0f548a](https://github.com/wt1234-donkey/visual-novel/commit/d5a778252b49b0b2b1de19de775692cbcd0f548a)，即PR #52后main。

读取当前主体、专题正文、原始发行、开发实绩和来源后，按可直接确认／需要补充来源／暂不宜判断记录。本批实施6项：4个公司身份、2条仅专题书目制作；候选中5项需要补充来源、1项暂不宜判断。所有修改均由同名JSON独立记录并经旧值检查应用，未覆盖迁移基线。

## 可直接确认：6项

### Q1：Double Fine Productions

- 定位：`entity-name-f9e8ee919b2e`。
- 原值：unknown／unresolved；最小修正：company／sourceReviewed。
- 证据、缺口和边界：官方About介绍制作室，页脚明确Double Fine Productions, Inc.；只确认公司身份，不将创办人早年LucasArts作品倒算为公司原作，也不给已发行的复刻作品自动增加原作开发。
- 来源：[1](https://www.doublefine.com/about)；[2](https://www.doublefine.com/)。
- 应改文件：本批独立JSON、生成器；entities.json、entity-migration-review.json、主体目录及引用此主体的专题HTML。原有publisher和所有职责不变。

### Q2：BROCCOLI

- 定位：`entity-name-f00bc453a063`。
- 原值：unknown／unresolved；最小修正：company／sourceReviewed。
- 证据、缺口和边界：官方英日公司概要明确BROCCOLI Co., Ltd.／株式会社ブロッコリー。仅核定公司类型，不据综合业务介绍给授权IP作品或各平台发行批量追加开发，不新增母公司关系。
- 来源：[1](https://broccoli.co.jp/company/profile/index_en.php)；[2](https://broccoli.co.jp/company/profile/)。
- 应改文件：本批独立JSON、生成器；entities.json、entity-migration-review.json、主体目录及引用此主体的专题HTML。原有publisher和所有职责不变。

### Q3：Bandai Namco Games

- 定位：`entity-name-40ed6431d1a6`。
- 原值：unknown／unresolved；最小修正：company／sourceReviewed。
- 证据、缺口和边界：官方2015年4月1日更名公告明确旧公司名株式会社バンダイナムコゲームス及新公司名。只确认历史公司身份，保持既有Bandai Namco Games署名，不改为现名，也不合并Namco、Bandai、Banpresto或其他地区主体。
- 来源：[1](https://www.bandainamcoent.co.jp/corporate/150401/)。
- 应改文件：本批独立JSON、生成器；entities.json、entity-migration-review.json、主体目录及引用此主体的专题HTML。原有publisher和所有职责不变。

### Q4：Edia

- 定位：`entity-name-f9dfce1ab0f0`。
- 原值：unknown／unresolved；最小修正：company／sourceReviewed。
- 证据、缺口和边界：官方公司概要明确株式会社エディア／Edia Co., Ltd.，既有2016发行公告同样具名该法人。仅确认公司类型，不因手机游戏IP与sprite原作有关而给sprite追加开发或监修。
- 来源：[1](https://edia.co.jp/company/overview/)；[2](https://prtimes.jp/main/html/rd/p/000000002.000021592.html)。
- 应改文件：本批独立JSON、生成器；entities.json、entity-migration-review.json、主体目录及引用此主体的专题HTML。原有publisher和所有职责不变。

### Q5：microcabin-diamond

- 定位：`entity-microcabin`／`microcabin-diamond`。
- 原值：无作品层职责，专题catalogueAssociation／unresolved／pendingRole；最小修正：追加作品层originalProduction，仅解除该条书目职责待核。
- 证据、缺口和边界：官方「ゲーム用ソフトウェア 過去の開発実績」逐机种列出1982年11月、PC-6001的ダイヤモンドアドベンチャー，支持《钻石冒险》的原作制作关联。仅解除本条书目职责待核；文字输入和仅专题书目位置不变，不新增主库作品、内容版本或平台发行，不声称完成全部机种职员表重验。
- 来源：[1](https://www.microcabin.co.jp/works/games/)。
- 应改文件：本批独立JSON、生成器；credits.json、entity-migration-review.json、主体目录／参与CSV、microcabin.html。收录仍bibliography，不新增内容／发行。

### Q6：microcabin-dream

- 定位：`entity-microcabin`／`microcabin-dream`。
- 原值：无作品层职责，专题catalogueAssociation／unresolved／pendingRole；最小修正：追加作品层originalProduction，仅解除该条书目职责待核。
- 证据、缺口和边界：官方「ゲーム用ソフトウェア 過去の開発実績」逐机种列出1983年、MZ-80B／MZ-2000及同年9月PC-8801的ドリームランド，支持《梦境之地》的原作制作关联。仅解除本条书目职责待核；文字输入和仅专题书目位置不变，不新增主库作品、内容版本或平台发行，不声称完成全部机种职员表重验。
- 来源：[1](https://www.microcabin.co.jp/works/games/)。
- 应改文件：本批独立JSON、生成器；credits.json、entity-migration-review.json、主体目录／参与CSV、microcabin.html。收录仍bibliography，不新增内容／发行。

Q1官网页脚列公司法定英文名，与官方About制作室自述对应；不因创办人履历把LucasArts原作制作转给Double Fine。Q2官方英文公司概要与日文概要对应，综合业务不等于逐作制作。Q3使用2015年4月1日的官方更名公告，只确认旧名确为公司，不改旧署名为现名，也不统一另存的Bandai、Namco、Banpresto对象。Q4使用官方公司概要和既有2016年10月6日Edia具名发行公告，确认现有Edia身份；公告没有给sprite具名开发或监修，相关专题仍待核。

Q5、Q6读取的是公司官网“ゲーム用ソフトウェア 過去の開発実績”表，不是仅有版权或发行目录。观察到的具名行包括：1982年11月PC-6001的ダイヤモンドアドベンチャー；1983年MZ-80B／MZ-2000与同年9月PC-8801的ドリームランド。只核定原作制作关联，不用其他机种条目增加平台发行，不声称已穷尽原始职员表或所有受托分工。官网先前成功返回开发实绩文本，后续重取出现502／503，本文件保留成功读取范围及重取限制。

两作的文字输入标签、原年份、身份、书目位置和准入边界全部不变；“制作已核实”与“进入主库”分别判断。

## 需要补充来源／暂不宜判断

| 项目 | 分类 | 证据缺口与最小方案 |
| --- | --- | --- |
| QD1 `entity-name-61e191a86b41` | 暂不宜判断 | 平台保留RIGHTWAY发行，但本轮公司站点只有株式会社ライトウェイ及渋谷地址，缺与游戏业务直接对应的链接；有同名公司风险，不凭英文标志或名称归为同一法人。需游戏合同／发行官方联络或同期公司页。 |
| QD2 `entity-name-431d2fb7a95c` | 需要补充来源 | 官网本轮403；平台开发者列CFK Co., Ltd.，但当前EULA首句拼接了Bliss Brain与CFK，需更清晰官方公司资料对应现有发行名义。本批不据混合条款归并法人或变更历史发行。 |
| QD3 `entity-name-c65fb9857dc9` | 需要补充来源 | 加賀電子原始公告可检索到株式会社サイバーフロント，但全文本轮403；官方IR搜索文本与本轮PDF提取不一致，暂不将搜索摘要当成完成全文复核。保留身份待核并继续找原始公告附件。 |
| QD4 `entity-microcabin` | 需要补充来源 | 本轮已读取的开发实绩文本没有定位到这三个具名条目，二手资料和版权署名不足以独立核定；需原版职员表、说明书或完整具名官方资料。 |
| QD5 `entity-sprite` | 需要补充来源 | Edia原始配信公告能确认其公司身份和配信，但没有具名sprite开发或监修；保持sprite专题职责待核。 |
| QD6 `entity-key` | 需要补充来源 | Key官方配信公告确认服务上线与内容介绍，但未明确其直接制作／开发分工，不因官网发布新闻就解除职责待核。 |

候选来源按本批JSON逐项保存。QD1已完整读取PlayStation的RIGHTWAY发行署名和rightway.jp的公司名／地址，但无可靠业务对应，不把同名公司作为已匹配证据。QD2已读Steam开发者字段与EULA；混合的公司名首句不能替代清晰法人身份资料。QD3读取到原始公告的官方检索文本，全文403；IR PDF的搜索文本与本轮提取未一致对应，故不应用身份订正。QD4未定位到具名官方开发行；QD5、QD6只有发行／服务开始公告，未确认所问主体的开发分工。

## 最小实施及保护范围

- 输入：`data/entity-fourth-review-20261022.json`与本文件；deferredReviews只记缺口，不参与生成。
- 生成器增加第四批读取，允许核对明确的dossierOnlyWorks引用。仍检查expectedPlacement、专题主体、旧职责与重复追加；不改变任何位置规则。
- 仅4个实体的类型、核对状态、来源、说明变化；稳定ID、名称、别名、日期、relations与dossiers不变。
- 全部旧4753条参与记录逐项保留；追加2条书目作品职责；只更改microcabin-diamond与microcabin-dream的两条专题引用。
- 四份核心JSON、作品／内容／平台发行、位置索引、两个迁移基线、前三批证据逐字保留。前三批精确差异继续对照各自已应用快照；本批当前差异单独对照本批baseCommit。

| 项目 | 本批前 | 本批后 |
| --- | ---: | ---: |
| 实体 | 326 | 326 |
| 参与记录 | 4753 | 4755 |
| 专题引用 | 2234 | 2234 |
| 待核身份 | 187 | 183 |
| 职责待核专题引用 | 613 | 611 |
| 主库作品／内容／平台发行 | 1274／1487／2487 | 1274／1487／2487 |

实体／数据库校验通过；Python34项、Node207项全部通过。三个生成器的 `--check` 与 `git diff --check` 均通过，CSV已同步。未做真实浏览器画面验收，以数据、HTML卡片、主库过滤行为及生成器一致性检查验证。
