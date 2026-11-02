# 第118、119批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 118 | 1345 | 483 | 500 | 23 | 338 | 1 |
| 119 | 1463 | 474 | 500 | 44 | 213 | 232 |

## 286条暂存处理

VNDB输入45条、NextMoe输入241条；本轮从旧暂存入选286条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：57,841 → 58,841。

## 新续采位置

- VNDB：`v62260`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVGcwTmpsOQ`
- IFDB：`7627`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共67条原始记录，按来源ID合并为56个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v60981 | PHANTASMAGORIA | 2025 | g1127 (1995) | ambiguous-name-year | [118: v60981 / held[0]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61154 | Headlights | 2025 | ifdb-5x7v9fiblus23eb6 (2022) | ambiguous-name-year | [118: v61154 / held[1]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61188 | Mirrors | 2025 | vndb-v18091 (1990) | ambiguous-name-year | [118: v61188 / held[2]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61265 | The Masterpiece | 2025 | vndb-v30845 (2021) | ambiguous-name-year | [118: v61265 / held[3]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61313 | Wild West | 2022 | vndb-v6052 (2012) | ambiguous-name-year | [118: v61313 / held[4]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61404 | Cutting Edge | 2026 | vndb-v53751 (2024) | ambiguous-name-year | [118: v61404 / held[5]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61484 | last call | 2025 | vndb-v21519 (2017) | ambiguous-name-year | [118: v61484 / held[6]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61493 | A College Education | 2026 | vndb-v5616 (2006) | ambiguous-name-year | [118: v61493 / held[7]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61496 | Delirium | 2025 | vndb-v28248 (2016) | ambiguous-name-year | [118: v61496 / held[8]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61668 | summer story | 2026 | nextmoe-30952 (2021) | ambiguous-name-year | [118: v61668 / held[9]](vndb-kana-bulk-review-20261102-r118.json); [119: 57397 / held[0]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v61807 | Lunatic | 2002 | vndb-v17260 (2014) | ambiguous-name-year | [118: v61807 / held[10]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61848 | Apprentice | 2011 | ifdb-sc9qfq1k945o51ak (1991) | ambiguous-name-year | [118: v61848 / held[11]](vndb-kana-bulk-review-20261102-r118.json); [119: 57554 / held[1]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v61857 | Byoushitsu no Quartet | 2015 | vndb-v44953 (2005) | ambiguous-name-year | [118: v61857 / held[12]](vndb-kana-bulk-review-20261102-r118.json); [119: 57563 / held[2]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v61869 | Natsu Matsuri | 2003 | vndb-v10170 (1999) | ambiguous-name-year | [118: v61869 / held[13]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v61970 | Ruins | 2011 | ifdb-rnsj9vbk0ewwip61 (2001) | ambiguous-name-year | [118: v61970 / held[14]](vndb-kana-bulk-review-20261102-r118.json); [119: 57669 / held[3]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v61987 | Dream Date | 2026 | vndb-v28418 (2020) | ambiguous-name-year | [118: v61987 / held[15]](vndb-kana-bulk-review-20261102-r118.json); [119: 57686 / held[4]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 疑似版本/依赖内容 | vndb:v62070 | Akuma demo Ore to Omae wa! ―Yuujin ga Inma Datta Toki no Dotei Sotsugyo Kaihi Ho― | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [118: v62070 / held[16]](vndb-kana-bulk-review-20261102-r118.json); [119: 57760 / held[5]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 疑似版本/依赖内容 | vndb:v62101 | Buddy Collection Extra -Kochou-sou no Kimyou na Gonin- | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [118: v62101 / held[17]](vndb-kana-bulk-review-20261102-r118.json); [119: 57790 / held[6]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62110 | Utakata | 2019 | vndb-v17841 (2003) | ambiguous-name-year | [118: v62110 / held[18]](vndb-kana-bulk-review-20261102-r118.json); [119: 57799 / held[7]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62145 | The House of Secrets | 2026 | ifdb-0slrzbo45nb1mebi (1985) | ambiguous-name-year | [118: v62145 / held[19]](vndb-kana-bulk-review-20261102-r118.json); [119: 57832 / held[8]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62160 | - la femme - BRUN ~ "Yotsuba" | 2003 | vndb-v62159 (2002) | ambiguous-name-year | [118: v62160 / held[20]](vndb-kana-bulk-review-20261102-r118.json) |
| 名称/年份/身份冲突 | vndb:v62179 | The Garden | 2025 | vndb-v35198 (2022) | ambiguous-name-year | [118: v62179 / held[21]](vndb-kana-bulk-review-20261102-r118.json); [119: 57865 / held[9]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62240 | Manin Densha | 2020 | nextmoe-5061 (2003) | ambiguous-name-year | [118: v62240 / held[22]](vndb-kana-bulk-review-20261102-r118.json); [119: 57922 / held[10]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62319 | Between The Lines | 2026 | vndb-v19561 (2016) | ambiguous-name-year | [119: 57997 / held[11]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62338 | Salvation | 2026 | vndb-v57784 (2025) | ambiguous-name-year | [119: 58015 / held[12]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62344 | Bitter &amp; Sweet | 2026 | vndb-v6234 (2006) | ambiguous-name-year | [119: 58021 / held[13]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62373 | Cvetok | 2026 | ifdb-77rsl9mezn5iogto (1998) | ambiguous-name-year | [119: 58049 / held[14]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62396 | Love Letter | 2024 | nextmoe-1961 (2002) | ambiguous-name-year | [119: 58068 / held[15]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62416 | Karen | 2010 | vndb-v983 (2003) | ambiguous-name-year | [119: 58083 / held[16]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62422 | mirror, mirror | 2021 | ifdb-vke24gmd8usqywu4 (2020) | ambiguous-name-year | [119: 58089 / held[17]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62532 | Danganronpa: Hope Recreation+ | 2025 | vndb-v62531 (2024) | ambiguous-name-year | [119: 58162 / held[18]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62670 | day : dream | 2023 | vndb-v9486 (1986) | ambiguous-name-year | [119: 58287 / held[19]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62681 | INNOCENT | 2023 | vndb-v21810 (1999) | ambiguous-name-year | [119: 58298 / held[20]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62745 | Blind | 2020 | vndb-v12138 (2012) | ambiguous-name-year | [119: 58356 / held[21]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62751 | Scavenger | 2025 | ifdb-ii7j0kliujc4k8wf (2003) | ambiguous-name-year | [119: 58362 / held[22]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62769 | ChangE | 2014 | vndb-v22340 (2017) | ambiguous-name-year | [119: 58379 / held[23]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62801 | Change | 2025 | vndb-v22340 (2017) | ambiguous-name-year | [119: 58409 / held[24]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 疑似版本/依赖内容 | vndb:v62845 | Vampire on Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [119: 58447 / held[25]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | vndb:v62867 | Tower | 2022 | ifdb-8u6m0cofv7m7pn5u (2009) | ambiguous-name-year | [119: 58463 / held[26]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:jtyzvv97m8irt63s | The Alchemist | 2003-01-01 00:00:00 | vndb-v29693 (2021) | name-year-conflict | [119: jtyzvv97m8irt63s / held[27]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:fk8xds3a66pyx208 | Ash | 2016-10-01 01:00:00 | vndb-v8565 (1994) | name-year-conflict | [119: fk8xds3a66pyx208 / held[28]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:68mdw9k76x61fuyb | Take One | 2005-01-01 00:00:00 | vndb-v54989 (2025) | name-year-conflict | [119: 68mdw9k76x61fuyb / held[29]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:d5jcsz4mn1bdqpxr | Alien | 1988-01-01 00:00:00 | ifdb-kp8y1zd5vc284d04 (1984) | name-year-conflict | [119: d5jcsz4mn1bdqpxr / held[30]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:o8iqwwgchaobbuhz | Assault on the Clonemaster | 1980-01-01 00:00:00 | ifdb-d1lmwmvd4qiyb007 (2017) | name-year-conflict | [119: o8iqwwgchaobbuhz / held[31]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:ti3xxdw11e1zlbe6 | Sherwood Forest | 1984-01-01 00:00:00 | ifdb-v9hnvrigiz5r5nxn (1982) | name-year-conflict | [119: ti3xxdw11e1zlbe6 / held[32]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:bnvzf6d0czmbk5ps | Dreamland | 2003-01-01 00:00:00 | nextmoe-37228 (2022) | name-year-conflict | [119: bnvzf6d0czmbk5ps / held[33]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:gaaxee2mvysvsaxd | Excalibur | 1987-01-01 00:00:00 | ifdb-q3isw8j98nnz6gm3 (1990) | name-year-conflict | [119: gaaxee2mvysvsaxd / held[34]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:iq9wxtd9a7vpcy2g | Shipwreck | 1987-01-01 00:00:00 | ifdb-1j9p7lpcoj2sf05i (1986) | name-year-conflict | [119: iq9wxtd9a7vpcy2g / held[35]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:u16mpjnk07d3l8i2 | Tethered | 2018-10-01 01:00:00 | vndb-v31011 (2021) | name-year-conflict | [119: u16mpjnk07d3l8i2 / held[36]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:url6d1j3aj61qmhp | Pirate Island | 1989-01-01 00:00:00 | ifdb-ic3chsxtj3ff2er3 (1985) | name-year-conflict | [119: url6d1j3aj61qmhp / held[37]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:zgauwdi6ie4u4pqc | The House | 2026-04-06 01:00:00 | ifdb-83noiwzup8nsasob (2007) | name-year-conflict | [119: zgauwdi6ie4u4pqc / held[38]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:x7cvej7bm7ixiz0a | Earthquake San Francisco 1906 | 1982-01-01 00:00:00 | ai-earthquake (1981) | name-year-conflict | [119: x7cvej7bm7ixiz0a / held[39]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:2752o3sh6y05ob1p | Journey | 1989-01-01 00:00:00 | ifdb-xehpx39rfnerjy1f (1979) | name-year-conflict | [119: 2752o3sh6y05ob1p / held[40]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:awzxljw8p7cwlkd0 | Diablo! | 1988-01-01 00:00:00 | sierra-on-line-diablo-hellfire (1996) | name-year-conflict | [119: awzxljw8p7cwlkd0 / held[41]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:7mlyo81bc9pk2txv | The Museum | 1989-01-01 00:00:00 | ifdb-sfgaszp8e63v8dtm (2008) | name-year-conflict | [119: 7mlyo81bc9pk2txv / held[42]](nextmoe-ifdb-bulk-review-20261102-r119.json) |
| 名称/年份/身份冲突 | ifdb:9lzmypxgtirgznc7 | &gt;DEVOTION | 2020-07-16 01:00:00 | g1414 (2019); supp26-redcandle-devotion (2019) | name-year-conflict | [119: 9lzmypxgtirgznc7 / held[43]](nextmoe-ifdb-bulk-review-20261102-r119.json) |

## 原始证据

- [第118批审计](vndb-kana-bulk-review-20261102-r118.json)
- [第119批审计](nextmoe-ifdb-bulk-review-20261102-r119.json)
- [两批汇总](basic-r118-r119-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
