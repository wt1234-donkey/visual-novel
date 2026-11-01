# 基础作品身份库：多来源目录与分批补录规则（2026-11-01）

本流程只追加到 \`data/main-adv-rpg-works-20261031.json\` 基础身份层。不会把目录条目直接写入 \`data/games.json\`，也不会自动认定作品质量、创作者、发行职责或内容版本。

## 已接入来源

| 来源 | 批次 | 原始标识与字段 | 使用范围与限制 |
| --- | --- | --- | --- |
| [NextMoe v2 catalog](https://developer.nextmoe.dev/docs/v2/listCatalogWorks) | 第14、16批 | NextMoe ID、VNDB ID、题名、别名、日期 | 仅 galgame + VNDB identity；第16批改用 rating_bangumi 排序，寻找不同目录排序下的新增记录 |
| [VNDB Kana API](https://api.vndb.org/kana) | 第15批 | VNDB vID、title/alttitle/aliases/released | 独立来源；遵守 [VNDB 数据许可](https://vndb.org/d17) |
| [Bangumi v0 Subjects API](https://github.com/bangumi/server/blob/master/openapi/v0.yaml) | 第17批 | Bangumi subject ID、name/name_cn、date、tags、platform | type=4、cat=4001 普通游戏；只纳入明确标注 ADV/VN/互动小说或 RPG 的作品，排除软件、扩展包、桌游类别 |
| [MobyGames API](https://www.mobygames.com/info/api/) | 待接入 | Game ID、题名、平台、首发年份 | 需要 API key；申请并接入前不声称已采集 |
| [IGDB API](https://api-docs.igdb.com/) | 待接入 | Game ID、name、first_release_date、version_parent | 需要 Twitch 客户端认证；须区分原作、版本、重制和 DLC |

## 第16批：NextMoe alternate ranking

- 使用 NextMoe 官方 v2 \`/catalog/works\` 列表接口，采用 \`sort=rating_bangumi\`，与此前的 \`rating_vndb\` 排序互补。
- 仅接受 medium=galgame、明确 VNDB ID、已发行且有日期的条目。
- 使用 NextMoe ID、VNDB ID、NFKC 标题/别名和年份对主库、专题、补充库及此前批次去重。
- 每批最多新增500部；不足500时保留实际数量，不降低门槛。
- API 按官方文档采用 page/limit，limit=100，遵守匿名请求速率和每日配额。

## 第17批：Bangumi game directory

- 使用 Bangumi 官方 v0 \`GET /v0/subjects\`，参数 \`type=4&cat=4001&sort=rank\`；每页50条。
- ADV/VN：优先要求 VN、视觉小说、Galgame、文字冒险、互动小说、乙女等明确标签；一般 ADV/AVG 标签只有在没有明显动作主导标签，或同时存在剧情、叙事、悬疑、推理等叙事标记时才纳入。
- RPG：要求 JRPG/CRPG/SRPG/DRPG 等偏叙事子类型，或同时存在明确剧情/叙事标记；单独的泛 RPG 标签不足以入库。
- AAVG、ARPG、ACT、FPS、RTS、平台跳跃等动作/玩法主导标签不会单独触发收录；只有同时有明确叙事证据时才可能作为基础候选。
- 条目类型 category 4001 为普通游戏；不从软件、DLC/扩展包、桌游类别导入。
- 名称优先采用 name_cn，保留 name 为别名；年份取 Bangumi date 的年份；标签原样保存在 sourceTags 供后续复核。
- 仅记录目录来源与触发筛选的 matchedSourceTags，不把 Bangumi 社区标签解释为已经完成“叙事为主、玩法为辅”的人工评估。基础候选仍需后续人工筛选叙事主次；本轮的严格标签门槛用于排除明显动作/策略/沙盒误收。
- 使用 subject ID、标题/别名、年份与全库交叉去重；重制、fan disc、合集等身份不明的条目暂缓。
- 遵守官方 API 的 User-Agent 和合理请求间隔。

## 入库规则

1. 每批独立审计文件保存扫描量、新增量、重复量、年份冲突和暂缓原因。
2. 不因凑足500而降低独立作品身份、年份、别名和来源门槛。
3. 相同外部 ID 不可跨批重复；标题/别名同年匹配视为已有身份，年份冲突进入待核队列。
4. 基础身份记录只用于发现和检索。进入精选叙事库或严格 \`games.json\` 仍需单独核查首发、版本、平台和创作关系。
5. 第16/17批执行脚本：\`scripts/import_basic_multisource_r16_r17_20261101.py\`；CI 工作流负责真实 API 导入、审计和回归测试。
