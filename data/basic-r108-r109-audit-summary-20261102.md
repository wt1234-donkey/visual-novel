# 第108、109批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 108 | 1419 | 528 | 500 | 34 | 320 | 37 |
| 109 | 1643 | 580 | 500 | 50 | 261 | 252 |

## 242条暂存处理

VNDB输入19条、NextMoe输入223条；本轮从旧暂存入选242条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：52,841 → 53,841。

## 新续采位置

- VNDB：`v55424`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVEl5T1RCOQ`
- IFDB：`6504`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共84条原始记录，按来源ID合并为61个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v53991 | FRAGILE | 2017 | vndb-v65088 (2009) | ambiguous-name-year | [108: v53991 / held[0]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54004 | A Night Out | 2018 | vndb-v29091 (2020) | ambiguous-name-year | [108: v54004 / held[1]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54055 | Forgotten Memories | 2024 | vndb-v34272 (2021) | ambiguous-name-year | [108: v54055 / held[2]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54076 | Kiseki | 2024 | vndb-v44804 (2003) | ambiguous-name-year | [108: v54076 / held[3]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54448 | Kanraku ~Purinsesu~ | 2008 | vndb-v9352 (2004) | ambiguous-name-year | [108: v54448 / held[4]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54471 | Manatsu no Yo no Yume | 2003 | g827 (2005); vndb-v11520 (2006) | ambiguous-name-year | [108: v54471 / held[5]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54474 | Last Day | 2021 | ifdb-9u8zksm7e51t3bar (2020) | ambiguous-name-year | [108: v54474 / held[6]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54490 | Day and Night | 2019 | vndb-v29431 (2020) | ambiguous-name-year | [108: v54490 / held[7]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54510 | Guardian | 2010 | nextmoe-22596 (2010); vndb-v9825 (1999) | ambiguous-name-year | [108: v54510 / held[8]](vndb-kana-bulk-review-20261102-r108.json) |
| 疑似版本/依赖内容 | vndb:v54523 | Bitch ni Natte, New Game! ~Game to Rendoushite Real Demo Henkasuru Ane no Sugata~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [108: v54523 / held[9]](vndb-kana-bulk-review-20261102-r108.json) |
| 名称/年份/身份冲突 | vndb:v54556 | SAIKA | 2025 | vndb-v33879 (2003) | ambiguous-name-year | [108: v54556 / held[10]](vndb-kana-bulk-review-20261102-r108.json); [109: 50985 / held[0]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54559 | DAY BREAK | 2011 | vndb-v37965 (2022) | ambiguous-name-year | [108: v54559 / held[11]](vndb-kana-bulk-review-20261102-r108.json); [109: 50987 / held[1]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54666 | Until We Meet Again | 2025 | nextmoe-9562 (2005) | ambiguous-name-year | [108: v54666 / held[12]](vndb-kana-bulk-review-20261102-r108.json); [109: 51084 / held[2]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54678 | Atrocity | 2012 | vndb-v24912 (2018) | ambiguous-name-year | [108: v54678 / held[13]](vndb-kana-bulk-review-20261102-r108.json); [109: 51096 / held[3]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54715 | End of the World | 2025 | vndb-v24401 (2003) | ambiguous-name-year | [108: v54715 / held[14]](vndb-kana-bulk-review-20261102-r108.json); [109: 51129 / held[4]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54734 | Medusa | 2025 | ifdb-29pgq4rm62zyk725 (2003) | ambiguous-name-year | [108: v54734 / held[15]](vndb-kana-bulk-review-20261102-r108.json); [109: 51148 / held[5]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54745 | The Club | 2024 | vndb-v24245 (2018) | ambiguous-name-year | [108: v54745 / held[16]](vndb-kana-bulk-review-20261102-r108.json); [109: 51158 / held[6]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54798 | noise | 2011 | vndb-v13461 (2006) | ambiguous-name-year | [108: v54798 / held[17]](vndb-kana-bulk-review-20261102-r108.json); [109: 51207 / held[7]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 疑似版本/依赖内容 | vndb:v54800 | Clinical Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [108: v54800 / held[18]](vndb-kana-bulk-review-20261102-r108.json); [109: 51209 / held[8]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54871 | Stardust | 2025 | ifdb-6htd5qrilhcdrm5u (2006) | ambiguous-name-year | [108: v54871 / held[19]](vndb-kana-bulk-review-20261102-r108.json); [109: 51269 / held[9]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54887 | Nie | 2010 | vndb-v6889 (1999) | ambiguous-name-year | [108: v54887 / held[20]](vndb-kana-bulk-review-20261102-r108.json); [109: 51284 / held[10]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54888 | Fetish | 2013 | vndb-v8877 (1994) | ambiguous-name-year | [108: v54888 / held[21]](vndb-kana-bulk-review-20261102-r108.json); [109: 51285 / held[11]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v54925 | R(e)Born_ | 2025 | vndb-v46024 (2023) | ambiguous-name-year | [108: v54925 / held[22]](vndb-kana-bulk-review-20261102-r108.json); [109: 51321 / held[12]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 疑似版本/依赖内容 | vndb:v54975 | Kodoku na Hoshi no Kagayaki ~Re:Stars And Lights's Append Disc~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [108: v54975 / held[23]](vndb-kana-bulk-review-20261102-r108.json); [109: 51369 / held[13]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 疑似版本/依赖内容 | vndb:v55036 | MCC Fandisk ~Sono 1~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [108: v55036 / held[24]](vndb-kana-bulk-review-20261102-r108.json); [109: 51415 / held[14]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55136 | Rakuen | 2005 | vndb-v14746 (2000); vndb-v2285 (1998) | ambiguous-name-year | [108: v55136 / held[25]](vndb-kana-bulk-review-20261102-r108.json) |
| 疑似版本/依赖内容 | vndb:v55193 | Xuexing Huajia DLC Qingren Jie | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [108: v55193 / held[26]](vndb-kana-bulk-review-20261102-r108.json); [109: 51554 / held[15]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55200 | a day in the life | 2024 | ifdb-yhtrbifi3nte5xav (2024); vndb-v36838 (2022) | ambiguous-name-year | [108: v55200 / held[27]](vndb-kana-bulk-review-20261102-r108.json); [109: 51561 / held[16]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55204 | Growing Up | 2024 | ifdb-5i53mr5dbhy5bgsc (2011) | ambiguous-name-year | [108: v55204 / held[28]](vndb-kana-bulk-review-20261102-r108.json); [109: 51565 / held[17]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55251 | Cabin Fever!!! | 2024 | nextmoe-30492 (2021) | ambiguous-name-year | [108: v55251 / held[29]](vndb-kana-bulk-review-20261102-r108.json); [109: 51609 / held[18]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55264 | Forbidden Love | 2025 | vndb-v1852 (2002) | ambiguous-name-year | [108: v55264 / held[30]](vndb-kana-bulk-review-20261102-r108.json); [109: 51619 / held[19]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 疑似版本/依赖内容 | vndb:v55301 | Sora no Baroque BugBug Append Ban | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [108: v55301 / held[31]](vndb-kana-bulk-review-20261102-r108.json); [109: 51650 / held[20]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55377 | Until We Meet Again | 2025 | nextmoe-9562 (2005) | ambiguous-name-year | [108: v55377 / held[32]](vndb-kana-bulk-review-20261102-r108.json); [109: 51716 / held[21]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55402 | Waiting | 2025 | vndb-v27220 (2010) | ambiguous-name-year | [108: v55402 / held[33]](vndb-kana-bulk-review-20261102-r108.json); [109: 51739 / held[22]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55451 | Till Death Do Us Part | 2025 | vndb-v22540 (2017) | ambiguous-name-year | [109: 51787 / held[23]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 疑似版本/依赖内容 | vndb:v55565 | Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [109: 51895 / held[24]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55628 | SANA | 2025 | vndb-v43720 (2003) | ambiguous-name-year | [109: 51955 / held[25]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55637 | Five Years | 2025 | vndb-v2374 (2001) | ambiguous-name-year | [109: 51964 / held[26]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55670 | Growing Pains | 2025 | ifdb-d84ng0i76ts22aji (2019) | ambiguous-name-year | [109: 51995 / held[27]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55681 | I Remember You | 2025 | vndb-v51997 (2024) | ambiguous-name-year | [109: 52005 / held[28]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55714 | MGLA | 2023 | vndb-v37982 (2022) | ambiguous-name-year | [109: 52037 / held[29]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 来源日期冲突 | vndb:v55736 | Harmony | 2013-08-12 | NextMoe: 2012-08-11 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [109: 52052 / held[30]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55758 | Saishuu Densha | 2018 | vndb-v30710 (1998) | ambiguous-name-year | [109: 52073 / held[31]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 来源日期冲突 | vndb:v55779 | Alisa-mod | 2018-09-23 | NextMoe: 2015-12-03 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [109: 52093 / held[32]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55879 | Something Left | 2025 | vndb-v45120 (2023) | ambiguous-name-year | [109: 52180 / held[33]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55889 | Zai Jian | 2022 | vndb-v42281 (2023) | ambiguous-name-year | [109: 52187 / held[34]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | vndb:v55975 | Jin Ni Yiren | 2026 | alicesoft-extra-onlyyou (1996) | ambiguous-name-year | [109: 52267 / held[35]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:fjnwkt63cy7s78pe | Mutiny! | 1996-01-01 00:00:00 | vndb-v21120 (2017) | name-year-conflict | [109: fjnwkt63cy7s78pe / held[36]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:eqjb26w3sqnt9ezx | Enigma | 2001-01-01 00:00:00 | nextmoe-21146 (2015) | name-year-conflict | [109: eqjb26w3sqnt9ezx / held[37]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:qlfee7oclsfc8c3l | Around the World In Eighty Days | 1981-11-01 01:00:00 | ifdb-7qylx43kl1kxetr0 (1988) | name-year-conflict | [109: qlfee7oclsfc8c3l / held[38]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:90e4g8tf9qn6s8et | Going rogue | 2021-01-01 00:00:00 | vndb-v33233 (2022) | name-year-conflict | [109: 90e4g8tf9qn6s8et / held[39]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:8f6fgqkkwrnvp7k8 | Island | 2022-01-01 00:00:00 | g1346 (2016); supp26-fw-island (2016) | name-year-conflict | [109: 8f6fgqkkwrnvp7k8 / held[40]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:u8zcowjmdns8nf5p | Rays | 1987-01-01 00:00:00 | vndb-v52528 (2024) | name-year-conflict | [109: u8zcowjmdns8nf5p / held[41]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:sun9qkqvuy6tcpfq | Marooned! | 1988-01-01 00:00:00 | ifdb-9vmsdpkz7h1nkq6q (2000) | name-year-conflict | [109: sun9qkqvuy6tcpfq / held[42]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:5iz05cexg449vrx3 | Distress | 2005-10-01 00:00:00 | vndb-v24116 (2018) | name-year-conflict | [109: 5iz05cexg449vrx3 / held[43]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:ua7h9z9j0iyamd1a | faith | 2023-06-02 01:00:00 | vndb-v12723 (2006) | name-year-conflict | [109: ua7h9z9j0iyamd1a / held[44]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:t9gcrt311dbexi2w | Secret Mission | 1991-01-01 00:00:00 | basic-d8d4027c7504 (1996) | name-year-conflict | [109: t9gcrt311dbexi2w / held[45]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:eehfdsijtf25uk8t | Silverwolf | 1992-01-01 00:00:00 | ifdb-odda0yoff58hia6y (2002) | name-year-conflict | [109: eehfdsijtf25uk8t / held[46]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:gjk9onoaq4eg8eim | Kidnapped | 1993-01-01 00:00:00 | vndb-v23323 (2012) | name-year-conflict | [109: gjk9onoaq4eg8eim / held[47]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:zn1dg22ie5cj8qsb | Marooned | 1992-01-01 00:00:00 | ifdb-9vmsdpkz7h1nkq6q (2000) | name-year-conflict | [109: zn1dg22ie5cj8qsb / held[48]](nextmoe-ifdb-bulk-review-20261102-r109.json) |
| 名称/年份/身份冲突 | ifdb:8dvrd3wkzy6unojw | Nebula | 1986-01-01 00:00:00 | vndb-v29846 (2020) | name-year-conflict | [109: 8dvrd3wkzy6unojw / held[49]](nextmoe-ifdb-bulk-review-20261102-r109.json) |

## 原始证据

- [第108批审计](vndb-kana-bulk-review-20261102-r108.json)
- [第109批审计](nextmoe-ifdb-bulk-review-20261102-r109.json)
- [两批汇总](basic-r108-r109-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
