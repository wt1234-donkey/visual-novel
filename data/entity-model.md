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

2026-10-24 I 字母首批使用 `entity-creator-i1-review-20261024.json` 与同名 Markdown，按 IBM、IDEA FACTORY、Imageepoch 连续核查 3／13。IBM 七条既有发行与四项待核关联保持；IDEA FACTORY 和 Imageepoch 各独立订正一项公司身份。Imageepoch 当事方明确将《ソニプロ》製作与 Tamsoft 开发区分，仅追加前者原作制作。3DS《闘神都市》后发改编开发先在审计记版本范围，不倒填至 1994 年原作；历史关系、作品身份和迁移基线不变。下一家 iMel。

2026-10-24 I 字母第二批使用 `entity-creator-i2-review-20261024.json` 与同名 Markdown，按 iMel、Impact Interactive Publishing、IMYUIC(ALICESOFT)、Index Corporation 连续核查，I 累计 7／13。iMel已有六条限定移植开发不重复，Impact及2013年旧Index各订正一项公司身份，均不由出版／运营倒推原作开发。IMYUIC与AliceSoft的复合名义由2022年历史管理改名产生，保留旧数据并单列史实订正需求，不自动合并2020原品牌或2022独立品牌；下一家 Infocom。

2026-10-24 I 字母第三批使用 `entity-creator-i3-review-20261024.json` 与同名 Markdown，连续核查 Infocom、Infogrames、Innocent Grey，I 累计 10／13。根据权利方原始代码公告，只给 Infocom 的《Zork I–III》家用机商业版追加三条原作制作，不并入早期大型机作品；Infogrames 以当事方同期新闻稿和 SEC 申报确认历史美国公司身份，与法国母公司、另一子公司及后起同名品牌分开。Innocent Grey 的11部制作品牌沿用，不重复追加。旧发行、其余职责待核、作品位置、主体关系及迁移基线不改；下一家 Interchannel。

2026-10-22第二批使用 `entity-followup-review-20261022.json` 及同名Markdown，独立于首批和迁移基线。生成器按批次读取，核对旧身份／作品职责后，仅追加5项身份订正与3条作品职责。身份订正不得重复命中同一ID；MangaGamer的品牌身份使用显式 `preserveReleaseRoles: true`，保留旧 `publisher`，不由类型变化自动生成 `publishingBrand` 或 `originalPublishingBrand`。`beforeWorkRoles` 记录追加前的作品层角色；`dossierId: null` 允许仅给具名子品牌追加职责，不将职责上推到父品牌专题。指定专题的订正必须核对其主体和旧待核状态，才解除该条待核。

2026-10-22第三批为 `entity-third-review-20261022.json` 与同名Markdown，独立记录5项公司身份和3条作品职责。Nitroplus公司与同名品牌继续分开；具名制作室／品牌证据只追加品牌制作，不解除公司专题待核。OVERDRIVE具名原作开发则核对自身专题旧状态后解除单条待核。前两批精确差异继续保存在其已应用快照回归中，当前新增差异对照本批baseCommit验证。

2026-10-22第四批为 `entity-fourth-review-20261022.json` 与同名Markdown：4项公司身份与2条Micro Cabin书目制作。明确 `expectedPlacement: bibliography` 的具名订正可核对 `dossierOnlyWorks` 并解除单条书目职责待核；收录位置继续bibliography，不建立主库作品、内容或发行。角色核查与主库准入分别判断。旧批次精确差异仍对照其应用快照，当前数据另以本批baseCommit检验。

2026-10-22 A—Z创作登记首批使用 `entity-creator-a-review-20261022.json` 与同名Markdown。顺序核查前8个A主体，仅应用5条具名作品职责及1项Akatsuki Games公司身份订正。其余核查结论与进度不产生职责，保持原始发行、主库准入、身份关系和迁移基线。作品职责已核与主体法律身份待核可并存；具体范围见独立记录。

2026-10-22 A—Z第二批使用 `entity-creator-a2-review-20261022.json` 与同名Markdown；从Alchemist连续到Alicesoft，累计12／32个主体完成证据分流，新增40条ALICESOFT制作品牌。没有身份或关系订正；子品牌、前身与75条旧专题待核不继承制作职责，原作／关联位置不变。首批精确差异固定至其应用快照，当前批次单独对照baseCommit检验。

