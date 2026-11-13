import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {readFileSync} from 'node:fs';
import {resolve,extname} from 'node:path';
import {gitFixture} from '../helpers/catalogue-git-fixture.mjs';
import {gitBlobHash} from '../../src/infrastructure/filesystem/basic-store.mjs';
import {planCommand} from '../../src/application/commands/execute.mjs';
import {receiptPath} from '../../src/infrastructure/filesystem/command-executor.mjs';
import {editableValues,projectWork,saveEdit} from '../../work-edit-model.mjs';
import {upgradeFormalHistory,replayFormalJournal,formalState} from '../../src/domain/catalogue/formal-journal.mjs';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=resolve(import.meta.dirname,'../..'),REV='a'.repeat(40);
const read=name=>JSON.parse(readFileSync(resolve(root,'data',name+'.json')));
const work=read('games').works.find(w=>w.id==='g039'),taxonomy=read('taxonomy');
const checkpoint=()=>upgradeFormalHistory({schemaVersion:1,records:{}},{at:'2026-11-13T02:00:00Z'});
function amend(store,n){return saveEdit(store,work,{...editableValues(projectWork(work,store)),notes:'浏览器核验正式备注 '+n},
 {id:'browser-'+n,at:'2026-11-13T02:00:00Z',actor:'other-editor',expectedRevision:store.records[work.id]?.revision||0,reason:'核对浏览器正式编辑历史 '+n,sources:[work.source]},taxonomy,[work]);}
