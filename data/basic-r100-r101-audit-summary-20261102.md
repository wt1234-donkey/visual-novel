# 第100、101批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 100 | 1572 | 720 | 500 | 26 | 275 | 51 |
| 101 | 1491 | 538 | 500 | 37 | 188 | 228 |

## 345条暂存处理

用户本轮填写354条；第98、99批原审计实际为345条（72＋273），本轮按这345条实际记录逐项复核。

VNDB输入72条、NextMoe输入273条；本轮从旧暂存入选345条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：48,841 → 49,841。

## 新续采位置

- VNDB：`v49669`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZORGN4TmpkOQ`
- IFDB：`5634`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共63条原始记录，按来源ID合并为51个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v48180 | Copycat | 2016 | vndb-v35558 (2022) | ambiguous-name-year | [100: v48180 / held[0]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48268 | Happy Birthday | 2023 | vndb-v14105 (2010) | ambiguous-name-year | [100: v48268 / held[1]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48334 | Yoru no Tobari | 2001 | vndb-v13358 (2012) | ambiguous-name-year | [100: v48334 / held[2]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48363 | Valhalla | 2001 | g114 (1983) | ambiguous-name-year | [100: v48363 / held[3]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48431 | Flower | 2000 | vndb-v30494 (2020) | ambiguous-name-year | [100: v48431 / held[4]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48485 | MiST | 2001 | nextmoe-33415 (2022) | ambiguous-name-year | [100: v48485 / held[5]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48490 | Blue Blood | 2003 | vndb-v5640 (2007) | ambiguous-name-year | [100: v48490 / held[6]](vndb-kana-bulk-review-20261102-r100.json) |
| 疑似版本/依赖内容 | vndb:v48591 | Mana '94 ~Demo Yappari Kawa ga Suki! II | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [100: v48591 / held[7]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48647 | One More Time | 2017 | vndb-v38380 (2016) | ambiguous-name-year | [100: v48647 / held[8]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v48833 | The Creature | 2023 | vndb-v36235 (2021) | ambiguous-name-year | [100: v48833 / held[9]](vndb-kana-bulk-review-20261102-r100.json); [101: 45934 / held[0]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v48841 | .EXE | 2022 | nextmoe-206 (2007) | ambiguous-name-year | [100: v48841 / held[10]](vndb-kana-bulk-review-20261102-r100.json); [101: 45939 / held[1]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v48934 | The Tower | 2021 | ifdb-nwuj3s93o2p9fxw1 (2018) | ambiguous-name-year | [100: v48934 / held[11]](vndb-kana-bulk-review-20261102-r100.json); [101: 46026 / held[2]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v48949 | Lost | 2023 | vndb-v14352 (2013) | ambiguous-name-year | [100: v48949 / held[12]](vndb-kana-bulk-review-20261102-r100.json); [101: 46040 / held[3]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v48950 | Safe House | 2023 | ifdb-8e1v6jfzud5exkjg (2010) | ambiguous-name-year | [100: v48950 / held[13]](vndb-kana-bulk-review-20261102-r100.json); [101: 46041 / held[4]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v48973 | Santa's Secret | 2023 | vndb-v24929 (2018) | ambiguous-name-year | [100: v48973 / held[14]](vndb-kana-bulk-review-20261102-r100.json); [101: 46062 / held[5]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49166 | Falling Star | 2024 | vndb-v48638 (2023) | ambiguous-name-year | [100: v49166 / held[15]](vndb-kana-bulk-review-20261102-r100.json); [101: 46221 / held[6]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49193 | Jabberwocky | 2023 | vndb-v13382 (2013) | ambiguous-name-year | [100: v49193 / held[16]](vndb-kana-bulk-review-20261102-r100.json); [101: 46247 / held[7]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49196 | Dear | 2001 | vndb-v49804 (1999) | ambiguous-name-year | [100: v49196 / held[17]](vndb-kana-bulk-review-20261102-r100.json) |
| 疑似版本/依赖内容 | vndb:v49227 | Koibana Ren'ai - Mini Fandisk -  After Festival | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [100: v49227 / held[18]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v49252 | Tail Tale | 2023 | vndb-v994 (2003) | ambiguous-name-year | [100: v49252 / held[19]](vndb-kana-bulk-review-20261102-r100.json); [101: 46298 / held[8]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49293 | STRANDED | 2023 | nextmoe-33237 (2021) | ambiguous-name-year | [100: v49293 / held[20]](vndb-kana-bulk-review-20261102-r100.json); [101: 46329 / held[9]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49315 | -Dear my sister- | 2010 | vndb-v13575 (2001) | ambiguous-name-year | [100: v49315 / held[21]](vndb-kana-bulk-review-20261102-r100.json); [101: 46349 / held[10]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 疑似版本/依赖内容 | vndb:v49478 | Koi ni wa Amae ga Hitsuyou Desu ~Motto Amaeru Dake MiniFanDisc | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [100: v49478 / held[22]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v49491 | Rendezvous | 2024 | vndb-v7056 (2000) | ambiguous-name-year | [100: v49491 / held[23]](vndb-kana-bulk-review-20261102-r100.json); [101: 46495 / held[11]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49494 | Bu Shuangxiu Jiu Qushi | 2022 | nextmoe-21318 (2015) | ambiguous-name-year | [100: v49494 / held[24]](vndb-kana-bulk-review-20261102-r100.json) |
| 疑似版本/依赖内容 | vndb:v49588 | Pray to Snow Append -Shiawase no Jikan- | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [100: v49588 / held[25]](vndb-kana-bulk-review-20261102-r100.json) |
| 名称/年份/身份冲突 | vndb:v49743 | Love is Blind | 2024 | vndb-v44934 (2006) | ambiguous-name-year | [101: 46705 / held[12]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 来源日期冲突 | vndb:v49791 | Apophis no Negai | 2014 | NextMoe: 2010-08-15 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [101: 46750 / held[13]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 来源日期冲突 | vndb:v49828 | 23 Sisters | 2024-02-04 | NextMoe: 2022-11-15 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [101: 46782 / held[14]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49838 | END | 2011 | vndb-v49443 (2003) | ambiguous-name-year | [101: 46790 / held[15]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49896 | Kaerimichi | 2012 | vndb-v32266 (2021) | ambiguous-name-year | [101: 46835 / held[16]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49907 | connect | 2011 | ifdb-t2sezaqjx8j89nnx (2008) | ambiguous-name-year | [101: 46845 / held[17]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49975 | Hydrangea | 2024 | vndb-v43849 (2012) | ambiguous-name-year | [101: 46907 / held[18]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v49979 | Snow Drop | 2014 | vndb-v112 (2000) | ambiguous-name-year | [101: 46911 / held[19]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v50070 | Happy valentines day | 2024 | vndb-v9888 (2012) | ambiguous-name-year | [101: 46986 / held[20]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v50077 | Crossroads | 2023 | ifdb-cmj8xyhj3s20mcva (2015) | ambiguous-name-year | [101: 46989 / held[21]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v50123 | Wuxian zhi Wu | 2024 | vndb-v43862 (2013) | ambiguous-name-year | [101: 47029 / held[22]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v50132 | Inside the Box | 2024 | vndb-v29204 (2006) | ambiguous-name-year | [101: 47038 / held[23]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | vndb:v50267 | Skhovanky | 2024 | ifdb-ljb863xxbw125k2g (1997) | ambiguous-name-year | [101: 47161 / held[24]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:6cpsp17x7j11zh4m | Snowed In | 2021-04-01 01:00:00 | nextmoe-47303 (2024) | name-year-conflict | [101: 6cpsp17x7j11zh4m / held[25]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:quiocupf59o11n8g | Arcadia | 2015-01-01 00:00:00 | vndb-v16979 (2007) | name-year-conflict | [101: quiocupf59o11n8g / held[26]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:nm9ta7ku78hmcp5z | The Snow Queen | 1985-01-01 00:00:00 | mosaic-snow-queen (1986) | name-year-conflict | [101: nm9ta7ku78hmcp5z / held[27]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:oc4jf24yotpal4ve | Schooldays | 2001-01-01 00:00:00 | g033 (2005) | name-year-conflict | [101: oc4jf24yotpal4ve / held[28]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:nue0kr86i5cpkqze | Voices | 2001-01-01 00:00:00 | vndb-v46712 (2023) | name-year-conflict | [101: nue0kr86i5cpkqze / held[29]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:h6gwlggjjyc1e7vl | Jealousy | 2016-12-04 01:00:00 | vndb-v8736 (1995) | name-year-conflict | [101: h6gwlggjjyc1e7vl / held[30]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:t1y822i599h85w3b | Firefly | 2019-01-14 01:00:00 | vndb-v5901 (2010) | name-year-conflict | [101: t1y822i599h85w3b / held[31]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:wk1ews8wko2r9823 | Heaven's Vault | 2019-04-16 01:00:00 | g1408 (2019); supp26-inkle-heavens (2019) | name-year-conflict | [101: wk1ews8wko2r9823 / held[32]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:du51t0qrhjqlnbij | 80 DAYS | 2014-07-31 01:00:00 | g1407 (2014); supp26-inkle (2014) | name-year-conflict | [101: du51t0qrhjqlnbij / held[33]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:w3o4jb8cp5ldd0hm | The Alchemist | 2022-10-01 01:00:00 | vndb-v29693 (2021) | name-year-conflict | [101: w3o4jb8cp5ldd0hm / held[34]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:ech2mmnek9cwc3fd | The Proposal | 2017-11-13 01:00:00 | ifdb-6386r4eg4uptbvao (2005) | name-year-conflict | [101: ech2mmnek9cwc3fd / held[35]](nextmoe-ifdb-bulk-review-20261102-r101.json) |
| 名称/年份/身份冲突 | ifdb:g4mgfnh4pvu3deuc | Humbug | 2003-12-07 01:00:00 | ifdb-z37lzijvuz5gtsu2 (1991) | name-year-conflict | [101: g4mgfnh4pvu3deuc / held[36]](nextmoe-ifdb-bulk-review-20261102-r101.json) |

## 原始证据

- [第100批审计](vndb-kana-bulk-review-20261102-r100.json)
- [第101批审计](nextmoe-ifdb-bulk-review-20261102-r101.json)
- [两批汇总](basic-r100-r101-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