2026-10-22 A—Z第三批使用 `entity-creator-a3-review-20261022.json` 与同名Markdown；连续核查第13—20个主体，追加American Laser Games两作制作、Applique子品牌4作及本品牌8作制作品牌。身份关系不改，子品牌不解除母品牌专题待核，2016先行LVN与后续扩充的职责不混用；ANIPLEX.EXE的製作／制作资料差异继续具名待核。

2026-10-23 A—Z第四批使用 `entity-creator-a4-review-20261023.json` 与同名Markdown；连续核查AQUAPLUS公司、同名品牌、ARIA、Arsys Software及ASa Project，累计25／32。新增3条具名职责（2部作品），独立确认ARIA品牌身份并显式保留旧发行职责；ASa Project既有22条制作品牌不重复录入。公司／品牌不同维度按作品去重，原作与后发主机职责分开，旧专题待核、实体关系和迁移基线不改。

2026-10-23 A—Z第五批使用 `entity-creator-a5-review-20261023.json` 与同名Markdown；连续核查ASCII、Asmik、Asoberu!、Atari与Atlus，累计30／32。新增3条ASCII具名原作制作职责（2部主收录、1部专题关联），并独立确认Asmik、Atari、Atlus为公司主体；保留Asmik发行、Atari／Atari Melbourne House及Atlus／Dennou Eizou Seisakusho的既有分工，不以发行或品牌沿革倒推开发。Asoberu!与ASCII其余职责继续按证据缺口待核，专题位置、旧关系和迁移基线不改。
2026-10-23 A—Z第六批使用 `entity-creator-a6-review-20261023.json` 与同名Markdown；完成A字母32／32，下一家为Bandai Namco Games。AUGUST沿用既有品牌档案与《爱丽丝秘迹》限定联合制作记录，不重复追加；依据あざらしそふと官方页面与版权提示，将 `entity-name-a7f6066af4b9` 从身份待核订正为品牌。保留其与SMEE的联合发行署名，不自动建立Nexton母公司关系，不新增开发职责；主库作品、内容版本、平台发行及迁移基线不变。
2026-10-23 A—Z的B字母首批使用 `entity-creator-b1-review-20261023.json` 与同名Markdown；按Bandai Namco Games、Bandai Visual、Banpresto连续核查3／10，累计35／42。依据集团历史与2018年正式公告，仅将Bandai Visual的历史公司身份从unknown订正为company。Bandai Namco Games既有公司身份不变；Banpresto旧游戏公司、后设景品公司和品牌延续暂不混并。三家均不从发行／业务移转证据推断逐作开发，旧作品和迁移基线不变；下一家BLACKRAINBOW。
2026-10-23 B字母第二批使用 `entity-creator-b2-review-20261023.json` 与同名Markdown；连续核查BLACKRAINBOW、Bliss Brain、Blizzard Entertainment，B累计6／10、A—Z累计38／42。官方产品规格确认BLACKRAINBOW为品牌，暴雪公司资料确认Blizzard Entertainment为公司；Bliss Brain既有公司身份与2024年发行沿用。仅订正两个待核身份，保留《かすみ遊戯》原版／DVDPG后发版与Diablo／Hellfire的不同发行和增补范围，不推导开发职责；下一家BPS。
2026-10-23 B字母第三批使用 `entity-creator-b3-review-20261023.json` 与同名Markdown；连续核查BPS、BROCCOLI、Brøderbund、Byakuya Shobo，B累计10／10、A—Z累计42／42。独立来源确认BPS与Brøderbund是历史游戏发行公司，BROCCOLI既有公司身份沿用；白夜書房官网可证公司现状，但旧版“白夜書店”与该发行主体的对应关系尚缺原版版权页，继续待核。没有新增开发职责或公司沿革关系，既有发行与迁移基线不改；下一家Cabbage Soft。
2026-10-23 C字母首批使用 `entity-creator-c1-review-20261023.json` 与同名Markdown；连续核查Cabbage Soft、CAPCOM、Caramel Box、Carry Lab、CFK，C累计5／18、A—Z累计47／60。依据原版职员署名，仅给Caramel Box两部原作登记制作品牌，独立订正其品牌身份及CFK公司身份。Cabbage既有8部制作品牌沿用；CAPCOM首版开发和Carry Lab旧专题关联保留证据缺口。后发版发行、关系和迁移基线不变；下一家Chunsoft。
2026-10-23 C字母第二批使用 `entity-creator-c2-review-20261023.json` 与同名Markdown；从Chunsoft连续核查到Comptiq，C累计10／18、A—Z累计52／60。旧Chunsoft两部自有代表原作与《善人シボウデス》当时官网具名开发限定登记3条原作制作；Coktel Vision S.A.依并购方同期披露独立订正为公司。Cinematronics原街机制造／发行、Clochette已登记10条制作品牌、Comptiq刊物发行继续分开，不据此扩展开发、关系和后发版本职责；下一家Core Magazine。

