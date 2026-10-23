# A—Z 创作登记 E3：Enterbrain—EXNOA（2026-10-24）

按组织与沿革左侧英文排序核 E 字母第 9—13 项，E 累计 13／13、A—Z 累计 83／83；下一家 F&C。这里的“已核”只表示已检查主体及本批关联资料，不表示名下全部作品均有创作证据。

| 主体 | 分类、证据与缺口 | 最小修正 |
| --- | --- | --- |
| Enterbrain（エンターブレイン） | **公司身份可直接确认，具体创作需补来源**：[KADOKAWA 2013 年吸收合并议案](https://group.kadokawa.co.jp/documents/topics/20130531sstt59th.pdf)明确“株式会社エンターブレイン”为同期法人；[《True Love Story 3》PS2 片尾转录](https://raido.moe/staff/ps2/ps2_true_love_story_3.html)及[《Summer Days, and yet...》片尾转录](https://raido.moe/staff/ps2/ps2_true_love_story_summer.html)列具体人员及 GameCRAB 分工，目前不足以给 Enterbrain 添加开发职责。需制作合同、片尾中的主体制作署名或同期官方说明。 | 在独立记录中订正 `entity-name-059d1b76bb62` 为 `company/sourceReviewed`；2001/2003 两项发行、别名、关系保留，2013 年合并后的品牌形态不倒填。 |
| ENTERGRAM | **现有公司身份已核，44 条具体职责需补来源**：[公司概要](https://www.entergram.co.jp/corporate.html)与[招聘资料](https://www.entergram.co.jp/recruit/)支持其软件开发业务、自有引擎；但不能由整体业绩把旧 PC 原作或每项主机移植自动计作公司创作。需逐作版本片尾或官方开发说明。 | 保留 `entity-entergram` 公司档案和 44 条发行署名；本批不加作品创作。 |
| EXAMU | **一项专题关联作品的共同开发可直接确认**：[Nitroplus 街机作品页](https://www.nitroplus.co.jp/works/other-game)写明与エクサム共同开发且列 EXAMU Inc.；[主机作品页](https://www.nitroplus.co.jp/works/consumer-game)将 PS3/PS4 版列为移植版、Marvelous 发行。后者的具体移植开发仍需独立署名。 | 独立订正 `entity-name-49d0968e137f` 为公司，给 `nitroplus-extra-blasterz` 的专题关联作品加 `coDeveloper` 一条；不增主库制作，不改既有街机发行和主机发行。 |
| EXNOA（DG REMAKE） | **组合署名暂不宜判为单一主体，移植开发需补来源**：[EXNOA 官方公告](https://dmmgames.co.jp/news/detail/id=1786)分别指明运营公司和 DG REMAKE 品牌，并介绍《同級生リメイクCSver》；当前两条主机发行署名不足以证明移植程序、美术等具体工序，亦不能追认 1992 年原作开发。需主机版片尾及分清法人／品牌的证据。 | `entity-name-b06c3e4e3ae1` 保留 `unknown/unresolved` 与组合原文；两条发行不变，不拆并主体或增创作。 |
| EXNOA（DMM GAMES） | **组合署名暂不宜判为单一主体，专题创作需补来源**：[EXNOA 公告](https://dmmgames.co.jp/news/detail/id=1562)和[运营公司页面](https://dmmgames.co.jp/)可分辨公司与 DMM GAMES 运营品牌；《我が姫君に栄冠をクライマックス》的具体制作仍须片尾或项目方说明。 | `entity-name-5f2bf730e86e` 保留 `unknown/unresolved` 和专题发行原文；不并入既有 DMM GAMES 品牌，不增创作。 |

事实订正和追加职责位于独立 JSON 审核记录。生成器据此更新主体、职责、页面索引；主库 `data/games.json`、专题原始档案、原有发行职责、既有组织关系及迁移基线均保持原值。EXAMU 的新增纪录仅在“专题关联”显示。
