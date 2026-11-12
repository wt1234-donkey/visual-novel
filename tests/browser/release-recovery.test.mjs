import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
import {gzipSync} from 'node:zlib';
import {gitFixture} from '../helpers/catalogue-git-fixture.mjs';
import {gitBlobHash} from '../../src/infrastructure/filesystem/basic-store.mjs';
import {planCommand} from '../../src/application/commands/execute.mjs';
import {receiptPath} from '../../src/infrastructure/filesystem/command-executor.mjs';

const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=resolve(import.meta.dirname,'../..'),A='a'.repeat(40),B='b'.repeat(40);
async function fixture(saveMode='legacy'){
 const api=gitFixture();api.changeFile('data/source.json','source');const lease=api.lease(['data/source.json']);
 const files=new Map();let current=A,expired=false;
 for(const revision of [A,B]){
  const put=(path,value)=>{const text=JSON.stringify(value);files.set(path,text);return {path:path.replace(/^data\//,''),sha:gitBlobHash(text)};};
  const order=Array.from({length:60},(_,i)=>i);if(revision===B)order.reverse();
  const index={groups:['Maker'],gameplay:['ADV'],statuses:['promoted-basic'],rows:order.map(i=>['i'+i,'w'+i,'Test '+i,1965,0,0,0])};
  const assets={};assets['basic-index.json']={sha:put('data/basic-web/'+revision+'/basic-index.json',index).sha};
  for(let n=0;n<3;n++)assets['basic-'+n+'.json']={sha:put('data/basic-web/'+revision+'/basic-'+n+'.json',order.slice(n*25,(n+1)*25).map(i=>({source:'https://example.org/'+revision[0]+'/w'+i}))).sha};
  const basic=put('data/catalogue-web/'+revision+'/basic-manifest.json',{schema:1,revision,sourceLease:lease,saveMode,shardSize:25,basic:{total:60,promotedBasic:60,promotedDossier:0,existingComplete:0},home:{total:0},assets});
  const regions=put('data/catalogue-web/'+revision+'/resources/basic-manufacturer-regions.json',{schemaVersion:1,entries:[]});
  const edits=put('data/catalogue-web/'+revision+'/resources/basic-catalogue-edits.json',api.store);
  files.set(revision,JSON.stringify({schemaVersion:1,revision,basic,sourceLease:lease,resources:{'data/basic-manufacturer-regions.json':regions,'data/basic-catalogue-edits.json':edits}}));
 }
 const server=createServer(async(request,response)=>{
  try{
   let path=new URL(request.url,'http://localhost').pathname.slice(1);
   if(path==='data/catalogue-release.json'){response.setHeader('content-type','application/json');response.end(files.get(current));return;}
   if(path==='deployment.json'){response.setHeader('content-type','application/json');response.end(JSON.stringify({revision:current,ancestors:[]}));return;}
   if(expired&&path.includes(A)){response.writeHead(404);response.end();return;}
   if(path.endsWith('.gz')&&files.has(path.slice(0,-3))){response.end(gzipSync(files.get(path.slice(0,-3))));return;}
   if(files.has(path)){response.setHeader('content-type','application/json');response.end(files.get(path));return;}
   const file=resolve(root,path);if(!file.startsWith(root+'/'))throw Error('invalid path');
   response.setHeader('content-type',extname(file)==='.mjs'?'text/javascript':extname(file)==='.css'?'text/css':'text/html');response.end(await readFile(file));
  }catch{response.writeHead(404);response.end();}
 });
 await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
 const browser=await chromium.launch({headless:true});const page=await browser.newPage();
 await page.route('https://api.github.com/**',async route=>{
  const request=route.request();
  if(request.url().includes('/actions/runs')){await route.fulfill({status:200,contentType:'application/json',body:'{"workflow_runs":[]}'});return;}
  if(request.url().endsWith('/dispatches')){
   const body=request.postDataJSON(),command=JSON.parse(api.blobs.get(body.client_payload.commandSha));
   const basicRows=Array.from({length:60},(_,i)=>({id:'i'+i,matchedWorkId:'w'+i,title:'Test '+i,firstYear:1965,group:'Maker',gameplay:'ADV',plotStyles:[],source:'https://example.org/'+current[0]+'/w'+i}));
   const result=planCommand(command,{sourceLease:lease,basicRows,basicStore:api.store},'tester');
   api.publish(result.store);api.changeFile(receiptPath(command.operationId),JSON.stringify(result.receipt));api.calls.push({method:'POST',path:'/dispatches'});
   await route.fulfill({status:204});return;
  }
  const result=await api.fetch(request.url(),{method:request.method(),body:request.postData(),headers:request.headers()});await route.fulfill({status:result.status,contentType:'application/json',body:JSON.stringify(await result.json())});
 });
 const url='http://127.0.0.1:'+server.address().port+'/minimal-adv-rpg.html';
 await page.goto(url);await page.locator('#count').filter({hasText:'找到 60 条'}).waitFor();
 return {api,page,switchRelease:()=>{current=B;expired=true;},close:async()=>{await browser.close();await new Promise(resolve=>server.close(resolve));}};
}
test('actual basic catalogue rebinds an expired release and keeps query, page and stable selection',async()=>{
 const f=await fixture();try{
  const {page}=f;await page.locator('#q').fill('Test');await page.locator('[data-select="w0"]').check();await page.locator('#next').click();
  f.switchRelease();await page.locator('#next').click();await page.waitForURL(/release=bbbb/);
  await page.locator('#catalogue-recovery').filter({hasText:'已恢复到新发布'}).waitFor();
  assert.equal(await page.locator('#q').inputValue(),'Test');assert.match(await page.locator('#pagination').textContent(),/第 3/);assert.match(await page.locator('#basic-selected').textContent(),/1部/);
  await page.locator('#prev').click();await page.locator('#prev').click();
  await page.locator('tr').filter({has:page.locator('[data-select="w0"]')}).getByRole('link',{name:'资料'}).waitFor();
  assert.equal(await page.locator('[data-select="w0"]').isChecked(),true);
  assert.equal(await page.locator('tr').filter({has:page.locator('[data-select="w0"]')}).getByRole('link',{name:'资料'}).getAttribute('href'),'https://example.org/b/w0');
 }finally{await f.close();}
});
test('unsaved actual edit form restores only changed fields and excludes credentials',async()=>{
 const f=await fixture();try{
  const {page}=f;await page.locator('[data-edit="w0"]').click();await page.locator('#be-edit [name=title]').fill('Recovered title');await page.locator('.be-auth summary').click();await page.locator('#be-token').fill('do-not-persist-token');
  f.switchRelease();await page.evaluate(next=>window.dispatchEvent(new CustomEvent('catalogue-release-change',{detail:{nextRevision:next}})),B);
  const saved=await page.evaluate(()=>sessionStorage.getItem('catalogue-release-recovery-v1'));assert.ok(saved.includes('Recovered title'));assert.ok(!saved.includes('do-not-persist-token'));
  await page.getByRole('button',{name:'保留草稿并恢复新发布'}).click();await page.waitForURL(/release=bbbb/);
  await page.locator('#basic-editor fieldset').filter({hasText:'恢复草稿：核对当前值与原输入'}).waitFor();
  assert.equal(await page.locator('#be-edit [name=title]').inputValue(),'Recovered title');assert.equal(await page.locator('#be-token').inputValue(),'');
  assert.equal(await page.locator('#be-edit [name=source]').inputValue(),'https://example.org/b/w0');
  assert.equal(await page.getByLabel('我已核对当前来源与恢复的输入').isChecked(),false);assert.equal(f.api.calls.filter(call=>call.method==='POST').length,0);
  const submitReachesForm=()=>page.locator('#be-edit').evaluate(form=>{let reached=false;form.addEventListener('submit',()=>{reached=true;},{once:true});form.dispatchEvent(new Event('submit',{bubbles:true,cancelable:true}));return reached;});
  assert.equal(await submitReachesForm(),false,'unreviewed recovered input cannot be submitted');
  await page.getByRole('button',{name:'关闭窗口'}).click();await page.locator('[data-edit="w0"]').click();
  assert.equal(await submitReachesForm(),true,'closing the recovered form removes its review gate');
  assert.equal(f.api.calls.filter(call=>call.method==='POST').length,0);
 }finally{await f.close();}
});
test('storage failure leaves the original edit input in place and stops navigation',async()=>{
 const f=await fixture();try{
  const {page}=f;await page.locator('[data-edit="w0"]').click();await page.locator('#be-edit [name=title]').fill('Keep this input');
  await page.evaluate(()=>{Storage.prototype.setItem=function(){throw Error('storage unavailable');};});
  f.switchRelease();await page.evaluate(next=>window.dispatchEvent(new CustomEvent('catalogue-release-change',{detail:{nextRevision:next}})),B);
  await page.locator('#catalogue-recovery').filter({hasText:'已停止刷新'}).waitFor();assert.ok(!page.url().includes('release='));assert.equal(await page.locator('#be-edit [name=title]').inputValue(),'Keep this input');
 }finally{await f.close();}
});
test('trusted mode saves an actual form through dispatch with the existing Contents credential',async()=>{
 const f=await fixture('trusted');try{
  const {page}=f;await page.locator('[data-edit="w0"]').click();await page.locator('.be-auth summary').click();await page.locator('#be-token').fill('test-only-credential');
  await page.locator('#be-connect').click();await page.locator('#be-message').filter({hasText:'已连接'}).waitFor();
  await page.locator('#be-edit [name=title]').fill('Trusted title');await page.getByRole('button',{name:'直接保存修改',exact:true}).click();
  await page.locator('#be-message').filter({hasText:'已提交 GitHub 主分支'}).waitFor();
  assert.equal(f.api.store.records.w0.values.title,'Trusted title');assert.equal(f.api.calls.filter(call=>call.path==='/dispatches').length,1);
  assert.equal(f.api.calls.filter(call=>call.method==='PATCH'||call.path==='/git/commits').length,0,'browser never advances main or creates data commits in trusted mode');
 }catch(error){error.message+='\nSave UI: '+await f.page.locator('#be-message').textContent()+'\nRequests: '+JSON.stringify(f.api.calls.slice(-12).map(call=>({method:call.method,path:call.path})));throw error;}
 finally{await f.close();}
});
