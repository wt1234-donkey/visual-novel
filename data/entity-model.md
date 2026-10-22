# 公司、品牌、参与角色与作品位置

本规范落实2026-10-21《叙事作品数据库与专题分类改造规划》。新增实体与参与索引，保留原作品、内容、发行及旧专题档案。仅维护 wt1234-donkey/visual-novel。

## 独立的四个维度

1. 实体身份：公司／组织、品牌、制作团队、刊物／出版名义、个人、身份待核。
2. 参与角色：原作制作、开发、联合制作、制作品牌、原作发行品牌、发行署名、发行品牌、移植开发、本地化、授权合作、监修、版权署名。
3. 收录位置：主库、叙事／跨类型关联、仅专题书目；玩法参考表继续保存目录参考，不产生主库身份。
4. 互动方式：沿用既有受控标签；不凭操作形式推定叙事主次或公司关系。

## 文件

- `entities.json`：稳定实体ID、类型、名称／检索别名、历史说明、独立日期、来源；专题主题、范围和关系另外保存。
- `credits.json`：以作品、内容版本或平台发行ID为目标的署名；每条记录保存实体、角色、原文、来源、核对状态和适用范围。其 `dossierMemberships` 保存全部既有专题引用及关系分组。
- `entity-migration-review.json`：全部原发行名称与旧别名的映射、待核身份和职责数量。不将不确定名称强行归为公司或品牌。
- `work-classification.json`：全库各作品档案的既有位置和复核队列；本轮 `notReassessed` 表示尚未重新核定叙事主次。
- `entity-migration-baseline.json`：本轮四份核心原档案的SHA-256审计值、逐对象摘要及数量基线。新作品可以追加；既有对象发生变更时生成器拒绝重新覆盖基线。
- `entity-catalogue.json`：上述数据供主库检索的派生索引，不是另一套人工编辑的权威记录。
- `entity-credits.csv`：逐参与记录导出，角色作品数可能重叠，不能相加当作独立游戏总数。

`publisher` 原文与 `publisherCompanies` 仍作为历史／兼容字段保存。旧 `publisherAliases` 中的公司归档不再支配新实体检索；同一实体的拼写别名与不同实体的品牌归属明确分开。Nitro+CHiRAL、Silky’s Plus子品牌、FairyTale分支等在新模型保留独立身份。

## 证据等级与未知状态

- `sourceReviewed`：本轮核对所列来源支持的身份或职责，不表示已核定所有历史时期。
- `existingDossier`／`existingCredit`：从既有专题或发行记录继承的事实，保留原证据，不声称本轮逐一外部重验。
- `unresolved`／`pendingRole`：身份或具体职责未确认。发行有署名，不等于法人已知；进入专题，也不等于参与开发。

原作首发品牌署名自动生成的是 `originalPublishingBrand`，不是开发职责。`productionBrand` 和 `originalProduction` 仅用于已有品牌目录或逐项制作资料支持的范围。ANIPLEX.EXE是发行品牌；《ATRI》的Frontwing与枕为联合制作方，两者不混用。

所有关系可以带起止时间和精度；未知终点不解释为持续至今。运营关系不自动给母公司增加全部历史发行或直接开发署名。Falcom、T&E SOFT、Banpresto涉及复杂主体变化，先以沿革专题保存，主体连续性未核部分不伪造。

## 筛选规则

- 品牌：制作品牌、原作发行品牌、具体发行品牌分别命中。原作品牌作用于该作品的已收录版本；仅后续新增的品牌署名只命中其适用内容／发行。
- 原作制作／开发：只读取原作制作、开发或联合制作，不把发行角色推导成开发。暂未核定职责的作品不作为“没有开发方”的结论。
- 发行主体：只匹配具体发行层的发行署名／品牌；平台、年份、配音等条件须匹配同一条发行记录。
- 参与主体与职责：可以查询监修、版权、移植等关系，内容层职责只作用于关联该内容的发行。
- 专题范围与关系：保留本品牌／原作、联合、发行、授权与职责待核五组；同一专题内每部作品只显示一张卡，卡片可列多个角色。
- 品牌家族扩展：默认关闭，显式开启后才沿已登记关系扩展；它是目录查询，不是历年公司归属断言。
- 历史发行归档：保留旧筛选作为兼容入口，可能采用旧的公司归并；新查询优先使用发行主体。

## 收录与分类边界

本轮不改变1274部主库作品、1487个内容版本、2487条平台发行；现有769条专题关联记录与132条书目保留。后两项未经跨专题身份核对，不可相加宣称独立作品数。每个档案进入位置审核表，不按标题相同自动合并。

既有养成、输入式及其他例外沿用。关联作品只有取得叙事主导、独立身份和内容证据才可转入主库；RPG、ADV、问答及IP标签均不足以自动决定。文字输入只是互动标签，原有范围限制与缺乏资料分别保留，不在关系迁移中批量增删。

后续具体转入须复用作品身份、保留旧锚点和玩法总表引用；不据此新增普通移植或将未核内容关联改成已知相同／新增。

## 日期、统计与旧链接

80专题的旧URL、全部旧页面ID、历史分期说明、UK和品牌延续标签继续有效。首页类型标签取代自动“社”后缀，五年分组仍按专题关联主库作品的最早原作首发年，明确不代表公司成立、品牌启用或首次发行年。GAINAX仍为1989年、1985—1989组；GAINA暂无主库作品。

