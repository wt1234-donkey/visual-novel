# 第120、121批采集与隔离审计

扫描数包含旧暂存复核；去重数是复用已有来源身份或名称/别名的记录次数，不是独立旧作品数。

| 批次 | 复核及扫描 | 去重复用 | 新增 | 隔离记录 | 无效/缺年/未发行等 | 新暂存 |
|---|---:|---:|---:|---:|---:|---:|
| 120 | 1601 | 578 | 500 | 30 | 468 | 25 |
| 121 | 1564 | 553 | 500 | 50 | 226 | 235 |

## 233条暂存处理

VNDB输入1条、NextMoe输入232条；本轮从旧暂存入选232条。逐条处理状态保存在两个审计文件的pendingQueueReview中。

基础身份库：58,896 → 59,896。

## 新续采位置

- VNDB：`v63900`
- NextMoe：`cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOakF4T1RKOQ`
- IFDB：`7859`（固定档案及原排序不变）

## 年份、身份与疑似版本隔离清单

共80条原始记录，按来源ID合并为62个待核来源身份。名称相同或年份不同不代表已确认同一作品；疑似版本也不代表已确认没有新增内容。

| 类别 | 来源身份 | 标题 | 本次来源年/日期 | 匹配身份（年）或另一来源日期 | 原因 | 原始记录定位 |
|---|---|---|---|---|---|---|
| 名称/年份/身份冲突 | vndb:v62382 | SECRET | 2006 | vndb-v15180 (1997) | ambiguous-name-year | [120: v62382 / held[0]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v62531 | Danganronpa: Hope Recreation | 2024 | vndb-v62532 (2025) | ambiguous-name-year | [120: v62531 / held[1]](vndb-kana-bulk-review-20261102-r120.json); [121: 58161 / held[0]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v62815 | EPISODE-ZERO | 2002 | vndb-v39430 (2004) | ambiguous-name-year | [120: v62815 / held[2]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v62903 | Limerence | 2026 | vndb-v37193 (2022) | ambiguous-name-year | [120: v62903 / held[3]](vndb-kana-bulk-review-20261102-r120.json); [121: 58499 / held[1]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v62910 | How To Be Human | 2026 | vndb-v53010 (2024) | ambiguous-name-year | [120: v62910 / held[4]](vndb-kana-bulk-review-20261102-r120.json); [121: 58506 / held[2]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 疑似版本/依赖内容 | vndb:v62922 | Demo Boku wa, Konna Mono Janai. | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [120: v62922 / held[5]](vndb-kana-bulk-review-20261102-r120.json); [121: 58518 / held[3]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v62969 | COLORS | 2007 | vndb-v20722 (2008) | ambiguous-name-year | [120: v62969 / held[6]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v62977 | Rain | 2005 | vndb-v17316 (2013) | ambiguous-name-year | [120: v62977 / held[7]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v63088 | Cursed | 2024 | vndb-v33412 (2021) | ambiguous-name-year | [120: v63088 / held[8]](vndb-kana-bulk-review-20261102-r120.json); [121: 58673 / held[4]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63090 | Futarigurashi | 2025 | nextmoe-1241 (2008); vndb-v246 (1997) | ambiguous-name-year | [120: v63090 / held[9]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v63114 | One Day | 2026 | vndb-v37038 (2001); vndb-v43186 (2023) | ambiguous-name-year | [120: v63114 / held[10]](vndb-kana-bulk-review-20261102-r120.json); [121: 58696 / held[5]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63287 | Chousa Chuu ni …!? | 2025 | vndb-v63286 (2023) | ambiguous-name-year | [120: v63287 / held[11]](vndb-kana-bulk-review-20261102-r120.json); [121: 58848 / held[6]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 疑似版本/依赖内容 | vndb:v63322 | Hara Harami Imouto's!?(Sisters) ~Aaah!? Onii-chan no Ecchi…Demo…Daisuki♪~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [120: v63322 / held[12]](vndb-kana-bulk-review-20261102-r120.json); [121: 58875 / held[7]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63383 | puppy | 2026 | vndb-v38748 (2022) | ambiguous-name-year | [120: v63383 / held[13]](vndb-kana-bulk-review-20261102-r120.json); [121: 58932 / held[8]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63393 | Elizabeth | 2025 | vndb-v45718 (2023) | ambiguous-name-year | [120: v63393 / held[14]](vndb-kana-bulk-review-20261102-r120.json); [121: 58942 / held[9]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63410 | Ryoujoku Katei Kyoushi | 2006 | vndb-v10298 (2003); vndb-v14512 (1996) | ambiguous-name-year | [120: v63410 / held[15]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v63449 | ECLIPSE | 2005 | vndb-v6522 (2011) | ambiguous-name-year | [120: v63449 / held[16]](vndb-kana-bulk-review-20261102-r120.json) |
| 来源日期冲突 | vndb:v63528 | Yumeno Owari | 2025; 2025-05-03 | vndb-v27237 (2000); NextMoe: 2012-02-13 | ambiguous-name-year; VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [120: v63528 / held[17]](vndb-kana-bulk-review-20261102-r120.json); [121: 59065 / held[10]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63550 | The Beginning of the End | 2026 | ifdb-wmvzp92l98ouxpho (1992) | ambiguous-name-year | [120: v63550 / held[18]](vndb-kana-bulk-review-20261102-r120.json); [121: 59085 / held[11]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63575 | Star Fall | 2026 | vndb-v49371 (2024) | ambiguous-name-year | [120: v63575 / held[19]](vndb-kana-bulk-review-20261102-r120.json); [121: 59108 / held[12]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63591 | Go Shujin Sama to Boku | 2002 | vndb-v40657 (2006) | ambiguous-name-year | [120: v63591 / held[20]](vndb-kana-bulk-review-20261102-r120.json) |
| 疑似版本/依赖内容 | vndb:v63610 | My Final Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [120: v63610 / held[21]](vndb-kana-bulk-review-20261102-r120.json); [121: 59141 / held[13]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63624 | Snowdrift | 2026 | ifdb-8toxgs1oxuya8jq0 (2017) | ambiguous-name-year | [120: v63624 / held[22]](vndb-kana-bulk-review-20261102-r120.json); [121: 59154 / held[14]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63766 | The Psychologist | 2026 | vndb-v31779 (2021) | ambiguous-name-year | [120: v63766 / held[23]](vndb-kana-bulk-review-20261102-r120.json); [121: 59280 / held[15]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 疑似版本/依赖内容 | vndb:v63768 | Dizzy-tan Fan Disc ~Osana Tsuma wa Man 3sai!?~ | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [120: v63768 / held[24]](vndb-kana-bulk-review-20261102-r120.json) |
| 疑似版本/依赖内容 | vndb:v63769 | Dizzy-tan Fan Disc #RELOAD | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [120: v63769 / held[25]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v63831 | One Last Goodbye | 2026 | nextmoe-36715 (2022) | ambiguous-name-year | [120: v63831 / held[26]](vndb-kana-bulk-review-20261102-r120.json); [121: 59328 / held[16]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63845 | Asphyxia | 2019 | vndb-v18060 (2015) | ambiguous-name-year | [120: v63845 / held[27]](vndb-kana-bulk-review-20261102-r120.json); [121: 59342 / held[17]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63862 | Tegami | 2003 | vndb-v1298 (2005) | ambiguous-name-year | [120: v63862 / held[28]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v63879 | Onna Kyoushi | 2004 | nextmoe-7240 (2002) | ambiguous-name-year | [120: v63879 / held[29]](vndb-kana-bulk-review-20261102-r120.json) |
| 名称/年份/身份冲突 | vndb:v63934 | EO:Lockdown | 2026 | vndb-v63907 (2025) | ambiguous-name-year | [121: 59427 / held[18]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63964 | Cupid | 2026 | nextmoe-20251 (2015) | ambiguous-name-year | [121: 59456 / held[19]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v63972 | Lost Connections | 2026 | vndb-v45577 (2023) | ambiguous-name-year | [121: 59464 / held[20]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v64090 | Sakura Saku | 2026 | vndb-v63595 (2001) | ambiguous-name-year | [121: 59569 / held[21]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 来源日期冲突 | vndb:v64124 | Fairy Mate ~Te Nori Yousei to Sugosu Hibi~ | 2026-05-23 | NextMoe: 2025-09-19 | VNDB original year is later than the earlier release claimed by NextMoe; source association or original year requires review. | [121: 59603 / held[22]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 疑似版本/依赖内容 | vndb:v64171 | Battle Live! The Idol School Collection | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [121: 59648 / held[23]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v64255 | Ashes to Ashes | 2026 | vndb-v43894 (2023) | ambiguous-name-year | [121: 59727 / held[24]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v64263 | snow drop | 2016 | vndb-v112 (2000) | ambiguous-name-year | [121: 59735 / held[25]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v64264 | Fairy Tale | 2013 | vndb-v11102 (2012) | ambiguous-name-year | [121: 59736 / held[26]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | vndb:v64428 | Jack in the Box | 2013 | ifdb-6rhf7eaywwh2bv4q (2007) | ambiguous-name-year | [121: 59894 / held[27]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 疑似版本/依赖内容 | vndb:v64530 | Dimitrescu's Trial | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [121: 59992 / held[28]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 疑似版本/依赖内容 | vndb:v64637 | Trial And Error Sensei Daisuki!! Hen | 原审计未提供 | 内容关系待核 | possible-edition-or-dependent-content | [121: 60091 / held[29]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:4duolnjc42ehvcsc | The Amulet | 2004-01-01 00:00:00 | ifdb-t9yu9px5qt2qolr8 (1990) | name-year-conflict | [121: 4duolnjc42ehvcsc / held[30]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:qnyl1ifw24cw2kh8 | The Guardian | 2011-10-01 01:00:00 | nextmoe-33403 (2023) | name-year-conflict | [121: qnyl1ifw24cw2kh8 / held[31]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:puse276wmmjj42mb | Adrift | 2025-12-01 01:00:00 | nextmoe-14737 (2011) | name-year-conflict | [121: puse276wmmjj42mb / held[32]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:saf8k4k7a4q490yu | The Prisoner | 1984-01-01 00:00:00 | vndb-v16625 (2015) | name-year-conflict | [121: saf8k4k7a4q490yu / held[33]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:psawlvvpyhh1q7tf | stars | 2015-04-08 01:00:00 | vndb-v9097 (1997) | name-year-conflict | [121: psawlvvpyhh1q7tf / held[34]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:i6ykddfxjyrjlxia | The Amulet | 1985-01-01 00:00:00 | ifdb-t9yu9px5qt2qolr8 (1990) | name-year-conflict | [121: i6ykddfxjyrjlxia / held[35]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:pt5de7xn3j7ms8og | Home | 2026-06-29 01:00:00 | vndb-v15962 (2014) | name-year-conflict | [121: pt5de7xn3j7ms8og / held[36]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:mdjlmgpdjeqnhsxl | Pyramid | 1986-01-01 00:00:00 | ifdb-o9jmq54q6s84mp6w (1990) | name-year-conflict | [121: mdjlmgpdjeqnhsxl / held[37]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:lq1vuafjav88xoya | The Temple | 2012-01-01 00:00:00 | ifdb-kq9qgjkf2k6xn1c0 (2002) | name-year-conflict | [121: lq1vuafjav88xoya / held[38]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:0ftyb3oixpk97b77 | Menagerie | 1982-09-01 01:00:00 | ifdb-g6j7mzwr5oz50zzw (2001) | name-year-conflict | [121: 0ftyb3oixpk97b77 / held[39]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:h5832qua165vuw8o | Letters | 2016-10-01 01:00:00 | vndb-v4342 (2009) | name-year-conflict | [121: h5832qua165vuw8o / held[40]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:b7hze6jtld5i8wx8 | Breaker | 2020-01-01 00:00:00 | vndb-v35264 (2021) | name-year-conflict | [121: b7hze6jtld5i8wx8 / held[41]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:vjunv4o9yenejd7n | Voices | 2013-12-17 01:00:00 | vndb-v46712 (2023) | name-year-conflict | [121: vjunv4o9yenejd7n / held[42]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:4gp22g2h4dzvuwds | The Hole | 2022-12-21 01:00:00 | vndb-v40005 (2005) | name-year-conflict | [121: 4gp22g2h4dzvuwds / held[43]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:bxcc1elm88h10ojp | Venom | 1988-01-01 00:00:00 | vndb-v44320 (2023) | name-year-conflict | [121: bxcc1elm88h10ojp / held[44]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:59d0udoc5ofsg7fj | Redemption | 2003-01-01 00:00:00 | vndb-v44926 (2014) | name-year-conflict | [121: 59d0udoc5ofsg7fj / held[45]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:eniz1i3tehmq7zyz | Monsters | 2013-05-25 01:00:00 | ifdb-202tyoigv6ycmnbg (2004) | name-year-conflict | [121: eniz1i3tehmq7zyz / held[46]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:cytdripio9o61zu5 | The Fugitive | 1985-03-01 00:00:00 | ifdb-ocwbz5r9bcpq2wx7 (2001) | name-year-conflict | [121: cytdripio9o61zu5 / held[47]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:o23p32yj3d0cf4id | hide and seek | 2019-08-02 01:00:00 | ifdb-ljb863xxbw125k2g (1997) | name-year-conflict | [121: o23p32yj3d0cf4id / held[48]](nextmoe-ifdb-bulk-review-20261102-r121.json) |
| 名称/年份/身份冲突 | ifdb:j8idhxmkrlnjr5tm | The Mansion | 2019-01-01 00:00:00 | ifdb-cgix4gqeb4fqcbsw (1991) | name-year-conflict | [121: j8idhxmkrlnjr5tm / held[49]](nextmoe-ifdb-bulk-review-20261102-r121.json) |

## 原始证据

- [第120批审计](vndb-kana-bulk-review-20261102-r120.json)
- [第121批审计](nextmoe-ifdb-bulk-review-20261102-r121.json)
- [两批汇总](basic-r120-r121-diversity-20261102.json)

测试及PR/部署运行记录另见对应GitHub Actions和PR；本报告不预先声明尚未执行的发布成功。
