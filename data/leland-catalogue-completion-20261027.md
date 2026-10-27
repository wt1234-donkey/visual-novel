# Leland清单补齐及主库来源补充（2026-10-27）

## 远程基线与本次范围

开始前已读取远程main：`e05836e6a4b5989dc3e7a03343ae7ee0b19fd61f`，PR #143已合并，当前无未合并PR。保留既有Leland专题、g045及业务沿革结果。本次依据用户给出的完整清单补缺，不重建旧身份。

专题玩法参考由14行／3组扩为33行／6组，新增19行；其中有18项街机／套件／原型、6项家用机作品、1项3DO改作、6项Williams时期团队项目，以及2行前身／过渡期边界参考。行数含套件、同名改作和合并参考，不能解释为33部独立作品。正文仍为1部既有主库作品g045。

## 本次补齐

| 范围 | 处理 |
| --- | --- |
| 街机与原型 | 原有11条补入Viper、Super Dodge Ball、Aaaargh!、Super Off-Road Track-Pak、Asylum，共16条。另有正文g045与Space Ace套件，因此本次清单18项街机相关项目都有去向。 |
| 家用机 | Pro Quarterback、Super Off Road: The Baja、Fun ’N Games、Troy Aikman NFL Football、Double Dragon V、Kyle Petty’s No Fear Racing六项。 |
| 3DO改作 | 1995年Fun ’N Games独立列参考，Williams署名；未完成素材与小游戏逐项比较，不建立主库内容身份。 |
| 后继团队 | MK3、DOOM、Final DOOM、MK Trilogy、Robotron X、Cruis’n USA，保留Williams／Player 1等实际署名与平台限制。 |
| 前身边界 | Dragon’s Lair／Space Ace原版保留既有Cinematronics身份；补入Up Your Alley过渡期参考。 |

## 两部主库作品

- `g044` Space Ace：保留1984年原作及原内容／发行。添加1991年Leland套件说明，明确斜向输入与取消难度选择；没有证实新增动画、人物或剧情，故不新增作品、内容版本或普通平台发行。专题转换套件行直接链接Cinematronics的原作卡片。
- `g045` Dragon’s Lair II：复用已有1991记录，补充Don Bluth动画团队、Leland设备制造／商业发行的分工背景及反派Mordroc。补充材料不是新的正式开发署名，不推定完整程序开发归属。

这些材料记录在`data/work-notes.json`，首页与专题共用，由数据校验器检查外键、来源和锚点格式。核心games、内容／实体迁移基线和正式职责保持。主库仍为1274部／1487个内容版本／2487条平台发行，专题仍81个。

## 逐项来源与证据边界

