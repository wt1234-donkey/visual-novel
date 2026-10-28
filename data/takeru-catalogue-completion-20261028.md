# TAKERU指定对话清单补齐（2026-10-28）

目标仅为 `wt1234-donkey/visual-novel`。用户已明确指定：依据“列出Leland的游戏及游戏类型清单”项目中的TAKERU游戏清单，修改TAKERU专题、补充主库并上线。TAKERU为Brother的软件销售渠道；不是同名Sur de Wave公司，也不把渠道目录解释为Brother独立开发清单。

## 对话清单与实际去向

以远程main `a4cdcae0cc5cba9ab93f2f475ca8ea74768b4eef` 为基线。对话的MobyGames关联目录35项和PC-88原创／专售目录29项，除Cosmo Saint Leaza重复外各有去向；另保留原专题Madeline、Cocktail Soft增刊号，共65行项目。行数含追加包、资料扩展及非游戏，不是65部独立游戏，也不是渠道全部销售记录。对话提及的更大MSX目录不在这两份指定清单的穷尽声明内。

| 范围 | 处理 |
| --- | --- |
| 新增主库3部 | g1307 Proserpia、g1308 Lonely Heart、g1309 Crystal Chaser |
| 复用既有主库5部 | g743、g812、g1278保持；g755口红冒险2、g830毕业新增渠道专题引用，不复制作品或普通再发行 |
| 新增剧情RPG关联3部 | HAYATO、Cosmo Saint Leaza、Estland Campaign；原作共3个内容、3条首次发行 |
| Sorcerian追加内容 | 复用sierra-on-line-sorcerian，追加7个内容版本／10条首次批次发行，共19篇剧情；不复制本体或拆成7部独立原作 |
| 原专题输入书目 | Madeline继续仅专题，不扩大文字输入主库例外 |
| 其他项目 | 其余35项中的31项、29项中的15项逐行列类型、来源及边界；共享RPG链接回原专题，体育、牌类、工具、合集、纯动作不自动转主库 |

新增主库内容共4个、首次发行共4条：3个原作加Crystal Chaser的2023 R版；新关联及Sorcerian增补另计，不混入主库统计。所有旧主库作品、内容、发行字段保持；Sorcerian旧对象字段及旧内容／发行保持，只追加有明确增量的记录。旧实体迁移基线不改。

## 逐作证据与判定

