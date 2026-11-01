# 1970年代早期互动小说与文字冒险补录（2026-11-01）

基础身份库：10,833 → 10,840；输入候选 12 部，新建身份 7 部，关联已有身份 4 部，待核 6 部。

## 年份口径

firstYear按最早可核的创作/首个实质版本年份记录。开发起始、首次可玩、公开传播、同期杂志刊载、商业销售和后续移植分别写入证据说明；不将不同阶段混成一个首发日期。

## 已审阅作品

| 作品 | 年份 | 历史范围 | 类型 | 平台线索 | 来源 |
|---|---:|---|---|---|---|
| Hunt the Wumpus | 1973 | precursor | 文字迷宫探索（互动小说前史） | BASIC、早期分时系统 | [档案/资料](https://foldoc.org/wumpus) |
| Wander | 1974 | proto-adventure | 文字世界模拟／互动小说原型 | Unix（PSL Games distribution） | [档案/资料](https://www.inform-fiction.org/manual/html/s46.html) |
| Zork | 1977 | core-interactive-fiction | 文字冒险（MDL解析器） | PDP-10、ITS | [档案/资料](https://github.com/MITDDC/zork) |
| Stuga | 1978 | core-interactive-fiction | 瑞典语文字冒险（解析器指令） | DEC-10 Oden、QZ time-sharing system | [档案/资料](https://microheaven.com/svenska/stuga_historik.shtml) |
| Acheton | 1978 | core-interactive-fiction | 文字冒险（大型机解析器） | IBM 370 Phoenix | [档案/资料](https://ifarchive.org/indexes/if-archive/phoenix/games/zcode/) |
| Haunt | 1978 | core-interactive-fiction | 文字冒险（规则系统驱动） | DEC-10、DEC-20 | [档案/资料](https://laird.engin.umich.edu/haunt/) |
| Dog Star Adventure | 1979 | core-interactive-fiction | 文字冒险（BASIC两词解析器） | TRS-80 Model I Level II | [档案/资料](https://www.ifarchive.org/indexes/if-archive/games/source/basic/) |

## 年份与版本核验说明

- **Hunt the Wumpus（1973）**：FOLDOC记载Gregory Yob约于1973年创作；其完整BASIC程序于Creative Computing第1卷第5期（1975年9—10月）刊载。此处firstYear登记创作年份，不把1975年杂志刊载误写成创作年。它是文字迷宫探索前驱，不具备Adventure式自然语言解析器，故单独标记precursor。
- **Wander（1974）**：Graham Nelson的互动小说史将Peter Langston的Wander明确记为1974年，描述为含房间、状态和可携带物品的文字世界建模程序，并谨慎称其为proto-adventure。它兼具早期文字游戏与创作系统性质，不能等同成熟商业文字冒险。
- **Zork（1977）**：MIT Libraries Department of Distinctive Collections公开保存1977年Zork源代码，档案说明作品由Tim Anderson、Marc Blank、Bruce Daniels和Dave Lebling等人在MIT创作。Computer History Review记载首个版本于1977年6月出现。Dungeon是早期流传名称；Infocom于1980—1982年将大型机作品拆分为商业三部曲，Zork I不是本条的首发年份。
- **Stuga（1978）**：作者相关历史记述称Kimmo Eriksson、Viggo Eriksson和Olle Johansson于1977年开始制作，首个版本在1978年秋完成，并于1978年末放到瑞典QZ公共主机区供用户运行。1986年PC商业版改名Stugan，属于后续平台发行，不替代1978年原始版本年份。
- **Acheton（1978）**：IF Archive的Cambridge Phoenix目录记载Acheton由David Seal、Jonathan Thackray和Jonathan Partington创作，年份为1978—1980；Inform书目将其首个实质版本范围列为1978—1979。Cambridge历史资料说明Thackray和Seal于1978年开始创作，后续继续扩展至1980年前后。firstYear取开始创作/首个实质版本1978，不把完成年份或后来的PC移植年份当作首发。
- **Haunt（1978）**：作者John E. Laird的个人学术主页明确说明Haunt是受Adventure启发的文字互动冒险，开发始于其约1978—1981年在Carnegie Mellon读研期间；Inform书目将作品列为1978年。firstYear取开发起始年1978，后续开发跨至1981年，不代表1978年已完成最终版本。
- **Dog Star Adventure（1979）**：IF Archive保存的dogstar.bas注明来源为SoftSide 1979年5月刊；Solution Archive记载原版磁带于TRS-80平台发行，并于1979年4月刊广告、5月刊登BASIC输入清单。原程序版权页标注1979。Death Planet是后续商业发行标题/版本，不另建原作身份。

## 已有身份关联（未重复新增）

- Colossal Cave Adventure：匹配已有身份 g089（1976）
- Adventureland：匹配已有身份 g091（1978）
- Voodoo Castle：匹配已有身份 ai-voodoo-castle（1979）
- The Count：匹配已有身份 g093（1979）

## 自动去重或年份冲突待核

- **Mystery Fun House**：部分二手清单列1979，但IF归档版本信息出现1981版权年份；尚未取得可统一原版首发的同期一手证据。
- **Pyramid of Doom**：不同目录对1979/1981年份存在冲突；须核对Scott Adams与Alvin Files合作原版的同期发行材料。
- **Secret Mission / Mission Impossible**：标题别名、作品编号及发行年份存在混用；需取得可核对的原版磁带或同期广告后再确定身份与年份。
- **Journey to the Center of the Earth（Greg Hassett）**：互动小说史文献特别提示该1978条目存在真实性/恶搞疑问，本批不纳入基础身份库。
- **Hunt the Wumpus 的1975年刊载版本**：与1973年创作身份属于同一作品；不另建1975年作品身份或内容版本，刊载年份只保留在证据说明。
- **Pirate Adventure**：title/alias exists with a different firstYear

## 人工范围排除

- **SHRDLU**：1972年自然语言理解研究系统，不是游戏作品。
- **DND / PEDIT5**：PLATO上的早期地下城RPG/迷宫游戏，与本批以文字冒险和互动小说为核心的收录边界不同；可另做计算机RPG前史专题。
- **MUD1 / Essex MUD**：多人在线虚拟世界/角色扮演系统，不作为本批单人互动小说作品入库。
- **The Oregon Trail**：历史旅行教育模拟，不属于本批文字冒险/互动小说核心类型。

## 分类原则

- Hunt the Wumpus标记为文字迷宫探索前驱，不宣称其具有Adventure式自然语言解析器。
- Wander标记为文字世界模拟/互动小说原型，兼具创作系统性质，不与成熟商业文字冒险混为一类。
- Colossal Cave Adventure的Crowther原始作品与Woods扩展属于同一作品的版本演进，不重复建身份。
- Zork指MIT大型机原始作品；1980—1982年商业三部曲是后续拆分发行，不把Zork I年份倒填给原始作品。
- Stuga、Acheton和Haunt的开发跨越多个年份，firstYear只取最早可核的创作/首个实质版本年份。
- Adventureland的1978年首个实质版本、1979年广告和馆藏平台记录分别保留。

## 自动验证与上线

导入脚本保留导入前全部作品对象哈希，并逐条复核新增记录；重复执行不会重复追加。GitHub Actions运行数据/实体校验、Python和Node回归测试后，将审计文件、报告和基础身份库生成结果提交到本PR分支。只有检查通过且合并到main后，才视为正式上线。

## 本批暂缓

- **Mystery Fun House**：部分二手清单列1979，但IF归档版本信息出现1981版权年份；尚未取得可统一原版首发的同期一手证据。
- **Pyramid of Doom**：不同目录对1979/1981年份存在冲突；须核对Scott Adams与Alvin Files合作原版的同期发行材料。
- **Secret Mission / Mission Impossible**：标题别名、作品编号及发行年份存在混用；需取得可核对的原版磁带或同期广告后再确定身份与年份。
- **Journey to the Center of the Earth（Greg Hassett）**：互动小说史文献特别提示该1978条目存在真实性/恶搞疑问，本批不纳入基础身份库。
- **Hunt the Wumpus 的1975年刊载版本**：与1973年创作身份属于同一作品；不另建1975年作品身份或内容版本，刊载年份只保留在证据说明。
