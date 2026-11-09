// Generate the public browse/search index and on-demand detail shards during Pages packaging.
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {gzipSync} from 'node:zlib';
import {nameKey,projectRegistry,validateStore} from '../basic-catalogue-model.mjs';
import {compareBasicOrder,normalizeBasicQuery} from '../basic-catalogue-index.mjs';
import {applyWorkEdits} from '../work-edit-model.mjs';

const registryPath='main-adv-rpg-works-20261031.json';
export function assembleBasicRows(registry,initial,batches){
 const byIndex=new Map(registry.works.map(w=>[w.indexId,w]));
 const holding=new Set(registry.identityReview.map(w=>w.indexId));
 const rows=initial.map(w=>{
  const identity=byIndex.get(w.id);
  const placement=identity?.mainPlacement;
  const status=holding.has(w.id)?'identity-review':
   ['promoted-basic','promoted-dossier'].includes(placement)?placement:w.status;
  return {...w,status,matchedWorkId:identity?.id||w.matchedWorkId,linkedRecordId:identity?.linkedRecordId,
   ...(identity?.plotTags?{plotTags:identity.plotTags}:{}),...(identity?.plotStyles?{plotStyles:identity.plotStyles}:{}),
   ...(identity?.plotTagEvidence?{plotTagEvidence:identity.plotTagEvidence}:{})};
 });
 const byMatched=new Map(rows.filter(w=>w.matchedWorkId).map(w=>[w.matchedWorkId,w]));
 const nameYears=new Set(rows.map(w=>nameKey(w.title)+'|'+w.year));
 for(const [batch,records] of batches){
  for(const r of records){
   const key=nameKey(r.title)+'|'+r.year;
   const canonical=r.registryId&&byMatched.get(r.registryId);
   if(canonical){
    canonical.aliases=[...new Set([...(canonical.aliases||[]),r.title,...(r.aliases||[])])].filter(t=>t!==canonical.title);
    canonical.groups=[...new Set([...(canonical.groups||[]),canonical.group,r.group])];
    canonical.gameplayNote=canonical.gameplayNote||r.gameplayNote;
    continue;
   }
   if(nameYears.has(key))continue;
   const status=r.status==='existing-complete'?'main-linked':
    ['linked-existing-registry','linked-existing-full-or-dossier'].includes(r.status)?'main-registry-linked':r.status;
   const row={...r,id:batch+'-'+key,matchedWorkId:r.registryId,status};
   rows.push(row);
   if(row.matchedWorkId)byMatched.set(row.matchedWorkId,row);
   nameYears.add(key);
  }
 }
 const representedIds=new Set(rows.flatMap(r=>[r.matchedWorkId,r.registryId].filter(Boolean)));
 const representedIndexIds=new Set(rows.map(r=>r.id));
 for(const w of registry.works){
  const key=nameKey(w.title)+'|'+w.firstYear;
  if(representedIds.has(w.id)||representedIndexIds.has(w.indexId)||(w.intakePolicy!=='append-without-deduplication'&&nameYears.has(key)))continue;
  rows.push({
   id:w.indexId,matchedWorkId:w.id,title:w.title,aliases:w.aliases||[],year:w.firstYear,
   gameplay:w.gameplay||'玩法待核',gameplayNote:w.gameplayNote,group:w.group||'来源关联待核',
   plotStyles:w.plotStyles,plotTags:w.plotTags,plotTagEvidence:w.plotTagEvidence,linkedRecordId:w.linkedRecordId,source:w.source,
   status:w.mainPlacement==='existing-complete'?'main-linked':w.mainPlacement,
   reason:w.intakePolicy==='append-without-deduplication'?'未去重导入 · 来源状态：'+(w.sourceDevelopmentStatus||'未提供'):''
  });
  representedIds.add(w.id);representedIndexIds.add(w.indexId);nameYears.add(key);
 }
 return rows.sort(compareBasicOrder);
}