2026-10-23 C字母第三批使用 `entity-creator-c3-review-20261023.json` 与同名Markdown；连续核查Core Magazine、CoreMoreco、CROSSNET、Crystal Soft及CUBE，C累计15／18、A—Z累计57／60。依据公司交易表示、原版职员表转录及历史权利方目录分别订正Core Magazine、CROSSNET、Crystal Soft三个公司身份；CoreMoreco品牌身份缺原始材料继续待核。CUBE既有11条创作沿用，FAVORITE五作的制作不转给CROSSNET；只保存既有发行，不新增开发职责或公司关系。下一家CUFFS。

2026-10-23 C字母第四批使用 `entity-creator-c4-review-20261023.json` 与同名Markdown；连续核查CUFFS、Cyan Worlds, Inc.、CyberFront，完成C字母18／18，A—Z累计60／60。CUFFS已登记六部主品牌制作，不能把同页CUBE/Sphere系列归并。Cyan现行法人据官方法律条款、CyberFront历史法人据母公司同期披露各自订正为公司；《Riven》1997原作、2024重制发行以及跨品牌移植开发均保持各自证据边界。没有新增作品开发或关系；下一家D3 Publisher。

2026-10-23 D字母首批使用 `entity-creator-d1-review-20261023.json` 与同名Markdown；连续核查D3 Publisher、D4 Enterprise、Data East、dB-SOFT，D累计4／10、A—Z累计64／70。D3官网及2007年官方产品目录支持其公司身份，独立订正旧待核身份；其PS2后发发行不推断PC原作开发。D4复刻配信、Data East各期发行和dB-SOFT旧专题关联继续分别按版本与原始署名核定。没有新增创作职责或组织关系；下一家Digital Leisure。

2026-10-23 D字母第二批使用 `entity-creator-d2-review-20261023.json` 与同名Markdown；核查Digital Leisure、Digiturbo、DMM GAMES、DMM GAMES／AUGUST，D累计8／10、A—Z累计68／70。前三项分别以公司官网、Nitroplus正式沿革及EXNOA平台与商号资料独立订正身份，保留所有原发行角色；DMM GAMES同名旧法人不自动合并。复合署名继续待核，AUGUST既有合作开发事实不由此重复推导。没有新增创作职责或组织关系；下一家Double Fine Productions。

2026-10-23 D字母第三批使用 `entity-creator-d3-review-20261023.json` 与同名Markdown；核查Double Fine Productions、DreamWorks Interactive，D累计10／10、A—Z累计70／70。Double Fine原有公司身份沿用，官方《Broken Age》片尾支持新增一条原作制作；LucasArts三部旧作的后发复刻另按版本核，不倒填原版创作。DreamWorks Interactive依据微软1996年公告独立订正公司身份，两部旧发行保留，逐作创作待原始片尾；合资背景不自动增加单方母子关系。下一家E3 Staff。

2026-10-24 I4完成I组13／13，审核见 `entity-creator-i4-review-20261024.json` 及同名Markdown。日文Interchannel与IRI-CT各独立订正公司身份；英文Interchannel的2002／2006混合旧署名另核，不合并节点或增加制作职责。下一家J. K. Greye Software。

2026-10-24 J1完成J组5／5，独立记录见 `entity-creator-j1-review-20261024.json` 与同名Markdown。现代JAST与JAST USA各自订正公司类别，不合并身份；日本旧JAST的g015据明确开发馆录增加一条原作制作。JHV发行、J.K.Greye版权及其他未核职责各自保留。下一家KADOKAWA。

2026-10-24 K1核查K组前六项，独立记录为 `entity-creator-k1-review-20261024.json` 与同名Markdown。两条角川游戏、两条角川书店旧节点各订正公司类别，同名法人分设及逐版映射仍需独立审查；KADOKAWA混合时期与三方复合节点保持unknown，不加开发。进度K组6／14；下一家Kaga Create。

2026-10-24 K2核查K组第7—10项，独立审核为 `entity-creator-k2-review-20261024.json` 与同名Markdown。加賀クリエイト及原KID各订正公司类别，前者现行官网已显示ENTERGRAM，后者同名后设品牌另核；Key既有21作与绯染天空限定合作、KT公司发行均沿用。无新增开发；进度K组10／14，下一家KOEI。

