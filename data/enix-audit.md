# Enix（艾尼克斯）主表七部补齐（2026-10-14）

## 本次补录与当前数量

按用户“将主表的那7部补充进数据库和专题”的具名指示，补录以下七部独立作品及八条内容版本。现主库999部作品／2139条版本、56个厂商专题；Enix主库关联28部／31条版本，连同原跨类型《七风岛物语》为29部／32条。28部主库作品都有Enix发行记录，其中30条版本实际归档Enix，另1条《Riven》2024重制版归档Cyan Worlds。

| 新增作品 | ID | 已核首条记录 | 操作与内容边界 |
| --- | --- | --- | --- |
| 翼人2：基塔克拉复活 | g996 | 1986 PC-8801 | 图文指令；独立续作 |
| 北斗神拳：剧画冒险 | g997 | 1986 PC-8801 | 菜单调查、实时战斗；区分同名动作游戏 |
| 动物乐园杀人事件 | g998 | 1987 MSX | 菜单调查；小说不列游戏版本 |
| 翼人 Special：告别梦战士 | g999 | 1987 PC-8801mkIISR以降 | 图文指令；第三部独立故事，非前作加强版 |
| 古村物语 | g1000 | 1988 PC-8801mkIISR以降 | 菜单、俯视探索及事件冒险 |
| 裂痕：Riven | g1001 | 1997 PlayStation（日本） | Enix日版首批；另记2024新谜题与扩展叙事重制 |
| 神秘方舟：幻影剧场 | g1002 | 1999 PlayStation | 动作解谜融合；非1995《Mystic Ark》的普通移植 |

两个新指令作品g996、g999通过`authorizedCommandWorkIds`具名登记，附本次指示的范围说明；原七个`legacyCommandWorkIds`保持不变，也不启用全厂商指令游戏的广泛例外。《幻影剧场》明确标为“动作解谜融合”，不将实际动作操作隐藏为纯文字选择。新中文名均标站内编辑译名。

## 来源与版本判断

