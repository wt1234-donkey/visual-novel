import test from 'node:test';
import assert from 'node:assert/strict';
import {readReleaseManifest,readReleaseJson} from '../src/infrastructure/storage/release-reader.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';
import {createBasicWebIndex} from '../basic-catalogue-index.mjs';
import {operationReceipt,publicationState} from '../src/application/publication/status.mjs';
import {checkPublication} from '../src/features/publication-status.mjs';
import {captureChangedFields} from '../src/features/release-recovery.mjs';

const A='a'.repeat(40),B='b'.repeat(40),C='c'.repeat(40);
async function fixture(){
 const files=new Map(),requests=[];let current=A;
 for(const revision of [A,B]){
  const text=JSON.stringify({name:revision===A?'original':'updated'}),path='catalogue-web/'+revision+'/resources/taxonomy.json';
  const detail=JSON.stringify([{source:revision}]),detailPath='basic-web/'+revision+'/basic-0.json';
  const basic=JSON.stringify({schema:1,revision,shardSize:1,basic:{total:1},home:{total:0},assets:{'basic-0.json':{sha:await blobDigest(detail)}}});
  const basicPath='catalogue-web/'+revision+'/basic-manifest.json';
  files.set(path,text);files.set(detailPath,detail);files.set(basicPath,basic);
  files.set(revision,{schemaVersion:1,revision,resources:{'data/taxonomy.json':{path,sha:await blobDigest(text)}},basic:{path:basicPath,sha:await blobDigest(basic)}});
 }
 const fetcher=async url=>{
  requests.push(url);let value=url==='./data/catalogue-release.json'?files.get(current):files.get(url.replace(/^(?:\.\/)?data\//,''));
  return {ok:value!==undefined,status:value===undefined?404:200,text:async()=>value,json:async()=>typeof value==='string'?JSON.parse(value):value};
 };
 return {files,requests,fetcher,setCurrent:value=>{current=value;}};
}
test('all resources stay on one verified snapshot even after the root manifest advances',async()=>{
 const f=await fixture();await readReleaseManifest(f.fetcher);f.setCurrent(B);
 assert.deepEqual(await readReleaseJson('data/taxonomy.json',f.fetcher),{name:'original'});
 const index=createBasicWebIndex(f.fetcher);assert.equal((await index.meta()).revision,A);
 assert.deepEqual((await index.details('basic',[0])).get(0),{source:A});
 assert.equal(f.requests.filter(path=>path==='./data/catalogue-release.json').length,1);
});
test('a removed old detail requests a release rebind instead of interpreting an old slot in the new index',async()=>{
 const f=await fixture(),index=createBasicWebIndex(f.fetcher);await index.meta();f.setCurrent(B);f.files.delete('basic-web/'+A+'/basic-0.json');
 await assert.rejects(index.details('basic',[0]),error=>error.code==='RELEASE_CHANGED'&&error.previousRevision===A&&error.nextRevision===B);
 assert.equal((await index.meta()).revision,A);assert.ok(!f.requests.includes('data/basic-web/'+B+'/basic-0.json'));
 const rebound=createBasicWebIndex(f.fetcher);assert.equal((await rebound.meta()).revision,B);
 assert.deepEqual((await rebound.details('basic',[0])).get(0),{source:B});
});
test('corrupt resources and details fail checksum validation without returning unchecked root data',async()=>{
 const f=await fixture();f.files.set('catalogue-web/'+A+'/resources/taxonomy.json','{}');
 await assert.rejects(readReleaseJson('data/taxonomy.json',f.fetcher),/摘要/);
 const index=createBasicWebIndex(f.fetcher);await index.meta();f.files.set('basic-web/'+A+'/basic-0.json','[]');
 await assert.rejects(index.details('basic',[0]),/摘要/);
});
const receipt=commit=>operationReceipt({operationId:'op-'+commit[0],kind:'basic',revision:1,commit,at:'2026-11-12T00:00:00Z'});
test('three saved operations are all published by a single later cumulative release',async()=>{
 const receipts=[A,B,C].map(receipt),deployment={revision:'d'.repeat(40),ancestors:[A,B,C]};let requests=0;
 const rows=await checkPublication(receipts,async url=>{requests++;assert.equal(url,'./deployment.json');return {ok:true,json:async()=>deployment};});
 assert.deepEqual(rows.map(row=>row.state),['published','published','published']);assert.equal(requests,1);
});
test('a failed descendant build reports failure, whereas missing API access reports uncertainty',async()=>{
 const saved=receipt(A),run={head_sha:B,path:'.github/workflows/pages.yml',event:'push',status:'completed',conclusion:'failure',created_at:'2026-11-12T00:10:00Z',html_url:'https://github.com/wt1234-donkey/visual-novel/actions/runs/1'};
 const rows=await checkPublication([saved],async url=>({ok:true,json:async()=>url==='./deployment.json'?{revision:C,ancestors:[]}:url.includes('/actions/')?{workflow_runs:[run]}:{status:'ahead'}}));
 assert.equal(rows[0].state,'failed');assert.equal(rows[0].url,run.html_url);
 const unknown=await checkPublication([saved],async()=>({ok:false,status:403}));assert.equal(unknown[0].state,'unknown');
});
test('rollback never claims that newer saved data is online, and a later normal publication resolves it',()=>{
 const saved=receipt(B),deployment={revision:A,ancestors:[A],rollback:{at:'2026-11-12T01:00:00Z'}};
 assert.equal(publicationState(saved,deployment).state,'rollback');
 assert.equal(publicationState(saved,{revision:C,ancestors:[A,B,C]}).state,'published');
});
test('recovery captures only changed non-secret fields and never stores credentials or confirmation',()=>{
 const field=(name,type,value,initial)=>({name,id:'',type,value,defaultValue:initial,tagName:'INPUT'});
 const fields=[field('title','text','draft','source'),field('group','text','maker','maker'),field('token','password','secret',''),field('upload','file','local',''),field('confirmed','checkbox','on','')];
 assert.deepEqual(captureChangedFields({querySelectorAll:()=>fields}),[{name:'title',id:'',type:'text',option:null,before:'source',value:'draft'}]);
});
