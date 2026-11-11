import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {createEditClient,TOKEN_SETUP_URL} from '../work-edit-api.mjs';
import {same,lines,validURL} from '../management-model.mjs';
import {editableValues,projectWork,saveEdit,saveCreatorNames,undoEdit,changedFields,validateHistory,CREATOR_NAME_FIELDS} from '../work-edit-model.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name+'.json',import.meta.url),'utf8'));
const base=read('games').works.find(w=>w.id==='g039'),taxonomy=read('taxonomy');
const empty=()=>({schemaVersion:1,records:{}});
function saved(){const after=editableValues(base);after.notes='已保存的网页更正记录';return saveEdit(empty(),base,after,{id:'test-edit',actor:'test-user',at:'2026-11-04T08:00:00Z',reason:'已核对的网页更正',sources:[base.source],expectedRevision:0},taxonomy,[base]);}
async function harness({published=saved(),publishedStatus=200,latest=published}={}){
 const elements=new Map(),calls=[],handlers={},formValues={},events=[];
 const element=selector=>{if(!elements.has(selector))elements.set(selector,{selector,innerHTML:'',textContent:'',className:'',value:'',open:true,focus(){},querySelector:element,disabled:false});return elements.get(selector);};
 const dialog={innerHTML:'',open:false,setAttribute(){},addEventListener(type,fn){handlers[type]=fn;},showModal(){this.open=true;},close(){this.open=false;},querySelector:element,querySelectorAll:()=>[]};
 const document={createElement:tag=>tag==='dialog'?dialog:{},head:{append(){}},body:{append(){}}};
 const fetcher=async(url,options={})=>{
  calls.push({url,options});
  if(url.startsWith('https://api.github.com')){
   if(!options.headers?.Authorization)return {ok:false,status:403,headers:new Headers(),json:async()=>({message:'API rate limit exceeded'})};
   if(options.method==='PUT'){latest=JSON.parse(Buffer.from(JSON.parse(options.body).content,'base64').toString('utf8'));return {ok:true,status:200,json:async()=>({content:{sha:'saved-sha'},commit:{sha:'saved-commit'}})};}
   const data=url.endsWith('/user')?{login:'wt1234-donkey'}:url.endsWith('/visual-novel')?{permissions:{push:true}}:{sha:'latest-sha',content:Buffer.from(JSON.stringify(latest)).toString('base64')};
   return {ok:true,status:200,headers:new Headers(),json:async()=>data};
  }
  const data=url.includes('work-edit-history')?published:url.includes('games.json')?{works:[base]}:url.includes('supplement')?{works:[]}:url.includes('taxonomy')?taxonomy:{companies:[]};
  return {ok:url.includes('work-edit-history')?publishedStatus===200:true,status:url.includes('work-edit-history')?publishedStatus:200,json:async()=>structuredClone(data)};
 };
 const context=vm.createContext({readPublishedSource:async path=>(await fetcher('./'+path)).json(),loadEffectiveCatalogue:async()=>({raw:{main:{works:[base]},supplement:{works:[]},history:publishedStatus===200?structuredClone(published):{invalid:true}},sourceLease:null}),document,fetch:fetcher,console,structuredClone,crypto:globalThis.crypto,confirm:()=>true,same,lines,validURL,editableValues,projectWork,saveEdit,saveCreatorNames,undoEdit,changedFields,validateHistory,CREATOR_NAME_FIELDS,window:{dispatchEvent:e=>events.push(e)},CustomEvent:class {constructor(type,{detail}){this.type=type;this.detail=detail;}},FormData:class {constructor(form){const current=vm.runInContext('editableValues(projectWork(base,snapshot.store))',context);this.values=formValues[form.selector]||Object.fromEntries(Object.entries(current).map(([k,v])=>[k,Array.isArray(v)&&k!=='interactionModes'?v.join('\n'):v]));}get(k){return this.values[k]??null;}getAll(k){return this.values[k]||[];}has(k){return Boolean(this.values[k]);}},TOKEN_SETUP_URL,createEditClient:token=>createEditClient(token,fetcher)});
 const source=readFileSync(new URL('../live-work-editor.mjs',import.meta.url),'utf8').replace(/^import .*;$/gm,'').replace('export async function showLiveWorkEditor','async function showLiveWorkEditor');
 vm.runInContext(source,context);await vm.runInContext('showLiveWorkEditor("g039")',context);
 return {context,dialog,elements,calls,handlers,element,formValues,events,connect:async()=>{element('#le-token').value='github_pat_test_only';await handlers.click({target:{closest:()=>({id:'le-connect',hasAttribute:()=>false,dataset:{}})}});}};
}
test('an anonymous API 403 does not block opening the editor, viewing published edits or reaching the connection controls',async()=>{
 const {dialog,calls}=await harness();assert.equal(dialog.open,true);assert.ok(dialog.innerHTML.includes('id="le-form"'));assert.ok(dialog.innerHTML.includes('id="le-connect"'));assert.ok(dialog.innerHTML.includes('已保存的网页更正记录'));assert.ok(!dialog.innerHTML.includes('暂时无法编辑'));assert.ok(!calls.some(c=>c.url.startsWith('https://api.github.com')));
});
test('unavailable published history keeps authentication reachable and cannot silently initialize a new editable history',async()=>{
 const h=await harness({publishedStatus:503});assert.ok(h.dialog.innerHTML.includes('id="le-connect"'));assert.ok(h.dialog.innerHTML.includes('id="le-form" inert'));assert.match(h.element('#le-status').textContent,/当前资料暂不能保存/);
 assert.equal(vm.runInContext('historyReady',h.context),false);await h.connect();assert.equal(vm.runInContext('historyReady',h.context),true);assert.equal(vm.runInContext('snapshot.sha',h.context),'latest-sha');assert.ok(!h.dialog.innerHTML.includes('id="le-form" inert'));
});
test('connecting reads authenticated current history and refreshes stale published values before editing',async()=>{
 const h=await harness({published:empty(),latest:saved()});await h.connect();assert.ok(h.dialog.innerHTML.includes('已保存的网页更正记录'));assert.equal(vm.runInContext('snapshot.sha',h.context),'latest-sha');assert.ok(h.calls.filter(c=>c.url.startsWith('https://api.github.com')).every(c=>c.options.headers.Authorization==='Bearer github_pat_test_only'));
});
test('a new live revision does not replace an already entered draft and the reload control remains available',async()=>{
 const h=await harness({published:empty(),latest:saved()});vm.runInContext('dirty=()=>true',h.context);await h.connect();assert.equal(vm.runInContext('snapshot.store.records.g039',h.context),undefined);assert.equal(vm.runInContext('actor',h.context),'wt1234-donkey');assert.match(h.element('#le-status').textContent,/当前输入保留/);assert.ok(h.dialog.innerHTML.includes('id="le-refresh"'));
});

