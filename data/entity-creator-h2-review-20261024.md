# A—Z 创作登记 H2：Hudson Soft—Human（2026-10-24）

按组织与沿革左侧排序连续核 H 第 6—10 项。H 累计 10／12，A—H 已核 117／119；下一家 HummingBird Soft。作品的制作品牌和具体程序、脚本承制人员不是同一个字段；原始发行和历史身份均保留。

| 主体 | 证据判断、原始署名与缺口 | 最小修正及文件 |
| --- | --- | --- |
| Hudson Soft（ハドソンソフト） | **公司身份可直接维持；三条专题开发职责需补原始来源。** [SEC同期集团资料](https://www.sec.gov/Archives/edgar/data/1191141/000119312505073349/d6k.htm)支持既有法人档案。[《デゼニワールド》保存实物目录](https://www.gamepres.org/catalog/?cat=1&id=8811000648008&nav=brand)确认1985年Hudson发行，所存[同期杂志文字](https://www.gamepres.org/pc88/library/1985/1985_12.html)记载两名Hudson人员前期取材；还需原版片尾或制作署名来判定公司承担的实际开发工序。专题《オリエンタルブルー》和《Miami Law》亦缺该层证据，后者北美发行署名属于Hudson Entertainment。 | `entity-hudson`的70条旧发行和三个`pendingRole`保留；本批不将发行、版权、取材或子公司关系转换成整部原作开发。 |
| HULOTTE | **十部主品牌作品的品牌制作可直接确认；具体承制另核。** [品牌首作公告](https://hulotte.jp/pc/archives/44)由HULOTTE工作人员称《With Ribbon》为新品牌作品；[官方产品目录](https://hulotte.jp/pc/products)与十部作品各自官网对应`g843`、`g853`、`g844—g849`、`g851—g852`，含《With Ribbon》附属短篇。既有`originalPublishingBrand`只表示首发署名；主机移植及国际版发行仍依原版本。`g850`另署HULOTTE ROI，HULOTTE专题的母品牌职责缺具体共同制作证据。 | 审核JSON逐作追加十条`productionBrand`，在`data/credits.json`及组织索引呈现主品牌制作；旧发行、关系和`g850`母品牌`pendingRole`均不改。 |
| HULOTTE ROI | **一部子品牌制作可直接确认。** [当事方官网](https://hulotte.jp/product/kokoro/)的规格表把《ココロのカタチとイロとオト》品牌署为HULOTTE ROI，[公告](https://hulotte.jp/pc/archives/2731)称其为出道作。官网列独立原画、脚本与音乐署名，不能推出母品牌直接编写或独自完成全部开发。 | 仅给`entity-hulotte_roi`的`g850`追加一条`productionBrand`；既有`brandFamily`仍不主张准确起止，不把作品上推到`entity-hulotte`。 |
| HUMAN | **历史发行公司类别可核；两种字形的对象同一性暂不合并。** [HuneX原项目表](https://www.hunex.co.jp/archives/works/ps1)明确`g916-v2`的発売元是`HUMAN`、版权`©1998 HuneX`；[Sunsoft权利方说明](https://prtimes.jp/main/html/rd/p/000000024.000029510.html)确认同期存在ヒューマン株式会社。HuneX的制作与PC-FX版NEC发行各自独立，需PS原盒确认HUMAN法律全称。 | 在本批独立记录`entity-name-53708cc2d758`为`company/sourceReviewed`；保留大写`HUMAN`发行原文，暂不合并下一行小写Human节点或新增作品制作。 |
| Human（ヒューマン） | **历史法人类别可核；《クロックタワー2》逐作开发需补源。** [Sunsoft当事方公告](https://prtimes.jp/main/html/rd/p/000000024.000029510.html)明确1995年首作由ヒューマン株式会社发行，却把现代复刻的移植／新要素指给WayForward和Limited Run Games；库内`g1015-v1`的`ヒューマン`署名[现据二手PS索引](https://psxdatacenter.com/games/J/C/SLPS-00657.html)，需1996原盒和片尾。 | 独立订正`entity-name-4f1d0851948b`为`company/sourceReviewed`，不把1995首作或2024复刻职责转到1996续作，不调整既有对象合并关系。 |

全部身份订正及十一条逐作品牌制作见[H2结构化审核记录](entity-creator-h2-review-20261024.json)。本批仅修改增量审核输入并重建派生索引、组织和专题页面；`data/games.json`、既有发行、原关系与迁移基线保持原样。
