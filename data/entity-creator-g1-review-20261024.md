# A—Z 创作登记 G1：G-MODE—GameBank（2026-10-24）

依组织与沿革左侧英文字母顺序核 G 第 1—5 项。G 累计 5／13，A—Z 累计 99／107，下一家 General Products。已核主体不表示全部关联作品均已证实创作。

| 主体 | 核查分类、原始证据及缺口 | 最小修正 |
| --- | --- | --- |
| G-MODE | **法人身份可直接确认；1984 原作制作不成立。**[公司资料](https://gmodecorp.com/company)和[当事方 2024 年公告](https://prtimes.jp/main/html/rd/p/000000744.000001474.html)署株式会社ジー・モード；库内 `g012-v3/v4` 原文 `G-MODE` 只指 2024 年《オホーツクに消ゆ》重制发行。公告把重制共同开发署给旧版制作人员与 room6，并提及 2024 年新故事。需可限于 `g012-c-3` 的内容层审定记录与各参与者具体分工，不能由发行或版权推公司为 1984 原作开发。 | 独立订正 `entity-name-9eb4e4c25db9` 为 `company/sourceReviewed`；保留旧发行两行，不新增作品级创作。 |
| GAINA | **既有法人沿革可直接确认；游戏创作暂无记录。**[母公司公告](https://prtimes.jp/main/html/rd/p/000000004.000147544.html)明确原株式会社ガイナ于 2025 年更名 BENTEN Film、与原 GAINAX 不同。既有专题目前零主库、零关联游戏；如有游戏制作主张须原始发行、片尾及具体法人署名。 | 保留 `entity-gaina`、旧名、日期及独立专题，不把 GAINAX 的 15 部已核作品迁入，也不由动画创作推定游戏职责。 |
| GAINAX | **既有原作制作记录可直接维持；其余专题职责需补来源。**现有 15 部主库制作记录已经独立登记；[D4 权利物清单](https://d4e.co.jp/lights_cat/gainax)按当时发行厂家列早期游戏，[TinMachine 授权作品页](https://tinmachine.co.jp/eva_gainax/evangelion.html)说明部分 EVA 游戏为授权。五项未核专题关联与后续不同开发商的游戏仍需逐作片尾、企划／开发声明。 | 保留 `entity-gainax` 和 15 部已登记原作制作、授权及监修角色；不将系列游戏或 GAINA、米子 GAINAX 归成本社创作。 |
| Game Arts | **公司身份及一项专题关联原作制作可确认。**[Game Arts 沿革](https://www.gamearts.co.jp/ja/company/history_of_corp.html)载 1985 年公司设立、PC 开发起点与 1987 年《Zeliard》；[原版产品页](https://www.gamearts.co.jp/ja/products/pc-zeliard.html)列发行日与 ©1987 GAME ARTS；[游戏保存协会初期作品展与前代表讲演](https://www.gamepres.org/2022/07/23/exhibition2019-miyaji/)可交叉确认其原作系列。库内 `sierra-on-line-zeliard-v-original` 原文 `Game Arts`；Sierra DOS 版逐版移植工序仍须单独片尾。 | 订正 `entity-name-acf6175f07fb` 为公司，并仅给现有 **related** 作品 `sierra-on-line-zeliard` 加一条 `originalProduction`，不提高收录位置、不将 Sierra 发行并入该身份。 |
| GameBank（ゲームバンク） | **1990 年代法人身份可确认，具体发行及移植职责仍需补证。**[文化厅媒体艺术数据库](https://mediaarts-db.artmuseums.go.jp/id/C45030)列游戏バンク株式会社为 1995 年创设、1998 年终止的责任主体；[1997 年同期业界报道](https://pc.watch.impress.co.jp/docs/article/970106/gamebank.htm)以该法人为联络方。库内 `g831-v7` 的 `ゲームバンク` Windows 95 署名当前仅引[维基条目](https://ja.wikipedia.org/wiki/卒業II_〜Neo_Generation〜)；需 1996 年包装或同期销售表和移植片尾。2015 年出现同名新法人，不能追溯合并。 | 独立订正 `entity-name-b8429ea71808` 为 `company/sourceReviewed`；原始发行与别名不变，不加原作／Windows 移植开发，也不建立未经核定的企业继承关系。 |

本批三项身份订正和一条限定于专题关联作品的原作制作，均有独立 [JSON 审核记录](entity-creator-g1-review-20261024.json)。`data/games.json`、历史发行、实体关系及迁移基线保持原样。
