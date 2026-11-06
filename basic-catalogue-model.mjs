// Shared, additive basic-catalogue edits. Original source records remain auditable.
export const emptyStore=()=>({schemaVersion:1,revision:0,additions:[],records:{},recent:[]});
export const workKey=w=>w.matchedWorkId||w.registryId||w.id;
export const nameKey=s=>String(s||'').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');
export const STYLE_GROUPS={
 '情感与关系':['恋爱','纯爱','日常','青春','成长','亲情','友情','百合','耽美','群像','三角关系','病娇'],
 '氛围与情绪':['喜剧','轻松','温情','治愈','催泪','感伤','致郁','悲剧','黑暗','热血','燃系','唯美'],
 '悬疑与冲突':['悬疑','推理','惊悚','恐怖','猎奇','心理','犯罪','复仇','生存','战争'],
 '幻想与冒险':['冒险','史诗','奇幻','科幻','魔幻现实','超自然','历史','武侠','末世','赛博朋克'],
 '表达与思考':['荒诞','讽刺','黑色幽默','哲思','意识流','实验性','元叙事'],
 '成人与禁忌题材':['成人向','色情','背德','禁忌关系','NTR','乱伦'],
 '其他':['其他']
};
export const STYLE_OPTIONS=Object.values(STYLE_GROUPS).flat();
const clone=x=>structuredClone(x);
const own=(obj,k)=>Object.hasOwn(obj,k);
const fields=['title','firstYear','group','gameplay','plotStyles','source'];
export function validateValues(v){
 if(!v||typeof v!=='object'||Object.keys(v).some(k=>!fields.includes(k)))throw Error('作品字段无效');
 for(const k of ['title','group','gameplay'])if(typeof v[k]!=='string'||!v[k].trim()||v[k].length>500)throw Error('名称、厂商和主要玩法不能为空，且须少于500字');
 if(v.firstYear!==null&&(!Number.isInteger(v.firstYear)||v.firstYear<1970||v.firstYear>new Date().getFullYear()+10))throw Error('年份须为1970年至未来10年内的整数，未知请留空');
 if(!Array.isArray(v.plotStyles)||v.plotStyles.length>3||new Set(v.plotStyles).size!==v.plotStyles.length||v.plotStyles.some(s=>typeof s!=='string'||!s.trim()||s.length>30))throw Error('剧情风格最多3个，每个不超过30字且不重复');
 if(typeof v.source!=='string')throw Error('来源格式无效');
 if(v.source){try{if(!['https:','http:'].includes(new URL(v.source).protocol))throw Error();}catch{throw Error('来源须为 http 或 https 网址');}}
 return v;
}
export function valuesOf(w){return {title:w.title,firstYear:w.firstYear??w.year??null,group:w.group||'厂商待核',gameplay:w.gameplay||'玩法待核',plotStyles:[...(w.plotStyles||[])],source:w.source||''};}
export function validateStore(s){
 if(!s||s.schemaVersion!==1||!Number.isSafeInteger(s.revision)||s.revision<0||!Array.isArray(s.additions)||!s.records||typeof s.records!=='object'||Array.isArray(s.records)||!Array.isArray(s.recent)||s.recent.length>3)throw Error('基础库修改记录格式无效');
 const ids=new Set();for(const w of s.additions){if(!/^manual-[a-zA-Z0-9-]+$/.test(w.id)||ids.has(w.id))throw Error('新增作品ID无效或重复');ids.add(w.id);validateValues(valuesOf(w));}
 for(const [id,r] of Object.entries(s.records)){
  if(!id||!r||typeof r!=='object'||Array.isArray(r)||['__proto__','constructor','prototype'].includes(id))throw Error('修改记录无效');
  if(r.values)validateValues(r.values);
  if(r.deleted!==undefined&&typeof r.deleted!=='boolean')throw Error('删除标记无效');
  if(r.parentId!==undefined&&r.parentId!==null){
   if(typeof r.parentId!=='string'||!r.parentId||r.parentId===id)throw Error('作品不能合并到自身');
   if(!r.relation||!['unverified','same','added'].includes(r.relation.type)||!r.relation.label?.trim())throw Error('请填写版本名称和内容关系');
   if(r.relation.type!=='unverified'&&(!r.relation.note?.trim()||!/^https?:\/\//.test(r.relation.source||'')))throw Error('已核实内容关系须填写具体差异依据与来源');
   const seen=new Set([id]);let p=r.parentId;while(p){if(seen.has(p))throw Error('作品合并关系存在循环');seen.add(p);p=s.records[p]?.parentId;}
  }
 }
 return s;
}
export function projectEntries(base,store,{includeChildren=false,includeDeleted=false}={}){
 validateStore(store);
 const all=[...base,...store.additions.map(w=>({...w,matchedWorkId:w.id,year:w.firstYear,status:'manual-basic'}))];
 return all.map(w=>{const key=workKey(w),r=own(store.records,key)?store.records[key]:{};const v=r.values||valuesOf(w);return {...w,...v,aliases:[...new Set([...(w.aliases||[]),...(r.aliases||[])])],year:v.firstYear,_key:key,_deleted:!!r.deleted,parentId:r.parentId||null,relation:r.relation||null};}).filter(w=>(includeDeleted||!w._deleted)&&(includeChildren||!w.parentId));
}
export function projectRegistry(registry,store){
 const known=new Set([...registry.works,...store.additions].map(workKey));const missing=Object.entries(store.records).filter(([id,r])=>!known.has(id)&&r.identity).map(([,r])=>r.identity);
 const all=projectEntries([...registry.works,...missing],store,{includeChildren:true}),children=new Map();for(const w of all)if(w.parentId){if(!children.has(w.parentId))children.set(w.parentId,[]);children.get(w.parentId).push(w);}
 const projected=all.filter(w=>!w.parentId);
 return {...registry,summary:{...registry.summary,accepted:projected.length},works:projected.map(w=>({...w,aliases:[...new Set([...(w.aliases||[]),...(children.get(w._key)||[]).flatMap(c=>[c.title,...(c.aliases||[])])])],indexId:w.indexId||w.id,firstYear:w.year,mainPlacement:w.mainPlacement||'promoted-basic'}))};
}
export function applyChange(store,base,action,meta){
 validateStore(store);
 if(meta.expectedRevision!==store.revision)throw Error('基础库已被其他页面修改，请重新读取后核对');
 if(!meta.actor||!meta.reason?.trim())throw Error('缺少操作人或修改说明');
 const next=clone(store),all=projectEntries(base,store,{includeChildren:true}),byId=new Map(all.map(w=>[w._key,w]));
 const touched=new Set(),added=[];
 const record=id=>{if(!byId.has(id))throw Error('作品不存在或已删除');touched.add(id);if(!own(next.records,id))Object.defineProperty(next.records,id,{value:{},enumerable:true,writable:true,configurable:true});const r=next.records[id];if(!r.identity){const old=byId.get(id);r.identity={id,indexId:old.indexId||old.id,aliases:old.aliases||[],...valuesOf(old),mainPlacement:old.status==='new-basic'?'identity-review':old.mainPlacement||old.status||'identity-review'};}return r;};
 if(action.type==='edit'){validateValues(action.values);const old=byId.get(action.id);if(!old)throw Error('作品不存在');const v=clone(action.values);const aliases=[...new Set([...(old.aliases||[]),...(next.records[action.id]?.aliases||[]),old.title])].filter(t=>t!==v.title);Object.assign(record(action.id),{values:v,aliases});}
 else if(action.type==='add'){
  if(!Array.isArray(action.works)||!action.works.length||action.works.length>500)throw Error('每次新增1至500部作品');
  const keys=new Set(all.map(w=>nameKey(w.title)+'|'+w.year));const ids=new Set([...base,...store.additions].map(workKey));
  for(const w of action.works){validateValues(valuesOf(w));const key=nameKey(w.title)+'|'+w.firstYear;if(keys.has(key))throw Error('存在同名同年作品：'+w.title+'；请编辑或合并已有身份');if(ids.has(w.id)||!/^manual-[a-zA-Z0-9-]+$/.test(w.id))throw Error('新增作品ID冲突');keys.add(key);ids.add(w.id);added.push(w.id);next.additions.push(clone(w));}
 }else if(action.type==='delete'){
  if(all.some(w=>w.parentId===action.id))throw Error('主作品仍有关联版本，请先解除版本合并');record(action.id).deleted=true;
 }else if(action.type==='merge'){
  const main=byId.get(action.mainId);if(!main||main.parentId)throw Error('请选择未合并的主作品');record(action.mainId);
  const children=[...new Set(action.ids)];if(!children.length||children.includes(action.mainId))throw Error('请选择主作品以外的版本');
  for(const id of children){const r=record(id);r.parentId=action.mainId;r.relation={...clone(action.relation),label:byId.get(id).title};for(const w of all)if(w.parentId===id){const child=record(w._key);child.parentId=action.mainId;}}
 }else if(action.type==='detach'){const r=record(action.id);r.parentId=null;delete r.relation;}
 else throw Error('不支持的操作');
 const changes=[...touched].map(id=>({id,before:own(store.records,id)?clone(store.records[id]):null,after:clone(next.records[id])}));
 if(!added.length&&changes.every(c=>JSON.stringify(c.before)===JSON.stringify(c.after)))throw Error('没有实际修改');
 next.revision++;next.recent.push({id:meta.id,at:meta.at,actor:meta.actor,reason:meta.reason,changes,added});next.recent=next.recent.slice(-3);
 validateStore(next);return next;
}
export function undoLast(store,revision){
 validateStore(store);if(revision!==store.revision)throw Error('基础库已变化，请重新读取');if(!store.recent.length)throw Error('没有可撤销的操作');
 const next=clone(store),last=next.recent.pop();for(const c of last.changes){if(c.before===null)delete next.records[c.id];else next.records[c.id]=clone(c.before);}next.additions=next.additions.filter(w=>!last.added.includes(w.id));next.revision++;validateStore(next);return next;
}
export const CSV_HEADERS=['名称','年份','厂商','主要玩法','剧情风格1','剧情风格2','剧情风格3','来源'];
export function parseCSV(text){
 const rows=[];let row=[],value='',quoted=false;const t=text.replace(/^\uFEFF/,'');
 for(let i=0;i<t.length;i++){const c=t[i];if(c==='"'){if(quoted&&t[i+1]==='"'){value+='"';i++;}else if(quoted)quoted=false;else if(!value)quoted=true;else throw Error('CSV引号格式无效');}else if(!quoted&&(c===','||c==='\n'||c==='\r')){row.push(value);value='';if(c!==','){if(c==='\r'&&t[i+1]==='\n')i++;rows.push(row);row=[];}}else value+=c;}
 if(quoted)throw Error('CSV引号未闭合');if(value||row.length){row.push(value);rows.push(row);}return rows.filter(r=>r.some(v=>v.trim()));
}
export function parseImport(text,format){
 let input;if(format==='json'){input=JSON.parse(text);if(!Array.isArray(input))throw Error('JSON须为作品数组');}
 else{const [header,...rows]=parseCSV(text);if(!header||header.join('|')!==CSV_HEADERS.join('|'))throw Error('CSV表头须与下载模板完全一致');input=rows.map((r,i)=>{if(r.length!==8)throw Error('第'+(i+2)+'行列数须为8');return {title:r[0].trim(),firstYear:r[1].trim()?Number(r[1]):null,group:r[2].trim(),gameplay:r[3].trim(),plotStyles:[...new Set(r.slice(4,7).map(s=>s.trim()).filter(Boolean))],source:r[7].trim()};});}
 if(!input.length||input.length>500)throw Error('每次导入1至500部作品');return input.map((w,i)=>{try{return validateValues(w);}catch(e){throw Error('第'+(i+1)+'部：'+e.message);}});
}