- **翼人2：** [游戏保存协会1986年4月目录](https://www.gamepres.org/pc88/library/1986/1986_4.html)及[FM-7资料](https://fm-7.com/museum/products/vryaz12r/)支持PC-8801原作、Enix及人物／剧情；FM-7为同年6月后版，未核新增内容不另列。
- **北斗神拳：** [协会1986年5月目录](https://www.gamepres.org/pc88/library/1986/1986_5.html)支持Enix电脑冒险版与角色故事；[操作资料](https://w.atwiki.jp/retroadventure/pages/94.html)辅助核菜单选择。与其他厂商发行的同名家庭机、街机动作作品分开。
- **动物乐园杀人事件：** [协会馆藏目录](https://www.gamepres.org/catalog/?id=8811002158000)支持Enix、1987和MSX；[玩法资料](https://w.atwiki.jp/gcmatome/pages/7312.html)辅助核警探、警犬おいどん与菜单调查。1989小说属于其他媒介。
- **翼人Special：** [协会1987年12月目录](https://www.gamepres.org/pc88/library/1987/1987_12.html)说明输入指令、两段故事及角色；[平台资料](https://www.8-bits.info/gamelist/PC88/info/info_fyTNpnZXBKtAgKsX.php)交叉核发行。1988 MSX2无新增内容证据，不追加；两段故事不拆为两个游戏。
- **古村物语：** [协会1988年12月目录](https://www.gamepres.org/pc88/library/1988/1988_12.html)支持Enix、俯视探索冒险及シオン／カイザー王；PC-98无已核新增叙事不另列。
- **Riven：** [日本PS产品档案](https://www.suruga-ya.jp/product/detail/140001086)核1997/12/23及エニックス；[原版故事与产品资料](https://psxdatacenter.com/games/J/R/SLPS-01180.html)支持人物与环境解谜。首条是Enix日本PS发行，不能代表全球电脑版的发行署名；五张CD是一部完整作品，1998日本Saturn普通移植不另列。Cyan[2024开发说明](https://cyan.com/2024/03/19/a-classic-reimagined-riven-set-for-2024-release-for-flatscreen-and-vr-platforms/)明确新谜题与扩展叙事，所以追加内容版本；[上市公告](https://cyan.com/2024/06/03/riven-launch-date/)核2024/06/25及Windows、macOS、Meta Quest。同批平台合为一行；[Steam产品页](https://store.steampowered.com/app/1712350/Riven/)核Cyan Worlds, Inc.发行与英语人声，中文、日文不能据此标为有配音。图像重做和VR本身不是增行理由。
- **幻影剧场：** [PS产品与操作资料](https://psxdatacenter.com/games/J/M/SLPM-86147.html)核1999/03/18、Enix、少年／少女选角、港城剧场故事及物品使用／攻击／跑动等动作。保留动作解谜细分类，区分1995年RPG原作。

除2024《Riven》已核英语人声外，其余七条首批记录的角色配音保持“未核实”。不把芯片音源、动画口型、同捆音带直接当人物录音。普通移植、重售、下载渠道没有已核新增内容不追加版本；未发行计划不计。

## 校验与历史保护

本次以提交396409505fdd6f8c13b23f51e6addedc9e122d21为基线，检查原992部作品、2131条版本以及其他55个厂商专题逐对象不变。JSON与CSV同步，56个专题页面同步；测试覆盖七部独立身份、具名指令范围、动作细分类、Enix与Cyan发行筛选，以及Riven只有两条有依据的内容记录。当前28部是已核主表范围，不表示Enix全部RPG及跨类型叙事游戏均已穷尽。

以下为第一批历史审计，当时数量与范围仅描述该批。

# 第一批历史核对（2026-10-14）

## 成立顺序与历史署名

[官方公司概要](https://www.hd.square-enix.com/jpn/company/outline.html)明确1975/09/22设立；[官方沿革](https://www.hd.square-enix.com/jpn/company/history.html)分列1975年営団社募集サービスセンター前身、1982年8月改用Enix商号、1989年吸收合并、2003年Square合并及2008年持株公司分拆。专题采用官方前身起点，接在Microsoft之后、Data East之前；游戏业务及Enix名称不是从1975年就存在。

保留原作品的エニックス／艾尼克斯署名，归档索引统一Enix（艾尼克斯）。Enix、Square和合并后的Square Enix分别处理；官网今天显示SQUARE ENIX版权不证明1980或1990年代已经由合并后公司发行。开发作者、影视制作团队、游戏系统团队也不自动成为发行主体。

## 本批数量与旧记录保护

- 原主库975部作品、2100条版本对象原样保留；新增8部独立叙事作品、8条首发，更新为983部／2108条。
- Enix专题复用13部原库作品及15条旧记录；增加8部／8条主库内容，主库关联21部／23条。
- 官方明确为冒险RPG的《七风岛物语》放专题补充1部／1条，专题合计22部／24条。不是Enix全游戏、全部叙事作品或所有地区版本的穷尽目录。
- 专题总数53，其他52个专题对象不变。原13部作品及15条版本逐个对象保留，原来已有的普通平台行也不追溯删除。

## 原库13部

| 作品 | ID | 保留原记录 |
| --- | --- | --- |
| 波多比亚连续杀人事件 | g007 | 1983电脑、1985家庭机 |
| 玛丽酱危机一发 | g008 | 1983原作 |
| 女子宿舍危机 | g118 | 1983原作 |
| 飞鸟之恋 | g119 | 1983原作 |
| 不可思议之旅 | g120 | 1983原作 |
| 扎斯：夺回人工智能猎户座 | g078 | 1984原作 |
| 翼人 | g079 | 1984 PC-8801、1985 FM-7 |
| 高校大冒险 | g126 | 1984原作 |
| 暗黑城 | g127 | 1984原作 |
| 再一次：成功人生故事 | g128 | 1984原作 |
| 东京搭讪街 | g016 | 1985原作 |
| 轻井泽诱拐指南 | g017 | 1985原作 |
| 黄金国传奇 | g018 | 1985原作 |

七部原作品的“图文指令”细分类按具名legacyCommandWorkIds历史例外保留。不把旧分类重写成新菜单分类，也不借此继续新增需要键入词句的作品。旧姓名疑点、附带磁带与人物配音的区别、既有语音状态均不覆盖。专题作品卡直接引用主库同一ID。

## 新增八部

| 作品 | ID | 核定首年／平台 | 内容和操作依据 |
| --- | --- | --- | --- |
| JESUS／耶稣号：彗星危机 | g979 | 1987 PC-8801mkIISR | 固定菜单、数字键选项，非词句键入 |
| ANGELUS／安杰拉斯：恶魔的福音 | g980 | 1988 PC-8801mkIISR | F1—F10选取指令及通关自动欣赏模式 |
| Burning Point／燃烧点 | g981 | 1989 PC-8801mkIISR | 菜单式侦探调查与完整独立案件 |
| Misty Blue／迷雾之蓝 | g982 | 1990 PC-8801mkIISR | 数字键／回车菜单；人物关系与对话 |
| JESUS II／耶稣号2 | g983 | 1991 PC-8801mkIISR | 数字键菜单；独立新人物、新故事 |
| 欧亚特快杀人事件 | g984 | 1998 PlayStation | Cinema Active第一部，真人台词和限时搜证 |
| 0STORY／零度恋爱 | g985 | 2000 PlayStation 2 | Cinema Active第二部，全影片及全人声 |
| the FEAR／恐惧 | g986 | 2001 PlayStation 2 | Cinema Active第三部，实拍与CG恐怖选择 |

五部电脑作品归文字冒险／图文选项与调查，三部Cinema Active归互动动画／实拍影像·剧情分支。标题中的新中文名标站内编辑译名，日文及英文原名用于检索，不声称厂商正式汉化标题。

**JESUS。** [游戏保存协会1987年4月资料](https://www.gamepres.org/pc88/library/1987/1987_4.htm)明确停止词句寻找、改为固定命令选择；[有原广告与画面支持的回顾](https://akiba-pc.watch.impress.co.jp/docs/column/retrosoft/2040439.html)直接核1987/04/28、武麻速雄和FOJY，FM77AV同年7/24为后发行平台。[操作资料](https://www.8-bits.info/gamelist/PC88/info/info_va9UWtpTx7jN4aar.php)交叉核数字键菜单与发行方。Space Mouse是原产品内附小游戏，不单建一部新叙事作品。电脑版角色录音尚无直接清单，不把“AI说话”的文字描写或FM音源理解成实际人声。

**ANGELUS。** [原作画面、人物与键位资料](https://www.8-bits.info/gamelist/PC88/info/info_D03BjeRqNf3gPXfA.php)核1988年7月、记者ブライアン・パール及エリス・ミラー、F1—F10菜单与自动欣赏。张嘴动画不是配音证明；自动欣赏是原版内置功能，不追加版本行。未发行后续Holy Night不先补成已发售作品。

**Burning Point。** [游戏保存协会1989年2月目录](https://www.gamepres.org/pc88/library/1989/1989_2.htm)及[原作资料](https://www.8-bits.info/gamelist/PC88/info/info_TIHY9VixG9xTFdW5.php)支持Enix、PC-88、侦探マイク・スティール及调查原本已死孙女的案件；[协会冒险类型回顾](https://www.gamepres.org/pc88/library/adv.html)将其列入固定菜单阶段。日期仅以1989年为版本字段，零售档案2/23只作辅助，不凭声卡支持认定人声。

**Misty Blue。** [协会1990年4月目录](https://www.gamepres.org/pc88/library/1990/1990_4.htm)直接核4/2与Enix；[操作资料](https://www.8-bits.info/gamelist/PC88/info/info_IeQZ0MYkID5uFTLT.php)核菜单选择、回车确认。[剧情与系统考证](https://w.atwiki.jp/gcmatome/pages/4471.html)支持水上和哉、音乐人关系和多对象对话。原产品附加高校生回想与Enix Quest关系先写备注，不把同捆小模块都当独立发售作品；原声专辑不作游戏版。角色录音未核。

**JESUS II。** [版本与键位资料](https://www.8-bits.info/gamelist/PC88/info/info_r4Gwg8GGTHL3GW7D.php)直接核1991/03/24 PC-88原版、数字键菜单及1991/07/28 X68000后版。[剧情考证](https://w.atwiki.jp/retroadventure/pages/261.html)支持五色和也、佐伯真治及独立故事背景。它是续作，不合成前作版本；X68000只有平台和时间证据，没有新增叙事素材证据，不增行。人物衣着与职业的制作差异不编造统一解释，角色录音未核。

**欧亚特快杀人事件。** [产品及封面资料](https://psxdatacenter.com/games/J/M/SLPM-86135.html)支持1998/11/26、Enix、实拍推理；[原作片尾转录](https://raido.moe/staff/ps1/ps1_eurasia_express_satsujin.html)支持片岡つばさ、田宮京子及演员、录音、系统开发与发行工作人员。玩家探侦身份来自产品故事说明。演员台词记有人声，多张CD是同一完整发行，不拆版本。

**0STORY。** [官网产品页](https://www.jp.square-enix.com/game/detail/0story/)由game_detail.js读取同目录[game.json](https://www.jp.square-enix.com/game/detail/0story/game.json)，实际数据明确Cinema Active第二部、PS2、2000/04/27以及フルムービー＆フル音声。[实物产品与故事资料](https://psxdatacenter.com/psx2/games2/SLPM-65002.html)核Enix、General Entertainment、灵魂主人公与莉娜。二手页页头写5/17而正文写4/27；5/17也为原声发行，采用官方4/27，不混用唱片日期。当前官网版权改署SQUARE ENIX，历史版本仍记Enix。

**the FEAR。** [2001/07/11发布会及制作人原话](https://dengekionline.com/data/news/2001/7/11/6912c2130460179f71b3596a7f8c0676.html)明确第三部、7/26、PS2、四张DVD及演员；[游戏片尾转录](https://raido.moe/staff/ps2/ps2_fear.html)核实ENIX CORPORATION PRESENTS、演员和录音。片尾资料网页的页头7/29与发布会矛盾，本批按7/26记录并保留异文。[玩法考证](https://www.gavas.jp/products/detail.php?product_id=11347)支持摄像师身份。人物栏采用角色群体身份，不把演员姓名直接当虚构人物名。

[制作人访谈](https://automaton-media.com/articles/interviewsjp/20191118-106237/2/)辅助说明三部真人游戏路径和分支设计；日期以原产品或同期发布信息为准，不单凭回忆定日。

## 跨类型补充、版本边界与待续

**七风岛物语。** [官方产品页](https://www.jp.square-enix.com/game/detail/nanatukaze/)的[动态产品数据](https://www.jp.square-enix.com/game/detail/nanatukaze/game.json)直接支持1997/11/27、Sega Saturn和冒险RPG，简介为追查岛上黑风。实际取回数据核对，网页文字抓取只显示菜单不等于产品无资料。主角竜神ガープ由[有游戏画面支持的玩法考证](https://segasaturn-life.com/review-seven-wind/)辅助核。记录于relatedGames，主库四类数量不包含本作；配音未拿到直接演员证据暂未核实。

- JESUS FC由キングレコード发行，已见剧情、台词、角色形象删改及伙伴固定；删减和替换不直接证明增加新内容。本批暂不增行，不将之倒归Enix。原[FC说明书](https://www.gamingalexandria.com/fc/Jesus%20Kyoufu%20no%20Bio%20Monster/Jesus%20Kyoufu%20no%20Bio%20Monster%20-%20Cleartype.pdf)另支持发行身份，后续素材差异仍可核对。
- ANGELUS和JESUS II等普通电脑平台移植，没有已核第一次加入的剧情、场景、人物或录音，不因机种不同追加版本。廉价重售、下载渠道和不同光盘数量同样处理。
- 原g007的1985 FC行原样保留；[2005手机报道](https://k-tai.watch.impress.co.jp/cda/article/news_toppage/22125.html)提到新图像、提示和通关特典，但特典内容与首次加入的素材尚待具体核，暂不制造后版记录。[2023官网](https://www.jp.square-enix.com/ai-tech-preview/portopia/jp/)定位为AI技术体验，不能仅凭新平台和技术功能增加叙事版本。2027预告不计已发售。
- PS《金田一少年事件簿：悲报岛》《地狱乐园》发行方为讲谈社；Hudson《星见岛》已在原库专题。漫画题材或厂商印象不能替代发行署名，因此不收入Enix清单。
- Wingman后续、Riven日本发行在第二批补齐；Planet Laika及Enix RPG仍未完成全目录整理。Wonder Trek为Sony发行，不收入Enix发行清单。以下首批计数及范围保留为历史记录。
- LEVEL DIVE在发布会上公布且拍摄完成，不证明已经发售。Holy Night等取消或未完成计划不补造版本。外附音声、动画、攻略书和商品原声不是独立叙事游戏。

## 验证

JSON／CSV一致性、厂商别名归档、53个专题引用和静态页同步均检查；运行既有筛选测试。旧975部作品、2100条版本与其他52个专题逐对象比较。本批未改历史对象，也未以菜单新分类覆盖原库旧指令细分类。未核角色录音、日期异文和后版增量保留说明。
