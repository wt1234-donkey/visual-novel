# 第98、99批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 98 | 1346 | 535 | 500 | 29 | 210 | 72 |
| 99 | 1532 | 595 | 500 | 30 | 134 | 273 |

## 259条暂存处理

VNDB输入46条、NextMoe输入213条；本轮从旧暂存入选259条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：47,841 → 48,841。

## 新续采位置

- VNDB：`v48125`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZORFU0TmpOOQ`
- IFDB：`5416`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共59条原始记录，按来源ID合并为47个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v46834 | Shadows of the past | 2023 | ifdb-d3aadvqav48oqnmo (1990) | ambiguous-name-year | [98: v46834 / held[0]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46837 | Convergence | 2023 | vndb-v31169 (2017) | ambiguous-name-year | [98: v46837 / held[1]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46842 | Another Day | 2023 | vndb-v33415 (2021); vndb-v44520 (2023) | ambiguous-name-year | [98: v46842 / held[2]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46888 | Recollection | 2023 | vndb-v15746 (2014) | ambiguous-name-year | [98: v46888 / held[3]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46904 | After Party | 2021 | g1538 (2019) | ambiguous-name-year | [98: v46904 / held[4]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46907 | Fairy Tale: Little Red Riding Hood and the Cursed Forest | 2024 | vndb-v11102 (2012) | ambiguous-name-year | [98: v46907 / held[5]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46932 | Vampire Hunter | 2023 | vndb-v27233 (2001) | ambiguous-name-year | [98: v46932 / held[6]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v46936 | Eternity | 2023 | vndb-v12269 (2006) | ambiguous-name-year | [98: v46936 / held[7]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47213 | S1LENT_H1LL.EXE | 2022 | konami-sh1 (1999) | ambiguous-name-year | [98: v47213 / held[8]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47224 | Trick or Treat | 2023 | nextmoe-19648 (2014) | ambiguous-name-year | [98: v47224 / held[9]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47235 | Tunnel Vision | 2023 | vndb-v15974 (2014) | ambiguous-name-year | [98: v47235 / held[10]](vndb-kana-bulk-review-20261102-r98.json); [99: 44511 / held[0]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v47299 | White Blood | 2023 | vndb-v41468 (2022) | ambiguous-name-year | [98: v47299 / held[11]](vndb-kana-bulk-review-20261102-r98.json); [99: 44570 / held[1]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v47325 | Xiari Wuyu | 1992 | nextmoe-30952 (2021) | ambiguous-name-year | [98: v47325 / held[12]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47547 | Unravel trigger | 2024 | nextmoe-279 (2007) | ambiguous-name-year | [98: v47547 / held[13]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47616 | Mother | 2023 | vndb-v30967 (2021) | ambiguous-name-year | [98: v47616 / held[14]](vndb-kana-bulk-review-20261102-r98.json); [99: 44848 / held[2]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v47678 | WILD CARD | 2000 | square-wildcard (2001) | ambiguous-name-year | [98: v47678 / held[15]](vndb-kana-bulk-review-20261102-r98.json) |
| 疑似版本/依赖内容 | vndb:v47814 | Dokodemo Dare to demo Sex Kyokashou THE GAME ~Masao no Yaritai Houdai 16-nin Haramase Bukatsudou~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [98: v47814 / held[16]](vndb-kana-bulk-review-20261102-r98.json); [99: 45027 / held[3]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v47847 | Angel | 2023 | g705 (1993) | ambiguous-name-year | [98: v47847 / held[17]](vndb-kana-bulk-review-20261102-r98.json); [99: 45056 / held[4]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 疑似版本/依赖内容 | vndb:v47865 | Patch Works | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [98: v47865 / held[18]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47912 | Trouble Travel | 2001 | vndb-v14468 (1999) | ambiguous-name-year | [98: v47912 / held[19]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v47920 | Atropos | 2022 | g848 (2018) | ambiguous-name-year | [98: v47920 / held[20]](vndb-kana-bulk-review-20261102-r98.json); [99: 45119 / held[5]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v47929 | Flotsam | 2023 | ifdb-tvsfql0tujacs2sz (2001) | ambiguous-name-year | [98: v47929 / held[21]](vndb-kana-bulk-review-20261102-r98.json); [99: 45128 / held[6]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 疑似版本/依赖内容 | vndb:v47956 | Koi ni wa Amae ga Hitsuyou Desu ~Motto Amaete Morau Dake MiniFanDisc | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [98: v47956 / held[22]](vndb-kana-bulk-review-20261102-r98.json) |
| 疑似版本/依赖内容 | vndb:v48012 | Futanari Chiryou no Mahouyaku ~Demo, Okusuri Nomu to Shasei Shitakute Gaman Dekinakunacchau no~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [98: v48012 / held[23]](vndb-kana-bulk-review-20261102-r98.json); [99: 45198 / held[7]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48020 | Sky | 2001 | vndb-v3724 (2002) | ambiguous-name-year | [98: v48020 / held[24]](vndb-kana-bulk-review-20261102-r98.json) |
| 名称/年份/身份冲突 | vndb:v48034 | HELLO,WORLD!^▼^ | 2023 | g599 (2002) | ambiguous-name-year | [98: v48034 / held[25]](vndb-kana-bulk-review-20261102-r98.json); [99: 45217 / held[8]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48042 | Noriko | 2018 | g019 (1988) | ambiguous-name-year | [98: v48042 / held[26]](vndb-kana-bulk-review-20261102-r98.json); [99: 45225 / held[9]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48070 | mind. | 2019 | vndb-v10152 (1998) | ambiguous-name-year | [98: v48070 / held[27]](vndb-kana-bulk-review-20261102-r98.json); [99: 45250 / held[10]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48109 | Ame Nochi Hare | 2013 | vndb-v46412 (2008) | ambiguous-name-year | [98: v48109 / held[28]](vndb-kana-bulk-review-20261102-r98.json); [99: 45285 / held[11]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 来源日期冲突 | vndb:v48165 | Spy Mission ~Kanojo wa Ossan no Maid~ | 2023-02-17 | NextMoe: 2022-09-10 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [99: 45336 / held[12]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48180 | Copycat | 2016 | vndb-v35558 (2022) | ambiguous-name-year | [99: 45351 / held[13]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48268 | Happy Birthday | 2023 | vndb-v14105 (2010) | ambiguous-name-year | [99: 45432 / held[14]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 来源日期冲突 | vndb:v48623 | Niku Choukyou ~Boku no Megami ga Niku Dorei~ | 2018-06-18 | NextMoe: 2012-06-18 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [99: 45743 / held[15]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | vndb:v48647 | One More Time | 2017 | vndb-v38380 (2016) | ambiguous-name-year | [99: 45767 / held[16]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 来源日期冲突 | vndb:v48694 | Mixpirit | 2021-01-17 | NextMoe: 2020-10-11 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [99: 45811 / held[17]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:vtuf6hfo9aj5xs64 | Winter Wonderland | 1999-01-01 00:00:00 | vndb-v32504 (2021) | name-year-conflict | [99: vtuf6hfo9aj5xs64 / held[18]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:9zot2l65fz5w71gm | Detention | 2013-08-27 01:00:00 | g1413 (2017); supp26-redcandle (2017) | name-year-conflict | [99: 9zot2l65fz5w71gm / held[19]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:ify2fa74spuft3kl | Excalibur | 2021-04-02 01:00:00 | ifdb-q3isw8j98nnz6gm3 (1990) | name-year-conflict | [99: ify2fa74spuft3kl / held[20]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:tlyk69fz5pmbwhbp | (untitled) | 1999-01-01 00:00:00 | vndb-v7504 (2010) | name-year-conflict | [99: tlyk69fz5pmbwhbp / held[21]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:jd11p084y6h9ghcv | Phantasmagoria | 2020-10-31 01:00:00 | g1127 (1995) | name-year-conflict | [99: jd11p084y6h9ghcv / held[22]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:2j2pmgclwk9jitsu | Top Secret | 1985-08-01 00:00:00 | ifdb-nqpdkwrujhtfqof0 (1986) | name-year-conflict | [99: 2j2pmgclwk9jitsu / held[23]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:4i4vtdfnuybgmvv7 | Moving Day | 2016-04-22 01:00:00 | vndb-v26936 (2019) | name-year-conflict | [99: 4i4vtdfnuybgmvv7 / held[24]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:04quwg97k5ng9nqd | Paranoia | 1987-02-01 01:00:00 | ifdb-42vm6hiqadzy1xn7 (1986) | name-year-conflict | [99: 04quwg97k5ng9nqd / held[25]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:rlxb5i0vjrnfr6x9 | Ghost Town | 1980-01-01 00:00:00 | ai-ghost-town (1980); microcabin-ghost (1984) | name-year-conflict | [99: rlxb5i0vjrnfr6x9 / held[26]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:lkecgaio416qrs20 | Hades | 1996-01-01 00:00:00 | ifdb-jy5c0hlbjfxsclog (1989) | name-year-conflict | [99: lkecgaio416qrs20 / held[27]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:ee0z3jeyi82unr1t | A Mother's Love | 2013-12-14 01:00:00 | nextmoe-26068 (2022) | name-year-conflict | [99: ee0z3jeyi82unr1t / held[28]](nextmoe-ifdb-bulk-review-20261102-r99.json) |
| 名称/年份/身份冲突 | ifdb:6mqh1t7b85tckuxs | Legacy | 1987-01-01 00:00:00 | vndb-v42509 (2023) | name-year-conflict | [99: 6mqh1t7b85tckuxs / held[29]](nextmoe-ifdb-bulk-review-20261102-r99.json) |

## 原始证据

- [第98批审计](vndb-kana-bulk-review-20261102-r98.json)
- [第99批审计](nextmoe-ifdb-bulk-review-20261102-r99.json)
- [两批汇总](basic-r98-r99-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