2026-10-25 K3完成K组14／14，独立审核见 `entity-creator-k3-review-20261025.json` 与同名Markdown。工画堂独立订正公司身份，ascii-haja与g040按当事方资料各记原作制作；ASCII职责待核及关联位置保留。KOEI与KDE其余逐作开发不从发行推定。下一家Laplacian。

2026-10-25 L1核查L组前5／12，独立记录见 `entity-creator-l1-review-20261025.json` 与同名Markdown。Laplacian按原时期刊物、品牌负责人开发回顾及两部新作明确制作规格追加五条制作品牌；历史与现行公司分开，OneRoom销售和白昼梦后发版不外推。Leaf既有13条制作品牌沿用；raw Legend独立订正为历史公司类别，与英国专题及美国公司保持分设，其余职责待核。下一家Leland。

2026-10-25 L2连续核查Leland、Liar-soft、LJN、LOGIN SOFT、LOGiN，独立记录为 `entity-creator-l2-review-20261025.json` 与同名Markdown。Leland原版传单和LJN原版手册分别订正历史公司类别；LOGIN SOFT依具名品牌史料订正为品牌，显式保持旧发行角色，不自动生成其他发行职责。Liar-soft既有原作制作沿用，LOGiN刊物与游戏发行主体的对应继续待核。无新增制作或关系；L累计10／12，下一家LucasArts。

2026-10-25 L3完成L组12／12，独立审核为 `entity-creator-l3-review-20261025.json` 与同名Markdown。原版目录确认LucasArts历史公司，社团官网确认LunaSystem制作团队；按具名创作史、开发人员访谈及明确STAFF制作分别给三部LucasArts原作、四部旅行部原作追加七条原作制作。后发重制、补丁、合作展示与NanaWind专题待核不继承；既有目录、发行、关系和迁移基线保持。下一家Macadamia Soft。

2026-10-25 M1核查Macadamia Soft至Makura前五项，独立记录为 `entity-creator-m1-review-20261025.json` 与同名Markdown。Magical Zoo据保存协会品牌／部门及制作史订正为品牌，显式保留原publisher，并给The Screamer追加制作品牌；MAGES.据2014原作制作人发布会记录给CHAOS;CHILD追加原作制作，2019 Steam开发证据另限定。Madosoft与枕既有制作沿用，Macadamia具体制作待核；ASCII专题待核及关联位置不改。M累计5／30，下一家MangaGamer。

2026-10-25 M2连续核查MangaGamer至松下电器／Panasoft复合名义，独立审核为 `entity-creator-m2-review-20261025.json` 与同名Markdown。Marvelous及Marvelous Interactive各订正公司类别，现行页的回溯改名不改历史发行；Masaya依2014当事方品牌转让公告订正品牌，显式保留publisher。无新增制作／本地化；MangaGamer既有身份沿用，复合名义继续待核，不与下一项松下电器节点合并。M累计10／30。

2026-10-25 M3核查松下电器至Micro Cabin，独立审核为 `entity-creator-m3-review-20261025.json` 与同名Markdown。松下电器和MediaWorks各订正历史公司类别；官网原作开发行支持Micro Cabin 23条原作制作及4条联合制作，松下电器两条合作、Rogue早期复合作者一条合作另限定。后发移植、年份异文和复合个体身份不自动解决；Melbourne House出版／Beam制作继续分开。书目位置与ASCII职责待核保持，M累计15／30，下一项Microsoft。

2026-10-25 M4连续核查Microsoft至Minato Carnival，独立审核为 `entity-creator-m4-review-20261025.json` 与同名Markdown。三个微软公司／品牌节点沿用，逐作发行不推开发；World目录外项目不自动准入。以官方索引可取得的逐作具名制作说明给Minato Carnival三作追加制作品牌，正文不可达与两个FD制作范围另记，父品牌／公司专题待核保持。无身份、关系、原始发行或位置变更，M累计20／30，下一项Minato Soft。

2026-10-25 M5核查Minato Soft至mirai works，独立记录为 `entity-creator-m5-review-20261025.json` 与同名Markdown。官方历史品牌介绍支持Minato Station订正品牌并保留旧publisher；逐作具名资料限定追加Minato Soft四条、mirai宿星三条制作品牌。2011再版证据不冒充2007首版材料，合集、短篇与后发移植另核；minori既有19条制作沿用。官网正文不可达的索引证据范围明确保留，mirai works身份及父公司职责仍待核；M累计25／30，下一项Mixx Entertainment。

