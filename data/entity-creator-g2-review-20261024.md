# A—Z 创作登记 G2：General Products—Good Navigate（2026-10-24）

依组织与沿革左侧英文字母顺序核 G 第 6—10 项。G 累计 10／13，A—Z 累计 104／107，下一家 Good Smile Company。已核主体不表示所有关联作品均已证实创作。

| 主体 | 分类、原始署名与证据缺口 | 最小修正及文件 |
| --- | --- | --- |
| General Products | **需要补充来源，法人／品牌身份暂不宜判断。** `gainax-dennou1/2/3-v2` 三条历史发行的原文均为 `General Products`，依据 [MAME 磁盘清单](https://github.com/mamedev/mame/blob/master/hash/pc8801_flop.xml)；[收藏实物图录](https://retroblues.sakura.ne.jp/regeokiba/gainax/gainax.htm)将 GAINAX 列制作、GENERAL PRODUCTS 列销售。同名旧店、后来的官方商店及法人主体不能靠名称合并；需同期包装、版权页及企业登记，逐版确认发行合同。 | `entity-name-0956fc2c3ad0` 保留 `unknown/unresolved` 与三条发行署名；只在本批审核文件记录疑点，不增加开发作品。 |
| GeneX | **法人身份可直接确认；部分发行需要补充来源。** [2003 年同期报道](https://game.watch.impress.co.jp/docs/20031228/pm.htm)直称株式会社ジェネックス；库中 `g823-v1/v2/v3` 原署 `GeneX`。2006 年 Windows 版，[Game Watch](https://game.watch.impress.co.jp/docs/20060615/pm4.htm)写 GeneX 发行，[4Gamer](https://www.4gamer.net/games/031/G003193/20060615171838/)写 CyberFront，需原盒及版权页核对发行／分销分工；PSP 版需包装背面原文。 | 在 `data/entity-creator-g2-review-20261024.json` 订正 `entity-name-6ce5a7f6ac91` 为 `company/sourceReviewed`，生成 `data/entities.json`；保持 `data/credits.json` 及原始发行不变，不由发行补开发。 |
| GeneX（ジェネックス） | **法人身份可直接确认；三版具体署名需要补充来源。** [同期法名称呼](https://game.watch.impress.co.jp/docs/20031228/pm.htm)及 [2002 年《Only you》PS2 发行通知](https://game.watch.impress.co.jp/docs/digest/200209.htm)的ジェネックス官网产品链接支持企业身份。`alicesoft-extra-onlyyou-v3/v4/v5` 的原署名 `GeneX（ジェネックス）` 仅引[私家目录](https://alicecottage1989.blog.jp/archives/37863815.html)，需各版原盒及片尾；AliceSoft 的 Windows 原作与 PS2 移植分开。 | 独立订正 `entity-name-f7fd3e45b4ae` 为 `company/sourceReviewed`；保留双语 ID 与另一 GeneX ID，不自动合并关系，不登记原作开发。 |
| GigasDrop. | **品牌身份可直接确认；开发仍待核。** [Nitroplus 2011 年当事方消息](https://www.nitroplus.co.jp/news/2011/2613.php)称其为 MAGES. 的 PC 游戏品牌，并明确该日发行 `g631-v1`；需要原片尾和经营沿革时段才能断言开发与历史归属。 | 独立订正 `entity-name-c30e25476da0` 为 `brand/sourceReviewed`，设置 `preserveReleaseRoles`；既有 `publisher` 行保持，暂不添 `operatedBy` 时间关系和创作职责。 |
| Good Navigate（グッドナビゲイト） | **法人身份及 PS2 发行可直接确认；移植开发需要补充来源。** [F&C 官方商品页](https://fandc.co.jp/catalog/consumer/800)列 `g735-v4` 原署 `グッドナビゲイト` 为 2009 年 PS2 发售元；[2005 年同期报道](https://game.watch.impress.co.jp/docs/20050308/io.htm)直称株式会社グッドナビゲイト、将 GNソフトウェア称其游戏品牌。原作 `g735-v1` 则为 Cocktail Soft 的 2008 年 Windows 版；需 PS2 版片尾核移植者。 | 独立订正 `entity-name-4671824b3a8c` 为 `company/sourceReviewed`；不将 PS2 发行归为 Windows 原作制作，也不重写品牌关系。 |

本批四项身份订正、零条创作新增均记录在 [JSON 审核批次](entity-creator-g2-review-20261024.json)。生成器从独立记录重建 `data/entities.json`、`data/organizations.json` 及展示页面；`data/games.json`、历史发行、既有关系、迁移基线均不改。
