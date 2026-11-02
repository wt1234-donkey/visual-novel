# 第130、131批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 130 | 1056 | 95 | 500 | 29 | 382 | 50 |
| 131 | 3051 | 767 | 500 | 67 | 1717 | 0 |

## 56条暂存处理

VNDB输入56条、NextMoe输入0条；本轮从旧暂存入选56条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：63,896 → 64,896。

## 新续采位置

- VNDB：`v70299`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNakk1TWpRM2ZR`
- IFDB：`9966`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共96条原始记录，按来源ID合并为96个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v69348 | Shin Taketori Monogatari | 2026 | vndb-v9516 (1984) | ambiguous-name-year | [130: v69348 / held[0]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69362 | will | 2023 | vndb-v10710 (2007) | ambiguous-name-year | [130: v69362 / held[1]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69375 | MIU | 2026 | vndb-v8210 (2001) | ambiguous-name-year | [130: v69375 / held[2]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69383 | DUPLICITY | 2026 | vndb-v26926 (2019) | ambiguous-name-year | [130: v69383 / held[3]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69398 | Descent | 2026 | vndb-v25730 (2019) | ambiguous-name-year | [130: v69398 / held[4]](vndb-kana-bulk-review-20261102-r130.json) |
| 疑似版本/依赖内容 | vndb:v69408 | Sore demo Anata ga Sukidatta | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [130: v69408 / held[5]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69434 | The Waiting Room | 2026 | ifdb-us1bp5yjkwkot7qg (2021) | ambiguous-name-year | [130: v69434 / held[6]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69518 | CONTROL | 2026 | vndb-v27651 (2018) | ambiguous-name-year | [130: v69518 / held[7]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69526 | Raika | 2008 | vndb-v12191 (1994) | ambiguous-name-year | [130: v69526 / held[8]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69558 | Stay the Night — Episode 1: The Almosts | 2026 | vndb-v57026 (2024) | ambiguous-name-year | [130: v69558 / held[9]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69585 | Sweet Tooth | 2026 | vndb-v44128 (2023) | ambiguous-name-year | [130: v69585 / held[10]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69666 | dawn | 2009 | konami-dawn (2005) | ambiguous-name-year | [130: v69666 / held[11]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69689 | The Chase | 2025 | vndb-v61343 (2024) | ambiguous-name-year | [130: v69689 / held[12]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69826 | Akane | 2010 | vndb-v22864 (2005) | ambiguous-name-year | [130: v69826 / held[13]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69878 | Tanabata | 2009 | vndb-v16325 (2012) | ambiguous-name-year | [130: v69878 / held[14]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69883 | Captive | 2026 | vndb-v33825 (2010) | ambiguous-name-year | [130: v69883 / held[15]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69980 | My World | 2017 | vndb-v37986 (2022) | ambiguous-name-year | [130: v69980 / held[16]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v69995 | Demon Heart | 2008 | nextmoe-21991 (2018) | ambiguous-name-year | [130: v69995 / held[17]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70013 | Friends | 2011 | nextmoe-14806 (2012) | ambiguous-name-year | [130: v70013 / held[18]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70022 | Kokoro no Kakera | 2010 | vndb-v20211 (1999) | ambiguous-name-year | [130: v70022 / held[19]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70024 | Natsuyume | 2013 | vndb-v50053 (2008) | ambiguous-name-year | [130: v70024 / held[20]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70083 | Jester Quest | 2026 | ifdb-s61nmrs9a9s9i6js (1988) | ambiguous-name-year | [130: v70083 / held[21]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70101 | 3days | 2003 | vndb-v49638 (2008) | ambiguous-name-year | [130: v70101 / held[22]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70145 | Kasumi Yuugi | 2002 | g673 (1999) | ambiguous-name-year | [130: v70145 / held[23]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70171 | As you wish | 2025 | vndb-v44112 (2023) | ambiguous-name-year | [130: v70171 / held[24]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70185 | Love Pani! | 2010 | vndb-v15992 (2004) | ambiguous-name-year | [130: v70185 / held[25]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70246 | Offside | 2012 | vndb-v24266 (2022) | ambiguous-name-year | [130: v70246 / held[26]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70249 | Stalemate | 2013 | vndb-v5900 (2010) | ambiguous-name-year | [130: v70249 / held[27]](vndb-kana-bulk-review-20261102-r130.json) |
| 名称/年份/身份冲突 | vndb:v70274 | Sex On The Beach | 2025 | vndb-v67739 (2022) | ambiguous-name-year | [130: v70274 / held[28]](vndb-kana-bulk-review-20261102-r130.json) |
| 疑似版本/依赖内容 | vndb:v66987 | Caste Joui no Mesu-tachi ga Iribitaru Ore no Yaribeya Harem ~Biju ga Tsuyoi Mesu de Haramase Onaho Collection o Tsukuru!~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [131: 226567 / held[0]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67026 | Porcelain Hearts | 2026 | vndb-v29753 (2017) | ambiguous-name-year | [131: 226606 / held[1]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67053 | Remember Me | 2026 | vndb-v54496 (2022) | ambiguous-name-year | [131: 226636 / held[2]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67128 | My Guardian Angel | 2026 | vndb-v31197 (2016) | ambiguous-name-year | [131: 226710 / held[3]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67237 | In Your Shadow | 2026 | vndb-v24799 (2018) | ambiguous-name-year | [131: 226827 / held[4]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67272 | AprilFool | 2012 | vndb-v15623 (2007) | ambiguous-name-year | [131: 226862 / held[5]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67279 | Over the Edge | 2026 | ifdb-jr8abn3p5x11lfa8 (2006) | ambiguous-name-year | [131: 226869 / held[6]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67281 | Asterius | 2026 | vndb-v44519 (2023) | ambiguous-name-year | [131: 226871 / held[7]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67286 | Leap of Faith | 2026 | nextmoe-27964 (2020) | ambiguous-name-year | [131: 226876 / held[8]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67302 | As You Wish | 2026 | vndb-v44112 (2023) | ambiguous-name-year | [131: 226897 / held[9]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67411 | Schwarzwald | 2026 | vndb-v13272 (2010) | ambiguous-name-year | [131: 227019 / held[10]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67460 | Stay With Me | 2026 | vndb-v56979 (2025) | ambiguous-name-year | [131: 227074 / held[11]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67473 | NoAH | 2026 | ifdb-ml4pe41qrai83teh (1984) | ambiguous-name-year | [131: 227087 / held[12]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 疑似版本/依赖内容 | vndb:v24869 | Re;quartz Append | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [131: 227462 / held[13]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67573 | The Vault | 2018 | ifdb-9bo8243zp18pwzs8 (2010) | ambiguous-name-year | [131: 228672 / held[14]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67733 | Alien | 2022 | ifdb-d5jcsz4mn1bdqpxr (1988); ifdb-kp8y1zd5vc284d04 (1984) | ambiguous-name-year | [131: 228815 / held[15]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67815 | Odna Seksualnaya Istoriya | 2019 | vndb-v13293 (2012) | ambiguous-name-year | [131: 228880 / held[16]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v67836 | &lt;Ghost&gt; Town | 2023 | ai-ghost-town (1980); microcabin-ghost (1984) | ambiguous-name-year | [131: 228900 / held[17]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68021 | Adrift | 2026 | nextmoe-14737 (2011) | ambiguous-name-year | [131: 229054 / held[18]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68107 | Enigma | 2014 | nextmoe-21146 (2015) | ambiguous-name-year | [131: 229126 / held[19]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68135 | Prototype | 2026 | vndb-v41417 (2022) | ambiguous-name-year | [131: 229154 / held[20]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68136 | Otome | 2024 | vndb-v6775 (2006) | ambiguous-name-year | [131: 229155 / held[21]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 疑似版本/依赖内容 | vndb:v68200 | Triple Pairing - MiniFandisc | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [131: 229183 / held[22]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68187 | Toriko | 2011 | vndb-v14583 (1996) | ambiguous-name-year | [131: 229202 / held[23]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68218 | Eat the Rich | 2026 | ifdb-n7ef5o66fnhwed6d (2024) | ambiguous-name-year | [131: 229229 / held[24]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 疑似版本/依赖内容 | vndb:v68223 | EVA-teki Kanmusu Collection Souryuu Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [131: 229234 / held[25]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 疑似版本/依赖内容 | vndb:v68224 | EVA-teki Kanmusu Collection Ayanami Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [131: 229235 / held[26]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | vndb:v68225 | Yakata | 2014 | vndb-v14513 (1996) | ambiguous-name-year | [131: 229236 / held[27]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:rn2a4uusmh2mosmr | Adventure | 1989-01-01 00:00:00 | ifdb-16y1pp3l16qh7khh (2020) | name-year-conflict | [131: rn2a4uusmh2mosmr / held[28]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:ugkmgida95j1vaab | A Date With Death | 2008-10-01 00:00:00 | nextmoe-43150 (2023) | name-year-conflict | [131: ugkmgida95j1vaab / held[29]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:nzonb4z9is9tnuq6 | Wake Up | 2021-02-24 01:00:00 | ifdb-ivjms7ovf1k39bsz (2024) | name-year-conflict | [131: nzonb4z9is9tnuq6 / held[30]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:2o8te971vaknf4dp | Drip | 2015-04-09 01:00:00 | vndb-v235 (1996) | name-year-conflict | [131: 2o8te971vaknf4dp / held[31]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:2pdvzl4wlmq14gq7 | Underground | 2019-07-30 01:00:00 | vndb-v51225 (2024) | name-year-conflict | [131: 2pdvzl4wlmq14gq7 / held[32]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:hqx29ju0r3n8fkin | Nevermore | 2018-10-02 01:00:00 | nextmoe-1528 (2019) | name-year-conflict | [131: hqx29ju0r3n8fkin / held[33]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:wq4r6tmv04h2dsj4 | Locked In! | 2022-01-01 00:00:00 | vndb-v10977 (2012) | name-year-conflict | [131: wq4r6tmv04h2dsj4 / held[34]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:8tqqyj1oez5hjlju | Mother | 2015-01-01 00:00:00 | vndb-v30967 (2021) | name-year-conflict | [131: 8tqqyj1oez5hjlju / held[35]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:tjw2f61fcwhfnsm2 | NIGHTBOUND | 2017-10-01 01:00:00 | nextmoe-26691 (2019) | name-year-conflict | [131: tjw2f61fcwhfnsm2 / held[36]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:wriiv9wst55m7m7c | Purple | 2024-12-02 01:00:00 | vndb-v13597 (2012) | name-year-conflict | [131: wriiv9wst55m7m7c / held[37]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:aviocvjl3dpderh4 | Big Brother, | 2024-06-16 01:00:00 | vndb-v16100 (2014) | name-year-conflict | [131: aviocvjl3dpderh4 / held[38]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:84p1thlrf2nmpizv | Quinn &amp; Flynn | 2022-09-03 01:00:00 | vndb-v47565 (2023) | name-year-conflict | [131: 84p1thlrf2nmpizv / held[39]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:9oypkqtkoecu8kzl | The Best Man | 2021-10-01 01:00:00 | ifdb-f5mkursovywoc4h1 (2000) | name-year-conflict | [131: 9oypkqtkoecu8kzl / held[40]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:3jbew4fxoz3ziwta | Binary | 2020-04-01 01:00:00 | ifdb-jamnxiokunlkg87a (2023) | name-year-conflict | [131: 3jbew4fxoz3ziwta / held[41]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:mjaul3amg3782xy0 | Prison Break | 2023-04-20 01:00:00 | ifdb-vb6swjio5yc96ics (2009) | name-year-conflict | [131: mjaul3amg3782xy0 / held[42]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:lmtsso95cs0m7vnk | DEVIL'S LIMINAL | 2022-01-01 00:00:00 | vndb-v40795 (2026) | name-year-conflict | [131: lmtsso95cs0m7vnk / held[43]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:n921m771fvvocpbo | The Circular Ruins | 2010-01-01 00:00:00 | vndb-v44435 (2023) | name-year-conflict | [131: n921m771fvvocpbo / held[44]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:h92s9gaqno9fhtbw | Will | 2017-11-07 01:00:00 | vndb-v10710 (2007) | name-year-conflict | [131: h92s9gaqno9fhtbw / held[45]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:byq168qxxaxc7bve | Inheritance | 2014-03-09 01:00:00 | vndb-v27875 (2018) | name-year-conflict | [131: byq168qxxaxc7bve / held[46]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:enoxfkie4ti0zot8 | R E B I R T H | 2026-06-28 01:00:00 | nextmoe-26475 (2020) | name-year-conflict | [131: enoxfkie4ti0zot8 / held[47]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:m0w7fo10t8d5ahjs | Last Minute | 2012-09-30 01:00:00 | vndb-v60354 (2025) | name-year-conflict | [131: m0w7fo10t8d5ahjs / held[48]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:mp3t0rf36e7nll8d | Tower | 2018-10-01 01:00:00 | ifdb-8u6m0cofv7m7pn5u (2009); vndb-v62867 (2022) | name-year-conflict | [131: mp3t0rf36e7nll8d / held[49]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:be5h09qgp80gqz5l | Atlantis | 2022-01-27 01:00:00 | ifdb-x25hcrxpdc4k9o43 (1997) | name-year-conflict | [131: be5h09qgp80gqz5l / held[50]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:8bn7doljquhbq6c3 | Asher | 2018-07-03 01:00:00 | vndb-v14816 (2014) | name-year-conflict | [131: 8bn7doljquhbq6c3 / held[51]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:gg24k97b1nix2avl | The Pawn | 2024-01-01 00:00:00 | ifdb-a3ege93gjofe5q0m (1985) | name-year-conflict | [131: gg24k97b1nix2avl / held[52]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:l46t9onh3rmz27xa | Lethe | 2022-12-05 01:00:00 | vndb-v43859 (2012) | name-year-conflict | [131: l46t9onh3rmz27xa / held[53]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:okvelssfvrn0huu6 | Scoop | 2020-08-04 01:00:00 | vndb-v61802 (2003) | name-year-conflict | [131: okvelssfvrn0huu6 / held[54]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:xh9917r0g3zk943e | 1981 | 2012-01-01 00:00:00 | ifdb-6tlsv79zs2xq9ecs (2001) | name-year-conflict | [131: xh9917r0g3zk943e / held[55]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:20fjuqknnjt1t3ul | Going Home | 2016-10-31 01:00:00 | ifdb-ks3fzs7hu54qzkkx (2012) | name-year-conflict | [131: 20fjuqknnjt1t3ul / held[56]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:r9hutvddtgykd3fz | Dark Deeds | 2015-01-01 00:00:00 | ifdb-h42k9fsxkh25km1c (2011) | name-year-conflict | [131: r9hutvddtgykd3fz / held[57]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:myltjee4uv2wzgpc | Space Invaders | 2017-05-20 01:00:00 | ifdb-y5ui14n1q6gkuuvq (2001) | name-year-conflict | [131: myltjee4uv2wzgpc / held[58]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:w2cgucs8a2aasxv8 | Bodiless | 2019-01-01 00:00:00 | vndb-v45824 (2022) | name-year-conflict | [131: w2cgucs8a2aasxv8 / held[59]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:54qm1xyxe8a05v41 | Homebound | 2020-07-05 01:00:00 | ifdb-ugv5ae889j8g1lkq (2025) | name-year-conflict | [131: 54qm1xyxe8a05v41 / held[60]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:a3abrxk8i66wgbil | The Intruder | 2013-03-20 01:00:00 | ifdb-k4y7rnmiics5h7ej (2022) | name-year-conflict | [131: a3abrxk8i66wgbil / held[61]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:i7k6ttmuyxapgnn0 | The Interrogation | 2016-02-23 01:00:00 | vndb-v47043 (2023) | name-year-conflict | [131: i7k6ttmuyxapgnn0 / held[62]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:stkrrbel8m21b37q | Transit | 2012-09-30 01:00:00 | ifdb-vyh7meppnbpt3fv5 (2021) | name-year-conflict | [131: stkrrbel8m21b37q / held[63]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:ublblcc6toi8nc9j | A Day in the Life | 2022-03-27 01:00:00 | ifdb-yhtrbifi3nte5xav (2024); vndb-v36838 (2022) | name-year-conflict | [131: ublblcc6toi8nc9j / held[64]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:8kuxdkciywxzfyuz | Zugzwang | 2024-06-30 01:00:00 | ifdb-hpesnywwgnl862rz (1998) | name-year-conflict | [131: 8kuxdkciywxzfyuz / held[65]](nextmoe-ifdb-bulk-review-20261102-r131.json) |
| 名称/年份/身份冲突 | ifdb:v34u9l9f3e3xvf19 | 呃啊！ Capybara | 2016-01-01 00:00:00 | vndb-v18973 (2017) | name-year-conflict | [131: v34u9l9f3e3xvf19 / held[66]](nextmoe-ifdb-bulk-review-20261102-r131.json) |

## 原始证据

- [第130批审计](vndb-kana-bulk-review-20261102-r130.json)
- [第131批审计](nextmoe-ifdb-bulk-review-20261102-r131.json)
- [两批汇总](basic-r130-r131-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
