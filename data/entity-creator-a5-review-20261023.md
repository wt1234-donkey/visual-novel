# A—Z 创作登记第五批：ASCII—Atlus（2026-10-23）

## 范围与结论

本批按英文字母顺序核查第 26—30 个 A 主体，累计完成 **30／32** 个，下一家为 **AUGUST**。核查对象为 ASCII、Asmik（アスミック）、Asoberu! BD-GAME（あそべる！BD-GAME）、Atari、Atlus。

本批只新增 3 条创作职责，均为 ASCII 的具名作品；另确认 Asmik、Atari、Atlus 的主体层级。Asoberu! BD-GAME 的官方页面能确认产品／品牌语境，但没有足够可读证据确认运营法人或创作职责，因此继续待核。

## 可直接确认

| 主体 | 作品 | 记录 | 依据与最小修正 |
| --- | --- | --- | --- |
| ASCII | 《阿里昂》／アリオン（g1003） | `originalProduction`，作品层，主库 | [8BITS 产品资料](https://www.8-bits.info/gamelist/PC88/info/info_wANYKNB7WWya78VW.php)同时列出メーカー名与開発元为アスキー。新增一条 ASCII→g1003 原作制作；不把电影原作或后发平台当作新的创作职责。 |
| ASCII | 《冒险者们：贤者的遗言》／冒険者達 賢者の遺言（g1004） | `originalProduction`，作品层，主库 | [8BITS 产品资料](https://www.8-bits.info/gamelist/PC88/info/info_NR8hzxRbmVqpXag5.php)明确メーカー名与開発元均为アスキー。新增一条作品层原作制作；不把作者、移植者或预告续作推给 ASCII。 |
| ASCII | 《混沌天使》／カオスエンジェルズ（ascii-chaos-angels） | `originalProduction`，作品层，专题关联 | [8BITS 产品资料](https://www.8-bits.info/gamelist/PC88/info/info_sEVfQsIiv2Bv01nr.php)明确メーカー名与開発元均为アスキー。新增一条专题关联作品的原作制作；保留 `related` 位置，不转入主库。 |
| Asmik（アスミック） | 历史主体 | `company`，身份已核 | [Asmik Ace 官方沿革](https://www.asmik-ace.co.jp/history/)记载 1985 年株式会社アスミック成立、1998 年与 Ace Pictures 合并；[公司概要](https://www.asmik-ace.co.jp/profile/)列出计算机软件企划、制作、发行等业务。只确认主体身份，保留《深层迷宫IV》为 HummingBird Soft 开发、Asmik 发行。 |
| Atari | 历史主体 | `company`，身份已核 | [Atari 官方关于页](https://atari.com/pages/about)和[历史页](https://atari.com/pages/history)确认其互动娱乐制作公司身份、1972 年创立及 1984 年分裂。只确认公司层，不合并 Atari Melbourne House；《变形金刚：2004版》仍是 Atari 发行、Atari Melbourne House 开发。 |
| Atlus | 历史主体 | `company`，身份已核 | [Atlus 官方历史](https://atlus.co.jp/recruit/about/history/)明确 1986 年以计算机游戏开发公司成立。只订正主体身份；《暗黑弥赛亚／地狱之夜》仍保留 Dennou Eizou Seisakusho 开发、Atlus 发行。 |

## 需要补充来源

| 主体 | 当前状态 | 缺口 | 最小修正方案 |
| --- | --- | --- | --- |
| Asoberu! BD-GAME | `unknown`／发行署名 | [官方产品页](https://bd-game.product.co.jp/product/product10.html)能确认 BDPG 产品品牌，但当前可读信息不足以确认运营法人、与 VISUAL ARTS 的关系或具体制作职责。 | 保留现有 `entity-name-80a218385951`、g163 发行记录和待核状态；取得页面版权页、公司登记、产品封面或发布稿后，再单独订正身份。 |
| ASCII | 仅部分登记 | ASCII 发行署名共 51 条，不能由发行关系推断全部开发。尤其《鄂霍次克消失》资料显示 LOGIN SOFT 开发、ASCII 发行。 | 只保留本批 3 条具名开发证据；后续逐作读取原始说明书、片尾或开发方资料。 |

## 暂不宜判断

- 不把 ASCII 的 51 条历史发行署名批量升级为 `originalProduction` 或 `developer`。
- 不把 Asmik Ace 的现行法人身份自动追溯为所有历史 Asmik 署名的同一法律实体，也不把 Asmik 发行写成 HummingBird Soft 之外的开发。
- 不把 Atari 的品牌、Atari Corporation、Atari Games、Infogrames 及 Atari Melbourne House 合并为一个无时间范围的开发主体。
- 不把 Atlus 的公司历史能力当作《暗黑弥赛亚／地狱之夜》的逐作开发证明；现有作品仍按具体开发方记录。
- 不把 `ascii-chaos-angels` 的专题关联位置改成主库；本批只补参与职责。

## 文件与审计

- 独立证据记录：`data/entity-creator-a5-review-20261023.json`、本文。
- 生成规则：`scripts/build_entity_model.py` 读取本批审核 JSON；`scripts/build_organizations.py` 将 30／32 进度和创作分类写入组织与沿革索引。
- 不修改 `data/games.json`、内容版本、平台发行、既有关系、专题成员、主库首页或迁移基线。
- 3 条新增职责按实体、作品和角色去重：ASCII 公司 3 部，其中 2 部主库、1 部专题关联；不增加作品对象或版本对象。

