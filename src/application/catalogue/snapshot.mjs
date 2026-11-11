import {emptyStore} from '../../domain/catalogue/model.mjs';
import {workKey,nameKey} from '../../domain/catalogue/identity.mjs';
import {compareBasicOrder} from '../../domain/catalogue/order.mjs';
import {createCatalogueView} from './view.mjs';
import {projectWork} from '../../../work-edit-model.mjs';

export function assembleBasicRows(registry,initial,batches){
 const byIndex=new Map();
 for(const work of registry.works)if(work.indexId){
  if(byIndex.has(work.indexId)&&byIndex.get(work.indexId).id!==work.id)throw Error('来源身份映射冲突：'+work.indexId);
  byIndex.set(work.indexId,work);
 }
 const holding=new Set((registry.identityReview||[]).map(w=>w.indexId));
 const rows=initial.map(w=>{
  const identity=byIndex.get(w.id);
  const placement=identity?.mainPlacement;
  const status=holding.has(w.id)?'identity-review':
   ['promoted-basic','promoted-dossier'].includes(placement)?placement:w.status;
  return {...w,...(identity?{mainPlacement:identity.mainPlacement,sourceRefs:identity.sourceRefs,intakePolicy:identity.intakePolicy}:{}),status,matchedWorkId:identity?.id||w.matchedWorkId,linkedRecordId:identity?.linkedRecordId||w.linkedRecordId,
   ...(identity?.plotTags?{plotTags:identity.plotTags}:{}),...(identity?.plotStyles?{plotStyles:identity.plotStyles}:{}),
   ...(identity?.plotTagEvidence?{plotTagEvidence:identity.plotTagEvidence}:{})};
 });
 const byMatched=new Map(rows.filter(w=>w.matchedWorkId).map(w=>[w.matchedWorkId,w]));
 for(const [batch,records] of batches){
  for(const r of records){
   const key=nameKey(r.title)+'|'+r.year;
   const explicit=r.registryId||byIndex.get(r.id)?.id;
   const canonical=explicit&&byMatched.get(explicit);
   if(canonical){
    canonical.sourceRecordIds=[...new Set([...(canonical.sourceRecordIds||[]),batch+':'+(r.id||explicit),r.id].filter(Boolean))];
    canonical.aliases=[...new Set([...(canonical.aliases||[]),r.title,...(r.aliases||[])])].filter(t=>t!==canonical.title);
    canonical.groups=[...new Set([...(canonical.groups||[]),canonical.group,r.group])];
    canonical.gameplayNote=canonical.gameplayNote||r.gameplayNote;
    continue;
   }
   const status=r.status==='existing-complete'?'main-linked':
    ['linked-existing-registry','linked-existing-full-or-dossier'].includes(r.status)?'main-registry-linked':r.status;
   const legacyId=batch+'-'+key;
   const collision=rows.some(w=>w.id===legacyId);
   const id=collision?legacyId+'|'+encodeURIComponent(r.registryId||r.id||r.source||JSON.stringify(r)):legacyId;
   const row={...r,id,matchedWorkId:explicit,status};
   rows.push(row);
   if(row.matchedWorkId)byMatched.set(row.matchedWorkId,row);
  }
 }
 const representedIds=new Set(rows.flatMap(r=>[r.matchedWorkId,r.registryId].filter(Boolean)));
 const representedIndexIds=new Set(rows.map(r=>r.id));
 for(const w of registry.works){
  if(representedIds.has(w.id)||representedIndexIds.has(w.indexId))continue;
  rows.push({
   ...w,id:w.indexId||w.id,matchedWorkId:w.id,title:w.title,aliases:w.aliases||[],year:w.firstYear,
   gameplay:w.gameplay||'玩法待核',gameplayNote:w.gameplayNote,group:w.group||'来源关联待核',
   plotStyles:w.plotStyles,plotTags:w.plotTags,plotTagEvidence:w.plotTagEvidence,linkedRecordId:w.linkedRecordId,source:w.source,
   status:w.mainPlacement==='existing-complete'?'main-linked':w.mainPlacement,
   reason:w.intakePolicy==='append-without-deduplication'?'未去重导入 · 来源状态：'+(w.sourceDevelopmentStatus||'未提供'):''
  });
  representedIds.add(w.id);representedIndexIds.add(w.indexId);
 }
 return rows.sort(compareBasicOrder);
}

// One pure input-to-snapshot boundary. I/O and index compression are adapters.
export function buildCatalogueSnapshot({registry, initial = [], batches = [], store = emptyStore(), main = {works:[]}, supplement = {works:[]}, history = {records:{}}}, {strict = true} = {}) {
 const sourceRows = assembleBasicRows(registry, initial, batches);
 const view = createCatalogueView(sourceRows, store, {strict});
 const identities = view.identities;
 const formalById = new Map([...supplement.works, ...main.works].map(work => [work.id, projectWork(work, history)]));
 const formalIdByWorkId = new Map();
 for (const row of view.all) {
  const formalId = row.linkedRecordId || (formalById.has(row._key) ? row._key : null);
  if (formalId && formalById.has(formalId)) formalIdByWorkId.set(row._key, formalId);
 }
 const names = new Map();
 for (const row of view.entries) {
  const key = nameKey(row.title) + '|' + row.year;
  if (!names.has(key)) names.set(key, []);
  names.get(key).push(row._key);
 }
 const identityCandidates = [...names].filter(([,ids]) => ids.length > 1).map(([key,ids]) => ({key, ids}));
 const registryIds = new Set(registry.works.map(workKey));
 const homeRows = view.entries.filter(row => (registryIds.has(row._key) || row._key.startsWith('manual-')) &&
  row.mainPlacement !== 'existing-complete' && !formalIdByWorkId.has(row._key)).map(row => ({...row,
   firstYear:row.year, mainPlacement:row.mainPlacement || row.status || 'promoted-basic',
   aliases:[...new Set([...(row.aliases || []), ...(view.childrenByMain.get(row._key) || []).flatMap(child => [child.title, ...(child.aliases || [])])])]
  }));
 return {schemaVersion:1, revision:store.revision, sourceRows, ...view, identities, formalById, formalIdByWorkId, identityCandidates,
  home:{rows:homeRows, excluded:view.entries.length - homeRows.length}};
}

// Legacy API retained for scripts/tests; the implementation uses the same view.
export function assembleHomeRows(registry, store, fullWorks) {
 return buildCatalogueSnapshot({registry, store, main:{works:fullWorks}}).home;
}