2026-10-25 M6完成M组30／30，独立审核为 `entity-creator-m6-review-20261025.json` 与同名Markdown。Mixx Entertainment与Mosaic Publishing Ltd各订正公司类别，原Ltd与专题节点不合并；月星組たまきゅう按官方具名STAFF追加一条制作品牌，父级职责待核保留。萌えAPP服务与公司混合原文继续待核，Mosaic出版与外部开发分开；登记／原手册索引可达范围另记，不改旧发行、位置、关系或基线。下一项NanaWind。

2026-10-25 N1开始N组，独立记录为 `entity-creator-n1-review-20261025.json` 与同名Markdown。逐作具名文本及STAFF原图支持NanaWind十条制作品牌，LunaSystem旅行部四篇及专题待核不继承；Natsume、NEC Avenue和英文NEC Interchannel各订正公司类别。当前改名、当事方持权公告与原厂手册分别限定身份，NEC-HE发行／出资不推制作，日文NEC Interchannel下一项另核；不改原目录、发行、位置、关系或基线。N累计5／21。

2026-10-25 N2连续核查日文NEC Interchannel至英文Nihon Falcom，独立记录为 `entity-creator-n2-review-20261025.json` 与同名Markdown。原厂手册与官方具名资料支持NEC、Neverland及历史Falcom三个公司类别；Nitroplus发售公告及Falcom IR开发陈述各支持一条原作制作。NetEase Games部门分类继续待核，NekoNyan本地化、Neverland后发Saturn开发与原作范围分开；专题待核、旧发行、节点关系、目录及基线保持。N累计10／21，下一项Falcom沿革专题。

2026-10-25 N3连续核查Falcom沿革至NIS America，独立记录为 `entity-creator-n3-review-20261025.json` 与同名Markdown。Falcom新旧法人不合并，仅按原开发公告补两条历史原作制作；NineLives、两个任天堂旧节点及NIS America分别订正公司类别。任天堂具名制作人资料支持BOND共同原作制作及两部Square合作原作联合制作；NineLives个人履历、NIS后发出版不推开发。仅Romancia自身专题分组更新，其他待核和全部位置／发行／基线保持，N累计15／21，下一项NITRO CHiRAL。

2026-10-25 N4连续核查NITRO CHiRAL至novamicus，独立记录为 `entity-creator-n4-review-20261025.json` 与同名Markdown。按官方具名资料新增CHiRAL节奏游戏一条制作品牌、公司Rusty Rabbit一条共同原作制作、旧Nitroplus十作制作品牌；仅公司Rusty一条自身专题待核解除。ORIGIN为2021新品牌，不承接早期原作；novamicus订正品牌并显式保持旧publisher，ONE.2023内容不倒填1998。其余子品牌／父公司待核、位置、旧发行、关系和基线保持，N累计20／21，下一项NOVECT。

2026-10-25 N5核查NOVECT，独立记录为 `entity-creator-n5-review-20261025.json` 与同名Markdown。逐作官网STAFF、企划说明及两部原包制作栏支持九条原作制作；保留旧团队身份、Novectacle原署名、外部参与与后发移植边界。九条自身专题关联增加制作角色并转original，原publisher及位置保持；第一次投票年份差异另列待核，不改历史日期。N累计21／21，A—N累计214／214，下一项Origin Systems。

2026-10-25 O1按Origin Systems、OTAKU Plan、OVERDRIVE、Overflow顺序完成O组四项，记录为 `entity-creator-o1-review-20261025.json` 与同名Markdown。原厂手册确认Origin公司与一条原作制作；OTAKU Plan按自述仅记本地化发行团队；OVERDRIVE九作补制作品牌，GROOVER原作范围保持；Overflow仅订正品牌并保留publisher，首发间接来源及2005制作另列待核。三项身份、十条职责，九条自身专题分组更新，全部旧目录／日期／位置／关系与基线保持。O累计4／4，A—O累计218／218，下一项Palette（ぱれっと）。

2026-10-25 P1按Palette、Philips Interactive Media、PIACCI、Pioneer LDC、英文Pony Canyon顺序核查，记录为 `entity-creator-p1-review-20261025.json` 与同名Markdown。十八条既有品牌制作保持，蜂蜜庄仅补一条related制作品牌；四个旧发行节点按具名主体资料订正公司，不从发行推开发，不合并近似法人。来源缓存与直连维护／403／404的区别明确记录，全部原日期、内容／发行、位置、关系和基线保持。P累计5／13，A—P累计223／231，下一项日文显示名Pony Canyon。

