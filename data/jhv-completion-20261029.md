# Japan Home Video清单对照与内容补录

日期：2026-10-29（北京时间）。仅维护 wt1234-donkey/visual-novel。
基线：c91cb9841d664813130616598cf4e43e0992679e。
工作分支：catalogue/jhv-content-completion-20261029。

## 实际增量与清单边界

项目“列出Leland的游戏及游戏类型清单”的个人上下文检索恢复了九个作品名及类型摘要：卒業、Desert Dragoon、侍魂、Star Cruiser II、卒業II、Atlantia、URM、Aggregare、卒業 Crossworld。九项已有五部主库、四部关联身份。本次复用全部九项，**新增独立作品0部、新增平台发行0条**；不是将九项重新插入数据库。检索未提供原表逐字全文，不能宣称已取得原始完整表格或穷尽厂商历史目录。

此前仅确认作品已存在，未补齐其中若干内容身份。本轮新增主库内容2项、关联内容1项，复用六条已有发行；主库仍1328部作品，内容1544→1546，发行仍2544条。JHV正文仍九张卡，内容12→15项；五部主库的25条、四部关联的8条历史发行全部保留原ID。所有非JHV专题配置、主体身份、职责和两份迁移基线保持。

|作品／旧身份|本次处理|证据与限制|
|---|---|---|
|卒業／g830|新增g830-c-final，复用1994年3DO g830-v6|[实机评测](https://lunchbox360.livedoor.biz/archives/10550095.html)展示全动画片头；与先行PC Engine内容g830-c-3比较。只据新增片头，不把色数、界面或旧歌曲当新内容。|
|卒業II／g831|新增g831-c-special，复用1995年3DO g831-v6|[版本资料与用户评述](https://www.gavas.jp/products/detail.php?product_id=3599)称新增原创片头及结局图像；[另一份版本比较](https://asobigokoro.work/graduation-ii-neo-generation-pc-fx-released-in-1994/)亦列相应增量。两者均非同期官方公告，不声称已核完整事件表；仅登记明确的影像增量。|
|Star Cruiser II／jhv-star2|新增jhv-star2-c-cd，复用1994年v2、v3，共享一个内容|[实物收藏目录](https://retroblues.sakura.ne.jp/regeokiba/jhv/jhv.htm)说明部分CG重绘及CD-DA音乐；同一PC-9821／FMT兼用光盘，不按平台重复内容。MAME的4月与收藏目录8月26日冲突保留，只采用共同年份。|
|2004卒業復刻版／g830-v9、g831-v9|两条旧发行分别关联各自原作，contentRelation=same|[IRI-CT当事公告第1页](https://www.iid.co.jp/legacy/news/press/pdf/2004/040511.pdf)明确两作PC-98版原样再现；合集、附属设定集不新增作品／内容。公告只预告7月下旬，不据其确定7月23日。|
|Desert Dragoon／jhv-desert|复用|策略关联已存在，无确证新故事内容，不重复登记模拟复刻。|
|侍魂／jhv-samurai|复用历史例外|原SNK作品与JHV后发FMT署名分开，不扩录普通移植。|
|Atlantia／g832、URM／g833、Crossworld／g834、Aggregare／jhv-aggregare|复用|没有取得符合准入且尚缺的独立作品证据；URM年代异文不拆作。|

## 历史订正、去重与职责

`jhv-content-review-20261029.json`逐条保存六条发行的旧／新内容字段、原完整对象SHA-256、来源和理由。仅允许contentVersionId、contentRelation、contentNote三个字段改变；保留原年、平台、publisher、publisherCompanies、source、differences与releaseRole。生成器检查原迁移哈希时仅逆向还原这六条具名审核字段，不重算基线，也不放宽其他作品；任何额外署名或年份改写均报错。新增内容指向原有首批发行，不复制一个“新发行”来绕过历史对象核对。

3DO仍署SharRock／北部通信工業；2004合集仍署IRI-CT，不因JHV原作关系或版权行改成JHV发行。CD版1993 Arsys原始发行不受1994 JHV版影响。FINAL／SPECIAL是已有作品内容；2004盘内两作分别归并，不制造第三部合集游戏。所有旧作品名、别名和卡片锚点保持。

主库与JHV以及同样引用g830／g831的Hokubu、NEC Avenue、NEC HE、TAKERU页面一起重建。增加五条主库来源说明；历史“无新增”审计保留日期语境，不覆盖旧结论。

## 未完成事项与下一次位置

1. Sensual Angels：MAME PC-98 CD及FMT目录只有年、平台与JHV署名；未找到足够叙事／操作证据，继续待核，不能编造成已收录作品。下一次优先寻找原包装、说明书或实机流程。
2. 餓狼伝説SPECIAL FMT：历史检索给出1996年JHV补充线索，零售目录亦有JHV归档；SNK官网的移植表未列FMT。仅列玩法参考并注明需原包装确认职责。纯竞技不按既有侍魂例外扩大正文，未新增游戏、内容或发行。
3. 卒業R／III／M／Vacation／Marriage／Next等：其他发行公司和IP版权不能自动归属JHV，具体版本逐项另核。
4. FINAL“毕业旅行”说法与[版本核查页](https://w.atwiki.jp/gcmatome/pages/1718.html)的质疑相冲突，本轮不采用该增量。SPECIAL完整事件表、PC-FX等版动画与先行版逐镜头差异仍待原件核查，不能把所有移植一律标新增。
5. URM精确年代、Beluga工种与Atlantia原作职员表继续沿上次记录，不因本轮增补关闭。

## 验证与发布记录

数据和实体校验已通过，CSV、实体／专题生成器同步；新增回归覆盖六条字段审核、拒绝改写publisher／年份、同盘两作去重、CD跨平台共享内容、旧对象和基线保持及页面可见性。PR171的历史精确增量断言固定到其已发布提交，本轮当前数据由独立JHV回归验证。

验证结果：Python 375项（333通过、42项既有历史策略跳过）；Node 242项全部通过。`validate_data.py`、`validate_entity_model.py`、三个规定生成器的`--check`以及`git diff --check`全部通过。实体337、职责5239、专题93、位置2297、身份待核35、专题职责待核623，均与基线一致。

本文件与数据一起提交；PR链接、远程提交、合并及Pages最终结果追加在本分支PR正文中，避免把未完成发布提前写成成功。当前工具不能指定或核实GPT-6 Sol high／GPT-6.1 Sol high配置，使用可用运行配置继续，未声称切换。
