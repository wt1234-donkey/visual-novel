import test from 'node:test';
import assert from 'node:assert/strict';
import {createEditClient} from '../src/infrastructure/github/contents-repository.mjs';
import {submitCommand} from '../src/infrastructure/github/command-transport.mjs';
import {createCommandSession} from '../src/application/commands/session.mjs';
import {checkPublication} from '../src/features/publication-status.mjs';
import {commandText} from '../src/application/commands/envelope.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';
const A='a'.repeat(40),B='b'.repeat(40),C='c'.repeat(40),never=()=>new Promise(()=>{});
const command={schemaVersion:1,operationId:'recovery-test',kind:'formal',actor:'tester',at:'2026-11-14T00:00:00Z',reason:'复核失败后的操作恢复',sources:[],expectedRevision:0,sourceLease:{schemaVersion:1,files:{}},action:{type:'creators',workId:'g039',names:{writerNames:['Writer'],artistNames:[],musicianNames:[]}}};
const receipt={schemaVersion:1,operationId:command.operationId,kind:command.kind,actor:command.actor,revision:1,command:commandText(command)};
async function api({terminalReceipt=false}={}){
 let checks=0,dispatches=0;
 const request=async(path,method,body)=>{
  if(path.endsWith('/git/ref/heads/main'))return {object:{sha:A}};
  if(path.includes('/contents/')){checks++;if(terminalReceipt&&checks>=7){const raw=JSON.stringify(receipt);return {sha:await blobDigest(raw),content:Buffer.from(raw).toString('base64')};}throw Object.assign(Error('absent'),{status:404});}
  if(path.endsWith('/git/blobs'))return {sha:await blobDigest(body.content)};
  if(path.endsWith('/dispatches')){dispatches++;return {};}
  throw Error(path);
 };
 return {request,get dispatches(){return dispatches;}};
}
test('connection and response bodies have deadlines even when the fetch adapter ignores cancellation',async()=>{
 for(const bodyOnly of [false,true]){
  const signals=[];const fetcher=async(url,o)=>{signals.push(o.signal);return bodyOnly?{ok:true,json:never,headers:{get:()=>null}}:never();};
  await assert.rejects(createEditClient('test-only',fetcher,{requestTimeout:25}).connect(),e=>e.name==='TimeoutError');
  assert.ok(signals.every(s=>s));await Promise.all(signals.map(s=>s.aborted?Promise.resolve():new Promise(resolve=>s.addEventListener('abort',resolve,{once:true}))));
 }
});
test('a hung public status request cannot outlive the receipt wait budget or change the operation ID',async()=>{
 const f=await api();let pollingSignal;
 await assert.rejects(submitCommand(f.request,command,{timeout:35,requestTimeout:200,interval:0,pause:async()=>{},fetchPublic:async(url,o)=>{pollingSignal=o.signal;return never();}}),e=>e.code==='COMMAND_PENDING'&&e.operationId===command.operationId);
 assert.equal(f.dispatches,1);assert.equal(pollingSignal.aborted,true);
});
test('a failed terminal run is rejected only after rechecking the atomic receipt',async()=>{
 const fetchPublic=async()=>({ok:true,json:async()=>({workflow_runs:[{path:'.github/workflows/catalogue-command.yml',display_title:'保存 '+command.operationId,status:'completed',conclusion:'failure',html_url:'https://github.com/wt1234-donkey/visual-novel/actions/runs/1'}]})});
 const f=await api();await assert.rejects(submitCommand(f.request,command,{interval:0,pause:async()=>{},fetchPublic}),e=>e.code==='COMMAND_REJECTED'&&e.commandNotApplied===true);
 const saved=await api({terminalReceipt:true});assert.equal((await submitCommand(saved.request,command,{interval:0,pause:async()=>{},fetchPublic})).operationId,command.operationId);
});
test('confirmed rejection releases the pending command, while ambiguous results preserve it across reload',async()=>{
 const memory=new Map(),storage={getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v),removeItem:k=>memory.delete(k)};
 let s=createCommandSession({kind:'formal',storage});
 await assert.rejects(s.execute(command,async()=>{throw Object.assign(Error('rejected'),{commandNotApplied:true});}));
 const fresh={...command,operationId:'fresh-command',expectedRevision:2,sourceLease:{schemaVersion:1,files:{source:B}}};let received;
 await s.execute(fresh,async c=>{received=c;return {};});assert.equal(received.operationId,fresh.operationId);assert.equal(received.expectedRevision,2);
 await assert.rejects(s.execute(command,async()=>{throw Object.assign(Error('unknown'),{code:'COMMAND_PENDING'});}));
 s=createCommandSession({kind:'formal',storage});await s.execute(fresh,async c=>{received=c;return {};});assert.equal(received.operationId,command.operationId);
});
test('publication timeouts finish and a transient failed comparison is retried on the next check',async()=>{
 const saved={...receipt,at:command.at,commit:A};let firstSignal;
 assert.equal((await checkPublication([saved],async(url,o)=>{firstSignal=o.signal;return never();},{timeout:25,requestTimeout:200}))[0].state,'unknown');assert.ok(firstSignal.aborted);
 let comparisons=0;
 const fetcher=async url=>{if(url==='./deployment.json')return {ok:true,json:async()=>({revision:C})};if(url.includes('/actions/'))return {ok:true,json:async()=>({workflow_runs:[{head_sha:B,path:'.github/workflows/pages.yml',event:'push',status:'in_progress'}]})};comparisons++;return {ok:comparisons>1,json:async()=>({status:'ahead'})};};
 assert.equal((await checkPublication([saved],fetcher))[0].state,'unknown');assert.equal((await checkPublication([saved],fetcher))[0].state,'publishing');assert.equal(comparisons,2);
});
