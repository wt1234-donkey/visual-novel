# A—Z 创作登记 C1：Cabbage Soft—CFK（2026-10-23）

C 字母已核查 5／18，A—Z 累计47／60；下一家Chunsoft。按左侧英文名称顺序复核五家：两项主体身份订正，两条限定原作的制作品牌职责。当前进度表示已进行证据分流，并非所有历史职责完成核定。

| 主体 | 分类与证据缺口 | 最小修正 |
| --- | --- | --- |
| Cabbage Soft（きゃべつそふと） | [官方首作规格](https://cabbage-soft.com/products/hoshikoi/product/)明确品牌，[现产品页](https://cabbage-soft.com/products/jna/)沿用；既有专题的8部`productionBrand`已登记。国际版与主机后发版的逐项开发须职员表。 | 保留现有品牌、8部创作和各平台发行，不重复添加。 |
| CAPCOM | [公司沿革](https://www.capcom.co.jp/ir/english/company/history.html)与[系列数据](https://www.capcom.co.jp/ir/business/salesdata.html)确认公司及《逆转裁判》《Breath of Fire》系列，但原有`g049/g172/g173/g182/square-bof`是发行署名；逐作首版开发仍需职员表或具名制作资料。 | 继续沿用已核公司身份；不从系列所有权和发行批量推断开发。 |
| Caramel Box（キャラメルBOX） | [HOBIBOX官方活动资料](https://product.hobibox.net/chara1_2017oct/)以品牌名列产品；[《シャマナシャマナ》](https://w.atwiki.jp/ercr/pages/1257.html)和[《処女はお姉さまに恋してる》](https://w.atwiki.jp/ercr/pages/1258.html)的首版职员转录均明确“製作：キャラメルBOX”，同时把HOBIBOX、Nitro+列为协力。其他作品及品牌经营沿革待核。 | 独立JSON订正`entity-name-53ec4c5b9afc`的`unknown`→`brand`并保留发行角色；只给`g639/g640`追加`productionBrand`。 |
| Carry Lab（キャリーラボ） | [D4当时発売メーカー目录](https://d4e.co.jp/lights_cat/carry_lab)明确列《スターライトアドベンチャー》，[权利继承说明](https://d4e.co.jp/20190304/2946)介绍历史公司及移植业务；仍需原版人员名单确认`g103`和旧专题3项的制作分工。 | 保留公司身份、发行与3项专题职责待核；D4现存权利不倒填早期开发。 |
| CFK | [官方公司介绍](https://www.cfk.kr/Company/company_list?lang=en)列游戏发行与本地化，[官方法律告知](https://www.cfk.kr/News/news_view?news_seq=1374)使用“주식회사 CFK”；既有五部作品仅是后发版本发行，需逐版制作人员资料。 | 独立JSON订正`entity-name-431d2fb7a95c`的`unknown`→`company`；原作GAINAX及其他版本关系不变。 |

修改独立审核记录、生成器和派生主体／组织索引；`games.json`、`company-coverage.json`、旧发行原文、关系、内容／发行ID和迁移基线不变。下一轮从Chunsoft继续。
