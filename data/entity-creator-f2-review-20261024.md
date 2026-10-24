# A—Z 创作登记 F2：Firebird—FuRyu（フリュー）（2026-10-24）

依组织与沿革左侧顺序核 F 字母第 6—11 项。F 累计 11／11，A—Z 累计 94／94；下一家 G-MODE。身份核定不等于把相应发行作品计作开发。事实订正在独立 [审核记录](entity-creator-f2-review-20261024.json)，保留迁移基线、旧发行原文和既有身份关系。

| 主体 | 分类、原始署名与证据缺口 | 最小修正及文件 |
| --- | --- | --- |
| Firebird | **可直接确认品牌身份，开发职责不成立**。[Play It Again 的 Firebird 档案](https://ourdigitalheritage.org/hostedArchives/playitagain/companies/firebird/index.html)称它为 Telecomsoft 创立的发行 label；[《Samurai Warrior》作品资料](https://ourdigitalheritage.org/hostedArchives/playitagain/games/samurai-warrior-the-battles-of-usagi-yojimbo/index.html)分别列 Firebird 发行与 Beam Software 开发。原 `melbournehouse-usagi-v1` 署名 Firebird；具体经营时段仍需合同或当期目录。 | `entity-name-9dbcd9638453` 单独改为 `brand/sourceReviewed`；保留原 `publisher` 行，不添制作、不新建未经审查的母子关系。记录于本批 JSON，生成 `data/entities.json`、组织页和企业页。 |
| Fox Interactive | **公司身份可直接确认；库内发行版本需要补充来源**。[News Corporation 的 SEC 子公司表](https://www.sec.gov/Archives/edgar/data/1308161/000119312507187791/dex21.htm)列 Fox Interactive, Inc.，但 `koei-croc2-v1` 的 `Fox Interactive` 原始发行行所引[光荣日版产品页](https://www.gamecity.ne.jp/products/products/ee/Rlcroc.htm)不能据以确认该日版 Fox 发行。需日版封底、手册或同期地区发行列表核定发行方及区域。 | `entity-name-00dfc4724ca6` 单独订正 `company/sourceReviewed`；旧发行行暂留并登记错配候选，待具名版本证据再另立事实订正；不添开发。 |
| Frontwing | **既有共同制作可直接确认**。[ANIPLEX.EXE 的《ATRI》公告](https://aniplex-exe.com/news/?category=atri-mdm&id=52873)署制作“フロントウイング×枕”；现有 `g200` 的 `coDeveloper` 已对应。其他作品及法人分工需逐作原始片尾。 | `entity-frontwing`、现有共同制作和品牌身份不改；审核记录标记已核，零新增职责。 |
| Fruitbat Factory | **公司身份可直接确认；原作开发不成立**。[该公司同期新闻稿](https://blog.fruitbatfactory.com/tag/press-release/)自称 Fruitbat Factory, Ltd.；[《野良与皇女与流浪猫之心》](https://store.steampowered.com/app/1010600/)及[续作](https://store.steampowered.com/app/1128260/) Steam 页在 2019 英文版列 TOKYOTOON 开发、TOKYOTOON 与 Fruitbat Factory 发行。原始 `g900-v9`、`g901-v8` 是联合发行署名；具体本地化工序需该两版片尾或官方通告。 | `entity-name-b5c18c410b18` 单独订正 `company/sourceReviewed`，两条发行行照旧，不添原作开发、本地化或移植开发。 |
| FuRyu | **公司身份可直接确认；原版创作需区分**。[FURYU 公司概况](https://www.furyu.jp/english/company/profile.html)列视频游戏业务；[3DS《ファタモルガーナの館》官方访谈](https://www.cs.furyu.jp/kataruhito/fatamorgana/)涉及后发版。原始 `g192-v7` 的 `FuRyu` 为发行署名；3DS 实际移植制作团队和 Novectacle 原作的工序需另核。 | `entity-name-60381c8a73f3` 独立订正 `company/sourceReviewed`，保留 `publisher`；不倒填原作制作。 |
| FuRyu（フリュー） | **公司身份可直接确认；与另一目录身份暂不合并**。[フリュー株式会社的 2014 年产品公告](https://www.furyu.jp/news/2014/10/yuukiyuuna-cs.html)署其发行《結城友奈は勇者である 樹海の記憶》，[英文公司概况](https://www.furyu.jp/english/company/profile.html)对应 FURYU Corporation。原始 `hawkeye-jukai-v-original` 署名 `フリュー`；作品实际开发职员需片尾。目录产生 FuRyu 与 FuRyu（フリュー）两个既有 ID，虽有同一法人名称线索，去重会改变旧身份绑定。 | 仅 `entity-name-27ad495eb1bc` 订正 `company/sourceReviewed`；两个 ID、发行原文、组织关系均保留，去重另列迁移审计，不添制作。 |

本批五项独立身份订正、零条创作职责追加。`data/games.json`、`data/credits.json`、迁移基线及既有主体关系保持原样；Fox 对应的地区版发行疑点不以身份订正覆盖历史记录。
