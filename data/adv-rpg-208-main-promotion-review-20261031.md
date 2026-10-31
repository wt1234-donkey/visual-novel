# 项目厂商ADV／RPG候选作品主库基础层筛选与入库审核（2026-10-31）

## 此次完成的工作

从原208条项目厂商清单候选出发，先根据已有完整作品、公司专题及新基础身份三种存量归档查重。**仅登记作品名称、首发年份、主要玩法、来源和身份关联**，不为了让作品进入主库而虚构主要角色、具体机型、制作个人或内容版本。

| 处理结果 | 数量 | 处理方式 |
|---|---:|---|
| 既有完整作品档案 | 57 | 原ID复用，在主库统一身份层登记，不新增重复作品 |
| 从厂商专题关联主库 | 103 | 保留原`dossierOnlyWorks`/`relatedGames`等身份，在统一主库基础层建立直接索引 |
| 新纳入主库基础身份 | 47 | 使用之前生成的稳定`basic-`ID，登记标题、首年和玩法 |
| 作品／版本身份待核 | 1 | 《Dragon Knight & Graffiti》原作模式与增量剧情可能重合，先不作为独立作品登记 |
| **总计审核** | **208** | **207条已入主库身份层，1条待核** |

## 主库与完整档案的分工

- `data/main-adv-rpg-works-20261031.json` 是主库的**基础作品身份层**，接入主页`index.html`的**作品发现**；`data/games.json` 是旧有强制包含角色、平台发行与内容版本的完整档案层，两者共享作品身份而不复制发行版本。
- 现有1570余部作品的完整叙事编目统计不会因为本次只有最小字段的作品而虚假增加。
- 本轮从专题及基础索引真正新增**150个可从主库作品发现检索的身份**；57部完整主库已有作品保持不变。
- `minimal-adv-rpg.html`仍是详细表格式检索，能够区分主库已收录、厂商专题关联、基础身份和独立作品资格待核。

## 208条候选作品逐项处理结果

