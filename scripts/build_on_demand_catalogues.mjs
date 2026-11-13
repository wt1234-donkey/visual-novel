import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {gzipSync} from 'node:zlib';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {loadEffectiveInputsSync,sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {readJsonFileSync} from '../src/infrastructure/filesystem/registry.mjs';
import {buildEffectiveCatalogue,mergeFormalDatasets,projectBasicSources} from '../src/domain/catalogue/effective.mjs';
import {projectRegistry,validateStore} from '../basic-catalogue-model.mjs';
import {scanRegistry} from '../bulk-import-model.mjs';
import {createAtlas} from '../discovery-model.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';
import {buildSourceIdentityIndex} from './build_source_identity_index.mjs';
const pick=(v,keys)=>Object.fromEntries(keys.filter(k=>v[k]!==undefined).map(k=>[k,v[k]]));
const identity=w=>pick(w,['id','indexId','title','displayTitle','originalTitle','chineseTitle','aliases','titleAliases','firstYear','yearStatus','sourceRefs','identityWorkId','basicRegistryId','linkedRecordId','mainPlacement','source']);
const summary=w=>({...pick(w,['id','title','displayTitle','sourceTitle','originalTitle','chineseTitle','chineseTitleType','titleAliases','firstYear','yearStatus','datePrecision','category','subcategory','genre','interactionModes','writerNames','artistNames','musicianNames','formalTitle','formalOverride','formalAt']),characters:w.characters||[],synopsis:(w.synopsis||'').slice(0,140)});
export async function buildOnDemandCatalogues(root,output,revision){
 const read=name=>JSON.parse(readFileSync(join(root,'data',name),'utf8'));
 const raw=loadEffectiveInputsSync(root),inputs={main:raw.main,supplement:raw.supplement,history:raw.history,store:raw.basicStore,registry:readJsonFileSync(join(root,'data/main-adv-rpg-works-20261031.json'))},sourceLease=sourceLeaseSync(root),coverage=raw.coverage;
 const sourceIdentity=buildSourceIdentityIndex(root,output,revision),formalLinks=raw.formalLinks;
 const effective=buildEffectiveCatalogue({main:inputs.main,supplement:inputs.supplement,history:inputs.history,basicStore:inputs.store,formalLinks,coverage});
 const full=mergeFormalDatasets(effective),catalogue=read('entity-catalogue.json'),editorial=read('discovery-editorial.json'),creators=read('creator-credits.json'),notes=read('work-notes.json');
 const atlas=createAtlas(full,catalogue,editorial,creators,notes),refs={};
 async function save(name,value){const path=`catalogue-web/${revision}/on-demand/${name}.json`,text=JSON.stringify(value)+'\n';mkdirSync(join(output,'data',path,'..'),{recursive:true});writeFileSync(join(output,'data',path),text);writeFileSync(join(output,'data',path+'.gz'),gzipSync(text));return {path,gzip:path+'.gz',sha:await blobDigest(text)};}
 const rawById=new Map([...inputs.supplement.works,...inputs.main.works].map(w=>[w.id,w]));
 const families={formal:{},editorial:{},notes:{}};
 const ids=full.works.map(w=>w.id),size=25;
 for(let offset=0;offset<ids.length;offset+=size){
  const part=ids.slice(offset,offset+size),n=offset/size;
  for(const family of Object.keys(families)){
   const rows=Object.fromEntries(part.map(id=>[id,family==='formal'?{source:rawById.get(id),work:atlas.works.get(id),contentVersions:atlas.contents.get(id)||[],platformReleases:atlas.releases.get(id)||[]}:family==='editorial'?editorial.works[id]??null:notes.works[id]??null]));
   families[family][n]=await save(`${family}-${n}`,rows);
  }
 }
 const lightEditorial={...editorial,works:Object.fromEntries(Object.entries(editorial.works).map(([id,w])=>[id,pick(w,['position','style','theme','structure','cover','openQuestions'])]))};
 const directory={schemaVersion:1,revision,ids,shardSize:size,families,identityStats:sourceIdentity.stats,
  data:{...full,works:full.works.map(summary),contentVersions:full.contentVersions.map(c=>pick(c,['id','workId','label','firstYear','basis'])),platformReleases:full.platformReleases.map(r=>pick(r,['id','workId','year','platform','publisher','publisherCompanies','kind','voice','contentVersionId','contentRelation','releaseRole'])),searchById:Object.fromEntries(atlas.search)},
  raw:{main:{...inputs.main,works:inputs.main.works.map(summary),contentVersions:[],platformReleases:[]},supplement:{...inputs.supplement,works:inputs.supplement.works.map(summary),contentVersions:[],platformReleases:[]},history:inputs.history,basicStore:inputs.store,formalLinks},
  editorial:lightEditorial,catalogue:{...catalogue,credits:catalogue.credits.map(c=>pick(c,['id','workId','entityId','role','targetType','targetId','status']))},
  coverage:{...coverage,companies:coverage.companies.map(c=>({...pick(c,['id','name']),relatedGames:(c.relatedGames||[]).map(identity),dossierOnlyWorks:(c.dossierOnlyWorks||[]).map(identity)}))},sourceLease};
 refs.formal=await save('formal-directory',directory);
 refs.advancedSearch=await save('advanced-search',{contents:Object.fromEntries(full.contentVersions.map(c=>[c.id,c.evidence||''])),releases:Object.fromEntries(full.platformReleases.map(r=>[r.id,r.differences||'']))});refs.validation=await save('validation',Object.keys(inputs.history.records||{}).map(id=>rawById.get(id)).filter(Boolean));refs.releases=await save('releases',{platformReleases:full.platformReleases,contentVersions:full.contentVersions});refs.creators=await save('creators',creators);refs.organizations=await save('organizations',catalogue);refs.baseline=await save('baseline',read('narrative-editorial-baseline-20261029.json'));
 const formalSource=buildEffectiveCatalogue({main:inputs.main,supplement:inputs.supplement,history:inputs.history});
 const byId=new Map([...formalSource.main.works,...formalSource.supplement.works].map(w=>[w.id,w]));
 const sourceRows=projectBasicSources(inputs.registry.works.map(w=>({...w,year:w.firstYear})),byId,formalLinks).map(w=>({...w,firstYear:w.year,identityLink:sourceIdentity.links.get(w.id)}));
 const registry=projectRegistry({...inputs.registry,works:sourceRows},validateStore(inputs.store));
 const reserved=[...effective.main.works,...effective.supplement.works,...effective.coverage.companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])])].map(w=>({...w,identityWorkId:sourceIdentity.profileWorkIds.get(w.id)||w.id}));
 const scan=scanRegistry(registry,reserved),bulkSize=100,shards={},buckets={},lookup=Array.from({length:64},()=>({})),lookupRefs={};
 const bucket=(key,slot)=>{(buckets[key]??=[]).push(slot);};
 for(let slot=0;slot<scan.length;slot++){
  const r=scan[slot];bucket(r.status,slot);bucket('year:'+r.work.firstYear,slot);bucket(r.status+':'+r.work.firstYear,slot);
  const prefix=parseInt(createHash('sha256').update(r.work.indexId).digest('hex').slice(0,2),16)%64;
  lookup[prefix][r.work.indexId]=slot;
 }
 for(let offset=0;offset<scan.length;offset+=bulkSize)shards[offset/bulkSize]=await save(`bulk-${offset/bulkSize}`,scan.slice(offset,offset+bulkSize));
 for(let n=0;n<lookup.length;n++)lookupRefs[n]=await save(`bulk-lookup-${n}`,lookup[n]);
 const search=await save('bulk-search',scan.map((r,slot)=>[slot,[r.work.title,...(r.work.aliases||[]),r.work.id,r.work.indexId,...(r.work.sourceRefs||[])].join(' ').normalize('NFKC').toLowerCase().replace(/\s/g,''),r.work.firstYear,r.status]));
 const reservedRef=await save('bulk-reserved',reserved.map(identity));
 refs.bulk=await save('bulk-directory',{schemaVersion:1,revision,count:scan.length,shardSize:bulkSize,shards,buckets,lookup:lookupRefs,search,reserved:reservedRef,identityStats:sourceIdentity.stats});
 refs.sourceIdentities=sourceIdentity.ref;
 return refs;
}
