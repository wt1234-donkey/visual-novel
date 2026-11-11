// A display projection, never a rewrite of source facts, releases or scoped credits.
export const CREATOR_NAME_FIELDS={writerNames:'剧作',artistNames:'美术',musicianNames:'音乐'};
export const EDIT_FIELDS=['title','originalTitle','chineseTitle','chineseTitleType','titleAliases','category','subcategory','genre','synopsis','characters','charactersNote','charactersSource','source','interactionModes','interactionNote','interactionBasis','interactionSources','notes',...Object.keys(CREATOR_NAME_FIELDS)];
const clone=value=>structuredClone(value);
const unique=rows=>[...new Set(rows.filter(value=>typeof value==='string'&&value.trim()))];
export function projectFormalWork(work,history){
 const patch=history?.records?.[work.id]?.overrides||{};
 return {...work,...Object.fromEntries(EDIT_FIELDS.filter(key=>Object.hasOwn(patch,key)).map(key=>[key,clone(patch[key])]))};
}
export const displayTitle=work=>work.displayTitle||work.chineseTitle||work.title;
export function formalFieldMeta(record={}){
 const result=clone(record.fieldMeta||{});
 for(const event of record.recent||[])for(const key of EDIT_FIELDS){
  if(JSON.stringify(event.before?.[key])!==JSON.stringify(event.after?.[key])&&!Object.hasOwn(record.fieldMeta||{},key))result[key]={id:event.id,at:event.at};
 }
 return Object.fromEntries(Object.entries(result).filter(([key])=>Object.hasOwn(record.overrides||{},key)));
}
export function basicTitleIsChanged(record){return !!record?.values?.title&&(!record.identity||record.values.title!==record.identity.title);}
export function resolveBasicTitle(record,formalTitle,formalOverride,formalAt=0,fallback=formalTitle){
 if(!basicTitleIsChanged(record))return formalTitle||fallback;
 const basicAt=Date.parse(record.fieldMeta?.title?.at||'')||0;
 return formalOverride&&formalAt>=basicAt?formalTitle:record.values.title;
}
export function mergeFormalDatasets({main,supplement}){
 const merged={...main};
 for(const key of ['works','contentVersions','platformReleases']){const rows=main[key]||[],known=new Set(rows.map(row=>row.id));merged[key]=[...rows,...(supplement[key]||[]).filter(row=>!known.has(row.id))];}
 return merged;
}

export function buildEffectiveCatalogue({main={works:[]},supplement={works:[]},coverage={companies:[]},history={records:{}},basicStore={records:{}},formalLinks={}}={}){
 const patches=new Map();
 for(const [id,record] of Object.entries(basicStore.records||{})){
  if(!record.values)continue;
  const formalId=formalLinks[id]||id;
  const changed=Object.fromEntries(Object.entries(record.values).filter(([key,value])=>['title','firstYear','yearStatus'].includes(key)&&(!record.identity||JSON.stringify(value)!==JSON.stringify(record.identity[key]))));
  const prior=patches.get(formalId);
  if(prior&&Object.keys(changed).some(key=>Object.hasOwn(prior.values,key)&&JSON.stringify(prior.values[key])!==JSON.stringify(changed[key])))throw Error('同一正式身份存在冲突的基础更正：'+formalId);
  patches.set(formalId,{...record,values:{...(prior?.values||{}),...changed}});
 }
 const effective=work=>{
  const current=projectFormalWork(work,history),record=patches.get(work.id),basic=record?.values,formalRecord=history.records?.[work.id],formalPatch=formalRecord?.overrides||{};
  const formalTitle=Object.hasOwn(formalPatch,'chineseTitle')?current.chineseTitle||current.title:Object.hasOwn(formalPatch,'title')?current.title:current.chineseTitle||current.title;
  const formalOverride=Object.hasOwn(formalPatch,'chineseTitle')||Object.hasOwn(formalPatch,'title');
  const titleMeta=formalFieldMeta(formalRecord);
  const formalAt=Math.max(0,...['title','chineseTitle'].map(key=>Date.parse(titleMeta[key]?.at)||0));
  const title=resolveBasicTitle(record,formalTitle,formalOverride,formalAt);
  return {...current,sourceTitle:work.title,sourceFirstYear:work.firstYear,displayTitle:title,
   formalTitle,formalOverride,formalAt,
   ...(basic?.yearStatus?{yearStatus:basic.yearStatus}:{}),
   ...(basic&&Object.hasOwn(basic,'firstYear')?{firstYear:basic.firstYear}:{}),
   titleAliases:unique([...(current.titleAliases||[]),work.title,work.chineseTitle,work.originalTitle,...(work.titleAliases||[])])};
 };
 const projectData=data=>({...data,works:(data.works||[]).map(effective)});
 const projectedCoverage={...coverage,companies:(coverage.companies||[]).map(company=>({...company,
  ...(company.relatedGames?{relatedGames:company.relatedGames.map(effective)}:{}),
  ...(company.dossierOnlyWorks?{dossierOnlyWorks:company.dossierOnlyWorks.map(effective)}:{})}))};
 return {schemaVersion:1,main:projectData(main),supplement:projectData(supplement),coverage:projectedCoverage};
}

export function projectBasicSources(rows,formalById,formalLinks={}){
 return rows.map(row=>{
  const id=row.linkedRecordId||formalLinks[row.matchedWorkId||row.registryId||row.id]||row.matchedWorkId||row.id;
  const formal=formalById.get(id);
  if(!formal)return row;
  return {...row,sourceTitle:row.title,sourceYear:row.year,title:displayTitle(formal),year:formal.firstYear,firstYear:formal.firstYear,
   formalTitle:formal.formalTitle,formalOverride:formal.formalOverride,formalAt:formal.formalAt,
   aliases:unique([...(row.aliases||[]),row.title,formal.title,formal.chineseTitle,formal.originalTitle,...(formal.titleAliases||[])])};
 });
}
