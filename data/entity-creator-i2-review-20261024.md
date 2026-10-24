# A—Z 创作登记 I2：iMel—Index Corporation（2026-10-24）

接续 [I1](entity-creator-i1-review-20261024.md)，按左侧顺序核 I 第 4—7 项，I 累计 7／13，A—I 累计 126／132；下一家 Infocom。逐条结论见[结构化 I2 审核](entity-creator-i2-review-20261024.json)。

| 主体 | 判断、证据缺口 | 最小修正及文件 |
| --- | --- | --- |
| iMel | **已有六条后发移植开发可直接沿用。** [当事方实绩](https://imel.co.jp/activity/)把在售项目与具体制作实绩分列；`g200`、`g201`原记录限定主机及移动平台。`g211`、`g213`部分平台亦被官方具名为移植开发，但目前缺逐版本与已收录平台对象的严格映射；`g899`、`g214`、`g216`在售不足以认定逐版开发。其他系统或演出受托项目也不可归作原作开发。 | `data/credits.json`既有 iMel 发行及六条 `portDeveloper` 不重复追加，七个现有作品身份与内容不改。逐发行平台如需补职责，先取得版本片尾／产品页与明确平台映射，再作版本级追加。 |
| Impact Interactive Publishing | **历史公司身份可直接确认。** [1997年《Computer Gaming World》的《DogDay》广告](https://archive.org/stream/Computer_Gaming_World_Issue_158/Computer_Gaming_World_Issue_158_djvu.txt)在版权行明确 `Impact Interactive Publishing Pty Ltd.`，[同期负责人署名信](https://www.justadventure.com/2005/01/01/the-state-of-adventure-gaming-october-1998/)亦用此法人名。广告证明出版／权利，未证明开发；原作制作须核 Eyst 原版包装与片尾。广告的1996版权年也不能单独核定北美首发日。 | 对既有 `entity-name-c73a46096ea7` 单独订正 `unknown`→`company`；旧 `g1014-v1` 的 `publisher`、原作年份及开发待核均保持。审查证据存 JSON，生成器只应用身份订正。 |
| IMYUIC(ALICESOFT) | **组成名义可确认，复合身份暂不宜判断为独立公司或单一品牌。** [2020年AliceSoft公告](https://www.alicesoft.com/information/2020/entry002611.html)称 IMAYUI 创立个人品牌 IMYUIC、AliceSoft 出品。[2022年独立公告](https://www.alicesoft.com/information/2022/entry003001.html)明确已售作品为区别同名独立品牌，改用 `IMYUIC(ALICESOFT)` 名义继续由AliceSoft管辖。原 `alicesoft-extra-hentailabyrinth-v1` 标 2020 首发、复合名义，存在时间语义差；它属于既有发行史实的单独订正，需要原始2020商店页面及2022改名证据一起审查，不能借生成器重写迁移基线。 | 本批保留复合节点 `entity-name-3de89d1ab0a5` 的 `unknown` 和旧发行对象，不把独立后的 IMYUIC、AliceSoft、2022管理署名折为同一创作主体；在审核记录列出下一次事实订正所需来源。 |
| Index Corporation | **2013年旧公司身份可直接确认。** [《Key COLLECTION》同期发布](https://www.gamer.ne.jp/news/201310150044/)于10月15日以 Index Corporation 署名上线和版权。[Sega Sammy 财报](https://www.segasammy.co.jp/ja/archives/ir/ar2014/pdf/FINANCIALS.pdf)说明旧 Index 业务于11月1日让与 Sega Dream，新公司随后也改名 Index，再更名 Atlus。同名不能跨越法人移转直接归并。上线与运营不充分证明具体代码开发，需片尾／当时团队资料。 | 对既有 `entity-name-1b20d2df8464` 单独订正 `unknown`→`company`，限2013年10月旧公司署名；`key-collection-v1/v2` 双平台发行、Key 授权位置及关系均不变，不补开发。 |

本批只变更独立审核、身份订正规则与其派生索引／组织页。`data/games.json`、旧发行、品牌／股权关系及迁移基线保持，2020复合名义疑点已作为后续单独史实订正记录。
