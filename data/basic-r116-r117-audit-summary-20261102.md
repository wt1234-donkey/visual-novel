# 第116、117批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 116 | 1459 | 423 | 500 | 46 | 445 | 45 |
| 117 | 1646 | 529 | 500 | 57 | 319 | 241 |

## 280条暂存处理

VNDB输入59条、NextMoe输入221条；本轮从旧暂存入选280条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：56,841 → 57,841。

## 新续采位置

- VNDB：`v60931`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOVGN5TXpoOQ`
- IFDB：`7405`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共103条原始记录，按来源ID合并为74个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v59531 | Hello World! | 2025 | g599 (2002) | ambiguous-name-year | [116: v59531 / held[0]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59542 | Echoes | 2025 | vndb-v50422 (2024) | ambiguous-name-year | [116: v59542 / held[1]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59545 | Curse | 2025 | konami-curse (2005) | ambiguous-name-year | [116: v59545 / held[2]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59575 | GOLOD | 2025 | vndb-v51416 (2016) | ambiguous-name-year | [116: v59575 / held[3]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59600 | Mirror \| Mirror | 2025 | ifdb-vke24gmd8usqywu4 (2020) | ambiguous-name-year | [116: v59600 / held[4]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59631 | The Wedding | 2026 | ifdb-5r1iabxsfwmz40ev (1996) | ambiguous-name-year | [116: v59631 / held[5]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59632 | Onigashima | 2025 | vndb-v41832 (2001) | ambiguous-name-year | [116: v59632 / held[6]](vndb-kana-bulk-review-20261102-r116.json) |
| 疑似版本/依赖内容 | vndb:v59647 | Hazuki Bukkake CG Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [116: v59647 / held[7]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59659 | Strings attached | 2025 | ifdb-p71wudmczcl8to5s (2026) | ambiguous-name-year | [116: v59659 / held[8]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59768 | Night Drive | 2025 | ifdb-2174obt391f36ave (2017) | ambiguous-name-year | [116: v59768 / held[9]](vndb-kana-bulk-review-20261102-r116.json) |
| 疑似版本/依赖内容 | vndb:v59836 | Futanari Witches Pantsu Janai kara Hamide chau! ! Triple Edition | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [116: v59836 / held[10]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59857 | Leucochloridium | 2025 | vndb-v43872 (2014) | ambiguous-name-year | [116: v59857 / held[11]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v59885 | The Whisperer in Darkness | 2025 | vndb-v20151 (2016) | ambiguous-name-year | [116: v59885 / held[12]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v60010 | Love Bites | 2025 | vndb-v18977 (2018) | ambiguous-name-year | [116: v60010 / held[13]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v60025 | Forget It | 2025 | vndb-v40669 (2022) | ambiguous-name-year | [116: v60025 / held[14]](vndb-kana-bulk-review-20261102-r116.json); [117: 55926 / held[0]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60053 | Drop Dead Gorgeous | 2025 | vndb-v49716 (2023) | ambiguous-name-year | [116: v60053 / held[15]](vndb-kana-bulk-review-20261102-r116.json); [117: 55951 / held[1]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60086 | Oddity | 2025 | vndb-v45288 (2023) | ambiguous-name-year | [116: v60086 / held[16]](vndb-kana-bulk-review-20261102-r116.json); [117: 55983 / held[2]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60122 | Divine Devotion | 2024 | vndb-v54589 (2025) | ambiguous-name-year | [116: v60122 / held[17]](vndb-kana-bulk-review-20261102-r116.json); [117: 56009 / held[3]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 疑似版本/依赖内容 | vndb:v60223 | Atelier Kurimami Fan Disc ~ Playmate | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [116: v60223 / held[18]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v60244 | Bloom | 2026 | vndb-v50826 (2024) | ambiguous-name-year | [116: v60244 / held[19]](vndb-kana-bulk-review-20261102-r116.json); [117: 56099 / held[4]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60248 | Double Exposure | 2025 | vndb-v27286 (2019) | ambiguous-name-year | [116: v60248 / held[20]](vndb-kana-bulk-review-20261102-r116.json); [117: 56103 / held[5]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60292 | Lewd Island | 2026 | vndb-v29011 (2020) | ambiguous-name-year | [116: v60292 / held[21]](vndb-kana-bulk-review-20261102-r116.json); [117: 56144 / held[6]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60311 | PHOBOS | 2025 | vndb-v9006 (1992) | ambiguous-name-year | [116: v60311 / held[22]](vndb-kana-bulk-review-20261102-r116.json); [117: 56158 / held[7]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60324 | Nightbound | 2025 | nextmoe-26691 (2019) | ambiguous-name-year | [116: v60324 / held[23]](vndb-kana-bulk-review-20261102-r116.json); [117: 56171 / held[8]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60330 | BLOOD SUGAR | 2024 | vndb-v35714 (2017) | ambiguous-name-year | [116: v60330 / held[24]](vndb-kana-bulk-review-20261102-r116.json); [117: 56177 / held[9]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60341 | ​Happily ever after | 2025 | vndb-v52508 (2024) | ambiguous-name-year | [116: v60341 / held[25]](vndb-kana-bulk-review-20261102-r116.json); [117: 56187 / held[10]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60361 | Going Up? | 2025 | ifdb-kjoi2d4d8ir6edjv (2018) | ambiguous-name-year | [116: v60361 / held[26]](vndb-kana-bulk-review-20261102-r116.json); [117: 56207 / held[11]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60372 | Love Craft | 2024 | vndb-v60211 (2025) | ambiguous-name-year | [116: v60372 / held[27]](vndb-kana-bulk-review-20261102-r116.json); [117: 56218 / held[12]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60402 | In Plain Sight | 2025 | vndb-v51816 (2024) | ambiguous-name-year | [116: v60402 / held[28]](vndb-kana-bulk-review-20261102-r116.json); [117: 56246 / held[13]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60403 | You and Me+ | 2025 | vndb-v18829 (2015) | ambiguous-name-year | [116: v60403 / held[29]](vndb-kana-bulk-review-20261102-r116.json); [117: 56247 / held[14]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60405 | Something Borrowed | 2025 | vndb-v34235 (2021) | ambiguous-name-year | [116: v60405 / held[30]](vndb-kana-bulk-review-20261102-r116.json); [117: 56249 / held[15]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60406 | Monsters | 2025 | ifdb-202tyoigv6ycmnbg (2004) | ambiguous-name-year | [116: v60406 / held[31]](vndb-kana-bulk-review-20261102-r116.json); [117: 56250 / held[16]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60407 | Nicole | 2025 | vndb-v10587 (2013) | ambiguous-name-year | [116: v60407 / held[32]](vndb-kana-bulk-review-20261102-r116.json); [117: 56251 / held[17]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60418 | KuzuYuzu ~True End Story~ | 2009 | vndb-v18614 (2008) | ambiguous-name-year | [116: v60418 / held[33]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v60422 | Trick Treat Test! | 2025 | vndb-v14796 (2014) | ambiguous-name-year | [116: v60422 / held[34]](vndb-kana-bulk-review-20261102-r116.json); [117: 56265 / held[18]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60493 | Haishin | 2025 | vndb-v31095 (2021) | ambiguous-name-year | [116: v60493 / held[35]](vndb-kana-bulk-review-20261102-r116.json); [117: 56330 / held[19]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60499 | Reflection | 2025 | vndb-v32611 (2021) | ambiguous-name-year | [116: v60499 / held[36]](vndb-kana-bulk-review-20261102-r116.json); [117: 56336 / held[20]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60592 | Jian Fang | 2025 | nextmoe-8498 (2021) | ambiguous-name-year | [116: v60592 / held[37]](vndb-kana-bulk-review-20261102-r116.json); [117: 56424 / held[21]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60737 | Home | 2025 | vndb-v15962 (2014) | ambiguous-name-year | [116: v60737 / held[38]](vndb-kana-bulk-review-20261102-r116.json); [117: 56553 / held[22]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60743 | Memories Never Die | 2019 | vndb-v49400 (2022) | ambiguous-name-year | [116: v60743 / held[39]](vndb-kana-bulk-review-20261102-r116.json); [117: 56559 / held[23]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 疑似版本/依赖内容 | vndb:v60783 | Waifu by Myside: Patch Me In | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [116: v60783 / held[40]](vndb-kana-bulk-review-20261102-r116.json); [117: 56596 / held[24]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60800 | the experiment | 2024 | ifdb-7hv3wd80cnibrfle (2018) | ambiguous-name-year | [116: v60800 / held[41]](vndb-kana-bulk-review-20261102-r116.json); [117: 56611 / held[25]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60822 | Maneater | 2025 | vndb-v57565 (2024) | ambiguous-name-year | [116: v60822 / held[42]](vndb-kana-bulk-review-20261102-r116.json); [117: 56630 / held[26]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60832 | Limelight | 2025 | vndb-v21314 (1989) | ambiguous-name-year | [116: v60832 / held[43]](vndb-kana-bulk-review-20261102-r116.json); [117: 56640 / held[27]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v60886 | ChiarOscuro | 2025 | ifdb-da1m33pz3allwbcx (2022) | ambiguous-name-year | [116: v60886 / held[44]](vndb-kana-bulk-review-20261102-r116.json); [117: 56690 / held[28]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 疑似版本/依赖内容 | vndb:v60910 | "Otome" Series Shujinkou Patch 2 | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [116: v60910 / held[45]](vndb-kana-bulk-review-20261102-r116.json) |
| 名称/年份/身份冲突 | vndb:v60981 | PHANTASMAGORIA | 2025 | g1127 (1995) | ambiguous-name-year | [117: 56770 / held[29]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61028 | Mi Primer Amor | 2025 | vndb-v50359 (2022) | ambiguous-name-year | [117: 56812 / held[30]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 来源日期冲突 | vndb:v61149 | Gravekeeper | 2025-12-01 | NextMoe: 2020-09-20 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [117: 56925 / held[31]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61154 | Headlights | 2025 | ifdb-5x7v9fiblus23eb6 (2022) | ambiguous-name-year | [117: 56930 / held[32]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61188 | Mirrors | 2025 | vndb-v18091 (1990) | ambiguous-name-year | [117: 56958 / held[33]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61265 | The Masterpiece | 2025 | vndb-v30845 (2021) | ambiguous-name-year | [117: 57023 / held[34]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61313 | Wild West | 2022 | vndb-v6052 (2012) | ambiguous-name-year | [117: 57065 / held[35]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61404 | Cutting Edge | 2026 | vndb-v53751 (2024) | ambiguous-name-year | [117: 57146 / held[36]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 来源日期冲突 | vndb:v61429 | B.E.S.T | 2025-08-29 | NextMoe: 2023-05-29 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [117: 57170 / held[37]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61484 | last call | 2025 | vndb-v21519 (2017) | ambiguous-name-year | [117: 57220 / held[38]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61493 | A College Education | 2026 | vndb-v5616 (2006) | ambiguous-name-year | [117: 57228 / held[39]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | vndb:v61496 | Delirium | 2025 | vndb-v28248 (2016) | ambiguous-name-year | [117: 57231 / held[40]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:712qja53snen3oez | Ground Zero | 1985-08-01 00:00:00 | ifdb-1eis3bu5w67ou2lp (1984) | name-year-conflict | [117: 712qja53snen3oez / held[41]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:6vjoir3xk915psqe | Babyface | 2020-10-01 01:00:00 | vndb-v2064 (2000) | name-year-conflict | [117: 6vjoir3xk915psqe / held[42]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:mayi3yxq33htyn7c | Pegasus | 1985-01-01 00:00:00 | vndb-v7550 (2011) | name-year-conflict | [117: mayi3yxq33htyn7c / held[43]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:ybbqk5dutu0jr7qp | One Night Stand | 2016-10-20 01:00:00 | nextmoe-32903 (2022) | name-year-conflict | [117: ybbqk5dutu0jr7qp / held[44]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:c1474qcnjcy4rrz2 | Escape | 2017-01-01 00:00:00 | nextmoe-7725 (2015) | name-year-conflict | [117: c1474qcnjcy4rrz2 / held[45]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:6prxdjcx267jdrk7 | Frog | 2023-06-28 01:00:00 | vndb-v11025 (2012) | name-year-conflict | [117: 6prxdjcx267jdrk7 / held[46]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:1icn389bkjchkxgt | Leviathan | 2021-04-29 01:00:00 | vndb-v46014 (2007) | name-year-conflict | [117: 1icn389bkjchkxgt / held[47]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:3qv4tbxc06dh275u | Homecoming | 2020-08-27 01:00:00 | vndb-v45673 (2018) | name-year-conflict | [117: 3qv4tbxc06dh275u / held[48]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:b8k1sf87k1byy9a0 | Scoop | 1985-01-01 00:00:00 | vndb-v61802 (2003) | name-year-conflict | [117: b8k1sf87k1byy9a0 / held[49]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:8qgk0fd0vdqrdmh9 | Escape | 1987-01-01 00:00:00 | nextmoe-7725 (2015) | name-year-conflict | [117: 8qgk0fd0vdqrdmh9 / held[50]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:fq7djzkmrjy3rp7t | Empyrean | 2016-04-23 01:00:00 | vndb-v36283 (2022) | name-year-conflict | [117: fq7djzkmrjy3rp7t / held[51]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:cfaida8lq4quiwba | The Mist | 2013-09-16 01:00:00 | ifdb-ar75k5yjtdgttj1o (1985) | name-year-conflict | [117: cfaida8lq4quiwba / held[52]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:hag9leik8yy0n5rj | Friends? | 2022-10-12 01:00:00 | nextmoe-14806 (2012) | name-year-conflict | [117: hag9leik8yy0n5rj / held[53]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:9gdt0vqq0yxztafh | Time | 2014-08-21 01:00:00 | vndb-v56190 (2021) | name-year-conflict | [117: 9gdt0vqq0yxztafh / held[54]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:fcas37p9u01i2sij | One Week | 2001-01-01 00:00:00 | vndb-v45525 (2023) | name-year-conflict | [117: fcas37p9u01i2sij / held[55]](nextmoe-ifdb-bulk-review-20261102-r117.json) |
| 名称/年份/身份冲突 | ifdb:lkiup6xmiwifkvdi | Hydrangea | 2024-03-16 01:00:00 | vndb-v43849 (2012) | name-year-conflict | [117: lkiup6xmiwifkvdi / held[56]](nextmoe-ifdb-bulk-review-20261102-r117.json) |

## 原始证据

- [第116批审计](vndb-kana-bulk-review-20261102-r116.json)
- [第117批审计](nextmoe-ifdb-bulk-review-20261102-r117.json)
- [两批汇总](basic-r116-r117-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
