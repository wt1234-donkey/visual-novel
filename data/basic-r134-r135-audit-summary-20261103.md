# 第134、135批：IFDB与PC-98历史目录补录

本轮不请求VNDB或NextMoe。PC-98先核对原始年份与别名，合格身份均分两批；余下名额由IFDB补足。

| 批次 | PC-98新增 | IFDB扫描 | IFDB去重复用 | IFDB隔离 | IFDB新增 | 总新增 |
|---|---:|---:|---:|---:|---:|---:|
| 134 | 4 | 551 | 17 | 38 | 496 | 500 |
| 135 | 4 | 540 | 19 | 25 | 496 | 500 |

基础身份库：65,472 → 66,472。两批各500，合计1000。

## PC-98目录逐条审核

两份目录共1892条原始记录；经目录交叉核对、原作年证据和全库别名检查，新增8个作品身份。原始目录记录数不当作独立作品数。

| 处理状态 | 原始记录数 |
|---|---:|
| missing-year-held | 2 |
| name-year-or-multiple-identity-held | 110 |
| needs-primary-year-and-alias-review | 448 |
| outside-narrative-adv-rpg-scope | 540 |
| possible-edition-or-dependent-content-held | 6 |
| reused-title-alias-and-year | 768 |
| reviewed-alias-reuse | 2 |
| reviewed-candidate | 16 |

两份目录的全部逐条结果见[PC-98目录审计](pc98-catalogue-audit-20261103.json)。待核项保留原始标题、目录ID和年份，不作为已合格暂存或新增数。

