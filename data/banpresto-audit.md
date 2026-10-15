# Banpresto（万普）首批剧情与RPG专题核对

核对日期：2026-10-15。目标仓库：`wt1234-donkey/visual-novel`。

## 成立时间与选择理由

集团2008年重组公告第2页列旧Banpresto成立日为1977年4月30日；2006年公告另有月级日期。以可读的集团原始公告为日级依据，不套用2008年景品公司的成立时间。原库g913《我的女神》的电脑首发已经明确署Banpresto，因此本轮回补1977组尚无专题的既有发行主体，早于1978年成立的KOEI。

- 成立及重组原始公告：https://www.bandainamco.co.jp/releases/images/3/42276.pdf
- 2006年成立月份旁证：https://www.bandainamco.co.jp/releases/images/3/29288.pdf

旧Banpresto的游戏业务于2008年由Bandai Namco Games承继，后继新增内容保留该发行主体。Bandai母公司、Namco与Banpresto不得互设别名。未给未核成立日期的厂商强排日级顺序，也不声称世界游戏厂商已穷尽。

## 本轮边界

13部作品：复用1部；新增主库3部；新建专题RPG记录9部。原有《我的女神》的作品、两项内容和两条发行对象完全复用。新增部分共16个内容身份／16条首次内容发行（12个原作、4个有证据增补）。专题合计18个内容身份／18条发行。

RPG存放于共享的company-coverage.json专题数据，通过互动CSV和专题卡片展示；内容关系待核的发行才进入内容审核CSV，本轮新RPG无此类行。首页四类主库保持实际类型边界；主库内容／平台CSV不包含专题RPG。完整RPG内容和发行数据保存在专题JSON中。

不新增纯日常养成、麻将、棋盘或纯竞技作品。RPG的夜会话、好感度与旅店剧情背景不等于独立日程养成玩法。此为首批，非万普全目录完成。

## 具名作品与互动方式

| 原作年 | 作品／ID | 位置 | 内容／发行 | 互动标签 | 首发／内容依据 |
|---|---|---|---|---|---|
| 1993 | 我的女神（1993年冒险游戏）（g913） | 主库复用 | 2／2 | 选项分支 | https://ja.wikipedia.org/wiki/ああっ女神さまっ |
| 1995 | 学校里发生的恐怖故事（g1061） | 新增主库 | 2／2 | 选项分支 | https://www.nintendo.co.jp/wii/vc/vc_gkh/vc_gkh_01.html |
| 1996 | 晦：月之隐（g1062） | 新增主库 | 1／1 | 选项分支 | https://www.nintendo.co.jp/wii/vc/vc_tuki/vc_tuki_01.html |
| 2000 | 召唤之夜（banpresto-sn1） | 专题RPG | 1／1 | 选项分支、战术策略、战斗指令 | https://www.gavas.jp/products/detail.php?product_id=9113 |
| 2001 | 召唤之夜2（banpresto-sn2） | 专题RPG | 2／2 | 选项分支、战术策略、战斗指令 | https://game.watch.impress.co.jp/docs/20011225/ps.htm |
| 2003 | 召唤之夜：铸剑物语（banpresto-craft1） | 专题RPG | 1／1 | 选项分支、直接移动、即时动作 | https://www.nintendo.co.jp/n08/before/03_0406.html |
| 2003 | 召唤之夜3（banpresto-sn3） | 专题RPG | 2／2 | 选项分支、战术策略、战斗指令 | https://game.watch.impress.co.jp/docs/ship/200308_1.htm |
| 2004 | 召唤之夜：铸剑物语2（banpresto-craft2） | 专题RPG | 1／1 | 选项分支、直接移动、即时动作 | https://www.nintendo.co.jp/n08/before/04_0810.html |
| 2005 | 召唤之夜：铸剑物语 起源之石（banpresto-craft3） | 专题RPG | 1／1 | 选项分支、直接移动、即时动作 | https://www.nintendo.co.jp/n08/index.html |
| 2005 | 召唤之夜外传：破晓之翼（banpresto-ex） | 专题RPG | 1／1 | 选项分支、直接移动、即时动作 | https://game.watch.impress.co.jp/docs/20050523/sum.htm |
| 2006 | 召唤之夜4（banpresto-sn4） | 专题RPG | 2／2 | 选项分支、战术策略、战斗指令 | https://game.watch.impress.co.jp/docs/20060628/sn.htm |
| 2007 | 召唤之夜：双生时代 精灵们的共鸣（banpresto-twin） | 专题RPG | 1／1 | 选项分支、直接移动、即时动作 | https://www.nintendo.co.jp/ds/software/as7j/index.html |
| 2007 | 四十八（暂定）（g1063） | 新增主库 | 1／1 | 选项分支 | https://game.watch.impress.co.jp/docs/20071120/48.htm |

