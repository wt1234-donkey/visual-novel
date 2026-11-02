# 第128、129批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 128 | 1006 | 132 | 500 | 20 | 298 | 56 |
| 129 | 3044 | 44 | 500 | 35 | 2465 | 0 |

## 6条暂存处理

VNDB输入6条、NextMoe输入0条；本轮从旧暂存入选6条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：62,896 → 63,896。

## 新续采位置

- VNDB：`v69273`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNakkxT0RnemZR`
- IFDB：`9415`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共55条原始记录，按来源ID合并为55个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v68245 | Ori | 2007 | vndb-v7973 (1998) | ambiguous-name-year | [128: v68245 / held[0]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68246 | Wana | 2008 | vndb-v14312 (2013) | ambiguous-name-year | [128: v68246 / held[1]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68360 | Smile | 2026 | vndb-v3288 (2010) | ambiguous-name-year | [128: v68360 / held[2]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68463 | Scramble Heart | 2001 | vndb-v486 (2007) | ambiguous-name-year | [128: v68463 / held[3]](vndb-kana-bulk-review-20261102-r128.json) |
| 疑似版本/依赖内容 | vndb:v68516 | Hitomishiri Demo Yaru Toki wa Ru! | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [128: v68516 / held[4]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68551 | RED | 2014 | nextmoe-14623 (1992) | ambiguous-name-year | [128: v68551 / held[5]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68609 | Utsusemi | 2010 | vndb-v7455 (1999) | ambiguous-name-year | [128: v68609 / held[6]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68631 | angel lover | 2026 | vndb-v40132 (2021) | ambiguous-name-year | [128: v68631 / held[7]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68655 | Limit | 2009 | vndb-v15501 (2014) | ambiguous-name-year | [128: v68655 / held[8]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68739 | Welcome Home | 2026 | vndb-v23823 (2017) | ambiguous-name-year | [128: v68739 / held[9]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68801 | FANTASIA | 2007 | vndb-v8211 (2005) | ambiguous-name-year | [128: v68801 / held[10]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68872 | Hakoniwa | 2026 | nextmoe-3859 (2025) | ambiguous-name-year | [128: v68872 / held[11]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68904 | Cosmo's | 2026 | vndb-v17320 (2013) | ambiguous-name-year | [128: v68904 / held[12]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v68985 | Kimi ga Suki | 2025 | vndb-v38583 (2007) | ambiguous-name-year | [128: v68985 / held[13]](vndb-kana-bulk-review-20261102-r128.json) |
| 疑似版本/依赖内容 | vndb:v68988 | My Collection Another Story 1 Ayano &amp; Maki Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [128: v68988 / held[14]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v69015 | Half Blood | 2025 | vndb-v5774 (2003) | ambiguous-name-year | [128: v69015 / held[15]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v69060 | Katei Kyoushi | 1994 | vndb-v14512 (1996) | ambiguous-name-year | [128: v69060 / held[16]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v69082 | Soul Date | 2026 | vndb-v42976 (2023) | ambiguous-name-year | [128: v69082 / held[17]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v69209 | Dead Reckoning | 2026 | ifdb-62nzfrvab3j6csaf (2003) | ambiguous-name-year | [128: v69209 / held[18]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v69239 | DESIRE | 2026 | vndb-v65431 (2013) | ambiguous-name-year | [128: v69239 / held[19]](vndb-kana-bulk-review-20261102-r128.json) |
| 名称/年份/身份冲突 | vndb:v69362 | will | 2023 | vndb-v10710 (2007) | ambiguous-name-year | [129: 221135 / held[0]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:jb091lzkdkb44n22 | Cursed | 2011-10-01 01:00:00 | vndb-v33412 (2021) | name-year-conflict | [129: jb091lzkdkb44n22 / held[1]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:grwhiavt083z18ii | One last chance | 2026-06-22 01:00:00 | vndb-v19111 (2016) | name-year-conflict | [129: grwhiavt083z18ii / held[2]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:bslf6tlzqeatqvln | Dungeon | 1984-01-01 00:00:00 | ifdb-q84zlpfr3x855ukd (2006) | name-year-conflict | [129: bslf6tlzqeatqvln / held[3]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:dcyjfx8eizyi6m3g | Funhouse | 1984-01-01 00:00:00 | ifdb-ngqbbtnybfqaxnqb (2003) | name-year-conflict | [129: dcyjfx8eizyi6m3g / held[4]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:qajj0sped9ld538v | Dark Forest | 2003-01-01 00:00:00 | ifdb-q9gxlx9qfe0qx1ig (1984) | name-year-conflict | [129: qajj0sped9ld538v / held[5]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:kqbv8d633eg28nnf | In the end | 2024-03-29 01:00:00 | ifdb-gjfpoi9klpbrfyoa (1996) | name-year-conflict | [129: kqbv8d633eg28nnf / held[6]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:qm51kq57gyh33udv | Paradox | 2013-09-28 01:00:00 | ifdb-7hxws2l0r8q7v146 (1984) | name-year-conflict | [129: qm51kq57gyh33udv / held[7]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:479t3ui7ps8ghqsy | Radicofani | 2020-10-01 01:00:00 | ifdb-kos6pjrwndtk3tba (2005) | name-year-conflict | [129: 479t3ui7ps8ghqsy / held[8]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:73k5n9bwpqqysk4x | The Gift of the Magi | 2014-10-31 01:00:00 | vndb-v7756 (2011) | name-year-conflict | [129: 73k5n9bwpqqysk4x / held[9]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:mnb6krd8belfkwsv | Merlin's Quest | 1984-01-01 00:00:00 | ifdb-z70s199zg72pknr8 (2002) | name-year-conflict | [129: mnb6krd8belfkwsv / held[10]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:72ji5re6yjln6iyd | The Train | 2018-05-30 01:00:00 | ifdb-2shn3wfk4nfv7ohr (2017) | name-year-conflict | [129: 72ji5re6yjln6iyd / held[11]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:se79a0b8rpkj8qz3 | Survivor | 1984-01-01 00:00:00 | ifdb-niem9jka6vfzsr39 (1989) | name-year-conflict | [129: se79a0b8rpkj8qz3 / held[12]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:29l04xfgii5roq63 | Glass | 2006-01-01 00:00:00 | nextmoe-19776 (2014) | name-year-conflict | [129: 29l04xfgii5roq63 / held[13]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:o5ytl292ya4r1q4n | Scars | 2016-10-31 01:00:00 | vndb-v48609 (2023) | name-year-conflict | [129: o5ytl292ya4r1q4n / held[14]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:6te7v3u4tzzla4ns | Snow Joke | 1985-01-01 00:00:00 | ifdb-lyvgtml4yrzaxtbk (1991) | name-year-conflict | [129: 6te7v3u4tzzla4ns / held[15]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:7b5bwgpdgp20kkch | Contract | 1985-01-01 00:00:00 | ifdb-redw94qtdt1x1s6z (2025) | name-year-conflict | [129: 7b5bwgpdgp20kkch / held[16]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:jsda7qkiaxrkvu5c | Time Zone | 1985-01-01 00:00:00 | g059 (1982) | name-year-conflict | [129: jsda7qkiaxrkvu5c / held[17]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:nmgpefi2cazumr0h | Malice in Blunderland | 1985-01-01 00:00:00 | ifdb-mbf742ftjf06hagh (1986) | name-year-conflict | [129: nmgpefi2cazumr0h / held[18]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:fbzswfyjsnrkxuci | goodnight | 2023-07-01 01:00:00 | vndb-v33808 (2021) | name-year-conflict | [129: fbzswfyjsnrkxuci / held[19]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:1n1gkh84dv7bkigf | Treasure Hunt | 1986-01-01 00:00:00 | ifdb-pxpqnb4pb5rfn98k (2016) | name-year-conflict | [129: 1n1gkh84dv7bkigf / held[20]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:aceemlstv4qlb786 | Aftermath | 2016-11-16 01:00:00 | ifdb-coehmf85g72ttpnf (2000) | name-year-conflict | [129: aceemlstv4qlb786 / held[21]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:8b72k3s64zekst4m | Alice | 2023-01-31 01:00:00 | psk-alice (1984); vndb-v43194 (2023) | name-year-conflict | [129: 8b72k3s64zekst4m / held[22]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:79sxv4tgvgf5jfmm | Murder | 1986-01-01 00:00:00 | ifdb-fl2qc14akizazsge (2012) | name-year-conflict | [129: 79sxv4tgvgf5jfmm / held[23]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:dhzcnc8n13fybm3k | Murder Hunt | 1986-01-01 00:00:00 | ifdb-hy494hhy2ekcr09p (1985) | name-year-conflict | [129: dhzcnc8n13fybm3k / held[24]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:6g18wb4yvzj7397z | Cradle | 2012-11-28 01:00:00 | vndb-v34347 (2021) | name-year-conflict | [129: 6g18wb4yvzj7397z / held[25]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:dehj6pktd40b2ovm | Castle Dracula | 1987-01-01 00:00:00 | ifdb-3t0o0qpypl96qatg (1985) | name-year-conflict | [129: dehj6pktd40b2ovm / held[26]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:6lssl0ewk4yz5g28 | Second Chance | 2005-01-01 00:00:00 | nextmoe-30337 (2017) | name-year-conflict | [129: 6lssl0ewk4yz5g28 / held[27]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:lis59ao3xfqnhnon | Closure | 2021-10-01 01:00:00 | vndb-v14355 (2013) | name-year-conflict | [129: lis59ao3xfqnhnon / held[28]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:3pwabplqhed7676n | Requiem | 2006-01-01 00:00:00 | vndb-v3804 (2004) | name-year-conflict | [129: 3pwabplqhed7676n / held[29]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:vjqqjqdstxpp3ncj | Romeo and Juliet | 1988-01-01 00:00:00 | vndb-v31969 (2021) | name-year-conflict | [129: vjqqjqdstxpp3ncj / held[30]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:pps1ho75c2rannke | Haunted House | 2011-01-01 00:00:00 | ifdb-l83fkolmk4rrv1gz (1979) | name-year-conflict | [129: pps1ho75c2rannke / held[31]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:ry4zkpmrc7ls5yu8 | Freedom | 2008-10-01 00:00:00 | ifdb-f9sydfatib2kady1 (2000) | name-year-conflict | [129: ry4zkpmrc7ls5yu8 / held[32]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:fru4niwvvzargtp5 | Nightmare | 1989-01-01 00:00:00 | vndb-v7588 (2011) | name-year-conflict | [129: fru4niwvvzargtp5 / held[33]](nextmoe-ifdb-bulk-review-20261102-r129.json) |
| 名称/年份/身份冲突 | ifdb:murbm2qlcoykooua | Forgotten Island | 1989-01-01 00:00:00 | ifdb-tv73msg2a4zr4csu (2022) | name-year-conflict | [129: murbm2qlcoykooua / held[34]](nextmoe-ifdb-bulk-review-20261102-r129.json) |

## 原始证据

- [第128批审计](vndb-kana-bulk-review-20261102-r128.json)
- [第129批审计](nextmoe-ifdb-bulk-review-20261102-r129.json)
- [两批汇总](basic-r128-r129-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
