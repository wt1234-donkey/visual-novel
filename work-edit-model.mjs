import {same,nameKey,validURL} from './management-model.mjs';
export const EDIT_FIELDS=['title','originalTitle','chineseTitle','chineseTitleType','titleAliases','category','subcategory','genre','synopsis','characters','charactersNote','charactersSource','source','interactionModes','interactionNote','interactionBasis','interactionSources','notes'];
const arrays=new Set(['titleAliases','characters','interactionModes','interactionSources']);
const copy=x=>structuredClone(x);
export function editableValues(work){return Object.fromEntries(EDIT_FIELDS.map(k=>[k,copy(work[k]??(arrays.has(k)?[]:k==='chineseTitleType'?'通行译名':''))]));}
export function projectWork(work,store){const patch=store?.records?.[work.id]?.overrides||{};return {...work,...Object.fromEntries(EDIT_FIELDS.filter(k=>Object.hasOwn(patch,k)).map(k=>[k,copy(patch[k])]))};}
export function applyWorkEdits(data,store){data.works=data.works.map(w=>projectWork(w,store));return data;}
export function validateValues(values,taxonomy,base,allWorks=[]){
 if(!values||!same(Object.keys(values).sort(),[...EDIT_FIELDS].sort()))throw Error('作品字段不完整或包含不可编辑的身份／发行字段');
 for(const [k,v]of Object.entries(values)){if(arrays.has(k)){if(!Array.isArray(v)||v.length>100||v.some(x=>typeof x!=='string'||!x.trim()||x.length>500)||new Set(v).size!==v.length)throw Error(k+' 需要不重复的有效文本列表');}else if(typeof v!=='string'||v.length>20000)throw Error(k+' 需要有效文本');}
 for(const k of ['title','originalTitle','genre','synopsis','interactionNote','interactionBasis'])if(!values[k].trim())throw Error('请填写名称、原名、类型、剧情简介及玩法依据');
 if(!values.characters.length||values.characters.some(n=>n.includes('待核实')))throw Error('请填写有依据的主要角色');
 if(!taxonomy.subcategories[values.category]?.includes(values.subcategory))throw Error('主／细分类不匹配');
 if(!values.interactionModes.length||values.interactionModes.some(m=>!(m in taxonomy.interactionModes))||values.interactionModes.includes('待核实')&&values.interactionModes.length>1)throw Error('玩法标签无效，待核实须单独选择');
 if(!validURL(values.source)||!values.interactionSources.length||values.interactionSources.some(s=>!validURL(s))||values.charactersSource&&!validURL(values.charactersSource))throw Error('请填写有效的作品、玩法及角色来源链接');
 if(!['通行译名','站内编辑译名'].includes(values.chineseTitleType)||values.chineseTitleType==='站内编辑译名'&&!values.chineseTitle.trim())throw Error('请填写中文译名并选择有效的译名类型');
 const keys=w=>[w.title,w.originalTitle,w.chineseTitle,...(w.titleAliases||[])].map(nameKey).filter(Boolean),old=new Set(keys(base)),introduced=keys(values).filter(k=>!old.has(k));
 const duplicate=allWorks.find(w=>w.id!==base.id&&keys(w).some(k=>introduced.includes(k)));if(duplicate)throw Error('新名称／别名与已有作品 '+duplicate.id+' 冲突');
 if(JSON.stringify(values).length>40000)throw Error('本部资料过长，请精简后保存');
}
export function saveEdit(store,base,after,meta,taxonomy,allWorks=[]){
 const result=copy(store),row=result.records[base.id]||{revision:0,overrides:{},recent:[]};
 if(row.revision!==meta.expectedRevision)throw Error('作品已被修改，请重新读取后核对');
 const current=editableValues(projectWork(base,store));validateValues(after,taxonomy,current,allWorks);
 if(same(current,after))throw Error('没有实际修改');
 if(typeof meta.reason!=='string'||meta.reason.trim().length<5||meta.reason.length>1000||!meta.sources?.length||!meta.sources.every(validURL))throw Error('请填写至少5字修改说明和有效来源');
 const raw=editableValues(base),patch=Object.fromEntries(EDIT_FIELDS.filter(k=>!same(raw[k],after[k])).map(k=>[k,copy(after[k])]));
 const entry={id:meta.id,revision:row.revision+1,at:meta.at,actor:meta.actor,reason:meta.reason.trim(),sources:copy(meta.sources),before:copy(row.overrides),after:copy(patch)};
 if(!entry.id||!entry.at||!entry.actor)throw Error('缺少修改身份或时间');
 result.records[base.id]={revision:entry.revision,overrides:patch,recent:[...row.recent,entry].slice(-3)};
 return result;
}
export function undoEdit(store,base,targetId,expectedRevision,taxonomy,allWorks=[]){
 const row=store.records[base.id];if(!row||row.revision!==expectedRevision)throw Error('作品已变化，请重新读取');
 const index=row.recent.findIndex(e=>e.id===targetId);if(index<0)throw Error('只能回撤本作品最近3次修改');
 const overrides=copy(row.recent[index].before),restored={...editableValues(base),...overrides};
 validateValues(restored,taxonomy,editableValues(projectWork(base,store)),allWorks);
 const result=copy(store);result.records[base.id]={revision:row.revision+1,overrides,recent:row.recent.slice(0,index)};return result;
}
export function changedFields(before,after){return EDIT_FIELDS.filter(k=>!same(before[k],after[k]));}
export function validateHistory(store,works,taxonomy){
 if(!store||store.schemaVersion!==1||!store.records||Array.isArray(store.records))throw Error('修改历史格式无效');
 const base=new Map(works.map(w=>[w.id,w]));
 for(const [id,row]of Object.entries(store.records)){
  if(!base.has(id)||!Number.isInteger(row.revision)||row.revision<1||!row.overrides||!Array.isArray(row.recent)||row.recent.length>3)throw Error('作品修订结构无效：'+id);
  const patchOK=patch=>patch&&typeof patch==='object'&&!Array.isArray(patch)&&Object.keys(patch).every(k=>EDIT_FIELDS.includes(k));
  if(!patchOK(row.overrides))throw Error('修订包含受保护字段');
  const ids=new Set();let prior=null,rev=0;
  for(const e of row.recent){if(!patchOK(e.before)||!patchOK(e.after)||!e.id||ids.has(e.id)||!Number.isInteger(e.revision)||e.revision<=rev||e.revision>row.revision||!Number.isFinite(Date.parse(e.at))||!e.actor||!e.reason||e.reason.trim().length<5||!e.sources?.length||!e.sources.every(validURL))throw Error('历史快照无效');if(prior&&!same(prior,e.before))throw Error('历史快照不连续');ids.add(e.id);rev=e.revision;prior=e.after;}
  if(prior&&!same(prior,row.overrides))throw Error('现行更正与最近修改不一致');
  validateValues(editableValues(projectWork(base.get(id),store)),taxonomy,editableValues(base.get(id)),works.map(w=>projectWork(w,store)));
 }
 return true;
}
