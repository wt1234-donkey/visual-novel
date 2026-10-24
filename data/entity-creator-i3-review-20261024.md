# A—Z 创作登记 I3：Infocom—Innocent Grey（2026-10-24）

接续 [I2](entity-creator-i2-review-20261024.md)，按左侧顺序核 I 第 8—10 项，I 累计 10／13，A—I 累计 129／132；下一家 Interchannel。逐条证据及未解决范围见[结构化 I3 审核](entity-creator-i3-review-20261024.json)。

| 主体 | 判断、证据缺口 | 最小修正及文件 |
| --- | --- | --- |
| Infocom | **《Zork I–III》家用机商业版原作制作可直接确认。** [微软、Xbox、Activision的源代码公告](https://opensource.microsoft.com/blog/2025/11/20/preserving-code-that-shaped-generations-zork-i-ii-and-iii-go-open-source/)明确Infocom团队将早期大型机作品拆成三部，并公开[原始代码归档](https://github.com/historicalsource/zork1)。`g002/g062/g063` 的现有主库身份是1980—1982年的商业版；早期大型机原作不能据此当成同一作品。其余经典游戏、Infocomics、两部原公司RPG以及后期品牌／系列的创作，需要逐作原版职员表或代码、及原公司结束后的时序证据；仅有发行署名不能覆盖这些范围。 | 在 `data/entity-creator-i3-review-20261024.json` 独立登记3条 `originalProduction`，生成到 `data/credits.json` 及页面；旧 `publisher` 保留。`infocom` 专题的三部既有卡片增加原作制作角色，其余职责待核与后期系列维持原状；`data/games.json` 不改。 |
| Infogrames | **2002—2003年美国法人身份可直接确认。** [2002年当事方《Men in Black II》新闻稿转录](https://www.nintendoworldreport.com/news/7774/mib-2-alien-escape-escapes-to-gamecube)署 `Infogrames, Inc.`，且开发为 Melbourne House；[《Unreal II》同期官网FAQ归档](https://greatemerald.eu/lostsites/unreal2/faq.html)署 Legend Entertainment 创作及 Infogrames, Inc. 制造／营销。[公司向 SEC 申报](https://www.sec.gov/Archives/edgar/data/1002607/000095012306002721/y17768e10vkza.htm)确认该美国法人于2003年改名 Atari, Inc.。新闻稿还列法国母公司及另一美国子公司为不同法人；不能把同名后起品牌并入。`Unreal II` 各地区首版署名仍可用原包装进一步核定。 | 对既有 `entity-name-c8ec85da2361` 独立订正 `unknown`→`company`，维持两作旧发行与其专题待核。无新增Infogrames开发，不添加法人家族边或改写历史发行；变更进入主体派生索引与组织页。 |
| Innocent Grey | **11部既有制作品牌职责直接沿用。** [品牌官方当年产品页](https://www.gungnir.co.jp/innocentgrey/products/pro_caucasus/cc_index.html)及[《天之少女》制作册](https://www.gungnir.co.jp/innocentgrey/products/pro_shell3/dl/kara3_pamp01.pdf)说明品牌项目与具体职员；[Gungnir权利说明](https://www.gungnir.co.jp/innocentgrey/copyright.html)不能逐作替代该品牌署名。后发主机移植与跨地区发行仍需逐版本证据。 | `g233`—`g243` 已有 `productionBrand` 保持，不重复新增；无母公司逐作程序开发的推断。专题、原始发行、主体关系不改。 |

这批只添加独立审核、3条限定原作制作、一项历史公司身份及派生索引／组织页。主库作品、内容版本、平台发行、旧署名、主体关系和迁移基线均不改。