- [MAME Leland驱动](https://github.com/mamedev/mame/blob/master/src/mame/cinematronics/leland.cpp)：识别Viper、Track-Pak、既有体育项目、Asylum原型与Up Your Alley前身署名；MAME标年不是精确商业首发日。John Elway与All American Football的旧馆藏异年仍在行内保留。
- [1987-12-15 Game Machine原刊](https://onitama.tv/gamemachine/pdf/19871215p.pdf)：Technos把Super Dodge Ball北美营销权授予Leland。1987日本原作与1988北美清单时间分开。
- [Asylum历史条目](https://www.arcade-history.com/?id=137&n=asylum&page=detail)：1991未发行原型；不能将原型年份当正式首发。
- [Space Ace档案](https://www.dragons-lair-project.com/games/pages/sa.asp)：原作1984、1991套件、斜向输入与取消难度选择。
- [Dragon’s Lair II档案](https://www.dragons-lair-project.com/games/pages/dl2.asp)：动画制作、Leland设备制造及Mordroc故事背景；与旧传单发行证据并列。
- 家用机与改作采用逐行链接：[The Baja](https://www.mobygames.com/game/47253/super-off-road-the-baja/)、[Double Dragon V SNES](https://www.mobygames.com/game/7088/double-dragon-v-the-shadow-falls/releases/snes/)、[Troy Aikman](https://snescentral.com/article.php?id=0729)、[Kyle Petty](https://www.mobygames.com/game/39265/kyle-pettys-no-fear-racing/)、[Fun ’N Games 3DO发行](https://www.mobygames.com/game/43880/fun-n-games/releases/)。部分MobyGames正文直读403，但搜索索引可读；未将其表述为完成原厂说明书逐页复验。
- 后继范围按逐平台资料：[DOOM PS](https://www.mobygames.com/game/30997/doom/releases/playstation/)、[Final DOOM PS](https://www.mobygames.com/game/30998/final-doom/releases/)、[MK Trilogy N64职员表](https://www.mobygames.com/game/2036/mortal-kombat-trilogy/credits/n64/)、[Cruis’n USA N64职员表](https://www.mobygames.com/game/3587/cruisn-usa/credits/n64/)、[Robotron X](https://www.mobygames.com/game/13604/robotron-x/releases/)。

待核：Aaaargh!的具体合作工种；Brute Force的1990／1991异文；MK3 Windows团队范围；Robotron X协作工种；3DO Fun ’N Games的逐项增量与作品身份。清单给出的关联线索在这些行保留为待核，不转成正式开发职责。1994收购后的团队连续性只在历史范围说明，未新增无法独证的法人更名／持股关系。

## 发布前校验

数据、实体关系校验通过；Leland专项4项通过；Node全量222项通过。Python全量303项中255项通过，48项因远程缺少历史快照提交／提交内文件而报错；在未修改的e05836e远程基线复测，48项错误签名完全一致。GitHub API亦确认例如37a7d920历史对象不存在。保留历史断言，只让旧批次针对app.mjs的“不变”断言读取其当时固定快照；不改作品或迁移基线。所有生成器一致性及差异空白检查通过。

## 实际发布断点

本轮部分Git blob对象创建成功且与本地哈希一致；随后上传`data/gameplay-catalogues.json`被自动审批拒绝，理由是没有确认本轮完整清单扩充向公开仓库发布的明确授权。按要求停止后续远程写入，未创建本次远程分支／提交／PR，未合并main，未触发本次Pages发布。经个人上下文核对，先前的授权涵盖已发布旧批，本轮完整清单扩充需要用户明确授权。不得把已写入的未引用文件对象记为网站已更新。

本地分支`codex/leland-catalogue-completion-20261027`保存全部变更。取得此次完整清单扩充的公开发布授权后，先复核远程main，再继续上传余下对象、创建分支提交与PR、合并并核查Pages；不要重复收录已完成数据。浏览器本地预览因远程浏览器无法访问工作区localhost而不可用；本地Playwright未能下载浏览器，故未宣称完成可视化验收。发布后仍须核查线上页面与主库两部作品的补充说明。

## 本轮继续后的检查点

用户要求继续后，先复核远程main，发现PR #144已合并，main推进至`8c16099af18e77b618f747223952d4e140e67b8f`。已将本地Leland更新rebase到该提交；检索索引冲突通过现行生成器重建解决，保留CoreMoreco身份审核及637条组织验证展示。主库、正式职责、组织数据、组织证据台账与迁移基线均与最新main逐字节一致；仅Leland专题范围和补充说明按本次范围变化。

数据／实体校验与全部生成一致性通过；Node225项通过。Python全量执行304项，48项仍缺历史提交对象；另1项旧组织批次的“目录不变”断言与本次合法扩充冲突，已将其固定在该批发布快照，并新增当前组织结果完整保留的回归检查。修复后组织专项1项、Leland专项5项通过，未删除或放宽历史证据断言。

本次完整清单扩充的公开发布自动审批限制仍未解除；未再次尝试被拒的上传，未创建本次远程提交／PR，未合并或上线。下一步需用户明确授权本次33条Leland参考项目与g044、g045补充上传至公开仓库wt1234-donkey/visual-novel、合并main并发布Pages；取得授权后仍先复核远程状态。

## 本次公开发布已获授权

用户已明确授权：“授权将本次更新上传至公开仓库 wt1234-donkey/visual-novel，合并 main 并发布 Pages”。据此继续此次33条参考清单、g044／g045补充与配套页面更新的公开发布。发布前再次fetch确认main仍为8c16099，工作区干净，没有待合并PR，已校验内容无需重做。此前自动审批阻断的上传事项现按此次明确授权恢复。最终合并及Pages结果以GitHub实际响应为准。
