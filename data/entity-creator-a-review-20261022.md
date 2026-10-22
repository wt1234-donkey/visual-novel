# A—Z 创作记录登记：A 字母首批

核查日期：2026-10-22。基准：`d8f37e90abf47af94e9285167a26b6865497e332`（PR #58）。人工证据规则与完整A字母队列见同名JSON；生成器仅应用其 `identityCorrections` 和 `creditAdditions`，进度、待核结论不产生开发署名。

## 按顺序处理8个主体

按英文基本字母排序，忽略大小写和拉丁重音；âge按Age排列。32个A字母主体中，本批按顺序处理前8个，下一家为Alchemist。这里的“已核查”包含来源不足的结论，不代表该厂商全部创作记录已登记。

| 顺序 | 主体 | 本批结果 | 证据边界／缺口 |
| --- | --- | --- | --- |
| 1 | Accolade | 需要补充来源，未加创作 | 《Star Control 3》原说明书52—53页分列Accolade与Legend，后者具名开发、故事、系统与程序；不能把发行或参与职员直接扩大为本作完整开发。 |
| 2 | Activision | AZ1：新增《佐克：大审判官》原作制作1条；其余继续核对 | GOG授权页Company第一项链接为 `developers=activision`，第二项为发行。对照《重返佐克》的Infocom及《佐克：复仇女神》的Zombie开发项，未把同系列整批上推。两部Santa Fe及跨期法律主体仍需原职员表。 |
| 3 | Addison-Wesley Productions | 需要补充来源，未加创作 | 旧发行原文保留；《阿伦达文城堡的秘密》本轮403，《对抗者》二手职员列出个人作者及地区出版社。缺原书版权页和与历史名义的对应。 |
| 4 | Addison-Wesley Publishing Company | 需要补充来源，未加创作 | 维持5条专题待核及现有发行；书籍作者、Beam开发、地区出版与本主体均不能相互替代。 |
| 5 | Adventure International | 需要补充来源，未加创作 | 保留4条直接发行及36条专题待核；原目录13.5MB超本轮网页提取上限，尚未逐页核对。需区分Scott Adams个人、美国公司、AI UK及移植团队，尤其成立前作品。 |
| 6 | Adventure Soft | AZ2：新增《魔法师西蒙》原作制作1条 | 现行发行方的周年版授权说明明确其为原作开发者，且周年版由MojoTouch制作。只登记1993原作，不增周年版、移植或旧名关系；公司／团队法律身份待核。 |
| 7 | âge | AZ3、AZ4：新增《Muv-Luv》《Muv-Luv Alternative》制作品牌2条 | 官网自身作品目录及两张单作页支持制作品牌目录关联；原作规格页保留2006署名。现行Steam开发栏为aNCHOR，未倒改2003／2006原作身份，也不合并两个实体。品牌／团队的具体身份仍待补证。 |
| 8 | Akatsuki Games | AZ5：新增《怪兽8号 THE GAME》原作制作1条；AZ6：核定公司身份 | 2024原始公告明确公司承担企划、制作、开发、运营，2025首发公告对应同一已收录作品。该作维持关联位置，不给TOHO、母公司或Production I.G自动追加开发。 |

## 原始来源

- Accolade：[原说明书镜像](https://device.report/m/641008c8b769ab2a81e989e882b706f958c324e431158f537892f8a104143de6)，Credits 52—53。本批只核对既有主体范围，没有给Legend另加本次A字母队列以外的职责。
- Activision：[大审判官](https://www.gog.com/en/game/zork_grand_inquisitor)、[开发方筛选链接](https://www.gog.com/en/games?developers=activision)；范围对照：[重返佐克](https://www.gog.com/en/game/return_to_zork)、[复仇女神](https://www.gog.com/en/game/zork_nemesis_the_forbidden_lands)。前者原作开发署名和后者不同，不据公司版权行核定职责。
- Addison-Wesley：[既有城堡条目](https://www.mobygames.com/game/179572/the-secret-of-arendarvon-castle/)、[已读取的对抗者二手职员条目](https://www.mobygames.com/game/179676/the-antagonists/)、[既有出版公司目录](https://www.mobygames.com/company/3739/addison-wesley-publishing-company-inc/)。二手资料只作待核线索，本批没有从中登记开发。
- Adventure International：[既有原目录](https://www.mocagh.org/ai/ai-v3i2catalog.pdf)，本轮提取受文件大小限制，未冒充全文已读。
- Adventure Soft：[发行方周年版说明](https://store.steampowered.com/app/674150/?l=english)，授权说明区分原作开发者与周年版开发者；官网本轮不可读取，法律身份不补造。
- âge：[自身产品目录](https://age-soft.com/main/products/)、[Muv-Luv单作页](https://age-soft.com/main/products/マブラヴ/)、[Alternative单作页](https://age-soft.com/main/products/マブラヴオルタネイティヴ/)、[原规格](https://muvluv.com/alternative/spec.htm)。[现行Steam本篇](https://store.steampowered.com/app/802880/)及[Alternative](https://store.steampowered.com/app/802890/)用于版本署名对照，不能单独证明早期原作法人。
- Akatsuki Games：[2024-06-16制作开发公告](https://games.aktsk.jp/news/60063/)、[2025-08-31首发公告](https://games.aktsk.jp/news/61804/)。

## 实施与保护

新增5条作品层职责及1项身份订正，全部保留稳定ID、旧署名和原来源。所有 `dossierId` 均为null，不解除其他主体专题的待核引用。主库、关联作品、内容、平台发行及公司关系不变；不重算迁移基线。正式参与记录从4755增至4760，待核身份183减至182，专题待核仍611。主库有创作记录的独立作品由278增至282，另新增1条关联作品创作记录。

左侧“探索企业家族”及其搜索结果按A—Z排序，数字与其他名称置后；关系树结构不改变。组织页显示本批8／32的核查进度、下一家及此证据入口。主库首页正文、布局、筛选与五年导航不改，资料索引更新后仍能读取新增职责。
