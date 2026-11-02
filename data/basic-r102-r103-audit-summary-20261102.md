# 第102、103批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 102 | 1551 | 708 | 500 | 32 | 284 | 27 |
| 103 | 1546 | 555 | 500 | 33 | 216 | 242 |

## 279条暂存处理

VNDB输入51条、NextMoe输入228条；本轮从旧暂存入选279条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：49,841 → 50,841。

## 新续采位置

- VNDB：`v51204`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZORGcwTlRSOQ`
- IFDB：`5852`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共65条原始记录，按来源ID合并为53个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v49743 | Love is Blind | 2024 | vndb-v44934 (2006) | ambiguous-name-year | [102: v49743 / held[0]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49805 | requiem | 2001 | vndb-v3804 (2004) | ambiguous-name-year | [102: v49805 / held[1]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49838 | END | 2011 | vndb-v49443 (2003) | ambiguous-name-year | [102: v49838 / held[2]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49896 | Kaerimichi | 2012 | vndb-v32266 (2021) | ambiguous-name-year | [102: v49896 / held[3]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49907 | connect | 2011 | ifdb-t2sezaqjx8j89nnx (2008) | ambiguous-name-year | [102: v49907 / held[4]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49973 | LiFe | 2008 | vndb-v16565 (2014) | ambiguous-name-year | [102: v49973 / held[5]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49975 | Hydrangea | 2024 | vndb-v43849 (2012) | ambiguous-name-year | [102: v49975 / held[6]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v49979 | Snow Drop | 2014 | vndb-v112 (2000) | ambiguous-name-year | [102: v49979 / held[7]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50017 | Rib²on | 2002 | vndb-v9059 (1995) | ambiguous-name-year | [102: v50017 / held[8]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50070 | Happy valentines day | 2024 | vndb-v9888 (2012) | ambiguous-name-year | [102: v50070 / held[9]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50077 | Crossroads | 2023 | ifdb-cmj8xyhj3s20mcva (2015) | ambiguous-name-year | [102: v50077 / held[10]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50132 | Inside the Box | 2024 | vndb-v29204 (2006) | ambiguous-name-year | [102: v50132 / held[11]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50148 | LingerieS | 2024 | nextmoe-2550 (2001) | ambiguous-name-year | [102: v50148 / held[12]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50180 | Yasoukyoku | 2004 | vndb-v11026 (2006) | ambiguous-name-year | [102: v50180 / held[13]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50267 | Skhovanky | 2024 | ifdb-ljb863xxbw125k2g (1997) | ambiguous-name-year | [102: v50267 / held[14]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50338 | Imo Imo! | 2011 | vndb-v12432 (2013) | ambiguous-name-year | [102: v50338 / held[15]](vndb-kana-bulk-review-20261102-r102.json); [103: 47223 / held[0]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50382 | Dyspersija | 2024 | vndb-v15530 (2014) | ambiguous-name-year | [102: v50382 / held[16]](vndb-kana-bulk-review-20261102-r102.json); [103: 47262 / held[1]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 疑似版本/依赖内容 | vndb:v50388 | Maid-san Katsudou Shashinshuu | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [102: v50388 / held[17]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50443 | Dejavu | 2024 | ifdb-bhu49t1gxfwetcru (1993) | ambiguous-name-year | [102: v50443 / held[18]](vndb-kana-bulk-review-20261102-r102.json); [103: 47316 / held[2]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50517 | Toriko | 2007 | vndb-v14583 (1996) | ambiguous-name-year | [102: v50517 / held[19]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50521 | Dahlia | 2024 | vndb-v15862 (2014) | ambiguous-name-year | [102: v50521 / held[20]](vndb-kana-bulk-review-20261102-r102.json); [103: 47384 / held[3]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50583 | Sweet Nothings | 2024 | vndb-v17627 (2015) | ambiguous-name-year | [102: v50583 / held[21]](vndb-kana-bulk-review-20261102-r102.json); [103: 47443 / held[4]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50614 | Go-toubun no Hanayome: Gotopazu Story 2nd | 2024 | vndb-v42382 (2023) | ambiguous-name-year | [102: v50614 / held[22]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v50661 | Calling !! | 2024 | vndb-v6430 (2003) | ambiguous-name-year | [102: v50661 / held[23]](vndb-kana-bulk-review-20261102-r102.json); [103: 47516 / held[5]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50713 | Daisy Chain | 2024 | vndb-v21492 (2017) | ambiguous-name-year | [102: v50713 / held[24]](vndb-kana-bulk-review-20261102-r102.json); [103: 47564 / held[6]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50731 | Lost and Found | 2024 | ifdb-ntty23xwy1njd98p (2018) | ambiguous-name-year | [102: v50731 / held[25]](vndb-kana-bulk-review-20261102-r102.json); [103: 47580 / held[7]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50751 | SUDS | 2024 | ifdb-11xl0m4crt4pkqvt (1986) | ambiguous-name-year | [102: v50751 / held[26]](vndb-kana-bulk-review-20261102-r102.json); [103: 47600 / held[8]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50796 | Kami no Niwa | 2023 | vndb-v13463 (2007) | ambiguous-name-year | [102: v50796 / held[27]](vndb-kana-bulk-review-20261102-r102.json); [103: 47639 / held[9]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50906 | The Lair | 2024 | vndb-v32456 (2021) | ambiguous-name-year | [102: v50906 / held[28]](vndb-kana-bulk-review-20261102-r102.json); [103: 47737 / held[10]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v50921 | Jigsaw | 2010 | ifdb-28uhmejlntcbccqm (1995) | ambiguous-name-year | [102: v50921 / held[29]](vndb-kana-bulk-review-20261102-r102.json) |
| 名称/年份/身份冲突 | vndb:v51149 | Re:start | 2009 | vndb-v13496 (2006) | ambiguous-name-year | [102: v51149 / held[30]](vndb-kana-bulk-review-20261102-r102.json) |
| 来源日期冲突 | vndb:v51165 | White Noise | 2011 | vndb-v18356 (2015); NextMoe: 2010-02-07 | ambiguous-name-year; VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [102: v51165 / held[31]](vndb-kana-bulk-review-20261102-r102.json); [103: 47928 / held[11]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51313 | Petrichor | 2024 | nextmoe-1622 (2020) | ambiguous-name-year | [103: 48057 / held[12]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51408 | Summer With You | 2024 | vndb-v34177 (2022) | ambiguous-name-year | [103: 48145 / held[13]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 疑似版本/依赖内容 | vndb:v51482 | Veilcrest: Trial of The Arcane | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [103: 48208 / held[14]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51498 | REALITY | 2024 | nextmoe-22327 (2017) | ambiguous-name-year | [103: 48223 / held[15]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51574 | Lost And Found | 2024 | ifdb-ntty23xwy1njd98p (2018) | ambiguous-name-year | [103: 48297 / held[16]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51691 | Dead Zone | 2024 | vndb-v4657 (1986) | ambiguous-name-year | [103: 48403 / held[17]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51719 | Sanctuary | 2024 | ifdb-0i9mv4y334ppy25a (1990) | ambiguous-name-year | [103: 48428 / held[18]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | vndb:v51745 | tea party | 2024 | vndb-v14154 (2007) | ambiguous-name-year | [103: 48452 / held[19]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:sxf6c25bwme74cw9 | Jump | 2001-01-01 00:00:00 | vndb-v43879 (2023) | name-year-conflict | [103: sxf6c25bwme74cw9 / held[20]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:ed3hqbwx69eig068 | Dragon Slayer | 1984-01-01 00:00:00 | ifdb-2brd2ihbw9gsr7ua (1985) | name-year-conflict | [103: ed3hqbwx69eig068 / held[21]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:sc59pe9zg3ld8a0l | Eclipse | 1990-01-01 00:00:00 | vndb-v6522 (2011) | name-year-conflict | [103: sc59pe9zg3ld8a0l / held[22]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:acu9ag7o5mlg5eys | Paranoia | 2009-01-01 00:00:00 | ifdb-42vm6hiqadzy1xn7 (1986) | name-year-conflict | [103: acu9ag7o5mlg5eys / held[23]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:5zarqfzke417ujry | Parallel | 2008-02-19 00:00:00 | ifdb-3gby8gwsi4e5nteo (2014) | name-year-conflict | [103: 5zarqfzke417ujry / held[24]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:xmo87hjaydnz52o3 | Final Exam | 2015-10-01 01:00:00 | vndb-v40816 (2022) | name-year-conflict | [103: xmo87hjaydnz52o3 / held[25]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:f9s43tfh7jzg6q1p | Inspiration! | 2011-06-08 01:00:00 | ifdb-2n6vrsmrn310mucc (2001) | name-year-conflict | [103: f9s43tfh7jzg6q1p / held[26]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:yuek2bwjka7lbdvc | Amnesia | 1986-01-01 00:00:00 | basic-64e34fa44ed9 (2011) | name-year-conflict | [103: yuek2bwjka7lbdvc / held[27]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:o1dv4v9zxxfwbfbs | Cabin Fever | 2007-01-01 00:00:00 | nextmoe-30492 (2021) | name-year-conflict | [103: o1dv4v9zxxfwbfbs / held[28]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:eyb6bqqp39z67vdt | STRANDED | 2023-07-19 01:00:00 | nextmoe-33237 (2021) | name-year-conflict | [103: eyb6bqqp39z67vdt / held[29]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:9n2ep3rbby520xjr | Hallowe'en | 2000-01-01 00:00:00 | ifdb-a1c82gyqjqiv2ogo (2020) | name-year-conflict | [103: 9n2ep3rbby520xjr / held[30]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:bcr8ae8yncd4anse | Wish | 2007-09-30 00:00:00 | vndb-v64983 (2008) | name-year-conflict | [103: bcr8ae8yncd4anse / held[31]](nextmoe-ifdb-bulk-review-20261102-r103.json) |
| 名称/年份/身份冲突 | ifdb:h9oyhbl42nz2ruxg | Winter Wonderland | 1986-01-01 00:00:00 | vndb-v32504 (2021) | name-year-conflict | [103: h9oyhbl42nz2ruxg / held[32]](nextmoe-ifdb-bulk-review-20261102-r103.json) |

## 原始证据

- [第102批审计](vndb-kana-bulk-review-20261102-r102.json)
- [第103批审计](nextmoe-ifdb-bulk-review-20261102-r103.json)
- [两批汇总](basic-r102-r103-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
