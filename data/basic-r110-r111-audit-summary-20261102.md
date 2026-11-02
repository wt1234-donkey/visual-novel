# 第110、111批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 110 | 1337 | 515 | 500 | 26 | 283 | 13 |
| 111 | 1476 | 502 | 500 | 42 | 197 | 235 |

## 289条暂存处理

VNDB输入37条、NextMoe输入252条；本轮从旧暂存入选289条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：53,841 → 54,841。

## 新续采位置

- VNDB：`v56759`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVE0wTVRGOQ`
- IFDB：`6728`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共68条原始记录，按来源ID合并为60个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v55451 | Till Death Do Us Part | 2025 | vndb-v22540 (2017) | ambiguous-name-year | [110: v55451 / held[0]](vndb-kana-bulk-review-20261102-r110.json) |
| 疑似版本/依赖内容 | vndb:v55565 | Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [110: v55565 / held[1]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55628 | SANA | 2025 | vndb-v43720 (2003) | ambiguous-name-year | [110: v55628 / held[2]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55637 | Five Years | 2025 | vndb-v2374 (2001) | ambiguous-name-year | [110: v55637 / held[3]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55670 | Growing Pains | 2025 | ifdb-d84ng0i76ts22aji (2019) | ambiguous-name-year | [110: v55670 / held[4]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55681 | I Remember You | 2025 | vndb-v51997 (2024) | ambiguous-name-year | [110: v55681 / held[5]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55714 | MGLA | 2023 | vndb-v37982 (2022) | ambiguous-name-year | [110: v55714 / held[6]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55736 | Harmony | 2013 | konami-harmony (2002) | ambiguous-name-year | [110: v55736 / held[7]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55758 | Saishuu Densha | 2018 | vndb-v30710 (1998) | ambiguous-name-year | [110: v55758 / held[8]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55772 | Rebirth | 2010 | nextmoe-26475 (2020) | ambiguous-name-year | [110: v55772 / held[9]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55808 | Tegami | 1995 | vndb-v1298 (2005) | ambiguous-name-year | [110: v55808 / held[10]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55879 | Something Left | 2025 | vndb-v45120 (2023) | ambiguous-name-year | [110: v55879 / held[11]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v55889 | Zai Jian | 2022 | vndb-v42281 (2023) | ambiguous-name-year | [110: v55889 / held[12]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v56023 | Trick and Treat | 2025 | vndb-v16549 (2014) | ambiguous-name-year | [110: v56023 / held[13]](vndb-kana-bulk-review-20261102-r110.json); [111: 52315 / held[0]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56149 | Botan'yuki | 2003 | vndb-v46033 (2004) | ambiguous-name-year | [110: v56149 / held[14]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v56213 | Strange House | 2010 | vndb-v47762 (2023) | ambiguous-name-year | [110: v56213 / held[15]](vndb-kana-bulk-review-20261102-r110.json) |
| 疑似版本/依赖内容 | vndb:v56311 | Time To Decide / Over The Phone | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [110: v56311 / held[16]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v56488 | &lt;&lt;Inreal'nost'&gt;&gt; | 2023 | vndb-v13626 (2013) | ambiguous-name-year | [110: v56488 / held[17]](vndb-kana-bulk-review-20261102-r110.json); [111: 52728 / held[1]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 疑似版本/依赖内容 | vndb:v56546 | Tachi Cole! 2 | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [110: v56546 / held[18]](vndb-kana-bulk-review-20261102-r110.json) |
| 疑似版本/依赖内容 | vndb:v56547 | Tachi Cole! | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [110: v56547 / held[19]](vndb-kana-bulk-review-20261102-r110.json) |
| 名称/年份/身份冲突 | vndb:v56640 | The One | 2025 | vndb-v26697 (2019) | ambiguous-name-year | [110: v56640 / held[20]](vndb-kana-bulk-review-20261102-r110.json); [111: 52860 / held[2]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56643 | Alpha | 2024 | vndb-v4524 (1986) | ambiguous-name-year | [110: v56643 / held[21]](vndb-kana-bulk-review-20261102-r110.json); [111: 52863 / held[3]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56646 | Into the Woods | 2025 | vndb-v38268 (2022) | ambiguous-name-year | [110: v56646 / held[22]](vndb-kana-bulk-review-20261102-r110.json); [111: 52866 / held[4]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56660 | Inheritance | 2025 | vndb-v27875 (2018) | ambiguous-name-year | [110: v56660 / held[23]](vndb-kana-bulk-review-20261102-r110.json); [111: 52876 / held[5]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56663 | Plus One | 2024 | vndb-v44923 (2000) | ambiguous-name-year | [110: v56663 / held[24]](vndb-kana-bulk-review-20261102-r110.json); [111: 52879 / held[6]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56711 | Shipwrecked | 2021 | ifdb-dbszwwmz3y1p4f2i (2016) | ambiguous-name-year | [110: v56711 / held[25]](vndb-kana-bulk-review-20261102-r110.json); [111: 52920 / held[7]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56780 | Love at First Bite | 2025 | vndb-v45830 (2016) | ambiguous-name-year | [111: 52980 / held[8]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56797 | Limerence | 2025 | vndb-v37193 (2022) | ambiguous-name-year | [111: 52995 / held[9]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56814 | The Scalper | 2025 | vndb-v16453 (1999) | ambiguous-name-year | [111: 53009 / held[10]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56845 | Dreamland | 2025 | nextmoe-37228 (2022) | ambiguous-name-year | [111: 53034 / held[11]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 来源日期冲突 | vndb:v56884 | Artificial Affection | 2025-06-14 | NextMoe: 2024-12-29 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [111: 53065 / held[12]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v56921 | AfterParty | 2025 | g1538 (2019) | ambiguous-name-year | [111: 53100 / held[13]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57002 | Blood in the Water | 2026 | vndb-v52545 (2024) | ambiguous-name-year | [111: 53171 / held[14]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57008 | Limerence | 2024 | vndb-v37193 (2022) | ambiguous-name-year | [111: 53177 / held[15]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57066 | Lab Rats | 2025 | vndb-v46750 (2017) | ambiguous-name-year | [111: 53230 / held[16]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57113 | Burden of Proof | 2023 | vndb-v42279 (2018) | ambiguous-name-year | [111: 53276 / held[17]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57115 | Blind Date | 2022 | vndb-v24988 (2018) | ambiguous-name-year | [111: 53278 / held[18]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57137 | Gemini | 2024 | vndb-v2493 (2004) | ambiguous-name-year | [111: 53299 / held[19]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57157 | Eclipse | 2025 | vndb-v6522 (2011) | ambiguous-name-year | [111: 53318 / held[20]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57187 | Ailurophobia | 2025 | vndb-v39232 (2022) | ambiguous-name-year | [111: 53348 / held[21]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 疑似版本/依赖内容 | vndb:v57225 | Kanmi Girls Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [111: 53385 / held[22]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57229 | Little Lamb | 2025 | vndb-v31306 (2021) | ambiguous-name-year | [111: 53389 / held[23]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | vndb:v57231 | Deception | 2025 | vndb-v14997 (2014) | ambiguous-name-year | [111: 53391 / held[24]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:z20nf4sdyoo1o9ol | Ascension | 2023-01-01 00:00:00 | nextmoe-227192 (2013) | name-year-conflict | [111: z20nf4sdyoo1o9ol / held[25]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:1lsvlixuj4m8u86q | Adventure | 2018-03-16 01:00:00 | ifdb-16y1pp3l16qh7khh (2020) | name-year-conflict | [111: 1lsvlixuj4m8u86q / held[26]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:t7bsd50giy9nndv2 | The House | 1993-01-01 00:00:00 | ifdb-83noiwzup8nsasob (2007) | name-year-conflict | [111: t7bsd50giy9nndv2 / held[27]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:vqxi4r7h6jrfnrpg | Virus | 2002-01-01 00:00:00 | g1165 (1997) | name-year-conflict | [111: vqxi4r7h6jrfnrpg / held[28]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:4oww6ykj7z4upz6s | Meltdown | 1993-01-01 00:00:00 | vndb-v48376 (2023) | name-year-conflict | [111: 4oww6ykj7z4upz6s / held[29]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:ywvaovbn5u6hgozu | Weekend | 2005-05-24 01:00:00 | vndb-v47724 (2020) | name-year-conflict | [111: ywvaovbn5u6hgozu / held[30]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:c0rmm8yhtup2rqa8 | Monster | 1988-01-01 00:00:00 | vndb-v51448 (2024) | name-year-conflict | [111: c0rmm8yhtup2rqa8 / held[31]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:wshx0ocn2u9rfvve | Castle Adventure | 1982-11-01 00:00:00 | ifdb-mz7tsvrsrrqhddhw (1984) | name-year-conflict | [111: wshx0ocn2u9rfvve / held[32]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:4ujqlsiy2g70diqa | Dragon Quest | 1994-01-01 00:00:00 | enix-dq1 (1986) | name-year-conflict | [111: 4ujqlsiy2g70diqa / held[33]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:2h56epweeq6ajomi | The Great Escape | 1984-01-01 00:00:00 | ifdb-wtsh0u4b7xw2expn (2000) | name-year-conflict | [111: 2h56epweeq6ajomi / held[34]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:or6q1mucaqjtfs5x | Ghost Town | 1985-01-01 00:00:00 | ai-ghost-town (1980); microcabin-ghost (1984) | name-year-conflict | [111: or6q1mucaqjtfs5x / held[35]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:99q4ysnvj2aq5ki1 | The Wizard of Oz | 1995-01-01 00:00:00 | g1604 (1985) | name-year-conflict | [111: 99q4ysnvj2aq5ki1 / held[36]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:ldynf8j06b9iim05 | explorer | 2013-01-01 00:00:00 | ifdb-odbjqn2xmw3pgkiy (1984) | name-year-conflict | [111: ldynf8j06b9iim05 / held[37]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:emztzj9stz7u6pmy | Ascenseur | 2008-01-01 00:00:00 | vndb-v40539 (2021) | name-year-conflict | [111: emztzj9stz7u6pmy / held[38]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:4hmgcwho6v19weyw | Discord | 2001-01-01 00:00:00 | vndb-v19434 (2015) | name-year-conflict | [111: 4hmgcwho6v19weyw / held[39]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:cmqevo7j72tph16n | end | 2015-12-28 01:00:00 | vndb-v49443 (2003) | name-year-conflict | [111: cmqevo7j72tph16n / held[40]](nextmoe-ifdb-bulk-review-20261102-r111.json) |
| 名称/年份/身份冲突 | ifdb:pyuu6dl4xf7jw6mj | Genie | 2002-01-01 00:00:00 | vndb-v21098 (2017) | name-year-conflict | [111: pyuu6dl4xf7jw6mj / held[41]](nextmoe-ifdb-bulk-review-20261102-r111.json) |

## 原始证据

- [第110批审计](vndb-kana-bulk-review-20261102-r110.json)
- [第111批审计](nextmoe-ifdb-bulk-review-20261102-r111.json)
- [两批汇总](basic-r110-r111-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