2026-10-25 P2连续核查日文显示名Pony Canyon至Psionic，记录为 `entity-creator-p2-review-20261025.json` 与同名Markdown。具名公司资料、同期品牌报道和作者第一方主页支持公司／品牌／个人三项身份订正，仅追加Ghostscape一条原作制作。pride缺原始制作资料，PROTOTYPE整体移植业务不批量推逐版开发，两者原职责保持；全部专题、旧发行、日期、位置、关系和基线保持。P累计10／13，A—P累计228／231，下一项PSK。

P2同时允许独立身份订正将动态解析的unknown节点核为既有模型中的individual类别，仍要求原署名、订正前状态、具名来源和说明全部匹配；本批仅命中Psionic。不改变历史发行角色或其他主体的归类规则。

2026-10-25 P字母第三批使用 `entity-creator-p3-review-20261025.json` 与同名Markdown，按PSK、Purple software、Purple（JAST期）完成P组13／13。现行Purple software仅确认品牌身份并保留publisher；PSK的ザ・病院与旧Purple的かすみ遊戯各按当事方明确开发说明补一条原作职责，现行品牌、历史品牌、母公司和后发DVDPG职责分开。其他逐作STAFF和沿革继续待核，作品／内容／发行、关系与基线不改；下一项Quest（クエスト）。

2026-10-25 Q字母首批使用 `entity-creator-q1-review-20261025.json` 与同名Markdown，完成Quest一项（Q组1／1）。收购方财报与ARTDINK官方页确认历史公司身份，原开发者访谈支持两条限定SFC原作制作；两部作品保持Riverhill关联目录位置，后发移植、增补与人员移籍不向原公司倒填职责。全部专题关联、关系及基线保持；下一项Rainbird。

2026-10-25 R字母首批使用 `entity-creator-r1-review-20261025.json` 与同名Markdown，按Rainbird、RED FLAG SHIP、RIGHTWAY连续核查3／5。同期出版行与访谈支持Rainbird出版品牌类别并显式保留publisher，政府法人资料及公司官网各确认后两项公司身份；全部职责和专题关联逐条保持，制作与经营沿革缺口具名待核。下一项Riverhill Soft（リバーヒルソフト）。

2026-10-25 R字母第二批使用 `entity-creator-r2-review-20261025.json` 与同名Markdown，完成Riverhill Soft、Russell，R累计5／5。创始人分期履历与当事开发访谈支持Riverhill十部既有原作制作，其中一部仍保留related；Russell只确认公司身份，PSP发行与ゆずソフト追加内容制作分开。两条指定专题待核解除，其他历史发行、身份关系与基线保持；下一项SAGA PLANETS。

2026-10-25 S字母首批使用 `entity-creator-s1-review-20261025.json` 与同名Markdown，核查SAGA PLANETS、Screaming Villains、SEGA（3／42）。追加SAGA两条关联制作品牌、SEGA两条关联原作制作；确认Screaming Villains公司身份并将2017周年版developer限定于既有增补内容g934-c-2。独立审核入口允许content／developer，必须验证确切目标、所属作品、added性质及目标旧职责，不允许直接解除指定专题待核。原作发行不继承增补内容开发，收录位置、历史发行及基线保持；下一项Seikaisha（星海社）。

2026-10-25 S字母第二批使用 `entity-creator-s2-review-20261025.json` 与同名Markdown，连续核查Seikaisha、Sekai Project、Serenity Forge、Shall Luck，S累计7／42。确认星海社及Shall Luck公司身份，只追加星海社一条原作制作和Serenity Forge一条限定g056-c-3的Plus增补内容开发。联合企画／開発不拆成独占技术分工；2017原版及2025内容未核的移动版不继承Plus开发，Sekai Project本地化及Shall Luck的GBA技术职责另核。原始发行、专题引用、关系和基线保持；下一项SharRock。

2026-10-26 S字母第三批使用 `entity-creator-s3-review-20261026.json` 与同名Markdown，连续核查SharRock、Shiravune、小学馆Production与小学馆，S累计11／42。确认小学馆公司身份，官方具名DEVELOPER只给Shiravune的2022同级生发行g046-v3追加developer；不反写原作、2021重制或共有内容ID。独立审核入口允许release／developer，核对同作品目标发行、原职责并禁止专题捷径。SharRock品牌与Shall Luck、ShoPro制片与外部技术制作分别保留；其余缺口、旧发行、专题、关系和基线保持。下一项Sierra On-Line。

