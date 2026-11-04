import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFileSync} from 'node:fs';
import {createEditClient,TOKEN_SETUP_URL} from '../work-edit-api.mjs';
import {same,lines,validURL} from '../management-model.mjs';
import {editableValues,projectWork,saveEdit,undoEdit,changedFields,validateHistory} from '../work-edit-model.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name+'.json',import.meta.url),'utf8'));
const base=read('games').works.find(w=>w.id==='g039'),taxonomy=read('taxonomy');
const empty=()=>({schemaVersion:1,records:{}});
function saved(){const after=editableValues(base);after.notes='已保存的网页更正记录';return saveEdit(empty(),base,after,{id:'test-edit',actor:'test-user',at:'2026-11-04T08:00:00Z',reason:'已核对的网页更正',sources:[base.source],expectedRevision:0},taxonomy,[base]);}
async function harness({published=saved(),publishedStatus=200,latest=published}={}){
 const elements=new Map(),calls=[],handlers={};
 const element=selector=>{if(!elements.has(selector))elements.set(selector,{innerHTML:'',textContent:'',className:'',value:'',open:true,focus(){},querySelector:element,disabled:false});return elements.get(selector);};
 const dialog={innerHTML:'',open:false,setAttribute(){},addEventListener(type,fn){handlers[type]=fn;},showModal(){this.open=true;},close(){this.open=false;},querySelector:element,querySelectorAll:()=>[]};
 const document={createElement:tag=>tag==='dialog'?dialog:{},head:{append(){}},body:{append(){}}};
 const fetcher=async(url,options={})=>{
  calls.push({url,options});
  if(url.startsWith('https://api.github.com')){
   if(!options.headers?.Authorization)return {ok:false,status:403,headers:new Headers(),json:async()=>({message:'API rate limit exceeded'})};
   const data=url.endsWith('/user')?{login:'wt1234-donkey'}:url.endsWith('/visual-novel')?{permissions:{push:true}}:{sha:'latest-sha',content:Buffer.from(JSON.stringify(latest)).toString('base64')};
   return {ok:true,status:200,headers:new Headers(),json:async()=>data};
  }
  const data=url.includes('work-edit-history')?published:url.includes('games.json')?{works:[base]}:url.includes('supplement')?{works:[]}:url.includes('taxonomy')?taxonomy:{companies:[]};
  return {ok:url.includes('work-edit-history')?publishedStatus===200:true,status:url.includes('work-edit-history')?publishedStatus:200,json:async()=>structuredClone(data)};
 };
 const context=vm.createContext({document,fetch:fetcher,console,structuredClone,crypto:globalThis.crypto,confirm:()=>true,same,lines,validURL,editableValues,projectWork,saveEdit,undoEdit,changedFields,validateHistory,TOKEN_SETUP_URL,createEditClient:token=>createEditClient(token,fetcher)});
 const source=readFileSync(new URL('../live-work-editor.mjs',import.meta.url),'utf8').replace(/^import .*;$/gm,'').replace('export async function showLiveWorkEditor','async function showLiveWorkEditor');
 vm.runInContext(source,context);await vm.runInContext('showLiveWorkEditor("g039")',context);
 return {context,dialog,elements,calls,handlers,element,connect:async()=>{element('#le-token').value='github_pat_test_only';await handlers.click({target:{closest:()=>({id:'le-connect',hasAttribute:()=>false,dataset:{}})}});}};
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
