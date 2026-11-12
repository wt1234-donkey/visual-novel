import {readFile,writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {gunzipSync} from 'node:zlib';
import assert from 'node:assert/strict';
import {createOnDemandReader} from '../src/infrastructure/storage/on-demand-reader.mjs';
import {createCatalogueWorker} from '../basic-catalogue-index.mjs';
const [site,out]=process.argv.slice(2);if(!site)throw Error('usage: static-artifact [output.json]');
function session(){const calls=[];let bytes=0;const fetcher=async url=>{calls.push(url);try{const buffer=await readFile(resolve(site,String(url).replace(/^\.\//,'')));bytes+=buffer.length;return new Response(buffer);}catch{return new Response('',{status:404});}};return {reader:createOnDemandReader(fetcher),calls,get bytes(){return bytes;}};}
const results=[];
for(const kind of ['formal','bulk']){
 const s=session(),d=await s.reader.directory(kind);if(kind==='bulk')await s.reader.bulkPage({status:'available'});
 const firstCalls=[...s.calls],firstBytes=s.bytes;
 if(kind==='formal')await s.reader.formal('g039');else {const first=(await s.reader.bulkPage({status:'available'})).rows[0];assert.deepEqual((await s.reader.bulk([first.work.indexId])).get(first.work.indexId),first);}
 assert.ok(!s.calls.some(url=>url.includes('/basic-registry/')||url.endsWith('/inputs.json')));
 results.push({kind,directoryCount:kind==='formal'?d.ids.length:d.count,catalogueRequests:firstCalls.length,catalogueBytes:firstBytes,singleWorkExtraRequests:s.calls.length-firstCalls.length,singleWorkExtraBytes:s.bytes-firstBytes,rawSourceShardRequests:0,paths:s.calls});
}
let terminated=0;class Silent {postMessage(){} terminate(){terminated++;}}
const start=performance.now(),search=createCatalogueWorker({WorkerClass:Silent});assert.equal(await search({kind:'home'}),null);const workerFallbackMs=performance.now()-start;assert.ok(workerFallbackMs<5000);assert.equal(terminated,1);
const manifest=JSON.parse(await readFile(resolve(site,'data/catalogue-release.json'),'utf8')),bulk=JSON.parse(gunzipSync(await readFile(resolve(site,'data',manifest.catalogues.bulk.gzip))));
const searchBytes=(await readFile(resolve(site,'data',bulk.search.gzip))).length;
const result={schemaVersion:1,revision:manifest.revision,measuredAt:new Date().toISOString(),method:'Node filesystem adapter invoking production readers; actual compressed file bytes, no HTTP headers/modules/HTML; not a mobile browser timing measurement',results,workerFallbackMs,workerEnvironment:'Node silent-Worker stub, production default 4000ms deadline',lazyBulkSearchGzipBytes:searchBytes};
if(out)await writeFile(out,JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result,null,2));