| 本次PC-98新增作品 | 原作年 | 证据 |
|---|---:|---|
| サバッシュ | 1988 | [来源](https://www.gamepres.org/catalog/?id=8811001892004) |
| エメラルドドラゴン | 1989 | [来源](https://www.gamepres.org/pc88/library/bashou.html) |
| ヴェインドリーム | 1991 | [来源](https://www.gamepres.org/catalog/?id=8811000924003) |
| 黒の剣 | 1995 | [来源](https://www.gamepres.org/catalog/?id=8811006777009) |
| ラストハルマゲドン | 1988 | [来源](https://www.gamepres.org/pc88/library/1988/1988_7.htm) |
| スパン・オブ・ドリーム | 1990 | [来源](https://www.gamepres.org/catalog/?id=8811000480004) |
| ティラム バラム | 1992 | [来源](https://www.gamepres.org/catalog/?id=8811006863009) |
| ダークセラフィム | 1995 | [来源](https://d4e.co.jp/20251118/4904) |

## IFDB续采位置

固定档案SHA-256：`0f7909470d03f4235e49637e492ca1c31ad7e0558a61bdd07fced1cb128a935b`；筛选截止日期继续使用2026-11-02，排序不变。

起点：10527；第134批后：11078；第135批后：11618。

本轮IFDB无已合格剩余暂存；PC-98待核项目独立保留，不能用未核年份或平台移植凑数。

## IFDB名称／年份／身份隔离清单

| 批次 | IFDB来源ID | 标题 | 来源日期 | 匹配已有身份及年份 |
|---|---|---|---|---|
| 134 | rzlf56h622r8w2is | Thief | 2014-01-10 01:00:00 | ifdb-fkx54zuwiaycx81n (1989) |
| 134 | 3kfuoe9vqb00rr04 | Rain | 2014-12-06 01:00:00 | vndb-v17316 (2013); vndb-v66955 (2009) |
| 134 | v966lgn8f6p1vco1 | Timeless | 2019-05-11 01:00:00 | vndb-v15008 (2014) |
| 134 | omahluwlcfwtonf5 | Ashes to Ashes | 2026-04-24 01:00:00 | vndb-v43894 (2023) |
| 134 | oupagfdahyj8it4m | First Contact | 2024-09-01 01:00:00 | vndb-v32017 (2019) |
| 134 | qbvd79sdy6510222 | En la Oscuridad | 2025-10-31 01:00:00 | ifdb-4ondzpua8avfc2zq (2017) |
| 134 | z31hsbzaj6fi1sjt | Forest | 2013-04-21 01:00:00 | g1373 (2004); supp26-liar (2004) |
| 134 | y77pe2aa1xis4vsu | Actual Sunlight | 2013-01-03 01:00:00 | vndb-v32333 (2012) |
| 134 | 0az5jyuxu4cb5wqz | Brimstone | 2021-02-14 01:00:00 | ifdb-lcxift6r9krwfppu (1985) |
| 134 | ieyfhsulc5t646oi | Wake Up | 2014-08-11 01:00:00 | ifdb-ivjms7ovf1k39bsz (2024) |
| 134 | ifekmpd0cflkp9r8 | Dream Walker | 2021-01-01 00:00:00 | vndb-v41625 (2023) |
| 134 | mwk8wtkl7ffuc0p1 | Wild West | 2025-06-29 01:00:00 | vndb-v6052 (2012); vndb-v61313 (2022) |
| 134 | vyaotcscx55b2bp5 | A Pocketful of Snow | 2024-01-01 01:00:00 | vndb-v48985 (2023) |
| 134 | dcwntqqwkqmfg4wk | Distance | 2016-12-18 01:00:00 | vndb-v2582 (2009) |
| 134 | cd81k42054qn3fb2 | OBJECT PERMANENCE | 2023-10-30 01:00:00 | ifdb-g4m1oc36cli8h3xz (2018) |
| 134 | jw038svg64f2id6u | Lex | 2014-09-22 01:00:00 | vndb-v25109 (1993) |
| 134 | znv32e75b1vq66p7 | Train | 2015-03-15 01:00:00 | vndb-v11536 (2011) |
| 134 | ayr1uwdv5fyk5jtk | Stars | 2016-02-14 01:00:00 | vndb-v9097 (1997) |
| 134 | d7szlmhriopknd1y | Roar | 2024-10-31 01:00:00 | vndb-v26437 (2019) |
| 134 | 8hdtgidxze1lqpyw | Devotion | 2024-07-15 01:00:00 | g1414 (2019); ifdb-9lzmypxgtirgznc7 (2020); supp26-redcandle-devotion (2019) |
| 134 | xcivytjt1v64qx3t | Emergence | 2024-01-15 01:00:00 | vndb-v54915 (2025) |
| 134 | 2aiwz2wvcrhc5dcp | Egress | 2017-03-29 01:00:00 | vndb-v46230 (2023) |
| 134 | z38s3iz6z9g4rdlq | Moon Base | 2017-10-01 01:00:00 | ifdb-fs7ufjowq87ure7q (2002) |
| 134 | m6ie50ktfmr54pm1 | Blind | 2011-10-01 01:00:00 | vndb-v12138 (2012); vndb-v62745 (2020) |
| 134 | qfawv15gf50ev8yb | Castle Adventure! | 2012-09-30 01:00:00 | ifdb-mz7tsvrsrrqhddhw (1984) |
| 134 | 73f3ukavvju219ct | Carpe Diem | 2024-08-15 01:00:00 | vndb-v11629 (2011) |
| 134 | jz2q7uk4gp0zx2ph | Oxygen | 2010-10-01 01:00:00 | ifdb-po9fvo4krznzdtmg (2015) |
| 134 | 93qzblhr0iyaxdqw | Quest for the Holy Grail | 2012-01-01 00:00:00 | ifdb-qhjomh8hnpptdwf0 (1983) |
| 134 | 7khuz6omlar7qy1p | La fuite | 2022-06-24 01:00:00 | ifdb-pwaei4pgdhfjxgyo (2021) |
| 134 | r2y6iry1bz5lkpht | Invasion | 2015-10-31 01:00:00 | vndb-v42683 (2023) |
| 134 | etm8us6qmr1nwmqe | Bed Time | 2012-03-24 01:00:00 | nextmoe-20241 (2015) |
| 134 | pla4h5k2l4btls1m | Between Two Worlds | 2024-11-07 01:00:00 | nextmoe-38390 (2025) |
| 134 | ckzokgsmxbun6kxl | My ████████ Angel | 2025-06-28 01:00:00 | vndb-v43321 (2023) |
| 134 | 3ddzh19s52rk17o3 | Dragon | 2012-04-03 01:00:00 | ifdb-x3wcrapu08ztd061 (2000) |
| 134 | ggn1wjt8g651dvlv | The Tempest | 2021-07-29 01:00:00 | ifdb-59g5czw7izz7aoip (1992) |
| 134 | d6zapb4on77355l4 | Recurrent | 2024-08-16 01:00:00 | vndb-v23688 (2018) |
| 134 | 9bz4qwb0uhrjph4m | Full Circle | 2012-08-21 01:00:00 | vndb-v7575 (2009) |
| 134 | gk546rivj65wt8gp | lighthouse | 2018-04-27 01:00:00 | vndb-v50244 (2024) |
| 135 | hvo2w5vurqm17lok | Labyrinth | 2012-12-22 01:00:00 | ifdb-5czip2mqeves47ot (2020) |
| 135 | nlxpufnjcpdx655r | The Village | 2019-10-31 01:00:00 | ifdb-mvwyqmpgy1jhb0vc (1985) |
| 135 | 35yqdqy3ennlte69 | Life On Mars? | 2014-01-10 01:00:00 | vndb-v52066 (2026) |
| 135 | vp5xvfqvycyz2q3r | Animalia | 2018-10-01 01:00:00 | vndb-v47453 (2023) |
| 135 | si39ri8ng9bqimv1 | A Clean Getaway | 2024-06-01 01:00:00 | ifdb-orssyc3rn54mrg97 (2023) |
| 135 | 4lbwojdld1g77r9l | Eleanor | 2021-04-02 01:00:00 | vndb-v26227 (2018) |
| 135 | zud3a0c8kk2aftut | The Haunting | 2013-03-19 01:00:00 | ifdb-j67hoxr1aomlwnxn (1991) |
| 135 | z8treod1ut9qve51 | Darkness | 2019-04-04 01:00:00 | ifdb-zll159j3yve208xq (2004) |
| 135 | 7ujhd623jpnizadb | Monster | 2023-03-07 01:00:00 | vndb-v51448 (2024) |
| 135 | ofwxv117k3by2v4u | Inventory | 2015-01-01 00:00:00 | ifdb-j0yvxmp7vn1yzw4z (2008) |
| 135 | ickkqi4gvjksm01b | Time Trip | 2012-10-18 01:00:00 | ifdb-sp0g7h17eusswcxv (2020) |
| 135 | 9d7xtzmoc92goueb | Falling | 2017-01-01 00:00:00 | nextmoe-22551 (2014) |
| 135 | hrtcwrqty0w5mp56 | Rivals | 2020-09-20 01:00:00 | vndb-v9273 (2010) |
| 135 | wxmgen6pniwlbdap | The Commute | 2025-01-01 00:00:00 | ifdb-m0g5oijhy0b6hkkk (1998) |
| 135 | gqnj52jfaxomve5a | Through Time | 2014-04-09 01:00:00 | ifdb-f3k74ovanhhjs3j6 (2009) |
| 135 | d4br0muwsvpvnb8c | Advent | 2017-12-01 01:00:00 | vndb-v27604 (1996) |
| 135 | 6gb2luc912w5hx6z | Still Life | 2019-12-16 01:00:00 | vndb-v12785 (2013) |
| 135 | qn6zav7hfitml558 | Karen | 2013-10-20 01:00:00 | vndb-v62416 (2010); vndb-v983 (2003) |
| 135 | 48cq99jqwr57hkp9 | Dark Carnival | 2013-09-24 01:00:00 | vndb-v12829 (2008) |
| 135 | l8tr8m9tlkgix1sk | Detritus | 2025-09-01 01:00:00 | vndb-v39332 (2021) |
| 135 | rkbxfdmie302zb8v | Last Valentine's Day | 2023-10-01 01:00:00 | vndb-v48577 (2013) |
| 135 | m97opgqgfozvi89i | Murder at the Manor | 2018-10-01 01:00:00 | ifdb-xjymmpdlzs2eugjk (1983) |
| 135 | yj7sm4drbpqv1hpa | Tea Party | 2011-01-01 00:00:00 | vndb-v14154 (2007) |
| 135 | xw3b58v76zzuny75 | Door | 2023-09-29 01:00:00 | ifdb-xuyokgskcsqq2vxm (2008) |
| 135 | q6v604a5iz69jddq | Wake Up | 2018-10-31 01:00:00 | ifdb-ivjms7ovf1k39bsz (2024) |

## 验证范围

全库包含基础身份、完整主库、创作者补充与专题关联；检查来源ID、大小写不敏感IFID、标题／别名、显式中日英合写名称及两批之间的重复。
已有对象、内容版本、平台发行、正式职责及旧批次保持不变。测试与PR／Pages实际状态另见工作流，不预先声明发布成功。
