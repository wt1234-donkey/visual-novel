// Generate the public browse/search index and on-demand detail shards during Pages packaging.
import {writeFileSync,mkdirSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
export {assembleBasicRows,assembleHomeRows} from '../src/application/catalogue/snapshot.mjs';
import {normalizeBasicQuery} from '../basic-catalogue-index.mjs';
import {buildAdvancedRows} from './build_basic_advanced_index.mjs';


function packBasicRows(works,gameplayBySlot){
 const groups=[],gameplay=[],statuses=[];
 const intern=values=>{
  const keys=new Map();
  return value=>{
   if(!keys.has(value)){keys.set(value,values.length);values.push(value);}
   return keys.get(value);
  };
 };
 const groupKey=intern(groups),gameplayKey=intern(gameplay),statusKey=intern(statuses);
 const rows=works.map((w,slot)=>{
  const row=[w.id,w.matchedWorkId||null,w.title,w.year,groupKey(w.group),gameplayKey(w.gameplay),statusKey(w.status)];
  const optional=[w.aliases?.length?w.aliases:null,w.groups?.length?w.groups.map(groupKey):null,w.plotStyles?.length?w.plotStyles:null,w.plotTags||null,gameplayBySlot.get(slot)?.length?gameplayBySlot.get(slot):null,w.formalTitle?{title:w.formalTitle,override:w.formalOverride,at:w.formalAt}:null];
  while(optional.length&&!optional.at(-1))optional.pop();
  return row.concat(optional);
 });
 return {rows,groups,gameplay,statuses};
}


export function buildBasicWebIndex(root,output,revision){
 const {snapshot,inputs,sourceLease}=loadCatalogueSnapshot(root);
 const {registry,main,supplement,history}=inputs;
 const {sourceRows:basic,home}=snapshot;
 const dir=join(output,'data','basic-web'),version=join(dir,revision),shardSize=250,assets={};
 mkdirSync(version,{recursive:true});
 const save=(path,data,compressed=false)=>{
  const json=JSON.stringify(data)+'\n';
  writeFileSync(path,json);
  if(path.startsWith(version+'/'))assets[path.slice(version.length+1)]={sha:createHash('sha1').update('blob '+Buffer.byteLength(json)+'\0').update(json).digest('hex')};
  if(compressed)writeFileSync(path+'.gz',gzipSync(json,{level:9}));
 };
 const shards=(kind,rows,project)=>{
  for(let slot=0;slot<rows.length;slot+=shardSize)
   save(join(version,kind+'-'+slot/shardSize+'.json'),rows.slice(slot,slot+shardSize).map(project));
 };
 const {indexed,gameplayBySlot}=buildAdvancedRows(root,basic,registry,main,supplement,history,snapshot);
 save(join(version,'basic-index.json'),packBasicRows(basic,gameplayBySlot),true);
 save(join(version,'basic-advanced.json'),indexed,true);
 const advancedCoverage={series:0,language:0,duration:0,releaseRegion:0};
 for(const item of Object.values(indexed)){
  for(const field of ['series','language','duration'])if(item[field])advancedCoverage[field]++;
  if(item.releases?.some(release=>release.releaseRegion))advancedCoverage.releaseRegion++;
 }
 shards('basic',basic,({source,gameplayNote,reason,linkedRecordId,plotTagEvidence})=>({source:source||'',gameplayNote,reason,linkedRecordId,plotTagEvidence}));
 save(join(version,'home-search.json'),home.rows.map(w=>normalizeBasicQuery([w.title,...(w.aliases||[]),w.group,...(w.sourceRefs||[])].join(' '))),true);
 shards('home',home.rows,({title,aliases,firstYear,gameplay,group,source,mainPlacement})=>({title,aliases,firstYear,gameplay,group,source,mainPlacement}));
 const {promotedBasic,promotedDossier,existingComplete}=registry.summary;
 save(join(version,'identity-review.json'),{candidates:snapshot.identityCandidates,issues:snapshot.issues});
 save(join(dir,'manifest.json'),{schema:1,revision,shardSize,sourceLease,assets,basic:{total:basic.length,promotedBasic,promotedDossier,existingComplete,advancedCoverage},
  home:{total:home.rows.length,excluded:home.excluded},
  catalogue:{schemaVersion:snapshot.schemaVersion,dataRevision:snapshot.revision,identityCandidates:snapshot.identityCandidates.length,journal:snapshot.journal}});
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const [root,output,revision]=process.argv.slice(2);
 buildBasicWebIndex(root,output,revision);
}
