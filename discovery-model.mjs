import {normalize,filterCatalogue} from './filter.mjs';
export const CREATOR_ROLES={writer:'剧作者',artist:'画师',musician:'音乐创作者'};
export const MAKER_ROLES=new Set(['productionBrand','originalProduction','developer','coDeveloper']);
export const PENDING='__pending__';
export const titleOf=work=>work.chineseTitle||work.title;
const group=(rows,key)=>{const map=new Map();for(const row of rows){const k=row[key];if(!map.has(k))map.set(k,[]);map.get(k).push(row)}return map};
export function createAtlas(data,catalogue,editorial,creators,notes={works:{}}){
  const works=new Map(data.works.map(w=>[w.id,w]));
  const entities=new Map(catalogue.model.entities.map(e=>[e.id,e]));
  const people=new Map(creators.people.map(p=>[p.id,p]));
  const personal=group(creators.credits,'workId');
  const organization=group(catalogue.credits,'workId');
  const releases=group(data.platformReleases,'workId');
  const contents=group(data.contentVersions,'workId');
  const search=new Map();
  for(const w of data.works){
    const names=(personal.get(w.id)||[]).flatMap(c=>{const p=people.get(c.personId);return [p?.name,p?.alias]});
    const makers=(organization.get(w.id)||[]).filter(c=>MAKER_ROLES.has(c.role)).flatMap(c=>{const e=entities.get(c.entityId);return [e?.name,...(e?.aliases||[])]});
    search.set(w.id,normalize([w.title,w.chineseTitle,w.originalTitle,...(w.titleAliases||[]),w.genre,w.synopsis,w.category,w.subcategory,...w.characters,...(w.interactionModes||[]),...names,...makers].join(' ')));
  }
  return {data,catalogue,editorial,creators,notes,works,entities,people,personal,organization,releases,contents,search};
}
export function metadataValues(atlas,work,key){
  if(key==='gameplay')return work.interactionModes||[];
  const value=atlas.editorial.works[work.id]?.[key];
  return value?(Array.isArray(value)?value:[value]):[];
}
export function creatorCredits(atlas,workId,role=''){
  return (atlas.personal.get(workId)||[]).filter(c=>!role||c.role===role);
}
export function creatorWorkIds(atlas,kind,id,role=''){
  if(kind==='person')return new Set(atlas.creators.credits.filter(c=>c.personId===id&&(!role||c.role===role)).map(c=>c.workId));
  if(kind==='cooperation'){
    const c=atlas.creators.collaborations.find(c=>c.id===id);
    if(!c)return new Set();
    // Only show works with direct credits for every named person, even for candidates.
    return new Set(c.workIds.filter(wid=>c.people.every(pid=>creatorCredits(atlas,wid).some(credit=>credit.personId===pid))));
  }
  return new Set(atlas.catalogue.credits.filter(c=>c.entityId===id&&MAKER_ROLES.has(c.role)&&['work','content'].includes(c.targetType)).map(c=>c.workId));
}
export function filterAtlas(atlas,filters={},entityIndex=null){
  let candidates=atlas.data.works;
  const legacy=filters.legacy||{};
  if(Object.values(legacy).some(v=>v)){
    const ids=new Set(filterCatalogue(atlas.data,{...legacy,query:'',sort:'oldest'},entityIndex).map(item=>item.work.id));
    candidates=candidates.filter(w=>ids.has(w.id));
  }
  const query=normalize(filters.query);
  let out=candidates.filter(w=>(!query||atlas.search.get(w.id).includes(query))&&Object.entries(filters.facets||{}).every(([key,value])=>!value||(value===PENDING?metadataValues(atlas,w,key).length===0:metadataValues(atlas,w,key).includes(value))));
  if(filters.sort==='newest')out.sort((a,b)=>b.firstYear-a.firstYear||titleOf(a).localeCompare(titleOf(b),'zh'));
  else if(filters.sort==='oldest')out.sort((a,b)=>a.firstYear-b.firstYear||titleOf(a).localeCompare(titleOf(b),'zh'));
  else if(filters.sort==='title')out.sort((a,b)=>titleOf(a).localeCompare(titleOf(b),'zh'));
  else {const featured=Object.keys(atlas.editorial.works);out.sort((a,b)=>(featured.includes(a.id)?featured.indexOf(a.id):-1+1e5)-(featured.includes(b.id)?featured.indexOf(b.id):-1+1e5)||a.firstYear-b.firstYear||titleOf(a).localeCompare(titleOf(b),'zh'));}
  return out;
}
export function productionCredits(atlas,wid){return (atlas.organization.get(wid)||[]).filter(c=>MAKER_ROLES.has(c.role)&&['work','content'].includes(c.targetType));}
export function sourceStatus(status){return {sourceReviewed:'来源已核',existingEvidence:'沿用既有证据',existingDossier:'沿用既有档案',existingCredit:'沿用既有署名',pendingRole:'职责待核',unresolved:'待核实',editorialObservation:'编辑归纳',candidate:'合作线索 · 待核'}[status]||'待核实';}
export function creditScope(atlas,credit){
  const s=credit.scope;
  if(s.type==='release'){
    const r=atlas.data.platformReleases.find(r=>r.id===s.releaseId);
    return r?`${r.year} · ${r.platform} · ${r.kind}`:'适用发行待核';
  }
  if(s.type==='externalEdition')return `${s.year} · ${s.platform} · 官方产品页署名`;
  return credit.scopeLabel||s.label||'具名作品署名';
}