async function fixture({initial=checkpoint(),loseReceipt=false}={}){
 let store=structuredClone(initial),blocked=false,dispatches=0;
 const api=gitFixture();api.changeFile('data/source.json','source');api.changeFile('data/work-edit-history.json',JSON.stringify(store));const lease=api.lease(['data/source.json']);
 const files=new Map();
 const put=(name,value)=>{const path=`data/catalogue-web/${REV}/${name}.json`,text=JSON.stringify(value);files.set(path,text);return {path:path.slice(5),sha:gitBlobHash(text)};};
 const details=put('formal-0',{[work.id]:{source:work,work}}),validation=put('validation',[work]);
 const formal=put('formal-directory',{schemaVersion:1,revision:REV,ids:[work.id],shardSize:25,families:{formal:{0:details}},
  raw:{main:{works:[work]},supplement:{works:[]},history:store},coverage:{companies:[]},sourceLease:lease});
 const resources={'data/taxonomy.json':put('taxonomy',taxonomy),'data/work-edit-history.json':put('history',store)};
 const release={schemaVersion:1,revision:REV,saveMode:'trusted',sourceLease:lease,resources,catalogues:{formal,validation}};
 const server=createServer(async(req,res)=>{
  try{
   const path=new URL(req.url,'http://localhost').pathname.slice(1);
   if(path==='formal-test.html'){res.setHeader('content-type','text/html');res.end('<!doctype html><meta charset="utf-8"><main></main><script type="module">import {showLiveWorkEditor} from "./live-work-editor.mjs";window.openFormal=()=>showLiveWorkEditor("g039");</script>');return;}
   if(path==='data/catalogue-release.json'){res.setHeader('content-type','application/json');res.end(JSON.stringify(release));return;}
   if(files.has(path)){res.setHeader('content-type','application/json');res.end(files.get(path));return;}
   const file=resolve(root,path);if(!file.startsWith(root+'/'))throw Error('invalid path');
   res.setHeader('content-type',extname(file)==='.mjs'?'text/javascript':extname(file)==='.css'?'text/css':'text/html');res.end(await readFile(file));
  }catch{res.writeHead(404);res.end();}
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
 try{browser=await chromium.launch({headless:true});}catch(error){await new Promise(resolve=>server.close(resolve));throw error;}
 const page=await browser.newPage(),errors=[];page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.route('https://api.github.com/**',async route=>{
  const req=route.request(),url=req.url();
  if(blocked&&url.includes('/contents/data/command-receipts/')){await route.fulfill({status:503,contentType:'application/json',body:'{"message":"Injected receipt response loss"}'});return;}
  if(url.endsWith('/dispatches')){
   dispatches++;const body=req.postDataJSON(),command=JSON.parse(api.blobs.get(body.client_payload.commandSha));
   const result=planCommand(command,{sourceLease:lease,formalWorks:[work],reservedWorks:[work],formalStore:store,taxonomy},'tester');
   if(!result.alreadyApplied){store=result.store;api.changeFile('data/work-edit-history.json',JSON.stringify(store));api.changeFile(receiptPath(command.operationId),JSON.stringify(result.receipt));}
   blocked=loseReceipt;await route.fulfill({status:204});return;
  }
  const result=await api.fetch(url,{method:req.method(),body:req.postData(),headers:req.headers()});
  await route.fulfill({status:result.status,contentType:'application/json',body:JSON.stringify(await result.json())});
 });
 await page.goto('http://127.0.0.1:'+server.address().port+'/formal-test.html');await page.waitForFunction(()=>typeof window.openFormal==='function');await page.evaluate(()=>window.openFormal());
 await page.locator('#le-form').waitFor();
 return {page,api,errors,get store(){return store;},get dispatches(){return dispatches;},
  later(){store=amend(store,'later');api.changeFile('data/work-edit-history.json',JSON.stringify(store));blocked=false;},
  async connect(){await page.locator('#le-auth summary').click();await page.locator('#le-token').fill('test-only-credential');await page.locator('#le-connect').click();await page.locator('#le-status').filter({hasText:'已连接账号'}).waitFor();},
  close:async()=>{await browser.close();await new Promise(resolve=>server.close(resolve));}};
}

test('actual formal dialog pages beyond three edits and appends an independent undo through the trusted executor', {timeout:60000},async()=>{
 let initial=checkpoint();for(let n=1;n<=25;n++)initial=amend(initial,n);
 const f=await fixture({initial});try{
  const {page}=f;assert.equal(await page.locator('[data-audit-id]').count(),20);
  await page.locator('#le-history-older').click();assert.equal(await page.locator('[data-audit-id]').count(),5);await page.locator('[data-audit-id="browser-1"]').waitFor();
  await page.locator('#le-history-newest').click();await f.connect();
  await page.locator('[data-le-undo="browser-25"]').click();await page.locator('#le-status').filter({hasText:'已保存到主库'}).waitFor();
  assert.equal(f.store.journal.events.length,26);const event=f.store.journal.events.at(-1);
  assert.equal(event.commandType,'undo');assert.equal(event.undoOf,'browser-25');assert.equal(event.actor,'tester');
  await page.locator('[data-audit-id="'+event.id+'"]').filter({hasText:'撤销事件'}).waitFor();
  assert.deepEqual(replayFormalJournal(f.store.journal),formalState(f.store));assert.equal(f.dispatches,1);assert.deepEqual(f.errors,[]);
 }finally{await f.close();}
});

test('actual formal retry reconciles a lost response and keeps later edits with the original receipt', {timeout:60000},async()=>{
 const f=await fixture({loseReceipt:true});try{
  const {page}=f;await f.connect();await page.locator('#le-form [name=notes]').fill('正式保存响应丢失的原始修改');
  await page.locator('#le-form [name=reason]').fill('核对正式作品保存中断重试');await page.locator('#le-form [name=confirmed]').check();
  await page.locator('#le-form button[type=submit]').click();await page.locator('#le-status').filter({hasText:'HTTP 503'}).waitFor();
  const original=f.store.journal.events[0];assert.equal(f.dispatches,1);f.later();const later=structuredClone(f.store);
  await page.reload();await page.waitForFunction(()=>typeof window.openFormal==='function');await page.evaluate(()=>window.openFormal());await page.locator('#le-form').waitFor();await f.connect();
  assert.equal(await page.locator('#le-token').inputValue(),'');
  await page.locator('#le-retry-pending').click();await page.locator('#le-status').filter({hasText:'后续修改已保留'}).waitFor();
  assert.equal(await page.locator('#le-form [name=notes]').inputValue(),'浏览器核验正式备注 later');
  assert.deepEqual(f.store,later);assert.equal(f.dispatches,1);assert.equal(f.store.journal.events.length,2);
  const receipts=await page.evaluate(()=>JSON.parse(localStorage.getItem('catalogue-operation-receipts-v1')));
  assert.equal(receipts[0].operationId,original.id);assert.equal(receipts[0].revision,1);assert.equal(receipts[0].kind,'formal');
  assert.deepEqual(f.errors,[]);
 }finally{await f.close();}
});
