# A—Z 创作登记 W1：WFS—WRIGHT FLYER STUDIOS（2026-10-26）

承接V1，依既有排序连续核查五项并完成W组5／5。A—W队列累计307／307，下一项Xbox Game Studios。核查结果按原发行、品牌、公司与具体开发目标区分；已登记不代表所有人员、历史关系和版本内容均已查清。

## WFS（WRIGHT FLYER STUDIOS）

[WFS更名公告](https://www.wfs.games/news/20181001_01.html)明确株式会社Wright Flyer Studios在2018年10月1日更名株式会社WFS；[2021品牌公告](https://www.wfs.games/news/20210830_01.html)与[2022首发说明](https://www.wfs.games/news/20220210_01.html)同时区分公司WFS和旗下游戏品牌Wright Flyer Studios。旧复合发行名用WFS历史公司主体核为`company`，但原始括号及两条移动平台publisher不变，与独立的品牌节点不合并。原法人名称是历史名，品牌仍在后续使用，不以共享字样新增任意时期的集团关系或公司开发职责。

## Whale（ホエール）

保留既有`brand/existingDossier`，以及g1263《我的女友不是人》的`publishingBrand`、`originalPublishingBrand`。既有[导览来源](https://www.mirai-soft.net/guide.php)本批直读返回502，不能据此补逐作制作。Minato Soft和Hawk Eye两处旧专题关联仍为`pendingRole`，不从同系品牌或发行自动转为制作。

## WhisperGames

[自家网站](https://www.whisperinteractive.com/)以WhisperGames提供游戏发行及本地化服务；[展会具名参展公司](https://www.gamescom.global/en/exhibitor/whisper-interactive)为Whisper Interactive (Xiamen) Co., Ltd.，与面对消费者的WhisperGames名义区分。[《Seventh Lair》Steam页](https://store.steampowered.com/app/1909810/Seventh_Lair/)只列它为共同Publisher，NOVECT为Developer。因此发行名义核为`brand`并显式保留原publisher，不以一般服务介绍推该作的开发或翻译，也不在没有注册原件时填法人设立日期。展会页直读只见标题，法律名称取检索可读摘要，此限制已记入待核。

## Wolf Team

游戏保存协会[1988《Arcus》具体馆藏](https://www.gamepres.org/catalog/?cat=1&id=8811003934009&nav=brand)将品牌Wolf Team与発売元株式会社ウルフチーム分别列示；[1990《あーくしゅ》馆藏](https://www.gamepres.org/catalog/?id=8811000812003)亦如此。其历史发行节点核为`company`，保留g085《Road Blaster》1992 Mega-CD发行；1985街机原作仍属Data East，不能由1992公司发行反推原作开发。[1992发行目录](https://www.gavas.jp/products/detail.php?product_id=5814)只能支持已有发行资料，具体移植开发另核。

## WRIGHT FLYER STUDIOS

按WFS[品牌公告](https://www.wfs.games/news/20210830_01.html)核为`brand`，原Steam发行的publisher不变。《绯染天空》[第一方官网](https://heaven-burns-red.com/)明确“企画・制作 WRIGHT FLYER STUDIOS × Key”，只给既有相关作品`key-rpg-hbr`追加一条`productionBrand`，Key原有`coDeveloper`保持。[Steam页](https://store.steampowered.com/app/1973710/)另明确2022 PC版Developer同一品牌，只对`key-rpg-hbr-v3`追加发行层`developer`。该PC发行仍是`contentRelation: unverified`、`contentVersionId: null`，不从开发字段推定和移动版同内容，也不补普通移植行。

## 应用与保护

WFS、Wolf Team订正为公司，WhisperGames和WRIGHT FLYER STUDIOS订正为品牌；Whale原身份不变。326个实体、名称、ID、日期、关系与80专题维持；身份待核44降至40。仅追加上述两条限定职责：5009→5011；2234条专题引用及601项`pendingRole`逐条保持。原1274部主库作品、1487内容版本、2487平台发行、2175位置及全部原publisher对象保持，Key专题的HBR合作组不自动改组。

V1精确差异测试固定在已发布树`7fd9b99d705fcbd62e47bdc5fb02b8fc4e419208`；本批另核四项身份、两条限定职责、原对象与V→W顺序。独立资料见[JSON核查记录](entity-creator-w1-review-20261026.json)。

## 验证

276项Python、222项Node测试通过；数据及实体校验、四项生成器`--check`和`git diff --check`通过。部署另以GitHub Actions确认。
