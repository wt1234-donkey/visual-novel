# 第132、133批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 132 | 87 | 0 | 76 | 0 | 11 | 0 |
| 133 | 3061 | 388 | 500 | 42 | 2131 | 0 |

## 50条暂存处理

VNDB输入50条、NextMoe输入0条；本轮从旧暂存入选50条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：64,896 → 65,472。

## 新续采位置

- VNDB：`v70336`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNak0wT1RFeGZR`
- IFDB：`10527`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共42条原始记录，按来源ID合并为42个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v68360 | Smile | 2026 | vndb-v3288 (2010) | ambiguous-name-year | [133: 229370 / held[0]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 疑似版本/依赖内容 | vndb:v68516 | Hitomishiri Demo Yaru Toki wa Ru! | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [133: 229521 / held[1]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | vndb:v68551 | RED | 2014 | nextmoe-14623 (1992) | ambiguous-name-year | [133: 229551 / held[2]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | vndb:v68609 | Utsusemi | 2010 | vndb-v7455 (1999) | ambiguous-name-year | [133: 229606 / held[3]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | vndb:v68631 | angel lover | 2026 | vndb-v40132 (2021) | ambiguous-name-year | [133: 229628 / held[4]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | vndb:v68739 | Welcome Home | 2026 | vndb-v23823 (2017) | ambiguous-name-year | [133: 229727 / held[5]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | vndb:v68872 | Hakoniwa | 2026 | nextmoe-3859 (2025) | ambiguous-name-year | [133: 229850 / held[6]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | vndb:v68904 | Cosmo's | 2026 | vndb-v17320 (2013) | ambiguous-name-year | [133: 229878 / held[7]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:h607dian8ba3hl8k | Waiting for Sunrise | 2021-05-08 01:00:00 | vndb-v5989 (2008) | name-year-conflict | [133: h607dian8ba3hl8k / held[8]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:6964n5qgmmiuv38g | Little Bird | 2014-05-13 01:00:00 | vndb-v45056 (2015) | name-year-conflict | [133: 6964n5qgmmiuv38g / held[9]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:5f43nlp696voabh4 | Awake | 2018-10-01 01:00:00 | ifdb-4qack3kx5ndignqj (2016) | name-year-conflict | [133: 5f43nlp696voabh4 / held[10]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:guzdbb81uv4n5za8 | Library | 2013-01-16 01:00:00 | ifdb-1f34jxoy8kbwdhdf (1991) | name-year-conflict | [133: guzdbb81uv4n5za8 / held[11]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:ns6228q9cj6px93t | Unpolished | 2015-01-01 00:00:00 | vndb-v13527 (2010) | name-year-conflict | [133: ns6228q9cj6px93t / held[12]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:4o26t9v42vx58sk1 | Flat | 2013-08-22 01:00:00 | ifdb-jte5k6kzfpms24a7 (2002) | name-year-conflict | [133: 4o26t9v42vx58sk1 / held[13]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:7y7du3y8zp7cee1q | One way out | 2017-10-01 01:00:00 | ifdb-gavscrrdvmg0eswo (2013) | name-year-conflict | [133: 7y7du3y8zp7cee1q / held[14]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:syzr310ah3qvk0oj | A Kiss from Death | 2021-07-01 01:00:00 | vndb-v27824 (2019); vndb-v43579 (2023) | name-year-conflict | [133: syzr310ah3qvk0oj / held[15]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:1l81g6qu4azjb0oq | Rock, Paper, Scissors! | 2022-01-01 00:00:00 | vndb-v68785 (2024) | name-year-conflict | [133: 1l81g6qu4azjb0oq / held[16]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:ovllat5e4g78824i | Lost | 2024-10-22 01:00:00 | vndb-v14352 (2013) | name-year-conflict | [133: ovllat5e4g78824i / held[17]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:giz7n4w3t8jz7al9 | The School of Death | 2013-08-07 01:00:00 | ifdb-bigjia6sq9vvgvtd (1984) | name-year-conflict | [133: giz7n4w3t8jz7al9 / held[18]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:nvhty4brxsc2ltoc | Buried | 2014-04-20 01:00:00 | vndb-v19753 (2016) | name-year-conflict | [133: nvhty4brxsc2ltoc / held[19]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:htl42xh4515qz4me | Gemini | 2014-01-01 00:00:00 | vndb-v2493 (2004) | name-year-conflict | [133: htl42xh4515qz4me / held[20]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:1615ilxrgpvu9c0c | Good Bones | 2024-01-01 00:00:00 | vndb-v47886 (2023) | name-year-conflict | [133: 1615ilxrgpvu9c0c / held[21]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:xk3balqbbisgoo35 | Dreamland | 2018-10-01 01:00:00 | ifdb-bnvzf6d0czmbk5ps (2003); nextmoe-37228 (2022) | name-year-conflict | [133: xk3balqbbisgoo35 / held[22]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:tavsi1xg32e71l7r | Wasteland | 2012-07-17 01:00:00 | vndb-v51747 (2024) | name-year-conflict | [133: tavsi1xg32e71l7r / held[23]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:saz1t56or902kqss | La fuga | 2017-02-02 01:00:00 | ifdb-e7o5hgek1x836kj1 (1990) | name-year-conflict | [133: saz1t56or902kqss / held[24]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:ukpvbo3cosmgkp5o | The Raven | 2014-11-17 01:00:00 | vndb-v38864 (2021) | name-year-conflict | [133: ukpvbo3cosmgkp5o / held[25]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:t3863cqfh8e3pq0u | Just Another Day | 2017-01-07 01:00:00 | ifdb-v7ms9cucablj20qk (2010) | name-year-conflict | [133: t3863cqfh8e3pq0u / held[26]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:idpz0h62kfhoiujd | petrichor | 2025-06-30 01:00:00 | nextmoe-1622 (2020) | name-year-conflict | [133: idpz0h62kfhoiujd / held[27]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:swjbhi7m9827di8c | Red | 2018-01-06 01:00:00 | nextmoe-14623 (1992) | name-year-conflict | [133: swjbhi7m9827di8c / held[28]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:cbq5wqbxd17krwdn | Starlight | 2013-03-26 01:00:00 | vndb-v1318 (2007) | name-year-conflict | [133: cbq5wqbxd17krwdn / held[29]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:28jqcftg9h5qj0x7 | salvage. | 2023-04-08 01:00:00 | ifdb-v87g98ga9jj1snow (1985) | name-year-conflict | [133: 28jqcftg9h5qj0x7 / held[30]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:djp38ld4pqzvap81 | Moonlight Walks | 2015-01-01 00:00:00 | vndb-v1452 (2005) | name-year-conflict | [133: djp38ld4pqzvap81 / held[31]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:n44doao8v14lddjv | Heroes! | 2021-04-02 01:00:00 | ifdb-j1uj9pygpuw3v9pc (2001) | name-year-conflict | [133: n44doao8v14lddjv / held[32]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:f33gznhn1553t6nw | Halloween | 2014-01-01 00:00:00 | ifdb-a1c82gyqjqiv2ogo (2020) | name-year-conflict | [133: f33gznhn1553t6nw / held[33]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:lahve83e5uleyrqk | Luna | 2021-05-25 01:00:00 | vndb-v63387 (2025) | name-year-conflict | [133: lahve83e5uleyrqk / held[34]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:mmgvldyw2sojbmi6 | Escape | 2013-09-28 01:00:00 | nextmoe-7725 (2015) | name-year-conflict | [133: mmgvldyw2sojbmi6 / held[35]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:jb3ex3jq1hwm3c5d | Double/Cross | 2015-07-03 01:00:00 | vndb-v32291 (2013) | name-year-conflict | [133: jb3ex3jq1hwm3c5d / held[36]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:wj7vrxythsmc7dmz | The Library | 2014-09-28 01:00:00 | ifdb-myt9vkrn185f9csm (2021) | name-year-conflict | [133: wj7vrxythsmc7dmz / held[37]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:26vu0i3vowbovhc1 | Two | 2013-04-06 01:00:00 | vndb-v62655 (2004) | name-year-conflict | [133: 26vu0i3vowbovhc1 / held[38]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:wm0pstatnqbv7tc3 | Colditz | 2010-01-01 00:00:00 | ifdb-3qsmch8qwejoziyf (1984) | name-year-conflict | [133: wm0pstatnqbv7tc3 / held[39]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:odt16gwamrxnzc93 | Inheritance | 2013-04-15 01:00:00 | vndb-v27875 (2018) | name-year-conflict | [133: odt16gwamrxnzc93 / held[40]](nextmoe-ifdb-bulk-review-20261102-r133.json) |
| 名称/年份/身份冲突 | ifdb:f99kibzl2391pe02 | Out | 2019-10-01 01:00:00 | vndb-v64747 (2026) | name-year-conflict | [133: f99kibzl2391pe02 / held[41]](nextmoe-ifdb-bulk-review-20261102-r133.json) |

## NextMoe 连续批次有效产出评估

下表仅统计NextMoe实时扫描，不混入IFDB档案扫描和旧暂存。入选不等于扫描候选总数。

| 批次 | NextMoe扫描 | 新合格候选 | 合格率 | 最终选中NextMoe | IFDB补录 | 主要排除原因 |
|---|---:|---:|---:|---:|---:|---|
| 129 | 2500 | 6 | 0.24% | 6 | 494 | invalid-medium-or-source-id: 2463, reused-external-identity: 29, name-year-conflict-held: 1 |
| 131 | 2500 | 0 | 0.00% | 0 | 500 | missing-name-year-or-unreleased: 1386, reused-external-identity: 754, invalid-medium-or-source-id: 331 |
| 133 | 2500 | 0 | 0.00% | 0 | 500 | invalid-medium-or-source-id: 2016, reused-external-identity: 361, missing-name-year-or-unreleased: 115 |

注意：合格率指可进入候选池的比例，不是网站总作品质量评价。若NextMoe连续低产出，后续可调整扫描窗口或减少无效扫描，但不能跳过来源去重及历史游标。


## 原始证据

- [第132批审计](vndb-kana-bulk-review-20261102-r132.json)
- [第133批审计](nextmoe-ifdb-bulk-review-20261102-r133.json)
- [两批汇总](basic-r132-r133-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
