import {buildAuditLedger} from '../../src/infrastructure/filesystem/audit-ledger.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,rmSync,readdirSync} from 'node:fs';
import {resolve,extname,join,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {gitFixture} from '../helpers/catalogue-git-fixture.mjs';
import {gitBlobHash} from '../../src/infrastructure/filesystem/basic-store.mjs';
import {planCommand} from '../../src/application/commands/execute.mjs';
import {receiptPath} from '../../src/infrastructure/filesystem/command-executor.mjs';
import {emptyIdentityStore,buildSourceIdentityCatalogue,applyIdentityReview,validateIdentityStore} from '../../src/domain/catalogue/source-identities.mjs';
import {emptyStore} from '../../basic-catalogue-model.mjs';
import {buildSourceIdentityIndex} from '../../scripts/build_source_identity_index.mjs';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=resolve(import.meta.dirname,'../..'),REV='a'.repeat(40);
async function fixture({loseReceipt=false}={}){
 const temp=mkdtempSync(join(tmpdir(),'identity-browser-')),output=join(temp,'public');
 const put=(path,value)=>{mkdirSync(dirname(join(temp,path)),{recursive:true});writeFileSync(join(temp,path),JSON.stringify(value));};
 const row=(id,title='Twin')=>({id,indexId:'index-'+id,title,firstYear:1990,aliases:[],source:'https://example.com/'+id,sourceRefs:['test:'+id],mainPlacement:'promoted-basic',linkedRecordId:null,gameplay:'ADV',group:'Test',batch:'test'});
 const registry={works:[row('s-a'),row('s-b'),row('s-c','Other')],identityReview:[]};
 let store=emptyIdentityStore(),blocked=false,dispatches=0,rawReads=0;
 const catalogue=()=>buildSourceIdentityCatalogue({registry,decisions:store});
 for(const [path,value] of Object.entries({'main-adv-rpg-works-20261031.json':registry,'games.json':{works:[]},'basic-catalogue-edits.json':emptyStore(),'work-edit-history.json':{schemaVersion:1,records:{}},'source-identity-decisions.json':store}))put('data/'+path,value);
 const api=gitFixture();api.changeFile('data/source.json','original immutable evidence');api.changeFile('data/source-identity-decisions.json',JSON.stringify(store));const lease=api.lease(['data/source.json']);
 async function syncArchive(){put('data/source-identity-decisions.json',store);const archive=await buildAuditLedger(temp);for(const name of readdirSync(join(temp,'data/audit-ledger/objects'))){const path='data/audit-ledger/objects/'+name,text=readFileSync(join(temp,path),'utf8');mkdirSync(dirname(join(output,path)),{recursive:true});writeFileSync(join(output,path),text);api.changeFile(path,text);}api.changeFile('data/audit-ledger/manifest.json',JSON.stringify(archive.pointer));return archive;}
 const archive=await syncArchive();
 const built=buildSourceIdentityIndex(temp,output,REV),manifestPath=join(output,'data',built.ref.path),manifest=JSON.parse(readFileSync(manifestPath,'utf8'));manifest.sourceLease=lease;
 const manifestText=JSON.stringify(manifest);writeFileSync(manifestPath,manifestText);const identityRef={path:built.ref.path,sha:gitBlobHash(manifestText)};
 const resources={};for(const [path,value] of [['data/source-identity-decisions.json',store],['data/main-adv-rpg-works-20261031.json',registry]]){
  const target=`catalogue-web/${REV}/resources/${path.split('/').at(-1)}`,text=JSON.stringify(value);mkdirSync(dirname(join(output,'data',target)),{recursive:true});writeFileSync(join(output,'data',target),text);resources[path]={path:target,sha:gitBlobHash(text)};
 }
 const pointerPath='catalogue-web/'+REV+'/audit-pointer.json',pointerText=JSON.stringify(archive.pointer);writeFileSync(join(output,'data',pointerPath),pointerText);resources['data/audit-ledger/manifest.json']={path:pointerPath,sha:gitBlobHash(pointerText)};
 const release={schemaVersion:1,revision:REV,saveMode:'trusted',sourceLease:lease,resources,catalogues:{sourceIdentities:identityRef}};
 const server=createServer(async(req,res)=>{try{
  const path=new URL(req.url,'http://localhost').pathname.slice(1);if(path==='data/catalogue-release.json'){res.setHeader('content-type','application/json');res.end(JSON.stringify(release));return;}
  if(path.includes('/resources/main-adv-rpg-works-20261031.json'))rawReads++;
  const file=path.startsWith('data/catalogue-web/')||path.startsWith('data/audit-ledger/')?resolve(output,path):resolve(root,path);if(!file.startsWith(root+'/')&&!file.startsWith(output+'/'))throw Error('invalid path');
  res.setHeader('content-type',path.endsWith('.json')?'application/json':path.endsWith('.gz')?'application/gzip':extname(file)==='.mjs'?'text/javascript':extname(file)==='.css'?'text/css':'text/html');res.end(await readFile(file));
 }catch{res.writeHead(404);res.end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;
 try{browser=await chromium.launch({headless:true});}catch(error){await new Promise(resolve=>server.close(resolve));rmSync(temp,{recursive:true,force:true});throw error;}
 const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('dialog',dialog=>dialog.accept());
 await page.route('https://api.github.com/**',async route=>{
  const req=route.request(),url=req.url();if(url.includes('/actions/runs?')){await route.fulfill({status:200,contentType:'application/json',body:'{"workflow_runs":[]}'});return;}if(blocked&&url.includes('/contents/data/command-receipts/')){await route.fulfill({status:503,contentType:'application/json',body:'{"message":"Injected receipt response loss"}'});return;}
  if(url.endsWith('/dispatches')){
   dispatches++;const body=req.postDataJSON(),command=JSON.parse(api.blobs.get(body.client_payload.commandSha));
   const result=planCommand(command,{sourceLease:lease,identityStore:store,sourceIdentity:catalogue()},'tester');
   if(!result.alreadyApplied){store=result.store;api.changeFile('data/source-identity-decisions.json',JSON.stringify(store));api.changeFile(receiptPath(command.operationId),JSON.stringify(result.receipt));await syncArchive();}
   blocked=loseReceipt;await route.fulfill({status:204});return;
  }
  const result=await api.fetch(url,{method:req.method(),body:req.postData(),headers:req.headers()});await route.fulfill({status:result.status,contentType:'application/json',body:JSON.stringify(await result.json())});
 });
 await page.goto('http://127.0.0.1:'+server.address().port+'/source-identities.html');await page.locator('#identity-count').filter({hasText:'来源记录共 3 条'}).waitFor();
 return {page,errors,get store(){return store;},get dispatches(){return dispatches;},get rawReads(){return rawReads;},registry,
  async connect(){await page.locator('#identity-auth summary').click();await page.locator('#identity-token').fill('test-only-credential');await page.locator('#identity-connect').click();await page.locator('#identity-status').filter({hasText:/^已连接/}).waitFor();},
  async later(){store=applyIdentityReview(store,catalogue(),{type:'resolve',caseId:'source:s-c',outcome:'link',links:[{sourceId:'s-c',workId:'s-c'}]},
   {id:'later-editor',at:'2026-11-13T04:00:00Z',actor:'other-editor',reason:'保留后续另一来源核对',sources:['https://example.com/s-c'],expectedRevision:store.revision});api.changeFile('data/source-identity-decisions.json',JSON.stringify(store));await syncArchive();blocked=false;},
  async review(){await page.locator('[data-view=cases]').click();await page.locator('#identity-count').filter({hasText:/^案件共/}).waitFor();await page.locator('#identity-rows [data-row]').first().click();await page.locator('#identity-review [name=workId]').fill('s-a');await page.locator('#identity-review [name=reason]').fill('逐条核对来源与同一作品身份');await page.locator('#identity-review [name=sources]').fill('https://example.com/evidence');await page.locator('#identity-review [name=confirmed]').check();await page.locator('[name=outcome][value=same-work]').click();},
  close:async()=>{await browser.close();await new Promise(resolve=>server.close(resolve));rmSync(temp,{recursive:true,force:true});}};
}
test('identity management loads light directories, reads one original on request, explicitly reviews and appends an independent undo', {timeout:60000},async()=>{
 const f=await fixture();try{const {page}=f,original=JSON.stringify(f.registry);assert.equal(f.rawReads,0);
  for(const view of ['works','links','cases','sources']){await page.locator('[data-view='+view+']').click();await page.locator('#identity-count').filter({hasText:new RegExp('^'+({works:'作品身份',links:'身份链接',cases:'案件',sources:'来源记录'}[view])+'共')}).waitFor();}assert.equal(f.rawReads,0);assert.deepEqual(f.store.links,{});
  await page.locator('#identity-rows [data-row]').first().click();await page.locator('#identity-original').click();await page.locator('#identity-original-body').filter({hasText:'s-a'}).waitFor();assert.equal(f.rawReads,1);
  await f.connect();await f.review();await page.locator('#identity-status').filter({hasText:'已保存身份核对 r1'}).waitFor();assert.equal(f.store.links['s-b'].workId,'s-a');assert.equal(JSON.stringify(f.registry),original);
  await page.locator('[data-undo]').first().click();await page.locator('#identity-status').filter({hasText:'已保存身份核对 r2'}).waitFor();assert.equal(f.store.events.at(-1).type,'undo');assert.deepEqual(f.store.links,{});validateIdentityStore(f.store);assert.equal(f.dispatches,2);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);assert.deepEqual(f.errors,[]);
 }finally{await f.close();}
});
test('identity retry after a lost response and reload confirms the original operation and preserves a later review', {timeout:60000},async()=>{
 const f=await fixture({loseReceipt:true});try{const {page}=f;await f.connect();await f.review();await page.locator('#identity-status').filter({hasText:'HTTP 503'}).waitFor();const original=f.store.events[0];assert.equal(f.dispatches,1);await f.later();const later=structuredClone(f.store);
  await page.reload();await page.locator('#identity-count').filter({hasText:'来源记录共 3 条'}).waitFor();await f.connect();assert.equal(await page.locator('#identity-token').inputValue(),'');await page.locator('#identity-retry').click();await page.locator('#identity-status').filter({hasText:'原操作仅确认一次'}).waitFor();
  assert.deepEqual(f.store,later);assert.equal(f.dispatches,1);const receipts=await page.evaluate(()=>JSON.parse(localStorage.getItem('catalogue-operation-receipts-v1')));assert.equal(receipts[0].operationId,original.id);assert.equal(receipts[0].kind,'identity');assert.deepEqual(f.errors,[]);
 }finally{await f.close();}
});