公司数、品牌数、其他主体数与专题数分别统计。一个沿革专题可能与另一个专题共享公司身份；同一作品的制作、发行、授权角色有重叠，不相加。角色数量均按对应作品ID去重。

## 更新与校验

编辑角色与主体规则后运行：

```sh
python3 scripts/build_entity_model.py
python3 scripts/build_entity_pages.py
python3 scripts/build_company_pages.py
python3 scripts/validate_entity_model.py
python3 scripts/validate_data.py
python3 -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.mjs
python3 scripts/build_entity_model.py --check
python3 scripts/build_entity_pages.py --check
python3 scripts/build_company_pages.py --check
```

主体、角色与位置索引为派生数据；人工核定规则由 `build_entity_model.py` 的具名映射及独立审核记录提供，不能只修改生成JSON或HTML。

2026-10-22首批核查使用 `entity-priority-review-20261022.json` 与同名Markdown记录。JSON的 `identityCorrections` 保留稳定ID、订正前类型与状态、核定类型、来源和范围；`creditAdditions` 保存逐作品职责、旧待核状态、原文及限定说明。生成器检查旧值后仅应用2项身份与4项职责，不改迁移基线、身份关系或原始发行。新增参与记录用 `reviewId`、`reviewRecord` 关联独立审查；专题卡片同时显示范围。`deferredReviews` 只登记证据缺口，不能作为身份映射、职责或位置变更规则。后续批次仍需独立证据与提交，不能把候选意见升级为已核事实。

## 名称格式（2026-10-21）

日文主体名称的显示格式为英文／拉丁字（日文），使用全角括号，例如 `HummingBird Soft（ハミングバードソフト）`、`Madosoft（まどそふと）`、`Minato Soft（みなとそふと）`。名称表 `entity-display-names.json` 同时管理旧中文名、日文名与旧英文拼写的显示。已有纯英文名称不强行补造日文名；国家、沿革和待核说明继续独立保留其含义。

`english`、`japanese` 为显示组成，不代表法人登记字段。`basis` 区分既有双语名（`existingBilingualName`）、目录拼写／惯用转写（`catalogueSpelling`）、罗马字（`romanization`）、编辑译名（`editorialTranslation`）；未宣称全部为官方英文。月星組、花月組暂无确证英文名，分别以 Moon-Star Group、Flower-Moon Group 作编辑译名，保留原文便于核对。个别本轮补核的名称另存 `source`。

`entity_names.py` 在历史署名解析与参与记录生成完成后应用显示名，并把旧名称、英日文各部分加入检索别名。名称表不参与身份解析：即使不同待核主体显示同名，也不合并 ID、身份、关系或职责。主体索引、主库筛选、专题导航、标题与参与 CSV 共用同一结果。历史发行归档的筛选值保持原值，只改标签；发行行在显示新名时同时列出“署名原文”。作品正文、史料引文、核心 JSON 与旧历史 CSV 保留原文。

修改名称表后运行本节上方全部生成器和校验，不直接编辑派生 JSON／HTML。

如需纠正原始史实，应在独立变更中保留旧证据、说明订正，并复核基线断言；不得仅为让生成器通过而重算或删除基线。

2026-10-22第二批使用 `entity-followup-review-20261022.json` 及同名Markdown，独立于首批和迁移基线。生成器按批次读取，核对旧身份／作品职责后，仅追加5项身份订正与3条作品职责。身份订正不得重复命中同一ID；MangaGamer的品牌身份使用显式 `preserveReleaseRoles: true`，保留旧 `publisher`，不由类型变化自动生成 `publishingBrand` 或 `originalPublishingBrand`。`beforeWorkRoles` 记录追加前的作品层角色；`dossierId: null` 允许仅给具名子品牌追加职责，不将职责上推到父品牌专题。指定专题的订正必须核对其主体和旧待核状态，才解除该条待核。

2026-10-22第三批为 `entity-third-review-20261022.json` 与同名Markdown，独立记录5项公司身份和3条作品职责。Nitroplus公司与同名品牌继续分开；具名制作室／品牌证据只追加品牌制作，不解除公司专题待核。OVERDRIVE具名原作开发则核对自身专题旧状态后解除单条待核。前两批精确差异继续保存在其已应用快照回归中，当前新增差异对照本批baseCommit验证。

2026-10-22第四批为 `entity-fourth-review-20261022.json` 与同名Markdown：4项公司身份与2条Micro Cabin书目制作。明确 `expectedPlacement: bibliography` 的具名订正可核对 `dossierOnlyWorks` 并解除单条书目职责待核；收录位置继续bibliography，不建立主库作品、内容或发行。角色核查与主库准入分别判断。旧批次精确差异仍对照其应用快照，当前数据另以本批baseCommit检验。

2026-10-22 A—Z创作登记首批使用 `entity-creator-a-review-20261022.json` 与同名Markdown。顺序核查前8个A主体，仅应用5条具名作品职责及1项Akatsuki Games公司身份订正。其余核查结论与进度不产生职责，保持原始发行、主库准入、身份关系和迁移基线。作品职责已核与主体法律身份待核可并存；具体范围见独立记录。

2026-10-22 A—Z第二批使用 `entity-creator-a2-review-20261022.json` 与同名Markdown；从Alchemist连续到Alicesoft，累计12／32个主体完成证据分流，新增40条ALICESOFT制作品牌。没有身份或关系订正；子品牌、前身与75条旧专题待核不继承制作职责，原作／关联位置不变。首批精确差异固定至其应用快照，当前批次单独对照baseCommit检验。
