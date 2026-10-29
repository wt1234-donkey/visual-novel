# 厂商补核与后续专题（2026-10-29）

基线：6aca87246df60132412331a11e5e1b617e6d6a6f；目标仅 wt1234-donkey/visual-novel。
工作分支：catalogue/manufacturers-20261029。本记录与数据一起提交；合并、部署的最终状态见该分支 PR 与本次运行结果。

## 来源与完成边界
尝试检索对话“列出Leland的游戏及游戏类型清单”的三家厂商表格两次，仅取得此前专题执行摘要，没有取得完整原始表格。因此本轮依据仓库已发布审计及下列新查来源补核，不能声称已经逐行覆盖原对话完整清单，也不编造缺失表格。
- Chunsoft此前两部街／金八先生以及各增补已在主库，全部复用。
- JHV五部主库与四部关联已存在，作品、内容、发行逐对象不改；本次新增可见类型对照及待核边界，没有独立新作准入确证。
- Ultra此前夜影、NES星际迷航已存在，全部复用，不混入同名电脑与Game Boy版。
- 原始未完成厂商表未能取得；本轮按实际发行参与与专题缺席情况生成新的可复算候选队列，明确不是原表复原。

## 本次增量
|对象|处理|来源|
|---|---|---|
|TRICK×LOGIC Season 1 / g1331|新增主库一作、一原作内容、一PSP首次发行；Chunsoft专题12部引用|https://www.4gamer.net/games/105/G010573/20100722025/|
|第一季推理系统及内容边界|关键词选择组合与调书解答不当文字输入；含案件1—4和5的推理预告；不凭“推理”贴剧情分支|https://www.4gamer.net/games/105/G010573/20100702069/|
|Snake's Revenge / ultra-snakes-revenge|新增潜入动作叙事关联、一原作内容、一NES北美首批发行；不放四类主目录，不与MSX2 Metal Gear 2合并|https://www.retrogames.cz/manualy/NES/Snakes_Revenge_-_NES_-_Manual.pdf|
|JHV|五部主库与四部旧关联全部保留，未新增作品；Sensual Angels及URM继续待核|data/jhv-audit-20261027.md|
|CAPCOM|新专题，复用g049/g172/g173/g182及既有法人entity-name-7554e19bb041；不新增同名实体或游戏副本|https://www.capcom.co.jp/ir/company/info.html|

Chunsoft不自动继承SCE发行：新作publisher明确Sony Computer Entertainment。未据目录或发行推定开发职责。
Snake's Revenge原手册已核故事、成员、潜入及横向动作；Ultra发行与Konami开发不自动互推。
CAPCOM官网区分1979-05-30法人设立与1983-06-11创业。专题首批最早作品仍是2001年，不将设立年作为作品导航年。

全库：1328主库作品／1544内容／2544发行；93专题。新增跨类型关联一部，附录不并入主库计数。

## 成功操作与验证
- 建立工作分支；所有旧主库作品、内容、发行逐对象保持，旧关联逐对象保持。
- 重建互动、内容与发行CSV，实体、组织索引、专题和首页导航。
- 数据与实体校验通过；三个规定生成器--check及git diff --check通过。
- Python 367项，325通过、42项按仓库既有历史基线策略跳过；Node 242项通过。
- Chunsoft／Ultra历史页面断言和SEGA确切增量测试固定至对应已发布快照；新增当前回归验证新作、旧对象保持、CAPCOM稳定身份及页面数量，不删除旧历史断言。
- 当前运行工具不提供模型／推理配置切换接口，无法验证已选GPT-6 Sol high或GPT-6.1 Sol high；未声称切换。

## 未完成事项与继续位置
1. 取得原对话三张完整游戏表后逐行补上原始对照；现有类型附录仅为有据子集。
2. Chunsoft：第二季2010年7月起分话下载及9月UMD的案件5解答、6—10话先后与内容依赖须逐话拆核；不将后发整包当原作首发。其次继续移动原作与未覆盖RPG。
3. JHV：Sensual Angels操作／叙事性质；URM年代异文及Beluga工种；Atlantia原作职员表；关联公司关系起止。未知不推为合格新作。
4. Ultra：Mission: Impossible已定位原手册，准入范围尚待逐项比较；Metal Gear NES版本与Konami旧身份复用，普通地区移植不扩录。
5. 新专题后续：CAPCOM首批以外的叙事系列及增补内容；再按data/dossier-queue-20261029.json核对已有发行但缺专题的候选。队列前列为Konami Digital Entertainment、Koei Tecmo Games、VISUAL ARTS、ENTERGRAM、PROTOTYPE；已有集团专题可涵盖者不强制再建，不据候选队列推定成立日或原作开发。
6. 本文写入时发布尚待进行；最终PR、合并提交及Pages状态由本次运行结果报告，不将准备动作写成上线成功。


## 发布回执

- PR：https://github.com/wt1234-donkey/visual-novel/pull/170，已合并。
- 分支数据提交：896b96818f230867a23807a8adeea085d58a90e3。
- main合并提交：3fb3ca3ef0713000cce16f3c60e155782947c6a2。
- 远程Git树996bc3a996ef61e6cbfb97b6a4718c424a8c1059与本地通过验证的树一致；命令行缺登录凭据后使用已连接GitHub账号上传，每文件blob哈希逐一核对一致。
- Pages数据发布：https://github.com/wt1234-donkey/visual-novel/actions/runs/40733101886；build、deploy与report-build-status全部success。
- 站点：https://wt1234-donkey.github.io/visual-novel/；新专题capcom.html。该回执仅补充本轮记录，不修改已上线数据。
- 下次从上方未完成事项第1项（原始完整表格）及第2项（第二季分话与UMD内容关系）继续；不可重复新增g1331、ultra-snakes-revenge或CAPCOM既有四作。


## 2026-10-29 万普后续扩充

按后续用户ADV／RPG授权完成44部新作品（4主库、40共享关联）与九部召唤之夜原身份恢复；万普正文74部、类型表79行。主库1333／1551内容／2549发行。上文为先前批次的当时记录，最新万普明细、验证、未完成及继续位置见[本轮进度](banpresto-completion-20261029.md)，最终发布回执以本轮PR为准。


## 2026-10-29 Brøderbund后续扩充

新增13部身份（6主库、1关联、6输入书目），Riven复用g1001与原作内容，补1997电脑首批；正文19部，类型表33行。主库1339／1557内容／2556发行。详见[本轮进度](broderbund-completion-20261029.md)，最终提交、PR、main及Pages回执以本轮PR正文为准。
