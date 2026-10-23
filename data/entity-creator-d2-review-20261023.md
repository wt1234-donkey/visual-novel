# A—Z 创作登记 D2：Digital Leisure—DMM GAMES／AUGUST（2026-10-23）

按组织与沿革左侧英文顺序核查 D 字母第 5—8 项，D 累计 8／10，A—Z 累计 68／70；下一家 Double Fine Productions。已审核进度不等于把发行或平台署名登记为创作。

| 主体 | 核查结论与证据缺口 | 最小修正 |
| --- | --- | --- |
| Digital Leisure | **可直接确认身份**：[公司官网](https://digitalleisure.com/company/)自述 Digital Leisure Inc. 于 1997 年成立，为游戏开发及发行公司；[《Dragon’s Lair》20 周年版手册](https://mocagh.org/miscgame/dragonslair20th-manual.pdf)保留后发版署名。1983 年街机原版早于此公司，复刻移植的具体人员与职责须另查该版片尾。 | 独立订正 `entity-name-bbf1e79f8c9f` 为公司，保留 `g010-v2` 发行；不增加 1983 原版开发。 |
| Digiturbo（デジターボ） | **可直接确认身份**：[Nitroplus 官方沿革](https://www.nitroplus.co.jp/company/history/)列 1997 年有限会社デジターボ、2000 年株式会社化、2016 年更名コンテライド、2024 年并入 Nitroplus；[Phantom 旧版](https://nitro-origin.com/game/phantom/archives/)及 [DRAMAtical Murder re:code](https://www.nitrochiral.com/game/dramatical_murder_recode.php)分别保留当时署名。逐版移植／原版创作职责仍需包装及片尾。 | 独立订正 `entity-name-32b13af88204` 为历史公司；保留 3 条旧发行，既有实体和关系 ID 不合并、不倒填原版开发。 |
| DMM GAMES | **可直接确认对外身份；法人映射需逐版来源**：[EXNOA 业务说明](https://dmmgames.co.jp/business/)明确运营 DMM GAMES 平台；[官方商号变更公告](https://dmmgames.co.jp/news/detail/id=210)记载合同会社DMM GAMES 在 2020-04-10 更名 EXNOA。`g037-v2` 与 Nitroplus 专题共 11 条旧发行的具体发行法人、各版本实际研发单位尚不能仅凭对外署名判定。 | 将 `entity-name-2ddaddfb96a5` 核定为对外品牌／平台名称并显式保留原 `publisher` 职责；不合并同名旧法人、EXNOA 或 Shiravune，不新增开发。 |
| DMM GAMES／AUGUST | **暂不宜判断复合身份**：[AUGUST 产品目录](https://august-soft.com/product)称双方合作，[官方历史访谈](https://august-soft.com/20th/history/)说明 AUGUST 负责世界观、剧本、角色，DMM 一方承担游戏系统。现有 `entity-august` 的 `coDeveloper` 有单独证据；两条复合发行署名不是一个可核实法人。仍需原始片尾、服务条款和各版本合同或公告核定各自发行主体及技术团队。 | 保留 `entity-name-16c097f224f4` 待核及 `august-rpg-imys-v1/v2` 原文，不拆分旧署名，不建立斜线关系。 |

本批仅在独立审核 JSON 中记录三项身份事实订正，`creditAdditions` 为空。`games.json`、`company-coverage.json`、`credits.json`、旧实体 ID／组织关系和迁移基线不变。