test('quick creator form saves multiple names without source, reason or confirmation and dispatches the published overlay',async()=>{
 const h=await harness({published:empty()});
 await vm.runInContext('showLiveWorkEditor("g039",{creatorsOnly:true})',h.context);
 assert.ok(h.dialog.innerHTML.includes('id="le-creators-form"'));
 assert.ok(h.dialog.innerHTML.includes('id="le-form" hidden'));
 await h.connect();
 h.formValues['#le-creators-form']={writerNames:'测试剧作甲\n测试剧作乙\n测试剧作甲',artistNames:'测试画师',musicianNames:'测试音乐'};
 await vm.runInContext('saveNames()',h.context);
 const put=h.calls.find(c=>c.options.method==='PUT');assert.ok(put,h.element('#le-status').textContent);
 const store=JSON.parse(Buffer.from(JSON.parse(put.options.body).content,'base64').toString('utf8')),row=store.records.g039;
 assert.deepEqual(row.overrides.writerNames,['测试剧作甲','测试剧作乙']);assert.deepEqual(row.recent[0].sources,[]);
 assert.equal(JSON.parse(put.options.body).sha,'latest-sha');assert.equal(h.events[0].type,'catalogue-work-edit');
 assert.ok(h.dialog.innerHTML.includes('测试画师'));assert.match(h.element('#le-status').textContent,/已保存到主库/);
});
test('quick save preserves an unrelated full-form draft instead of silently dropping it',async()=>{
 const h=await harness({published:empty()});await h.connect();
 h.formValues['#le-form']={...editableValues(base),title:base.title+' 编辑草稿'};
 h.formValues['#le-creators-form']={writerNames:'测试剧作',artistNames:'',musicianNames:''};
 await vm.runInContext('saveNames()',h.context);assert.ok(!h.calls.some(c=>c.options.method==='PUT'));assert.match(h.element('#le-status').textContent,/也有未保存修改/);
});
