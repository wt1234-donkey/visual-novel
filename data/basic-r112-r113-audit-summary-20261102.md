# 第112、113批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 112 | 1313 | 373 | 500 | 42 | 398 | 0 |
| 113 | 1561 | 543 | 500 | 55 | 235 | 228 |

## 248条暂存处理

VNDB输入13条、NextMoe输入235条；本轮从旧暂存入选248条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：54,841 → 55,841。

## 新续采位置

- VNDB：`v58077`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVFExTmpoOQ`
- IFDB：`6954`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共97条原始记录，按来源ID合并为75个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v56780 | Love at First Bite | 2025 | vndb-v45830 (2016) | ambiguous-name-year | [112: v56780 / held[0]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v56797 | Limerence | 2025 | vndb-v37193 (2022) | ambiguous-name-year | [112: v56797 / held[1]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v56814 | The Scalper | 2025 | vndb-v16453 (1999) | ambiguous-name-year | [112: v56814 / held[2]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v56845 | Dreamland | 2025 | nextmoe-37228 (2022) | ambiguous-name-year | [112: v56845 / held[3]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v56921 | AfterParty | 2025 | g1538 (2019) | ambiguous-name-year | [112: v56921 / held[4]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57002 | Blood in the Water | 2026 | vndb-v52545 (2024) | ambiguous-name-year | [112: v57002 / held[5]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57008 | Limerence | 2024 | vndb-v37193 (2022) | ambiguous-name-year | [112: v57008 / held[6]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57066 | Lab Rats | 2025 | vndb-v46750 (2017) | ambiguous-name-year | [112: v57066 / held[7]](vndb-kana-bulk-review-20261102-r112.json) |
| 疑似版本/依赖内容 | vndb:v57107 | Ren'ai, Hajimemashite - Mini Fandisc - Summer Vacation | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [112: v57107 / held[8]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57113 | Burden of Proof | 2023 | vndb-v42279 (2018) | ambiguous-name-year | [112: v57113 / held[9]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57115 | Blind Date | 2022 | vndb-v24988 (2018) | ambiguous-name-year | [112: v57115 / held[10]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57137 | Gemini | 2024 | vndb-v2493 (2004) | ambiguous-name-year | [112: v57137 / held[11]](vndb-kana-bulk-review-20261102-r112.json) |
| 疑似版本/依赖内容 | vndb:v57154 | Smile Remaster | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [112: v57154 / held[12]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57157 | Eclipse | 2025 | vndb-v6522 (2011) | ambiguous-name-year | [112: v57157 / held[13]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57187 | Ailurophobia | 2025 | vndb-v39232 (2022) | ambiguous-name-year | [112: v57187 / held[14]](vndb-kana-bulk-review-20261102-r112.json) |
| 疑似版本/依赖内容 | vndb:v57225 | Kanmi Girls Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [112: v57225 / held[15]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57229 | Little Lamb | 2025 | vndb-v31306 (2021) | ambiguous-name-year | [112: v57229 / held[16]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57231 | Deception | 2025 | vndb-v14997 (2014) | ambiguous-name-year | [112: v57231 / held[17]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57257 | Disconnected | 2025 | vndb-v44505 (2023) | ambiguous-name-year | [112: v57257 / held[18]](vndb-kana-bulk-review-20261102-r112.json); [113: 53415 / held[0]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57357 | Seeing Red | 2024 | vndb-v32011 (2021) | ambiguous-name-year | [112: v57357 / held[19]](vndb-kana-bulk-review-20261102-r112.json); [113: 53512 / held[1]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57413 | REBOOT | 2025 | vndb-v52491 (2019) | ambiguous-name-year | [112: v57413 / held[20]](vndb-kana-bulk-review-20261102-r112.json); [113: 53565 / held[2]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57429 | Wo Buyao Yige Ren Shuijiao ya! | 2024 | ifdb-oy6ld63a47b9vn1x (1998) | ambiguous-name-year | [112: v57429 / held[21]](vndb-kana-bulk-review-20261102-r112.json); [113: 53580 / held[3]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 来源日期冲突 | vndb:v57431 | Higanbana | 2016 | vndb-v31395 (2002); vndb-v43531 (2006); NextMoe: 2015-12-31 | ambiguous-name-year; VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [112: v57431 / held[22]](vndb-kana-bulk-review-20261102-r112.json); [113: 53582 / held[4]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57472 | Knock-Knock | 2024 | vndb-v56704 (2017) | ambiguous-name-year | [112: v57472 / held[23]](vndb-kana-bulk-review-20261102-r112.json); [113: 53621 / held[5]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57474 | The Party | 2024 | vndb-v44428 (2023) | ambiguous-name-year | [112: v57474 / held[24]](vndb-kana-bulk-review-20261102-r112.json); [113: 53623 / held[6]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57495 | Eve | 2026 | vndb-v1441 (2008) | ambiguous-name-year | [112: v57495 / held[25]](vndb-kana-bulk-review-20261102-r112.json); [113: 53642 / held[7]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 疑似版本/依赖内容 | vndb:v57560 | Nagaruboshi Fandisk. | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [112: v57560 / held[26]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v57596 | Movchannja | 2024 | vndb-v13329 (2012) | ambiguous-name-year | [112: v57596 / held[27]](vndb-kana-bulk-review-20261102-r112.json); [113: 53732 / held[8]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57632 | Lost in the Woods | 2024 | vndb-v46298 (2023) | ambiguous-name-year | [112: v57632 / held[28]](vndb-kana-bulk-review-20261102-r112.json); [113: 53764 / held[9]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57697 | SERENITY | 2021 | nextmoe-29801 (2022) | ambiguous-name-year | [112: v57697 / held[29]](vndb-kana-bulk-review-20261102-r112.json); [113: 53825 / held[10]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57703 | Red | 2024 | nextmoe-14623 (1992) | ambiguous-name-year | [112: v57703 / held[30]](vndb-kana-bulk-review-20261102-r112.json); [113: 53831 / held[11]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57705 | Love Song | 2024 | vndb-v15032 (2014) | ambiguous-name-year | [112: v57705 / held[31]](vndb-kana-bulk-review-20261102-r112.json); [113: 53833 / held[12]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57706 | Change | 2024 | vndb-v22340 (2017) | ambiguous-name-year | [112: v57706 / held[32]](vndb-kana-bulk-review-20261102-r112.json); [113: 53834 / held[13]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 疑似版本/依赖内容 | vndb:v57719 | The Prey's Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [112: v57719 / held[33]](vndb-kana-bulk-review-20261102-r112.json); [113: 53843 / held[14]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57724 | Moonlight | 2022 | vndb-v23642 (2016) | ambiguous-name-year | [112: v57724 / held[34]](vndb-kana-bulk-review-20261102-r112.json); [113: 53848 / held[15]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57804 | Doubt! | 2023 | vndb-v54431 (2012) | ambiguous-name-year | [112: v57804 / held[35]](vndb-kana-bulk-review-20261102-r112.json); [113: 53912 / held[16]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57868 | The Box | 2025 | ifdb-pkubqzkvhqolbcy9 (2016) | ambiguous-name-year | [112: v57868 / held[36]](vndb-kana-bulk-review-20261102-r112.json); [113: 53971 / held[17]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57877 | Connection | 2025 | vndb-v7306 (2011) | ambiguous-name-year | [112: v57877 / held[37]](vndb-kana-bulk-review-20261102-r112.json); [113: 53980 / held[18]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57962 | Ruin | 2024 | vndb-v56075 (2020) | ambiguous-name-year | [112: v57962 / held[38]](vndb-kana-bulk-review-20261102-r112.json); [113: 54061 / held[19]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v57979 | Curtain Call | 2025 | vndb-v35382 (2022) | ambiguous-name-year | [112: v57979 / held[39]](vndb-kana-bulk-review-20261102-r112.json); [113: 54075 / held[20]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58013 | Kiss yori Amakute Fukai Mono | 2005 | vndb-v1008 (2008) | ambiguous-name-year | [112: v58013 / held[40]](vndb-kana-bulk-review-20261102-r112.json) |
| 名称/年份/身份冲突 | vndb:v58015 | Nightmare | 2025 | vndb-v7588 (2011) | ambiguous-name-year | [112: v58015 / held[41]](vndb-kana-bulk-review-20261102-r112.json); [113: 54105 / held[21]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58135 | A Chance Encounter | 2025 | vndb-v37237 (2022) | ambiguous-name-year | [113: 54186 / held[22]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58142 | forget-me-not | 2025 | nextmoe-16804 (2014); vndb-v44021 (2015) | ambiguous-name-year | [113: 54193 / held[23]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58185 | Vampire Lover | 2025 | vndb-v31261 (2020) | ambiguous-name-year | [113: 54235 / held[24]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58198 | Forget Me Not | 2025 | nextmoe-16804 (2014); vndb-v44021 (2015) | ambiguous-name-year | [113: 54248 / held[25]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58205 | an_encounter | 2025 | vndb-v44940 (2022) | ambiguous-name-year | [113: 54255 / held[26]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58214 | The Haunting | 2025 | ifdb-j67hoxr1aomlwnxn (1991) | ambiguous-name-year | [113: 54264 / held[27]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58257 | Night Shift | 2024 | ifdb-nii7ymjqvrjq8ojx (2023) | ambiguous-name-year | [113: 54300 / held[28]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 来源日期冲突 | vndb:v58299 | Nora Inu no Iinazuke -Stray dog fiance- | 2024-07-26 | NextMoe: 2023-12-20 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [113: 54329 / held[29]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58307 | Gekka Bijin | 2023 | vndb-v2489 (1998) | ambiguous-name-year | [113: 54337 / held[30]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58343 | Shiro to Kuro | 2023 | vndb-v31278 (2020) | ambiguous-name-year | [113: 54369 / held[31]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58442 | GAKUEN-Tengoku | 2015 | vndb-v25938 (2005) | ambiguous-name-year | [113: 54449 / held[32]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | vndb:v58528 | Juniper | 2025 | vndb-v51789 (2024) | ambiguous-name-year | [113: 54523 / held[33]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:3x2sojljv04qni8i | Constraints | 2001-01-01 00:00:00 | ifdb-rl2xdcgxy0t66x9j (2002) | name-year-conflict | [113: 3x2sojljv04qni8i / held[34]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:7sr1v9vb9r4ansq5 | Diorama | 1999-01-01 00:00:00 | vndb-v5372 (2005) | name-year-conflict | [113: 7sr1v9vb9r4ansq5 / held[35]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:0y8aha1d6dv4cawl | Matchmaker | 1986-01-01 00:00:00 | vndb-v47046 (2023) | name-year-conflict | [113: 0y8aha1d6dv4cawl / held[36]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:s4ndt66a53p5hkno | Pegasus | 2013-07-08 01:00:00 | vndb-v7550 (2011) | name-year-conflict | [113: s4ndt66a53p5hkno / held[37]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:cic260su6jmkpjt3 | (untitled) | 1999-01-01 00:00:00 | vndb-v7504 (2010) | name-year-conflict | [113: cic260su6jmkpjt3 / held[38]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:p8prp8ker2m5rb0i | Zombies | 1999-01-01 00:00:00 | ifdb-7c1hob5xlmxeyxcl (2004) | name-year-conflict | [113: p8prp8ker2m5rb0i / held[39]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:hqd18uc0yw1oxo9l | Far From Home | 2002-01-01 00:00:00 | ifdb-gmik0xu9vjc1ga49 (2021) | name-year-conflict | [113: hqd18uc0yw1oxo9l / held[40]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:n39lqllkrcxbbi8n | Reunion | 2004-01-01 00:00:00 | vndb-v13243 (2013) | name-year-conflict | [113: n39lqllkrcxbbi8n / held[41]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:0mu33xks7epsd1js | Escape | 2016-01-01 00:00:00 | nextmoe-7725 (2015) | name-year-conflict | [113: 0mu33xks7epsd1js / held[42]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:j11gdl8c4t0n3lzz | Zero | 2004-01-01 00:00:00 | alicesoft-extra-zeroaction (2004); vndb-v43188 (2023) | name-year-conflict | [113: j11gdl8c4t0n3lzz / held[43]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:4beljteb8329os7c | Room | 2016-01-12 01:00:00 | vndb-v43862 (2013) | name-year-conflict | [113: 4beljteb8329os7c / held[44]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:v8cymsh1u24t2tnq | Cave | 2004-01-01 00:00:00 | ifdb-u94un0rox6hbn4sl (1999) | name-year-conflict | [113: v8cymsh1u24t2tnq / held[45]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:vxmk4alugyuijmcy | Dear Diary | 2002-06-10 01:00:00 | vndb-v47019 (2022) | name-year-conflict | [113: vxmk4alugyuijmcy / held[46]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:gm3cvj8litzshnxi | The Visit | 2014-01-01 00:00:00 | nextmoe-25830 (2020) | name-year-conflict | [113: gm3cvj8litzshnxi / held[47]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:dtmrh4w8l3cs73s7 | Spiral | 2012-09-30 01:00:00 | g1449 (2019); vndb-v44441 (2023) | name-year-conflict | [113: dtmrh4w8l3cs73s7 / held[48]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:i2b3gyyh8e3atjem | Reflection | 2013-09-09 01:00:00 | vndb-v32611 (2021) | name-year-conflict | [113: i2b3gyyh8e3atjem / held[49]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:xgvedz8j1ly23tfb | Existence | 2009-01-01 00:00:00 | vndb-v56373 (2025) | name-year-conflict | [113: xgvedz8j1ly23tfb / held[50]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:h1yfw6yhvhdvwowd | Stowaway! | 1988-01-01 00:00:00 | ifdb-jwd9f2ba1om1oo4j (2004) | name-year-conflict | [113: h1yfw6yhvhdvwowd / held[51]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:nb2q52186kuir6ft | Fox | 2002-01-01 00:00:00 | vndb-v36340 (2022) | name-year-conflict | [113: nb2q52186kuir6ft / held[52]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:692uyvb2h1vl5nst | Space detective | 2016-01-01 00:00:00 | ifdb-2k6pmv9xznc4e4km (1986) | name-year-conflict | [113: 692uyvb2h1vl5nst / held[53]](nextmoe-ifdb-bulk-review-20261102-r113.json) |
| 名称/年份/身份冲突 | ifdb:2tifxpo30ncld09z | House | 2018-04-06 01:00:00 | ifdb-c1tty9pesr0qqdno (2003) | name-year-conflict | [113: 2tifxpo30ncld09z / held[54]](nextmoe-ifdb-bulk-review-20261102-r113.json) |

## 原始证据

- [第112批审计](vndb-kana-bulk-review-20261102-r112.json)
- [第113批审计](nextmoe-ifdb-bulk-review-20261102-r113.json)
- [两批汇总](basic-r112-r113-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
