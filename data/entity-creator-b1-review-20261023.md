# A—Z 创作登记 B1：Bandai Namco Games—Banpresto（2026-10-23）

按英文名连续核查 B 字母前 3／10 个主体；A 字母 32／32 保持完成。下一家为 BLACKRAINBOW。逐项对照现有主体档案、`credits.json`、Banpresto 专题及原发行来源；本批只订正一项历史公司身份，不新增作品层创作职责。

| 主体 | 分类 | 可确认事实与证据缺口 | 最小修正／文件 |
| --- | --- | --- | --- |
| Bandai Namco Games | 可直接确认身份；需要补充逐作来源 | [官方2015年更名公告](https://www.bandainamcoent.co.jp/corporate/150401/)证明既有公司身份，[公司沿革](https://www.bandainamcoent.co.jp/corporate/history/)说明游戏业务；g1075—g1079及《魔法少女小圆 携带版》现有10条是原始发行署名，不是创作职员表。需逐作官方制作名单或初版片尾确定原作制作／开发分工。 | `entity-creator-b1-review-20261023.json`登记核查；`entities.json`现有公司身份与`credits.json`发行记录不变；组织页显示零项已确认创作。 |
| Bandai Visual（バンダイビジュアル） | 可直接确认历史公司；需要补充版本制作来源 | [集团历史](https://www.bandainamco.co.jp/about/history/corporate.html)记载バンダイビジュアル公司，[2018年集团组织公告](https://www.bandainamco.co.jp/cgi-bin/releases/index.cgi/file/view/6083?entry_id=5501)确认商号变化。g830《卒業》现有两条バンダイビジュアル署名对应后发平台，不是1992原作开发。尚需Mac／WonderSwan版本原始职员表。 | 独立JSON记录旧`unknown`→`company`，由`build_entity_model.py`生成`entities.json`与索引；保留ID、日文原署名、发行职责、作品身份、关系和迁移基线。 |
| Banpresto | 暂不宜统一判断身份；需要补充逐作来源 | [集团2008年业务移管沿革](https://www.bandainamco.co.jp/about/history/corporate.html)与[原有集团公告](https://www.bandainamco.co.jp/releases/images/3/42276.pdf)区分旧游戏业务、新设景品公司。现有专题21条横跨旧发行和品牌延续，原始发行16部作品与后续5部语境不同。需每项包装／片尾与时期法人证据，不能把2008年前后不同主体合并成一家公司或由业务承接推出开发。 | `banpresto.html`专题和`company-coverage.json`继续保留历史分组，`entity-banpresto`身份待核，`credits.json`及`dossierMemberships`不动；证据缺口写入本独立审核记录。 |

不修改主库、内容版本、平台发行和旧专题链接。现有 `publisher` 原文及旧发行索引全部保留；组织关系、开发职责和发行身份各自独立，未核角色继续待核。页面进度新增 B 字母 3／10，同时保留 A—Z 累计 35 项和前六批证据链接。下一批从 BLACKRAINBOW 顺序继续。
