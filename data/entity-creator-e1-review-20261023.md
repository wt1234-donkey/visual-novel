# A—Z 创作登记 E1：E3 Staff—El Dia（2026-10-23）

按组织与沿革左侧英文排序核查 E 字母第 1—4 项，E 累计 4／13，A—Z 累计 74 个已核主体；下一家 Electronic Arts。已核主体数不代表该主体有已证实的创作作品。

| 主体 | 分类、来源及证据缺口 | 最小修正与文件 |
| --- | --- | --- |
| E3 Staff（イースリースタッフ） | **销售可直接确认，身份需补充来源**：[《卒業 Crossworld》PS 原版片尾转录](https://raido.moe/staff/ps1/ps1_sotsugyo_crossworld.html)把“企画製作”列为 M2／SOFIX，把“販売”列为イースリースタッフ。片尾未说明它是法人还是品牌，亦不能凭销售署名判断其他作品创作。需同期包装背面、法人登记、公司广告及其他游戏片尾。 | `data/entity-creator-e1-review-20261023.json` 记录待核；`data/entities.json` 继续 unknown/unresolved；`data/credits.json` 保留 `g834-v1` 原发行，不增加开发。 |
| Edia | **公司身份可直接确认，作品制作需补来源**：[公司概要](https://edia.co.jp/company/overview/)确认法人；[公司 2016 年新闻](https://edia.co.jp/news/pressrelease/2016/10/06/6081/)说明《蒼の彼方のフォーリズム-ETERNAL SKY-》是另作卡牌游戏，含本作独有剧情，由本社上线运营。新闻不能确定各项开发人员，也不能将它当成原版《苍彼》或直接提升至主库。需该作原版片尾及剧情主次核查。 | 身份和 `sprite-eternal-sky-v1/v2` 两条发行不变；保持专题关联位置，暂不增加创作职责或主库作品。 |
| EISYS（株式会社エイシス） | **公司身份可直接确认，制作职责需补来源**：[公司官网](https://www.eisys.co.jp/company/information)列法人与英文名；[Nitroplus《沙耶之歌》Android 官方页](https://www.nitroplus.co.jp/game/saya/)仅标 2015 年 Android 版“販売 株式会社エイシス”，并说明它是 2003 年 PC 原作的移植。需移植开发片尾才能登记移植职责。 | 在独立审核 JSON 订正 `entity-name-84c36fc1f1e1` 为 company/sourceReviewed；生成 `data/entities.json`，`g163-v3` 发行不变，原作制作不归 EISYS。 |
| El Dia | **品牌身份可直接确认，历史原作不宜归入**：[RED FLAGSHIP 负责人同期访谈](https://www.famitsu.com/news/201612/16123008.html)明确 El Dia 是其品牌；[品牌《慟哭 そして…》复刻页](https://el-dia.net/doukoku/)对应后发版。尚需复刻版片尾确定各项制作职责；若要画经营关系，需先建立 RED FLAGSHIP 独立档案及时间依据。 | 独立订正 `entity-name-a0fea5d6d6c9` 为 brand/sourceReviewed，设置 `preserveReleaseRoles` 保留 `g1160` 两条原发行职责；不自动生成原作发行品牌或 1998 年原作制作职责，也不修改 Data East 的历史署名。 |

生成文件 `data/entities.json`、`data/entity-migration-review.json` 和页面索引只反映上述两项身份订正与登记进度。`data/games.json`、`data/company-coverage.json`、`data/credits.json`、既有关系与迁移基线保持原事实；后续若核实作品制作，须再另立证据记录。
