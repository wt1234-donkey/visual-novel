"""Build additive entity/credit/classification indexes without rewriting historical records."""
import argparse
import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from entity_names import apply_names, NAMES as DISPLAY_NAMES, display_name

ROOT = Path(__file__).resolve().parents[1]
BASE = '35b988136f016199d26121e41ca8d7b99d18e310'
DATE = '2026-10-22'
PRIORITY_REVIEW = 'data/entity-priority-review-20261022.json'
FOLLOWUP_REVIEW = 'data/entity-followup-review-20261022.json'
THIRD_REVIEW = 'data/entity-third-review-20261022.json'
FOURTH_REVIEW = 'data/entity-fourth-review-20261022.json'
CREATOR_A_REVIEW = 'data/entity-creator-a-review-20261022.json'
CREATOR_A2_REVIEW = 'data/entity-creator-a2-review-20261022.json'
CREATOR_A3_REVIEW = 'data/entity-creator-a3-review-20261022.json'
CREATOR_A4_REVIEW = 'data/entity-creator-a4-review-20261023.json'
CREATOR_A5_REVIEW = 'data/entity-creator-a5-review-20261023.json'
CREATOR_A6_REVIEW = 'data/entity-creator-a6-review-20261023.json'
CREATOR_B1_REVIEW = 'data/entity-creator-b1-review-20261023.json'
CREATOR_B2_REVIEW = 'data/entity-creator-b2-review-20261023.json'
CREATOR_B3_REVIEW = 'data/entity-creator-b3-review-20261023.json'
CREATOR_C1_REVIEW = 'data/entity-creator-c1-review-20261023.json'
CREATOR_C2_REVIEW = 'data/entity-creator-c2-review-20261023.json'
CREATOR_C3_REVIEW = 'data/entity-creator-c3-review-20261023.json'
CREATOR_C4_REVIEW = 'data/entity-creator-c4-review-20261023.json'
CREATOR_D1_REVIEW = 'data/entity-creator-d1-review-20261023.json'
CREATOR_D2_REVIEW = 'data/entity-creator-d2-review-20261023.json'
CREATOR_D3_REVIEW = 'data/entity-creator-d3-review-20261023.json'
CREATOR_E1_REVIEW = 'data/entity-creator-e1-review-20261023.json'
CREATOR_E2_REVIEW = 'data/entity-creator-e2-review-20261024.json'
CREATOR_E3_REVIEW = 'data/entity-creator-e3-review-20261024.json'
CREATOR_F1_REVIEW = 'data/entity-creator-f1-review-20261024.json'
CREATOR_F2_REVIEW = 'data/entity-creator-f2-review-20261024.json'
CREATOR_G1_REVIEW = 'data/entity-creator-g1-review-20261024.json'
CREATOR_G2_REVIEW = 'data/entity-creator-g2-review-20261024.json'
CREATOR_G3_REVIEW = 'data/entity-creator-g3-review-20261024.json'
CREATOR_H1_REVIEW = 'data/entity-creator-h1-review-20261024.json'
CREATOR_H2_REVIEW = 'data/entity-creator-h2-review-20261024.json'
CREATOR_H3_REVIEW = 'data/entity-creator-h3-review-20261024.json'
CREATOR_I1_REVIEW = 'data/entity-creator-i1-review-20261024.json'
CREATOR_I2_REVIEW = 'data/entity-creator-i2-review-20261024.json'
CREATOR_I3_REVIEW = 'data/entity-creator-i3-review-20261024.json'
CREATOR_I4_REVIEW = 'data/entity-creator-i4-review-20261024.json'
CREATOR_J1_REVIEW = 'data/entity-creator-j1-review-20261024.json'
CREATOR_K1_REVIEW = 'data/entity-creator-k1-review-20261024.json'
CREATOR_K2_REVIEW = 'data/entity-creator-k2-review-20261024.json'
CREATOR_K3_REVIEW = 'data/entity-creator-k3-review-20261025.json'
CREATOR_L1_REVIEW = 'data/entity-creator-l1-review-20261025.json'
CREATOR_L2_REVIEW = 'data/entity-creator-l2-review-20261025.json'
CREATOR_L3_REVIEW = 'data/entity-creator-l3-review-20261025.json'
CREATOR_M1_REVIEW = 'data/entity-creator-m1-review-20261025.json'
CREATOR_M2_REVIEW = 'data/entity-creator-m2-review-20261025.json'
CREATOR_M3_REVIEW = 'data/entity-creator-m3-review-20261025.json'
CREATOR_M4_REVIEW = 'data/entity-creator-m4-review-20261025.json'
CREATOR_M5_REVIEW = 'data/entity-creator-m5-review-20261025.json'
CREATOR_M6_REVIEW = 'data/entity-creator-m6-review-20261025.json'
CREATOR_N1_REVIEW = 'data/entity-creator-n1-review-20261025.json'
CREATOR_N2_REVIEW = 'data/entity-creator-n2-review-20261025.json'
CREATOR_N3_REVIEW = 'data/entity-creator-n3-review-20261025.json'
CREATOR_N4_REVIEW = 'data/entity-creator-n4-review-20261025.json'
CREATOR_N5_REVIEW = 'data/entity-creator-n5-review-20261025.json'
CREATOR_O1_REVIEW = 'data/entity-creator-o1-review-20261025.json'
CREATOR_P1_REVIEW = 'data/entity-creator-p1-review-20261025.json'
CREATOR_P2_REVIEW = 'data/entity-creator-p2-review-20261025.json'
CREATOR_P3_REVIEW = 'data/entity-creator-p3-review-20261025.json'
CREATOR_Q1_REVIEW = 'data/entity-creator-q1-review-20261025.json'
CREATOR_R1_REVIEW = 'data/entity-creator-r1-review-20261025.json'
CREATOR_R2_REVIEW = 'data/entity-creator-r2-review-20261025.json'
CREATOR_S1_REVIEW = 'data/entity-creator-s1-review-20261025.json'
CREATOR_S2_REVIEW = 'data/entity-creator-s2-review-20261025.json'
CREATOR_S3_REVIEW = 'data/entity-creator-s3-review-20261026.json'
CREATOR_S4_REVIEW = 'data/entity-creator-s4-review-20261026.json'
TYPE_LABELS = {'company':'公司／组织','brand':'品牌','team':'制作团队','publication':'刊物／出版名义','individual':'个人','unknown':'身份待核','history':'沿革专题'}
ROLE_LABELS = {'originalProduction':'原作制作','developer':'开发','coDeveloper':'联合制作','productionBrand':'制作品牌','originalPublishingBrand':'原作发行品牌','publisher':'发行署名','publishingBrand':'发行品牌','portDeveloper':'移植开发','localizer':'本地化','licensor':'授权合作','supervisor':'监修','copyrightCredit':'版权署名','catalogueAssociation':'专题关联（职责待核）','addedAnimation':'新增动画制作'}
BRANDS = set('key aniplex_exe sprite madosoft yuzusoft innocent_grey minori august toneworks asaproject leaf sagaplanets smee favorite cuffs cube sphere palette silkys silkys_plus alicesoft overdrive cocktailsoft macadamia fairytale cabbage hulotte laplacian applique clochette nanawind harukaze sorahane hummingbird_soft minatosoft'.split())
HISTORIES = {'sierra','sierra_on_line','falcom','te_soft','banpresto'}
NAMES = {'key':['Key'], 'novect':['NOVECT','Novectacle'], 'aniplex_exe':['ANIPLEX.EXE'], 'sprite':['sprite','sprite games'], 'madosoft':['まどそふと'], 'yuzusoft':['ゆずソフト'], 'innocent_grey':['Innocent Grey'], 'minori':['minori'], 'august':['AUGUST'], 'toneworks':['tone work’s',"tone work's"], 'asaproject':['ASa Project'], 'elf':['ELF','エルフ'], 'leaf':['Leaf'], 'sagaplanets':['SAGA PLANETS'], 'smee':['SMEE'], 'favorite':['FAVORITE'], 'cuffs':['CUFFS'], 'cube':['CUBE'], 'sphere':['Sphere'], 'palette':['ぱれっと'], 'silkys':['Silky’s',"Silky's"], 'silkys_plus':['Silky’s Plus',"Silky's Plus"], 'alicesoft':['Alicesoft','ALICESOFT','アリスソフト'], 'nitroplus':['Nitroplus','NITRO PLUS'], 'overdrive':['OVERDRIVE'], 'jast':['JAST（日本）'], 'cocktailsoft':['Cocktail Soft','カクテルソフト','カクテル・ソフト'], 'macadamia':['Macadamia Soft'], 'fairytale':['フェアリーテール','FairyTale','FAIRYTALE'], 'gaina':['GAINA','BENTEN Film'], 'gainax':['GAINAX'], 'jhv':['Japan Home Video'], 'cabbage':['きゃべつそふと','Cabbage Soft'], 'hulotte':['HULOTTE'], 'laplacian':['Laplacian'], 'applique':['あっぷりけ'], 'clochette':['Clochette'], 'nanawind':['NanaWind'], 'harukaze':['HARUKAZE','HARU❀KAZE'], 'sorahane':['SORAHANE'], 'taito':['TAITO（太东）','TAITO'], 'nec_he':['NEC Home Electronics'], 'tokuma':['徳間書店'], 'sega':['世嘉','SEGA'], 'shopro':['小学館プロダクション'], 'hokubu':['北部通信工業'], 'konami':['Konami'], 'hudson':['Hudson Soft（哈德森）','Hudson Soft'], 'sinclair':['Sinclair Research'], 'cinematronics':['Cinematronics'], 'microsoft':['Microsoft'], 'enix':['Enix（艾尼克斯）','Enix'], 'dataeast':['Data East'], 'ascii':['ASCII'], 'melbournehouse':['Melbourne House'], 'koei':['光荣','KOEI'], 'banpresto':['Banpresto'], 'adventure_international':['Adventure International'], 'infocom':['Infocom'], 'sierra':['On-Line Systems','Sierra On-Line'], 'sierra_on_line':['Sierra On-Line'], 'psk':['PSK'], 'microcabin':['Micro Cabin','マイクロキャビン'], 'legend_uk':['Legend（英国）'], 'legend_entertainment':['Legend Entertainment'], 'te_soft':['T&E SOFT'], 'carry_lab':['Carry Lab','キャリーラボ'], 'champion_soft':['チャンピオンソフト','ChampionSoft','Champion Soft'], 'hummingbird_soft':['HummingBird Soft','ハミングバードソフト'], 'riverhill_soft':['Riverhill Soft','リバーヒルソフト'], 'falcom':['日本ファルコム','Falcom'], 'ibm':['IBM'], 'mosaic':['Mosaic Publishing'], 'square':['Square','スクウェア'], 'toho':['東宝','TOHO'], 'db_soft':['dB-SOFT'], 'comptiq':['Comptiq','コンプティーク'], 'minatosoft':['みなとそふと','Minato Soft'], 'hawkeye':['株式会社ホークアイ','Hawk Eye'], 'addison_wesley':['Addison-Wesley','Addison-Wesley Publishing Company']}
EXTRAS = [
 ('visualarts','VISUAL ARTS','company',['VisualArt’s','VisualArts','VISUAL ARTS'], 'https://visual-arts.jp/blog_2024_1/'),
 ('aquaplus','AQUAPLUS','company',['AQUAPLUS'],'https://aquaplus.jp/sitepolicy/'),
 ('aquaplus_brand','AQUAPLUS','brand',[], 'https://aquaplus.jp/'),
 ('aniplex','Aniplex','company',['Aniplex','Aniplex Inc.'],'https://aniplex-exe.com/'),
 ('fandc','F&C','company',['F&C','FANDC'],'https://fandc.co.jp/extra/corporate'),
 ('frontwing','Frontwing','brand',['Frontwing','フロントウイング'],'https://aniplex-exe.com/news/?category=atri-mdm&id=52873'),
 ('makura','枕','brand',['枕','Makura'],'https://aniplex-exe.com/news/?category=atri-mdm&id=52873'),
 ('liarsoft','Liar-soft','brand',['Liar-soft','ライアーソフト'],'https://aniplex-exe.com/news/?category=aniplex-exe&id=52845'),
 ('imel','iMel','company',['iMel','iMel株式会社'],'https://imel.co.jp/activity/'),
 ('prototype','PROTOTYPE','company',['PROTOTYPE'],'https://www.prot.co.jp/switch/kanon/'),
 ('nitroplus_brand','Nitroplus','brand',[], 'https://www.nitroplus.co.jp/company/'),
 ('nitrochiral','NITRO CHiRAL','brand',['Nitro+CHiRAL','Nitro CHiRAL','NITRO CHiRAL'],'https://www.nitroplus.co.jp/company/'),
 ('nitroorigin','NITRO ORIGIN','brand',['NITRO ORIGIN'],'https://www.nitroplus.co.jp/company/'),
 ('entergram','ENTERGRAM','company',['ENTERGRAM','Entergram','エンターグラム'],'https://www.entergram.co.jp/corporate.html'),
 ('mages','MAGES.','company',['MAGES.'],'https://mages.co.jp/about/company'),
 ('5pb','5pb.','brand',['5pb.'],'https://mages.co.jp/topics/ir/20190726/post-145'),
 ('koei_tecmo','光荣特库摩游戏（Koei Tecmo Games）','company',['コーエーテクモゲームス','Koei Tecmo Games','光荣特库摩游戏（Koei Tecmo Games）'],'https://www.koeitecmo.co.jp/company/group/'),
 ('hunex','HuneX','company',['HuneX','ヒューネックス'],'https://www.hunex.co.jp/archives/company/history'),
 ('dramaticcreate','dramatic create','brand',['dramatic create'],'https://www.hunex.co.jp/archives/service/dramaticcreate'),
 ('tinmachine','TinMachine','company',['TinMachine'],'https://tinmachine.co.jp/release.html'),
 ('yonago_gainax','米子GAINAX','company',['米子GAINAX'],'https://blissbrain.co.jp/pm2rg/'),
 ('blissbrain','Bliss Brain','company',['Bliss Brain'],'https://blissbrain.co.jp/pm2rg/'),
 ('konami_de','Konami Digital Entertainment','company',['Konami Digital Entertainment','コナミデジタルエンタテインメント','株式会社コナミデジタルエンタテインメント'],'https://www.konami.com/corporate/en/history/index.html'),
 ('sharrock','SharRock','brand',['SharRock','Shar Rock','シャーロック'],'https://www.sekonic.co.jp/company/history/'),
]
SUBBRANDS = [
 ('silkys_wasabi','Silky’s Plus WASABI','silkys_plus',['Silky’s Plus WASABI']),
 ('silkys_a5','Silky’s Plus A5和牛','silkys_plus',['Silky’s Plus A5和牛']),
 ('silkys_dolce','Silky’s Plus DOLCE','silkys_plus',['Silky’s Plus DOLCE']),
 ('tiare','Tiare','jast',['Tiare']),('jast_purple','Purple（JAST期）','jast',['Purple（JAST期）']),
 ('angel_hearts','Angel Hearts','jast',['Angel Hearts']),('pride','pride','jast',['pride']),('jast_crest','クレスト（JAST）','jast',['クレスト（JAST）']),
 ('fairytale_ethix','FAIRYTALE ETHIX','fairytale',['FAIRYTALE ETHIX']),('fairytale_x','FAIRYTALE/X指定','fairytale',['FAIRYTALE/X指定']),
 ('fairytale_tsuki','月星組','fairytale',['月星組/フェアリーテール']),('fairytale_hana','花月組','fairytale',['花月組/フェアリーテール']),
 ('hulotte_roi','HULOTTE ROI','hulotte',['HULOTTE ROI','HULOTTE Roi','ユロットロワ']),
 ('yuzusoft_sour','ゆずソフトSOUR','yuzusoft',['ゆずソフトSOUR']),
 ('applique_imouto','あっぷりけ-妹-','applique',['あっぷりけ-妹-','あっぷりけ -妹-']),
 ('alice_blue','Alice Blue','alicesoft',['Alice Blue']),('alice_noir','AliceNoir','alicesoft',['AliceNoir']),
 ('minato_carnival','みなとカーニバル','minatosoft',['みなとカーニバル','Minato Carnival']),
 ('minato_carnival_world','みなとカーニバルWorld','minatosoft',['みなとカーニバルWorld']),
 ('mirai','mirai','hawkeye',['mirai']),('whale','ホエール','hawkeye',['ホエール','Whale']),
 ('microsoft_studios','Microsoft Studios','microsoft',['Microsoft Studios','Microsoft Game Studios']),
 ('xbox_game_studios','Xbox Game Studios','microsoft',['Xbox Game Studios','Xbox Game Studios Publishing']),
 ('microsoft_home','Microsoft Home','microsoft',['Microsoft Home'])]

