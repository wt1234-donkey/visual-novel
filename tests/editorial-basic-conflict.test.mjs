import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import test from 'node:test';
import {emptyStore,valuesOf} from '../basic-catalogue-model.mjs';
import {makeProposal} from '../editorial-proposal.mjs';
import {applyEditorialBatch} from '../scripts/apply_editorial_batch.mjs';
import {sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';

const storeFile='basic-catalogue-edits.json';
const alpha={id:'a',title:'Alpha',year:1980,group:'Studio',gameplay:'ADV',status:'new-basic'};
const beta={...alpha,id:'b',title:'Beta'};
function fixture(t){
 const dir=mkdtempSync(join(tmpdir(),'editorial-conflict-'));
 t.after(()=>rmSync(dir,{recursive:true,force:true}));
 mkdirSync(join(dir,'data'));
 const write=(name,value)=>writeFileSync(join(dir,'data',name),JSON.stringify(value));
 const read=name=>JSON.parse(readFileSync(join(dir,'data',name)));
 const git=(...args)=>execFileSync('git',args,{cwd:dir,stdio:'pipe'});
 const commit=()=>{git('add','data');git('-c','user.name=Test','-c','user.email=test@example.org','commit','-qm','Test revision');};
 git('init','-q');
 write(storeFile,emptyStore());
 write('main-adv-rpg-works-20261031.json',{works:[],identityReview:[]});
 write('adv-rpg-minimal-index-20261031.json',{records:[alpha,beta]});
 for(const name of ['adv-rpg-next-studio-review-20261031.json','adv-rpg-round3-review-20261031.json'])write(name,{records:[]});
 write('editorial-publications.json',{batches:[]});
 commit();
 const publish=(...proposals)=>applyEditorialBatch({id:crypto.randomUUID(),proposals},dir);
 const proposal=(action,expectedRevision=0)=>makeProposal('basic','核对作品资料',{expectedRevision,action},[{id:action.id||'batch'}]);
 const edit=(work,title)=>proposal({type:'edit',id:work.id,values:{...valuesOf(work),title}});
 return {dir,publish,proposal,edit,write,read,commit};
}

test('approved edits and style updates can publish across unrelated revisions',t=>{
 const f=fixture(t);
 f.publish(f.edit(beta,'Beta revised'));
 f.commit();
 f.publish(f.edit(alpha,'Alpha revised'));
 assert.equal(f.read(storeFile).records.b.values.title,'Beta revised');
 assert.equal(f.read(storeFile).records.a.values.title,'Alpha revised');
 assert.equal(f.read(storeFile).revision,2);
});

test('an approved style batch touching a changed work stops atomically',t=>{
 const f=fixture(t);
 f.publish(f.edit(beta,'Beta revised'));
 f.commit();
 const before=f.read(storeFile),ledger=f.read('editorial-publications.json');
 const rows=[alpha,beta].map(w=>({id:w.id,mode:'append',tags:{theme:'科幻'}}));
 assert.throws(()=>f.publish(f.proposal({type:'style-update',rows})),/目标基础作品已变化（b）/);
 assert.deepEqual(f.read(storeFile),before);
 assert.deepEqual(f.read('editorial-publications.json'),ledger);
 f.publish(f.proposal({type:'style-update',rows:rows.slice(0,1)}));
 assert.equal(f.read(storeFile).records.a.style.plotTags.theme,'科幻');
});

test('a changed underlying catalogue or a stale destructive action requires fresh review',t=>{
 const f=fixture(t);
 f.publish(f.edit(beta,'Beta revised'));
 f.commit();
 assert.throws(()=>f.publish(f.proposal({type:'delete',id:'a'})),/无法自动校验此操作/);
 f.write('adv-rpg-minimal-index-20261031.json',{records:[{...alpha,year:1981},beta]});
 f.commit();
 assert.throws(()=>f.publish(f.edit(alpha,'Alpha revised')),/基础资料已更新/);
 assert.equal(f.read(storeFile).revision,1);
});
test('reviewed batch idempotency compares the complete payload and preserves later edits',t=>{
 const f=fixture(t),p=f.edit(alpha,'Alpha revised'),batch={id:crypto.randomUUID(),proposals:[p]};
 applyEditorialBatch(batch,f.dir);f.commit();f.publish(f.proposal({type:'edit',id:'b',values:{...valuesOf(beta),title:'Beta later'}},1));
 const before=f.read(storeFile);assert.equal(applyEditorialBatch(batch,f.dir).already,true);assert.deepEqual(f.read(storeFile),before);
 assert.throws(()=>applyEditorialBatch({...batch,proposals:[{...p,reason:'changed content'}]},f.dir),/批次ID已用于其他内容/);
 assert.deepEqual(f.read(storeFile),before);
});
test('trusted mode rejects legacy proposals with missing or changed source credentials',t=>{
 const f=fixture(t);f.write('trusted-save-policy.json',{schemaVersion:1,mode:'trusted'});
 const p=f.edit(alpha,'Alpha revised');assert.throws(()=>f.publish(p),error=>error.code==='SOURCE_CHANGED');
 p.change.sourceLease=sourceLeaseSync(f.dir);
 f.write('adv-rpg-minimal-index-20261031.json',{records:[{...alpha,year:1981},beta]});
 assert.throws(()=>f.publish(p),error=>error.code==='SOURCE_CHANGED');assert.equal(f.read(storeFile).revision,0);
});
