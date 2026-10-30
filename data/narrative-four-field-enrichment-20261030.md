# 四项叙事编目补录与遗留问题审计（2026-10-30）

此轮对当前主库269部未完成四项叙事编目的作品展开证据审查。字段包括叙事定位、剧情风格、故事题材、叙事结构。

## 原始统计与更新后的结果

| 指标 | 修改前 | 本轮补充 | 修改后 |
|---|---:|---:|---:|
| 四项已完成的作品 | 1318 | +101 | 1419 |
| 部分完成的作品 | 20 | +6 | 26 |
| 四项全空的作品 | 249 | -107 | 142 |
| 至少一项未完成的作品 | 269 | -101 | 168 |

| 尚缺字段 | 修改前 | 已补字段 | 修改后 |
|---|---:|---:|---:|
| 叙事定位 | 249 | 107 | 142 |
| 剧情风格 | 266 | 107 | 159 |
| 故事题材 | 256 | 107 | 149 |
| 叙事结构 | 255 | 101 | 154 |

## 本轮证据范围

- 72部：首批18组厂商补录的逐作品剧情简介。补录依据严格限定为主库中具名作品的既有 synopsis，保留原 source；未将继承链接视为重新外核。
- 35部：本轮逐作品核实了官方内容介绍，涵盖Rusty Lake、Wadjet Eye Games、Supermassive Games、Night School Studio、Half Mermaid、Simogo。
- 六部没有叙事结构充分依据的作品，保留结构缺项与需要补证的问题说明，不从互动选项或游戏类型推定多结局。
- 原8部历史编目保持不变；原21部特别缺证作品保持原有缺项。主库作品、发行和创作身份未改写。

## 具名官方证据样例

- **Rusty Lake: Roots**：官方介绍James Vanderboom种下特殊种子后家族命运改变，玩家通过生命树解锁后代肖像；另有33关官方流程标题。 [官方资料](https://www.rustylake.com/adventure-games/rusty-lake-roots.html)
- **Cube Escape: Paradox**：官方产品页确认侦探Dale困在两种宇宙、以解谜找回记忆；游戏电影联动，含两章和多个结局。 [官方资料](https://www.rustylake.com/room-escape-games/cube-escape-paradox.html)
- **The Past Within**：官方新闻资料明确玩家一人在过去、一人在未来，透过各自所见合作解谜，调查Albert Vanderboom的计划。官方产品另注明两章。 [官方资料](https://press.rustylake.com/sheet.php?p=The+Past+Within)
- **Underground Blossom**：官方游戏页指出七座地铁站分别象征Laura Vanderboom的人生、记忆和可能的未来。 [官方资料](https://www.rustylake.com/adventure-games/underground-blossom.html)
- **The Blackwell Legacy**：官方游戏页写明Rosa继承媒介身份，Joey幽灵成为伙伴，第一案调查大学发生的一连串自杀。 [官方资料](https://wadjeteyegames.com/games/blackwell-legacy/)
- **Unavowed**：官方游戏页列明主角曾受恶魔附身、加入Unavowed，并注明3种主角前史及分支故事。 [官方资料](https://wadjeteyegames.com/games/unavowed/)
- **Old Skies**：官方页介绍Fia Quinn为ChronoZen机构监管七名历史旅游客人，故事经过七个时代并涉及时间解谜。 [官方资料](https://wadjeteyegames.com/games/old-skies/)
- **Until Dawn**：官方介绍八名朋友困于山中度假地，互动决定人物能否生存，故事动态适应玩家选择。 [官方资料](https://www.supermassivegames.com/games/until-dawn)
- **The Quarry**：官方介绍九名营地辅导员被困并遇袭，每个决定决定关系、剧情与人物生死。 [官方资料](https://www.supermassivegames.com/games/the-quarry)
- **OXENFREE**：官方描述Alex带继弟前往Edwards Island聚会，意外打开幽灵裂隙，并强调对话选项影响朋友关系和事件走向。 [官方资料](https://nightschoolstudio.com/oxenfree/)
- **IMMORTALITY**：官方资料确认女演员Marissa Marcel主演三部未上映电影后失踪；作品以追查其电影资料展开。 [官方资料](https://halfmermaid.co/stories)
- **DEVICE 6**：官方说明Anna在岛上城堡醒来后失忆，游戏由六章以文字为地图的故事组成，文字结构反映位置及行进。 [官方资料](https://simogo.com/work/device-6/)

## 尚未解决的部分

- 旧档案：21部，部分早期作品需要说明书、剧情原文或可验证实玩流程。
- 首批18组：6部仅缺结构组织证据。
- Frontwing、Navel、CIRCUS、GIGA、KeroQ/Makura、light新增作品：87部原简介为占位内容，不能由品牌归属推断剧情。
- 最近推荐作品：54部尚待逐一获取独立官方故事介绍。

以上合计168部仍有至少一项缺失。

## 复核规则

只从具名作品材料归纳叙事事件、人物视点、章节或叙事目标；不得因存在选项推定多路线，也不得因公司或类型推定剧情风格。每个新增字段由独立的 fieldEvidence 保存 basis、sources、evidenceText 和 sourceFields。

验证：scripts/validate_narrative_editorial.py、tests/test_narrative_editorial.py，以及全库的Python/Node和实体关系测试。
