# Adventure International：叙事冒险与UK原创（2026-10-16）

维护目标：`wt1234-donkey/visual-novel`。基线为main的`27d68a8dddab065112e26fa851b7208866b6e558`。

## 范围与结果

- 按“游戏玩法分类梳理”原清单重新核对，只收叙事冒险。40个目录项目：美国本社及作者/改编关联36个，UK原创4部。
- 六个分组：Scott Adams经典14、Other Venture 5、Robert Lafore互动小说5、其他叙事调查9、Questprobe 3、UK原创4。三个Kid Venture、动作、策略、模拟、地牢RPG等不建作品卡片，只在排除清单说明。
- 主库复用`g089/g091/g092/g093/g138`，新增`g1080` Nightwalker，1982年TRS-80原作内容与首批发行各一条。
- 其余34部存`dossierOnlyWorks`，均含文字输入，不进入主库，也不虚构逐机种首发或内容身份。专题与主库范围不同，顶部7个内容/9条发行仅统计6部主库关联作品。
- 全库1077部作品、1268个内容版本、2260条平台发行、58专题。既有1076部、1267个内容和2259条发行按ID逐对象保留；其他57个厂商配置保持。

## 关键操作证据

| 项目 | 原资料 | 判定 |
|---|---|---|
| Nightwalker | [原厂说明书](https://www.mocagh.org/ai/nightwalker-manual.pdf)印刷页2—7；[发行目录](https://www.mobygames.com/game/120798/nightwalker/) | 方向键/固定按键移动与调查，Y/N为封闭回答，证据按编号选择。存档名输入不计文字输入玩法。主库新增。MobyGames的Text parser宽泛标签不代替说明书逐项控制说明。 |
| Labyrinth of Crete | [原厂说明书](https://www.mocagh.org/ai/labyrinthcrete-manual.pdf)Controlling Your Characters | VERB NOUN、J/或H/指定人物，GET COIN、SPEAK加名字等，明确为文字输入。仅专题。 |
| Olin in Emerald | [原厂说明书](https://www.mocagh.org/ai/olin-manual.pdf)Playing Olin | 多数用空格/回车选项，但部分问题必须键入答案。菜单与文字输入并存；不能只看菜单排除输入标签。仅专题。 |
| Spook House / Toxic Dumpsite | [原说明书](https://www.mocagh.org/ai/spooktoxic-manual.pdf) | 鼓励完整句子，最长50字符。倒计时不会取消输入玩法，仍属冒险。两个独立可玩程序分别计数。 |
| Lafore Interactive Fiction五部 | [原厂目录](https://www.mocagh.org/ai/ai-v3i1catalog.pdf)Interactive Fiction节；[原说明](https://www.mocagh.org/ai/if-manual.jpg) | 自由输入完整回应，不按预设选项分支冒险入主库。 |
| Maces & Magic三部 | [通用原手册](https://www.mocagh.org/ai/macemagic-manual-alt.pdf)Special Commands | 核心为属性/装备/地牢RPG，按本次其他类型排除；且G后的物品名称与P后的CLIMB等自由动作仍需输入，原目录“menu-driven”不能证明无输入。 |
| Treasure Quest | [原厂目录](https://www.mocagh.org/ai/ai-v3i2catalog.pdf)第14页；[说明书](https://www.mocagh.org/ai/treasurequest-manual.pdf) | 原厂分类Simulation，航向、时间、潮汐与船员模拟为核心，排除。纠正原清单把它放在其他叙事作品中的宽口径。 |
| Reign of the Red Dragon | [原厂手册](https://www.mocagh.org/ai/reddragon-manual.pdf) | 迷宫移动、角色装备和实时战斗/投掷操作为核心，按动作RPG排除。 |

## UK与作品身份

- UK四部：Gremlins: The Adventure；Robin of Sherwood: The Touchstones of Rhiannon；Seas of Blood；Super Gran: The Adventure。原清单遗漏的Super Gran文字冒险依[1985年原始发行档案](https://worldofspectrum.org/archive/software/text-adventures/super-gran-the-adventure-tynesoft)与[开发沿革](https://en.wikipedia.org/wiki/Adventure_Soft)补入。同名动作游戏不收。Super Gran实际发行Tynesoft，非Adventure International美国发行。
- 英国移植美国经典不另计UK原创；Mysterious Adventures早于AI UK的原作不因后购权变为UK原创。Rebel Planet、Kayleth、Temple of Terror等1986年后的Adventuresoft作品不扩入本期。
- Other Venture #1 Classic Adventure是John Rausch的巨洞改编，沿用`g089`；专题上下文说明1981 Apple II关系，不新造一部“巨洞原作”，不增普通移植发行。1976原作与1981改编不混为公司1976年成立/发行。
- Return to Pirate’s Isle为TI-99/4A的Scott Adams系列第14作，实际发行Texas Instruments；不是2000年Return to Pirate’s Island 2。
- Secret Mission/Mission Impossible/Atomic Mission与Fun House Mystery等改名不新增作品。双篇包装Spook House/Toxic Dumpsite和Sledge of Rahmul/Merlin’s Treasure各保留两个独立程序。
- X-Men未完成游戏、独立出版漫画、样本与合售包不增加独立作品。

## 年份、内容版本与证据限度

公司建制采用常见1979年说法，早期作品与自行销售始于1978；不伪造具体月日。原厂目录、[Strong藏品说明](https://www.museumofplay.org/blog/scott-adams-adventure-international-collection-documents-early-commercial-computer-gaming/)、[CASA目录](https://solutionarchive.com/list/company,3/orderby,year/orderdir,DESC/)与馆藏包装交叉核对。仅专题条目的年份是书目排序年，不是新建的逐平台首批发行声明。

早期日期异文保留：Pirate Adventure沿用原库1978，Strong记1979；Strange Odyssey、Pyramid、Mystery Fun House、Savage Island I等原作与商品目录标年有差异；Claymorgue采用BBC档案的TRS-80原作1983而非后移植1984；Labyrinth保留1981/1982/1983异文；Sledge/Merlin标题记1982但CASA备注指出1983列新品。未用后发说明书版权年反推原作。

本批只新增Nightwalker原作1个内容身份。C64三维界面与DOS后移植尚未形成具体、首次新增内容的完整证据链，不主动添平台行。SAGA确有新增绘图的情形，但各作首批日期和增量未逐一核完，不用“SAGA”或“增强”字样批量生成内容版本。专题为具名作品范围完成，不宣称所有版本增量已经穷尽。

## 验证

已通过：数据关系校验、Python 12项单元检查、Node 92项筛选/内容回归、58页生成一致、互动/内容/发行CSV同步，以及`git diff --check`。新增回归验证仅专题书目不进入主库/版本表、UK四部逐卡标签、Nightwalker检索与文字输入排除、Classic Adventure复用身份及排除清单不生成卡片。

发布状态以目标仓库main、合并请求及Pages工作流为准。
