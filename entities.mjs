// Entity identities and scoped participation are independent of the legacy publisher index.
export const BRAND_ROLES=new Set(['productionBrand','originalPublishingBrand','publishingBrand']);
export const DEVELOPER_ROLES=new Set(['originalProduction','developer','coDeveloper']);
export const PUBLISHER_ROLES=new Set(['publisher','publishingBrand']);
export function displayPublisherName(index,raw){return index.model.displayNames?.[raw]||raw;}
export function createEntityIndex(data,model,creditData,classification={placements:[]}){
  const entities=new Map(model.entities.map(e=>[e.id,e]));
  const mainIds=new Set(data.works.map(w=>w.id));
  const byWork=new Map(),workCredits=new Map(),releaseCredits=new Map(),contentCredits=new Map();
  for(const c of creditData.credits){
    if(!byWork.has(c.workId))byWork.set(c.workId,[]);byWork.get(c.workId).push(c);
    const map=c.targetType==='work'?workCredits:c.targetType==='release'?releaseCredits:contentCredits;
    if(!map.has(c.targetId))map.set(c.targetId,[]);map.get(c.targetId).push(c);
  }
  const memberships=new Map();
  for(const m of creditData.dossierMemberships){if(!memberships.has(m.workId))memberships.set(m.workId,[]);memberships.get(m.workId).push(m);}
  return {model,entities,mainIds,byWork,workCredits,releaseCredits,contentCredits,memberships,placements:new Map(classification.placements.map(p=>[p.workId,p]))};
}
export function relatedEntityIds(index,id,includeAffiliates=false){
  const ids=new Set([id]);if(!includeAffiliates)return ids;
  let changed=true;while(changed){changed=false;for(const r of index.model.relations){
    if(['operatedBy','brandFamily'].includes(r.type)&&ids.has(r.to)&&!ids.has(r.from)){ids.add(r.from);changed=true;}
  }}return ids;
}
export function creditsForRelease(index,workId,release){
  return [...(index.workCredits.get(workId)||[]),...(release.contentVersionId?index.contentCredits.get(release.contentVersionId)||[]:[]),...(index.releaseCredits.get(release.id)||[])];
}
export function matchesEntityFilters(index,work,release,filters){
  const credits=creditsForRelease(index,work.id,release);
  for(const [field,roles] of [['brand',BRAND_ROLES],['developer',DEVELOPER_ROLES],['publisher',PUBLISHER_ROLES]]){
    if(!filters[field])continue;
    if(field==='publisher'&&filters.publisher==='__unattributed__'){if(credits.some(c=>c.targetType==='release'&&PUBLISHER_ROLES.has(c.role)))return false;continue;}
    const ids=relatedEntityIds(index,filters[field],filters.includeAffiliates);
    if(!credits.some(c=>ids.has(c.entityId)&&roles.has(c.role)&&(field!=='publisher'||c.targetType==='release')))return false;
  }
  if(filters.participant||filters.participantRole){
    const ids=filters.participant?relatedEntityIds(index,filters.participant,filters.includeAffiliates):null;
    if(!credits.some(c=>(!ids||ids.has(c.entityId))&&(!filters.participantRole||c.role===filters.participantRole)))return false;
  }
  if(filters.dossier||filters.dossierRelation){
    if(!(index.memberships.get(work.id)||[]).some(m=>(!filters.dossier||m.dossierId===filters.dossier)&&(!filters.dossierRelation||m.group===filters.dossierRelation)))return false;
  }
  return true;
}
export function entitySearchText(index,workId,release){
  return creditsForRelease(index,workId,release).flatMap(c=>{const e=index.entities.get(c.entityId);return [e?.name,...(e?.aliases||[]),index.model.roleLabels[c.role],c.rawCredit]}).join(' ');
}
export function entityWorkCounts(index,roles=null,{releaseOnly=false}={}){
  const sets=new Map();for(const [wid,rows] of index.byWork){if(!index.mainIds.has(wid))continue;for(const c of rows){
    if(roles&&!roles.has(c.role)||releaseOnly&&c.targetType!=='release')continue;
    if(!sets.has(c.entityId))sets.set(c.entityId,new Set());sets.get(c.entityId).add(wid);
  }}return new Map([...sets].map(([id,ids])=>[id,ids.size]));
}
export function summarizeCredits(index,workId,releases){
  const seen=new Set(),result=[];for(const r of releases)for(const c of creditsForRelease(index,workId,r)){
    const key=c.entityId+'|'+c.role+'|'+c.targetType;if(seen.has(key))continue;seen.add(key);result.push(c);
  }return result;
}
