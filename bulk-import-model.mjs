import {nameKey, validURL, makeNewWork, validateNewBundle, nextWorkId, same} from './management-model.mjs';

export const REGISTRY_FILE='main-adv-rpg-works-20261031.json';
const names=w=>[w.title,w.originalTitle,w.chineseTitle,...(w.aliases||[]),...(w.titleAliases||[])].map(nameKey).filter(Boolean);
const refs=w=>(w.sourceRefs||[]).map(x=>String(x).toLowerCase());
const add=(map,key,w)=>{if(!map.has(key))map.set(key,[]);map.get(key).push(w);};
export function scanRegistry(registry,reserved){
 const byName=new Map(),byRef=new Map(),basicNames=new Map(),basicRefs=new Map();
 for(const w of reserved){for(const n of names(w))add(byName,n,w);for(const r of refs(w))add(byRef,r,w);}
 for(const w of registry.works.filter(w=>w.mainPlacement==='promoted-basic')){for(const n of names(w))add(basicNames,n,w);for(const r of refs(w))add(basicRefs,r,w);}
 return registry.works.map(w=>{
  const matches=[...new Map([...reserved.filter(r=>r.basicRegistryId===w.indexId||r.id===w.linkedRecordId),...names(w).flatMap(n=>byName.get(n)||[]),...refs(w).flatMap(r=>byRef.get(r)||[])].map(r=>[r.id,r])).values()];
  let status='available',reason='身份可补录，需补齐原作及首发证据';
  if(matches.length){status=matches.length===1&&matches[0].firstYear===w.firstYear?'existing':'conflict';reason=status==='existing'?'已有作品身份，跳过新增':'名称、别名或外部身份碰撞／年份冲突';}
  else if(w.mainPlacement!=='promoted-basic'){status='conflict';reason='已关联专题或其他身份，需复用原档案';}
  else if([...names(w).flatMap(n=>basicNames.get(n)||[]),...refs(w).flatMap(r=>basicRefs.get(r)||[])].some(r=>r.indexId!==w.indexId)){status='conflict';reason='基础库内部名称／外部身份重复，需核对';}
  else if(!w.indexId||!validURL(w.source)||!Number.isInteger(w.firstYear)||w.firstYear<1976||w.firstYear>new Date().getFullYear()){status='conflict';reason='基础身份缺少有效来源或年份';}
  return {work:w,status,reason,matches};
 });
}
export function emptyValues(w){return {title:w.title,originalTitle:w.title,year:String(w.firstYear),source:w.source,category:'',subcategory:'',genre:'',synopsis:'',characters:'',notes:'',modes:['待核实'],'interaction-note':'','interaction-sources':w.source,'content-evidence':'','content-source':'',platforms:'',publisher:'',voice:'未核实','release-evidence':'','release-source':''};}
export function makeBasicBundle(record,id,taxonomy){
 const {identity:w,values:v}=record;
 if(!record.confirmed)throw Error('尚未确认独立作品、收录范围及首批证据');
 if(Number(v.year)!==w.firstYear)throw Error('年份与基础身份不一致，请先核查基础库');
 if(![v.title,v.originalTitle].some(n=>names(w).includes(nameKey(n))))throw Error('名称与基础身份不匹配');
 if(!taxonomy.subcategories[v.category]?.includes(v.subcategory)||['纯文本指令','图文指令'].includes(v.subcategory))throw Error('请选择符合主库范围的主／细分类');
 if(!Array.isArray(v.modes)||!v.modes.every(m=>m in taxonomy.interactionModes))throw Error('玩法标签无效');
 if(typeof v.characters!=='string'||v.characters.includes('待核实'))throw Error('主要角色需要实际资料');
 const b=makeNewWork({...v,'work-id':id},taxonomy);
 b.work.basicRegistryId=w.indexId;b.work.titleAliases=[...(w.aliases||[])];b.work.sourceRefs=[...(w.sourceRefs||[])];
 validateNewBundle(b);return b;
}
export function prepareBulk(records,scan,reserved,taxonomy,reason,date){
 const errors=[],ready=[],all=[...reserved],seen=new Set(),lookup=new Map(scan.map(r=>[r.work.indexId,r]));
 for(const row of records){try{
  const id=row.identity?.indexId;if(seen.has(id))throw Error('队列内身份重复');seen.add(id);
  const current=lookup.get(id);if(!current||current.status!=='available')throw Error(current?.reason||'基础身份已不存在');
  if(!same(current.work,row.identity))throw Error('基础身份已变化，请移除后重新选择');
  const b=makeBasicBundle(row,nextWorkId(all),taxonomy);
  const hit=all.find(w=>names(w).some(n=>names(b.work).includes(n))||refs(w).some(r=>refs(b.work).includes(r)));
  if(hit)throw Error('与作品 '+hit.id+' 重复，请复用身份');
  all.push(b.work);ready.push({resource:'newWork',key:b.work.id,before:null,after:b});
 }catch(e){errors.push({id:row.identity?.indexId,title:row.identity?.title,message:e.message});}}
 const packages=[];
 for(const op of ready){let p=packages.at(-1);if(!p||p.operations.length===30||JSON.stringify({...p,operations:[...p.operations,op]}).length>60000){p={schemaVersion:1,createdAt:date,reason,operations:[]};packages.push(p);}p.operations.push(op);if(JSON.stringify(p).length>60000)errors.push({id:op.after.work.basicRegistryId,title:op.after.work.title,message:'单部作品超过60000字符，请精简资料'});}
 return {packages,errors,ready:ready.length};
}
export function mergeMetadata(current,incoming,scan){
 if(incoming.schemaVersion!==1||!Array.isArray(incoming.records)||incoming.records.length>500)throw Error('请使用本页导出的批量资料模板（最多500部）');
 const result=structuredClone(current),seen=new Set(),lookup=new Map(scan.map(r=>[r.work.indexId,r]));
 for(const row of incoming.records){const id=row.identity?.indexId;if(!id||seen.has(id))throw Error('资料文件中身份缺失或重复');seen.add(id);const live=lookup.get(id);if(!live||live.status!=='available')throw Error(id+' 已有身份或发生冲突，请重新读取');if(!same(row.identity,live.work))throw Error(id+' 基础身份已变化，请重新导出');if(!row.values||typeof row.values!=='object'||Array.isArray(row.values)||typeof row.confirmed!=='boolean')throw Error(id+' 缺少 values／confirmed 字段');const clean=emptyValues(live.work);for(const k of Object.keys(clean)){const v=row.values[k];if(k==='modes'){if(!Array.isArray(v)||!v.every(x=>typeof x==='string'))throw Error('玩法须为字符串数组');clean[k]=v;}else if(typeof v!=='string')throw Error(k+' 须为文本');else clean[k]=v;}const item={identity:structuredClone(live.work),values:clean,confirmed:row.confirmed};const i=result.findIndex(x=>x.identity.indexId===id);if(i<0)result.push(item);else result[i]=item;}
 return result;
}
