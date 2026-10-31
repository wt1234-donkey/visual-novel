# 基础作品身份库：目录来源与分批补录规则（2026-11-01）

这份文档只涉及基础身份层 `data/main-adv-rpg-works-20261031.json`，不修改 `data/games.json`、内容版本、平台发行或精选作品评价。

| 来源 | 用途与接入状态 | 原始标识与字段 | 限制 |
| --- | --- | --- | --- |
| [NextMoe v2 catalog](https://api.nextmoe.dev/v2/catalog/works) | 已接入，至第十四批 | NextMoe ID + VNDB ID，题名、别名、公开发行日期 | 必须满足 released、独立条目、明确 VNDB ID；排除版本混合与合集 |
| [VNDB Kana API](https://api.vndb.org/kana) | 第十五批新增独立直连来源 | VNDB vID、title/alttitle/aliases/released | 仅确认 VN 层作品身份；日期可能只有年/月；遵守 [VNDB 数据许可](https://vndb.org/d17) |
| [Bangumi API](https://bangumi.github.io/api/) | 下一阶段候选，尚未导入 | subject ID、名称、名称译名、日期、类别 | 只取游戏类型条目；需要确认每个条目是原作、移植、合集还是影视衍生 |
| [MobyGames API](https://www.mobygames.com/info/api/) | 下一阶段待接入 | game ID、原始作品名、首发年份、平台 | 需要 API key；谨防平台发行重复计为作品 |
| [IGDB](https://api-docs.igdb.com/) | 下一阶段待接入 | game ID、name、first_release_date、version_parent | 需要 Twitch 客户端认证；须严格区分 version/remake/DLC |

## 第十四、十五批

- 第十四批继续 NextMoe，并按既有源 ID、VNDB ID、NFKC 标题和别名、年份检查。
- 第十五批从 VNDB 原生 API 获取新的作品身份，避免只依赖 NextMoe 评分排序的目录覆盖范围。
- 每批最多 500 部，实际入库以在线导入产生的独立审计 JSON 和 GitHub Actions 校验结果为准；不能因数量不足而降低去重门槛。
- 来源/年份冲突、DLC、体验版、合集、重制、fan disc 以及独立性不明确的项目进入待审计队列，不以新的作品 ID 强行收录。
- 不同目录的同一 VNDB ID 必须视作同一作品身份，不能跨来源重复建档。原始目录的名称和年不代表创作者职责、剧情、游戏品质或首次发行版次已经核实。
- `scripts/import_basic_multisource_r14_r15_20261101.py` 执行批次；`.github/workflows/basic-multisource-r14-r15-20261101.yml` 负责校验、审计和自动提交到功能分支。
- 两个批次产生独立审计文件，合并进主库前须核对实际新增数和测试结果。

## 下一阶段来源扩张

先做 Bangumi（中文、日文别名补漏）与 MobyGames（欧美 ADV、互动叙事及早期 PC 游戏）的候选映射与跨目录去重；需要认证的目录不抓取未经许可的页面，不伪造来源字段。新增条目须来源可追溯，未核实内容不进入精选叙事作品库。
