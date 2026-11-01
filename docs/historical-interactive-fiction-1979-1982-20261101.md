# 1979—1982年欧美文字冒险与早期商业互动小说补录（2026-11-01）

基础身份库：10,840 → 10,842；17部输入候选中，新建身份 2 部，关联已有身份 13 部，候选待核 2 部。另有附加年份冲突及范围待核提示 5 条，不计入17部候选的互斥去向。

## 年份口径

firstYear按最早可核的商业发行/正式发行年份记录。开发起始、首次可玩、公开传播、同期杂志刊载和后续平台移植分别写入证据说明；不将不同阶段混成一个首发日期。

## 已审阅作品

| 作品 | 年份 | 历史范围 | 类型 | 平台线索 | 来源 |
|---|---:|---|---|---|---|
| Golden Voyage | 1981 | core-interactive-fiction | 文字冒险（两词解析器） | TRS-80 | [档案/资料](https://www.bbcmicro.co.uk/game.php?id=1717) |
| Dungeon Adventure | 1982 | core-interactive-fiction | 文字冒险（解析器） | BBC Micro、Nascom | [档案/资料](https://bbcmicro.co.uk/game.php?id=1735) |

## 年份与版本核验说明

- **Golden Voyage（1981）**：BBC Micro Games Archive明确说明该作品最初于1981年为TRS-80发行，并指出1981年9月杂志广告；同期SoftSide 1981年9月广告宣布Adventure #12 Golden Voyage，TRS-80软件手册目录亦将Adventure 12列为1981年。1984年BBC Micro移植不作为原作首发年份。
- **Dungeon Adventure（1982）**：BBC Micro Games Archive称原始磁带版于1982年发行，列Mike、Nick、Pete Austin；英国计算机历史中心亦列1982年BBC Micro版本。

## 已有身份关联（未重复新增）

- Zork I: The Great Underground Empire：匹配已有身份 g002（1980）
- Zork II: The Wizard of Frobozz：匹配已有身份 g062（1981）
- Zork III: The Dungeon Master：匹配已有身份 g063（1982）
- Deadline：匹配已有身份 g003（1982）
- Starcross：匹配已有身份 g064（1982）
- Ghost Town：匹配已有身份 ai-ghost-town（1980）
- Savage Island, Part I：匹配已有身份 ai-savage-island-1（1980）
- Savage Island, Part II：匹配已有身份 ai-savage-island-2（1981）
- Mystery House：匹配已有身份 g001（1980）
- The Wizard and the Princess：匹配已有身份 g057（1980）
- Cranston Manor：匹配已有身份 g058（1981）
- Time Zone：匹配已有身份 g059（1982）
- The Hobbit：匹配已有身份 g113（1982）

## 自动去重或年份冲突待核

- **Colossal Adventure**：馆藏资料存在1982/1983年份冲突，暂缓入库。
- **Adventure Quest**：Level 9馆藏资料列1983年，留待下一批。
- **Other Venture系列**：需要逐款核实作品身份、作者和发行年份。
- **Ghost Town**：additional alias matches a different year; same-year identity linked but conflict retained
- **The Wizard and the Princess**：additional alias matches a different year; same-year identity linked but conflict retained
- **Mission: Asteroid**：title/alias exists with a different firstYear
- **Ulysses and the Golden Fleece**：年份来源冲突：Sierra年表列1982年，另有二手资料列1981年；未取得足以排除冲突的一手发行证据，本批暂不写入基础身份库。

## 人工范围排除

- **Colossal Adventure**：年份存在冲突，暂不强行入库。
- **Adventure Quest / Snowball / Lords of Time**：主要资料列1983年，超出本批范围。

## 分类原则

- 本批同时收录纯文字解析器作品与图文结合冒险，两者玩法分别标注。
- Infocom、Adventure International、Sierra、Level 9和Melbourne House按作品身份分别记录。
- Zork I、II、III是独立商业续作，MIT大型机原作仍保持1977年身份。
- 分章续作仅在独立销售且具独立内容时单独建立身份。
- 争议年份作品暂缓，不为追求数量强行定年。
- 原始发行与后续平台移植分开记录。

## 自动验证与上线

导入脚本保留导入前全部作品对象哈希，并逐条复核新增记录；重复执行不会重复追加。GitHub Actions运行数据/实体校验、Python和Node回归测试后，将审计文件、报告和基础身份库生成结果提交到本PR分支。只有检查通过且合并到main后，才视为正式上线。

## 本批暂缓

- **Colossal Adventure**：馆藏资料存在1982/1983年份冲突，暂缓入库。
- **Adventure Quest**：Level 9馆藏资料列1983年，留待下一批。
- **Other Venture系列**：需要逐款核实作品身份、作者和发行年份。