2026-10-26 S字母第四批使用 `entity-creator-s4-review-20261026.json` 与同名Markdown，连续核查Sierra On-Line、Silky’s、Silky’s Plus、A5和牛，S累计15／42。原手册索引及创办人逐作回顾支持三条Sierra原作制作；官方开发座谈与品牌规格索引交叉支持A5和牛本篇一条制作品牌。转载传记、全文不可达及验证页明确区分；不从发行或版权补开发，不把子品牌制作上推父专题。身份、旧发行、位置与基线保持，下一项Silky’s Plus Alpha。

2026-10-26 S字母第五批使用 `entity-creator-s5-review-20261026.json` 与同名Markdown，连续核查Alpha、DOLCE、WASABI、Simon & Schuster Interactive，S累计19／42。官方具名团队定位与制作自述分别支持DOLCE言の葉、WASABIなないろ两条制作品牌；原手册及SEC材料支持Simon历史软件出版部门名义，以brand承载并显式保留publisher。Alpha旧发行与当前Sony列RED FLAGSHIP差异独立待核，不合并实体、不改原档案。父专题、旧发行、关系和基线保持，下一项Sinclair Research。

2026-10-26 S字母第六批使用 `entity-creator-s6-review-20261026.json` 与同名Markdown，连续核查Sinclair Research、Sir-tech Software、SMEE、SNK，S累计23／42。原Sir-tech手册实物署名及SNK官方分期历史分别确认两项历史公司类别；SNK旧公司与2001后起公司／品牌承继分开，不倒填日期或法律关系。Sinclair出版不推开发，SMEE25条既有制作沿用；全部4986条职责、专题、原始发行、位置和基线保持。下一项Sol Press。


## S组第七批身份核查（2026-10-26）

Sol Press及两条Sony Computer Entertainment原文独立订正为历史公司，Sony节点不合并、现名与日期不倒填。SORAHANE三条既有制作品牌保留，官网访问失败注明；Sphere四部官方编号产品复核不重复加职责。全部4986条职责与原作品／内容／发行保持，S进度28／42，下一项Spike。详见[独立审计](entity-creator-s7-review-20261026.md)。


## S组第八批身份与制作核查（2026-10-26）

历史Spike与日本Spinnaker分别订正company。官方原作目录、开发声明及社内访谈支持Spike的g035、Spike Chunsoft的g160和g161三条originalProduction；g171官方明确Chime开发，旧发行保留。sprite五条既有制作品牌不重复追加，2026-11-26预告不提前准入。全部旧职责、专题、内容／发行、关系和基线保持；S进度32／42，下一项Square Enix。详见[独立审计](entity-creator-s8-review-20261026.md)。


## S组第九批历史主体与原作创作（2026-10-26）

Square Enix日文署名及美国Square Soft独立核为company，2008前后同名公司时期保留缺口，不倒填日期或合并节点。美国开发者亲述与手册转录支持Evermore一条制作；官方加藤简介支持日本Square四作原作创作参与，原发行不推开发。四项Square专题由发行组显示为原作组，Evermore父专题仍待核，内容和收录位置保持。S进度36／42，下一项StarCraft。详见[独立审计](entity-creator-s9-review-20261026.md)。


## S组第十批历史公司与联合发行边界（2026-10-26）

StarCraft、Sumzap、Sunnyside Soft依原厂手册／公司概要分别核定company；Sunflower Ocean仅确认联合发行，保留unknown。具名上线公告与原期刊开发说明支持Sumzap一部、Sunnyside两部原作制作，产品线收购不建法人合并关系，三个父专题引用仍pendingRole。原作品、内容、发行及年代保持，S进度40／42，下一项Syawase Works China。详见[独立审计](entity-creator-s10-review-20261026.md)。


## S组收尾与发行层本地化（2026-10-26）

S11完成Syawase Works China、Synergy Inc.两项登记，S为42／42，下一项T&E SOFT。两项身份缺口保留，仅按官网2020中文版制作说明与原片尾转录分别追加g855-v3发行层localizer、黄砖路原作制作。独立审核入口的release允许developer或localizer，仍须同作品、具体发行ID、原角色与无专题捷径；本地化不计原作开发，不沿共享内容ID外溢。全部原始数据、实体、专题和基线保持，详见[独立审计](entity-creator-s11-review-20261026.md)。

