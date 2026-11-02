# 第96、97批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 96 | 1442 | 584 | 500 | 41 | 271 | 46 |
| 97 | 1486 | 558 | 500 | 51 | 164 | 213 |

## 310条暂存处理

VNDB输入42条、NextMoe输入268条；本轮从旧暂存入选310条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：46,841 → 47,841。

## 新续采位置

- VNDB：`v46783`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZORFExTURSOQ`
- IFDB：`5197`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共92条原始记录，按来源ID合并为66个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 疑似版本/依赖内容 | vndb:v45393 | Yuganda Sekai de Dokusho demo | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [96: v45393 / held[0]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45401 | RoomNo.404 | 2024 | vndb-v44344 (2005) | ambiguous-name-year | [96: v45401 / held[1]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45407 | Changeling | 2023 | nextmoe-22745 (2019) | ambiguous-name-year | [96: v45407 / held[2]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45432 | A Fairy Tale | 2023 | vndb-v43400 (2011) | ambiguous-name-year | [96: v45432 / held[3]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45453 | Nightmare | 2010 | vndb-v7588 (2011) | ambiguous-name-year | [96: v45453 / held[4]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45521 | dependence | 2023 | vndb-v34357 (2021) | ambiguous-name-year | [96: v45521 / held[5]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45801 | Byte | 2023 | ifdb-86bcll3ug7fjush3 (1983) | ambiguous-name-year | [96: v45801 / held[6]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45836 | Phantasm | 2023 | vndb-v18987 (2005) | ambiguous-name-year | [96: v45836 / held[7]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45850 | labyrinth | 2023 | ifdb-5czip2mqeves47ot (2020) | ambiguous-name-year | [96: v45850 / held[8]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45852 | Reunion | 2023 | vndb-v13243 (2013) | ambiguous-name-year | [96: v45852 / held[9]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45854 | FREAK | 2023 | ifdb-q8z6by8d3e2u8fyt (1986) | ambiguous-name-year | [96: v45854 / held[10]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45880 | MINE | 2023 | vndb-v38931 (2022) | ambiguous-name-year | [96: v45880 / held[11]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45947 | The way home | 2023 | vndb-v21802 (2017) | ambiguous-name-year | [96: v45947 / held[12]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v45964 | HAPPYBIRTHDAY | 2022 | vndb-v14105 (2010) | ambiguous-name-year | [96: v45964 / held[13]](vndb-kana-bulk-review-20261102-r96.json); [97: 43386 / held[0]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46000 | Passage | 2023 | vndb-v43825 (2008) | ambiguous-name-year | [96: v46000 / held[14]](vndb-kana-bulk-review-20261102-r96.json); [97: 43420 / held[1]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46018 | HAPPY☆X’MAS | 2004 | vndb-v795 (2006) | ambiguous-name-year | [96: v46018 / held[15]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v46020 | In The Dark | 2023 | vndb-v40008 (2008) | ambiguous-name-year | [96: v46020 / held[16]](vndb-kana-bulk-review-20261102-r96.json); [97: 43437 / held[2]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46065 | If You Stay | 2023 | nextmoe-58540 (2026) | ambiguous-name-year | [96: v46065 / held[17]](vndb-kana-bulk-review-20261102-r96.json); [97: 43478 / held[3]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46150 | PARANOIA | 2018 | ifdb-42vm6hiqadzy1xn7 (1986) | ambiguous-name-year | [96: v46150 / held[18]](vndb-kana-bulk-review-20261102-r96.json); [97: 43550 / held[4]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46178 | Alice | 2023 | psk-alice (1984); vndb-v43194 (2023) | ambiguous-name-year | [96: v46178 / held[19]](vndb-kana-bulk-review-20261102-r96.json); [97: 43578 / held[5]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46195 | Loop | 2023 | vndb-v20113 (2016) | ambiguous-name-year | [96: v46195 / held[20]](vndb-kana-bulk-review-20261102-r96.json); [97: 43595 / held[6]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46220 | Written in the Stars | 2023 | vndb-v24421 (2018) | ambiguous-name-year | [96: v46220 / held[21]](vndb-kana-bulk-review-20261102-r96.json); [97: 43620 / held[7]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46224 | Let Them Eat Cake | 2023 | ifdb-n9s65i1uim5uxyol (2022) | ambiguous-name-year | [96: v46224 / held[22]](vndb-kana-bulk-review-20261102-r96.json); [97: 43624 / held[8]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46292 | LOVEMACHINE | 2023 | vndb-v23988 (2018) | ambiguous-name-year | [96: v46292 / held[23]](vndb-kana-bulk-review-20261102-r96.json); [97: 43687 / held[9]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46335 | Podarunok | 2023 | nextmoe-211869 (2005) | ambiguous-name-year | [96: v46335 / held[24]](vndb-kana-bulk-review-20261102-r96.json); [97: 43728 / held[10]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46346 | Love: Spice! | 2023 | vndb-v20865 (2017) | ambiguous-name-year | [96: v46346 / held[25]](vndb-kana-bulk-review-20261102-r96.json); [97: 43736 / held[11]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46387 | Fragment | 2023 | vndb-v29177 (2011) | ambiguous-name-year | [96: v46387 / held[26]](vndb-kana-bulk-review-20261102-r96.json); [97: 43775 / held[12]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46399 | Love Island: The Game | 2022 | vndb-v29705 (2018) | ambiguous-name-year | [96: v46399 / held[27]](vndb-kana-bulk-review-20261102-r96.json); [97: 43786 / held[13]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46438 | Re;versible | 2010 | nextmoe-4536 (2007) | ambiguous-name-year | [96: v46438 / held[28]](vndb-kana-bulk-review-20261102-r96.json); [97: 43822 / held[14]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46493 | Spokuta | 2023 | vndb-v44926 (2014) | ambiguous-name-year | [96: v46493 / held[29]](vndb-kana-bulk-review-20261102-r96.json); [97: 43875 / held[15]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 疑似版本/依赖内容 | vndb:v46515 | Akuma Demo Ore to Omae wa! -Yuujin ga Inma Datta Toki no Doutei Sotsugyou Kaihihou- | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [96: v46515 / held[30]](vndb-kana-bulk-review-20261102-r96.json); [97: 43893 / held[16]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46522 | Yandere-chan | 2023 | vndb-v10665 (2012) | ambiguous-name-year | [96: v46522 / held[31]](vndb-kana-bulk-review-20261102-r96.json); [97: 43900 / held[17]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46560 | Hello, world | 2023 | g599 (2002) | ambiguous-name-year | [96: v46560 / held[32]](vndb-kana-bulk-review-20261102-r96.json); [97: 43931 / held[18]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46601 | New Earth | 2023 | vndb-v29440 (2021) | ambiguous-name-year | [96: v46601 / held[33]](vndb-kana-bulk-review-20261102-r96.json); [97: 43971 / held[19]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46627 | Delusion | 2023 | vndb-v37433 (2022) | ambiguous-name-year | [96: v46627 / held[34]](vndb-kana-bulk-review-20261102-r96.json) |
| 名称/年份/身份冲突 | vndb:v46666 | Resonance | 2022 | ifdb-bpwvrsiv73brmexc (2009) | ambiguous-name-year | [96: v46666 / held[35]](vndb-kana-bulk-review-20261102-r96.json); [97: 44027 / held[20]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46690 | Eternity | 2023 | vndb-v12269 (2006) | ambiguous-name-year | [96: v46690 / held[36]](vndb-kana-bulk-review-20261102-r96.json); [97: 44050 / held[21]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46702 | one last time. | 2023 | vndb-v23782 (2018) | ambiguous-name-year | [96: v46702 / held[37]](vndb-kana-bulk-review-20261102-r96.json); [97: 44060 / held[22]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46735 | Destination | 2022 | vndb-v42796 (2023) | ambiguous-name-year | [96: v46735 / held[38]](vndb-kana-bulk-review-20261102-r96.json); [97: 44090 / held[23]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46736 | Sisters | 2023 | nextmoe-15018 (2010) | ambiguous-name-year | [96: v46736 / held[39]](vndb-kana-bulk-review-20261102-r96.json); [97: 44091 / held[24]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46763 | The Island | 2023 | ifdb-9yv2fzucjovhlha0 (2012) | ambiguous-name-year | [96: v46763 / held[40]](vndb-kana-bulk-review-20261102-r96.json); [97: 44116 / held[25]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46834 | Shadows of the past | 2023 | ifdb-d3aadvqav48oqnmo (1990) | ambiguous-name-year | [97: 44172 / held[26]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46837 | Convergence | 2023 | vndb-v31169 (2017) | ambiguous-name-year | [97: 44175 / held[27]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46842 | Another Day | 2023 | vndb-v33415 (2021); vndb-v44520 (2023) | ambiguous-name-year | [97: 44180 / held[28]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46888 | Recollection | 2023 | vndb-v15746 (2014) | ambiguous-name-year | [97: 44218 / held[29]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46904 | After Party | 2021 | g1538 (2019) | ambiguous-name-year | [97: 44234 / held[30]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46907 | Fairy Tale: Little Red Riding Hood and the Cursed Forest | 2024 | vndb-v11102 (2012) | ambiguous-name-year | [97: 44237 / held[31]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46932 | Vampire Hunter | 2023 | vndb-v27233 (2001) | ambiguous-name-year | [97: 44260 / held[32]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46936 | Eternity | 2023 | vndb-v12269 (2006) | ambiguous-name-year | [97: 44264 / held[33]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v46956 | O Castelo | 2023 | ifdb-t00ivo2h14egzpnt (1983) | ambiguous-name-year | [97: 44281 / held[34]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v47213 | S1LENT_H1LL.EXE | 2022 | konami-sh1 (1999) | ambiguous-name-year | [97: 44491 / held[35]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | vndb:v47224 | Trick or Treat | 2023 | nextmoe-19648 (2014) | ambiguous-name-year | [97: 44500 / held[36]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:rwgmq79vq4wjxeaf | Blue Sky | 2002-08-11 01:00:00 | ifdb-gtwpx8ahp5et9nrz (2004) | name-year-conflict | [97: rwgmq79vq4wjxeaf / held[37]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:2nr1txpoz7lepqa4 | Buried | 2012-01-01 00:00:00 | vndb-v19753 (2016) | name-year-conflict | [97: 2nr1txpoz7lepqa4 / held[38]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:3goz0lfjaey5zp2b | The Maze | 2009-11-28 01:00:00 | ifdb-c83dw9sx4lcjp6m1 (2025) | name-year-conflict | [97: 3goz0lfjaey5zp2b / held[39]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:h1v51dfn61398fx3 | Secret | 2023-07-06 01:00:00 | vndb-v15180 (1997) | name-year-conflict | [97: h1v51dfn61398fx3 / held[40]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:ag3hyv123dhr0rkv | The Wizard and the Princess | 1980-01-01 00:00:00 | g057 (1980); melbournehouse-wizard-princess (1982) | name-year-conflict | [97: ag3hyv123dhr0rkv / held[41]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:flq62fa4u4kho5zb | Mission Asteroid | 1981-01-01 00:00:00 | sierra-mission-asteroid (1980) | name-year-conflict | [97: flq62fa4u4kho5zb / held[42]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:u1ibyqknb2vie6xm | Memoria | 2020-07-24 01:00:00 | nextmoe-5031 (2009) | name-year-conflict | [97: u1ibyqknb2vie6xm / held[43]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:og56z5wxbsq1qfan | Alice in Wonderland | 1989-01-01 00:00:00 | g1602 (1985) | name-year-conflict | [97: og56z5wxbsq1qfan / held[44]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:icyceot6zu3iynbp | Treasure Island | 1991-01-01 00:00:00 | g1603 (1985) | name-year-conflict | [97: icyceot6zu3iynbp / held[45]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:vcnqo6gaz260fl1u | Overboard! | 2021-06-02 01:00:00 | g1409 (2021); supp26-inkle-overboard (2021) | name-year-conflict | [97: vcnqo6gaz260fl1u / held[46]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:h2lul8gpg1ajchce | Tundra | 1993-01-01 00:00:00 | ifdb-90ljpmjxyd34d837 (1998) | name-year-conflict | [97: h2lul8gpg1ajchce / held[47]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:suogk7bg7ydueggf | Treasure Island | 2012-04-25 01:00:00 | g1603 (1985) | name-year-conflict | [97: suogk7bg7ydueggf / held[48]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:j3dgszmb0qqpe1p3 | The House | 1992-01-01 00:00:00 | ifdb-83noiwzup8nsasob (2007) | name-year-conflict | [97: j3dgszmb0qqpe1p3 / held[49]](nextmoe-ifdb-bulk-review-20261102-r97.json) |
| 名称/年份/身份冲突 | ifdb:v0hmaiqnnpi0ccti | The Test | 1992-01-01 00:00:00 | vndb-v35318 (2022) | name-year-conflict | [97: v0hmaiqnnpi0ccti / held[50]](nextmoe-ifdb-bulk-review-20261102-r97.json) |

## 原始证据

- [第96批审计](vndb-kana-bulk-review-20261102-r96.json)
- [第97批审计](nextmoe-ifdb-bulk-review-20261102-r97.json)
- [两批汇总](basic-r96-r97-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
