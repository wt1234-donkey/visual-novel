# A—Z 创作登记 I1：IBM—Imageepoch（2026-10-24）

沿组织与沿革的英文字母顺序核 I 组前 3／13 家；A—H 既有 119 项，加本批为 122／132；下一家 iMel。逐条对照主体、专题、原始发行、原版产品页及版本来源。审核数据见 [I1 结构化记录](entity-creator-i1-review-20261024.json)。

| 主体 | 判断、证据缺口 | 最小修正及文件 |
| --- | --- | --- |
| IBM | **已可确认发行，创作职责仍需补源。** [《Zyll》原版手册](https://mocagh.org/miscgame/zyll-manual.pdf)写 IBM 版权和出版，不列具体开发方。[IBM PCjr《King’s Quest》手册](https://www.sierragamers.com/wp-content/uploads/2019/12/Kings_Quest_1_Manual_1_IBM_Version.pdf)支持该版发行，不能替代 Sierra 原作署名。[《Peter and the Wolf》当年包装文案转录](https://elisoftware.org/wiki/Peter_And_The_Wolf_(PC,_CD-ROM)_IBM_-_1995_USA,_Canada_Release)则明列 Seventh Level 制作动画。Hyperman 的多方开发目录互异，需原版片尾核分工。`g089`、`g1198`、`g1199`、`ibm-yellow-brick-road` 四条关联还缺 IBM 对应版本／合辑的原始出版物；IBM PC 机种名不构成公司开发。 | `data/entity-creator-i1-review-20261024.{json,md}`记核查和缺口；保留 `data/credits.json` 中七条具体发行及四条专题“职责待核”，不增加 IBM 创作记录。 |
| IDEA FACTORY | **法人身份可直接确认。** [官网公司资料](https://www.ideaf.co.jp/company/)给出アイディアファクトリー株式会社与 IDEA FACTORY Co., Ltd.，成立于 1994 年。[《アンジェリーク 魔恋の六騎士》官方页](https://www.otomate-p.jp/game/game-96/)及[《ネオ アンジェリーク 天使の涙》官方资料](https://www.otomate.jp/neoangelique/info/)保留两方版权，但不列具体开发分工。需原版职员表、片尾或开发访谈确认 IDEA FACTORY、Otomate 与光荣特库摩的各自职责。 | 将既有 `entity-name-382a9f6ab2ee` 由 `unknown` 订正为 `company`，保留稳定 ID、原发行、已有版权及主体关系；不新增两作创作。规则在 `scripts/build_entity_model.py` 引用独立审核，输出 `data/entities.json` 等派生文件。 |
| Imageepoch | **法人及《ソニプロ》的製作可直接确认。** [当事方版权条款](https://www.jrpg.jp/policy.html)明列株式会社イメージエポック；[官方《ソニプロ》产品页](https://www.jrpg.jp/game/detail/tid43)分列“製作／イメージエポック、開発／タムソフト”。[《闘神都市》3DS版产品页](https://www.jrpg.jp/game/detail/tid41)明确由 Imageepoch 制作和开发，但这是 1994 年作品的后发改编版本，不能补作原作开发；版本层重制开发的细分展示需另外设计和核对片尾。 | 将旧发行身份 `entity-name-b72187fd26e6` 独立订正为 `company`；仅对专题关联 `nitroplus-extra-sonipro` 加一条 Imageepoch `originalProduction`，保留 Tamsoft 开发、原发行及关联位置。`alicesoft-extra-toushin2-v3` 的后发开发只记审计，不向原作追加制作。 |

本批修改独立审核记录与生成规则、实体和职责派生索引、组织与沿革页面。`data/games.json`、`data/company-coverage.json`、历史发行、原有关系与迁移基线不改；审查记录的 `baseCommit` 为 `42057ac4da3071bb444cdce55519c8b4be2a00de`。