## 后发内容的准入依据

| 作品 | 内容首发 | 相对内容 | 核实增量 | 证据 |
|---|---|---|---|---|
| 学校里发生的恐怖故事 | 1996 · S版：新增女主人公与剧情 | g1061-c-original | 相对1995年SFC原作，1996/07/19的S版新增女主人公剧情，并重作图像与声音。女主剧情是单列内容身份的依据，普通PS平台适配不是。 | https://www.gavas.jp/products/detail.php?product_id=9153 |
| 召唤之夜2 | 2008 · DS版：新增召唤兽 | banpresto-sn2-c-original | 相对2001年PS原作，2008/08/07的DS版由官方明确列出新规召唤兽；新可用召唤内容作为增补依据，同时改用召唤沟通等系统。未将系统便利性本身当新剧情。 | https://www.nintendo.co.jp/ds/software/yskj/index.html |
| 召唤之夜3 | 2012 · PSP版：新增插画、人物录音与战斗会话 | banpresto-sn3-c-original | 相对2003年PS2原作，2012/10/04的PSP版增加事件插画、重录部分角色声音及大量战斗会话；傀儡单位等系统另说明。具体素材与录音增量使本版单列，UMD和下载包装不拆内容身份。 | https://game.watch.impress.co.jp/docs/news/557821.html |
| 召唤之夜4 | 2012 · PSP版：新增事件插画与白夜战斗事件 | banpresto-sn4-c-original | 相对2006年PS2原作，2012/11/15的PSP版为番外篇增加新绘事件插画，加入无尽回廊深处与白夜成员相关的事件及可用傀儡单位；本轮以新绘素材和新增事件为依据，不将旧番外篇整体误称首次新增。 | https://game.watch.impress.co.jp/docs/news/571705.html |

《召唤之夜》DS版只查到新操作／系统，未据此建立新内容身份；不是宣称其与原版完全相同。《召唤之夜2》官方明确新召唤兽，才单列。普通Archives、廉价版、地区翻译、VC再发行与包装差别均不加行。PSP的UMD／下载形式合为同一内容首发记录，未凭销售形式增加行数。

## 证据层级与未完项目

任天堂的原作回顾和许可产品页用于首发年、玩法与作品介绍；万代南梦宫集团公告用于公司身份。同期GAME Watch报道用于实际发行方与可核增补；历史原版资料库、零售产品介绍、片尾转录和玩家文档是补充证据，不能声称等同原说明书或逐平台实机核查。互动标签仅概览已核主要方式，不保证所有附带小游戏已穷尽。

《铸剑物语2》《起源之石》片尾转录列Voice Cast，记有（部分）；演员名单不支持全语音结论。其他新增原版的配音覆盖未作专项核实，明确记未核实，不因为有主题歌、实写照片或“有声小说”分类就填有配音。

- 《铸剑物语2》原片尾转录：https://raido.moe/staff/gba/gba_summon_night_csm_2.html
- 《起源之石》原片尾转录：https://raido.moe/staff/gba/gba_summon_night_csm_3.html

待补：超级机器人大战、ONI、其他万普剧情RPG以及柯南推理作品；必须逐作核对历史发行方。已见《地下游乐园》《疑惑豪华列车》署Bandai，《黎明纪念碑》许可表署Banpresto，不能把整个系列一并归万普。本轮未给这些待核作品造空记录。后续系列作品是否纳入，应以发行沿革或明确关联证据决定，而非把同版权全部算作同一厂商。

## 验证与发布

执行AGENTS.md规定的三组校验以及专题静态同步检查；同时与origin/main逐ID比对所有既有作品、内容身份、平台发行和专题对象。实际检查结果以本轮完成记录为准。当前更新分支`codex/banpresto-dossier-20261015`从main的440c828建立。发布仅到目标仓库；尚未推送或合并时不记已上线。

已完成：数据验证、12项Python回归测试、84项JavaScript测试、57个专题静态同步检查、新页内部锚点与首页入口检查。与基准逐ID比对，1057部既有主库作品、1240个既有主库内容、2232条既有发行及56个既有专题对象完全一致。两处旧测试的全库固定计数已改为完整ID集合／对应厂商发行集合断言。

发布目标：本批更新经专用分支提交到wt1234-donkey/visual-novel，合并main后使用现有GitHub Pages配置发布；不回写旧仓库。
