import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {mkdtempSync,mkdirSync,writeFileSync,rmSync,readFileSync,readdirSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve,join,dirname,extname} from 'node:path';
import {gitFixture} from '../helpers/catalogue-git-fixture.mjs';
import {gitBlobHash} from '../../src/infrastructure/filesystem/basic-store.mjs';
import {loadCatalogueSnapshot} from '../../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {emptyStore} from '../../basic-catalogue-model.mjs';
import {emptyFieldStore,applyFieldCommand,validateFieldStore} from '../../src/domain/catalogue/field-evidence.mjs';
import {buildEffectiveCatalogue} from '../../src/domain/catalogue/effective.mjs';
import {planCommand} from '../../src/application/commands/execute.mjs';
import {receiptPath} from '../../src/infrastructure/filesystem/command-executor.mjs';
import {buildFieldEvidenceDirectory} from '../../scripts/build_field_evidence.mjs';
import {buildAuditLedger} from '../../src/infrastructure/filesystem/audit-ledger.mjs';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=resolve(import.meta.dirname,'../..'),REV='a'.repeat(40);
async function fixture({loseReceipt=false}={}){
 const temp=mkdtempSync(join(tmpdir(),'field-browser-')),files=new Map(),scope={type:'work',workId:'g001',id:'g001'};
 const put=(name,value)=>{mkdirSync(dirname(join(temp,'data',name)),{recursive:true});writeFileSync(join(temp,'data',name),JSON.stringify(value));};
 const registry={works:[{id:'g001',indexId:'index-1',title:'Original Name',firstYear:1990,group:'Same Studio',gameplay:'ADV',source:'https://example.org/source',mainPlacement:'existing-complete',linkedRecordId:'g001'}],identityReview:[]};
 const main={works:[{id:'g001',title:'Original Name',firstYear:1990}],contentVersions:[{id:'c1',workId:'g001',label:'Original Content',firstYear:1990}],platformReleases:[{id:'r1',workId:'g001',year:1990,publisher:'Same Studio',platform:'PC'}]};
 for(const [name,value] of Object.entries({'main-adv-rpg-works-20261031.json':registry,'games.json':main,'non-rpg-creator-supplement-20261030.json':{works:[]},'work-edit-history.json':{schemaVersion:1,records:{}},'basic-catalogue-edits.json':emptyStore(),'company-coverage.json':{companies:[]},'field-evidence.json':emptyFieldStore(),'entities.json':{entities:[{id:'e1',name:'Same Studio',type:'company'},{id:'e2',name:'Same Studio',type:'brand'}]},'creator-credits.json':{people:[{id:'p1',name:'Same Person'},{id:'p2',name:'Same Person'}]}}))put(name,value);
 for(const n of ['adv-rpg-minimal-index-20261031','adv-rpg-next-studio-review-20261031','adv-rpg-round3-review-20261031'])put(n+'.json',{records:[]});
 let loaded=loadCatalogueSnapshot(temp),store=emptyFieldStore(),blocked=false,dispatches=0,targetReads=0,rawReads=0,archiveReads=0;
 const a=(id,value,field='firstYear')=>({id,scope,field,value,sources:['https://example.org/'+id],sourceIds:['g001'],subjects:[],status:'supported'});
 const meta=id=>({id,actor:'other-editor',at:'2026-11-13T06:00:00Z',reason:'核对不同来源的登记年份',sources:['https://example.org/evidence'],expectedRevision:store.revision});
 for(const [id,value] of [['older',1990],['newer',1991]])store=applyFieldCommand(store,loaded.snapshot.fieldCatalogue.context,{type:'assert',assertion:a(id,value)},meta('add-'+id));
 put('field-evidence.json',store);loaded=loadCatalogueSnapshot(temp);
 const api=gitFixture();api.changeFile('data/source.json','immutable source');api.changeFile('data/field-evidence.json',JSON.stringify(store));const lease=api.lease(['data/source.json']);
 async function syncArchive(){put('field-evidence.json',store);const archive=await buildAuditLedger(temp);for(const name of readdirSync(join(temp,'data/audit-ledger/objects'))){const path='data/audit-ledger/objects/'+name,text=readFileSync(join(temp,path),'utf8');files.set(path,text);api.changeFile(path,text);}api.changeFile('data/audit-ledger/manifest.json',JSON.stringify(archive.pointer));return archive;}
 const archive=await syncArchive();
 const save=async(name,value)=>{const path=`catalogue-web/${REV}/${name}.json`,text=JSON.stringify(value);files.set('data/'+path,text);return {path,sha:gitBlobHash(text)};};
 const directory=await buildFieldEvidenceDirectory('',REV,{snapshot:loaded.snapshot,sourceLease:lease},buildEffectiveCatalogue({main}),save),resource=await save('field-store',store);
 const release={schemaVersion:1,revision:REV,saveMode:'trusted',sourceLease:lease,resources:{'data/field-evidence.json':resource},catalogues:{fieldEvidence:directory}};
 release.resources['data/audit-ledger/manifest.json']=await save('audit-pointer',archive.pointer);
 const server=createServer(async(req,res)=>{try{const path=new URL(req.url,'http://localhost').pathname.slice(1);if(path.includes('field-targets-'))targetReads++;if(path.includes('basic-registry/')||path.includes('resources/main-adv-rpg'))rawReads++;
  if(path==='data/catalogue-release.json'){res.setHeader('content-type','application/json');res.end(JSON.stringify(release));return;}if(files.has(path)){res.setHeader('content-type','application/json');res.end(files.get(path));return;}
  const file=resolve(root,path);if(!file.startsWith(root+'/'))throw Error('invalid path');res.setHeader('content-type',extname(file)==='.mjs'?'text/javascript':extname(file)==='.css'?'text/css':'text/html');res.end(await readFile(file));
 }catch{res.writeHead(404);res.end();}});
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));let browser;try{browser=await chromium.launch({headless:true});}catch(error){await new Promise(resolve=>server.close(resolve));rmSync(temp,{recursive:true,force:true});throw error;}
 const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[];page.on('pageerror',error=>errors.push(error.message));page.on('dialog',dialog=>dialog.accept());
 await page.route('https://api.github.com/**',async route=>{const req=route.request(),url=req.url();if(url.includes('/actions/runs?')){await route.fulfill({status:200,contentType:'application/json',body:'{"workflow_runs":[]}'});return;}
  if(url.includes('/contents/data/audit-ledger/manifest.json'))archiveReads++;
  if(blocked&&url.includes('/contents/data/command-receipts/')){await route.fulfill({status:503,contentType:'application/json',body:'{"message":"Injected receipt response loss"}'});return;}
  if(url.endsWith('/dispatches')){dispatches++;const command=JSON.parse(api.blobs.get(req.postDataJSON().client_payload.commandSha));const result=planCommand(command,{sourceLease:lease,fieldStore:store,fieldContext:loaded.snapshot.fieldCatalogue.context},'tester');if(!result.alreadyApplied){store=result.store;api.changeFile('data/field-evidence.json',JSON.stringify(store));api.changeFile(receiptPath(command.operationId),JSON.stringify(result.receipt));await syncArchive();}blocked=loseReceipt;await route.fulfill({status:204});return;}
  const r=await api.fetch(url,{method:req.method(),body:req.postData(),headers:req.headers()});await route.fulfill({status:r.status,contentType:'application/json',body:JSON.stringify(await r.json())});
 });
 await page.goto('http://127.0.0.1:'+server.address().port+'/field-evidence.html');await page.locator('#fe-status').filter({hasText:'目录已就绪'}).waitFor();
 return {page,errors,registry,get store(){return store;},get dispatches(){return dispatches;},get targetReads(){return targetReads;},get rawReads(){return rawReads;},get archiveReads(){return archiveReads;},
  async open(){await page.locator('#fe-work').fill('g001');await page.locator('#fe-search button').click();await page.locator('#fe-status').filter({hasText:'本部范围已就绪'}).waitFor();await page.locator('#fe-field').selectOption('firstYear');await page.locator('[data-assertion=newer]').waitFor();},
  async connect(){await page.locator('#fe-auth summary').click();await page.locator('#fe-token').fill('test-only-credential');await page.locator('#fe-connect').click();await page.locator('#fe-status').filter({hasText:/^已连接/}).waitFor();},
  async select(){await page.locator('#fe-reason').fill('比较两项年份来源并明确采用后者');await page.locator('[data-fe-select=newer]').click();},
  async later(){store=applyFieldCommand(store,loaded.snapshot.fieldCatalogue.context,{type:'assert',assertion:a('later','Later Maker','group')},meta('later-editor'));api.changeFile('data/field-evidence.json',JSON.stringify(store));await syncArchive();blocked=false;},
  close:async()=>{await browser.close();await new Promise(resolve=>server.close(resolve));rmSync(temp,{recursive:true,force:true});}};
}
test('actual field management retains conflicting sources, explicitly selects and independently undoes, while manual names need no source', {timeout:60000},async()=>{
 const f=await fixture();try{const {page}=f,original=JSON.stringify(f.registry);assert.equal(f.targetReads,0);await f.open();assert.equal(f.targetReads,1);assert.equal(await page.locator('[data-assertion]').count(),2);await page.locator('#fe-current').filter({hasText:'1990'}).waitFor();assert.equal(Object.keys(f.store.choices).length,0);await f.connect();await f.select();await page.locator('#fe-status').filter({hasText:'已保存字段证据 r3'}).waitFor();const choiceEvent=f.store.events.at(-1);
  await page.locator('#fe-current').filter({hasText:'1991'}).waitFor();await page.locator('#fe-add [name=value]').fill('1992');await page.locator('#fe-add [name=sources]').fill('https://example.org/third');await page.locator('#fe-add [name=reason]').fill('保留后来新增的第三项来源');await page.locator('#fe-add button[type=submit]').click();await page.locator('#fe-status').filter({hasText:'已保存字段证据 r4'}).waitFor();await page.locator('#fe-current').filter({hasText:'1991'}).waitFor();assert.equal(await page.locator('[data-assertion]').count(),3);
  await page.locator('[data-fe-undo="'+choiceEvent.id+'"]').click();await page.locator('#fe-status').filter({hasText:'已保存字段证据 r5'}).waitFor();await page.locator('#fe-current').filter({hasText:'1990'}).waitFor();assert.equal(Object.keys(f.store.assertions).length,3);assert.equal(Object.keys(f.store.choices).length,0);assert.equal(f.store.events.at(-1).type,'undo');
  await page.locator('#fe-field').selectOption('writerNames');await page.waitForFunction(()=>!document.getElementById('fe-add-panel').inert);await page.locator('#fe-add [name=value]').fill('Same Person');await page.locator('#fe-add [name=reason]').fill('保留手动添加姓名的既有权限');assert.equal(await page.locator('#fe-add [name=state]').inputValue(),'manual');await page.locator('#fe-add button[type=submit]').click();await page.locator('#fe-status').filter({hasText:'已保存字段证据 r6'}).waitFor();const manual=Object.values(f.store.assertions).find(a=>a.field==='writerNames');assert.deepEqual(manual.sources,[]);assert.deepEqual(manual.subjects,[]);assert.equal(manual.status,'manual');
  await page.locator('#fe-add details summary').click();await page.locator('#fe-subject-catalogue').click();const ids=await page.locator('#fe-subjects code').allTextContents();assert.ok(ids.includes('entity:e1')&&ids.includes('entity:e2')&&ids.includes('person:p1')&&ids.includes('person:p2'));
  validateFieldStore(f.store);assert.equal(JSON.stringify(f.registry),original);assert.equal(f.rawReads,0);assert.ok(f.archiveReads>0,'actual browser queries the bound archive index after trusted saves');assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth),true);assert.deepEqual(f.errors,[]);
 }finally{await f.close();}
});
test('actual field retry survives lost receipt, later evidence and reload with the original operation ID', {timeout:60000},async()=>{
 const f=await fixture({loseReceipt:true});try{const {page}=f;await f.open();await f.connect();await f.select();await page.locator('#fe-status').filter({hasText:'HTTP 503'}).waitFor();const original=f.store.events.at(-1);assert.equal(f.dispatches,1);await f.later();const later=structuredClone(f.store);
  await page.reload();await page.locator('#fe-status').filter({hasText:'本部范围已就绪'}).waitFor();await f.connect();assert.equal(await page.locator('#fe-token').inputValue(),'');await page.locator('#fe-retry').click();await page.locator('#fe-status').filter({hasText:'原操作仅确认一次'}).waitFor();assert.deepEqual(f.store,later);assert.equal(f.dispatches,1);const receipts=await page.evaluate(()=>JSON.parse(localStorage.getItem('catalogue-operation-receipts-v1')));assert.equal(receipts[0].operationId,original.id);assert.equal(receipts[0].revision,3);assert.equal(receipts[0].kind,'field');assert.equal(f.rawReads,0);assert.deepEqual(f.errors,[]);
 }finally{await f.close();}
});
