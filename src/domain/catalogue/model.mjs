import {withJournal,appendJournal,validateJournal} from './journal.mjs';
import {validateJournalIndex} from './journal-index.mjs';
// Shared, additive basic-catalogue edits. Original source records remain auditable.
export const emptyStore=()=>({schemaVersion:1,revision:0,additions:[],records:{},recent:[]});
import {workKey,nameKey} from './identity.mjs';
export {workKey,nameKey} from './identity.mjs';
import {STYLE_KEYS,STYLE_DIMENSIONS,styleName,styleState,styleList,styleValue,styleLabels,styleEvidenceEntries,packStyleEvidence,validateStyleTags,validateStyleEvidence} from '../taxonomy/style-tags.mjs';
export {STYLE_GROUPS,STYLE_OPTIONS} from '../taxonomy/style-tags.mjs';
const clone=x=>structuredClone(x);
const own=(obj,k)=>Object.hasOwn(obj,k);
const fields=['title','firstYear','group','gameplay','plotStyles','plotTags','plotTagEvidence','source'];
function validateStyles(v){
 if(!Array.isArray(v.plotStyles)||v.plotStyles.length>3||new Set(v.plotStyles).size!==v.plotStyles.length||v.plotStyles.some(s=>typeof s!=='string'||!s.trim()||s.length>30))throw Error('剧情风格最多3个，每个不超过30字且不重复');
 if(own(v,'plotTags'))validateStyleTags(v.plotTags);
 if(own(v,'plotTagEvidence'))validateStyleEvidence(v.plotTagEvidence,v.plotTags||{});
}
export function validateValues(v){
 if(!v||typeof v!=='object'||Object.keys(v).some(k=>!fields.includes(k)))throw Error('作品字段无效');
 for(const k of ['title','group','gameplay'])if(typeof v[k]!=='string'||!v[k].trim()||v[k].length>500)throw Error('名称、厂商和主要玩法不能为空，且须少于500字');
 if(v.firstYear!==null&&(!Number.isInteger(v.firstYear)||v.firstYear<1970||v.firstYear>new Date().getFullYear()+10))throw Error('年份须为1970年至未来10年内的整数，未知请留空');
 validateStyles(v);
 if(typeof v.source!=='string')throw Error('来源格式无效');
 if(v.source){try{if(!['https:','http:'].includes(new URL(v.source).protocol))throw Error();}catch{throw Error('来源须为 http 或 https 网址');}}
 return v;
}
export function valuesOf(w){return {title:w.title,firstYear:w.firstYear??w.year??null,group:w.group||'厂商待核',gameplay:w.gameplay||'玩法待核',plotStyles:[...(w.plotStyles||[])],...(w.plotTags?{plotTags:clone(w.plotTags)}:{}),...(w.plotTagEvidence?{plotTagEvidence:clone(w.plotTagEvidence)}:{}),source:w.source||''};}
// Reconcile a form opened before another GitHub edit: preserve fields the user
// did not touch, but never silently overwrite a concurrent edit to the same field.
export function reconcileBasicEdit(opened,submitted,latest){
 const same=(a,b)=>JSON.stringify(a??null)===JSON.stringify(b??null);
 const result=clone(submitted),conflicts=[];
 const labels={title:'作品名称',firstYear:'首发年份',group:'厂商／创作主体',gameplay:'主要玩法',source:'资料来源'};
 const keepLatest=key=>{if(own(latest,key))result[key]=clone(latest[key]);else delete result[key];};
 for(const key of ['title','firstYear','group','gameplay','source']){
  if(same(submitted[key],opened[key]))keepLatest(key);
  else if(!same(latest[key],opened[key])&&!same(latest[key],submitted[key]))conflicts.push(labels[key]);
 }
 const styleFields=['plotStyles','plotTags','plotTagEvidence'];
 const userChangedStyles=styleFields.some(key=>!same(opened[key],submitted[key]));
 const liveChangedStyles=styleFields.some(key=>!same(opened[key],latest[key]));
 if(!userChangedStyles)for(const key of styleFields)keepLatest(key);
 else if(liveChangedStyles&&styleFields.some(key=>!same(submitted[key],latest[key])))conflicts.push('作品特征标签');
 if(conflicts.length)throw Error('该作品已在其他页面更新，字段冲突：'+conflicts.join('、')+'。本次未写入；当前表单内容已保留，请核对后重新打开作品。');
 return validateValues(result);
}
export function validateStore(s){
 if(!s||![1,2,3].includes(s.schemaVersion)||!Number.isSafeInteger(s.revision)||s.revision<0||!Array.isArray(s.additions)||!s.records||typeof s.records!=='object'||Array.isArray(s.records)||!Array.isArray(s.recent)||s.recent.length>3)throw Error('基础库修改记录格式无效');
 const ids=new Set();for(const w of s.additions){if(!/^manual-[a-zA-Z0-9-]+$/.test(w.id)||ids.has(w.id))throw Error('新增作品ID无效或重复');ids.add(w.id);validateValues(valuesOf(w));}
 for(const [id,r] of Object.entries(s.records)){
  if(!id||!r||typeof r!=='object'||Array.isArray(r)||['__proto__','constructor','prototype'].includes(id))throw Error('修改记录无效');
  if(r.values)validateValues(r.values);
  if(own(r,'legacyPlotStyles'))validateStyles({plotStyles:r.legacyPlotStyles});
  if(own(r,'style')){
   if(!r.style||Object.keys(r.style).some(k=>!['plotStyles','plotTags','plotTagEvidence'].includes(k))||!own(r.style,'plotTags'))throw Error('标签修改记录无效');
   validateStyles(r.style);
  }
  if(r.deleted!==undefined&&typeof r.deleted!=='boolean')throw Error('删除标记无效');
  if(r.parentId!==undefined&&r.parentId!==null){
   if(typeof r.parentId!=='string'||!r.parentId||r.parentId===id)throw Error('作品不能合并到自身');
   if(!r.relation||!['unverified','same','added'].includes(r.relation.type)||!r.relation.label?.trim())throw Error('请填写版本名称和内容关系');
   if(r.relation.type!=='unverified'&&(!r.relation.note?.trim()||!/^https?:\/\//.test(r.relation.source||'')))throw Error('已核实内容关系须填写具体差异依据与来源');
   const seen=new Set([id]);let p=r.parentId;while(p){if(seen.has(p))throw Error('作品合并关系存在循环');seen.add(p);p=s.records[p]?.parentId;}
  }
 }
 if(s.schemaVersion===3)validateJournalIndex(s,validateStore);
 else if(s.schemaVersion===2)validateJournal(s,validateStore);
 else if(own(s,'journal'))throw Error('旧版基础库不能携带新版变更日志');
 return s;
}
export function upgradeStore(store){validateStore(store);return withJournal(store);}
// A source ID may occur more than once in the generated index. Render each stable
// identity once, and recover stored identity snapshots when the base index changes.
export function projectEntries(base,store,{includeChildren=false,includeDeleted=false}={}){
 validateStore(store);
 const known=new Set([...base,...store.additions].map(workKey));
 const snapshots=Object.entries(store.records)
  .filter(([id,r])=>!known.has(id)&&r.identity)
  .map(([id,r])=>({...r.identity,matchedWorkId:id,year:r.identity.firstYear??null,status:r.identity.mainPlacement||'identity-review'}));
 const all=[...base,...store.additions.map(w=>({...w,matchedWorkId:w.id,year:w.firstYear,status:'manual-basic'})),...snapshots];
 const identities=new Map();
 for(const w of all){
  const key=workKey(w),r=own(store.records,key)?store.records[key]:{},v=r.values||valuesOf(w);
  const row={...w,...v,...r.style,aliases:[...new Set([...(w.aliases||[]),...(r.aliases||[])])],year:v.firstYear,
   _key:key,_deleted:!!r.deleted,parentId:r.parentId||null,relation:r.relation||null};
  if(identities.has(key)){
   const original=identities.get(key);
   original.aliases=[...new Set([...(original.aliases||[]),w.title,...(w.aliases||[])])].filter(name=>name!==original.title);
   continue;
  }
  identities.set(key,row);
 }
 return [...identities.values()].filter(w=>(includeDeleted||!w._deleted)&&(includeChildren||!w.parentId));
}

// The first row is the canonical work. Every other row is an independent
// source/version identity, displayed only after opening the work.
export function versionGroup(entries,mainId){
 const main=entries.find(w=>w._key===mainId&&!w.parentId&&!w._deleted);
 if(!main)return [];
 const children=entries.filter(w=>w.parentId===mainId&&!w._deleted)
  .sort((a,b)=>(Number.isInteger(a.year)?a.year:Infinity)-(Number.isInteger(b.year)?b.year:Infinity)||
   String(a.title).localeCompare(String(b.title),'zh-Hans-CN'));
 return [main,...children];
}
export function projectRegistry(registry,store){
 const all=projectEntries(registry.works,store,{includeChildren:true}),children=new Map();
 for(const w of all)if(w.parentId){if(!children.has(w.parentId))children.set(w.parentId,[]);children.get(w.parentId).push(w);}
 const projected=all.filter(w=>!w.parentId);
 return {...registry,summary:{...registry.summary,accepted:projected.length},works:projected.map(w=>{
  const aliases=[...new Set([...(w.aliases||[]),...(children.get(w._key)||[]).flatMap(c=>[c.title,...(c.aliases||[])])])].filter(name=>name!==w.title);
  return {...w,aliases,indexId:w.indexId||w.id,firstYear:w.year,mainPlacement:w.mainPlacement||'promoted-basic'};
 })};
}
export function applyChange(store,base,action,meta){
 validateStore(store);
 if(meta.expectedRevision!==store.revision)throw Error('基础库已被其他页面修改，请重新读取后核对');
 if(!meta.actor||!meta.reason?.trim())throw Error('缺少操作人或修改说明');
 const next=clone(store),all=projectEntries(base,store,{includeChildren:true}),byId=new Map(all.map(w=>[w._key,w]));
 const touched=new Set(),added=[];
 const record=id=>{if(!byId.has(id))throw Error('作品不存在或已删除');touched.add(id);if(!own(next.records,id))Object.defineProperty(next.records,id,{value:{},enumerable:true,writable:true,configurable:true});const r=next.records[id];if(!r.identity){const old=byId.get(id);r.identity={id,indexId:old.indexId||old.id,aliases:old.aliases||[],...valuesOf(old),mainPlacement:old.status==='new-basic'?'identity-review':old.mainPlacement||old.status||'identity-review'};}return r;};
 if(action.type==='edit'){validateValues(action.values);const old=byId.get(action.id);if(!old)throw Error('作品不存在');const v=clone(action.values);const aliases=[...new Set([...(old.aliases||[]),...(next.records[action.id]?.aliases||[]),old.title])].filter(t=>t!==v.title);const r=record(action.id);Object.assign(r,{values:v,aliases});delete r.style;}
 else if(action.type==='style-update'){
  const {updates}=planStyleUpdates(all,action.rows);
  for(const update of updates)record(update.id).style=update.style;
 }else if(action.type==='add'){
  if(!Array.isArray(action.works)||!action.works.length||action.works.length>500)throw Error('每次新增1至500部作品');
  const keys=new Set(all.map(w=>nameKey(w.title)+'|'+w.year));const ids=new Set([...base,...store.additions].map(workKey));
  for(const w of action.works){validateValues(valuesOf(w));const key=nameKey(w.title)+'|'+w.firstYear;if(keys.has(key))throw Error('存在同名同年作品：'+w.title+'；请编辑或合并已有身份');if(ids.has(w.id)||!/^manual-[a-zA-Z0-9-]+$/.test(w.id))throw Error('新增作品ID冲突');keys.add(key);ids.add(w.id);added.push(w.id);next.additions.push(clone(w));}
 }else if(action.type==='delete'){
  if(all.some(w=>w.parentId===action.id))throw Error('主作品仍有关联版本，请先解除版本合并');record(action.id).deleted=true;
 }else if(action.type==='merge'){
  const main=byId.get(action.mainId);
  if(!main||main.parentId||main._deleted)throw Error('请选择未合并的主作品');
  if(!Array.isArray(action.ids))throw Error('关联版本列表无效');
  const children=[...new Set(action.ids)];
  if(!children.length||children.includes(action.mainId))throw Error('请选择主作品以外的版本');
  for(const id of children){
   const candidate=byId.get(id);
   if(!candidate||candidate._deleted||candidate.parentId)throw Error('只可合并尚未归属其他主作品的有效记录：'+id);
  }
  record(action.mainId);
  for(const id of children){
   const r=record(id);r.parentId=action.mainId;r.relation={...clone(action.relation),label:byId.get(id).title};
   for(const w of all)if(w.parentId===id){const child=record(w._key);child.parentId=action.mainId;}
  }
 }else if(action.type==='detach'){
  if(!byId.get(action.id)?.parentId)throw Error('该作品没有可解除的合并关系');
  const r=record(action.id);r.parentId=null;delete r.relation;}
 else throw Error('不支持的操作');
 const changes=[...touched].map(id=>({id,before:own(store.records,id)?clone(store.records[id]):null,after:clone(next.records[id])}));
 if(!added.length&&changes.every(c=>JSON.stringify(c.before)===JSON.stringify(c.after)))throw Error('没有实际修改');
 next.revision++;next.recent.push({id:meta.id,at:meta.at,actor:meta.actor,reason:meta.reason,changes,added});next.recent=next.recent.slice(-3);
 appendJournal(store,next,meta,action.type,meta.intent||action);
 validateStore(next);return next;
}
export function undoLast(store,revision,meta){
 validateStore(store);if(revision!==store.revision)throw Error('基础库已变化，请重新读取');if(!store.recent.length)throw Error('没有可撤销的操作');
 const next=clone(store),last=next.recent.pop();for(const c of last.changes){if(c.before===null)delete next.records[c.id];else next.records[c.id]=clone(c.before);}next.additions=next.additions.filter(w=>!last.added.includes(w.id));next.revision++;
 if(store.schemaVersion===2||store.schemaVersion===3){
  if(!meta)throw Error('撤销缺少操作身份');
  appendJournal(store,next,meta,'undo',{type:'undo',targetId:last.id});
 }
 validateStore(next);return next;
}
export function planStyleUpdates(works,rows){
 if(!Array.isArray(rows)||!rows.length||rows.length>500)throw Error('每批须选择1至500部作品');
 const seen=new Set(),byId=new Map(works.map(w=>[w._key,w])),updates=[],unchanged=[];
 for(const row of rows){
  if(!row.id||seen.has(row.id))throw Error('作品ID缺失或重复：'+row.id);
  seen.add(row.id);
  const work=byId.get(row.id);
  if(!work||work._deleted)throw Error('作品不存在或已删除：'+row.id);
  if(row.title&&row.title!==work.title)throw Error('作品名称与当前ID不符：'+row.id+' · '+work.title);
  if(!['fill','append','set','remove'].includes(row.mode))throw Error('无效的标签操作');
  validateStyleTags(row.tags,{allowClear:row.mode==='set'});
  if(row.evidence)validateStyleEvidence(row.evidence,row.tags);
  const {tags:before,legacy}=styleState(work),after={...before};
  const evidence=new Map(styleEvidenceEntries(before,work.plotTagEvidence));
  const incoming=new Map(styleEvidenceEntries(row.tags,row.evidence));
  let changed=false;
  for(const [key,value] of Object.entries(row.tags)){
   const old=styleList(before[key]),wanted=styleList(value);
   if(row.mode==='fill'&&old.length)continue;
   const next=row.mode==='remove'?old.filter(tag=>!wanted.includes(tag)):
    row.mode==='append'?[...new Set([...old,...wanted])]:wanted;
   if(old.length===next.length&&old.every(tag=>next.includes(tag)))continue;
   changed=true;
   if(next.length)after[key]=styleValue(next);
   else delete after[key];
   for(const tag of next)if(!old.includes(tag)&&incoming.has(tag))evidence.set(tag,incoming.get(tag));
  }
  if(!changed){unchanged.push({id:row.id,title:work.title});continue;}
  try{validateStyleTags(after);}catch(error){throw Error(work.title+'：'+error.message);}
  const selected=styleLabels(after);
  const style={plotStyles:legacy.filter(tag=>!selected.includes(styleName(tag))),plotTags:after,plotTagEvidence:packStyleEvidence(after,evidence)};
  validateStyles(style);
  updates.push({id:row.id,title:work.title,before,after,style});
 }
 return {updates,unchanged};
}
