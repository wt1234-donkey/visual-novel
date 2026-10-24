# A—Z 创作登记 F1：F&C—FG REMAKE（2026-10-24）

按组织与沿革左侧英文排序核 F 字母第 1—5 项，F 累计 5／11，A—Z 累计 88／94；下一家 Firebird。已核查主体不代表其所有关联作品均已证实创作。

| 主体 | 分类、证据与缺口 | 最小修正 |
| --- | --- | --- |
| F&C | **既有公司身份可直接确认；逐作创作需补来源**：[F&C 企业页](https://fandc.co.jp/extra/corporate)载设立于 1997 年、游戏软件企划／开发／销售及代表系列，但目录中 Cocktail Soft、FairyTale、FC01／FC03 等分品牌署名的具体工序、1997 年之前原作与后发版本不能由集团清单一概归属公司。需各作当期片尾／制作团队与法人分工。 | 保留 `entity-fandc` 公司档案和既有家族关系；不增公司作品职责，亦不吸收子品牌记录。 |
| F&C・FC03 | **品牌身份可直接确认，2000 年原作创作不归于 DVD 品牌**：[2001 DVD 版](https://fandc.co.jp/catalog/pc/754)和[2003 廉价版](https://fandc.co.jp/catalog/pc/631)官方资料均列“ブランド：F&C・FC03”；[DreamSoft 当事方沿革](https://fandc.co.jp/dreamsoft/about.html)称 2001 年春由此名义起步，同时明确其法人继续存续。《Natural2 -DUO-》2000 年原版另署 FairyTale。需 DVD 增补内容的团队及品牌／法人具体时段。 | 独立订正 `entity-name-d8351a6222ea` 为 `brand/sourceReviewed`，显式保留两条旧 release 的 `publisher` 角色、原文、关系，不给 `g777` 补原作制作。 |
| FANZA GAMES（DG REMAKE） | **组合身份暂不宜判断；旧来源存在版本错配**：`g046-v2` 是 2021 年 PC 发行，但其当前来源为[EXNOA 2023 年《CSver》公告](https://dmmgames.co.jp/news/detail/id=1786)，只明确 2024 年主机版的 DG REMAKE 运营。同期[2021 年 PC 商品页](https://a.sofmap.com/product_detail.aspx?sku=21447788)及[发售报道](https://game.watch.impress.co.jp/docs/news/1308585.html)显示 FANZA GAMES。仍需 2021 原版包装、官方产品页或片尾判断完整署名与开发，不能把 2024 品牌倒填 2021。 | 保留 `entity-name-fdc56bbd260d` 待核、`g046-v2` 原发行及来源；把证据错配作为**单独的事实订正候选**登记，待原始依据与迁移基线审查后再修。 |
| FAVORITE | **品牌作品已登记，法人分工仍逐作限定**：[官方产品目录](https://www.favo-soft.jp/soft/product.html)与[权利说明](https://www.favo-soft.jp/soft/guideline.html)支持既有品牌目录及有限会社フェイバリット的存在；现有 14 部主库作品已经有 `productionBrand`，早期 CROSSNET 销售与后续 ENTERGRAM／dramatic create 主机发行各自保留。官网著作权声明不足以把每版制作或品牌版权同一化为法人逐作开发。 | `entity-favorite` 及 14 条已存在制作品牌不重复追加；旧发行、关系和专题位置不变。 |
| FG REMAKE | **2025 年品牌身份可直接确认，创作范围应限重制内容**：[官方作品站](https://www.fanzagames-digination.com/fgremake/nonomura_re/)和[EXNOA 原文公告转载](https://moe-gameaward.com/media/2025/05/30/20204/)明示美少女游戏品牌及《野々村病院の人々 リメイク》；本库 `g306-c-6` 是 2025 年增补内容，原版 `g306-c-original` 是 1994 年 Silky’s。现行本批审核追加仅支持作品级制作，缺能只指向 `g306-c-6` 的已审机制与具体制作职员依据。 | 独立订正 `entity-name-4bbd70f3b821` 为 `brand/sourceReviewed`，保留旧发行 `publisher` 和两版身份；不把 2025 年品牌倒填为 1994 年原作制作。 |

两项身份订正写在独立 JSON 审核记录中，均保留历史发行角色。未增加任何作品级创作职责；`data/games.json`、专题档案、既有组织关系与迁移基线不改。下一批从 Firebird 继续。
