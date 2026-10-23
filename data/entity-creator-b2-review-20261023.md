# A—Z 创作登记 B2：BLACKRAINBOW—Blizzard Entertainment（2026-10-23）

B 字母累计核查 6／10，A—Z 累计 38／42；下一家 BPS。本批按顺序核对三个主体的档案、原始平台署名与相关作品页面，仅订正两项主体类型，作品创作职责未增加。

| 主体 | 分类 | 已核证据与缺口 | 最小修正 |
| --- | --- | --- | --- |
| BLACKRAINBOW | 可直接确认品牌；原作职责需补来源 | [官方产品规格](https://blackrainbow.jp/dl/dotfuck/data.html)明确列“ブランド BLACKRAINBOW”；[《かすみ遊戯》官方DVDPG页面](https://www.blackrainbow.jp/dvdpg/006/index.html)将后发版标为BLACKRAINBOW DVDPG Division，并附Windows原版。g673的1999年原版署Purple（JAST期），2002年后发版署BLACKRAINBOW；尚需1999年原作制作与DVDPG人员名单。 | `entity-creator-b2-review-20261023.json`记旧`unknown`→`brand`，生成`entities.json`等索引；保留两条平台原始署名，不把DVDPG发行倒填为原作创作。 |
| Bliss Brain | 可直接确认既有公司及发行；具体开发需补来源 | [官方公司资料](https://blissbrain.co.jp/title/corporate/)自称游戏发行公司；[Regeneration官方页面](https://blissbrain.co.jp/pm2rg/)说明2004 Refine基础、赤井孝美重绘及米子GAINAX制作开场动画。g821的2024年Switch／Steam首批发行已登记；还缺游戏程序、企划等逐项制作职员表。 | 身份、两条发行、增补内容和米子GAINAX限定动画职责沿用原值；不从发行方身份追加游戏创作。 |
| Blizzard Entertainment | 可直接确认公司；Diablo制作职责需补来源 | [暴雪公司页面](https://www.blizzard.com/company/about/)使用Blizzard Entertainment, Inc.，[官方GOG说明](https://news.blizzard.com/en-us/article/22887361/diablo-now-available-on-gog-com)明确Hellfire不是暴雪官方产品、由其同意在GOG附赠。专题作品中Diablo原版与Sierra发行的1997年Hellfire增补已分列；逐作开发仍需同期人员名单。 | 独立JSON记旧`unknown`→`company`；维持原版暴雪发行与Hellfire的Sierra发行、内容增补关系，不新增Hellfire的暴雪开发。 |

受影响文件是独立审核JSON与本文、`scripts/build_entity_model.py`、生成的主体及页面索引，以及 `scripts/build_organizations.py` 和组织目录进度。核心 `games.json`、`company-coverage.json`、旧发行原文、主体关系、作品/内容/发行ID与迁移基线不变。品牌及公司类型只说明主体身份，不把发行记录自动算作开发作品；下一批从 BPS 继续。
