# 第104、105批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 104 | 1427 | 522 | 500 | 34 | 306 | 65 |
| 105 | 1553 | 606 | 500 | 36 | 200 | 211 |

## 269条暂存处理

VNDB输入27条、NextMoe输入242条；本轮从旧暂存入选269条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：50,841 → 51,841。

## 新续采位置

- VNDB：`v52640`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZORGsyTnpkOQ`
- IFDB：`6063`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共70条原始记录，按来源ID合并为49个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v51313 | Petrichor | 2024 | nextmoe-1622 (2020) | ambiguous-name-year | [104: v51313 / held[0]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51340 | Aria | 2007 | konami-aria (2003) | ambiguous-name-year | [104: v51340 / held[1]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51408 | Summer With You | 2024 | vndb-v34177 (2022) | ambiguous-name-year | [104: v51408 / held[2]](vndb-kana-bulk-review-20261102-r104.json) |
| 疑似版本/依赖内容 | vndb:v51482 | Veilcrest: Trial of The Arcane | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [104: v51482 / held[3]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51498 | REALITY | 2024 | nextmoe-22327 (2017) | ambiguous-name-year | [104: v51498 / held[4]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51574 | Lost And Found | 2024 | ifdb-ntty23xwy1njd98p (2018) | ambiguous-name-year | [104: v51574 / held[5]](vndb-kana-bulk-review-20261102-r104.json) |
| 疑似版本/依赖内容 | vndb:v51602 | Tsundere na Ane ga Shitsukoku Karandekuru no de Mushi Shiteitara, Ikinari Osowareta Ken ni Tsuite ~Demo, Nande SM Play?~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [104: v51602 / held[6]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51691 | Dead Zone | 2024 | vndb-v4657 (1986) | ambiguous-name-year | [104: v51691 / held[7]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51719 | Sanctuary | 2024 | ifdb-0i9mv4y334ppy25a (1990) | ambiguous-name-year | [104: v51719 / held[8]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51745 | tea party | 2024 | vndb-v14154 (2007) | ambiguous-name-year | [104: v51745 / held[9]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51773 | On Air! | 2018 | vndb-v17706 (1999) | ambiguous-name-year | [104: v51773 / held[10]](vndb-kana-bulk-review-20261102-r104.json); [105: 48477 / held[0]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v51778 | Reflection | 2024 | vndb-v32611 (2021) | ambiguous-name-year | [104: v51778 / held[11]](vndb-kana-bulk-review-20261102-r104.json); [105: 48482 / held[1]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v51799 | VESSELS | 2024 | ifdb-javv3knt46m97dbd (2025) | ambiguous-name-year | [104: v51799 / held[12]](vndb-kana-bulk-review-20261102-r104.json); [105: 48503 / held[2]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v51899 | Teacher's Pet | 2024 | vndb-v33957 (2021) | ambiguous-name-year | [104: v51899 / held[13]](vndb-kana-bulk-review-20261102-r104.json); [105: 48595 / held[3]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v51903 | Nightmare | 1998 | vndb-v7588 (2011) | ambiguous-name-year | [104: v51903 / held[14]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v51956 | Welcome Home | 2020 | vndb-v23823 (2017) | ambiguous-name-year | [104: v51956 / held[15]](vndb-kana-bulk-review-20261102-r104.json); [105: 48640 / held[4]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v51961 | Sleepless | 2024 | vndb-v39465 (2022) | ambiguous-name-year | [104: v51961 / held[16]](vndb-kana-bulk-review-20261102-r104.json); [105: 48645 / held[5]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v51967 | Mirrored | 2024 | ifdb-95gfrnslsr1rou53 (2014); vndb-v42746 (2023) | ambiguous-name-year | [104: v51967 / held[17]](vndb-kana-bulk-review-20261102-r104.json); [105: 48651 / held[6]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52077 | Duplicity | 2024 | vndb-v26926 (2019) | ambiguous-name-year | [104: v52077 / held[18]](vndb-kana-bulk-review-20261102-r104.json); [105: 48754 / held[7]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52126 | Blind Love | 2024 | vndb-v17898 (2015) | ambiguous-name-year | [104: v52126 / held[19]](vndb-kana-bulk-review-20261102-r104.json); [105: 48798 / held[8]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52129 | ROGUE | 2024 | ascii-rogue (1980) | ambiguous-name-year | [104: v52129 / held[20]](vndb-kana-bulk-review-20261102-r104.json); [105: 48801 / held[9]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52153 | Riverside | 2024 | ifdb-m7ppqal8vjkmbfqk (2008) | ambiguous-name-year | [104: v52153 / held[21]](vndb-kana-bulk-review-20261102-r104.json); [105: 48822 / held[10]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 疑似版本/依赖内容 | vndb:v52218 | Magikano Fandisc ~Janken Pon tte Maji Desu ka?~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [104: v52218 / held[22]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v52225 | Journal of a Saint | 2024 | ifdb-cgix4gqeb4fqcbsw (1991) | ambiguous-name-year | [104: v52225 / held[23]](vndb-kana-bulk-review-20261102-r104.json); [105: 48883 / held[11]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52241 | Reunion | 2024 | vndb-v13243 (2013) | ambiguous-name-year | [104: v52241 / held[24]](vndb-kana-bulk-review-20261102-r104.json); [105: 48899 / held[12]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52249 | SMILE | 2024 | vndb-v3288 (2010) | ambiguous-name-year | [104: v52249 / held[25]](vndb-kana-bulk-review-20261102-r104.json); [105: 48907 / held[13]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52304 | Cohabitation | 2024 | vndb-v246 (1997) | ambiguous-name-year | [104: v52304 / held[26]](vndb-kana-bulk-review-20261102-r104.json); [105: 48961 / held[14]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52324 | Injoku no Meikyuu | 2010 | vndb-v49452 (2012) | ambiguous-name-year | [104: v52324 / held[27]](vndb-kana-bulk-review-20261102-r104.json); [105: 48979 / held[15]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52380 | Omoi no Kakera | 2007 | vndb-v40532 (2005) | ambiguous-name-year | [104: v52380 / held[28]](vndb-kana-bulk-review-20261102-r104.json) |
| 名称/年份/身份冲突 | vndb:v52387 | lemonade | 2024 | vndb-v32432 (2021) | ambiguous-name-year | [104: v52387 / held[29]](vndb-kana-bulk-review-20261102-r104.json); [105: 49034 / held[16]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52396 | red eye | 2024 | ifdb-vwq0xmj49cnkye9j (2004) | ambiguous-name-year | [104: v52396 / held[30]](vndb-kana-bulk-review-20261102-r104.json); [105: 49042 / held[17]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52457 | PETRICHOR | 2024 | nextmoe-1622 (2020) | ambiguous-name-year | [104: v52457 / held[31]](vndb-kana-bulk-review-20261102-r104.json); [105: 49093 / held[18]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52566 | Michi Annai | 2023 | vndb-v52565 (2022) | ambiguous-name-year | [104: v52566 / held[32]](vndb-kana-bulk-review-20261102-r104.json); [105: 49194 / held[19]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52569 | Hen'ai | 2024 | vndb-v10132 (2000) | ambiguous-name-year | [104: v52569 / held[33]](vndb-kana-bulk-review-20261102-r104.json); [105: 49197 / held[20]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52696 | Eydolon | 2024 | vndb-v1488 (2007) | ambiguous-name-year | [105: 49319 / held[21]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52809 | Obsession | 2024 | vndb-v40659 (2006) | ambiguous-name-year | [105: 49409 / held[22]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52887 | Genesis | 2024 | ifdb-o7nq769ihazfchxu (2012) | ambiguous-name-year | [105: 49477 / held[23]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52935 | All Hallow's Eve | 2024 | ifdb-xtpiuzfe41bm598k (2010) | ambiguous-name-year | [105: 49524 / held[24]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v52939 | As Dusk Falls | 2024 | g964 (2022) | ambiguous-name-year | [105: 49528 / held[25]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v53004 | Undercover | 2025 | ifdb-3l7sdvp1cdycfal2 (1992) | ambiguous-name-year | [105: 49590 / held[26]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v53072 | IRIS | 2024 | nextmoe-465 (2018) | ambiguous-name-year | [105: 49653 / held[27]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | vndb:v53094 | Natsu Sora Shoujo | 2012 | vndb-v4319 (2005) | ambiguous-name-year | [105: 49672 / held[28]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:pgz2dbaixrrv01g0 | Dragon Quest | 1987-01-01 00:00:00 | enix-dq1 (1986) | name-year-conflict | [105: pgz2dbaixrrv01g0 / held[29]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:e7euznoq2gk45xzc | The Hollow | 1985-01-01 00:00:00 | vndb-v38992 (2022) | name-year-conflict | [105: e7euznoq2gk45xzc / held[30]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:h6yj013xuhioseik | Ghost Town | 2009-04-22 00:00:00 | ai-ghost-town (1980); microcabin-ghost (1984) | name-year-conflict | [105: h6yj013xuhioseik / held[31]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:1mn18bh1s38tw9bp | Jack | 2013-11-30 01:00:00 | g1278 (1988) | name-year-conflict | [105: 1mn18bh1s38tw9bp / held[32]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:honstaavp2mczam2 | Blink | 2004-01-01 00:00:00 | ifdb-mbsoddwcsu9fgksf (2023) | name-year-conflict | [105: honstaavp2mczam2 / held[33]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:qu3fiu2kaa5x12y6 | Dead End | 1990-01-01 00:00:00 | vndb-v16587 (2014) | name-year-conflict | [105: qu3fiu2kaa5x12y6 / held[34]](nextmoe-ifdb-bulk-review-20261102-r105.json) |
| 名称/年份/身份冲突 | ifdb:d7zemrqxdrdo6lhl | Tic-Tac-Toe | 2014-01-05 01:00:00 | vndb-v13983 (2011) | name-year-conflict | [105: d7zemrqxdrdo6lhl / held[35]](nextmoe-ifdb-bulk-review-20261102-r105.json) |

## 原始证据

- [第104批审计](vndb-kana-bulk-review-20261102-r104.json)
- [第105批审计](nextmoe-ifdb-bulk-review-20261102-r105.json)
- [两批汇总](basic-r104-r105-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
