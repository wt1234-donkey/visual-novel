import {loadEffectiveCatalogueSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {gunzipSync} from 'node:zlib';
import {normalizeFilterText,manufacturerKey,gameplayKeys} from '../basic-catalogue-filters.mjs';
import {normalizeLanguage,searchValues} from '../basic-combined-search.mjs';
import {CREATOR_NAME_FIELDS,projectWork} from '../work-edit-model.mjs';
import {MAKER_ROLES} from '../discovery-model.mjs';

const ifdb='ifdb-append-source-20261104.json.gz.b64',vndb='vndb-right-only-source-20261103.json.gz.b64';
const knownName=v=>typeof v==='string'&&v.trim()&&!/^(unknown|anonymous|n\/a|待核实|未知|匿名|未核实|—|-)$/i.test(v.trim());
const asList=v=>Array.isArray(v)?v:typeof v==='string'?[v]:[];
const normalized=values=>[...new Set(values.filter(knownName).map(normalizeFilterText))];
const tokens=v=>asList(v).flatMap(searchValues);
const creators=v=>tokens(v).flatMap(x=>x.split(/\s+(?:and|&)\s+/i)).filter(Boolean);
const group=(rows,key)=>{
 const out=new Map();
 for(const row of rows){const value=row[key];if(!out.has(value))out.set(value,[]);out.get(value).push(row);}
 return out;
};
const empty=v=>v===undefined||v===null||(Array.isArray(v)&&!v.length);
const compact=row=>Object.fromEntries(Object.entries(row).filter(([,v])=>!empty(v)));
const sourceThemes=new Map([['science fiction','科幻'],['sci-fi','科幻'],['sf','科幻'],['fantasy','奇幻'],['historical','历史'],['history','历史'],['mystery','悬疑'],['detective','推理'],['war','战争'],['crime','犯罪'],['post-apocalyptic','末世'],['cyberpunk','赛博朋克'],['supernatural','超自然']]);
const platformNames={win:'Windows',lin:'Linux',mac:'Mac',ios:'iOS',and:'Android',swi:'Nintendo Switch',swi2:'Nintendo Switch 2',ns:'Nintendo Switch',psp:'PlayStation Portable',psv:'PlayStation Vita',ps1:'PlayStation',ps2:'PlayStation 2',ps3:'PlayStation 3',ps4:'PlayStation 4',ps5:'PlayStation 5',nes:'NES',sfc:'Super Famicom',gba:'Game Boy Advance',gbc:'Game Boy Color',nds:'Nintendo DS',n3d:'Nintendo 3DS',drc:'Dreamcast',xb3:'Xbox 360',xbo:'Xbox One',xxs:'Xbox Series X/S',web:'Web'};
const platformValues=platform=>normalized([platform,platformNames[normalizeFilterText(platform)]]);

const graphicSubcategories=new Set(['图文选项／调查','图文指令','光盘图文冒险','输入式图文冒险']);
const textSubcategories=new Set(['纯文本指令','输入式叙事冒险']);
function documentedGameplay(work){
 const modes=(work.interactionModes||[]).filter(mode=>mode!=='待核实').flatMap(gameplayKeys).filter(key=>!key.startsWith('custom:'));
 const presentation=graphicSubcategories.has(work.subcategory)?'graphic-adventure':
  textSubcategories.has(work.subcategory)?'interactive-fiction':
  ['视觉小说','互动动画'].includes(work.category)?gameplayKeys(work.category)[0]:null;
 return [...new Set(presentation?[presentation,...modes]:modes)];
}

export function buildAdvancedRows(root,rows,registry,main,supplement,history,catalogueSnapshot=null){
 const read=name=>JSON.parse(readFileSync(join(root,'data',name),'utf8'));
 const snapshot=name=>JSON.parse(gunzipSync(Buffer.from(readFileSync(join(root,'data',name),'utf8'),'base64')));
 const effective=loadEffectiveCatalogueSync(root),companies=effective.coverage.companies;
 const dossierWorks=companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])]);
 const formal=catalogueSnapshot?.formalById||new Map([...supplement.works,...main.works].map(w=>[w.id,projectWork(w,history)]));
 const catalogue=new Map([...dossierWorks.map(w=>[w.id,projectWork(w,history)]),...formal]);
 const entities=read('entity-catalogue.json'),entityById=new Map(entities.model.entities.map(e=>[e.id,e]));
 const organization=group(entities.credits,'workId');
 const namesFor=credit=>{const e=entityById.get(credit.entityId);return [e?.name,...(e?.aliases||[]),credit.rawCredit];};
 const personData=read('creator-credits.json'),personById=new Map(personData.people.map(p=>[p.id,p])),credits=group(personData.credits,'workId');
 const releases=group([...(effective.supplement.platformReleases||[]),...(effective.main.platformReleases||[])],'workId');
 const contents=group([...(effective.supplement.contentVersions||[]),...(effective.main.contentVersions||[])],'workId');
 const editorial=read('discovery-editorial.json').works;
 const releaseRegions=read('basic-release-regions.json');
 const regions=new Map();
 for(const {names,region} of read('basic-manufacturer-regions.json').entries)for(const name of names){
  const key=manufacturerKey(name);regions.set(key,regions.has(key)&&regions.get(key)!==region?null:region);
 }
 const registryById=new Map(registry.works.map(w=>[w.id,w]));
 const ifdbRows=new Map(snapshot(ifdb).map(r=>[r.IFDB_TUID,r]));
 const vndbRows=new Map(snapshot(vndb).map(r=>[r.vID,r]));
 const indexed={},gameplayBySlot=new Map();
 for(const [slot,row] of rows.entries()){
  const entry=registryById.get(row.matchedWorkId)||{};
  const w=catalogue.get(row.linkedRecordId||entry.linkedRecordId)||catalogue.get(row.matchedWorkId);
  if(w)gameplayBySlot.set(slot,documentedGameplay(w));
  const ifid=entry.sourceTuid||entry.sourceRefs?.find(ref=>ref.startsWith('ifdb:'))?.slice(5);
  const ifRow=ifdbRows.get(ifid);
  const vIds=[...new Set((entry.sourceRefs||[]).filter(ref=>/^vndb:v\d+$/.test(ref)).map(ref=>ref.slice(5)))];
  const vnRow=vIds.length===1?vndbRows.get(vIds[0]):undefined;
  const meta=editorial[w?.id]||{};
  const org=organization.get(w?.id)||[];
  const personNames=(credits.get(w?.id)||[]).flatMap(c=>{
   const p=personById.get(c.personId);return [p?.name,p?.alias];
  });
  const makerNames=org.filter(c=>MAKER_ROLES.has(c.role)&&['work','content'].includes(c.targetType)).flatMap(namesFor);
  const developerNames=org.filter(c=>['developer','coDeveloper','portDeveloper'].includes(c.role)).flatMap(namesFor);
  const sourceDevelopers=[...tokens(vnRow?.['开发者（VNDB关联）']),...tokens(entry.sourceDeveloperAssociations)];
  const regionNames=makerNames.length?makerNames:sourceDevelopers;
  const duration=Number(vnRow?.['平均游玩分钟']);
  const contentList=w&&(contents.get(w.id)||w.contentVersions||[]);
  const workReleases=(w&&(releases.get(w.id)||w.platformReleases)||[]).map(r=>compact({
   platform:platformValues(r.platform),releaseYear:r.year,releaseRegion:releaseRegions[r.id]||[],
   publisher:normalized([r.publisher,...(r.publisherCompanies||[]),...org.filter(c=>c.role==='publisher'&&c.targetType==='release'&&c.targetId===r.id).flatMap(namesFor)]),
   voice:normalized([r.voice]),contentRelation:[r.contentRelation].filter(Boolean)
  }));
  // Snapshot platforms are availability leads only; they carry no assumed region or release year.
  for(const platform of tokens(vnRow?.['平台']))workReleases.push({platform:platformValues(platform)});
  for(const [platform,year] of Object.entries(entry.sourcePlatformYears||{}))if(Number.isInteger(year))workReleases.push({platform:platformValues(platform),releaseYear:year});
  const record=compact({
   creator:normalized([...personNames,...Object.keys(CREATOR_NAME_FIELDS).flatMap(key=>w?.[key]||[]),...creators(entry.sourceAuthor||ifRow?.['作者或创作主体'])]),
   character:normalized(w?.characters||[]),series:normalized(asList(ifRow?.['系列'])),
   language:[...new Set([...tokens(entry.sourceLanguage),...tokens(ifRow?.['语言代码']),...tokens(vnRow?.['原始语言']),...tokens(vnRow?.['可用语言'])].filter(knownName).map(normalizeLanguage))],
   duration:Number.isFinite(duration)&&duration>0?duration:undefined,
   contentCount:contentList?.length?new Set(contentList.map(c=>c.id)).size:undefined,
   theme:normalized([...asList(meta.theme),...tokens(entry.sourcePlotTags),...asList(w?.genre).flatMap(v=>v.split(/[／/、；;,，]/)),...tokens(entry.sourceGenre)].flatMap(v=>[v,sourceThemes.get(normalizeFilterText(v))])),
   position:normalized(asList(meta.position)),structure:normalized(asList(meta.structure)),interaction:normalized(w?.interactionModes||[]),
   brand:normalized(org.filter(c=>['productionBrand','originalPublishingBrand','publishingBrand'].includes(c.role)).flatMap(namesFor)),
   developer:normalized([...developerNames,...sourceDevelopers]),participant:normalized(org.flatMap(namesFor)),
   productionRegion:[...new Set(regionNames.map(name=>regions.get(manufacturerKey(name))).filter(Boolean))],releases:workReleases
  });
  if(Object.keys(record).length)indexed[slot]=record;
 }
 return {indexed,gameplayBySlot};
}
