import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {join,resolve,extname} from 'node:path';
import {tmpdir} from 'node:os';
import {createHash} from 'node:crypto';
import {formalScale,identityScale,fieldScale} from '../helpers/audit-scale-fixture.mjs';
import {buildAuditLedger} from '../../src/infrastructure/filesystem/audit-ledger.mjs';
import {AUDIT_SOURCES,auditWorkIds} from '../../src/domain/audit/events.mjs';
import {FIELD_DEFINITIONS} from '../../src/domain/catalogue/field-evidence.mjs';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=resolve(import.meta.dirname,'../..'),REV='a'.repeat(40),report={environment:{viewport:'390×844',bandwidthMbps:5,latencyMs:100,cpuSlowdown:4,runsPerKind:1,limitations:'Chromium simulation of actual page/editor code; not Android. Formal scenario opens the actual editor from a minimal host, not the complete discovery shell.'},eventsPerKind:10000,scenarios:{}};
for(const [kind,make] of [['formal',formalScale],['identity',identityScale],['field',fieldScale]])test('mobile '+kind+' startup, selected work, history and undo evidence stay bounded at 10,000 events',{timeout:180000},async()=>{
 const temp=mkdtempSync(join(tmpdir(),'atlas-startup-')),files=new Map();let browser,server;
 try{
  mkdirSync(join(temp,'data'));const sample=make(10000),store=sample.store;
  writeFileSync(join(temp,AUDIT_SOURCES[kind]),JSON.stringify(store)+'\n');const archive=await buildAuditLedger(temp);
  const save=(name,value)=>{const path='catalogue-web/'+REV+'/'+name+'.json',text=JSON.stringify(value);files.set('data/'+path,text);return {path,sha:createHash('sha1').update('blob '+Buffer.byteLength(text)+'\0'+text).digest('hex')};};
  const resources={[AUDIT_SOURCES[kind]]:save('whole-source',store),'data/audit-ledger/manifest.json':save('audit-pointer',archive.pointer)},catalogues={};
  const sourceText=readFileSync(join(temp,AUDIT_SOURCES[kind]),'utf8'),sourceRef=resources[AUDIT_SOURCES[kind]];
  files.set('data/'+sourceRef.path,sourceText);sourceRef.sha=createHash('sha1').update('blob '+Buffer.byteLength(sourceText)+'\0'+sourceText).digest('hex');
  const sourceLease={schemaVersion:1,files:{'data/source.json':'b'.repeat(40)}};
  if(kind==='identity'){
   const rows=['hot','cold'].map(id=>({id,title:id,firstYear:1980,source:'https://example.org/'+id,link:{workId:id,status:'confirmed'},caseIds:['source:'+id],recordRef:{path:'never-read.json',slot:0}}));
   catalogues.sourceIdentities=save('identity',{schemaVersion:1,revision:REV,dataRevision:10000,sourceLease,stats:{sourceRecordCount:2,workIdentityCount:2,resolvedWorkCount:2,reviewedWorkCount:2},definitions:{},pages:{sources:[save('sources',rows)],works:[],cases:[]},totals:{sources:2,works:2,cases:0},lookups:{sources:[],works:[],cases:[]}});
  }else if(kind==='field'){
   const targets=['hot','cold'].map(id=>[id,[{scope:{type:'work',workId:id,id},values:{title:id,firstYear:1980,group:'Maker',writerNames:[],artistNames:[],musicianNames:[]}}]]),parts=Array.from({length:64},()=>({}));
   for(const [id,value] of targets)parts[createHash('sha256').update(id).digest()[0]%64][id]=value;
   catalogues.fieldEvidence=save('fields',{schemaVersion:1,revision:REV,sourceLease,stats:{revision:10000},aliases:{},fields:FIELD_DEFINITIONS,subjects:{entity:[],person:[]},lookups:parts.map((p,i)=>save('targets-'+i,p))});
  }else{
   const {works,taxonomy}=sample,rows=Object.fromEntries(works.map(w=>[w.id,{source:w,work:w}]));
   catalogues.formal=save('formal-directory',{schemaVersion:1,currentStateVersion:1,revision:REV,ids:['hot','cold'],shardSize:25,families:{formal:{0:save('formal-detail',rows)}},raw:{main:{works},supplement:{works:[]},history:{schemaVersion:1,records:{}}},coverage:{companies:[]},sourceLease});
   catalogues.validation=save('validation',works);resources['data/taxonomy.json']=save('taxonomy',taxonomy);
  }
  const release={schemaVersion:1,revision:REV,saveMode:'trusted',sourceLease,resources,catalogues};
  files.set('data/catalogue-release.json',JSON.stringify(release));
  files.set('editor-host.html','<meta name="viewport" content="width=device-width,initial-scale=1"><button id="open">编辑cold</button><script type="module">import {showLiveWorkEditor} from "./live-work-editor.mjs";document.getElementById("open").onclick=()=>showLiveWorkEditor("cold");</script>');
  let bytes=0,requests=0,wholeSourceReads=0;const bodies=[];
  server=createServer(async(req,res)=>{try{const path=new URL(req.url,'http://localhost').pathname.slice(1);if(path.endsWith('/whole-source.json'))wholeSourceReads++;
   const content=files.has(path)?Buffer.from(files.get(path)):await readFile(path.startsWith('data/audit-ledger/')?join(temp,path):join(root,path));
   requests++;bytes+=content.length;if(path.startsWith('data/audit-ledger/objects/')){const object=JSON.parse(content);if(object.type==='events')bodies.push(...object.events);}
   res.setHeader('content-type',({'.mjs':'text/javascript','.json':'application/json','.html':'text/html','.css':'text/css'})[extname(path)]||'application/octet-stream');res.end(content);
  }catch{res.writeHead(404);res.end();}});
  await new Promise(r=>server.listen(0,'127.0.0.1',r));browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:390,height:844},isMobile:true,hasTouch:true}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  const cdp=await page.context().newCDPSession(page);await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:100,downloadThroughput:5_000_000/8,uploadThroughput:5_000_000/8});await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});await cdp.send('Performance.enable');
  const start=performance.now(),url='http://127.0.0.1:'+server.address().port+'/';
  await page.goto(url+({formal:'editor-host.html',identity:'source-identities.html',field:'field-evidence.html'})[kind]);
  if(kind==='identity')await page.locator('#identity-count').filter({hasText:'来源记录共 2 条'}).waitFor();
  if(kind==='field')await page.locator('#fe-status').filter({hasText:'目录已就绪'}).waitFor();
  await page.waitForLoadState('networkidle');const startup={ms:Math.round(performance.now()-start),bytes,requests,eventBodies:bodies.length};assert.equal(bodies.length,0);
  if(kind==='identity'){await page.locator('[data-row="1"]').click();await page.locator('#identity-history .record').nth(19).waitFor();await page.locator('#identity-history details summary').first().click();}
  if(kind==='field'){await page.locator('#fe-work').fill('cold');await page.locator('#fe-search button').click();await page.locator('#fe-history [data-field-event]').nth(19).waitFor();await page.locator('#fe-history details summary').first().click();await page.locator('#fe-field').selectOption('firstYear');await page.waitForFunction(()=>!document.getElementById('fe-add-panel').inert);}
  if(kind==='formal'){await page.locator('#open').click();await page.locator('#le-history [data-audit-id]').nth(19).waitFor();await page.locator('#le-history details summary').first().click();assert.equal(await page.locator('[data-le-undo]').count(),3);}
  await page.waitForLoadState('networkidle');const metrics=await cdp.send('Performance.getMetrics'),heapBytes=metrics.metrics.find(m=>m.name==='JSHeapUsedSize').value;
  assert.equal(wholeSourceReads,0);assert.equal(bodies.length,20);assert.ok(bodies.every(e=>auditWorkIds(kind,e).includes('cold')));assert.deepEqual(errors,[]);assert.ok(bytes<1024*1024);assert.ok(heapBytes<64*1024*1024);
  report.environment.browser=browser.version();report.scenarios[kind]={startup,throughUndoPreview:{ms:Math.round(performance.now()-start),bytes,requests,heapBytes,eventBodies:bodies.length},wholeSourceReads,unrelatedEventBodies:0,errors};mkdirSync('test-results',{recursive:true});writeFileSync('test-results/audit-startup-mobile.json',JSON.stringify(report,null,2)+'\n');console.log('AUDIT_STARTUP',kind,JSON.stringify(report.scenarios[kind]));
 }finally{await browser?.close();if(server)await new Promise(r=>server.close(r));rmSync(temp,{recursive:true,force:true});}
});
