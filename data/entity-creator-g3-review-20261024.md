# A—Z 创作登记 G3：Good Smile Company—GT Interactive（2026-10-24）

依组织与沿革左侧英文字母顺序核 G 第 11—13 项。G 累计 13／13，A—Z 累计 107／107，下一家 H 组 HARUKAZE。核查主体不表示所有关联游戏都由该主体制作。

| 主体 | 分类、原始署名与证据缺口 | 最小修正及文件 |
| --- | --- | --- |
| Good Smile Company | **法人身份与发行可直接确认；创作职责不能由发行推定。** [公司档案](https://corporate.goodsmile.com/en/about-en/)明列 Good Smile Company, Inc.；[Nitroplus 2021 年原作消息](https://www.nitroplus.co.jp/news/2021/11504.php)将《咲う アルスノトリア》的原作署 Nitroplus、配信署 Good Smile Company、开发／运营署 NextNinja。库内 `nitroplus-extra-arsnotoria-v1/v2` 原发行 `Good Smile Company` 保留；若要记录其更具体的创意企划，需该作项目片尾或当事方制作分工。 | `data/entity-creator-g3-review-20261024.json` 独立订正 `entity-name-7c36813da51c` 为 `company/sourceReviewed`，重建 `data/entities.json`；不新增 Good Smile 的开发作品。NextNinja 应在 N 组独立核其主体与职责。 |
| GROOVER | **品牌身份及一部原作制作品牌可直接确认；法人经营归属暂不宜判断。** 原作制作人 [bamboo 的亲历说明](https://note.com/milktub696/n/nbf8eeeb3348d)明确 2001 年《グリーングリーン》是他在 GROOVER 品牌的首个制作项目；[原版职员表转录](https://w.atwiki.jp/ercr/pages/2904.html)列 2001-10-05 发售及品牌 GROOVER。`g650-v1` 原发行原文仍是 GROOVER；`g650-v2` 则是 2013 OVERDRIVE EDITION，不能倒填为 2001 年原作方。历史公司合同、软件片尾和 2013 重制的人员分工仍需补核。 | 订正 `entity-name-4d8bc5606e40` 为 `brand/sourceReviewed`，设置 `preserveReleaseRoles`；仅对主库 `g650` 新增一条 `productionBrand` 作品职责。不自动建立 GROOVER 与其他公司／OVERDRIVE 的经营关系。 |
| GT Interactive | **历史公司身份及《Unreal》两版发行可直接确认；其他发行仍需补来源。** [《Unreal》1998 原版手册](https://oldunreal.com/guides/Unreal%20manual.pdf)将开发人员与 GT 发行制作／测试人员分列；[《Return to Na Pali》1999 手册](https://oldunreal.com/guides/Unreal%20NaPali%20Manual.pdf)明确 GT Interactive Software Corp. 发行、Legend Entertainment 另为制作主体；[同期 SEC 登记摘录](https://www.sec.gov/news/digest/1998/dig090298.pdf)佐证法人名称。`legend-entertainment-wheel-of-time-v-original` 仅由今时销售页支持原发行，`riverhill-abe-v-original` 仅由维基页支持，须各自 1990 年代包装或版权页。 | 订正 `entity-name-5bae781ea87d` 为 `company/sourceReviewed`；四条既有发行职责原样保留，不因对 Legend 的历史投资或项目管理把相关作品登记为 GT 开发。 |

本批三项身份订正、一条限定于 2001 年原作的制作品牌职责，均记入 [JSON 审核批次](entity-creator-g3-review-20261024.json)。由生成器重建实体索引及组织页面；`data/games.json`、历史发行、旧关系与迁移基线不变。