def read(p): return json.loads((ROOT/p).read_text(encoding='utf-8'))
def canonical(x): return re.sub(r'\s+','',x.replace('’',"'").casefold())
def digest(x): return hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def render_json(d): return json.dumps(d,ensure_ascii=False,indent=2)+'\n'

def build():
 d=read('data/games.json'); coverage=read('data/company-coverage.json'); taxonomy=read('data/taxonomy.json'); companies={c['id']:c for c in coverage['companies']}
 review_batches=[read(PRIORITY_REVIEW),read(FOLLOWUP_REVIEW),read(THIRD_REVIEW),read(FOURTH_REVIEW),read(CREATOR_A_REVIEW),read(CREATOR_A2_REVIEW),read(CREATOR_A3_REVIEW),read(CREATOR_A4_REVIEW),read(CREATOR_A5_REVIEW),read(CREATOR_A6_REVIEW),read(CREATOR_B1_REVIEW),read(CREATOR_B2_REVIEW),read(CREATOR_B3_REVIEW),read(CREATOR_C1_REVIEW),read(CREATOR_C2_REVIEW),read(CREATOR_C3_REVIEW),read(CREATOR_C4_REVIEW),read(CREATOR_D1_REVIEW),read(CREATOR_D2_REVIEW),read(CREATOR_D3_REVIEW),read(CREATOR_E1_REVIEW),read(CREATOR_E2_REVIEW),read(CREATOR_E3_REVIEW),read(CREATOR_F1_REVIEW),read(CREATOR_F2_REVIEW),read(CREATOR_G1_REVIEW),read(CREATOR_G2_REVIEW),read(CREATOR_G3_REVIEW),read(CREATOR_H1_REVIEW),read(CREATOR_H2_REVIEW),read(CREATOR_H3_REVIEW),read(CREATOR_I1_REVIEW),read(CREATOR_I2_REVIEW),read(CREATOR_I3_REVIEW),read(CREATOR_I4_REVIEW),read(CREATOR_J1_REVIEW),read(CREATOR_K1_REVIEW),read(CREATOR_K2_REVIEW),read(CREATOR_K3_REVIEW),read(CREATOR_L1_REVIEW),read(CREATOR_L2_REVIEW),read(CREATOR_L3_REVIEW),read(CREATOR_M1_REVIEW),read(CREATOR_M2_REVIEW),read(CREATOR_M3_REVIEW),read(CREATOR_M4_REVIEW),read(CREATOR_M5_REVIEW),read(CREATOR_M6_REVIEW),read(CREATOR_N1_REVIEW),read(CREATOR_N2_REVIEW),read(CREATOR_N3_REVIEW),read(CREATOR_N4_REVIEW),read(CREATOR_N5_REVIEW),read(CREATOR_O1_REVIEW),read(CREATOR_P1_REVIEW),read(CREATOR_P2_REVIEW),read(CREATOR_P3_REVIEW),read(CREATOR_Q1_REVIEW),read(CREATOR_R1_REVIEW),read(CREATOR_R2_REVIEW),read(CREATOR_S1_REVIEW),read(CREATOR_S2_REVIEW),read(CREATOR_S3_REVIEW),read(CREATOR_S4_REVIEW)]
 identity_reviews={x['entityId']:x for batch in review_batches for x in batch['identityCorrections']}
 assert len(identity_reviews)==sum(len(batch['identityCorrections']) for batch in review_batches),'重复的主体订正'
 entities={}; aliases={}; dossiers=[]; relations=[]; credits=[]; memberships=[]; reviews=[]; placements=[]; names_review=[]; conflicts=[]
 def add_entity(eid,name,kind,names,source,basis='existingDossier',note=''):
  eid='entity-'+eid
  if eid not in entities:entities[eid]={'id':eid,'name':name,'type':kind,'aliases':list(dict.fromkeys([name,*names])),'sources':[source],'verification':basis,'historyNote':note,'dates':[]}
  for n in [name,*names]:aliases[canonical(n)]=eid
  return eid
 for cid,c in companies.items():
  eid='sierra_company' if cid in {'sierra','sierra_on_line'} else cid
  kind='brand' if cid in BRANDS else 'team' if cid=='novect' else 'publication' if cid=='comptiq' else 'unknown' if cid in {'falcom','te_soft','banpresto'} else 'company'
  name='Sierra On-Line（原On-Line Systems）' if cid in {'sierra','sierra_on_line'} else c['name']
  ident=add_entity(eid,name,kind,NAMES.get(cid,[]),c['source'],note=c['publisherNote'])
  dossiers.append({'id':cid,'name':c['name'],'dossierType':'history' if cid in HISTORIES else kind,'entityIds':[ident],'scope':c['scope'],'sources':[c['source']],'firstYearBasis':'关联主库作品最早原作首发年','firstYear':min((w['firstYear'] for w in d['works'] if w['id'] in c['workIds']),default=None)})
 for eid,name,kind,names,source in EXTRAS:add_entity(eid,name,kind,names,source,'sourceReviewed')
 # Publisher brand/company homographs remain distinct. Raw AQUAPLUS alone is a publishing-brand signature.
 aliases[canonical('AQUAPLUS')]='entity-aquaplus_brand'
 aliases[canonical('Nitroplus')]='entity-nitroplus_brand';aliases[canonical('NITRO PLUS')]='entity-nitroplus_brand'
 for eid,name,parent,names in SUBBRANDS:
  add_entity(eid,name,'brand',names,companies[parent]['source'],note='历史品牌／子品牌署名独立保存；不等于法人公司。')
  relations.append({'from':'entity-'+eid,'to':'entity-'+parent,'type':'brandFamily','period':{'from':None,'to':None,'precision':'unknown'},'status':'existingDossier','source':companies[parent]['source'],'note':'既有专题的品牌家族关系，未知时段不外推为历年经营归属。'})
 def relation(child,parent,source,note,status='sourceReviewed',start=None):
  relations.append({'from':'entity-'+child,'to':'entity-'+parent,'type':'operatedBy','period':{'from':start,'to':None,'precision':'year' if start else 'unknown','openEnd':'notAsserted'},'status':status,'source':source,'note':note})
 relation('key','visualarts','https://visual-arts.jp/blog_2024_1/','公司与品牌分开；不由当前运营关系反推所有历史版本的合同发行方。')
 relation('leaf','aquaplus',companies['leaf']['source'],'依既有品牌档案记录；起止时间未核。','existingDossier')
 relation('aquaplus_brand','aquaplus','https://aquaplus.jp/','公司与对外品牌同名，使用不同实体ID。')
 relation('aniplex_exe','aniplex','https://aniplex-exe.com/','小说游戏品牌与法人分开。')
 relation('alicesoft','champion_soft','https://www.alicesoft.com/outline/profile.html','Alicesoft品牌由Champion Soft经营；公司成立与品牌启用分开。',start=1989)
 relation('nitrochiral','nitroplus','https://www.nitroplus.co.jp/company/','子品牌独立，原署名不被公司别名吞并。')
 relation('nitroorigin','nitroplus','https://www.nitroplus.co.jp/company/','新品牌不追溯替换此前Nitroplus品牌署名。')
 relation('nitroplus_brand','nitroplus','https://www.nitroplus.co.jp/company/','公司与同名品牌分开。')
 for b in ['cocktailsoft','fairytale']:relation(b,'fandc',companies[b]['source'],'现有品牌关系；各时期经营主体另核，不倒填1980年代发行。','existingDossier')
 relation('5pb','mages','https://mages.co.jp/topics/ir/20190726/post-145','历史5pb.品牌关系；2019统一品牌说明不追溯覆盖原署名。')
 relation('dramaticcreate','hunex','https://www.hunex.co.jp/archives/service/dramaticcreate','发行品牌与法人分开，其他品牌作品不混入。')
 relation('silkys','elf',companies['silkys']['source'],'原品牌关系，不与Silky’s Plus合并。','existingDossier')
 relation('macadamia','db_soft',companies['macadamia']['source'],'历史品牌归属；法人起止另核。','existingDossier')
 relation('minatosoft','hawkeye',companies['hawkeye']['source'],'品牌活动起点不当作法人成立日。','existingDossier')
 relation('mirai','hawkeye','https://www.mirai-soft.net/guide.php','官方署名mirai（株式会社ホークアイ）。')
 # Preserve source-level alias distinctions; only use old aliases where they do not collapse a declared child brand.
 def resolve(raw,source):
  key=canonical(raw)
  if key in aliases:return aliases[key]
  previous=taxonomy['publisherAliases'].get(raw)
  if previous and canonical(previous) in aliases:
   target=aliases[canonical(previous)]; aliases[key]=target
   if raw not in entities[target]['aliases']:entities[target]['aliases'].append(raw)
   return target
  eid='entity-name-'+hashlib.sha256(raw.encode()).hexdigest()[:12]
  if eid not in entities:
   entities[eid]={'id':eid,'name':raw,'type':'unknown','aliases':[raw],'sources':[source],'verification':'unresolved','historyNote':'发行原文已保留；法人／品牌身份尚待核实。','dates':[]}
   reviewed=identity_reviews.get(eid)
   if reviewed:
    assert reviewed['status']=='sourceReviewed' and reviewed['rawName']==raw
    assert all(entities[eid][key]==value for key,value in reviewed['before'].items()),'主体旧值与独立订正记录不符'
    assert reviewed['type'] in {'company','team','brand','individual'} and reviewed['sources'] and reviewed['note']
    assert reviewed['type']!='brand' or reviewed.get('preserveReleaseRoles') is True,'身份核定不能自动改写旧发行职责'
    entities[eid].update(type=reviewed['type'],verification='sourceReviewed',historyNote=reviewed['note'])
    entities[eid]['sources']=list(dict.fromkeys([source,*reviewed['sources']]))
   else:
    names_review.append({'entityId':eid,'rawName':raw,'status':'pendingIdentity','source':source,'reason':'未以名称后缀推定法人或品牌；保留原发行署名。'})
  aliases[key]=eid;return eid
 def credit(eid,level,target,role,source,raw=None,status='existingCredit',note='',work_id=None):
  key=(eid,level,target,role)
  if key in credit_seen:return
  credit_seen.add(key)
  credits.append({'id':'credit-'+hashlib.sha256('|'.join(key).encode()).hexdigest()[:16],'entityId':eid,'targetType':level,'targetId':target,'workId':work_id or target,'role':role,'rawCredit':raw or entities[eid]['name'],'status':status,'source':source,'note':note,'territory':None})
 credit_seen=set(); allworks={w['id']:w for w in d['works']}; allreleases=list(d['platformReleases']); allcontents=list(d['contentVersions']); locations={w['id']:'main' for w in d['works']}
 for c in coverage['companies']:
  for field,loc in [('relatedGames','related'),('dossierOnlyWorks','bibliography')]:
   for w in c.get(field,[]):
    if w['id'] in allworks and digest(w)!=digest(allworks[w['id']]):conflicts.append({'id':w['id'],'dossierId':c['id'],'status':'pendingDuplicate'})
    allworks.setdefault(w['id'],w);locations.setdefault(w['id'],loc)
    if loc=='related':allreleases.extend(w['platformReleases']);allcontents.extend(w['contentVersions'])
 # Explicit splitting rules preserve raw brands that the legacy corporate index previously flattened.
 def release_entities(r):
  raw=r['publisher']; key=canonical(raw)
  if key in aliases:return [aliases[key]]
  if raw in taxonomy['nonCompanyCredits']:return []
  if raw in taxonomy['jointCredits']:return [resolve(n,r['source']) for n in taxonomy['jointCredits'][raw]]
  return [resolve(raw,r['source'])]
 for r in allreleases:
  eids=list(dict.fromkeys(release_entities(r)))
  for eid in eids:
   preserve_role=identity_reviews.get(eid,{}).get('preserveReleaseRoles',False)
   role='publishingBrand' if entities[eid]['type']=='brand' and not preserve_role else 'publisher'
   credit(eid,'release',r['id'],role,r['source'],r['publisher'],note='仅规范化此条历史发行署名；不据此推定开发职责。',work_id=r['workId'])
   if role=='publishingBrand' and r['year']==allworks[r['workId']]['firstYear'] and r['contentRelation']=='original':
    credit(eid,'work',r['workId'],'originalPublishingBrand',r['source'],r['publisher'],note='原作首发品牌署名；不等于该品牌独立完成全部程序、美术或剧本。')
 # Brand catalogues provide affiliation beyond whether a brand self-published a given port.
 for cid in ['key','leaf','innocent_grey','minori','august','toneworks','asaproject','sagaplanets','smee','favorite','cuffs','cube','sphere','palette','cabbage','madosoft','sprite','harukaze','sorahane','clochette']:
  c=companies[cid]
  for wid in c['workIds']:
   if cid=='leaf' and wid=='g159':continue # ToHeart2 was originally an AQUAPLUS work, Leaf only later content.
   credit('entity-'+cid,'work',wid,'productionBrand',c['source'],status='existingDossier',note='依据既有品牌目录登记；创作职责和实际发行分别列示。')
 # Key original production is explicitly scoped to its own main catalogue, not authorized/mobile related games.
 for wid in companies['key']['workIds']:credit('entity-key','work',wid,'originalProduction',companies['key']['source'],status='existingDossier',note='原作制作品牌；不把外部平台发行者当作原作创作者。')
 for wid,eids,src in [('g200',['frontwing','makura'],'https://aniplex-exe.com/news/?category=atri-mdm&id=52873'),('g201',['liarsoft'],'https://aniplex-exe.com/news/?category=aniplex-exe&id=52845')]:
  for eid in eids:credit('entity-'+eid,'work',wid,'coDeveloper' if wid=='g200' else 'originalProduction',src,status='sourceReviewed',note='官方制作署名；发行品牌另列。')
 for wid in [f'g{i}' for i in range(622,629)]:credit('entity-nitrochiral','work',wid,'productionBrand',companies['nitroplus']['source'],status='existingDossier',note='CHiRAL独立品牌，沿用既有单作资料，不倒归主品牌。')
 gainax_self=['g812','g813','g814','g815','g816','g817','g818','g819','g820','g821','g822','g824','g825','g826','g1277']
 for wid in gainax_self:credit('entity-gainax','work',wid,'originalProduction',allworks[wid]['source'],status='existingDossier',note='既有GAINAX核对档案明确本社原作制作；与授权作品分开。')
 for wid,role in [('g823','catalogueAssociation'),('g827','licensor'),('g828','licensor'),('g829','supervisor'),('g927','copyrightCredit'),('g1276','copyrightCredit')]:
  credit('entity-gainax','work',wid,role,allworks[wid]['source'],status='existingDossier',note='现有档案中的系列合作／授权／监修关系，不声称本社开发。')
 for r in allreleases:
  if r['workId'] in {'g200','g201'} and 'entity-imel' in release_entities(r):credit('entity-imel','release',r['id'],'portDeveloper','https://imel.co.jp/activity/',status='sourceReviewed',note='官方实绩的主机／手机移植开发；非原作剧本制作。',work_id=r['workId'])
 for cv in allcontents:
  if cv['workId']=='g821' and cv['firstYear']==2024:credit('entity-yonago_gainax','content',cv['id'],'addedAnimation','https://blissbrain.co.jp/pm2rg/',status='sourceReviewed',note='2024重制的新增动画，不是原GAINAX本社。',work_id='g821')
 # Apply independently sourced contributions; later-content development never becomes original-work production.
 reviewed_memberships={}
 for reviewed,audit in [(x,batch['audit']) for batch in review_batches for x in batch['creditAdditions']]:
  eid=reviewed['entityId'];wid=reviewed['workId'];cid=reviewed['dossierId']
  assert reviewed['status']=='sourceReviewed' and eid in entities and wid in allworks
  level=reviewed['targetType'];target=wid if level=='work' else reviewed.get('targetId')
  if level=='work':
   assert reviewed['role'] in {'coDeveloper','originalProduction','supervisor','productionBrand'}
   before_roles=reviewed.get('beforeWorkRoles',[])
  elif level=='release':
   assert reviewed['role']=='developer' and cid is None,'发行开发须独立限定发行ID，不能直接解除专题待核'
   release=next((r for r in allreleases if r['id']==target),None)
   assert release and release['workId']==wid,'发行开发追加必须命中同作品既有发行'
   before_roles=reviewed['beforeTargetRoles']
  else:
   assert level=='content' and reviewed['role']=='developer' and cid is None,'后发内容开发须独立限定内容ID，不能直接解除专题待核'
   content=next((cv for cv in allcontents if cv['id']==target),None)
   assert content and content['workId']==wid and content['basis']=='added','内容开发追加必须命中同作品既有增补内容'
   before_roles=reviewed['beforeTargetRoles']
  assert locations[wid]==reviewed['expectedPlacement']
  current_roles=sorted({x['role'] for x in credits if x['entityId']==eid and x['targetType']==level and x['targetId']==target})
  assert current_roles==before_roles,'目标职责旧值与独立追加记录不符'
  assert (eid,level,target,reviewed['role']) not in credit_seen,'已存在职责不能由追加记录覆盖'
  if cid:
   assert wid in [*companies[cid]['workIds'],*[w['id'] for field in ['relatedGames','dossierOnlyWorks'] for w in companies[cid].get(field,[])]]
   assert eid in next(d['entityIds'] for d in dossiers if d['id']==cid)
   assert not any(x['entityId']==eid and x['workId']==wid for x in credits),'专题解除待核须单独审核旧职责'
   assert reviewed['before']=={'roles':['catalogueAssociation'],'group':'unresolved','status':'pendingRole'}
   assert (cid,wid) not in reviewed_memberships
  credit(eid,level,target,reviewed['role'],reviewed['source'],raw=reviewed['rawCredit'],status='sourceReviewed',note=reviewed['note'],work_id=wid)
  credits[-1].update(reviewId=reviewed['reviewId'],reviewRecord=audit)
  if cid:reviewed_memberships[(cid,wid)]=reviewed
 assert set(identity_reviews)<=entities.keys(),'主体订正记录未命中既有身份'
 # Dossier memberships are separate from production assertions. Every existing member remains present.
 bywork=defaultdict(list)
 for x in credits:bywork[x['workId']].append(x)
 dossier_lookup={x['id']:x for x in dossiers}
 for c in coverage['companies']:
  subject=set(dossier_lookup[c['id']]['entityIds'])
  for wid in [*c['workIds'],*[w['id'] for w in c.get('relatedGames',[])],*[w['id'] for w in c.get('dossierOnlyWorks',[])]]:
   roles=sorted({x['role'] for x in bywork[wid] if x['entityId'] in subject}) or ['catalogueAssociation']
   if 'originalProduction' in roles or 'productionBrand' in roles or 'developer' in roles:group='original'
   elif 'coDeveloper' in roles:group='cooperation'
   elif any(x in roles for x in ['publisher','publishingBrand','originalPublishingBrand','portDeveloper']):group='release'
   elif any(x in roles for x in ['licensor','supervisor','copyrightCredit']):group='licensed'
   else:group='unresolved'
   membership_source=reviewed_memberships.get((c['id'],wid),{}).get('source',c['source'])
   memberships.append({'dossierId':c['id'],'workId':wid,'placement':locations[wid],'roles':roles,'group':group,'source':membership_source,'status':'pendingRole' if group=='unresolved' else 'existingEvidence'})
 for wid,w in allworks.items():
  loc=locations[wid]
  record={'workId':wid,'placement':loc,'narrativeAssessment':'notReassessed','decision':'retainExistingPlacement','source':w['source'],'reason':'本轮为实体与关系迁移，沿用既有收录；不从类型标签或互动方式自动推定叙事主次。','interactionModes':w['interactionModes']}
  placements.append(record)
  if loc!='main':reviews.append({**record,'status':'needsNarrativeEvidence' if loc=='related' else 'existingScopeRestriction','nextStep':'逐作比较叙事与系统主次；仅有ADV／RPG或IP标签不足以转入主库。' if loc=='related' else '区分原有范围限制与资料不足；输入标签本身不触发自动增删。'})
 # Every alias is inventoried, including compatibility-only raw spellings not present in current releases.
 mapping=[]
 for raw in sorted({r['publisher'] for r in allreleases} | set(taxonomy['publisherAliases']) | set(taxonomy['jointCredits'])):
  candidates=[r for r in allreleases if r['publisher']==raw]
  if candidates:ids=release_entities(candidates[0])
  elif canonical(raw) in aliases:ids=[aliases[canonical(raw)]]
  elif raw in taxonomy['publisherAliases'] and canonical(taxonomy['publisherAliases'][raw]) in aliases:ids=[aliases[canonical(taxonomy['publisherAliases'][raw])]]
  else:ids=[]
  mapping.append({'rawName':raw,'entityIds':ids,'legacyCanonical':taxonomy['publisherAliases'].get(raw),'status':'mapped' if ids else 'pendingOrNoncommercial','source':candidates[0]['source'] if candidates else None})
 baseline={'baseCommit':BASE,'preservedFiles':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['data/games.json','data/company-coverage.json','data/taxonomy.json','data/gameplay-catalogues.json']},'counts':{'works':len(d['works']),'contentVersions':len(d['contentVersions']),'platformReleases':len(d['platformReleases']),'dossiers':len(companies)},'relatedRecordCount':sum(len(c.get('relatedGames',[])) for c in companies.values()),'bibliographyRecordCount':sum(len(c.get('dossierOnlyWorks',[])) for c in companies.values())}
 date_facts={
  'entity-champion_soft':('established','1983-01','month',companies['champion_soft']['source']),
  'entity-alicesoft':('brandStarted','1989','year',companies['champion_soft']['source']),
  'entity-fandc':('established','1997-03-31','day','https://fandc.co.jp/extra/corporate'),
  'entity-minatosoft':('brandActivityStarted','2006','year',companies['minatosoft']['source']),
  'entity-gaina':('renamedBentenFilm','2025-08-01','day',companies['gaina']['source']),
  'entity-sierra_company':('renamedSierraOnLine','1982','year',companies['sierra_on_line']['source'])}
 for eid,(kind,value,precision,src) in date_facts.items():entities[eid]['dates'].append({'kind':kind,'value':value,'precision':precision,'source':src,'status':'existingEvidence'})
 apply_names(entities,dossiers)
 model={'schemaVersion':1,'updated':DATE,'typeLabels':TYPE_LABELS,'roleLabels':ROLE_LABELS,'entities':list(entities.values()),'relations':relations,'dossiers':dossiers,'displayNames':{raw:display_name(raw) for raw in DISPLAY_NAMES},'policy':'实体、参与角色、收录位置相互独立；不以当前品牌归属倒填历史署名。'}
 existing_baseline=ROOT/'data/entity-migration-baseline.json'
 if existing_baseline.exists():
  baseline=read('data/entity-migration-baseline.json')
  for field in ['works','contentVersions','platformReleases']:
   current={x['id']:digest(x) for x in d[field]}
   assert all(current.get(wid)==value for wid,value in baseline['objects'][field].items()),'既有记录变化需独立订正审核；不能重新生成覆盖基线'
 else:
  baseline['objects']={field:{x['id']:digest(x) for x in d[field]} for field in ['works','contentVersions','platformReleases']}
  baseline['originalDossiers']={cid:{'workIds':c['workIds'],'relatedIds':[w['id'] for w in c.get('relatedGames',[])],'bibliographyIds':[w['id'] for w in c.get('dossierOnlyWorks',[])]} for cid,c in companies.items()}

 return {'data/entities.json':model,'data/credits.json':{'schemaVersion':1,'updated':DATE,'credits':credits,'dossierMemberships':memberships},'data/work-classification.json':{'schemaVersion':1,'updated':DATE,'placements':placements,'reviewQueue':reviews,'policy':'保留既有位置；未重新核定叙事主次，不自动转入主库。'},'data/entity-migration-review.json':{'updated':DATE,'nameMappings':mapping,'pendingIdentities':names_review,'pendingMembershipCount':sum(x['status']=='pendingRole' for x in memberships),'identityConflicts':conflicts,'aliasPolicy':'旧taxonomy别名仅作兼容归档；新实体索引保留子品牌，所有实体关系单独记录。'},'data/entity-migration-baseline.json':baseline}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for path,value in build().items():
  output=render_json(value);target=ROOT/path
  if args.check:assert target.read_text()==output,f'{path} 未同步'
  else:target.write_text(output,encoding='utf-8')
  print(path)

if __name__=='__main__':main()
