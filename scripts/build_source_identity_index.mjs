import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {createHash} from 'node:crypto';
import {gzipSync} from 'node:zlib';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {projectRegistry} from '../src/domain/catalogue/model.mjs';
import {nameKey} from '../src/domain/catalogue/identity.mjs';
const bucket=id=>createHash('sha256').update(id).digest()[0]%64;
export function buildSourceIdentityIndex(root,output,revision){
 const {snapshot,inputs,sourceLease}=loadCatalogueSnapshot(root,{allowMissingLegacy:true}),model=snapshot.sourceIdentity;
 model.stats.bulkVisibleGroups=projectRegistry(inputs.registry,inputs.store).works.length;
 model.stats.legacySourceRowCount=snapshot.sourceRows.length;
 const physical=JSON.parse(readFileSync(join(root,'data/main-adv-rpg-works-20261031.json'),'utf8'));
 const prefix='catalogue-web/'+revision+'/on-demand/';
 const save=(name,value)=>{const path=prefix+'identity-'+name+'.json',text=JSON.stringify(value)+'\n';mkdirSync(join(output,'data',path,'..'),{recursive:true});writeFileSync(join(output,'data',path),text);writeFileSync(join(output,'data',path+'.gz'),gzipSync(text));return {path,gzip:path+'.gz',sha:createHash('sha1').update('blob '+Buffer.byteLength(text)+'\0').update(text).digest('hex')};};
 const sourceRows=[...model.sources.values()].map(s=>({id:s.id,indexId:s.indexId,title:s.record.title,firstYear:s.record.firstYear??null,
  source:s.record.source||'',sourceRefs:s.record.sourceRefs||[],link:model.links.get(s.id),caseIds:s.caseIds,
  recordRef:{path:physical.storage?.shards[Math.floor(s.ordinal/physical.storage.shardSize)]?.path||'main-adv-rpg-works-20261031.json',slot:physical.storage?s.ordinal%physical.storage.shardSize:s.ordinal}}));
 const workRows=[...model.works.values()];
 const caseRows=[...model.cases.values()].sort((a,b)=>(a.status==='resolved')-(b.status==='resolved'));
 const rows={sources:sourceRows,works:workRows,cases:caseRows},pages={},lookups={},pageSize=200,nameLookups=Array.from({length:64},()=>Object.create(null));
 const addName=(value,view,id)=>{const key=nameKey(value);if(!key)return;const part=nameLookups[bucket(key)];part[key]??={sources:[],works:[],cases:[]};if(!part[key][view].includes(id))part[key][view].push(id);};
 for(const s of model.sources.values())for(const value of [s.record.title,...(s.record.aliases||[])])addName(value,'sources',s.id);
 for(const w of workRows)for(const value of w.labels)addName(value,'works',w.id);
 for(const c of caseRows){addName(c.label,'cases',c.id);if(c.id.startsWith('name-year:'))addName(c.id.slice(10,c.id.lastIndexOf('|')),'cases',c.id);}
 for(const [view,items] of Object.entries(rows)){
  pages[view]=[];const ids=Array.from({length:64},()=>Object.create(null));
  for(let offset=0;offset<items.length;offset+=pageSize){const page=items.slice(offset,offset+pageSize);pages[view].push(save(view+'-'+offset/pageSize,page));for(let i=0;i<page.length;i++){ids[bucket(page[i].id)][page[i].id]=[offset/pageSize,i];if(view==='works')for(const alias of page[i].profileIds)ids[bucket(alias)][alias]=[offset/pageSize,i];}}
  lookups[view]=ids.map((part,n)=>save(view+'-lookup-'+n,part));
 }
 const nameRefs=nameLookups.map((part,n)=>save('names-'+n,part));
 return {ref:save('manifest',{schemaVersion:1,revision,dataRevision:inputs.identityStore.revision,stats:model.stats,pageSize,pages,lookups,nameLookups:nameRefs,
  totals:Object.fromEntries(Object.entries(rows).map(([key,value])=>[key,value.length])),sourceLease,
  definitions:{sourceRecordCount:'权威源登记中的记录数，保留全部原ID与证据；不含未准入暂存行。',workIdentityCount:'全部稳定作品身份（含未核与仅旧索引身份），不是已核独立作品总数。',resolvedWorkCount:'明示来源链接对应的不同作品身份数，含继承旧明确关联；只确认身份对应，不代表全部字段或内容版本已核实。',reviewedWorkCount:'通过本轮新增显式身份核对事件确认的不同目标身份数。',unreviewedSources:'尚无明示已确认对应的权威来源记录数。',basicVisibleGroups:'基础索引的兼容可见归组，包含早期遗留条目；不是来源数或已核作品数。',bulkVisibleGroups:'按权威源登记生成的批量入口可见归组。',pendingCases:'候选或历史待核案件数，同一来源可能涉及多个案件；不是待核来源数。'}}),stats:model.stats,links:model.links,profileWorkIds:new Map([...model.works.values()].flatMap(w=>w.profileIds.map(id=>[id,w.id])))};
}