2026-10-26 T字母首批使用 `entity-creator-t1-review-20261026.json` 与同名Markdown，连续核查T&E SOFT、Tactics（NEXTON）、TAITO、TAKERU，T累计4／19。NEXTON与Brother原站支持两项brand身份，TAKERU明确是软件销售服务；两项均保留旧publisher且不自动生成发行／制作品牌职责。T&E与TAITO逐作开发证据不足的范围单列待核，本批无新增职责、无专题解除。累计当前A—T队列登记283／298，下一项TamaMako gaming。

2026-10-26 T字母第二批使用 `entity-creator-t2-review-20261026.json` 与同名Markdown，连续核查TamaMako gaming、Team Salvato、Tiare、TikGames，T累计8／19。核定Team Salvato制作团队、TikGames公司身份，分别追加DDLC原作制作／既有Plus增补开发与Interpol原作制作三条职责，Serenity Forge协作保留。TamaMako联合发行不推本地化或开发，Tiare既有品牌不向JAST父专题上推制作；当前A—T队列登记287／298，下一项TinMachine。

2026-10-26 T字母第三批使用 `entity-creator-t3-review-20261026.json` 与同名Markdown，连续核查TinMachine、TOHO Games、TOHO、Tokuma Shoten Intermedia，T累计12／19。核定游戏品牌与历史出版公司两项身份；首发公告支持东宝参与Phantom Parade游戏企画制作，只追加一条原作制作并核对自身专题旧值后解除该作待核，Sumzap开发独立保持。TinMachine配信不推开发，品牌身份不自动产生职责；当前A—T队列登记291／298，下一项Tokuma Shoten（徳間書店）。

2026-10-26 T字母第四批使用 `entity-creator-t4-review-20261026.json` 与同名Markdown，连续核查Tokuma Shoten、Tokyo Shoseki、TOKYOTOON、tone work’s，T累计16／19。核定Tokyo Shoseki与TOKYOTOON公司身份；只给TOKYOTOON两条2019 Steam发行追加developer，2018公司成立不倒填2016／2017原作，未知内容关联保持。德间母子主体及tone work’s六条制作品牌沿用，不重复加角色或解除专题待核；当前A—T队列登记295／298，下一项Tonkin House（トンキンハウス）。

2026-10-26 T字母第五批使用 `entity-creator-t5-review-20261026.json` 与同名Markdown，按Tonkin House、Toshiba EMI、TYPE-MOON连续收尾，T累计19／19，当前A—T队列登记298／298。品牌／历史公司三项身份分别核定；TYPE-MOON四部既有商业作品仅追加制作品牌，旧同人月姬与2021作品不合并，发行和后发开发保持独立。Tonkin类别依据及原件不可读限制明确登记，不推YsIV开发；专题职责待核保留。下一项Ultra Games。

2026-10-26 U字母首批使用 `entity-creator-u1-review-20261026.json` 与同名Markdown，按Ultra Games、Union Planning连续核查并收尾，U累计2／2，当前A—U队列登记300／300。原Nightshade说明书区分商标与Ultra Software Corporation，具体1984馆藏著录确认Union历史公司，排除2007室内设计同名公司；身份核定不自动新增开发或发行品牌角色，全部旧职责与专题引用保留。下一项Virgin Games Ltd。

2026-10-26 V字母首批使用 `entity-creator-v1-review-20261026.json` 与同名Markdown，按Virgin Games Ltd、VISUAL ARTS连续核查并收尾，V累计2／2，当前A—V队列登记302／302。原说明书及同期广告具名Virgin Games Ltd出版销售公司，区别Mosaic制作与Level 9程序；VISUAL ARTS官方公司概要与沿革核既有公司身份及Key品牌分层。仅订正Virgin身份，不据公司与品牌归属自动增加创作、开发或新版发行；全部原职责、专题及旧发行保留。下一项WFS（WRIGHT FLYER STUDIOS）。

2026-10-26 W字母首批使用 `entity-creator-w1-review-20261026.json` 与同名Markdown，按WFS、Whale、WhisperGames、Wolf Team、WRIGHT FLYER STUDIOS连续完成W累计5／5，当前A—W队列登记307／307。官方更名、品牌公告与具体馆藏支持WFS／Wolf历史公司及两项发行品牌身份；Whale既有品牌不变。第一方HBR制作行与Steam开发行仅支持WRIGHT品牌一条相关作品制作品牌和一条PC发行开发，未核内容关系与原发行保留；旧专题待核不跨品牌继承。下一项Xbox Game Studios。
