# A—Z 创作登记第六批：AUGUST—Azarashi Soft（2026-10-23）

## 范围与结论

本批按英文字母顺序核查 A 字母最后两个主体，累计完成 **32／32** 个，下一家为 **Bandai Namco Games**。本批不新增作品层职责：AUGUST 的既有品牌档案和《爱丽丝秘迹》限定联合制作沿用前批证据；Azarashi Soft 仅将身份从 `unknown` 订正为 `brand`。

## 可直接确认

| 主体 | 结论 | 依据与最小修正 |
| --- | --- | --- |
| AUGUST | 既有品牌与限定联合制作记录可确认 | [AUGUST产品目录](https://august-soft.com/product)与[20周年年表](https://august-soft.com/20th/history/)支撑现有品牌档案；[DMM GAMES作品页](https://games.dmm.com/detail/imys)再次确认 AUGUST×DMM GAMES 的合作。仅完成队列登记，不重复追加 `coDeveloper`；DMM GAMES／AUGUST 复合发行署名、系统开发和运营分工保持原值。 |
| Azarashi Soft（あざらしそふと） | 品牌身份可确认 | [官方首页](https://azarashi-soft.nexton-net.jp/)与[官方说明](https://azarashi-soft.nexton-net.jp/top_sp.html)明确使用品牌语境；版权提示同时列出株式会社ネクストン及あざらしそふと。[HOOKSOFT历史页](https://www.hook-net.jp/htm/old_news/old_news_2019.htm)确认与SMEE的联合企划。最小修正是将既有稳定ID的 `type` 改为 `brand`、补充来源和审计备注，不改 g377 的原始联合发行职责。 |

## 需要补充来源

| 主体 | 当前缺口 | 最小修正方案 |
| --- | --- | --- |
| Azarashi Soft（あざらしそふと） | 官方版权页能确认品牌与株式会社ネクストン并列，但没有本轮可用的历史法人登记、经营起止或逐作开发分工证据。 | 暂不建立Nexton母公司关系，不批量新增 `originalProduction`／`developer`；后续取得公司沿革或作品原始职员表后，再对单项职责单独记证。 |
| AUGUST | DMM GAMES各时期法律主体、运营与发行责任仍需时期证据。 | 保留 `DMM GAMES／AUGUST` 复合署名和前批限定合作记录，不拆分或回填未证实关系。 |

## 暂不宜判断

- 不把 Azarashi Soft 与 Nexton 的版权并列自动扩展为无时间范围的母公司—品牌关系。
- 不把 `あざらしそふと / SMEE` 的联合发行署名升级为两家品牌各自独立开发，也不从品牌身份推定 g377 的系统、美术或剧本分工。
- 不把 AUGUST 的品牌目录或《爱丽丝秘迹》合作证据扩展为 DMM GAMES 复合署名的全部开发职责。
- 不改主库作品、内容版本、平台发行、既有组织关系或专题位置；本批没有新增 credit。

## 文件与审计

- 独立证据记录：`data/entity-creator-a6-review-20261023.json`、本文。
- 生成规则：`scripts/build_entity_model.py` 读取本批审核 JSON；`scripts/build_organizations.py` 将 A 字母完成度与下一家 Bandai Namco Games 写入组织与沿革索引。
- 既有关系与迁移基线保持不变；唯一身份订正为 `entity-name-a7f6066af4b9` 的品牌层级，发行职责继续保留原始来源。
