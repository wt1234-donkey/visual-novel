# A—Z 创作登记 B3：BPS—Byakuya Shobo（2026-10-23）

B 字母已核查 10／10，A—Z 累计 42／42；下一家 Cabbage Soft（きゃべつそふと）。本批核对四个主体的档案、作品原始发行署名及来源，仅以单独证据记录订正两个主体身份；没有新增作品开发职责。

| 主体 | 分类 | 已核证据与缺口 | 最小修正 |
| --- | --- | --- | --- |
| BPS | 公司身份可直接确认；创作职责需补来源 | [Tetris官方创办人简介](https://tetris.com/corporate-bios)称Bullet-Proof Software为Henk Rogers的首家游戏发行公司，发行《The Black Onyx》；[Rogers本人的回顾](https://www.sramanamitra.com/2009/09/17/the-story-of-tetris-henk-rogers-part-2/)说他撰写《Fire Crystal》。专题中的 `ascii-black-onyx-v1`、`ascii-fire-crystal-v1` 仍署BPS发行；需要首版制作名单确认公司层开发。 | 在独立JSON记录 `entity-name-cb3c445f13f2` 的 `unknown`→`company`；两条发行原文及专题位置不动，不建立未经核证的Blue Planet Software继承关系。 |
| BROCCOLI | 既有公司身份可直接确认；后发开发需补来源 | [英日公司概要](https://broccoli.co.jp/company/profile/index_en.php)确认株式会社ブロッコリー。`g818-v2`、`g825-v2/v3/v4` 的BROCCOLI发行与GAINAX原版及后续CyberFront版分开；需后发版职员表明确移植、开发或制作分工。 | 沿用已核身份与四条平台发行，不追加游戏创作或集团关系。 |
| Brøderbund | 公司身份可直接确认；逐作开发需补来源 | [《Prince of Persia》作者本人](https://www.jordanmechner.com/en/games-movies/prince-of-persia/)明确1989年Apple II版由Brøderbund发行，[其档案](https://www.jordanmechner.com/downloads/archive/whoswho.pdf)记Broderbund Software的共同创办人；[Cyan支持页](https://cyan.com/company/support/)确认旧《Myst》实体版由Brøderbund发行，[Cyan介绍](https://cyan.com/company/about-cyan/)记本社作品沿革。两部原版的Brøderbund开发仍缺同期名单。 | 单独记录 `entity-name-e0c32a99a906` 的 `unknown`→`company`；`riverhill-prince-v-original`、`g1060-v1` 的发行与创作分开。 |
| Byakuya Shobo（白夜書房） | 暂不宜判断此条历史署名的主体映射 | [公司官网](https://www.byakuya-shobo.co.jp/company/cc10339.html)确认株式会社白夜書房；[旧目录](https://alicecottage1989.blog.jp/archives/20634266.html)对应 `g542-v6` 的原文仍为“白夜書房（档案记作白夜書店）”。需要该版封面、版权页或同期目录查明“白夜書店”指向，才能确认与该公司同一历史发行主体。 | 保留 `entity-name-8b16f2bf500e` 的 `unknown`／`unresolved`、发行原文与实体ID；不把出版物发行当成游戏开发。 |

本批修改独立审核JSON和本文、`scripts/build_entity_model.py`、`scripts/build_organizations.py` 及派生主体／组织数据。`games.json`、专题原文、实体关系、作品／内容／发行ID和迁移基线不变。下一轮从C字母的Cabbage Soft开始。
