import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {createHash} from 'node:crypto';
import {checkSourceIdentities} from '../scripts/migrate_source_identities.mjs';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {journalKey} from '../src/domain/catalogue/journal.mjs';
import {buildSourceIdentityCatalogue,emptyIdentityStore,applyIdentityReview,validateIdentityStore,identityFormalLinks,identityHistory} from '../src/domain/catalogue/source-identities.mjs';
import {scanRegistry} from '../bulk-import-model.mjs';
import {emptyStore} from '../src/domain/catalogue/model.mjs';
import {sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {executeCommand,receiptPath} from '../src/infrastructure/filesystem/command-executor.mjs';
import {planCommand} from '../src/application/commands/execute.mjs';
import {createCommandSession} from '../src/application/commands/session.mjs';
import {buildSourceIdentityIndex} from '../scripts/build_source_identity_index.mjs';
import {createSourceIdentityReader} from '../src/infrastructure/storage/source-identity-reader.mjs';
const source=(id,title='Twin',year=1990)=>({id,indexId:'index-'+id,title,aliases:[],firstYear:year,gameplay:'ADV',group:'Source Maker',source:'https://example.org/shared-catalogue',sourceRefs:['source:'+id],intakePolicy:'append-without-deduplication',mainPlacement:'promoted-basic',linkedRecordId:null});
const records=()=>[source('s-a'),source('s-b'),{...source('s-c','Known',2001),linkedRecordId:'g001',mainPlacement:'existing-complete'}];
const formal=[{id:'g001',title:'Known',firstYear:2001}];
const registry=works=>({works,identityReview:[],summary:{accepted:works.length}});
const catalogue=(store=emptyIdentityStore(),rows=records(),profiles=formal)=>buildSourceIdentityCatalogue({registry:registry(rows),legacyRows:rows.map(w=>({...w,matchedWorkId:w.id})),formalWorks:profiles,decisions:store,visible:{basicVisibleGroups:rows.length,bulkVisibleGroups:rows.length}});
const meta=(id,revision)=>({id,actor:'tester',at:'2026-11-13T03:00:00Z',reason:'核对来源和作品的明确身份',sources:['https://example.org/identity-evidence'],expectedRevision:revision});
const twinCase='name-year:twin|1990';
const resolve={type:'resolve',caseId:twinCase,outcome:'same-work',links:[{sourceId:'s-a',workId:'s-a'},{sourceId:'s-b',workId:'s-a'}]};
const apply=(store,action,id)=>applyIdentityReview(store,catalogue(store),action,meta(id,store.revision));

test('migration keeps source IDs, order, original evidence and no-dedup rows, without treating provisional works as reviewed',()=>{
 const rows=records(),before=structuredClone(rows),c=catalogue(emptyIdentityStore(),rows);
 assert.deepEqual(rows,before);assert.deepEqual([...c.sources.keys()],rows.map(w=>w.id));assert.equal(c.stats.sourceRecordCount,3);
 assert.equal(c.stats.resolvedWorkCount,1);assert.equal(c.stats.reviewedWorkCount,0);assert.equal(c.stats.unreviewedSources,2);
 assert.equal(c.links.get('s-a').workId,'s-a');assert.equal(c.links.get('s-b').workId,'s-b');assert.equal(c.links.get('s-c').workId,'g001');
 assert.equal(c.cases.get(twinCase).sourceIds.length,2);assert.ok(c.works.has('s-a')&&c.works.has('s-b'));
});

test('shared source URLs and identical names/years only generate candidates, never a link or automatic merge',()=>{
 const rows=records();rows[0].sourceRefs=rows[1].sourceRefs=['shared:catalogue'];const c=catalogue(emptyIdentityStore(),rows);
 assert.equal(c.links.get('s-a').status,'unreviewed');assert.equal(c.links.get('s-b').status,'unreviewed');
 assert.equal(c.cases.get(twinCase).status,'open');assert.equal(c.stats.basicVisibleGroups,3);
 assert.ok(scanRegistry(registry(rows.slice(0,2)),[{id:'g099',title:'Twin',firstYear:1990}]).every(r=>r.status==='conflict'));
});

test('explicit same-work resolution changes only link/case decisions and counts distinct resolved targets separately from sources',()=>{
 const store=emptyIdentityStore(),c=catalogue(store),before=structuredClone([...c.sources.values()].map(s=>s.record));
 const next=applyIdentityReview(store,c,resolve,meta('review-1',0)),after=catalogue(next);
 assert.deepEqual(store,emptyIdentityStore());assert.equal(after.links.get('s-b').workId,'s-a');assert.equal(after.stats.sourceRecordCount,3);
 assert.equal(after.stats.reviewedWorkCount,1);assert.equal(after.stats.resolvedWorkCount,2);assert.equal(after.stats.basicVisibleGroups,3);
 assert.equal(after.cases.get(twinCase).status,'resolved');assert.deepEqual([...after.sources.values()].map(s=>s.record),before);
 assert.equal(next.events[0].sources[0],'https://example.org/identity-evidence');
});

test('an explicit distinct-work decision lets reviewed independent identities pass collision checks without merging them',()=>{
 const distinct={...resolve,outcome:'distinct',links:[{sourceId:'s-a',workId:'s-a'},{sourceId:'s-b',workId:'s-b'}]};
 const next=apply(emptyIdentityStore(),distinct,'different'),c=catalogue(next);
 assert.equal(c.links.get('s-a').workId,'s-a');assert.equal(c.links.get('s-b').workId,'s-b');assert.equal(c.stats.reviewedWorkCount,2);
 assert.ok(c.links.get('s-a').distinctFrom.includes('s-b'));
 const rows=records().slice(0,2).map(w=>({...w,identityLink:c.links.get(w.id)}));assert.ok(scanRegistry(registry(rows),[]).every(r=>r.status==='available'));
});

test('undo appends its own event, restores earlier links and keeps later unrelated review results',()=>{
 let store=apply(emptyIdentityStore(),resolve,'first');
 store=apply(store,{type:'resolve',caseId:'source:s-c',outcome:'link',links:[{sourceId:'s-c',workId:'g001'}]},'unrelated');
 const kept=structuredClone(store.links['s-c']),events=structuredClone(store.events);
 const undone=apply(store,{type:'undo',targetId:'first'},'undo-first');
 assert.deepEqual(undone.links['s-c'],kept);assert.equal(undone.links['s-a'],undefined);assert.deepEqual(undone.events.slice(0,2),events);
 assert.equal(undone.events[2].undoOf,'first');assert.equal(undone.revision,3);assert.ok(validateIdentityStore(undone));
});

test('later reviews of the same source, even reaffirming its target, prevent an older undo from replacing them',()=>{
 let store=apply(emptyIdentityStore(),resolve,'first');
 store=apply(store,{type:'resolve',caseId:'source:s-a',outcome:'link',links:[{sourceId:'s-a',workId:'s-a'}]},'reaffirmed');
 const before=structuredClone(store);assert.throws(()=>apply(store,{type:'undo',targetId:'first'},'bad-undo'),/后续修改/);assert.deepEqual(store,before);
});

test('full review history survives more than three operations and uses monotonic independent undo events',()=>{
 let store=emptyIdentityStore();for(let n=0;n<9;n++)store=apply(store,{type:'resolve',caseId:'source:s-a',outcome:'link',links:[{sourceId:'s-a',workId:'s-a'}]},'op-'+n);
 assert.equal(identityHistory(store,{limit:4}).events.length,4);assert.equal(identityHistory(store,{before:6,limit:10}).events.length,5);assert.equal(store.events.length,9);
 store=apply(store,{type:'undo',targetId:'op-8'},'undo');assert.equal(store.events.length,10);assert.equal(store.links['s-a'].operationId,'op-7');
});

test('event replay rejects modified commands, before-values, current state, undo targets and duplicate operation IDs',()=>{
 const original=apply(emptyIdentityStore(),resolve,'first');const mutations=[s=>s.links['s-a'].workId='s-b',s=>s.events[0].changes[0].before={},s=>s.events[0].intent.links[0].workId='s-b',s=>s.events.push(structuredClone(s.events[0]))];
 for(const change of mutations){const s=structuredClone(original);change(s);assert.throws(()=>validateIdentityStore(s));}
 const undo=apply(original,{type:'undo',targetId:'first'},'undo');undo.events[1].intent.targetId='different';assert.throws(()=>validateIdentityStore(undo));
});

test('unknown identities, incomplete case conclusions, forged actors, missing evidence and stale revisions are refused',()=>{
 const c=catalogue();const invalid=[{...resolve,links:[{sourceId:'missing',workId:'s-a'}]},{...resolve,links:[{sourceId:'s-a',workId:'absent'},{sourceId:'s-b',workId:'absent'}]}, {...resolve,links:resolve.links.slice(0,1)}];
 for(const action of invalid)assert.throws(()=>applyIdentityReview(emptyIdentityStore(),c,action,meta('bad',0)));
 assert.throws(()=>applyIdentityReview(emptyIdentityStore(),c,resolve,{...meta('bad',0),sources:[]}));
 assert.throws(()=>applyIdentityReview(emptyIdentityStore(),c,resolve,meta('stale',1)),/修订已变化/);
 const lease={schemaVersion:1,files:{'data/source.json':'a'.repeat(40)}};
 assert.throws(()=>planCommand({schemaVersion:1,operationId:'forged',kind:'identity',actor:'other',at:meta('x',0).at,reason:meta('x',0).reason,sources:meta('x',0).sources,expectedRevision:0,sourceLease:lease,action:resolve},{sourceLease:lease,identityStore:emptyIdentityStore(),sourceIdentity:c},'tester'),/操作人/);
});

test('additional source records reopen a resolved candidate while preserving previous explicit links and original IDs',()=>{
 const store=apply(emptyIdentityStore(),resolve,'first'),rows=[...records(),source('s-new')],c=catalogue(store,rows);
 assert.equal(c.cases.get(twinCase).status,'needs-recheck');assert.equal(c.links.get('s-new').status,'unreviewed');assert.equal(c.links.get('s-b').workId,'s-a');assert.equal(c.stats.sourceRecordCount,4);
});

test('a formal promotion uses its explicit source index and retains the existing work identity',()=>{
 const independent=apply(emptyIdentityStore(),{type:'resolve',caseId:'source:s-a',outcome:'link',links:[{sourceId:'s-a',workId:'s-a'}]},'independent');
 const before=catalogue(independent),after=catalogue(independent,records(),[...formal,{id:'g900',basicRegistryId:'index-s-a',title:'Formal Twin',firstYear:1990}]);
 assert.equal(after.links.get('s-a').workId,'s-a');assert.equal(after.works.size,before.works.size);assert.ok(after.works.get('s-a').profileIds.includes('g900'));
 assert.equal(identityFormalLinks(after)['s-a'],'g900');assert.equal(after.stats.formalProfiles,2);
});

function fixture(){const root=mkdtempSync(join(tmpdir(),'source-identities-'));const put=(name,value)=>{const path=join(root,name);mkdirSync(dirname(path),{recursive:true});writeFileSync(path,JSON.stringify(value));};
 put('data/main-adv-rpg-works-20261031.json',registry(records()));put('data/basic-catalogue-edits.json',emptyStore());put('data/games.json',{works:formal,contentVersions:[],platformReleases:[]});put('data/non-rpg-creator-supplement-20261030.json',{works:[],contentVersions:[],platformReleases:[]});put('data/work-edit-history.json',{schemaVersion:1,records:{}});put('data/company-coverage.json',{companies:[]});put('data/source-identity-decisions.json',emptyIdentityStore());put('data/taxonomy.json',{});
 for(const n of ['adv-rpg-minimal-index-20261031','adv-rpg-next-studio-review-20261031','adv-rpg-round3-review-20261031'])put('data/'+n+'.json',{records:[]});return {root,put};}

test('identity commands stage one decision journal plus its receipt; retry after later edits confirms without rewriting either',()=>{
 const f=fixture();try{const before=readFileSync(join(f.root,'data/main-adv-rpg-works-20261031.json'),'utf8');const cmd={schemaVersion:1,operationId:'first',kind:'identity',actor:'tester',at:meta('x',0).at,reason:meta('x',0).reason,sources:meta('x',0).sources,expectedRevision:0,sourceLease:sourceLeaseSync(f.root),action:resolve};
 const a=executeCommand(f.root,cmd,'tester');assert.deepEqual(a.paths,['data/source-identity-decisions.json',receiptPath(cmd.operationId)]);
 const later={...cmd,operationId:'later',expectedRevision:1,sourceLease:sourceLeaseSync(f.root),action:{type:'resolve',caseId:'source:s-c',outcome:'link',links:[{sourceId:'s-c',workId:'g001'}]}};executeCommand(f.root,later,'tester');
 const state=readFileSync(join(f.root,'data/source-identity-decisions.json'),'utf8');assert.equal(executeCommand(f.root,cmd,'tester').alreadyApplied,true);assert.equal(readFileSync(join(f.root,'data/source-identity-decisions.json'),'utf8'),state);assert.equal(readFileSync(join(f.root,'data/main-adv-rpg-works-20261031.json'),'utf8'),before);
 }finally{rmSync(f.root,{recursive:true,force:true});}
});

test('source/identity page readers fetch only required lookup/pages and read original source data only on explicit request',async()=>{
 const f=fixture(),output=join(f.root,'public'),revision='a'.repeat(40);try{const built=buildSourceIdentityIndex(f.root,output,revision),files=new Map();
 const registryRaw=readFileSync(join(f.root,'data/main-adv-rpg-works-20261031.json'),'utf8'),path='catalogue-web/'+revision+'/resources/registry.json';mkdirSync(join(output,'data',path,'..'),{recursive:true});writeFileSync(join(output,'data',path),registryRaw);
 const sha=text=>createHash('sha1').update('blob '+Buffer.byteLength(text)+'\0'+text).digest('hex');
 const release={schemaVersion:1,revision,catalogues:{sourceIdentities:built.ref},resources:{'data/main-adv-rpg-works-20261031.json':{path,sha:sha(registryRaw)}}};let rawReads=0;const calls=[];
 const fetcher=async url=>{const path=String(url).replace(/^\.\//,'');calls.push(path);if(path==='data/catalogue-release.json')return new Response(JSON.stringify(release));if(path.includes('/resources/'))rawReads++;return new Response(readFileSync(join(output,path)));};
 const reader=createSourceIdentityReader(fetcher),page=await reader.page('sources');assert.equal(page.rows.length,3);assert.equal(rawReads,0);
 const selected=await reader.byIds('sources',['s-a','s-b']);assert.equal(selected[0].id,'s-a');assert.equal(rawReads,0);assert.equal((await reader.original(selected[0])).id,'s-a');assert.equal(rawReads,1);
 assert.equal((await reader.page('cases',{query:'Twin'})).rows.length,1);assert.equal((await reader.byIds('works',['g001']))[0].id,'g001');
 }finally{rmSync(f.root,{recursive:true,force:true});}
});

test('unknown-response identity commands retain their immutable ID across reload, then confirm the existing receipt',async()=>{
 const data=new Map(),storage={getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v),removeItem:k=>data.delete(k)};
 const command={schemaVersion:1,kind:'identity',operationId:'pending',actor:'tester',at:meta('x',0).at,reason:meta('x',0).reason,sources:meta('x',0).sources,expectedRevision:0,sourceLease:{schemaVersion:1,files:{}},action:resolve};
 const first=createCommandSession({kind:'identity',storage});await assert.rejects(()=>first.execute(command,async()=>{throw Error('response lost');}));
 const second=createCommandSession({kind:'identity',storage});const result=await second.execute({...command,operationId:'new-id'},async original=>original);assert.deepEqual(result,command);assert.equal(data.size,0);
});


test('migration guard freezes the original source prefix while permitting later source appends and explicit profile admission',()=>{
 const f=fixture();try{
  const {inputs,snapshot}=loadCatalogueSnapshot(f.root),sha=createHash('sha256');for(const row of inputs.registry.works)sha.update(journalKey(row)+'\n');
  f.put('config/source-identity-baseline.json',{sourceRecordCount:3,sourceRecordsSha256:sha.digest('hex'),basicRevision:inputs.store.revision,visible:{...snapshot.sourceIdentity.stats,bulkVisibleGroups:3}});
  assert.equal(checkSourceIdentities(f.root).sourceRecords,3);
  const main={works:[...formal,{id:'g900',basicRegistryId:'index-s-a',title:'Verified Twin Profile',firstYear:1990}],contentVersions:[],platformReleases:[]};f.put('data/games.json',main);
  const promoted=checkSourceIdentities(f.root);assert.equal(promoted.stats.formalProfiles,2);assert.equal(promoted.stats.workIdentityCount,snapshot.sourceIdentity.stats.workIdentityCount);
  f.put('data/main-adv-rpg-works-20261031.json',registry([...records(),source('new-source','New',1999)]));assert.equal(checkSourceIdentities(f.root).sourceRecords,4);
  const changed=records();changed[0].source='https://example.org/replaced-evidence';f.put('data/main-adv-rpg-works-20261031.json',registry(changed));assert.throws(()=>checkSourceIdentities(f.root),/原始来源/);
 }finally{rmSync(f.root,{recursive:true,force:true});}
});

test('a promoted profile cannot manufacture an otherwise unknown target from a forged decision',()=>{
 const bad=apply(emptyIdentityStore(),resolve,'first');for(const link of Object.values(bad.links))link.workId='unknown-work';for(const link of bad.events[0].intent.links)link.workId='unknown-work';for(const change of bad.events[0].changes)if(change.table==='links')change.after.workId='unknown-work';
 validateIdentityStore(bad);assert.throws(()=>catalogue(bad,records(),[...formal,{id:'g900',basicRegistryId:'index-s-a',title:'Twin',firstYear:1990}]),/未知作品/);
});


test('bulk admission uses canonical work IDs when a known formal profile has a different retained ID',()=>{
 const independent=apply(emptyIdentityStore(),{type:'resolve',caseId:twinCase,outcome:'distinct',links:[{sourceId:'s-a',workId:'s-a'},{sourceId:'s-b',workId:'s-b'}]},'distinct');
 const linkedRows=records().slice(0,2).map(w=>({...w,identityLink:catalogue(independent).links.get(w.id)}));
 const profile={id:'g900',identityWorkId:'s-a',basicRegistryId:'index-s-a',title:'Twin',firstYear:1990};
 const distinct=scanRegistry(registry(linkedRows),[profile]);assert.equal(distinct[0].status,'existing');assert.equal(distinct[1].status,'available');
 linkedRows[1].identityLink={workId:'s-a',status:'confirmed'};assert.equal(scanRegistry(registry(linkedRows),[profile])[1].status,'existing');
});