| 关联组 | 作品名 | 年份 | 主要玩法 | 主库处理结果 | 原始资料 |
|---|---|---:|---|---|---|
| T&E SOFT | Planet Mephius | 1983 | ADV | 沿用完整主库 | [关联目录](https://www.gamepres.org/pc88/library/te.html) |
| T&E SOFT | Hydlide | 1984 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/te.html) |
| T&E SOFT | Terra 4001 | 1984 | ADV | 沿用完整主库 | [关联目录](https://www.gamepres.org/pc88/library/te.html) |
| T&E SOFT | Underground Exploration | 1984 | ADV | 沿用完整主库 | [关联目录](https://www.gamepres.org/pc88/library/te.html) |
| 日本 Falcom | Dragon Slayer II: Xanadu | 1985 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| T&E SOFT | Hydlide II: Shine of Darkness | 1985 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/te.html) |
| Square / Square Enix | Crystal Dragon | 1986 | ADV | 沿用完整主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Enix / Square Enix | Dragon Quest | 1986 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Enix / Square Enix | Dragon Quest II | 1987 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Square / Square Enix | Final Fantasy | 1987 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| T&E SOFT | Hydlide 3: The Space Memories | 1987 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/te.html) |
| HummingBird Soft | Laplace no Ma | 1987 | RPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/hummingbird.html) |
| 日本 Falcom | Sorcerian | 1987 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| 日本 Falcom | Ys I | 1987 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Enix / Square Enix | Dragon Quest III | 1988 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Square / Square Enix | Final Fantasy II | 1988 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| HummingBird Soft | Record of Lodoss War: Haiiro no Majo | 1988 | RPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/hummingbird.html) |
| 日本 Falcom | Ys II | 1988 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| TAKERU | プロセルピア | 1988 | RPG | 沿用完整主库 | [关联目录](https://www.gamepres.org/pc88/library/takeru.html) |
| 日本 Falcom | The Legend of Heroes | 1989 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Micro Cabin | Xak: The Art of Visual Stage | 1989 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/microcabin.html) |
| 日本 Falcom | Ys III: Wanderers from Ys | 1989 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| TAKERU | ロンリーハート | 1989 | ADV | 沿用完整主库 | [关联目录](https://www.gamepres.org/pc88/library/takeru.html) |
| NEC Avenue / PC Engine | Dragon Knight II | 1990 | RPG | 专题身份纳入主库 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Enix / Square Enix | Dragon Quest IV | 1990 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Square / Square Enix | Final Fantasy III | 1990 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Micro Cabin | Fray in Magical Adventure | 1990 | ARPG | 新建主库基础身份 | [关联目录](https://www.gamepres.org/pc88/library/microcabin.html) |
| HummingBird Soft | Ghost Hunter | 1990 | RPG | 新建主库基础身份 | [关联目录](https://www.gamepres.org/pc88/library/hummingbird.html) |
| Micro Cabin | Xak II: Rising of the Redmoon | 1990 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/microcabin.html) |
| TAKERU | エストランド物語 | 1990 | RPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/takeru.html) |
| NEC Avenue / PC Engine | Dragon Knight III | 1991 | RPG | 专题身份纳入主库 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Square / Square Enix | Final Fantasy IV | 1991 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Micro Cabin | Illusion City | 1991 | RPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/microcabin.html) |
| HummingBird Soft | Record of Lodoss War 2: Goshiki no Maryuu | 1991 | RPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/hummingbird.html) |
| Square / Square Enix | Seiken Densetsu | 1991 | ARPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Enix / Square Enix | Dragon Quest V | 1992 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Square / Square Enix | Final Fantasy V | 1992 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Philips Interactive Media | Laser Lords | 1992 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Enix / Square Enix | Soul Blazer | 1992 | ARPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| 日本 Falcom | The Legend of Heroes II | 1992 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| NEC Avenue / PC Engine | 同級生 | 1992 | ADV | 沿用完整主库 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| NEC Home Electronics | 3×3 EYES: Sanjiyan Hensei | 1993 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/697/nec-home-electronics-ltd/games/) |
| NEC Avenue / PC Engine | CAL II | 1993 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Micro Cabin | Dragon Half | 1993 | RPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/microcabin.html) |
| Enix / Square Enix | Illusion of Gaia | 1993 | ARPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Philips Interactive Media | Kether | 1993 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| NEC Home Electronics | Return to Zork | 1993 | ADV | 沿用完整主库 | [关联目录](https://www.mobygames.com/company/697/nec-home-electronics-ltd/games/) |
| Square / Square Enix | Secret of Mana | 1993 | ARPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Philips Interactive Media | Voyeur | 1993 | 互动电影ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Micro Cabin | Xak III: The Eternal Recurrence | 1993 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gamepres.org/pc88/library/microcabin.html) |
| NEC Avenue / PC Engine | 魔導物語I 炎の卒園児 | 1993 | RPG | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Alicesoft | AmbivalenZ | 1994 | ADV | 沿用完整主库 | [关联目录](https://www.alicesoft.com/) |
| Philips Interactive Media | Burn:Cycle | 1994 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| NEC Avenue / PC Engine | Dragon Knight 4 | 1994 | SRPG | 专题身份纳入主库 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Square / Square Enix | Final Fantasy VI | 1994 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Philips Interactive Media | Kingdom: The Far Reaches | 1994 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Square / Square Enix | LIVE A LIVE | 1994 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| 日本 Falcom | The Legend of Heroes III: The White Witch | 1994 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| NEC Home Electronics | Blue Chicago Blues | 1995 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/697/nec-home-electronics-ltd/games/) |
| Square / Square Enix | Chrono Trigger | 1995 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| NEC Avenue / PC Engine | Dragon Knight & Graffiti | 1995 | RPG | 身份／内容版本待核（不入独立作品） | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Enix / Square Enix | Dragon Quest VI | 1995 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Leaf | Filsnown -光と刻- | 1995 | RPG | 专题身份纳入主库 | [关联目录](https://zh.moegirl.org.cn/ja/Leaf) |
| Square / Square Enix | Seiken Densetsu 3 | 1995 | ARPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Konami | Suikoden | 1995 | RPG | 专题身份纳入主库 | [关联目录](https://www.konami.com/games/suikoden/) |
| Enix / Square Enix | Terranigma | 1995 | ARPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| 日本 Falcom | Ys V: Lost Kefin, Kingdom of Sand | 1995 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| NEC Home Electronics | リンダキューブ | 1995 | RPG | 专题身份纳入主库 | [关联目录](https://www.mobygames.com/company/697/nec-home-electronics-ltd/games/) |
| Alicesoft | 夢幻泡影 | 1995 | ADV | 沿用完整主库 | [关联目录](https://www.alicesoft.com/) |
| NEC Avenue / PC Engine | 天地無用！魎皇鬼 | 1995 | ADV | 沿用完整主库 | [关联目录](https://www.mobygames.com/company/1315/nec-avenue-ltd/games/) |
| Philips Interactive Media | Alien Incident | 1996 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Philips Interactive Media | Down in the Dumps | 1996 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Square / Square Enix | Dynami Tracer | 1996 | ADV | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Philips Interactive Media | Kingdom II: Shadoan | 1996 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Alicesoft | Only You | 1996 | RPG | 专题身份纳入主库 | [关联目录](https://www.alicesoft.com/) |
| Square / Square Enix | Radical Dreamers | 1996 | ADV | 沿用完整主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Philips Interactive Media | Secret Mission | 1996 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Enix / Square Enix | Star Ocean | 1996 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| 日本 Falcom | The Legend of Heroes IV: A Tear of Vermillion | 1996 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Square / Square Enix | Treasure Conflix | 1996 | ADV | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Philips Interactive Media | Voyeur II | 1996 | 互动电影ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Alicesoft | Atlach=Nacha | 1997 | ADV | 沿用完整主库 | [关联目录](https://www.alicesoft.com/) |
| Philips Interactive Media | Dossier Desiree | 1997 | 互动电影ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/1324/philips-interactive-media-inc/games/) |
| Square / Square Enix | Final Fantasy VII | 1997 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| NEC Home Electronics | アルバレアの乙女 | 1997 | SRPG | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/697/nec-home-electronics-ltd/games/) |
| Square / Square Enix | Another Mind | 1998 | ADV | 沿用完整主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Alicesoft | DiaboLiQuE | 1998 | ADV | 沿用完整主库 | [关联目录](https://www.alicesoft.com/) |
| Square / Square Enix | Parasite Eve | 1998 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Konami | Suikoden II | 1998 | RPG | 专题身份纳入主库 | [关联目录](https://www.konami.com/games/suikoden/) |
| Square / Square Enix | Xenogears | 1998 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Alicesoft | ぱすてるチャイム | 1998 | RPG | 专题身份纳入主库 | [关联目录](https://www.alicesoft.com/) |
| NEC Home Electronics | アンジェリーク 天空の鎮魂歌 | 1998 | RPG | 专题身份纳入主库 | [关联目录](https://www.mobygames.com/company/697/nec-home-electronics-ltd/games/) |
| Square / Square Enix | Chrono Cross | 1999 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Square / Square Enix | Final Fantasy VIII | 1999 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| MAGES. / 5pb. | Memories Off | 1999 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| 日本 Falcom | The Legend of Heroes V: A Cagesong of the Ocean | 1999 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Enix / Square Enix | Valkyrie Profile | 1999 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Enix / Square Enix | Dragon Quest VII | 2000 | RPG | 专题身份纳入主库 | [关联目录](https://www.dragonquest.jp/about/) |
| Square / Square Enix | Final Fantasy IX | 2000 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Konami | Suikoden Gaiden Vol.1: Swordsman of Harmonia | 2000 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.konami.com/games/suikoden/) |
| Banpresto / Summon Night | Summon Night | 2000 | SRPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| Square / Square Enix | Vagrant Story | 2000 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Leaf | まじかる☆アンティーク | 2000 | ADV | 专题身份纳入主库 | [关联目录](https://zh.moegirl.org.cn/ja/Leaf) |
| Square / Square Enix | Final Fantasy X | 2001 | RPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| MAGES. / 5pb. | Memories Off 2nd | 2001 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| Konami | Suikoden Gaiden Vol.2: Duel at Crystal Valley | 2001 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.konami.com/games/suikoden/) |
| Banpresto / Summon Night | Summon Night 2 | 2001 | SRPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| Alicesoft | DALK外伝 | 2002 | RPG | 专题身份纳入主库 | [关联目录](https://www.alicesoft.com/) |
| Square / Square Enix | Kingdom Hearts | 2002 | ARPG | 专题身份纳入主库 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| MAGES. / 5pb. | Memories Off: Omoide ni Kawaru Kimi | 2002 | 视觉小说 | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| Alicesoft | Rance 5D: Hitoribocchi no Onnanoko | 2002 | RPG | 专题身份纳入主库 | [关联目录](https://www.alicesoft.com/) |
| Konami | Suikoden III | 2002 | RPG | 专题身份纳入主库 | [关联目录](https://www.konami.com/games/suikoden/) |
| Banpresto / Summon Night | Summon Night 3 | 2003 | SRPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| Banpresto / Summon Night | Summon Night: Swordcraft Story | 2003 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| 日本 Falcom | Ys VI: The Ark of Napishtim | 2003 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Enix / Square Enix | Dragon Quest VIII | 2004 | RPG | 新建主库基础身份 | [关联目录](https://www.dragonquest.jp/about/) |
| Alicesoft | DUNGEONS&DOLLS | 2004 | RPG | 专题身份纳入主库 | [关联目录](https://www.alicesoft.com/) |
| MAGES. / 5pb. | Memories Off: Sorekara | 2004 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| Konami | Suikoden IV | 2004 | RPG | 专题身份纳入主库 | [关联目录](https://www.konami.com/games/suikoden/) |
| Banpresto / Summon Night | Summon Night: Swordcraft Story 2 | 2004 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| 日本 Falcom | Trails in the Sky FC | 2004 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Cing | Another Code: Two Memories | 2005 | ADV | 沿用完整主库 | [关联目录](https://www.mobygames.com/company/7018/cing-inc/games/) |
| MAGES. / 5pb. | Memories Off #5: Togireta Film | 2005 | 视觉小说 | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| Banpresto / Summon Night | Summon Night: Swordcraft Story - Hajimari no Ishi | 2005 | ARPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| Leaf | Tears to Tiara | 2005 | SRPG | 专题身份纳入主库 | [关联目录](https://zh.moegirl.org.cn/ja/Leaf) |
| Konami | Suikoden V | 2006 | RPG | 专题身份纳入主库 | [关联目录](https://www.konami.com/games/suikoden/) |
| Banpresto / Summon Night | Summon Night 4 | 2006 | SRPG | 专题身份纳入主库 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| 日本 Falcom | Trails in the Sky SC | 2006 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Cing | Hotel Dusk: Room 215 | 2007 | ADV | 沿用完整主库 | [关联目录](https://www.mobygames.com/company/7018/cing-inc/games/) |
| 日本 Falcom | Trails in the Sky the 3rd | 2007 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| MAGES. / 5pb. | CHAOS;HEAD | 2008 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| MAGES. / 5pb. | Corpse Party: BloodCovered | 2008 | ADV | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| Otomate / Idea Factory | Hakuoki: Shinsengumi Kitan | 2008 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.otomate.jp/) |
| MAGES. / 5pb. | Memories Off 6: T-wave | 2008 | 视觉小说 | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| Konami | Suikoden Tierkreis | 2008 | RPG | 专题身份纳入主库 | [关联目录](https://www.konami.com/games/suikoden/) |
| Konami | Time Hollow | 2008 | ADV | 新建主库基础身份 | [关联目录](https://www.konami.com/games/suikoden/) |
| Leaf | 君が呼ぶ、メギドの丘で | 2008 | RPG | 专题身份纳入主库 | [关联目录](https://zh.moegirl.org.cn/ja/Leaf) |
| Cing | Again: Interactive Crime Novel | 2009 | ADV | 新建主库基础身份 | [关联目录](https://www.mobygames.com/company/7018/cing-inc/games/) |
| Enix / Square Enix | Dragon Quest IX | 2009 | RPG | 新建主库基础身份 | [关联目录](https://www.dragonquest.jp/about/) |
| MAGES. / 5pb. | STEINS;GATE | 2009 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| 日本 Falcom | Ys Seven | 2009 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| あっぷりけ-妹- | フェイクアズール・アーコロジー | 2009 | ADV | 沿用完整主库 | [关联目录](https://bangumi.tv/person/7716/works/game) |
| CUBE | 夏ノ雨 | 2009 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| あっぷりけ-妹- | 才気煥発才色兼備の君たちへ | 2009 | ADV | 沿用完整主库 | [关联目录](https://bangumi.tv/person/7716/works/game) |
| FAVORITE | 星空のメモリア | 2009 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.favo-soft.jp/) |
| Cing | Last Window: The Secret of Cape West | 2010 | ADV | 沿用完整主库 | [关联目录](https://www.mobygames.com/company/7018/cing-inc/games/) |
| MAGES. / 5pb. | Memories Off: Yubikiri no Kioku | 2010 | 视觉小说 | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| 日本 Falcom | Trails from Zero | 2010 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| SAGA PLANETS | キサラギGOLD★STAR | 2010 | ADV | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| Otomate / Idea Factory | AMNESIA | 2011 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.otomate.jp/) |
| MAGES. / 5pb. | DUNAMIS15 | 2011 | ADV | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| 日本 Falcom | Trails to Azure | 2011 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| CUBE | your diary | 2011 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| FAVORITE | いろとりどりのセカイ | 2011 | 视觉小说 | 沿用完整主库 | [关联目录](https://www.favo-soft.jp/) |
| あっぷりけ-妹- | アルテミスブルー | 2011 | ADV | 沿用完整主库 | [关联目录](https://bangumi.tv/person/7716/works/game) |
| あっぷりけ-妹- | オトミミ∞インフィニティー | 2011 | ADV | 沿用完整主库 | [关联目录](https://bangumi.tv/person/7716/works/game) |
| MAGES. / 5pb. | ROBOTICS;NOTES | 2012 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| SAGA PLANETS | はつゆきさくら | 2012 | 视觉小说 | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| CUBE | 倉野くんちのふたご事情 | 2012 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| MAGES. / 5pb. | DISORDER6 | 2013 | ADV | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| Banpresto / Summon Night | Summon Night 5 | 2013 | SRPG | 新建主库基础身份 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| 日本 Falcom | Trails of Cold Steel | 2013 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| HARUKAZE | らぶおぶ恋愛皇帝 of LOVE! | 2013 | ADV | 沿用完整主库 | [关联目录](https://harukaze-soft.com/) |
| SAGA PLANETS | カルマルカ＊サークル | 2013 | ADV | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| MAGES. / 5pb. | CHAOS;CHILD | 2014 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| Otomate / Idea Factory | Code:Realize - Guardian of Rebirth | 2014 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.otomate.jp/) |
| 日本 Falcom | Trails of Cold Steel II | 2014 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| FAVORITE | アストラエアの白き永遠 | 2014 | 视觉小说 | 沿用完整主库 | [关联目录](https://www.favo-soft.jp/) |
| CUBE | 恋する彼女の不器用な舞台 | 2014 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| Alicesoft | Evenicle | 2015 | RPG | 专题身份纳入主库 | [关联目录](https://www.alicesoft.com/) |
| MintCUBE | あま恋シロップス | 2015 | ADV | 新建主库基础身份 | [关联目录](https://cuffs-cube.jp/main/products/) |
| SAGA PLANETS | 花咲ワークスプリング！ | 2015 | ADV | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| Otomate / Idea Factory | Collar×Malice | 2016 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.otomate.jp/) |
| Banpresto / Summon Night | Summon Night 6: Lost Borders | 2016 | SRPG | 新建主库基础身份 | [关联目录](https://www.gavas.jp/products/detail.php?product_id=9113) |
| 日本 Falcom | Ys VIII: Lacrimosa of Dana | 2016 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| HARUKAZE | ノラと皇女と野良猫ハート | 2016 | ADV | 沿用完整主库 | [关联目录](https://harukaze-soft.com/) |
| SAGA PLANETS | フローラル・フローラブ | 2016 | ADV | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| CUBE | 間宮くんちの五つ子事情 | 2016 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| Enix / Square Enix | Dragon Quest XI | 2017 | RPG | 新建主库基础身份 | [关联目录](https://www.dragonquest.jp/about/) |
| 日本 Falcom | Trails of Cold Steel III | 2017 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| CUBE | ゆらめく心に満ちた世界で、君の夢と欲望は叶うか | 2017 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| HARUKAZE | ノラと皇女と野良猫ハート2 | 2017 | ADV | 沿用完整主库 | [关联目录](https://harukaze-soft.com/) |
| MintCUBE | 人気声優のつくりかた | 2017 | ADV | 新建主库基础身份 | [关联目录](https://cuffs-cube.jp/main/products/) |
| SAGA PLANETS | 金色ラブリッチェ | 2017 | 视觉小说 | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| MAGES. / 5pb. | Memories Off: Innocent Fille | 2018 | 视觉小说 | 新建主库基础身份 | [关联目录](https://mages.co.jp/games/) |
| Square / Square Enix | Octopath Traveler | 2018 | RPG | 新建主库基础身份 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| Otomate / Idea Factory | Piofiore: Fated Memories | 2018 | 视觉小说 | 新建主库基础身份 | [关联目录](https://www.otomate.jp/) |
| 日本 Falcom | Trails of Cold Steel IV | 2018 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| MintCUBE | 勇者と魔王と、魔女のカフェ | 2018 | ADV | 新建主库基础身份 | [关联目录](https://cuffs-cube.jp/main/products/) |
| 日本 Falcom | Ys IX: Monstrum Nox | 2019 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| FAVORITE | さくら、もゆ。-as the Night's, Reincarnation- | 2019 | 视觉小说 | 沿用完整主库 | [关联目录](https://www.favo-soft.jp/) |
| 日本 Falcom | Trails into Reverie | 2020 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| SAGA PLANETS | かけぬけ★青春スパーキング！ | 2020 | ADV | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| CUBE | 神様のような君へ | 2020 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| HARUKAZE | Monkeys!¡ | 2021 | ADV | 沿用完整主库 | [关联目录](https://harukaze-soft.com/) |
| 日本 Falcom | The Legend of Heroes: Kuro no Kiseki | 2021 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| FAVORITE | ハッピーライヴ ショウアップ！ | 2021 | ADV | 沿用完整主库 | [关联目录](https://www.favo-soft.jp/) |
| CUBE | 海と雪のシアンブルー | 2021 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| SAGA PLANETS | AMBITIOUS MISSION | 2022 | ADV | 沿用完整主库 | [关联目录](https://sagaplanets.product.co.jp/) |
| MAGES. / 5pb. | ANONYMOUS;CODE | 2022 | 视觉小说 | 沿用完整主库 | [关联目录](https://mages.co.jp/games/) |
| 日本 Falcom | The Legend of Heroes: Kuro no Kiseki II | 2022 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| Square / Square Enix | Triangle Strategy | 2022 | SRPG | 新建主库基础身份 | [关联目录](https://www.jp.square-enix.com/recruit/career/ip/index.html) |
| CUBE | サメと生きる七日間 | 2022 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| CUBE | ネコと女子寮せよ！ | 2022 | ADV | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| CUBE | 夏ノ終熄 | 2022 | 视觉小说 | 沿用完整主库 | [关联目录](https://cuffs-cube.jp/main/products/) |
| 日本 Falcom | Ys X: Nordics | 2023 | ARPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |
| CUBE | 恋し彩る正義爛漫 | 2023 | ADV | 新建主库基础身份 | [关联目录](https://cuffs-cube.jp/main/products/) |
| 日本 Falcom | The Legend of Heroes: Kai no Kiseki | 2024 | RPG | 专题身份纳入主库 | [关联目录](https://www.falcom.co.jp/ir/falcomgame) |

## 特别核实的事项

1. 《Dragon Knight & Graffiti》1995年PC Engine发行信息记载附有Original Mode与本作RPG迷宫系统；需区分与《Dragon Knight》初版相同的剧情及独有新增故事，防止把重制/内容同版错误记作第二部作品。资料：https://www.tg-16.com/contributors/dshadoff/Daigirin/Daigirin_1997_06_NEC_Extract.pdf 。
2. 《Corpse Party: BloodCovered》最早章节与后续Windows整合版经历多次分段发行；2008按Windows初版登记，仅作为年份初筛，不代表1996原作或2006移动版发行年。年份和内容版本史后续单独核。
3. 《Summon Night 5》2013年作品关联Banpresto系列历史，但官方实际发行为Bandai Namco Games、制作为Felistella；本次仅维持“厂商关联组”，**不把Banpresto冒认为2013年制作/发行商**。参考：https://mediaarts-db.artmuseums.go.jp/id/M720871 。
4. 许多候选来源是厂商或系列总目录，**尚未逐条核查地区、首发平台、单日发行和制作职责**。本轮收录结论是作品基础身份与玩法初筛，而非完整出版年表终审。

## 测试与去重原则

运行`python3 scripts/promote_adv_rpg_candidates_20261031.py`生成统一主库身份层，运行单元测试确认208条候选恰好分为57/103/47/1，所有主库和专题引用ID真实存在、没有制造内容版本或角色字段。再对主页作品发现、详细列表、Node模块、旧有Python/Node与历史正文保护执行回归测试。
