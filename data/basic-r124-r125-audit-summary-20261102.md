# 第124、125批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 124 | 1445 | 458 | 500 | 28 | 410 | 49 |
| 125 | 3010 | 203 | 500 | 24 | 2283 | 0 |

## 309条暂存处理

VNDB输入45条、NextMoe输入264条；本轮从旧暂存入选309条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：60,896 → 61,896。

## 新续采位置

- VNDB：`v67308`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNakV3TXpBeWZR`
- IFDB：`8325`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共52条原始记录，按来源ID合并为47个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v65780 | My Valentine | 2022 | vndb-v55739 (2025) | ambiguous-name-year | [124: v65780 / held[0]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v65787 | Journey | 2024 | ifdb-2752o3sh6y05ob1p (1989); ifdb-xehpx39rfnerjy1f (1979) | ambiguous-name-year | [124: v65787 / held[1]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66200 | Obezglavlennaja | 2026 | vndb-v28753 (2020) | ambiguous-name-year | [124: v66200 / held[2]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66242 | Kakuriyo | 2023 | vndb-v11702 (2001) | ambiguous-name-year | [124: v66242 / held[3]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66307 | Inferno | 2022 | vndb-v50065 (2011) | ambiguous-name-year | [124: v66307 / held[4]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66309 | Insomnia | 2023 | ifdb-oy6ld63a47b9vn1x (1998) | ambiguous-name-year | [124: v66309 / held[5]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66462 | Sverkhnovaya! | 2021 | ifdb-4kzpaculjx4r2fxf (1987) | ambiguous-name-year | [124: v66462 / held[6]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66487 | Proshchalnoye pismo | 2023 | vndb-v58662 (2022) | ambiguous-name-year | [124: v66487 / held[7]](vndb-kana-bulk-review-20261102-r124.json); [125: 61896 / held[0]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | vndb:v66615 | Kalanchoe | 2021 | vndb-v3685 (2005) | ambiguous-name-year | [124: v66615 / held[8]](vndb-kana-bulk-review-20261102-r124.json); [125: 62022 / held[1]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | vndb:v66629 | Unfinished | 2026 | vndb-v54665 (2025) | ambiguous-name-year | [124: v66629 / held[9]](vndb-kana-bulk-review-20261102-r124.json); [125: 62036 / held[2]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | vndb:v66660 | LAVENDER | 2024 | vndb-v5769 (2000) | ambiguous-name-year | [124: v66660 / held[10]](vndb-kana-bulk-review-20261102-r124.json); [125: 62067 / held[3]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | vndb:v66686 | Dear ______; | 2026 | vndb-v49804 (1999) | ambiguous-name-year | [124: v66686 / held[11]](vndb-kana-bulk-review-20261102-r124.json); [125: 62093 / held[4]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | vndb:v66727 | Nagareochiru Shirabe ni Nosete | 2002 | nextmoe-8890 (2009) | ambiguous-name-year | [124: v66727 / held[12]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66759 | Suisougakubu Monogatari ~7-kakan~ | 2004 | nextmoe-30278 (2018) | ambiguous-name-year | [124: v66759 / held[13]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66891 | Sosei Kyouka-shiki Yuuki Seimei-tai: Torasutoman | 2026 | vndb-v35217 (2020) | ambiguous-name-year | [124: v66891 / held[14]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66898 | Fear Of Gods | 2022 | vndb-v32092 (2020) | ambiguous-name-year | [124: v66898 / held[15]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66940 | Honey. | 2026 | vndb-v44862 (2004) | ambiguous-name-year | [124: v66940 / held[16]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v66951 | Bloodlines | 2026 | vndb-v49392 (2024) | ambiguous-name-year | [124: v66951 / held[17]](vndb-kana-bulk-review-20261102-r124.json) |
| 疑似版本/依赖内容 | vndb:v66987 | Caste Joui no Mesu-tachi ga Iribitaru Ore no Yaribeya Harem ~Biju ga Tsuyoi Mesu de Haramase Onaho Collection o Tsukuru!~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [124: v66987 / held[18]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67026 | Porcelain Hearts | 2026 | vndb-v29753 (2017) | ambiguous-name-year | [124: v67026 / held[19]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67053 | Remember Me | 2026 | vndb-v54496 (2022) | ambiguous-name-year | [124: v67053 / held[20]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67128 | My Guardian Angel | 2026 | vndb-v31197 (2016) | ambiguous-name-year | [124: v67128 / held[21]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67237 | In Your Shadow | 2026 | vndb-v24799 (2018) | ambiguous-name-year | [124: v67237 / held[22]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67272 | AprilFool | 2012 | vndb-v15623 (2007) | ambiguous-name-year | [124: v67272 / held[23]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67279 | Over the Edge | 2026 | ifdb-jr8abn3p5x11lfa8 (2006) | ambiguous-name-year | [124: v67279 / held[24]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67281 | Asterius | 2026 | vndb-v44519 (2023) | ambiguous-name-year | [124: v67281 / held[25]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67286 | Leap of Faith | 2026 | nextmoe-27964 (2020) | ambiguous-name-year | [124: v67286 / held[26]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67302 | As You Wish | 2026 | vndb-v44112 (2023) | ambiguous-name-year | [124: v67302 / held[27]](vndb-kana-bulk-review-20261102-r124.json) |
| 名称/年份/身份冲突 | vndb:v67986 | Arcadia | 2023 | vndb-v16979 (2007) | ambiguous-name-year | [125: 207054 / held[5]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:1mspez4pljruogux | The Lighthouse | 2009-10-31 01:00:00 | ifdb-8pb1srlj0lvmkh7x (2008) | name-year-conflict | [125: 1mspez4pljruogux / held[6]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:dqjcri225a8lmu0k | Campfire Tales | 2018-10-01 01:00:00 | vndb-v32553 (2021) | name-year-conflict | [125: dqjcri225a8lmu0k / held[7]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:gdsdsced60ci885x | Sweet Dreams | 2003-01-01 00:00:00 | vndb-v24171 (2017); vndb-v44053 (2023) | name-year-conflict | [125: gdsdsced60ci885x / held[8]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:ysqz6re7lajdrtx2 | Castle of Doom | 1980-01-01 00:00:00 | ifdb-cpo9f66vvnb4hgsx (2015) | name-year-conflict | [125: ysqz6re7lajdrtx2 / held[9]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:uzrm00a80dt44cos | Who Are You Talking To? | 2013-08-09 01:00:00 | ifdb-1iw45paorns1c2s4 (2024) | name-year-conflict | [125: uzrm00a80dt44cos / held[10]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:2c3o8t8l14lzm7ry | Inevitable | 2017-10-01 01:00:00 | ifdb-cefpt9ubleq41v3w (2003) | name-year-conflict | [125: 2c3o8t8l14lzm7ry / held[11]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:4d1ib5uxdcmqizwf | Camelot | 2012-05-18 01:00:00 | ifdb-aheqquf0ok54dmb9 (1983) | name-year-conflict | [125: 4d1ib5uxdcmqizwf / held[12]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:z13dwhtjlrds8s5g | The Awakening | 2023-09-20 01:00:00 | nextmoe-28626 (2025) | name-year-conflict | [125: z13dwhtjlrds8s5g / held[13]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:8hxsy83yidlut9d4 | Blink | 2013-04-06 01:00:00 | ifdb-mbsoddwcsu9fgksf (2023) | name-year-conflict | [125: 8hxsy83yidlut9d4 / held[14]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:qnnbwnkml44qcipg | SOL | 2023-06-05 01:00:00 | vndb-v36196 (2024) | name-year-conflict | [125: qnnbwnkml44qcipg / held[15]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:wllglykysojzs283 | Through Time | 2014-04-10 01:00:00 | ifdb-f3k74ovanhhjs3j6 (2009) | name-year-conflict | [125: wllglykysojzs283 / held[16]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:57mesg9zu26i1722 | Bronx | 1988-01-01 00:00:00 | vndb-v48373 (2016) | name-year-conflict | [125: 57mesg9zu26i1722 / held[17]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:stbl8r123hu93y8h | Black Mountain | 1982-01-01 00:00:00 | vndb-v42436 (2023) | name-year-conflict | [125: stbl8r123hu93y8h / held[18]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:si9x0ucuxx9jtlxh | The Lake | 1988-09-01 00:00:00 | ifdb-bs0dmmo9585615vt (1999) | name-year-conflict | [125: si9x0ucuxx9jtlxh / held[19]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:k3hdjj6vo9y17ytf | Nine Lives | 2015-10-31 01:00:00 | vndb-v27872 (2018) | name-year-conflict | [125: k3hdjj6vo9y17ytf / held[20]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:eefftfc19x4wv3tp | Witch Hunt | 1987-01-01 00:00:00 | vndb-v62993 (2009) | name-year-conflict | [125: eefftfc19x4wv3tp / held[21]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:zw2zis2i7u996z6w | Our Personal Space | 2014-02-14 01:00:00 | nextmoe-20503 (2015) | name-year-conflict | [125: zw2zis2i7u996z6w / held[22]](nextmoe-ifdb-bulk-review-20261102-r125.json) |
| 名称/年份/身份冲突 | ifdb:o0dljdnk18c1ovqk | Time Traveler | 1989-01-01 00:00:00 | vndb-v29400 (2015) | name-year-conflict | [125: o0dljdnk18c1ovqk / held[23]](nextmoe-ifdb-bulk-review-20261102-r125.json) |

## 原始证据

- [第124批审计](vndb-kana-bulk-review-20261102-r124.json)
- [第125批审计](nextmoe-ifdb-bulk-review-20261102-r125.json)
- [两批汇总](basic-r124-r125-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
