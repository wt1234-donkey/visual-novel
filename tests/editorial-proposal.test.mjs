import test from 'node:test';
import assert from 'node:assert/strict';
import {validateProposal,makeProposal,editorialDraftURL} from '../editorial-proposal.mjs';
import worker from '../editorial-service/worker.mjs';

test('editorial draft carries one immutable proposal and retains source provenance',()=>{
 const p=makeProposal('basic','更正原作资料',{expectedRevision:5,action:{type:'edit',id:'g073',values:{}}},[{id:'g073',before:'原值',after:'新值'}],['https://example.org/game','javascript:alert(1)']);
 assert.equal(p.sources.length,1);
 assert.deepEqual(JSON.parse(decodeURIComponent(new URL(editorialDraftURL(p)).hash.slice(7))),p);
 assert.throws(()=>validateProposal({...p,change:{...p.change,expectedRevision:-1}}),/基础作品操作/);
 assert.throws(()=>validateProposal({...p,preview:[{after:'大'.repeat(30000)}]}),/55 KB/);
});

test('worker rejects cross-origin mutation and submissions without trusted identity',async()=>{
 const origin='https://editorial.example.org';
 const request=host=>new Request(origin+'/api/submit',{method:'POST',headers:{Origin:host,'Content-Type':'application/json'},body:'{}'});
 const db={prepare(){throw Error('the database must not be reached');}};
 assert.equal((await worker.fetch(request('https://outside.example.org'),{DB:db})).status,403);
 assert.equal((await worker.fetch(request(origin),{DB:db})).status,401);
});

test('a basic editor cannot approve or publish queue items',async()=>{
 const origin='https://editorial.example.org';
 const db={prepare(sql){return {bind(){return {run:async()=>({meta:{changes:0}}),first:async()=>sql.includes('SELECT role')?{role:'editor'}:null};}};}};
 for(const action of ['review','publish','member']){
  const request=new Request(origin+'/api/'+action,{method:'POST',headers:{Origin:origin,'Content-Type':'application/json',
   'oai-authenticated-user-id':'signed-user','oai-authenticated-user-email':'editor@example.org'},body:'{}'});
  assert.equal((await worker.fetch(request,{DB:db})).status,403);
 }
});
