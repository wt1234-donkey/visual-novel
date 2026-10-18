# Mosaic Publishing作品、玩法与发行归属核对

2026-10-18。目标：**wt1234-donkey/visual-novel**。本轮基线：13bca0717411599f433d952e4df4ea238ce8c794。

## 范围与统计

用户指定此前“列出Carry Lab（キャリーラボ）游戏类型清单”项目中的Mosaic Publishing。上下文检索未完整返回该原回复，不能宣称本轮取得了原文或逐字逐项复刻。此处依据[历史目录](https://www.lysator.liu.se/adventure/Mosaic_Publishing.html)、[Level 9作品目录](https://www.lysator.liu.se/adventure/Level_9_Computing.html)、[创办人及开发者访谈](https://classicadventurer.co.uk/pdf/03.pdf)、原厂说明书和馆藏，重建具名范围；不把检索失败当作停工理由，也不声称全部地区软件已穷尽。

- 新增主库4部：g1200《秘密日记》、g1201《The Archers》、g1202《Yes, Prime Minister》、g1203《Growing Pains》。均有原厂操作证据，未新增自由行动／对象／会话文字输入。
- 复用g131《The Saga of Erik the Viking》一个旧输入身份，原对象、标签、内容和发行不修改。
- 新建6部仅专题输入书目：Pen and the Dark、Width of the World、Nomad of Time、Stainless Steel Rat Saves the World、Snow Queen、Twice Shy。不进入games.json，不生成内容／发行。
- 正文11个档案；末尾34项／5组玩法表，11行对应正文，其余说明同作机种、包装、工具、计划和资料缺口，34项不是34部已发行游戏。
- 新增4个原作内容、4条最早已核批次发行，没有后发增补版。四段／更多程序不是四部独立作品。
- 主库1196→1200、内容1394→1398、平台发行2388→2392；跨类型591不变、仅专题书目116→122、专题72→73。

## 公司与开发／发行

[历史沿革](https://de.wikipedia.org/wiki/Mosaic_Publishing)记1983年7月由Vicky Carne创立；[创办人公开履历检索](https://uk.linkedin.com/in/vicky-carne)亦记Mosaic 1983—1988。月份采用有明确出处的历史资料，未补造日级成立日期。1987／1988结束时间在历史资料中不同，专题不强行认定统一法人注销日。

[The Classic Adventurer第3期的创办人及开发者访谈](https://classicadventurer.co.uk/pdf/03.pdf)用于核对出版思路、外部开发、未实现计划与第一方回顾，不把Mosaic的出版合作说成全部自行开发。具体作品归属优先看下表原厂署名。

Growing Pains的原厂手册明确署**Virgin Games Ltd**，本轮保留其最早已核Spectrum原作发行。同期评测明确Level 9与Mosaic合作、Virgin销售；[Mosaic馆藏](https://www.computinghistory.org.uk/det/13048/The-Growing-Pains-of-Adrian-Mole/)与MSX发行记录说明Mosaic关系，但普通机种移植和未经比较的同年记录不据此追加内容／平台行。主题关联不要求所有作品都由主题厂商发行。

## 四部新准入与原厂控制证据

| 作品 | 原作／已核首批 | 控制、剧情与来源 |
|---|---|---|
| The Secret Diary of Adrian Mole Aged 13¾ | 1985，ZX Spectrum，Mosaic Publishing Ltd | [原厂手册](https://unbox.ifarchive.org/1jspogoh0v/level9_docs/the_secret_diary_of_adrian_mole-manual.pdf)记1–3决定阿德里安的剧情，SHIFT继续；4打开帮助。内容是一年日记中的家庭、朋友与青春烦恼。手册自身明确1985 Mosaic出版；[Spectrum原版目录](https://worldofspectrum.net/item/0006942/)支持平台。 |
| The Archers | 1986，BBC Micro，Mosaic Publishing Ltd | [原厂手册](https://unbox.ifarchive.org/1jspogoh0v/level9_docs/the_archers-manual.pdf)记1–3作四名角色的编辑决定，SHIFT／RETURN继续，收听数据反映后果。人物Jack Woolley、Elizabeth Archer、Eddie Grundy、Nelson Gabriel逐一列出；©1986与[馆藏](https://www.computinghistory.org.uk/det/20812/The-Archers/)、[BBC目录](https://www.bbcmicro.co.uk/game.php?id=2035)一致。 |
| Yes, Prime Minister: The Computer Game | 1987，ZX Spectrum，Mosaic Publishing Ltd | [原厂手册](https://www.gamesdatabase.org/Media/SYSTEM/Amstrad_CPC//Manual/formated/Yes_Prime_Minister_-_Mosaic_Publishing.pdf)记五天事件、办公室对象光标、数字／光标对话、Hackergram选点与门内地点列表。Jim Hacker、Humphrey、Bernard均有角色说明。手册确认ODE制作及BBC由Five Ways实现；[Spectrum发行目录](https://worldofspectrum.net/item/0005819/)确认原版。 |
| The Growing Pains of Adrian Mole | 1987，ZX Spectrum，Virgin Games Ltd | [原厂手册](https://unbox.ifarchive.org/1jspogoh0v/level9_docs/the_growing_pains_of_adrian_mole-manual.pdf)记十八个月的学校家庭生活、1–3决定与SHIFT／RETURN继续，最后明确1987 Level 9／Virgin署名；[Spectrum发行档案](https://worldofspectrum.net/item/0006403/)区分Virgin原版和Ricochet再版。[同期评测存档](https://cpcrulez.fr/GamesTest/the_growing_pains_of_adrian_mole.htm)说明Mosaic合作。 |

“文字输入”按本库规则指键入自由行动、对象或会话。三部Level 9的数字选择属于选项分支；SAVE、LOAD、存档文件名与装载下一段的固定YES均为系统操作。没有因为手册出现“type”就全部排除，也没有以菜单存在为由忽略真正的解析器。

Yes, Prime Minister的光标可由摇杆或键盘控制，记点击调查，不写成鼠标／触屏专属；地点列表记菜单指令，不标直接角色移动。对话后的空格推进属于阅读推进。民意评分不直接等同资源经营；Hackergram用于回应立场，未凭图表外观贴成解谜。原厂提到快慢speech output不能单独证明真人配音；四条新发行为“未核实”，没有把BGM或文字显示误标有角色配音。

The Archers的四名人物分段是给定流程，本轮不推断可随时选择阅读视角，不额外贴视角切换。三部选择作品有预制角色事件和后果，区别于自由写日记工具，也不是按纯日常能力训练收录。

## 输入式书目

| 作品 | 年份、身份与控制依据 |
|---|---|
| Pen and the Dark | 1984，Keith Campbell，Colin Kapp文学改编；[作品与剧情](https://www.solutionarchive.com/game/id,394/)、[文字命令流程](https://www.solutionarchive.com/file/id,23603/)支持Fritz van Noon／Dr. Courtney的异常调查。仅专题。 |
| Width of the World | 1984，Simon Gould；[作品资料](https://www.solutionarchive.com/game/id,640/)与[实际指令流程](https://www.solutionarchive.com/file/id,904/)确认行动／对象／话语输入、寻找Sarah。原小说1983初刊不当游戏首发年。 |
| Nomad of Time | 1984，Shards；[Mosaic原厂手册](https://www.mocagh.org/miscgame/nomadoftime-manual.pdf)确认Oswald Bastable、六十天、飞艇固定面板与离艇后的两词英语命令。即使飞船部分非输入，仍有地点解析器，整作排除新增库。实时计时不自动标即时动作。 |
| Stainless Steel Rat Saves the World | 1984，Shards C64；[原厂再版说明](https://mocagh.org/miscgame/steelrat.pdf)确认1984 Shards、原发行Mosaic和两词英语输入；[流程](https://www.solutionarchive.com/file/id,3110/)交叉核查。与Harrison／O’Connell的Spectrum MIA条目不强行合并实现或补造发行。 |
| Snow Queen | 1986，St. Bride’s；[CASA](https://www.solutionarchive.com/game/id,1309/)明确1985仅预制作展示、成品不早于1986，[流程](https://www.solutionarchive.com/file/id,7230/)确认输入。保留WoS等1985异文，两个部分不拆作。 |
| Twice Shy | 1986，Ram Jam；[作品资料](https://www.solutionarchive.com/game/id,562/)确认Jonathan Derry与磁带调查，[流程](https://www.solutionarchive.com/file/id,797/)含自由行动／对象与询问人物词句。即使有赛马／驾驶／射击题材，仍按输入式排除新增库；未推断成即时枪战。 |

仅专题书目的“来源核对”表示控制有明确手册或字面指令流程支持，不表示本轮逐机种实机通关。未取得原厂控制证据的小游戏不额外猜标签。

## 沿革、工具与未发行边界

- g131已有1984 Spectrum发行，保持原字段；Level 9目录有该机种1985异文，专题说明。没有用新书目复制旧作品，也未改历史未知内容关系。
- Secret Diary的C64捆绑、BBC磁盘、后发渠道与Ricochet／Mastertronic／Alternative再版不制造新作品或内容。没有具体新剧情、美术、音乐或录音的首次批次证据，暂不扩列。
- [Spectrum Stainless Steel Rat档案](https://worldofspectrum.net/item/0010239/)标MIA、无发行记录；缺档不等于已证实未发行，也不等于已经核到C64同内容移植。只留身份待核参考。
- In the Beginning有[1983旧计划档案](https://www.gamesthatwerent.com/gtw64/in-the-beginning/)及1984成品目录／创办人回顾，列演化关卡动作参考，不因进化背景补成固定叙事。
- [My Secret File](https://www.computinghistory.org.uk/det/69007/My-Secret-File/)为儿童个人资料库；[Secret Diary Kit](https://www.computinghistory.org.uk/det/13025/The-Adrian-Mole-Secret-Diary-Kit/)有附纸本的套装实物，但未核独立预制剧情，均不入叙事库。Beyond the Arcade为Nicholas Palmer纸本书。
- [Raffles](https://www.solutionarchive.com/game/id,7861/)、[Alice](https://www.solutionarchive.com/game/id,7862/)、[The Amulet](https://www.solutionarchive.com/game/id,7242/)为未实现计划；Amulet的1987是拟发行年。Foundation未获授权，Coronation Street是未实现构想，1983新闻的Special Deliverance／Soldier, Ask Not／The World-Thinker不作已发行作品。
- Ram Jam的早期Yes Minister方案和ODE的1987已发行Yes, Prime Minister分别说明；不因改题制造两个已发行原作。Pen的Dragon、The Subways of Tazoo及Twice Shy C64计划不生成发行。

## 验证

运行CSV同步、内容／互动／数据模型校验、Python及Node全套测试和专题生成一致性检查。专项回归核对数字选择与系统命令边界、四个新作可检索、旧Erik复用、六部输入书目不入主库或生成内容、Virgin首发、四段不拆作、34行参考完整对应正文，以及计划／工具不混成已发行游戏。另以13bca0717411599f433d952e4df4ea238ce8c794逐对象比对旧1196主库、1394内容、2388发行、72个公司对象与72个生成页面。
