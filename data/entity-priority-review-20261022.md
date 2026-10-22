# visual-novel 首批主体与专题职责核查建议

核查日期：2026-10-22（北京时间）。本文件保存首批16项的独立证据与原始审查建议。A1—A6已按下述限定范围实施，B1—B8与C1—C2继续待核。

## 1. 审查基准与结论

本次读取的 main 为 [f146070527470017120c08973ada0fca398c00ee](https://github.com/wt1234-donkey/visual-novel/commit/f146070527470017120c08973ada0fca398c00ee)，包含关系重构 [PR #48](https://github.com/wt1234-donkey/visual-novel/pull/48) 及名称格式调整 PR #49。不是仅按10月21日审计摘要推断当前数据。

实际读取 entities.json、credits.json、entity-migration-review.json 后复核：326个实体、4743条参与记录、2234条专题引用，199个待核身份、620条 pendingRole 专题引用。已读 AGENTS.md、entity-model.md、build_entity_model.py、审计记录、相关原始作品／平台发行数据、实体生成页及相关专题卡片。

首批选16个核查单元，分类为：**可直接确认6项、需要补充来源8项、暂不宜判断2项**。一项可能覆盖两个关联主体或作品，不等于16个待核身份，也不等于16条专题引用。分类针对下文指定的结论；同一对象的发行职责可已确认，而其法人身份或开发职责仍待核。

优先理由：
- 高频身份：Spike Chunsoft覆盖31条发行／14部档案；MangaGamer覆盖24条／18部；JAST覆盖11条／11部；Shiravune覆盖7条／7部。以上是当前索引的不同发行ID和作品ID计数，不代表已逐条重新核定。
- 明显可补的职责：Key《绯染天空》、AUGUST《爱丽丝秘迹》、Minato Soft《结城友奈》PC特典与《Climax》，现有正文或官方资料已能支撑限定职责，但未转入参与索引。
- 最易误归的边界：多公司复合署名、公司与品牌同名、父品牌与子品牌、个人编剧与品牌制作、平台与实际发行者。
- 数量最大的待核专题包括 Alicesoft 75条、Nitroplus 73条。它们不是可批量补成“开发”的队列，因此先取具名案例核查。

## 2. 文件维护入口

实施说明：本批独立核定输入为 `data/entity-priority-review-20261022.json`。生成器只消费其中2项 `identityCorrections` 与4项 `creditAdditions`；10项 `deferredReviews` 仅保存缺口，不执行职责或身份推断。下文“最小修正／应改文件”保留审查时的逐项方案；实际执行范围仅A1—A6。

所有落地修改都应先增加独立证据记录，建议新建：
- `data/entity-priority-review-20261022.md`：逐项结论、原值、证据、缺口与适用范围。
- 如需要机器读取，再新增独立审核配置；当前仓库还没有这种通用订正配置，不应声称已有接口。

当前人工身份／职责规则的实际入口是 **`scripts/build_entity_model.py`**，不是生成JSON或HTML：
- 身份修正应按稳定 entityId 增加具名覆盖规则，保留旧ID、别名和 rawCredit；不能为改类型重新哈希或合并对象。
- 新职责使用既有 credit()、既有角色与 targetType；作品层／内容层／发行层按证据分别指定。
- entities.json、credits.json、entity-migration-review.json、entity-catalogue.json、entity-credits.csv、entities.html及专题HTML均由生成流程同步。
- 所有下列“应改文件”均是建议，不表示本次已修改。

## 3. 可直接确认：6项

### A1. Spike Chunsoft：可确认公司身份

**定位**：`entity-name-8a871cf93bfd`；当前 unknown／unresolved，主体页列发行署名14部，当前索引31条发行。

**证据**：
- [官方公司页](https://www.spike-chunsoft.co.jp/company/)明确公司身份。
- [官方沿革](https://www.spike-chunsoft.co.jp/company/outline/)明确2012年4月Spike与Chunsoft合并为株式会社スパイク・チュンソフト。
- 既有主体来源是[Zero Escape官方作品页](https://www.spike-chunsoft.co.jp/pages/zeroescape/doublepack/)，原索引的角色仍仅为 publisher。

**最小修正**：保持该ID，仅将 type 改为 company，verification 改为 sourceReviewed，追加公司／沿革来源和时间范围说明。现存 `entity-name-6d5cd9b9dc38`（Spike）与 `entity-name-21365baf366d`（Chunsoft）继续独立，不增加前身归并，也不把31条发行转成开发。日本公司与海外主体不凭英文名合并。

**证据缺口**：逐条历史发行合同、海外发行主体与开发分工本轮未重验，不阻碍这个限定的身份结论。

**应改文件**：新增独立审核记录；build_entity_model.py 的稳定ID身份覆盖及待核列表生成；派生 entities.json、entity-migration-review.json、entity-catalogue.json、entities.html 等。没有独立Spike专题可直接手工改页。

### A2. Shiravune：可确认本地化团队身份

**定位**：`entity-name-5caee77c6090`，当前 unknown／unresolved；7条发行／7部。

**证据**：[官方About](https://shiravune.com/about)自称东京本地化团队，负责把日本游戏带给英语和中文读者。现有主体源链接 `https://shiravune.com/archives/2502` 是单作资料，不能独自证明法人。

**最小修正**：保留ID，将 type 从 unknown 改为 team；verification 为 sourceReviewed；只确认“本地化团队”的身份。7条 publisher 记录继续保存，不因团队整体介绍而给7作批量新增 localizer 或 developer。

**证据缺口**：EXNOA法人归属、各时期运营关系和逐作本地化分工仍需另证。本次不新增 operatedBy 关系，不将团队直接改成独立法人。

**应改文件**：独立审核记录、build_entity_model.py；派生 entities.json、entity-migration-review.json、entity-catalogue.json、entities.html及引用此主体的页面。

### A3. 《绯染天空》：Key合作企划／制作可确认

**定位**：`key-rpg-hbr`；key专题为 related、pendingRole。平台发行原文：
- `key-rpg-hbr-v1/v2`：WFS（WRIGHT FLYER STUDIOS）。
- `key-rpg-hbr-v3`：WRIGHT FLYER STUDIOS。
- 两个待核ID分别为 `entity-name-a7663faeee46`、`entity-name-9e9cc680be5a`。

**证据**：[WFS 2022首发公告](https://www.wfs.games/news/20220210_01.html)明确Wright Flyer Studios与Key合作；[2024官方公告](https://www.wfs.games/news/20240717_01.html)标题明确合作企划制作，正文分别说明株式会社WFS与其品牌Wright Flyer Studios。2024页亦保存开发署名，证明公司与品牌不能简单当作一个同义名。

**最小修正**：只向 `entity-key` 增加 work／`key-rpg-hbr`／coDeveloper，note明确“合作企划与制作，不断言Key独自承担系统程序”；sourceReviewed。key专题改 cooperation。保留related位置及全部发行原文、内容关系。

**证据缺口**：两个WFS相关旧ID分别对应怎样的历史署名对象，需要另案拆解。此处不合并ID，不给复合署名强行标公司，也不追补未收录的国际版平台记录。

**应改文件**：独立审核记录；build_entity_model.py具名作品职责；派生credits.json的key成员、key.html、entity-catalogue.json、entity-credits.csv、entities.html等。company-coverage.json不必改。

### A4. 《爱丽丝秘迹》：AUGUST创作合作可确认

**定位**：`august-rpg-imys`；august专题 related／pendingRole。两条发行原文均为 DMM GAMES／AUGUST，对应待核复合ID `entity-name-16c097f224f4`。

**证据**：
- [AUGUST官方年表与访谈](https://august-soft.com/20th/history/)明确作品及与DMM的系统分工，原画与剧本创作由AUGUST方面叙述。
- [发行方填写的Google Play介绍](https://play.google.com/store/apps/details?hl=ja&id=com.dmm.games.irismysteria)明确世界观、剧本、角色制作由AUGUST负责，开发／运营由DMM GAMES负责。
- 年表区分2017首发、2018重新开放与2019正式服务／移动版，不能以现行商店说明反推各阶段合同法人。

**最小修正**：为 `entity-august` 新增 work／`august-rpg-imys`／coDeveloper，note限世界观、剧本与角色创作、注明系统开发／运营另有主体；august成员改cooperation。复合发行ID继续保留，不能直接把整串 type 改为company或将其当开发商。

**证据缺口**：DMM GAMES各时期法人、运营与发行责任仍需时期证据。此项只解除AUGUST合作职责的待核。

**应改文件**：独立审核记录、build_entity_model.py；派生credits.json、august.html、实体索引和CSV。保留company-coverage.json内旧发行字段和原内容身份。

### A5. 《结城友奈是勇者》PC特典：Minato Soft制作可确认

**定位**：`g1251`，2014原作；minatosoft与hawkeye两个专题均pendingRole。唯一既有发行 `g1251-v-original` 原文ポニーキャニオン。

**证据**：[动画官方第1卷商品页](https://yuyuyu.tv/season1/bddvd/bddvd_01.php)明确“企画タカヒロ、制作みなとそふと”，且区分游戏图像由Studio五组绘制、两人共同编剧；同页“発売元ポニーキャニオン”属于BD/DVD商品语境。

**最小修正**：为 `entity-minatosoft` 增加 work／g1251／originalProduction，note明确2014 PC特典的制作，minatosoft成员改original。保留Pony Canyon发行原文和附赠上下文，不将其解释为游戏开发；不把Minato品牌制作自动上推为Hawk Eye公司开发。

**证据缺口**：hawkeye→g1251的具体合同／制作职责仍待核；本项不解除hawkeye的pendingRole。续作S、A需分别读各卷来源，不能本次自动推广。

**应改文件**：独立审核记录、build_entity_model.py；派生credits.json、minatosoft.html、实体检索／CSV；hawkeye页面若共享卡片展示会同步显示新品牌职责，但其自身专题成员仍待核。

### A6. 《为我的女王献上荣冠：Climax》：监修可确认

**定位**：`minatosoft-climax`；minatosoft专题 related／pendingRole；发行原文EXNOA（DMM GAMES），对应 `entity-name-5f2bf730e86e`。

**证据**：[既有EXNOA公告](https://dmmgames.co.jp/news/detail/id=1562)读取中存在旧路径重定向不稳定；补用[EXNOA在PR TIMES发布的2023-06-20公告](https://prtimes.jp/main/html/rd/p/000004169.000032953.html)，明确Minato Soft监修新剧本以及新增角色设定、插画。

**最小修正**：为 `entity-minatosoft` 增加 work／`minatosoft-climax`／supervisor，note限上述监修；成员改licensed。保留related位置，不能写成开发，也不能因版权署名增加原作制作。

**证据缺口**：系统开发方、监修合同与所有后续章节范围未核；本次也不拆EXNOA／DMM复合身份。

**应改文件**：独立审核记录、build_entity_model.py；派生credits.json、minatosoft.html及索引CSV。仅新增可靠补充来源，不覆盖原链接或改动历史平台。

## 4. 需要补充来源：8项

### B1. MangaGamer：发行职责明确，法人／品牌／业务名义未定

**定位**：`entity-name-85a1fd56da66`；24条发行、18部；现为unknown。

**已读证据**：[官方博客About](https://blog.mangagamer.org/about/)说明其英语引进业务；[《海市蜃楼之馆》Steam页](https://store.steampowered.com/app/303310/The_House_in_Fata_Morgana/)将NOVECT列开发、MangaGamer列发行。官网about.php本轮403，不能声称已读到其法律运营说明。

**缺口**：法律运营实体名称、MangaGamer是品牌还是公司／团队、历史时期是否一致；一部商店页也不能确认24条发行均承担翻译。

**最小修正**：保留unknown／unresolved和publisher；追加“发行名义明确，法人／品牌类型待核”的审核说明与已读来源。逐作需要localizer时补该作本地化署名。不能为了消除unknown直接标公司。

**应改文件**：本轮仅独立审核记录；若上线提示，在build_entity_model.py为该ID增加具名historyNote／sources，重生成entities.json、entities.html及相关专题卡片。不要编辑核心games.json或批量增加职责。

### B2. JAST：先解决同名风险，保留三个对象

**定位**：`entity-name-251c0991e4f6`（JAST，11条发行）、`entity-name-8e61b50010ed`（JAST USA）与 `entity-jast`（日本旧JAST专题）。

**已读证据**：[Flowers Steam页](https://store.steampowered.com/app/452440/)明确Innocent Grey开发、JAST发行，页尾同时保留JAST USA版权署名；[国际JAST自述](https://jast.games/about)支持其发行业务。当前页面创办年份文字与页尾年份并不完全一致，不据此登记成立年份。

**缺口**：旧发行时的法律名称、品牌更名／连续性公告、11条记录各自的历史证据。当前Steam署名可能更新，不能等同于2016年包装的原文。

**最小修正**：三个ID继续独立；为这条国际发行名义追加同名消歧说明，并登记JAST／JAST USA在特定商店页同现的证据。当前范围内不合并ID、不把国际发行归入日本旧JAST专题，也不增加全库别名。

**应改文件**：独立审核记录；需要展示时在build_entity_model.py增加具名说明，派生entities.html、innocent_grey.html／nitroplus.html等引用卡片。未来若订正单条核心发行，另行履行基线订正，不直接替换publisher。

### B3. Legend／英国Legend：逐作对应有证据，尚不做全局合并

**定位**：`entity-name-7482e374b5bd`与 `entity-legend_uk`；g114-v1/v2及legend-uk-great-space-race-v-original，共3条发行／2部；legend_uk两条专题成员待核。

**已读证据**：legend_uk.html、data/legend-uk-audit.md；[WoS英国目录](https://worldofspectrum.net/publisher/8363/)把Valhalla和The Great Space Race归于Legend UK；[1984 CRASH同期采访](https://www.crashonline.org.uk/08/news.htm)明确Microl改称Legend，并讨论两作。这支持具名作品的英国发行语境，不能据字符串“Legend”合并美国Legend Entertainment。

**缺口**：ZX与C64各包装／手册的原始署名、对象映射与历史法律连续性的审核。旧WoS .org原链接与现行.net目录应一起保存，不静默改写。

**最小修正**：先在审核记录标记“英国发行语境已支持，身份对应订正另案”；保留两个ID。若要先改善专题，允许按逐作原厂证据登记限定的发行关联，但不能由别名规则批量制造developer。

**应改文件**：独立审核记录；未来具名职责规则在build_entity_model.py；派生legend_uk.html、credits.json及实体页。不得通过重算基线或覆盖publisher来消除待核。

### B4. Mosaic Publishing Ltd／Mosaic Publishing：出版与开发需继续分开

**定位**：`entity-name-170eeb0b71f8`与 `entity-mosaic`；原署名命中g131-v1及g1200/g1201/g1202的首发，共4条发行。mosaic专题11条pendingRole中含6条书目，没有平台发行可供直接推导。

**已读证据**：mosaic.html、data/mosaic-audit.md及[历史目录](https://www.lysator.liu.se/adventure/Mosaic_Publishing.html)。现有主体说明已记录Level 9、Ram Jam等外部制作；g131原记录明确Level 9制作。既有审核保存原厂手册链接，但本轮未逐份重读所有扫描件。

**缺口**：Mosaic Ltd与专题对象的身份对应原证、每作原厂出版／开发职员表；g1203原版保留Virgin Games发行，更不能把专题成员一律写成Mosaic自开发或自发行。

**最小修正**：先登记4条旧发行署名与专题出版语境的候选对应；不合并ID、不以Ltd后缀直接改公司、不批量修改11个成员。先读g1200原厂手册出版页和g131原说明，再决定逐条publisher关联；开发归属另证。

**应改文件**：独立审核记录，必要时补data/mosaic-audit.md；后续具名规则在build_entity_model.py，派生mosaic.html及实体索引。games.json内旧g131及Virgin首发不动。

### B5. 两条多公司复合署名：参与者明确，品牌归属及开发分工未齐

**定位**：
- `minatosoft-hanayui`：KADOKAWA／オルトプラス／scopes；待核ID `entity-name-0f93dc471cd5`；两条首批平台记录。
- `minatosoft-spyce`：オルトプラス／KADOKAWA／トライフォート；待核ID `entity-name-bd36baf4b6a9`；两条首批平台记录。
- 二者在minatosoft专题均related／pendingRole。

**已读证据**：[AltPlus 2017公告](https://www.altplus.co.jp/topics/20170608)、[2019公告](https://www.altplus.co.jp/topics/20190212-m)、专题与data/minatosoft-source-review.json。两份官方公告确认联合发布主体，前者说明タカヒロ等原作人员参加编剧，后者说明タカヒロ编写并全面监修故事。

**缺口**：本轮已读的发布公告未找到逐公司开发分工，故旧notes中“AltPlus与scopes开发”不能视为本轮已重验；タカヒロ个人职责也不自动等于Minato Soft品牌职责。

**最小修正**：保留两条复合ID和原发行串；在审核中逐一列出“已确认参与者／已确认个人贡献／未确认品牌授权”。本次不把一串公司变成一个company、不自动拆成三个开发者、不新增品牌运营关系；minatosoft成员继续pendingRole。需要展示时只增加有来源的限定说明。

**应改文件**：独立审核记录；必要时增补data/minatosoft-source-review.json的审核说明；具名展示规则在build_entity_model.py，派生minatosoft.html、entities.html。若以后拆参与记录，另提独立审核且保留旧复合身份。

### B6. PARQUET：SOUR身份明确，父品牌直接职责不能自动上推

**定位**：g232；子品牌 `entity-yuzusoft_sour`已有发行与原作发行品牌记录；父专题yuzusoft的g232仍pendingRole。

**已读证据**：yuzusoft.html、原作发行g232-v1（ゆずソフトSOUR）；[官方提供的Google Play介绍](https://play.google.com/store/apps/details?hl=ja&id=com.yuzusoft.sour.parquet)明确SOUR为姐妹品牌及由Yuzusoft常规人员制作。原SOUR网站本轮读取超时，保留其既有链接，不说它不存在。

**缺口**：将“原班人员”对应到父品牌的精确制作署名、首发PC职员表；现行移动商店可支持品牌说明，却不能直接替代2021原作合同。

**最小修正**：保留SOUR独立ID和父子关系；为子品牌的制作品牌职责建立候选证据，父专题注明“SOUR作品／家族关联，父品牌直接职责未核”。不把g232改归主品牌PC本篇，也不为了消除pendingRole给entity-yuzusoft补developer。

**应改文件**：独立审核记录；必要时build_entity_model.py具名备注；派生yuzusoft.html及实体页。不要用entity-display-names.json完成身份合并。

### B7. 《咎狗之血》：CHiRAL制作品牌与公司专题分开核

**定位**：g622；entity-nitrochiral已有productionBrand／originalPublishingBrand；nitroplus专题主体为entity-nitroplus公司，因此该专题成员仍pendingRole。后续g622-v7的NITRO PLUS只是对应发行层品牌。

**已读证据**：nitroplus.html、[CHiRAL单作官方页](https://www.nitrochiral.com/game/togainu.php)、[Nitroplus公司页](https://www.nitroplus.co.jp/company/)。单作页明确CHiRAL首作，并保留Nitroplus／HOBIBOX版权原文；版权串不等于逐公司开发说明。

**缺口**：公司在2005原作的具体制作、发行／授权合同；版权中的同名Nitroplus究竟怎样对应现有公司／品牌ID也须按当年证据确定。

**最小修正**：将这条pendingRole的原因写清为“公司专题引用；CHiRAL品牌职责已知，公司直接职责未核”。保留CHiRAL独立制作品牌，继续保存g622-v7的发行层品牌，不上推为原作开发。

**应改文件**：独立审核记录；若公开展示，build_entity_model.py具名note／成员说明需由生成器输出，派生nitroplus.html与credits.json相关备注。不批量解除Nitroplus的73条待核。

### B8. 《王子殿下Lv1.5》：存在开发协力线索，应优先取回原始职员表

**定位**：g545；Alice Blue原作发行品牌、KID后续发行已存在；alicesoft专题成员pendingRole。

**已读证据**：alicesoft.html、原平台署名Alice Blue；[现有BLGame Wiki来源](https://wikiwiki.jp/blgame/王子さまLv1.5)的职员表转录明确记Alice Blue企划和调试、Alicesoft开发协力，并另列音乐人员。这里存在比“旗下品牌”更具体的贡献线索。

**缺口**：原游戏职员表／手册或官方存档；转录准确性、开发协力范围及是否适用于PC原作而非PS版。本轮不能把转录来源称为原厂文件。

**最小修正**：先登记“开发协力候选”及转录字段，保留pendingRole。取得原证后，仅新增entity-alicesoft在g545原作范围的coDeveloper，note保留“开发协力”，不写成独立原作制作；Alice Blue及KID记录继续独立，PS版另核。

**应改文件**：独立审核记录，可补data/alicesoft-audit.md；后续build_entity_model.py具名职责，派生alicesoft.html、credits.json及索引。不能批量把Alice Blue全部作品视为Alicesoft自开发。

## 5. 暂不宜判断：2项

### C1. Mobage／GREE：平台名不能替代实际发行主体

**定位**：g209《任性High Spec》的g209-v2／v3，原文分别为“发行方待核实（Mobage）”“发行方待核实（GREE）”；对应 `entity-name-d1903e2fafb1`、`entity-name-e1232b52eff7`。两条内容关联均unverified、contentVersionId为null。

**已读证据**：madosoft.html及games.json的发行原文、差异说明；[原公告](https://madosoft.net/news/303)本轮无法读取。数据库保留的是公告发布与平台线索，不是已确认服务提供商。

**缺口**：2016服务页面、原始运营者／販売業者、版权及服务条款、准确上线日与内容差异。

**最小修正**：只在审核记录明确两个ID是待核占位，不是已核实法人；两条发行继续保留、不更名成DeNA或GREE、不推移植开发者、不补内容版本。源页面读不到不是反证。

**应改文件**：本轮仅新增独立审核记录；若改善公众提示，在build_entity_model.py给两个ID加占位说明，派生entities.html、madosoft.html；games.json及publisherCompanies保持原值。

### C2. 1988《初学餐桌礼仪》：目录署名与品牌启用时间冲突

**定位**：g594／g594-v1；待核ID `entity-name-de3ed19ac095`；alicesoft及champion_soft两个成员均pendingRole。

**已读证据**：champion_soft.html、原发行备注；[1988年10月PC-88目录](https://www.gamepres.org/pc88/library/1988/1988_10.html#table)及现有审计保留其アリスソフト署名与1989品牌启用的冲突。日期冲突本身不能决定哪条记录错误。

**缺口**：原包装、说明书、启动／版权画面、同期广告；需判断目录是否后世归类、日期误录或存在其他发行名义。

**最小修正**：继续“前身历史关联／具体发行待核”；不回填Alicesoft、Champion Soft，不因品牌晚启用而将作品年份改成1989；两专题位置、主库身份和唯一内容版本均保持。

**应改文件**：仅独立审核记录；新增资料后另开历史事实订正，才考虑games.json对应字段与基线审核。entity-migration-baseline.json不能直接重算或删除断言。

## 6. 建议实施顺序与可复核预期

**第一批只实施A1—A6**：
1. 在独立审核文件保存旧值、稳定ID、目标ID、拟新增值、来源标题与日期、读取日期、简短事实摘要、适用范围和仍未知项。
2. 在build_entity_model.py给A1／A2增加按稳定ID的类型覆盖；在生成pendingIdentities时只移除已有审核依据的两个对象。不能只改生成的review.json。
3. 给A3—A6各新增一条具名作品层职责，status用sourceReviewed。dossierMemberships沿用生成器的existingEvidence口径；不自造新的成员状态。
4. 不改关系数组、别名映射、entityId、workId、contentVersionId、releaseId，不更换已有发行原文；原始四份核心JSON无须改变。

如果按上述严格范围实施，预期为：
- 实体总数仍326；待核身份199→197。
- 参与记录4743→4747；专题引用总数仍2234。
- 待核专题职责620→616，只清除key/HBR、august/imys、minatosoft/g1251、minatosoft/climax四条；hawkeye/g1251仍待核。
- 主库1274部、内容1487个、平台发行2487条以及各作品既有位置均保持。
- 关系数组及实体ID集合保持一致。以上是方案预期，不是本次已经产生的结果。

**第二批再做B类**：先取回Alicesoft开发协力原证，再核Legend／Mosaic逐作身份对应；JAST、MangaGamer按法律／业务名义证据处理。复合署名的拆分需要独立设计与审核，不能把这次的提示补充伪装成身份拆并完成。

## 7. 落地验收要求

以下为本批生成与验收命令；执行结果另见本次提交／PR说明。

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

另检查：四份核心JSON字节摘要不变；relations和稳定ID不变；只减少4条具名pendingRole；父品牌与公司没有因子品牌贡献得到开发署名；Shiravune没有因团队类型改变而自动增加逐作翻译；所有旧专题URL、锚点与五年分组保持。独立提交应同时包含证据记录、规则与生成文件，不修改历史迁移基线。

## 8. 已读取的仓库入口

- [AGENTS.md](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/AGENTS.md)
- [entity-model.md](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/data/entity-model.md)
- [重构审计](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/data/entity-refactor-20261021-audit.md)
- [待核身份列表](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/data/entity-migration-review.json)
- [实体索引](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/data/entities.json)
- [参与与专题成员索引](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/data/credits.json)
- [实际规则入口](https://github.com/wt1234-donkey/visual-novel/blob/f146070527470017120c08973ada0fca398c00ee/scripts/build_entity_model.py)

实际核查的生成页包括entities.html、key.html、august.html、yuzusoft.html、minatosoft.html、mosaic.html、legend_uk.html、madosoft.html、champion_soft.html、nitroplus.html、alicesoft.html；另读相关公司覆盖、主库作品及平台发行原文。页面与JSON互证，页面存在来源链接不等于链接本轮可达；本报告已分别说明403、超时及旧路径重定向。

## 9. 本批实施与验收结果

已落实A1—A6：Spike Chunsoft核为公司、Shiravune核为本地化团队；Key/HBR及AUGUST/imys增加限定的联合制作，Minato Soft/g1251增加原作制作，Minato Soft/Climax增加监修。机器输入保留订正前值、原始署名、来源及适用范围。四条新增职责在专题卡片提供范围说明与本审核记录链接。

生成后实际数量：326个实体、4747条参与记录、2234条专题引用；197个历史署名身份与616条专题职责仍待核。四份原始核心JSON、两份迁移基线、全部实体ID／关系、专题位置及旧参与记录均与本批父提交一致。

验证：22项Python测试、205项Node测试通过；内容与实体校验通过；三类生成器的--check及git diff --check通过。回归额外确认Hawk Eye没有因Minato品牌贡献取得开发职责，CHiRAL／Alice Blue的父主体待核保持，Shiravune没有自动新增逐作本地化职责。B1—B8与C1—C2仅登记缺口，未执行身份拆并或事实订正。
