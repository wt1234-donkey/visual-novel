import {projectFormalWork,formalFieldMeta,CREATOR_NAME_FIELDS,EDIT_FIELDS} from './src/domain/catalogue/effective.mjs';
export {CREATOR_NAME_FIELDS,EDIT_FIELDS} from './src/domain/catalogue/effective.mjs';
import {same,nameKey,validURL} from './management-model.mjs';
import {upgradeFormalHistory,appendFormalEvent,confirmFormalOperation,validateFormalJournal} from './src/domain/catalogue/formal-journal.mjs';
const arrays=new Set(['titleAliases','characters','interactionModes','interactionSources',...Object.keys(CREATOR_NAME_FIELDS)]);
const copy=x=>structuredClone(x);
function creatorNamesOnly(before,after){const fields=EDIT_FIELDS.filter(k=>!same(before[k]??(k in CREATOR_NAME_FIELDS?[]:undefined),after[k]??(k in CREATOR_NAME_FIELDS?[]:undefined)));return fields.length>0&&fields.every(k=>k in CREATOR_NAME_FIELDS);}
function validEvidence(sources,before,after){return Array.isArray(sources)&&sources.every(validURL)&&(sources.length>0||creatorNamesOnly(before,after));}
export function editableValues(work){return Object.fromEntries(EDIT_FIELDS.map(k=>[k,copy(work[k]??(arrays.has(k)?[]:k==='chineseTitleType'?'通行译名':''))]));}
export const projectWork=projectFormalWork;
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
 store=upgradeFormalHistory(store,{at:meta.at});
 const type=meta.commandType||'edit',intent=meta.intent||{type:'edit',values:copy(after)};
 if(confirmFormalOperation(store,base.id,meta,type,intent))return copy(store);
 const result=copy(store),row=result.records[base.id]||{revision:0,overrides:{},recent:[]};
 if(row.revision!==meta.expectedRevision)throw Error('作品已被修改，请重新读取后核对');
 const current=editableValues(projectWork(base,store));validateValues(after,taxonomy,{...current,id:base.id},allWorks);
 if(same(current,after))throw Error('没有实际修改');
 if(typeof meta.reason!=='string'||meta.reason.trim().length<5||meta.reason.length>1000||!validEvidence(meta.sources,current,after))throw Error('请填写至少5字修改说明和有效来源；仅添加剧作、美术、音乐姓名时无需来源');
 const raw=editableValues(base),patch=Object.fromEntries(EDIT_FIELDS.filter(k=>!same(raw[k],after[k])).map(k=>[k,copy(after[k])]));
 const beforeFieldMeta=formalFieldMeta(row),fieldMeta=copy(beforeFieldMeta);
 for(const field of EDIT_FIELDS){
  if(!Object.hasOwn(patch,field))delete fieldMeta[field];
  else if(!same(current[field],after[field]))fieldMeta[field]={id:meta.id,at:meta.at};
 }
 const entry={id:meta.id,revision:row.revision+1,at:meta.at,actor:meta.actor,reason:meta.reason.trim(),sources:copy(meta.sources),before:copy(row.overrides),after:copy(patch),beforeFieldMeta};
 if(!entry.id||!Number.isFinite(Date.parse(entry.at))||!entry.actor)throw Error('缺少修改身份或时间');
 result.records[base.id]={revision:entry.revision,overrides:patch,fieldMeta,recent:[...row.recent,entry].slice(-3)};
 return appendFormalEvent(store,result,base.id,meta,type,intent,{before:current,after});
}
export function saveCreatorNames(store,base,names,meta,taxonomy,allWorks=[]){
 if(!names||!same(Object.keys(names).sort(),Object.keys(CREATOR_NAME_FIELDS).sort()))throw Error('请填写剧作、美术和音乐的姓名列表');
 const after={...editableValues(projectWork(base,store)),...copy(names)};
 return saveEdit(store,base,after,{...meta,reason:'添加或调整剧作、美术与音乐',sources:[],commandType:'creators',intent:{type:'creators',names:copy(names)}},taxonomy,allWorks);
}
export function undoEdit(store,base,targetId,expectedRevision,taxonomy,allWorks=[],meta){
 if(!meta)throw Error('撤销需要独立操作ID、操作人、时间和说明');
 meta={...meta,expectedRevision};store=upgradeFormalHistory(store,{at:meta.at});
 const intent={type:'undo',targetId};
 if(confirmFormalOperation(store,base.id,meta,'undo',intent))return copy(store);
 const row=store.records[base.id];if(!row||row.revision!==expectedRevision)throw Error('作品已变化，请重新读取');
 const index=row.recent.findIndex(e=>e.id===targetId);if(index<0)throw Error('只能回撤本作品最近3次修改');
 const overrides=copy(row.recent[index].before),restored={...editableValues(base),...overrides};
 validateValues(restored,taxonomy,{...editableValues(projectWork(base,store)),id:base.id},allWorks);
 const recent=row.recent.slice(0,index),fieldMeta=copy(row.recent[index].beforeFieldMeta||formalFieldMeta({overrides,recent}));
 const result=copy(store);result.records[base.id]={revision:row.revision+1,overrides,fieldMeta,recent};
 return appendFormalEvent(store,result,base.id,meta,'undo',intent,{before:editableValues(projectWork(base,store)),after:restored});
}
export function changedFields(before,after){return EDIT_FIELDS.filter(k=>!same(before[k],after[k]));}
export function validateHistory(store,works,taxonomy){
 if(store?.schemaVersion===2){
  if(!same(Object.keys(store).sort(),['journal','records','schemaVersion']))throw Error('正式修改历史含未知字段');
  validateHistory({schemaVersion:1,records:store.records},works,taxonomy);
  validateFormalJournal(store,state=>validateHistory(state,works,taxonomy));return true;
 }
 if(!store||store.schemaVersion!==1||!store.records||Array.isArray(store.records))throw Error('修改历史格式无效');
 const base=new Map(works.map(w=>[w.id,w]));
 for(const [id,row]of Object.entries(store.records)){
  if(!base.has(id)||!Number.isInteger(row.revision)||row.revision<1||!row.overrides||!Array.isArray(row.recent)||row.recent.length>3)throw Error('作品修订结构无效：'+id);
  const patchOK=patch=>patch&&typeof patch==='object'&&!Array.isArray(patch)&&Object.entries(patch).every(([k,v])=>EDIT_FIELDS.includes(k)&&(arrays.has(k)?Array.isArray(v)&&v.length<=100&&v.every(x=>typeof x==='string'&&x.trim()&&x.length<=500)&&new Set(v).size===v.length:typeof v==='string'&&v.length<=20000));
  if(!patchOK(row.overrides))throw Error('修订包含受保护字段');
  const metadataOK=(metadata,patch)=>metadata===undefined||metadata&&typeof metadata==='object'&&!Array.isArray(metadata)&&Object.entries(metadata).every(([key,value])=>Object.hasOwn(patch,key)&&value&&typeof value.id==='string'&&value.id&&Number.isFinite(Date.parse(value.at)));
  if(!metadataOK(row.fieldMeta,row.overrides)||row.recent.some(event=>!metadataOK(event.beforeFieldMeta,event.before)))throw Error('字段更正身份或时间无效');
  const ids=new Set();let prior=null,rev=0;
  for(const e of row.recent){if(!patchOK(e.before)||!patchOK(e.after)||!e.id||ids.has(e.id)||!Number.isInteger(e.revision)||e.revision<=rev||e.revision>row.revision||!Number.isFinite(Date.parse(e.at))||!e.actor||!e.reason||e.reason.trim().length<5||!validEvidence(e.sources,e.before,e.after))throw Error('历史快照无效');if(prior&&!same(prior,e.before))throw Error('历史快照不连续');ids.add(e.id);rev=e.revision;prior=e.after;}
  if(prior&&!same(prior,row.overrides))throw Error('现行更正与最近修改不一致');
  validateValues(editableValues(projectWork(base.get(id),store)),taxonomy,{...editableValues(base.get(id)),id},works.map(w=>projectWork(w,store)));
 }
 return true;
}
