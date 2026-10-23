# A—Z 创作登记 E2：Electronic Arts—Enix（2026-10-24）

按组织与沿革左侧英文排序核 E 字母第 5—8 项，E 累计 8／13，A—Z 累计 78／83 个已核主体；下一家 Enterbrain（エンターブレイン）。已核主体不代表全部关联作品均已证实创作。

| 主体 | 分类、证据与缺口 | 最小修正 |
| --- | --- | --- |
| Electronic Arts | **公司身份可直接确认，作品制作需补来源**：[EA 公司概要](https://www.ea.com/about?s=1713)确认法人；[《Blades of Vengeance》资料](https://www.gamesdatabase.org/game/sega-genesis/blades-of-vengeance.aspx)分列 Beam Software 开发、EA 发行。现有《Mars Saga》《Skullmonkeys》资料不足以把发行署名转为开发，后者还须按地区核其发行法人。需两作原版片尾及包装。 | 独立订正 `entity-name-328b53003a80` 为 company/sourceReviewed；三条 release 发行原文不变，不新增创作。 |
| ELF | **一项制作可直接确认，其余逐作待核**：[《新・御神楽少女探偵団》2003 Windows 原版片尾转录](https://raido.moe/staff/win/win_shin_mikagura_shojo_tanteidan.html)列“企画・プロデュース （株）エルフ”，并列 elf 的背景、CG、音响；另列 SIDO 原作、NUDE MAKER 游戏设计及程序。[《YU-NO》Saturn 版片尾](https://raido.moe/staff/sat/sat_yuno.html)的“製作・著作 elf”只适用该版本，不能单凭它订正 1996 年 PC-98 原作；[《Dragon Knight 4》PC-98 片尾](https://raido.moe/staff/pc98/pc98_dragon_knight_4.html)列人员与版权，还需独立的制作主体证据。其余目录和异平台版本待逐作查原署名。 | 为主库 `g320` 增 `entity-elf` 的一条 `originalProduction`，注记联合分工；既有公司身份、Silky’s 品牌关系、93 条发行和迁移基线不变。 |
| Enix America Corporation | **同期公司及发行署名可直接确认，沿革关系需补来源**：[《King Arthur & the Knights of Justice》原版手册](https://www.videogamemanual.com/snes/King%20Arthur%20%26%20The%20Knights%20of%20Justice%20%28USA%29.pdf)具名 Enix America Corporation；[Square Enix 集团史](https://www.hd.square-enix.com/eng/company/history.html)另记 1999 年设立的 ENIX AMERICA INC.，不能由近似名称认定两者是同一法人、旧名或连续的母子关系。需要同时代法人档案及本作游戏片尾判断具体创作。 | 独立订正 `entity-name-bd6862a41912` 为 company/sourceReviewed；`enix-arthur-v-original` 发行保持，不追加创作或组织关系。 |
| Enix（エニックス） | **一项共同制作可直接确认**：[集团沿革](https://www.hd.square-enix.com/eng/company/history.html)与既有公司身份相符；[《ユーラシアエクスプレス殺人事件》1998 PS 原版片尾转录](https://raido.moe/staff/ps1/ps1_eurasia_express_satsujin.html)明确“製作 ENIX／Foursome”，System Sacom 另有技术团队。其他 Enix 发行作品仍需各自片尾确认。 | 为主库 `g984` 增 `entity-enix` 一条 `originalProduction`，在注记中保留联合制作边界；76 条旧发行和公司沿革不变。 |

独立 JSON 审核记录两项身份事实订正、两项作品级创作追加。生成 `data/entities.json`、`data/credits.json`、`data/organizations.json`、页面索引及审计索引；不修改 `data/games.json`、`data/company-coverage.json`、任何原有 credit 行、既有组织关系和迁移基线。
