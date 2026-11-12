// Reproducible browser benchmark against two immutable static artifacts.
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile,mkdir,writeFile} from 'node:fs/promises';
import {resolve,extname} from 'node:path';
import {gzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const [before,after,out]=process.argv.slice(2);if(!before||!after||!out)throw Error('usage: before-site after-site output-directory');
const roots={before:resolve(before),after:resolve(after)},cache=new Map();
const server=createServer(async(req,res)=>{try{const url=new URL(req.url,'http://localhost'),[,kind,...parts]=url.pathname.split('/'),root=roots[kind],path=resolve(root||'',parts.join('/')||'index.html');if(!root||!path.startsWith(root+'/'))throw Error('path');let entry=cache.get(path);if(!entry){let body=await readFile(path),gzip=!path.endsWith('.gz')&&/\.(json|html|css|mjs|js|svg)$/.test(path);if(gzip)body=gzipSync(body);entry={body,gzip};cache.set(path,entry);}res.setHeader('Cache-Control','no-store');res.setHeader('Content-Type',({'.mjs':'text/javascript','.js':'text/javascript','.html':'text/html','.css':'text/css','.json':'application/json','.svg':'image/svg+xml'})[extname(path)]||'application/octet-stream');if(entry.gzip)res.setHeader('Content-Encoding','gzip');res.end(entry.body);}catch{res.writeHead(404);res.end();}});
await new Promise(r=>server.listen(0,'127.0.0.1',r));const origin='http://127.0.0.1:'+server.address().port;
const browser=await chromium.launch({headless:true}),results=[],faults=[];
const pages=[{name:'发现页',file:'index.html',ready:'#sa-work-results .sa-work'},{name:'管理台',file:'manage.html',ready:'#work-list [data-work]'},{name:'批量页',file:'bulk-import.html',ready:'#basic-rows [data-select]'}];
async function context(){return browser.newContext({viewport:{width:390,height:844},deviceScaleFactor:1,isMobile:true,hasTouch:true});}
try{
 for(const kind of ['before','after'])for(const target of pages)for(let run=1;run<=3;run++){
  const ctx=await context(),page=await ctx.newPage(),cdp=await ctx.newCDPSession(page),requests=new Map(),errors=[];let bytes=0;
  await cdp.send('Performance.enable');await cdp.send('Network.enable');await cdp.send('Network.setCacheDisabled',{cacheDisabled:true});await cdp.send('Network.emulateNetworkConditions',{offline:false,latency:100,downloadThroughput:5_000_000/8,uploadThroughput:5_000_000/8});await cdp.send('Emulation.setCPUThrottlingRate',{rate:4});
  cdp.on('Network.requestWillBeSent',e=>requests.set(e.requestId,e.request.url));cdp.on('Network.loadingFinished',e=>{bytes+=e.encodedDataLength;});page.on('pageerror',e=>errors.push(e.message));
  await page.addInitScript(()=>{window.__longTasks=[];new PerformanceObserver(list=>window.__longTasks.push(...list.getEntries().map(e=>({start:e.startTime,duration:e.duration})))).observe({type:'longtask',buffered:true});});
  const started=Date.now();let usableMs=null,timeout=false,interaction=null;
  try{await page.goto(`${origin}/${kind}/${target.file}`,{waitUntil:'domcontentloaded',timeout:30000});await page.locator(target.ready).first().waitFor({timeout:30000});usableMs=Date.now()-started;}
  catch{timeout=true;}
  const atReadyBytes=bytes,atReadyRequests=requests.size,rawSources=[...requests.values()].filter(x=>/basic-registry\/works-|registry-shards|main-adv-rpg.*\/|\/shards\/main/.test(x));
  const metrics=await cdp.send('Performance.getMetrics').catch(()=>({metrics:[]}));
  if(kind==='after'&&!timeout){const preBytes=bytes,preRequests=requests.size,start=Date.now();
   if(target.file==='index.html'){await page.locator('[data-work]').first().click();await page.locator('.sa-detail-top h1').waitFor();await page.getByRole('heading',{name:'故事概览'}).waitFor();}
   if(target.file==='manage.html'){await page.locator('#work-list [data-work]').first().click();await page.locator('#panel').getByRole('heading',{name:'作品档案',exact:true}).waitFor();}
   if(target.file==='bulk-import.html'){await page.selectOption('#status-filter','available');await page.locator('#basic-rows input[data-select]:enabled').first().waitFor();await page.locator('#basic-rows input[data-select]:enabled').first().check();await page.locator('#queue-selected').click();await page.locator('#queue-list [data-edit]').first().waitFor();}
   interaction={ms:Date.now()-start,bytes:bytes-preBytes,requests:requests.size-preRequests};
  }
  const longTasks=await page.evaluate(()=>window.__longTasks||[]);
  results.push({kind,page:target.name,file:target.file,run,usableMs,timeout,elapsedMs:Date.now()-started,initialBytes:atReadyBytes,initialRequests:atReadyRequests,sourceShardRequests:rawSources.length,allSourceShardRequests:[...requests.values()].filter(x=>/basic-registry\/works-|registry-shards|main-adv-rpg.*\/|\/shards\/main/.test(x)).length,longTasks:longTasks.length,longestTaskMs:Math.max(0,...longTasks.map(t=>t.duration)),heapBytes:metrics.metrics.find(x=>x.name==='JSHeapUsedSize')?.value??null,interaction,errors});
  console.log(JSON.stringify(results.at(-1)));await mkdir(out,{recursive:true});await writeFile(resolve(out,'samples-in-progress.json'),JSON.stringify({results,faults},null,2));await ctx.close();
 }
 // Use actual generated resources and actual pages for degradation/retry tests.
 const ctx=await context(),page=await ctx.newPage();let notesFail=true,creatorsFail=true;
 await page.route('**/on-demand/notes-*',route=>notesFail?route.fulfill({status:503,body:'unavailable'}):route.continue());
 await page.route('**/on-demand/creators.json*',route=>creatorsFail?route.fulfill({status:503,body:'unavailable'}):route.continue());
 await page.goto(`${origin}/after/index.html`);await page.locator('[data-work]').first().click();await page.getByRole('heading',{name:'故事概览'}).waitFor();await page.locator('[data-retry-resource^="notes:"]').waitFor();await page.locator('[data-retry-resource="creators"]').waitFor();faults.push('附注和个人署名503不阻断目录或作品档案，并显示独立重试');
 notesFail=false;creatorsFail=false;await page.locator('[data-retry-resource^="notes:"]').click();await page.locator('[data-retry-resource="creators"]').click();await page.locator('[data-retry-resource="creators"]').waitFor({state:'detached'});faults.push('失败后重试恢复，失败Promise未污染缓存');
 await page.goto(`${origin}/after/manage.html`);await page.locator('#work-list [data-work]').first().click();await page.locator('#panel').getByRole('heading',{name:'作品档案',exact:true}).waitFor();await page.locator('[data-tab="notes"]').click();await page.locator('#edit-form').waitFor();faults.push('管理台选择作品和切换附注均按需完成，编辑基线已加载');
 // Silent Worker: real 4s production deadline, then the ordinary main-thread path.
 const worker=await page.evaluate(async()=>{const {createCatalogueWorker}=await import('./basic-catalogue-index.mjs');let terminated=0;class Silent{postMessage(){}terminate(){terminated++;}}const search=createCatalogueWorker({WorkerClass:Silent});const start=performance.now(),result=await search({kind:'home'});return {ms:performance.now()-start,result,terminated};});assert.equal(worker.result,null);assert.equal(worker.terminated,1);assert.ok(worker.ms<5000);faults.push(`Worker无响应 ${Math.round(worker.ms)}ms 终止并返回回退信号`);
 await ctx.close();
 for(const r of results.filter(r=>r.kind==='after')){assert.equal(r.timeout,false,`${r.page} unavailable`);assert.equal(r.allSourceShardRequests,0,`${r.page} read original source shards`);assert.deepEqual(r.errors,[]);}
 const report={schemaVersion:1,recordedAt:new Date().toISOString(),environment:{browser:browser.version(),viewport:'390×844',bandwidthMbps:5,latencyMs:100,cpuSlowdown:4,runsPerPage:3,cache:'cold fresh browser context, network cache disabled',transport:'local static server; gzip for text, explicit .json.gz left as binary',readiness:'first visible catalogue row; optional resources excluded',limitations:'Chromium simulation only; no Android physical-device test; baseline >30s marked censored, not zero; time-to-usable is operational selector, not standardized TTI'},revisions:{before:JSON.parse(await readFile(resolve(before,'deployment.json'),'utf8')).revision,after:JSON.parse(await readFile(resolve(after,'deployment.json'),'utf8')).revision},results,faults};
 await mkdir(out,{recursive:true});await writeFile(resolve(out,'mobile-performance.json'),JSON.stringify(report,null,2)+'\n');
 const median=values=>[...values].sort((a,b)=>a-b)[Math.floor(values.length/2)];
 let md=`# 第3批手机性能测量\n\n测量时间：${report.recordedAt}\n\n基线：${report.revisions.before}\n候选：${report.revisions.after}\n\n390×844、5Mbps、100ms RTT、CPU 4倍降速；每页每版本3次冷启动。Chromium ${report.environment.browser}。本地静态服务按gzip传输；非Android真机实测。可用时间以首条目录可交互为准，不称为标准TTI。\n\n|页面|版本|可用时间中位数|首屏压缩流量中位数|请求数中位数|原109源分片请求|最长任务最大值|\n|---|---|---:|---:|---:|---:|---:|\n`;
 for(const target of pages)for(const kind of ['before','after']){const rows=results.filter(r=>r.page===target.name&&r.kind===kind),times=rows.filter(r=>r.usableMs!==null).map(r=>r.usableMs);md+=`|${target.name}|${kind==='before'?'优化前':'优化后'}|${times.length===3?(median(times)/1000).toFixed(2)+'s':'30s内未全部就绪（截尾）'}|${(median(rows.map(r=>r.initialBytes))/1048576).toFixed(2)}MiB|${median(rows.map(r=>r.initialRequests))}|${Math.max(...rows.map(r=>r.sourceShardRequests))}|${Math.round(Math.max(...rows.map(r=>r.longestTaskMs)))}ms|\n`;}
 md+='\n压缩流量统计CDP loadingFinished.encodedDataLength，含协议开销；超时基线的字节数仅为停止前已完成请求量下限。选择单部作品的增量及每次测量、JS堆、长任务、错误保存在同名JSON。长任务与堆可能包含交互阶段。\n\n'+faults.map(s=>'- '+s).join('\n')+'\n\n验收预算：优化后三页首屏中位数≤5s、≤2MiB；0个原始源分片读取；Worker≤5s终止回退。任何超标以原始数据为准，不据体积推算冒充实测。\n';
 await writeFile(resolve(out,'mobile-performance.md'),md);
}catch(error){console.error(error);process.exitCode=1;}finally{await browser.close();await new Promise(r=>server.close(r));}
