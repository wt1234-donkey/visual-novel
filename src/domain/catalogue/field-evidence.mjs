import {journalKey} from './journal.mjs';
import {isRecordedYear,isPublishedYear} from './dates.mjs';
const copy=structuredClone,same=(a,b)=>journalKey(a)===journalKey(b),object=v=>v&&typeof v==='object'&&!Array.isArray(v);
const fail=m=>{throw Error('字段证据：'+m);};
const id=v=>typeof v==='string'&&v.length>0&&v.length<=500&&!['__proto__','constructor','prototype'].includes(v);
const text=(v,n=500)=>typeof v==='string'&&v.trim().length>0&&v.length<=n;
const exact=(v,keys)=>{if(!object(v)||Object.keys(v).some(k=>!keys.includes(k)))fail('字段格式无效');};
const urls=v=>Array.isArray(v)&&v.length<=100&&v.every(u=>typeof u==='string'&&/^https?:\/\//.test(u)&&u.length<=4096);
export const FIELD_DEFINITIONS={work:{title:'显示名称',firstYear:'登记年份',group:'作品厂商／创作主体',writerNames:'剧作姓名',artistNames:'美术姓名',musicianNames:'音乐姓名'},content:{label:'内容名称',firstYear:'内容首次年份'},release:{year:'发行年份',publisher:'该次发行原署名',platform:'发行平台'}};
export const emptyFieldStore=()=>({schemaVersion:1,revision:0,assertions:{},choices:{},events:[]});
export const scopeKey=s=>JSON.stringify([s.type,s.workId,s.id]);
export const fieldKey=(s,f)=>JSON.stringify([s.type,s.workId,s.id,f]);
export function validateFieldScope(scope,field){exact(scope,['type','workId','id']);if(!Object.hasOwn(FIELD_DEFINITIONS,scope.type)||!Object.hasOwn(FIELD_DEFINITIONS[scope.type],field)||!id(scope.workId)||!id(scope.id)||scope.type==='work'&&scope.id!==scope.workId)fail('适用范围或字段无效');}
export function validateAssertion(a){
 exact(a,['id','scope','field','value','sources','sourceIds','status','subjects']);if(!id(a.id))fail('断言ID无效');validateFieldScope(a.scope,a.field);
 if(['firstYear','year'].includes(a.field)){if(!isRecordedYear(a.value)||a.field==='year'&&!isPublishedYear(a.value))fail('年份不符合登记／实际发行契约');}
 else if(a.field.endsWith('Names')){if(!Array.isArray(a.value)||a.value.length>100||a.value.some(v=>!text(v,200))||new Set(a.value).size!==a.value.length)fail('姓名须为不重复的文本数组');}
 else if(!text(a.value))fail('字段值须为非空文本');
 if(!urls(a.sources)||!Array.isArray(a.sourceIds)||a.sourceIds.length>100||a.sourceIds.some(v=>!id(v))||new Set(a.sourceIds).size!==a.sourceIds.length)fail('来源记录或URL无效');
 if(!['unverified','supported','disputed','manual'].includes(a.status)||!a.field.endsWith('Names')&&a.status==='manual')fail('核查状态无效');
 if(!a.sources.length&&!a.sourceIds.length&&(!a.field.endsWith('Names')||a.status!=='manual'))fail('请提供来源；无来源姓名保留为手动添加／未附证据');
 if(!Array.isArray(a.subjects)||a.subjects.length>20)fail('主体链接格式无效');
 for(const s of a.subjects){exact(s,['kind','id','signature']);if(!['entity','person'].includes(s.kind)||!id(s.id)||!text(s.signature,300))fail('主体须使用明确ID与原始署名');}
 return a;
}
function expectedChanges(store,action,meta,events){
 exact(action,{assert:['type','assertion'],select:['type','assertionId'],clear:['type','scope','field'],undo:['type','targetId']}[action?.type]||[]);
 const change=(table,key,after)=>({table,id:key,before:copy(store[table][key]??null),after:copy(after)});
 if(action.type==='assert'){validateAssertion(action.assertion);if(Object.hasOwn(store.assertions,action.assertion.id)||events.some(e=>e.type==='assert'&&e.intent.assertion.id===action.assertion.id))fail('断言ID已存在；原始断言不能覆盖');return [change('assertions',action.assertion.id,action.assertion)];}
 if(action.type==='select'){
  const a=store.assertions[action.assertionId];if(!a)fail('待选断言不存在');if(a.status==='disputed')fail('争议断言须先补充新的核对依据，不能直接采用');
  return [change('choices',fieldKey(a.scope,a.field),{assertionId:a.id,operationId:meta.id,actor:meta.actor,at:meta.at,reason:meta.reason})];
 }
 if(action.type==='clear'){validateFieldScope(action.scope,action.field);const key=fieldKey(action.scope,action.field);if(!store.choices[key])fail('该字段没有显式选用结论');return [change('choices',key,null)];}
 if(action.type==='undo'){
  const e=events.find(e=>e.id===action.targetId);if(!e)fail('撤销目标不存在');
  for(const c of e.changes)if(!same(store[c.table][c.id]??null,c.after))fail('该字段在此后已有修改，不能覆盖后续结论');
  return e.changes.map(c=>({...copy(c),before:copy(c.after),after:copy(c.before)}));
 }
 fail('不支持的命令');
}
function applyChanges(s,changes){for(const c of changes){if(c.after===null)delete s[c.table][c.id];else Object.defineProperty(s[c.table],c.id,{value:copy(c.after),writable:true,enumerable:true,configurable:true});}}
function checkChoices(s){for(const [key,c] of Object.entries(s.choices)){const a=s.assertions[c.assertionId];if(!a||fieldKey(a.scope,a.field)!==key)fail('选用结论引用了不存在或不同范围的断言');}}
export function validateFieldStore(s){
 exact(s,['schemaVersion','revision','assertions','choices','events']);if(s.schemaVersion!==1||!Number.isSafeInteger(s.revision)||s.revision<0||!object(s.assertions)||!object(s.choices)||!Array.isArray(s.events))fail('日志格式无效');
 const replay=emptyFieldStore(),seen=new Set();
 for(const e of s.events){
  exact(e,['schemaVersion','id','type','intent','actor','at','reason','sources','previousRevision','revision','changes','undoOf']);
  if(e.schemaVersion!==1||!id(e.id)||seen.has(e.id)||!id(e.actor)||!Number.isFinite(Date.parse(e.at))||!text(e.reason,1000)||e.reason.trim().length<5||!urls(e.sources)||e.previousRevision!==replay.revision||e.revision!==replay.revision+1||e.type!==e.intent?.type||!Array.isArray(e.changes))fail('事件身份、依据或连续性无效');
  if(e.type==='undo'&&e.undoOf!==e.intent.targetId||e.type!=='undo'&&e.undoOf!==undefined)fail('撤销记录不匹配');
  const expected=expectedChanges(replay,e.intent,{...e,id:e.id},replay.events);if(!same(e.changes,expected))fail('事件前后值与命令不匹配');
  applyChanges(replay,expected);checkChoices(replay);replay.revision=e.revision;replay.events.push(e);seen.add(e.id);
 }
 if(!same({revision:replay.revision,assertions:replay.assertions,choices:replay.choices},{revision:s.revision,assertions:s.assertions,choices:s.choices}))fail('完整回放与当前状态不一致');
 return s;
}
export function validateFieldReferences(store,context){
 validateFieldStore(store);
 for(const a of Object.values(store.assertions)){
  context.target(a.scope);
  if(a.sourceIds.some(id=>!context.sources.has(id)))fail('引用未知来源记录');
  for(const subject of a.subjects)if(!context.subjects[subject.kind]?.has(subject.id))fail('主体ID不存在；名称相同不能替代明确ID');
 }
 return store;
}
export function applyFieldCommand(store,context,action,meta){
 validateFieldStore(store);const old=store.events.find(e=>e.id===meta.id);
 if(old){if(!same(old.intent,action)||old.actor!==meta.actor||old.at!==meta.at||old.reason!==meta.reason?.trim()||!same(old.sources,meta.sources))fail('操作ID用于不同命令');return copy(store);}
 if(meta.expectedRevision!==store.revision)fail('字段证据修订已变化，请重新读取');
 const next=copy(store),entry={schemaVersion:1,id:meta.id,type:action.type,intent:copy(action),actor:meta.actor,at:meta.at,reason:meta.reason?.trim(),sources:copy(meta.sources),previousRevision:store.revision,revision:store.revision+1,
  changes:expectedChanges(store,action,{...meta,reason:meta.reason?.trim()},store.events),...(action.type==='undo'?{undoOf:action.targetId}:{})};
 applyChanges(next,entry.changes);next.revision++;next.events.push(entry);return validateFieldReferences(next,context);
}
export function fieldHistory(s,{workId=null,before=Infinity,limit=20}={}){
 if(!Number.isSafeInteger(limit)||limit<1||limit>100)fail('历史分页范围无效');
 const rows=s.events.filter(e=>e.revision<before&&(!workId||e.changes.some(c=>c.table==='assertions'?(c.after||c.before).scope.workId===workId:JSON.parse(c.id)[1]===workId))).reverse();return {events:copy(rows.slice(0,limit)),nextBefore:rows.length>limit?rows[limit-1].revision:null};
}
export function fieldProjection(store=emptyFieldStore(),aliases={}){
 validateFieldStore(store);const selected={};for(const c of Object.values(store.choices)){const a=store.assertions[c.assertionId];(selected[scopeKey(a.scope)]??={})[a.field]={...copy(a),selection:copy(c)};}
 return {selected,aliases};
}
export function chosenFields(plan={},type,workId,id=workId){const canonical=plan.aliases?.[workId]||workId;return plan.selected?.[scopeKey({type,workId:canonical,id:type==='work'?canonical:id})]||{};}
export function applyFieldValues(row,fields,{basic=false}={}){
 if(!Object.keys(fields).length)return row;
 const next={...row},fieldBase={},evidence={};
 for(const [key,a] of Object.entries(fields)){fieldBase[key]=copy(row[key]??null);next[key]=copy(a.value);evidence[key]=copy(a);
  if(key==='title'){fieldBase.displayTitle=row.displayTitle??null;next.displayTitle=a.value;next.titleAliases=[...new Set([...(row.titleAliases||[]),row.title,row.sourceTitle].filter(Boolean))];if(basic)next.aliases=[...new Set([...(row.aliases||[]),row.title].filter(v=>v&&v!==a.value))];}
  if(key==='firstYear'){fieldBase.yearStatus=row.yearStatus??null;next.yearStatus=a.status==='supported'&&isPublishedYear(a.value)?'published':'unverified';if(basic){fieldBase.year=row.year??null;next.year=a.value;}}
 }
 return {...next,fieldBase,fieldEvidence:evidence};
}
export function projectChosenBasicRow(row){return applyFieldValues(row,row.fieldEvidence||{},{basic:true});}
export function choiceBase(row){const out={...row,...row.fieldBase};delete out.fieldEvidence;delete out.fieldBase;return out;}
export const csvCell=v=>'"'+String(v??'').replace(/"/g,'""')+'"';
export function evidenceCsv(store){
 const header=['断言ID','作品ID','范围','范围ID','字段','候选值','核查状态','来源记录ID','来源URL','主体显式链接','是否当前选用','选用理由','选用操作ID'];
 return '\ufeff'+[header,...Object.values(store.assertions).map(a=>{const c=store.choices[fieldKey(a.scope,a.field)];return [a.id,a.scope.workId,a.scope.type,a.scope.id,a.field,Array.isArray(a.value)?a.value.join('；'):a.value,a.status,a.sourceIds.join('；'),a.sources.join('；'),a.subjects.map(s=>s.signature+' → '+s.kind+':'+s.id).join('；'),c?.assertionId===a.id?'是':'否',c?.assertionId===a.id?c.reason:'',c?.assertionId===a.id?c.operationId:''];})].map(row=>row.map(csvCell).join(',')).join('\n')+'\n';
}
export const assertionValueKey=a=>journalKey({value:a.value,subjects:[...a.subjects].sort((a,b)=>(a.kind+':'+a.id).localeCompare(b.kind+':'+b.id))});
export function fieldCounts(store){const fields=new Map();for(const a of Object.values(store.assertions)){const key=fieldKey(a.scope,a.field);if(!fields.has(key))fields.set(key,new Set());fields.get(key).add(assertionValueKey(a));}return {assertions:Object.keys(store.assertions).length,selections:Object.keys(store.choices).length,conflicts:[...fields.values()].filter(s=>s.size>1).length,events:store.events.length,revision:store.revision};}
