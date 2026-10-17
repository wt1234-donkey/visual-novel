# Carry Lab（キャリーラボ）专题与补库核对

日期：2026-10-18（中国时间）。目标：**wt1234-donkey/visual-novel**。

## 收录结果

- 新建`carry_lab.html`，公司成立时间采用PC历史资料及公司目录所记**1981年5月**，不补造具体日。首页增加专题入口。
- 正文**4个作品档案**：复用旧库《星光冒险 PART 1》g103；新增《Hao君的不可思议之旅》《魔塔崩坏》2部无文字输入的动作叙事关联；新增《星光冒险II》1部仅专题输入书目。
- 4类主库新增**0部／0内容／0发行**。两部动作叙事按原有`relatedGames`结构保存，每部1个原作内容、1条FDS首次发行，共**2部／2内容／2发行**。不能把动作平台游戏伪归文字冒险或视觉小说。
- `games.json`全部1171部／1369内容／2363发行保持字节不变，旧g103不重复创建或改写。全库专题关联504→506，仅专题输入书目109→110，专题66→67。
- 末尾玩法表**59项／10组**：4行引用正文，其余为同作海外版本、纯玩法游戏、第三方移植、年份／标题异文和工具。不是59部独立已发行游戏，不宣称全球全目录或原聊天的逐字备份。

## 作品与控制依据

| 原名 | 处理 | 依据与边界 |
|---|---|---|
| スターライト・アドベンチャー PART 1 | 复用g103 | [FM馆藏](https://fm-7.com/museum/products/vjg12a36/)记1983年、Carry Lab发行、Zero Soft开发。保留旧输入标签及内容／发行对象；不把仅有Y/N等部分操作的回顾作为全平台无输入结论。 |
| スターライト・アドベンチャーⅡ | 仅专题 | [FM馆藏](https://fm-7.com/museum/products/39yynpef/)记1983；[PC目录](https://www.gamepres.org/pc88/library/carry.htm)记PC-8801于1984年2月。firstYear采用较早的馆藏年份，明确并非1984全作品首发。[图文流程](https://www5d.biglobe.ne.jp/~object/sla2clip/sla2.html)包含物品词语LEFEX应答，另有计算机命令；不只因为起名、单次口令而排除。 |
| ハオ君の不思議な旅 | 新增动作叙事关联 | [日版原厂说明书扫描](https://gamegear.net/media/canonical/console/fds/manual/hao-kun-no-fushigi-na-tabi-japan__32531.pdf)说明学徒试炼、方向移动、A跳跃、B魔法和道具；[实机流程](https://w.atwiki.jp/famicomall/pages/859.html)补充城堡、象征物与存档。无自由行动词句解析。 |
| 魔塔の崩壊 | 新增动作叙事关联 | [原厂说明书扫描页](https://cdn-ak.f.st-hatena.com/images/fotolife/j/jackallsasaki/20210929/20210929003439.jpg)及[实机控制表](https://w.atwiki.jp/famicomall/pages/815.html)记方向键、跳跃、攻击、下+B道具和SELECT菜单。救援、成长、装备和限时逃脱提供简单叙事；不推定为回合RPG，也不从音乐判断配音。 |

两部动作作品中文检索名均标**站内编辑译名**，保留日文原名。配音状态本轮没有完成录音核实，内部记`未核实`，页面不会冒称无角色配音。

## 开发、发行与版本

1. Carry Lab是开发／移植主体之一；DOG是发行品牌。Hao原始发行署名保留**Square**；魔塔保留**Pony Canyon**。魔塔说明书另有Bothtec署名，不将其替代发行公司。[GameFAQs目录](https://gamefaqs.gamespot.com/games/company/75841-carry-lab)支持1987／1988的FDS发行。
2. Hao有1987-05-01与05-11的日期异文。记录采用无争议的年份，备注保留差异；不声称已用工商或厂商原发售表消除争议。Square Enix旧档案本轮不可读，新游戏详情页只返回框架，未把空页当作日期证据。
3. **Mystery Quest（1989）**是Hao的北美NES卡带关联，发行Taxan。[美版原厂手册](https://www.thegameisafootarcade.com/wp-content/uploads/2017/02/Mystery-Quest-Game-Manual.pdf)可供内容比较，但本轮未核到符合新增规则的首次新剧情／可玩内容，故只列参考，不增第二作品／内容版／发行。
4. [Hydlide的MZ移植回顾](https://akiba-pc.watch.impress.co.jp/docs/column/retrosoft/1276312.html)确认Carry Lab参与Hydlide及II的移植，原作为**T&E SOFT**。未核MZ版本首次新增内容，不为普通移植造本社原创或发行行；两部只列关联参考。首作MZ销售与II的T&E发行区分。
5. [D4目录](https://d4e.co.jp/lights_cat/carry_lab)用于历史发行／现权利关联；其标题并不证明全部程序原始开发归属。[PC历史目录](https://www.gamepres.org/pc88/library/carry.htm)也合并Taito／Nidecom标签，表内明确原作移植。JET、BASE／WICS与Missワープロ是工具，不计游戏。
6. 早期清单中的Flight Simulator／ポリゴブロック错误对译、Snaky名称及Gaplus机种日期异文只作参考，未据其建立新身份。未定年份的小品不补造时间。

## 验证

最终更新基于远程T&E SOFT专题合并提交`f7fc669`。其新增数据全部保留；Hydlide移植关联只在本页表中引用原作归属，不重复建立T&E已有RPG身份。

按AGENTS.md运行结构校验、Python与Node既有测试、专题生成一致性检查。另比较全部旧公司与游戏对象：旧公司对象、主库文件及其他66页全部保持，只有新增Carry Lab公司、附录、互动CSV和首页入口。

上线以远程main及Pages状态为准；本文件只记录内容和验证，不以本地文件存在冒称已发布。
