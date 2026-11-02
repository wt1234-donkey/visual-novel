# 第114、115批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 114 | 1400 | 445 | 500 | 45 | 351 | 59 |
| 115 | 1654 | 609 | 500 | 65 | 259 | 221 |

## 228条暂存处理

VNDB输入0条、NextMoe输入228条；本轮从旧暂存入选228条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：55,841 → 56,841。

## 新续采位置

- VNDB：`v59502`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVFU1TVRaOQ`
- IFDB：`7180`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共110条原始记录，按来源ID合并为80个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v58135 | A Chance Encounter | 2025 | vndb-v37237 (2022) | ambiguous-name-year | [114: v58135 / held[0]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58142 | forget-me-not | 2025 | nextmoe-16804 (2014); vndb-v44021 (2015) | ambiguous-name-year | [114: v58142 / held[1]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58185 | Vampire Lover | 2025 | vndb-v31261 (2020) | ambiguous-name-year | [114: v58185 / held[2]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58198 | Forget Me Not | 2025 | nextmoe-16804 (2014); vndb-v44021 (2015) | ambiguous-name-year | [114: v58198 / held[3]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58205 | an_encounter | 2025 | vndb-v44940 (2022) | ambiguous-name-year | [114: v58205 / held[4]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58214 | The Haunting | 2025 | ifdb-j67hoxr1aomlwnxn (1991) | ambiguous-name-year | [114: v58214 / held[5]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58257 | Night Shift | 2024 | ifdb-nii7ymjqvrjq8ojx (2023) | ambiguous-name-year | [114: v58257 / held[6]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58307 | Gekka Bijin | 2023 | vndb-v2489 (1998) | ambiguous-name-year | [114: v58307 / held[7]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58343 | Shiro to Kuro | 2023 | vndb-v31278 (2020) | ambiguous-name-year | [114: v58343 / held[8]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58442 | GAKUEN-Tengoku | 2015 | vndb-v25938 (2005) | ambiguous-name-year | [114: v58442 / held[9]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58528 | Juniper | 2025 | vndb-v51789 (2024) | ambiguous-name-year | [114: v58528 / held[10]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58637 | Paranojja | 2025 | ifdb-42vm6hiqadzy1xn7 (1986) | ambiguous-name-year | [114: v58637 / held[11]](vndb-kana-bulk-review-20261102-r114.json); [115: 54625 / held[0]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58683 | Star Crossed | 2025 | vndb-v48378 (2023) | ambiguous-name-year | [114: v58683 / held[12]](vndb-kana-bulk-review-20261102-r114.json); [115: 54663 / held[1]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58729 | NOKTJURN | 2020 | vndb-v46474 (2013) | ambiguous-name-year | [114: v58729 / held[13]](vndb-kana-bulk-review-20261102-r114.json); [115: 54709 / held[2]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58750 | THE FOOL | 2003 | vndb-v15243 (2008) | ambiguous-name-year | [114: v58750 / held[14]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58756 | Voice | 2021 | vndb-v13347 (2007) | ambiguous-name-year | [114: v58756 / held[15]](vndb-kana-bulk-review-20261102-r114.json); [115: 54736 / held[3]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58757 | Niguangzheng | 2026 | vndb-v46679 (2023) | ambiguous-name-year | [114: v58757 / held[16]](vndb-kana-bulk-review-20261102-r114.json); [115: 54737 / held[4]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58763 | Amazing Grace | 2008 | g836 (2018) | ambiguous-name-year | [114: v58763 / held[17]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58768 | Inugami | 2004 | vndb-v2774 (2009) | ambiguous-name-year | [114: v58768 / held[18]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58786 | Yakata | 2004 | vndb-v14513 (1996) | ambiguous-name-year | [114: v58786 / held[19]](vndb-kana-bulk-review-20261102-r114.json) |
| 名称/年份/身份冲突 | vndb:v58815 | The Offer | 2020 | vndb-v31207 (2019) | ambiguous-name-year | [114: v58815 / held[20]](vndb-kana-bulk-review-20261102-r114.json); [115: 54793 / held[5]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58822 | Kaleidoscope | 2020 | vndb-v4348 (2004) | ambiguous-name-year | [114: v58822 / held[21]](vndb-kana-bulk-review-20261102-r114.json); [115: 54798 / held[6]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58863 | Grief | 2024 | ifdb-18cypk9amp4ii8o1 (2008) | ambiguous-name-year | [114: v58863 / held[22]](vndb-kana-bulk-review-20261102-r114.json); [115: 54837 / held[7]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 疑似版本/依赖内容 | vndb:v58874 | DDLC Relapse | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [114: v58874 / held[23]](vndb-kana-bulk-review-20261102-r114.json); [115: 54848 / held[8]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v58902 | UNTITLED | 2021 | vndb-v7504 (2010) | ambiguous-name-year | [114: v58902 / held[24]](vndb-kana-bulk-review-20261102-r114.json); [115: 54875 / held[9]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59001 | Fal'shivka | 2025 | vndb-v2356 (2003) | ambiguous-name-year | [114: v59001 / held[25]](vndb-kana-bulk-review-20261102-r114.json); [115: 54967 / held[10]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59002 | (Ne)Real'nost' | 2025 | legend-entertainment-unreal-na-pali (1998) | ambiguous-name-year | [114: v59002 / held[26]](vndb-kana-bulk-review-20261102-r114.json); [115: 54968 / held[11]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59038 | halfmoon | 2026 | vndb-v32941 (2021) | ambiguous-name-year | [114: v59038 / held[27]](vndb-kana-bulk-review-20261102-r114.json); [115: 54997 / held[12]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59041 | Ai Ai | 2025 | vndb-v43412 (2023) | ambiguous-name-year | [114: v59041 / held[28]](vndb-kana-bulk-review-20261102-r114.json); [115: 55000 / held[13]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59042 | 3/4 spell swap | 2026 | ifdb-mmfu9pel99q6wppe (2025) | ambiguous-name-year | [114: v59042 / held[29]](vndb-kana-bulk-review-20261102-r114.json); [115: 55001 / held[14]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59055 | Cycle | 2017 | vndb-v32285 (2013) | ambiguous-name-year | [114: v59055 / held[30]](vndb-kana-bulk-review-20261102-r114.json); [115: 55012 / held[15]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59099 | The Library | 2014 | ifdb-myt9vkrn185f9csm (2021) | ambiguous-name-year | [114: v59099 / held[31]](vndb-kana-bulk-review-20261102-r114.json); [115: 55056 / held[16]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59100 | The Elevator | 2014 | vndb-v10347 (2012) | ambiguous-name-year | [114: v59100 / held[32]](vndb-kana-bulk-review-20261102-r114.json); [115: 55057 / held[17]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59101 | The Garden | 2014 | vndb-v35198 (2022) | ambiguous-name-year | [114: v59101 / held[33]](vndb-kana-bulk-review-20261102-r114.json); [115: 55058 / held[18]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59128 | Sunset | 2021 | vndb-v54570 (2020) | ambiguous-name-year | [114: v59128 / held[34]](vndb-kana-bulk-review-20261102-r114.json); [115: 55084 / held[19]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59192 | Good Boy! | 2025 | ifdb-nicbpsn9nuh7xkuw (2017) | ambiguous-name-year | [114: v59192 / held[35]](vndb-kana-bulk-review-20261102-r114.json); [115: 55146 / held[20]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59217 | overtime | 2025 | nextmoe-49921 (2024) | ambiguous-name-year | [114: v59217 / held[36]](vndb-kana-bulk-review-20261102-r114.json); [115: 55168 / held[21]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59234 | ... --- ... (Save Our Souls) | 2025 | vndb-v18963 (2015) | ambiguous-name-year | [114: v59234 / held[37]](vndb-kana-bulk-review-20261102-r114.json); [115: 55183 / held[22]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 疑似版本/依赖内容 | vndb:v59249 | How to Make a DDLC Mod | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [114: v59249 / held[38]](vndb-kana-bulk-review-20261102-r114.json); [115: 55195 / held[23]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59308 | On Thin Ice | 2021 | vndb-v42259 (2020) | ambiguous-name-year | [114: v59308 / held[39]](vndb-kana-bulk-review-20261102-r114.json); [115: 55251 / held[24]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59361 | The One | 2022 | vndb-v26697 (2019) | ambiguous-name-year | [114: v59361 / held[40]](vndb-kana-bulk-review-20261102-r114.json); [115: 55304 / held[25]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59397 | Last Day | 2012 | ifdb-9u8zksm7e51t3bar (2020) | ambiguous-name-year | [114: v59397 / held[41]](vndb-kana-bulk-review-20261102-r114.json); [115: 55339 / held[26]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59468 | Deja Vu | 2025 | ifdb-bhu49t1gxfwetcru (1993) | ambiguous-name-year | [114: v59468 / held[42]](vndb-kana-bulk-review-20261102-r114.json); [115: 55398 / held[27]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59469 | Poe's Raven | 2025 | vndb-v38864 (2021) | ambiguous-name-year | [114: v59469 / held[43]](vndb-kana-bulk-review-20261102-r114.json); [115: 55399 / held[28]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59470 | RJVN | 2025 | vndb-v31969 (2021) | ambiguous-name-year | [114: v59470 / held[44]](vndb-kana-bulk-review-20261102-r114.json); [115: 55400 / held[29]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59531 | Hello World! | 2025 | g599 (2002) | ambiguous-name-year | [115: 55457 / held[30]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59542 | Echoes | 2025 | vndb-v50422 (2024) | ambiguous-name-year | [115: 55468 / held[31]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59545 | Curse | 2025 | konami-curse (2005) | ambiguous-name-year | [115: 55470 / held[32]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59575 | GOLOD | 2025 | vndb-v51416 (2016) | ambiguous-name-year | [115: 55498 / held[33]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59600 | Mirror \| Mirror | 2025 | ifdb-vke24gmd8usqywu4 (2020) | ambiguous-name-year | [115: 55519 / held[34]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59631 | The Wedding | 2026 | ifdb-5r1iabxsfwmz40ev (1996) | ambiguous-name-year | [115: 55549 / held[35]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59632 | Onigashima | 2025 | vndb-v41832 (2001) | ambiguous-name-year | [115: 55550 / held[36]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59659 | Strings attached | 2025 | ifdb-p71wudmczcl8to5s (2026) | ambiguous-name-year | [115: 55577 / held[37]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59768 | Night Drive | 2025 | ifdb-2174obt391f36ave (2017) | ambiguous-name-year | [115: 55682 / held[38]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 疑似版本/依赖内容 | vndb:v59836 | Futanari Witches Pantsu Janai kara Hamide chau! ! Triple Edition | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [115: 55749 / held[39]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59857 | Leucochloridium | 2025 | vndb-v43872 (2014) | ambiguous-name-year | [115: 55769 / held[40]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59885 | The Whisperer in Darkness | 2025 | vndb-v20151 (2016) | ambiguous-name-year | [115: 55796 / held[41]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v59969 | Tsvit Paporoti | 2025 | vndb-v19833 (2016) | ambiguous-name-year | [115: 55872 / held[42]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | vndb:v60010 | Love Bites | 2025 | vndb-v18977 (2018) | ambiguous-name-year | [115: 55912 / held[43]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:ygkesj941rx2inl4 | Trapped | 2011-04-14 01:00:00 | vndb-v10384 (2012) | name-year-conflict | [115: ygkesj941rx2inl4 / held[44]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:8dyvvc6pdp7y1tr5 | End of The World | 2022-05-01 01:00:00 | vndb-v24401 (2003) | name-year-conflict | [115: 8dyvvc6pdp7y1tr5 / held[45]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:0odl661ptrlyo1ld | Dungeon Adventure | 1984-01-01 00:00:00 | historical-70369da71715fd01 (1982) | name-year-conflict | [115: 0odl661ptrlyo1ld / held[46]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:fj9gz0mwdufcodzl | Lost! | 1988-06-01 00:00:00 | vndb-v14352 (2013) | name-year-conflict | [115: fj9gz0mwdufcodzl / held[47]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:uke87yz74wm8chu7 | The City | 1983-01-01 00:00:00 | ifdb-a2wy18vpncjce925 (1998) | name-year-conflict | [115: uke87yz74wm8chu7 / held[48]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:o29cdkm67d56uckl | Where There's a Will | 2005-01-01 00:00:00 | vndb-v51774 (2024) | name-year-conflict | [115: o29cdkm67d56uckl / held[49]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:zryvnktpxoy76p4j | SHAPESHIFTER | 2012-10-16 01:00:00 | nextmoe-5629 (2010) | name-year-conflict | [115: zryvnktpxoy76p4j / held[50]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:ty2z1c41ec7i6mf6 | Identity | 2004-01-01 00:00:00 | nextmoe-27566 (2026) | name-year-conflict | [115: ty2z1c41ec7i6mf6 / held[51]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:bvpfkjeawcewjomk | the eternal adventures of tits magee | 2019-09-03 01:00:00 | vndb-v38690 (2020) | name-year-conflict | [115: bvpfkjeawcewjomk / held[52]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:kgvs750w4kzuirgt | Treasure Hunt | 1986-01-01 00:00:00 | ifdb-pxpqnb4pb5rfn98k (2016) | name-year-conflict | [115: kgvs750w4kzuirgt / held[53]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:c0gb9dob40jnuz4t | Ralph | 2001-01-01 00:00:00 | ifdb-og54uzaryp1nh1jh (1996) | name-year-conflict | [115: c0gb9dob40jnuz4t / held[54]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:cmednr12pypwsq20 | Snowman | 2020-10-31 01:00:00 | vndb-v41081 (2022) | name-year-conflict | [115: cmednr12pypwsq20 / held[55]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:clhbm04pua41bnj6 | Escape | 2013-10-28 01:00:00 | nextmoe-7725 (2015) | name-year-conflict | [115: clhbm04pua41bnj6 / held[56]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:huixucix8hmk6yfg | Time Quest | 1984-01-01 00:00:00 | legend-entertainment-timequest (1991) | name-year-conflict | [115: huixucix8hmk6yfg / held[57]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:urxrv27t7qtu52lb | Galatea | 2000-01-01 00:00:00 | vndb-v55516 (2025) | name-year-conflict | [115: urxrv27t7qtu52lb / held[58]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:wbx533v4ful0o9uw | The Way Home | 2016-06-12 01:00:00 | vndb-v21802 (2017) | name-year-conflict | [115: wbx533v4ful0o9uw / held[59]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:a30o796duklrp6cv | Wedding | 2010-03-04 01:00:00 | vndb-v18213 (2015) | name-year-conflict | [115: a30o796duklrp6cv / held[60]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:86pdqywaafo2sl9n | Bedlam | 1982-01-01 00:00:00 | ifdb-3oj97yagdl2990cs (1997) | name-year-conflict | [115: 86pdqywaafo2sl9n / held[61]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:ba2v4enwku7o445b | Yandere-chan | 2023-07-28 01:00:00 | vndb-v10665 (2012) | name-year-conflict | [115: ba2v4enwku7o445b / held[62]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:akgcnkurpb0mq1xc | Paranoia | 2012-01-01 00:00:00 | ifdb-42vm6hiqadzy1xn7 (1986) | name-year-conflict | [115: akgcnkurpb0mq1xc / held[63]](nextmoe-ifdb-bulk-review-20261102-r115.json) |
| 名称/年份/身份冲突 | ifdb:gss2e7619ri01v2d | Dracula | 1986-01-01 00:00:00 | ifdb-zj85vzo2r92jq6ie (2026) | name-year-conflict | [115: gss2e7619ri01v2d / held[64]](nextmoe-ifdb-bulk-review-20261102-r115.json) |

## 原始证据

- [第114批审计](vndb-kana-bulk-review-20261102-r114.json)
- [第115批审计](nextmoe-ifdb-bulk-review-20261102-r115.json)
- [两批汇总](basic-r114-r115-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
