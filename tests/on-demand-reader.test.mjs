import test from 'node:test';
import assert from 'node:assert/strict';
import {createOnDemandReader} from '../src/infrastructure/storage/on-demand-reader.mjs';
import {withDeadline,requestScope} from '../src/infrastructure/storage/async-read.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';
import {createCatalogueWorker,createHomeSearch} from '../basic-catalogue-index.mjs';
const revision='a'.repeat(40);
test('an unresponsive Worker terminates, resolves all callers, and stays on fallback',async()=>{
 let terminated=0;class Silent {postMessage(){} terminate(){terminated++;}}
 const search=createCatalogueWorker({WorkerClass:Silent,timeout:30}),started=Date.now();
 assert.deepEqual(await Promise.all([search({kind:'home'}),search({kind:'home'})]),[null,null]);
 assert.ok(Date.now()-started<500);assert.equal(terminated,1);assert.equal(await search({kind:'home'}),null);
});
test('cancelling one Worker query does not reject another or accept a late stale result',async()=>{
 let worker;class Responding {constructor(){worker=this;}postMessage(message){(this.messages??=[]).push(message);}terminate(){}}
 const search=createCatalogueWorker({WorkerClass:Responding,timeout:100}),abort=new AbortController();
 const first=search({kind:'home',query:'old'},{signal:abort.signal}),second=search({kind:'home',query:'new'});abort.abort();await assert.rejects(first,{name:'AbortError'});
 worker.onmessage({data:{id:worker.messages[0].id,result:'old'}});worker.onmessage({data:{id:worker.messages[1].id,result:'new'}});assert.equal(await second,'new');
});
test('deadline covers a hung body and aborts its signal even when the adapter ignores it',async()=>{
 let signal;await assert.rejects(withDeadline(s=>{signal=s;return new Promise(()=>{});},{timeout:15}),{name:'TimeoutError'});assert.ok(signal.aborted);
 const scope=requestScope(),old=scope.start(),next=scope.start();assert.ok(old.signal.aborted);assert.ok(!old.current());assert.ok(next.current());
});
test('stable IDs read only their published detail shard; failed optional resources retry independently',async()=>{
 const files=new Map(),calls=[];const put=async(name,value)=>{const path=`catalogue-web/${revision}/on-demand/${name}.json`,text=JSON.stringify(value);files.set('./data/'+path,text);return {path,sha:await blobDigest(text)};};
 const formal=await put('formal-0',{one:{source:{id:'one'},work:{id:'one'},contentVersions:[],platformReleases:[]}}),notes=await put('notes-0',{one:[]});
 const directory=await put('formal-directory',{schemaVersion:1,revision,ids:['one'],shardSize:25,families:{formal:{0:formal},notes:{0:notes}}});
 files.set('./data/catalogue-release.json',JSON.stringify({schemaVersion:1,revision,catalogues:{formal:directory}}));let fail=true;
 const fetcher=async url=>{calls.push(url);if(url.includes('notes-0')&&fail)return new Response('',{status:503});return new Response(files.get(url),{status:files.has(url)?200:404});};
 const reader=createOnDemandReader(fetcher);assert.equal((await reader.formal('one')).work.id,'one');await assert.rejects(reader.formal('one','notes'),/503/);assert.equal((await reader.formal('one')).work.id,'one');fail=false;assert.deepEqual(await reader.formal('one','notes'),[]);
 assert.equal(calls.filter(path=>path.includes('formal-0')).length,1);assert.ok(!calls.some(path=>/registry|inputs.json|source-shards/.test(path)));
});
