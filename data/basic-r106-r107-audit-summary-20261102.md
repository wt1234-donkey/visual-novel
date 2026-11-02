# 第106、107批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 106 | 1365 | 525 | 500 | 35 | 286 | 19 |
| 107 | 1532 | 534 | 500 | 51 | 224 | 223 |

## 276条暂存处理

VNDB输入65条、NextMoe输入211条；本轮从旧暂存入选276条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：51,841 → 52,841。

## 新续采位置

- VNDB：`v53978`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVEE1TlRaOQ`
- IFDB：`6284`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共86条原始记录，按来源ID合并为61个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 疑似版本/依赖内容 | vndb:v52668 | Fan Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [106: v52668 / held[0]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v52809 | Obsession | 2024 | vndb-v40659 (2006) | ambiguous-name-year | [106: v52809 / held[1]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v52887 | Genesis | 2024 | ifdb-o7nq769ihazfchxu (2012) | ambiguous-name-year | [106: v52887 / held[2]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v52935 | All Hallow's Eve | 2024 | ifdb-xtpiuzfe41bm598k (2010) | ambiguous-name-year | [106: v52935 / held[3]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v52939 | As Dusk Falls | 2024 | g964 (2022) | ambiguous-name-year | [106: v52939 / held[4]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v53004 | Undercover | 2025 | ifdb-3l7sdvp1cdycfal2 (1992) | ambiguous-name-year | [106: v53004 / held[5]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v53072 | IRIS | 2024 | nextmoe-465 (2018) | ambiguous-name-year | [106: v53072 / held[6]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v53094 | Natsu Sora Shoujo | 2012 | vndb-v4319 (2005) | ambiguous-name-year | [106: v53094 / held[7]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v53122 | Daojishi | 2024 | vndb-v13143 (2002) | ambiguous-name-year | [106: v53122 / held[8]](vndb-kana-bulk-review-20261102-r106.json); [107: 49698 / held[0]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53214 | My sister | 2010 | vndb-v12985 (2013); vndb-v4884 (1999) | ambiguous-name-year | [106: v53214 / held[9]](vndb-kana-bulk-review-20261102-r106.json); [107: 49775 / held[1]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53221 | Maze I | 2021 | vndb-v6159 (2000) | ambiguous-name-year | [106: v53221 / held[10]](vndb-kana-bulk-review-20261102-r106.json); [107: 49781 / held[2]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53241 | m (エム) | 2010 | vndb-v5237 (2009) | ambiguous-name-year | [106: v53241 / held[11]](vndb-kana-bulk-review-20261102-r106.json); [107: 49799 / held[3]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53284 | Private Teacher | 1999 | vndb-v14512 (1996); vndb-v53969 (2009) | ambiguous-name-year | [106: v53284 / held[12]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v53287 | Hide and seek | 2017 | ifdb-ljb863xxbw125k2g (1997) | ambiguous-name-year | [106: v53287 / held[13]](vndb-kana-bulk-review-20261102-r106.json); [107: 49842 / held[4]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53301 | Cave | 2021 | ifdb-u94un0rox6hbn4sl (1999) | ambiguous-name-year | [106: v53301 / held[14]](vndb-kana-bulk-review-20261102-r106.json); [107: 49853 / held[5]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53398 | Picture perfect | 2023 | nextmoe-28207 (2021) | ambiguous-name-year | [106: v53398 / held[15]](vndb-kana-bulk-review-20261102-r106.json); [107: 49936 / held[6]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 疑似版本/依赖内容 | vndb:v53407 | Thot on Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [106: v53407 / held[16]](vndb-kana-bulk-review-20261102-r106.json); [107: 49944 / held[7]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53410 | Alice | 2024 | psk-alice (1984); vndb-v43194 (2023) | ambiguous-name-year | [106: v53410 / held[17]](vndb-kana-bulk-review-20261102-r106.json); [107: 49946 / held[8]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53568 | A Million Promises | 2017 | vndb-v3909 (2010) | ambiguous-name-year | [106: v53568 / held[18]](vndb-kana-bulk-review-20261102-r106.json); [107: 50088 / held[9]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53578 | Put domoy | 2018 | vndb-v21802 (2017) | ambiguous-name-year | [106: v53578 / held[19]](vndb-kana-bulk-review-20261102-r106.json); [107: 50097 / held[10]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53617 | Incubus | 2023 | vndb-v62665 (2006) | ambiguous-name-year | [106: v53617 / held[20]](vndb-kana-bulk-review-20261102-r106.json); [107: 50130 / held[11]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53633 | Pinup | 2024 | vndb-v13521 (2000) | ambiguous-name-year | [106: v53633 / held[21]](vndb-kana-bulk-review-20261102-r106.json); [107: 50146 / held[12]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53667 | The Frontier | 2024 | vndb-v23582 (2018) | ambiguous-name-year | [106: v53667 / held[22]](vndb-kana-bulk-review-20261102-r106.json); [107: 50175 / held[13]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53693 | Night Drive | 2024 | ifdb-2174obt391f36ave (2017) | ambiguous-name-year | [106: v53693 / held[23]](vndb-kana-bulk-review-20261102-r106.json); [107: 50201 / held[14]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53706 | SCAVENGER | 2024 | ifdb-ii7j0kliujc4k8wf (2003) | ambiguous-name-year | [106: v53706 / held[24]](vndb-kana-bulk-review-20261102-r106.json); [107: 50213 / held[15]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53730 | TOY BOX | 2024 | vndb-v65093 (2009) | ambiguous-name-year | [106: v53730 / held[25]](vndb-kana-bulk-review-20261102-r106.json); [107: 50234 / held[16]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53758 | CRUSH!!! | 2024 | vndb-v4926 (2004) | ambiguous-name-year | [106: v53758 / held[26]](vndb-kana-bulk-review-20261102-r106.json); [107: 50261 / held[17]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53761 | Afterglow | 2021 | vndb-v31539 (2015) | ambiguous-name-year | [106: v53761 / held[27]](vndb-kana-bulk-review-20261102-r106.json); [107: 50263 / held[18]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53798 | Polar Opposites | 2024 | vndb-v38969 (2021) | ambiguous-name-year | [106: v53798 / held[28]](vndb-kana-bulk-review-20261102-r106.json); [107: 50297 / held[19]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 疑似版本/依赖内容 | vndb:v53821 | Toraware no Dark Elf ~Lod*ss War Heroine Assault Collection  II~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [106: v53821 / held[29]](vndb-kana-bulk-review-20261102-r106.json); [107: 50317 / held[20]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53829 | Purple | 2024 | vndb-v13597 (2012) | ambiguous-name-year | [106: v53829 / held[30]](vndb-kana-bulk-review-20261102-r106.json); [107: 50323 / held[21]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53844 | Solstice | 2024 | nextmoe-16698 (2015) | ambiguous-name-year | [106: v53844 / held[31]](vndb-kana-bulk-review-20261102-r106.json); [107: 50338 / held[22]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 疑似版本/依赖内容 | vndb:v53896 | KareKano Trial ~Toki o Kakeru Tokimeki Daisakusen♪~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [106: v53896 / held[32]](vndb-kana-bulk-review-20261102-r106.json); [107: 50388 / held[23]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53926 | Iinari | 2008 | nextmoe-7004 (2005) | ambiguous-name-year | [106: v53926 / held[33]](vndb-kana-bulk-review-20261102-r106.json) |
| 名称/年份/身份冲突 | vndb:v53951 | Steal My Heart | 2024 | vndb-v27795 (2019) | ambiguous-name-year | [106: v53951 / held[34]](vndb-kana-bulk-review-20261102-r106.json); [107: 50440 / held[24]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v53991 | FRAGILE | 2017 | vndb-v65088 (2009) | ambiguous-name-year | [107: 50479 / held[25]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v54004 | A Night Out | 2018 | vndb-v29091 (2020) | ambiguous-name-year | [107: 50492 / held[26]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v54055 | Forgotten Memories | 2024 | vndb-v34272 (2021) | ambiguous-name-year | [107: 50539 / held[27]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v54076 | Kiseki | 2024 | vndb-v44804 (2003) | ambiguous-name-year | [107: 50558 / held[28]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 来源日期冲突 | vndb:v54213 | Sargasso | 2024-12-28 | NextMoe: 2022-04-08 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [107: 50670 / held[29]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v54474 | Last Day | 2021 | ifdb-9u8zksm7e51t3bar (2020) | ambiguous-name-year | [107: 50917 / held[30]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v54490 | Day and Night | 2019 | vndb-v29431 (2020) | ambiguous-name-year | [107: 50932 / held[31]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | vndb:v54510 | Guardian | 2010 | nextmoe-22596 (2010); vndb-v9825 (1999) | ambiguous-name-year | [107: 50949 / held[32]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:r8f7u0w1gpw3ukbv | Nightmare | 1986-01-01 00:00:00 | vndb-v7588 (2011) | name-year-conflict | [107: r8f7u0w1gpw3ukbv / held[33]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:3sxrsiyp4rfbc2en | THE TOWER | 2025-06-26 01:00:00 | ifdb-nwuj3s93o2p9fxw1 (2018) | name-year-conflict | [107: 3sxrsiyp4rfbc2en / held[34]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:29jlztfxpfz4n581 | Labyrinth | 2024-03-17 01:00:00 | ifdb-5czip2mqeves47ot (2020) | name-year-conflict | [107: 29jlztfxpfz4n581 / held[35]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:iv8ndid1agp0e95v | Cave Adventure | 2007-07-18 01:00:00 | ifdb-j82egac597oy0z29 (1988) | name-year-conflict | [107: iv8ndid1agp0e95v / held[36]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:57nmjxa6i78konl7 | Castle Adventure | 1985-01-01 00:00:00 | ifdb-mz7tsvrsrrqhddhw (1984) | name-year-conflict | [107: 57nmjxa6i78konl7 / held[37]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:a1ds9l2vkodxtmxw | Serendipity | 1994-01-01 00:00:00 | vndb-v12906 (2013) | name-year-conflict | [107: a1ds9l2vkodxtmxw / held[38]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:u02ugbslonoxycd1 | Save the World! | 2014-01-01 00:00:00 | vndb-v42869 (2023) | name-year-conflict | [107: u02ugbslonoxycd1 / held[39]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:ox79nq87mllk44qo | DEADLINE | 2019-08-02 01:00:00 | g003 (1982); vndb-v42823 (2022) | name-year-conflict | [107: ox79nq87mllk44qo / held[40]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:mvh6n0to3p3wd301 | Blue | 2022-04-29 01:00:00 | vndb-v538 (2002) | name-year-conflict | [107: mvh6n0to3p3wd301 / held[41]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:daojnyuat3i5s7rm | Asylum | 1985-01-01 00:00:00 | vndb-v7692 (2003) | name-year-conflict | [107: daojnyuat3i5s7rm / held[42]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:cyn9p3cjnwrbkemi | Elements | 2001-01-01 00:00:00 | vndb-v30643 (2019) | name-year-conflict | [107: cyn9p3cjnwrbkemi / held[43]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:d9yxpfd1sr2ccol4 | INSOMNIA | 2023-04-19 01:00:00 | ifdb-oy6ld63a47b9vn1x (1998) | name-year-conflict | [107: d9yxpfd1sr2ccol4 / held[44]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:r67ofzas8p6y0ay4 | My Angel | 2000-01-01 00:00:00 | vndb-v43321 (2023) | name-year-conflict | [107: r67ofzas8p6y0ay4 / held[45]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:m2al2etgqh318hin | The Dark Tower | 1992-01-01 00:00:00 | ifdb-ehb3dxvs2e9lseop (2002) | name-year-conflict | [107: m2al2etgqh318hin / held[46]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:bmwt5ia96dih8bus | Disconnected | 2014-01-01 00:00:00 | vndb-v44505 (2023) | name-year-conflict | [107: bmwt5ia96dih8bus / held[47]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:zws1j2x2yiqywywi | Masquerade | 2000-01-01 00:00:00 | ifdb-zvi59g8krupjxhvz (1983) | name-year-conflict | [107: zws1j2x2yiqywywi / held[48]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:k2r7t7m6jm6vdq2y | Destiny | 1987-01-01 00:00:00 | vndb-v5592 (2002) | name-year-conflict | [107: k2r7t7m6jm6vdq2y / held[49]](nextmoe-ifdb-bulk-review-20261102-r107.json) |
| 名称/年份/身份冲突 | ifdb:s7i1114kfhnafp4r | Dungeon | 1985-01-01 00:00:00 | ifdb-q84zlpfr3x855ukd (2006) | name-year-conflict | [107: s7i1114kfhnafp4r / held[50]](nextmoe-ifdb-bulk-review-20261102-r107.json) |

## 原始证据

- [第106批审计](vndb-kana-bulk-review-20261102-r106.json)
- [第107批审计](nextmoe-ifdb-bulk-review-20261102-r107.json)
- [两批汇总](basic-r106-r107-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
