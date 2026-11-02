# 第126、127批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 126 | 949 | 152 | 500 | 24 | 267 | 6 |
| 127 | 3046 | 154 | 500 | 37 | 2355 | 0 |

## 49条暂存处理

VNDB输入49条、NextMoe输入0条；本轮从旧暂存入选49条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：61,896 → 62,896。

## 新续采位置

- VNDB：`v68238`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNakl3TURZM2ZR`
- IFDB：`8871`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共61条原始记录，按来源ID合并为61个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v67411 | Schwarzwald | 2026 | vndb-v13272 (2010) | ambiguous-name-year | [126: v67411 / held[0]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67460 | Stay With Me | 2026 | vndb-v56979 (2025) | ambiguous-name-year | [126: v67460 / held[1]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67473 | NoAH | 2026 | ifdb-ml4pe41qrai83teh (1984) | ambiguous-name-year | [126: v67473 / held[2]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67508 | Invisible | 2009 | g849 (2020) | ambiguous-name-year | [126: v67508 / held[3]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67566 | Twilight | 2009 | vndb-v8657 (1994) | ambiguous-name-year | [126: v67566 / held[4]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67573 | The Vault | 2018 | ifdb-9bo8243zp18pwzs8 (2010) | ambiguous-name-year | [126: v67573 / held[5]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67635 | Moshi, Moshi...... | 2008 | vndb-v27316 (2007) | ambiguous-name-year | [126: v67635 / held[6]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67733 | Alien | 2022 | ifdb-d5jcsz4mn1bdqpxr (1988); ifdb-kp8y1zd5vc284d04 (1984) | ambiguous-name-year | [126: v67733 / held[7]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67754 | pray | 2005 | vndb-v16980 (2013) | ambiguous-name-year | [126: v67754 / held[8]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67815 | Odna Seksualnaya Istoriya | 2019 | vndb-v13293 (2012) | ambiguous-name-year | [126: v67815 / held[9]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67836 | &lt;Ghost&gt; Town | 2023 | ai-ghost-town (1980); microcabin-ghost (1984) | ambiguous-name-year | [126: v67836 / held[10]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67862 | Re・Birth | 1986 | nextmoe-26475 (2020); vndb-v9057 (1995) | ambiguous-name-year | [126: v67862 / held[11]](vndb-kana-bulk-review-20261102-r126.json) |
| 疑似版本/依赖内容 | vndb:v67938 | Gag Patch Works | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [126: v67938 / held[12]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v67986 | Arcadia | 2023 | vndb-v16979 (2007) | ambiguous-name-year | [126: v67986 / held[13]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68021 | Adrift | 2026 | nextmoe-14737 (2011) | ambiguous-name-year | [126: v68021 / held[14]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68107 | Enigma | 2014 | nextmoe-21146 (2015) | ambiguous-name-year | [126: v68107 / held[15]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68135 | Prototype | 2026 | vndb-v41417 (2022) | ambiguous-name-year | [126: v68135 / held[16]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68136 | Otome | 2024 | vndb-v6775 (2006) | ambiguous-name-year | [126: v68136 / held[17]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68187 | Toriko | 2011 | vndb-v14583 (1996) | ambiguous-name-year | [126: v68187 / held[18]](vndb-kana-bulk-review-20261102-r126.json) |
| 疑似版本/依赖内容 | vndb:v68200 | Triple Pairing - MiniFandisc | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [126: v68200 / held[19]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68218 | Eat the Rich | 2026 | ifdb-n7ef5o66fnhwed6d (2024) | ambiguous-name-year | [126: v68218 / held[20]](vndb-kana-bulk-review-20261102-r126.json) |
| 疑似版本/依赖内容 | vndb:v68223 | EVA-teki Kanmusu Collection Souryuu Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [126: v68223 / held[21]](vndb-kana-bulk-review-20261102-r126.json) |
| 疑似版本/依赖内容 | vndb:v68224 | EVA-teki Kanmusu Collection Ayanami Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [126: v68224 / held[22]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v68225 | Yakata | 2014 | vndb-v14513 (1996) | ambiguous-name-year | [126: v68225 / held[23]](vndb-kana-bulk-review-20261102-r126.json) |
| 名称/年份/身份冲突 | vndb:v66891 | Sosei Kyouka-shiki Yuuki Seimei-tai: Torasutoman | 2026 | vndb-v35217 (2020) | ambiguous-name-year | [127: 215000 / held[0]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | vndb:v66898 | Fear Of Gods | 2022 | vndb-v32092 (2020) | ambiguous-name-year | [127: 215005 / held[1]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | vndb:v66940 | Honey. | 2026 | vndb-v44862 (2004) | ambiguous-name-year | [127: 215047 / held[2]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | vndb:v66951 | Bloodlines | 2026 | vndb-v49392 (2024) | ambiguous-name-year | [127: 215058 / held[3]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:nzutxgb0ocaxgrmz | Jabberwocky | 2023-01-01 00:00:00 | vndb-v13382 (2013) | name-year-conflict | [127: nzutxgb0ocaxgrmz / held[4]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:zk9zssjb5avexx9b | Flight of the Hummingbird | 2010-10-01 01:00:00 | vndb-v20332 (2015) | name-year-conflict | [127: zk9zssjb5avexx9b / held[5]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:hqkh68uq8xagx9n2 | Outline | 2005-01-01 00:00:00 | vndb-v21886 (1999) | name-year-conflict | [127: hqkh68uq8xagx9n2 / held[6]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:kqedeubj4ds7mmel | Minami Aoyama Adventure | 1982-01-01 00:00:00 | ifdb-ym7qvs8lbz975a9a (1983) | name-year-conflict | [127: kqedeubj4ds7mmel / held[7]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:ipd8cfcf7rgalzyq | Jack and the Beanstalk | 1988-01-01 00:00:00 | ifdb-jw6dmehgxmwusaeg (1984) | name-year-conflict | [127: ipd8cfcf7rgalzyq / held[8]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:47hsesg104e99gsi | Late to the Party | 2020-03-11 01:00:00 | vndb-v34231 (2022) | name-year-conflict | [127: 47hsesg104e99gsi / held[9]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:ullj64v8s5jlz48k | ADVENT | 2003-01-01 00:00:00 | vndb-v27604 (1996) | name-year-conflict | [127: ullj64v8s5jlz48k / held[10]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:9zyce6chm1uivw72 | Dilemma | 2012-01-01 00:00:00 | ifdb-milfkwhkljor5f29 (2018) | name-year-conflict | [127: 9zyce6chm1uivw72 / held[11]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:5ckhn542u3cr9pc6 | Treasure Island | 1983-01-01 00:00:00 | g1603 (1985) | name-year-conflict | [127: 5ckhn542u3cr9pc6 / held[12]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:wrlm64ui061b4sh4 | The Ritual | 2017-11-13 01:00:00 | ifdb-hsm6bvrl7wmtuczg (2015) | name-year-conflict | [127: wrlm64ui061b4sh4 / held[13]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:7n9huoky8k2gfwzo | The Tower | 1983-01-01 00:00:00 | ifdb-nwuj3s93o2p9fxw1 (2018) | name-year-conflict | [127: 7n9huoky8k2gfwzo / held[14]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:39t7d9fgq45m10l2 | Phantom | 2020-10-01 01:00:00 | g597 (2000) | name-year-conflict | [127: 39t7d9fgq45m10l2 / held[15]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:arwicdlwnwgtumzx | Salvage | 1983-01-01 00:00:00 | ifdb-v87g98ga9jj1snow (1985) | name-year-conflict | [127: arwicdlwnwgtumzx / held[16]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:13saf297yzgx9byz | Spring Cleaning | 2008-04-06 00:00:00 | vndb-v43658 (2023) | name-year-conflict | [127: 13saf297yzgx9byz / held[17]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:b8y15ull1q1hdcme | Floyd | 2001-01-01 00:00:00 | vndb-v35510 (2015) | name-year-conflict | [127: b8y15ull1q1hdcme / held[18]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:76ecmby2q849qlsl | A D R I F T | 2022-04-05 01:00:00 | nextmoe-14737 (2011) | name-year-conflict | [127: 76ecmby2q849qlsl / held[19]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:riv2ic6fioxsgw6w | PURE | 2025-09-01 01:00:00 | vndb-v8818 (1989) | name-year-conflict | [127: riv2ic6fioxsgw6w / held[20]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:yfmkeczfi5pn7pl7 | Haunted House | 1985-01-01 00:00:00 | ifdb-l83fkolmk4rrv1gz (1979) | name-year-conflict | [127: yfmkeczfi5pn7pl7 / held[21]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:qmevmwvr6ms0nj2n | College Craze | 2021-01-01 00:00:00 | nextmoe-30130 (2024) | name-year-conflict | [127: qmevmwvr6ms0nj2n / held[22]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:krxmgkrxcys0egn9 | Mysterious Island | 1983-01-01 00:00:00 | ifdb-pj6eqjll6u05bxzu (1999) | name-year-conflict | [127: krxmgkrxcys0egn9 / held[23]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:9qn2v3wws45qpzth | The Mouse | 2016-10-01 01:00:00 | ifdb-eolt81egigwl3dlv (1985) | name-year-conflict | [127: 9qn2v3wws45qpzth / held[24]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:bb3he06qx7j7x5ut | Sleepless | 2015-09-01 01:00:00 | vndb-v39465 (2022) | name-year-conflict | [127: bb3he06qx7j7x5ut / held[25]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:gmyqxwmgd4g2xfqi | Home | 2011-02-05 01:00:00 | vndb-v15962 (2014) | name-year-conflict | [127: gmyqxwmgd4g2xfqi / held[26]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:53ehc5vjhquy7ffg | one last time. | 2023-08-19 01:00:00 | vndb-v23782 (2018) | name-year-conflict | [127: 53ehc5vjhquy7ffg / held[27]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:j50n8ozuo1y34pl6 | The Whisperer in Darkness | 2014-05-23 01:00:00 | vndb-v20151 (2016) | name-year-conflict | [127: j50n8ozuo1y34pl6 / held[28]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:s6dk8qsc86jz2a0h | The Curse | 1983-01-01 00:00:00 | vndb-v61306 (2022) | name-year-conflict | [127: s6dk8qsc86jz2a0h / held[29]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:s90c9jdlext55ujp | Encounter | 1983-01-01 00:00:00 | vndb-v25598 (2019) | name-year-conflict | [127: s90c9jdlext55ujp / held[30]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:1qie1vk17usv2rkr | Fade to Black | 2004-02-28 01:00:00 | vndb-v20174 (2015) | name-year-conflict | [127: 1qie1vk17usv2rkr / held[31]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:2z9tyydlvi52vkg3 | Resonance | 2012-07-17 01:00:00 | ifdb-bpwvrsiv73brmexc (2009) | name-year-conflict | [127: 2z9tyydlvi52vkg3 / held[32]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:xv6o2yfg68f5c3si | Cry Wolf! | 1983-01-01 00:00:00 | ifdb-wtiyhpysbkp7ajg5 (2008) | name-year-conflict | [127: xv6o2yfg68f5c3si / held[33]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:yjg75j71bmw3fhfx | Castle of Doom | 1983-01-01 00:00:00 | ifdb-cpo9f66vvnb4hgsx (2015) | name-year-conflict | [127: yjg75j71bmw3fhfx / held[34]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:l49bnyq7ccb4y65l | The Mansion | 2019-06-14 01:00:00 | ifdb-cgix4gqeb4fqcbsw (1991) | name-year-conflict | [127: l49bnyq7ccb4y65l / held[35]](nextmoe-ifdb-bulk-review-20261102-r127.json) |
| 名称/年份/身份冲突 | ifdb:e26uvb9x1f152rv6 | The Beach | 2004-01-01 00:00:00 | vndb-v8432 (2011) | name-year-conflict | [127: e26uvb9x1f152rv6 / held[36]](nextmoe-ifdb-bulk-review-20261102-r127.json) |

## 原始证据

- [第126批审计](vndb-kana-bulk-review-20261102-r126.json)
- [第127批审计](nextmoe-ifdb-bulk-review-20261102-r127.json)
- [两批汇总](basic-r126-r127-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
