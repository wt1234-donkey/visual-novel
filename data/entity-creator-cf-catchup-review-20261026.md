# A—Z 创作登记补漏：C—F 八项（2026-10-26）

承接Y1，重新以当前显示名运行`sortFamilies`并与进度表比较，发现八个实体ID尚未列入`processedEntityIds`，但排在原定下一项5pb.之前。原因是旧批次的名称／排序快照不再覆盖当前显示名。本批依当前顺序补登记Champion Soft、Cocktail Soft、Crest / JAST、dramatic create、FairyTale / X-Shitei、FAIRYTALE ETHIX、FairyTale、Flower-Moon Group。累计登记320项，仍有6项待审，下一项5pb.；登记完成不等于所有职责和历史主体已证实。

## C：Champion Soft、Cocktail Soft、Crest / JAST

[Champion Soft当事公司](https://www.alicesoft.com/outline/contents.html)明确1983年1月设立、3月法人化，1989年成立ALICESOFT品牌；[公司资料](https://www.alicesoft.com/outline/profile.html)确认法定名。既有公司日期`1983-01`、97条平台发行职责与Alicesoft关系保持；1982旧标题的馆藏归档不倒填为尚未设立法人的发行。

[F&C官方《きゃんきゃんバニー》产品页](https://fandc.co.jp/catalog/pc/417)明确カクテルソフト品牌，原69作216条原作／平台发行品牌职责保留，F&C母体及授权发行的不同署名不自动归并。

Crest / JAST主要依[PC-88品牌目录](https://www.gamepres.org/pc88/library/jast.html)和[8BITS作品条目](https://www.8-bits.info/gamelist/PC88/info/info_sEYav8D601zXtfnZ.php)保留复合署名；g680《デリンジャー》的PC-98、MSX2、PC-88三条版本仍有年份和内容对照缺口。既有4条品牌职责保持，尚不由目录将品牌升为法人或推定每版开发。

## D：dramatic create

[HuneX官方沿革](https://www.hunex.co.jp/archives/company/history)明确2014年启动自有dramatic create品牌；[品牌业务页](https://www.hunex.co.jp/archives/service/dramaticcreate)明确它是主机软件销售品牌。本批给品牌节点补`brandActivityStarted/2014/year`一项；16条发行品牌职责和与HuneX的既有关系保持。1992年为HuneX设立，不用作品牌成立年；主机移植开发仍按具体作品核。

## F：四项FairyTale系显示名

[F&C产品目录](https://fandc.co.jp/catalog/pc)按商品分列フェアリーテール、FAIRYTALE/X指定、FAIRYTALE ETHIX、花月組。前者80作242条品牌职责、X指定5作17条、[ETHIX《donor》](https://fandc.co.jp/catalog/pc/683)所在节点2作6条、[花月組《月雀》](https://fandc.co.jp/catalog/pc/633)所在节点4作13条，原有署名和家族关系保持。[《鏡の中のオルゴール》产品页](https://fandc.co.jp/catalog/pc/625)称花月組为新标签。`Flower-Moon Group`仍是编辑译名；《月雀》属于桌上麻雀，不因品牌关系进入叙事主库。资料不足的逐版内容与制作分工继续待核。

## 应用与保护

本批无身份、职责或原始发行变更，仅在dramatic create加一条来源明确的年份。326实体、40待核身份、5011职责、2234专题引用、601项`pendingRole`，80专题及1274主库作品、1487内容版本、2487平台发行、2175位置均保持。详见[JSON核查记录](entity-creator-cf-catchup-review-20261026.json)。

## 验证

合并批次运行`validate_data.py`、`validate_entity_model.py`、288项Python测试、222项Node测试及三个实体生成器和专题页`--check`均通过；本批所加日期与审查顺序另有冻结前后树的针对性测试。公开部署由最终合并记录追踪。