- **Proserpia**：[PC-88作品资料](https://www.gamepres.org/pc88/library/1988/1988_3.html)明确1988年3月、全部操作使用数字小键盘、预设行动逐场景推进、战斗开始后自动结算，不需练级／积累金钱／绘制地图。尽管目录列RPG，实际以游戏书式叙事为主，收入主库；不将自动战斗标成逐回合指令。[片尾署名转录](https://raido.moe/staff/pc88/pc88_proserpia.html)区分Brother distribution与Amorphous presented by，本次不据转录补全部正式开发工种。
- **Lonely Heart**：[8BITS条目及三张游戏画面](https://www.8-bits.info/gamelist/PC88/info/info_Hv7YSEnu46K54BGv.php)记1989年6月PC-88、Swing Soft开发／TAKERU销售。第二、第三张画面可见固定行动列表和对象子菜单；结合[剧情资料](https://www.gamepres.org/pc88/library/1989/1989_6.html)确认侦探叙事，收入主库。并未取得完整原版说明书，不宣称所有机种操作均复验。
- **Crystal Chaser**：[原作者网站](https://www.gamecorpus.com/cc-r/)明确1991-06-15 PC-9801原作、TAKERU原创委托背景、人物及2023年新增内容。[D4原版公告](https://d4e.co.jp/20170615/2506)确认原版命令操作及TAKERU专售；[2023公告](https://d4e.co.jp/20231107/4342)明确7话扩为9话、完整新章、扩充终章、新人物和幕间剧场R。2023发行署D4 Enterprise，不倒署TAKERU；2017复刻、2025同内容Switch发行不补纯平台行。
- **HAYATO**：[1987年9月资料](https://www.gamepres.org/pc88/library/1987/1987_9.html)明确四章、战国穿越、恋人救援及Hydlide式动作RPG，列跨类型关联。
- **Cosmo Saint Leaza**：[1987年12月资料](https://www.gamepres.org/pc88/library/1987/1987_12.html)明确宇宙迁居剧情、章节回访与遭遇。它亦有包装销售资料，不能称所有TAKERU项目均仅通过自贩机销售。具体移动／战斗操作尚不足，显式待核实。
- **Estland Campaign**：[1990年11月资料](https://www.gamepres.org/pc88/library/1990/1990_11.html)明确PC-88原作、父仇与公主救援。1991 MSX2版是后发线索，不新增独立作品或纯平台发行；精确战斗操作未足，保留待核实。
- **口红冒险2**：[Generation MSX逐发行资料](https://generation-msx.nl/software/jast/lipstick-adventure-2/release/1533)附MSX FAN 1990-09第108页的TAKERU专售证据。复用g755及1989原作年；不把1990渠道机种年替代原作首年。

## Sorcerian：依赖本体的真正新增剧情

[Brother官方](https://global.brother/ja/digest/history/takeru)与[Falcom授权清单](https://www.falcom.co.jp/licence/list/software.html)确认渠道追加剧本／Selected Sorcerian关系。逐包剧情与机种先后以附有操作说明书、片尾转录的资料交叉核对：

| 追加包 | 实际新增剧情 | 首次批次 |
| --- | --- | --- |
| [宇宙からの訪問者](https://tk-nz.game.coocan.jp/sorcerian/about/game_sor5.html) | 4篇剧情＋魔法道具店WIZ | 1989年6月PC-98；6月8／10日异文保留，后发PC-88的7月不当首发 |
| [Selected 1](https://tk-nz.game.coocan.jp/sorcerian/about/game_sor7.html) | 美しき花嫁、銀の灯が消えた街＋磁盘杂志 | 1989-12-08 PC-88／PC-98／X1turbo／PC-88VA同批，磁盘尺寸不拆行 |
| Selected 2 | パンドラの箱、灼熱のワナ＋磁盘杂志 | 1990-01-30 PC-98；PC-88原目录1月与逐机种2月异文保留 |
| [Gilgamesh](https://tk-nz.game.coocan.jp/sorcerian/about/game_sor6.html) | 5篇顺序剧情＋专用结局 | 1990-02-09 PC-98 |
| Selected 3 | 時の神殿、呪われた遺跡＋磁盘杂志 | 1990-04-12 PC-98 |
| Selected 4 | 闇に消えた女神、妖夢幻伝説＋磁盘杂志 | 1990-05-24 PC-98；PC-88逐机种资料为6月 |
| Selected 5 | それゆけ！ドトーのトライアスロン、封印＋磁盘杂志 | 1990-07-13 PC-98 |

开发分工、授权、监督与销售不互相替代。不把2008普通复刻、2010合集或非首次批次的移植扩成新内容。

## 保留的具体缺口

本次完成指定清单的目录对应，不宣称所有项目已达到主库证据要求。Réserve操作及1992新增遭遇、Hero Syndrome的完整操作、Genesis同名身份／年份、Algarna／AIZA／Gage／Dungeon Ace的叙事主次与首发、Gakuen Toshi Z的Striker原作和TAKERU具体发行、Hydlide 3 Special的内容差异等，在参考行保留限制；不由ADV／RPG标签自动准入。Cyber Fight据同期目录补为ACT，Hero Syndrome据剧情资料补为悬疑ADV，但操作未核不转主库。1994业务移交仍待同期原件。

## 验证与发布

数据、实体、生成一致性与全部仓库测试按AGENTS.md执行。发布前复核远程main及差异，向同一目标仓库提交、合并并验证Pages。实际检查与发布结果在完成后补记，不用本文件中的计划代替上线结果。

### 本次发布前实际检查

- 主库数据、内容关系、实体与正式职责校验通过。
- Python全量354项：312项通过，42项历史快照测试因既有缺失对象按仓库机制跳过；无失败。
- Node全量242项全部通过。
- 三个生成器一致性、差异空白检查及TAKERU／Sorcerian页面本地链接与锚点检查通过。
- 组织证据台账、沿革事件与关系边保持；旧主库对象与迁移基线逐对象保持。旧初版页面的4卡片断言改读当次发布快照，当前12卡片、65行及跨专题引用另有现行回归；没有删除旧身份或证据断言。