function packBasicRows(works){
 const groups=[],gameplay=[],statuses=[];
 const intern=values=>{
  const keys=new Map();
  return value=>{
   if(!keys.has(value)){keys.set(value,values.length);values.push(value);}
   return keys.get(value);
  };
 };
 const groupKey=intern(groups),gameplayKey=intern(gameplay),statusKey=intern(statuses);
 const rows=works.map(w=>{
  const row=[w.id,w.matchedWorkId||null,w.title,w.year,groupKey(w.group),gameplayKey(w.gameplay),statusKey(w.status)];
  const optional=[w.aliases?.length?w.aliases:null,w.groups?.length?w.groups.map(groupKey):null,w.plotStyles?.length?w.plotStyles:null,w.plotTags||null];
  while(optional.length&&!optional.at(-1))optional.pop();
  return row.concat(optional);
 });
 return {rows,groups,gameplay,statuses};
}

export function assembleHomeRows(registry,store,fullWorks){
 const fullIds=new Set(fullWorks.map(w=>w.id));
 const fullNames=new Set(fullWorks.flatMap(w=>[w.title,w.originalTitle,w.chineseTitle,...(w.titleAliases||[])]
  .filter(Boolean).map(n=>nameKey(n)+'|'+w.firstYear)));
 const projected=projectRegistry(registry,store).works;
 const rows=projected.filter(w=>{
  if(w.mainPlacement==='existing-complete'||(w.linkedRecordId&&fullIds.has(w.linkedRecordId)))return false;
  return w.intakePolicy==='append-without-deduplication'||
   ![w.title,...(w.aliases||[])].some(n=>fullNames.has(nameKey(n)+'|'+w.firstYear));
 });
 rows.sort(compareBasicOrder);
 return {rows,excluded:projected.length-rows.length};
}

export function buildBasicWebIndex(root,output,revision){
 const read=name=>JSON.parse(readFileSync(join(root,'data',name),'utf8'));
 const registry=read(registryPath);
 const index=read('adv-rpg-minimal-index-20261031.json');
 const batches=[['batch2','adv-rpg-next-studio-review-20261031.json'],['batch3','adv-rpg-round3-review-20261031.json']];
 const basic=assembleBasicRows(registry,index.records,batches.map(([id,path])=>[id,read(path).records]));
 const full=new Map([...read('non-rpg-creator-supplement-20261030.json').works,...read('games.json').works].map(w=>[w.id,w]));
 const {works}=applyWorkEdits({works:[...full.values()]},read('work-edit-history.json'));
 const home=assembleHomeRows(registry,validateStore(read('basic-catalogue-edits.json')),works);
 const dir=join(output,'data','basic-web'),version=join(dir,revision),shardSize=250;
 mkdirSync(version,{recursive:true});
 const save=(path,data,compressed=false)=>{
  const json=JSON.stringify(data)+'\n';
  writeFileSync(path,json);
  if(compressed)writeFileSync(path+'.gz',gzipSync(json,{level:9}));
 };
 const shards=(kind,rows,project)=>{
  for(let slot=0;slot<rows.length;slot+=shardSize)
   save(join(version,kind+'-'+slot/shardSize+'.json'),rows.slice(slot,slot+shardSize).map(project));
 };
 save(join(version,'basic-index.json'),packBasicRows(basic),true);
 shards('basic',basic,({source,gameplayNote,reason,linkedRecordId,plotTagEvidence})=>({source:source||'',gameplayNote,reason,linkedRecordId,plotTagEvidence}));
 save(join(version,'home-search.json'),home.rows.map(w=>normalizeBasicQuery([w.title,...(w.aliases||[]),w.group,...(w.sourceRefs||[])].join(' '))),true);
 shards('home',home.rows,({title,aliases,firstYear,gameplay,group,source,mainPlacement})=>({title,aliases,firstYear,gameplay,group,source,mainPlacement}));
 const {promotedBasic,promotedDossier,existingComplete}=registry.summary;
 save(join(dir,'manifest.json'),{schema:1,revision,shardSize,basic:{total:basic.length,promotedBasic,promotedDossier,existingComplete},
  home:{total:home.rows.length,excluded:home.excluded}});
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const [root,output,revision]=process.argv.slice(2);
 buildBasicWebIndex(root,output,revision);
}
