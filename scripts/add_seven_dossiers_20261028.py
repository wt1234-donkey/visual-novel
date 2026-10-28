"""Add four historical company dossiers, four original narrative games and history notes.
Idempotent, additive; three already established dossiers remain unchanged.
"""
import json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def load(p):return json.loads((R/p).read_text(encoding="utf-8"))
def save(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
g=load("data/games.json"); cov=load("data/company-coverage.json")
existing={w["id"] for w in g["works"]}

SPECS=[
("g1303","钟楼","クロックタワー",1995,"文字冒险","动作解谜融合","恐怖悬疑／场景调查／多结局",["Jennifer Simpson","Scissorman","Mary Barrows"],"孤儿珍妮弗来到巴洛斯家族的宅邸，调查房间、寻找同伴并躲避巨剪杀手，在不同选择与生存结果中走向多种结局。",["点击调查","即时动作","谜题操作"],"指针调查房间、使用机关和躲避追击；不是自由文字输入。","Super Famicom","ヒューマン","Human Entertainment","未核实","https://mediaworld.co.jp/products/10006060003","https://www.mobygames.com/game/12414/clock-tower/"),
("g1304","Remember11：无限轮回","Remember11 -the age of infinity-",2004,"视觉小说","剧情分支／冒险","科幻悬疑／双视角／心理推理",["冬川こころ","優希堂悟","楠田ゆに","黛鈴"],"冬川心与优希堂悟分别卷入雪山事故和封闭设施事件，两个视角逐步揭开记忆与身份的联系。",["阅读推进","选项分支","视角切换"],"双视角章节的阅读与选项推进；视角切换仅指叙事路径，不宣称可随时切换。","PlayStation 2（日本）","KID","KID","有","https://www.mobygames.com/game/14487/remember11-the-age-of-infinity/releases/","https://w.atwiki.jp/ercr/pages/4724.html"),
("g1305","黄昏症候群：探索篇","トワイライトシンドローム 探索編",1996,"文字冒险","动作解谜融合","校园怪谈／都市传说／横向探索",["長谷川ユカリ","岸井ミカ","逸島チサト"],"三名女高中生夜间调查学校和街道的都市传说，逐章探访传闻地点并面临不同结果。",["直接移动","选项分支"],"横向移动探索与不同怪谈结局；不把未知操作推断为鼠标点击。","PlayStation（日本）","ヒューマン","Human Entertainment","未核实","https://www.mobygames.com/game/49539/twilight-syndrome-tansaku-hen/","https://w.atwiki.jp/advr/pages/15.html"),
("g1306","黄昏症候群：究明篇","トワイライトシンドローム 究明編",1996,"文字冒险","动作解谜融合","校园怪谈／后篇／都市传说",["長谷川ユカリ","岸井ミカ","逸島チサト"],"延续探索篇的三名少女的怪谈调查，追加独立发售的后续章节和事件。",["直接移动","选项分支"],"延续横向场景探索及按行动改变怪谈结局的结构。","PlayStation（日本）","ヒューマン","Human Entertainment","未核实","https://www.mobygames.com/game/49540/twilight-syndrome-kyumei-hen/","https://w.atwiki.jp/gcmatome/pages/3817.html")
]
for wid,title,original,year,cat,sub,genre,chars,story,modes,controls,platform,pub,company,voice,src,detail in SPECS:
 if wid in existing:
  assert next(w for w in g["works"] if w["id"]==wid)["originalTitle"]==original
  continue
 g["works"].append({"id":wid,"title":title,"chineseTitle":title,"chineseTitleType":"站内编辑译名","originalTitle":original,"titleAliases":[original],"firstYear":year,"category":cat,"subcategory":sub,"genre":genre,"characters":chars,"charactersSource":detail,"synopsis":story,"notes":"独立原作首发；普通移植、合集、复刻或未核的新增内容不另建版本。","source":src,"interactionModes":modes,"interactionNote":controls,"interactionBasis":"来源核对","interactionSources":[src,detail]})
 g["contentVersions"].append({"id":wid+"-c-original","workId":wid,"label":str(year)+"年原作／首批内容","firstYear":year,"basis":"original","evidence":"原作首次发行，具体日期及发行主体见发行资料；未将后发普通移植算成新内容。","source":src,"evidenceReleaseIds":[wid+"-v1"],"addedContent":[]})
 g["platformReleases"].append({"id":wid+"-v1","workId":wid,"year":year,"platform":platform,"publisher":pub,"publisherCompanies":[company],"kind":"原作首发","voice":voice,"differences":"独立原作首发；未核后发版差不新建内容版本。","source":src,"contentVersionId":wid+"-c-original","contentRelation":"original","contentNote":"原作／首批内容。","releaseRole":"contentDebut"})
save("data/games.json",g)
works={w["id"]:w for w in g["works"]}
COMPANIES=[
{"id":"dreamworks_interactive","name":"DreamWorks Interactive","ids":["g967","g968"],"source":"https://news.microsoft.com/source/1996/07/09/welcome-to-yourtown-usa/","scope":"1995年Microsoft与DreamWorks SKG共同成立互动软件公司，首批复用黏土动画与实拍恐怖冒险两部。","history":"1995年3月合资成立；2000年EA收购。The Neverhood, Inc.实际制作团队与发行、合资关系分开。","date":"1995-03","dateSource":"https://www.gamespot.com/articles/ea-buys-dreamworks-interactive/1100-2541510/","phase":"1995—2000","heading":"合资创作与后续收购"},
{"id":"human_entertainment","name":"Human Entertainment（ヒューマン）","ids":["g1303","g1305","g1306","g1015"],"source":"https://prtimes.jp/main/html/rd/p/000000024.000029510.html","scope":"历史Human叙事作品：1995钟楼初代、1996黄昏症候群前后篇、1996钟楼2。非叙事体育和摔角作品不计。","history":"1995 SFC初代与1996 PS续作是不同作品；黄昏前后篇分别发行。旧HUMAN大写身份与ヒューマン暂不合并。","phase":"1995—1996","heading":"恐怖调查与都市传说"},
{"id":"impact_interactive","name":"Impact Interactive Publishing","ids":["g1014"],"source":"https://www.mobygames.com/company/6879/impact-interactive-publishing-pty-ltd/","scope":"目前仅核到DogDay这一部叙事发行；Eyst开发与Impact发行、日版ASCII移植发行分开。","history":"同期广告使用Impact Interactive Publishing Pty Ltd，成立日、解散日与1996/1997地区发行异文仍待原始证据。","phase":"1996—1998","heading":"DogDay地区出版与日本移植"},
{"id":"kid","name":"KID（キッド）","ids":["g698","g719","g739","g718","g773","g152","g048","g153","g154","g050","g545","g233","g167","g1304","g168"],"source":"https://game.watch.impress.co.jp/docs/20070202/kid.htm","scope":"首批15部叙事作品：早期PC作品的主机移植、Memories Off、infinity与Remember11。开发与发行角色不自动等同。","history":"历史株式会社キッド与2007年CyberFront承继部分游戏权利分开；后续权利方不继承旧原作开发身份。","phase":"1996—2007","heading":"恋爱冒险、科幻悬疑与权利承继"}
]
byid={c["id"] for c in cov["companies"]}
for s in COMPANIES:
 if s["id"] in byid:continue
 ids=s["ids"]
 assert len(set(ids))==len(ids) and all(w in works for w in ids)
 c={"id":s["id"],"name":s["name"],"checkedAt":"2026-10-28","status":"首批已核叙事目录，尚非完整发行史","scope":s["scope"],"versionScope":"复用已有作品与内容发行身份；仅四部新作各建原作首发，普通移植、合集、廉价版及未核新增内容不加行。","publisherNote":s["history"],"publisherWorkText":"<p class=\"scope-note\"><strong>"+str(len(ids))+"部主库关联；实际制作、发行、移植及历史法人分开。</strong></p>","workIds":ids,"publisherWorkIds":ids,"catalogueEntryCount":len(ids),"source":s["source"],"sectionTitle":"首批叙事作品与历史署名","description":s["name"]+"历史叙事作品专题，含原作、内容版本、平台发行与组织沿革。","auditTitle":"原作、发行与职责核查","auditSourceLabel":"历史出版及游戏资料","auditLabel":str(len(ids))+"部已核主库作品，非完整发行目录。","auditNote":"证据及未决边界见 data/seven-dossiers-audit-20261028.md。","creativeProfile":{"thesis":"本专题仅按已核原作和发行署名归类，不将母公司、版权方或后续发行方自动当作开发团队。","phases":[{"period":s["phase"],"heading":s["heading"],"analysis":s["history"],"basis":"来源核对／编辑观察","source":s["source"]}]},"entries":[{"title":works[wid]["originalTitle"],"status":"本次新增原作" if wid in {"g1303","g1304","g1305","g1306"} else "复用既有主库","reason":"历史原作与具体发行按证据分层；后发普通移植不重复。","source":works[wid]["source"],"workIds":[wid]} for wid in ids]}
 if "date" in s:c["foundedAt"]=s["date"];c["foundedSource"]=s["dateSource"]
 cov["companies"].append(c)
save("data/company-coverage.json",cov)

# Reuse reviewed publisher IDs instead of creating homonymous company identities.
p=R/"scripts/build_entity_model.py";s=p.read_text(encoding="utf-8")
old=next(x for x in s.splitlines() if x.startswith("  ident={"))
new="""  ident={'leland':'entity-name-547f933b0469','takeru':'entity-name-08cbddd5e450','tokuma_intermedia':'entity-name-9832231b6baa','chunsoft':'entity-name-21365baf366d','ultra_games':'entity-name-c87c2b9662fc','broderbund':'entity-name-e0c32a99a906','lucasarts':'entity-name-57509c825879','nec_avenue':'entity-name-0b22f68e63fb','dreamworks_interactive':'entity-name-4c4c2f63075a','human_entertainment':'entity-name-4f1d0851948b','impact_interactive':'entity-name-c73a46096ea7','kid':'entity-name-3a59ff4a4f09'}.get(cid) if cid in {'leland','takeru','tokuma_intermedia','chunsoft','ultra_games','broderbund','lucasarts','nec_avenue','dreamworks_interactive','human_entertainment','impact_interactive','kid'} else add_entity(eid,name,kind,NAMES.get(cid,[]),c['source'],note=c['publisherNote'])"""
if old!=new:
 assert "nec_avenue" in old and "add_entity(eid,name,kind" in old
 p.write_text(s.replace(old,new),encoding="utf-8")

events=[]
def event(id,year,title,note,ids,url):
 events.append({"id":id,"entityIds":ids,"year":year,"title":title,"note":note,"recordIds":[],"sources":[{"title":"来源","url":url}]})
event("seven-shopro-1967",1967,"小学馆Production成立","1967/06/26独立成立，不与小学馆出版母公司合并。",["entity-shopro"],"https://www.shopro.co.jp/corporate/history/history_1990-1967.html")
event("seven-tokuma-1954",1954,"德间书店本体创立","1954年母公司创立不等于后设Intermedia成立。",["entity-tokuma"],"https://www.tokuma.jp/company/")
event("seven-dreamworks-1995",1995,"DreamWorks Interactive合资成立","Microsoft与DreamWorks SKG于1995年3月合资；不由股权推定逐作开发。",["entity-name-4c4c2f63075a","entity-microsoft"],"https://www.gamespot.com/articles/ea-buys-dreamworks-interactive/1100-2541510/")
event("seven-dreamworks-2000",2000,"EA收购DreamWorks Interactive","后续EA身份不倒填1996原作发行。",["entity-name-4c4c2f63075a"],"https://www.awn.com/news/ea-acquires-dreamworks-interactive")
event("seven-human-1995",1995,"Human发行钟楼初代","SFC初代与1996 PS续作不同；HUMAN异写未合并。",["entity-name-4f1d0851948b"],"https://mediaworld.co.jp/products/10006060003")
event("seven-impact-1996",1996,"Impact发行DogDay","Impact地区发行与Eyst原作开发分开，1996/1997异文待核。",["entity-name-c73a46096ea7"],"https://www.mobygames.com/company/6879/impact-interactive-publishing-pty-ltd/")
event("seven-kid-2007",2007,"KID权利与业务承继","CyberFront承接部分权利，不等于原KID法人继续经营。",["entity-name-3a59ff4a4f09"],"https://game.watch.impress.co.jp/docs/20070202/kid.htm")
event("seven-leaf-1996",1996,"Leaf早期视觉小说阶段","Leaf品牌与AQUAPLUS公司分开；1996雫与痕按历史署名归档。",["entity-leaf","entity-aquaplus"],"https://leaf.aquaplus.jp/product/index.html")
save("data/seven-dossiers-history-20261028.json",{"reviewedAt":"2026-10-28","audit":"data/seven-dossiers-audit-20261028.md","events":events})
p=R/"scripts/build_organizations.py";s=p.read_text(encoding="utf-8")
old="'nec-home-electronics-history-20261028'] for event";new="'nec-home-electronics-history-20261028','seven-dossiers-history-20261028'] for event"
if old in s:p.write_text(s.replace(old,new),encoding="utf-8")
else:assert new in s

audit="""# 七家厂商专题及组织沿革首批核查（2026-10-28）

保留既有Shogakukan Production（shopro，3部）、Tokuma Shoten（tokuma，6部）、Leaf（leaf，14部）及Tokuma Intermedia子专题；不重复创建作品或历史法人。

本次新建DreamWorks Interactive（2部复用）、Human Entertainment（4部，其中3部新增）、Impact Interactive Publishing（1部复用）、KID（15部，其中1部新增）专题。新增主库四部：g1303钟楼1995 SFC、g1304 Remember11 2004 PS2、g1305黄昏症候群探索篇1996 PS、g1306黄昏症候群究明篇1996 PS。各新增一条原作内容和首次发行；后发普通移植与合集不计新增内容。

## 来源
- ShoPro官方沿革：https://www.shopro.co.jp/corporate/history/history_1990-1967.html
- 德间书店公司概要：https://www.tokuma.jp/company/
- Leaf官方产品目录：https://leaf.aquaplus.jp/product/index.html
- DreamWorks 1995合资与2000收购：https://www.gamespot.com/articles/ea-buys-dreamworks-interactive/1100-2541510/
- DreamWorks 1996产品线：https://news.microsoft.com/source/1996/07/09/welcome-to-yourtown-usa/
- Human钟楼原版：https://mediaworld.co.jp/products/10006060003
- Human黄昏探索篇：https://www.mobygames.com/game/49539/twilight-syndrome-tansaku-hen/
- Human黄昏究明篇：https://www.mobygames.com/game/49540/twilight-syndrome-kyumei-hen/
- Impact与DogDay：https://www.mobygames.com/company/6879/impact-interactive-publishing-pty-ltd/
- DogDay地区发行：https://www.hardcoregaming101.net/dogday/
- KID Remember11：https://www.mobygames.com/game/14487/remember11-the-age-of-infinity/releases/
- KID 2007业务承继：https://game.watch.impress.co.jp/docs/20070202/kid.htm

## 待核及范围限制
1. Human原有HUMAN大写和ヒューマン两个身份仍保留，缺原盒法人证据，不合并。
2. DreamWorks合资、收购不等于The Neverhood原作由Microsoft或DreamWorks单方开发；The Neverhood, Inc.另署。
3. Impact确切成立、解散日期和DogDay 1996/1997地区日期异文未核；Eyst开发与Impact发行分开。
4. KID早期主机移植不自动判为其原创开发；CyberFront继受权利不继承旧法人身份。
5. 钟楼The First Fear与Rewind、黄昏Special合集、Remember11后发版均未证实首次新增剧情等内容，暂不新增内容身份。
6. 四个新专题是有证据的叙事首批目录，非厂商全部游戏史；不录纯体育、射击、麻将或非叙事作品。

新专题复用已审历史发行主体稳定ID，组织事件仅是有来源的历史展示，不修改旧作品与发行原文。按仓库正常生成器及测试核验。
"""
(R/"data/seven-dossiers-audit-20261028.md").write_text(audit,encoding="utf-8")
print("Prepared four new dossiers, four original works and eight organization events.")
