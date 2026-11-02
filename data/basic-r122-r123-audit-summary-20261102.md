# 第122、123批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 122 | 1825 | 837 | 500 | 67 | 376 | 45 |
| 123 | 1655 | 513 | 500 | 44 | 334 | 264 |

## 260条暂存处理

VNDB输入25条、NextMoe输入235条；本轮从旧暂存入选260条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：59,896 → 60,896。

## 新续采位置

- VNDB：`v65736`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOakU0TnpSOQ`
- IFDB：`8079`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共111条原始记录，按来源ID合并为91个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v63930 | Shimai | 1994 | vndb-v5536 (2010) | ambiguous-name-year | [122: v63930 / held[0]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v63934 | EO:Lockdown | 2026 | vndb-v63907 (2025) | ambiguous-name-year | [122: v63934 / held[1]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v63964 | Cupid | 2026 | nextmoe-20251 (2015) | ambiguous-name-year | [122: v63964 / held[2]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v63972 | Lost Connections | 2026 | vndb-v45577 (2023) | ambiguous-name-year | [122: v63972 / held[3]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64018 | Tsumi to Batsu | 2003 | g341 (1999) | ambiguous-name-year | [122: v64018 / held[4]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64043 | Christmas | 2003 | ifdb-gai5cscmtceltbug (2006); vndb-v9292 (2011) | ambiguous-name-year | [122: v64043 / held[5]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64052 | Guernica | 2007 | vndb-v18055 (1996) | ambiguous-name-year | [122: v64052 / held[6]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64084 | pure | 1999 | vndb-v8818 (1989) | ambiguous-name-year | [122: v64084 / held[7]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64090 | Sakura Saku | 2026 | vndb-v63595 (2001) | ambiguous-name-year | [122: v64090 / held[8]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64091 | Kokuhaku | 1996 | vndb-v2561 (2009) | ambiguous-name-year | [122: v64091 / held[9]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64105 | Magical☆Panic | 1993 | vndb-v8788 (1996) | ambiguous-name-year | [122: v64105 / held[10]](vndb-kana-bulk-review-20261102-r122.json) |
| 疑似版本/依赖内容 | vndb:v64127 | Love Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [122: v64127 / held[11]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64158 | Countdown | 2006 | vndb-v13143 (2002) | ambiguous-name-year | [122: v64158 / held[12]](vndb-kana-bulk-review-20261102-r122.json) |
| 疑似版本/依赖内容 | vndb:v64171 | Battle Live! The Idol School Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [122: v64171 / held[13]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64213 | UNBALANCE | 2004 | vndb-v5419 (2009) | ambiguous-name-year | [122: v64213 / held[14]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64215 | SUMMER ALBUM | 2006 | vndb-v14024 (1998) | ambiguous-name-year | [122: v64215 / held[15]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64255 | Ashes to Ashes | 2026 | vndb-v43894 (2023) | ambiguous-name-year | [122: v64255 / held[16]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64263 | snow drop | 2016 | vndb-v112 (2000) | ambiguous-name-year | [122: v64263 / held[17]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64264 | Fairy Tale | 2013 | vndb-v11102 (2012) | ambiguous-name-year | [122: v64264 / held[18]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64270 | SEVEN DAYS | 2003 | vndb-v63861 (2004) | ambiguous-name-year | [122: v64270 / held[19]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64273 | Kimi ga Suki | 2005 | vndb-v38583 (2007) | ambiguous-name-year | [122: v64273 / held[20]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64370 | KAZAHANA | 2003 | vndb-v19020 (2009) | ambiguous-name-year | [122: v64370 / held[21]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64428 | Jack in the Box | 2013 | ifdb-6rhf7eaywwh2bv4q (2007) | ambiguous-name-year | [122: v64428 / held[22]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64451 | I WISH | 2002 | vndb-v43720 (2003) | ambiguous-name-year | [122: v64451 / held[23]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64474 | Snow White | 2003 | vndb-v10880 (2010) | ambiguous-name-year | [122: v64474 / held[24]](vndb-kana-bulk-review-20261102-r122.json) |
| 疑似版本/依赖内容 | vndb:v64530 | Dimitrescu's Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [122: v64530 / held[25]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64561 | Koibana | 2001 | vndb-v11561 (2013) | ambiguous-name-year | [122: v64561 / held[26]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64568 | Ensemble | 2001 | vndb-v61889 (2007) | ambiguous-name-year | [122: v64568 / held[27]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64619 | In The Dark | 2009 | vndb-v40008 (2008) | ambiguous-name-year | [122: v64619 / held[28]](vndb-kana-bulk-review-20261102-r122.json) |
| 疑似版本/依赖内容 | vndb:v64637 | Trial And Error Sensei Daisuki!! Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [122: v64637 / held[29]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64724 | Partner | 2004 | vndb-v3596 (2001) | ambiguous-name-year | [122: v64724 / held[30]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64764 | Doll | 2015 | vndb-v9274 (2008) | ambiguous-name-year | [122: v64764 / held[31]](vndb-kana-bulk-review-20261102-r122.json); [123: 60210 / held[0]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v64789 | Okaerinasai | 2000 | vndb-v68667 (2006) | ambiguous-name-year | [122: v64789 / held[32]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64821 | Film Noir | 2004 | vndb-v6269 (1999) | ambiguous-name-year | [122: v64821 / held[33]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64852 | Kimi to Ita Jikan | 2001 | vndb-v60680 (2004) | ambiguous-name-year | [122: v64852 / held[34]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v64870 | Seesaw Game | 2017 | vndb-v64423 (2011) | ambiguous-name-year | [122: v64870 / held[35]](vndb-kana-bulk-review-20261102-r122.json); [123: 60310 / held[1]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v64871 | Amnesia | 2013 | basic-64e34fa44ed9 (2011) | ambiguous-name-year | [122: v64871 / held[36]](vndb-kana-bulk-review-20261102-r122.json); [123: 60311 / held[2]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v64928 | Psyche | 2013 | ifdb-0esz1txvbkcw9c9h (2026) | ambiguous-name-year | [122: v64928 / held[37]](vndb-kana-bulk-review-20261102-r122.json); [123: 60365 / held[3]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v64929 | Ai no Uta | 2013 | vndb-v15032 (2014) | ambiguous-name-year | [122: v64929 / held[38]](vndb-kana-bulk-review-20261102-r122.json); [123: 60366 / held[4]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v64939 | Kaikou | 2012 | vndb-v3808 (2010) | ambiguous-name-year | [122: v64939 / held[39]](vndb-kana-bulk-review-20261102-r122.json); [123: 60374 / held[5]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v64999 | Doctor☆Stop! | 2007 | g557 (1992) | ambiguous-name-year | [122: v64999 / held[40]](vndb-kana-bulk-review-20261102-r122.json) |
| 疑似版本/依赖内容 | vndb:v65021 | TRIAL | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [122: v65021 / held[41]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65032 | INVADER | 2024 | vndb-v66291 (2005) | ambiguous-name-year | [122: v65032 / held[42]](vndb-kana-bulk-review-20261102-r122.json); [123: 60461 / held[6]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65036 | LOVE GAME | 2005 | vndb-v17374 (2004) | ambiguous-name-year | [122: v65036 / held[43]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65046 | BLUE HEAVEN | 2003 | vndb-v15378 (2007) | ambiguous-name-year | [122: v65046 / held[44]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65057 | SUMMON NIGHT | 2003 | banpresto-sn1 (2000) | ambiguous-name-year | [122: v65057 / held[45]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65091 | La vie en rose | 2008 | vndb-v65089 (2009) | ambiguous-name-year | [122: v65091 / held[46]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65096 | Carnival | 2009 | nextmoe-945 (2004) | ambiguous-name-year | [122: v65096 / held[47]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65141 | Floor 13 | 2026 | ifdb-47kbe7iqov5kc68m (1991) | ambiguous-name-year | [122: v65141 / held[48]](vndb-kana-bulk-review-20261102-r122.json); [123: 60568 / held[7]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65159 | Reflect | 2015 | vndb-v65156 (2013) | ambiguous-name-year | [122: v65159 / held[49]](vndb-kana-bulk-review-20261102-r122.json); [123: 60586 / held[8]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65181 | Okinimesu mama | 2008 | vndb-v40956 (1995) | ambiguous-name-year | [122: v65181 / held[50]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65221 | happy end | 2018 | vndb-v38584 (2009) | ambiguous-name-year | [122: v65221 / held[51]](vndb-kana-bulk-review-20261102-r122.json); [123: 60644 / held[9]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65231 | Gift | 2024 | nextmoe-211869 (2005) | ambiguous-name-year | [122: v65231 / held[52]](vndb-kana-bulk-review-20261102-r122.json); [123: 60653 / held[10]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65289 | Overdrive | 2026 | vndb-v64371 (2003) | ambiguous-name-year | [122: v65289 / held[53]](vndb-kana-bulk-review-20261102-r122.json); [123: 60709 / held[11]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65298 | Che Ye Wei Mian | 2026 | vndb-v10013 (2012) | ambiguous-name-year | [122: v65298 / held[54]](vndb-kana-bulk-review-20261102-r122.json); [123: 60718 / held[12]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65314 | SnowDrop | 2015 | vndb-v112 (2000) | ambiguous-name-year | [122: v65314 / held[55]](vndb-kana-bulk-review-20261102-r122.json); [123: 60734 / held[13]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65352 | Nie | 2026 | vndb-v6889 (1999) | ambiguous-name-year | [122: v65352 / held[56]](vndb-kana-bulk-review-20261102-r122.json); [123: 60768 / held[14]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65400 | You+Me=? | 2022 | vndb-v58001 (2025) | ambiguous-name-year | [122: v65400 / held[57]](vndb-kana-bulk-review-20261102-r122.json); [123: 60815 / held[15]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65471 | "Snow" | 2002 | nextmoe-1990 (2003) | ambiguous-name-year | [122: v65471 / held[58]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65497 | LOVEgame | 2011 | vndb-v17374 (2004) | ambiguous-name-year | [122: v65497 / held[59]](vndb-kana-bulk-review-20261102-r122.json); [123: 60906 / held[16]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65518 | Innocent | 2005 | vndb-v21810 (1999); vndb-v62681 (2023) | ambiguous-name-year | [122: v65518 / held[60]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65538 | Tenohira | 2009 | vndb-v65112 (2006) | ambiguous-name-year | [122: v65538 / held[61]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65641 | Chikan Densha | 2003 | vndb-v11572 (2012) | ambiguous-name-year | [122: v65641 / held[62]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65648 | Blind Date | 2024 | vndb-v24988 (2018) | ambiguous-name-year | [122: v65648 / held[63]](vndb-kana-bulk-review-20261102-r122.json); [123: 61044 / held[17]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65663 | Imoutohime | 2002 | vndb-v23332 (2009) | ambiguous-name-year | [122: v65663 / held[64]](vndb-kana-bulk-review-20261102-r122.json) |
| 名称/年份/身份冲突 | vndb:v65703 | Do No Harm | 2026 | vndb-v56658 (2025) | ambiguous-name-year | [122: v65703 / held[65]](vndb-kana-bulk-review-20261102-r122.json); [123: 61098 / held[18]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65707 | S Dnyom Rozhdeniya! | 2018 | vndb-v14105 (2010) | ambiguous-name-year | [122: v65707 / held[66]](vndb-kana-bulk-review-20261102-r122.json); [123: 61155 / held[19]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65780 | My Valentine | 2022 | vndb-v55739 (2025) | ambiguous-name-year | [123: 61224 / held[20]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65787 | Journey | 2024 | ifdb-2752o3sh6y05ob1p (1989); ifdb-xehpx39rfnerjy1f (1979) | ambiguous-name-year | [123: 61231 / held[21]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v65948 | Soushitsu | 2026 | vndb-v14352 (2013) | ambiguous-name-year | [123: 61388 / held[22]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v66200 | Obezglavlennaja | 2026 | vndb-v28753 (2020) | ambiguous-name-year | [123: 61626 / held[23]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v66242 | Kakuriyo | 2023 | vndb-v11702 (2001) | ambiguous-name-year | [123: 61674 / held[24]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v66307 | Inferno | 2022 | vndb-v50065 (2011) | ambiguous-name-year | [123: 61732 / held[25]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v66309 | Insomnia | 2023 | ifdb-oy6ld63a47b9vn1x (1998) | ambiguous-name-year | [123: 61734 / held[26]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | vndb:v66462 | Sverkhnovaya! | 2021 | ifdb-4kzpaculjx4r2fxf (1987) | ambiguous-name-year | [123: 61872 / held[27]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:17krz4tzz4kbnjnq | The Challenge | 1987-01-01 00:00:00 | ifdb-snlb16yj8k3lsrf8 (2013) | name-year-conflict | [123: 17krz4tzz4kbnjnq / held[28]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:9dqos1v1iyb8q99p | Cosmos | 1989-01-01 00:00:00 | vndb-v17320 (2013) | name-year-conflict | [123: 9dqos1v1iyb8q99p / held[29]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:yzyinfws6b87ldhh | Shipwrecked | 2009-10-07 01:00:00 | ifdb-dbszwwmz3y1p4f2i (2016) | name-year-conflict | [123: yzyinfws6b87ldhh / held[30]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:11tnb08k1jov4hyl | Sorcerer of Claymorgue Castle | 1984-01-01 00:00:00 | ai-claymorgue (1983) | name-year-conflict | [123: 11tnb08k1jov4hyl / held[31]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:574yp5ttl1jzfrf5 | Shangri La | 2002-01-01 00:00:00 | vndb-v30660 (2021) | name-year-conflict | [123: 574yp5ttl1jzfrf5 / held[32]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:5g2v7r2amwqh5izg | Alien | 1982-01-01 00:00:00 | ifdb-d5jcsz4mn1bdqpxr (1988); ifdb-kp8y1zd5vc284d04 (1984) | name-year-conflict | [123: 5g2v7r2amwqh5izg / held[33]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:wyycuxu3epw1tmlf | Escape! | 2019-04-04 01:00:00 | nextmoe-7725 (2015) | name-year-conflict | [123: wyycuxu3epw1tmlf / held[34]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:2owjwbu11aharp0h | Stowaway | 2025-04-02 01:00:00 | ifdb-jwd9f2ba1om1oo4j (2004) | name-year-conflict | [123: 2owjwbu11aharp0h / held[35]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:1jt4xlcw9i3jvxzh | N O I R | 2017-10-01 01:00:00 | vndb-v36708 (2022) | name-year-conflict | [123: 1jt4xlcw9i3jvxzh / held[36]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:gti5j0nqvvqqvnzo | Perseus and Andromeda | 1983-01-01 00:00:00 | vndb-v33880 (2019) | name-year-conflict | [123: gti5j0nqvvqqvnzo / held[37]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:aj49e4zmd70ohnep | Sanctuary | 1989-01-01 00:00:00 | ifdb-0i9mv4y334ppy25a (1990) | name-year-conflict | [123: aj49e4zmd70ohnep / held[38]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:k7vjmsqait48fwhh | Detritus | 2013-06-23 01:00:00 | vndb-v39332 (2021) | name-year-conflict | [123: k7vjmsqait48fwhh / held[39]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:dn4ibijvklvljl56 | Cold Iron | 2017-01-01 00:00:00 | ifdb-x8ohk12d1a6f12ge (2011) | name-year-conflict | [123: dn4ibijvklvljl56 / held[40]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:wjcxcwm4x2cc5ao2 | Death Trap | 1981-01-01 00:00:00 | ifdb-grfr9thk88irowip (2021) | name-year-conflict | [123: wjcxcwm4x2cc5ao2 / held[41]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:narh8d4zgv7fa9is | Afuera | 2007-12-21 00:00:00 | vndb-v21828 (2016) | name-year-conflict | [123: narh8d4zgv7fa9is / held[42]](nextmoe-ifdb-bulk-review-20261102-r123.json) |
| 名称/年份/身份冲突 | ifdb:wnmn5ptfzi6nt64x | The Last Dragon | 1985-08-01 00:00:00 | vndb-v40596 (2022) | name-year-conflict | [123: wnmn5ptfzi6nt64x / held[43]](nextmoe-ifdb-bulk-review-20261102-r123.json) |

## 原始证据

- [第122批审计](vndb-kana-bulk-review-20261102-r122.json)
- [第123批审计](nextmoe-ifdb-bulk-review-20261102-r123.json)
- [两批汇总](basic-r122-r123-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
