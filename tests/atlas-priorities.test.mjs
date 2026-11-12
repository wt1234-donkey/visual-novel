import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,writeFileSync,readFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {buildEffectiveCatalogue,mergeFormalDatasets} from '../src/domain/catalogue/effective.mjs';
import {buildCatalogueSnapshot} from '../src/application/catalogue/snapshot.mjs';
import {DATE_CONTRACT,isRecordedYear,isPublishedYear,recordedDate} from '../src/domain/catalogue/dates.mjs';
import {applyChange,emptyStore,valuesOf,undoLast,projectEntries} from '../basic-catalogue-model.mjs';
import {buildEffectiveRelease} from '../scripts/build_effective_catalogue.mjs';
import {loadEffectiveCatalogue} from '../src/infrastructure/storage/effective-reader.mjs';
import {createBasicRepository} from '../src/infrastructure/github/basic-repository.mjs';
import {createEditClient} from '../src/infrastructure/github/contents-repository.mjs';
import {commitBasicCommand} from '../src/application/catalogue/commands.mjs';
import {gitFixture} from './helpers/catalogue-git-fixture.mjs';

const work={id:'formal',title:'Source name',chineseTitle:'原显示名',originalTitle:'Source name',firstYear:1965,group:'Source maker',gameplay:'ADV'};
const row={...work,id:'source',matchedWorkId:'identity',linkedRecordId:'formal',year:1965};
const baseInputs={main:{works:[work],contentVersions:[{id:'c',workId:'formal'}],platformReleases:[{id:'r',workId:'formal'}]},registry:{works:[{...row,id:'identity',indexId:'source',mainPlacement:'existing-complete'}]}};
const meta={id:'operation',actor:'test',at:'2026-11-11T13:00:00Z',reason:'核对当前资料'};

test('formal and basic display projections agree without changing source facts or content identities',()=>{
 const original=JSON.stringify(baseInputs),history={records:{formal:{overrides:{title:'Current formal name',writerNames:['手动姓名']}}}};
 const snapshot=buildCatalogueSnapshot({...baseInputs,history});
 assert.equal(snapshot.entries[0].title,'Current formal name');assert.equal(snapshot.formalById.get('formal').displayTitle,'Current formal name');
 assert.equal(snapshot.entries[0].sourceTitle,'Source name');assert.ok(snapshot.entries[0].aliases.includes('Source name'));
 const effective=buildEffectiveCatalogue({...baseInputs,history});
 assert.deepEqual(effective.main.contentVersions,baseInputs.main.contentVersions);assert.deepEqual(effective.main.platformReleases,baseInputs.main.platformReleases);
 assert.deepEqual(effective.main.works[0].writerNames,['手动姓名']);assert.equal(JSON.stringify(baseInputs),original);
 const store=emptyStore();store.records.identity={values:{...valuesOf(row),title:'Manual basic name'},fieldMeta:{title:{id:'manual',at:'2026-11-11T13:00:00Z'}}};
 const basic=buildCatalogueSnapshot({...baseInputs,history,store});
 assert.equal(basic.entries[0].title,'Manual basic name');assert.equal(basic.formalById.get('formal').displayTitle,'Manual basic name');
});

test('published raw inputs support consistent undo, checksum verification and browser projection',async t=>{
 const root=mkdtempSync(join(tmpdir(),'effective-release-'));t.after(()=>rmSync(root,{recursive:true,force:true}));mkdirSync(join(root,'data'));
 const files={'games.json':baseInputs.main,'basic-catalogue-edits.json':emptyStore(),'work-edit-history.json':{schemaVersion:1,records:{formal:{overrides:{title:'Corrected'}}}},'main-adv-rpg-works-20261031.json':baseInputs.registry};
 for(const [name,value] of Object.entries(files))writeFileSync(join(root,'data',name),JSON.stringify(value));
 for(const [file,value] of Object.entries({'entity-catalogue.json':{model:{entities:[]},credits:[]},'discovery-editorial.json':{works:{}},'creator-credits.json':{people:[],credits:[],collaborations:[]},'work-notes.json':{works:{}},'narrative-editorial-baseline-20261029.json':{works:{}}}))writeFileSync(join(root,'data',file),JSON.stringify(value));
 const out=join(root,'site');await buildEffectiveRelease(root,out,'a'.repeat(40));let corrupt=false;
 const fetch=async path=>{const text=readFileSync(join(out,path.replace('./','')),'utf8');return {ok:true,json:async()=>JSON.parse(text),text:async()=>text+(corrupt?' ':'')};};
 const loaded=await loadEffectiveCatalogue(fetch);assert.equal(mergeFormalDatasets(loaded).works[0].displayTitle,'Corrected');
 const undone=buildEffectiveCatalogue({...loaded.raw,history:{records:{}}});assert.equal(undone.main.works[0].displayTitle,'原显示名');
 assert.equal(loaded.sourceLease.schemaVersion,1);corrupt=true;await assert.rejects(loadEffectiveCatalogue(fetch),/摘要/);
});

test('linked name edits follow field timestamps and undo restores the formal source view',()=>{
 const history={records:{formal:{overrides:{title:'Formal edit'},recent:[{at:'2026-11-11T12:00:00Z',before:{},after:{title:'Formal edit'}}]}}};
 const initial=buildCatalogueSnapshot({...baseInputs,history});
 const store=applyChange(emptyStore(),initial.sourceRows,{type:'edit',id:'identity',values:{...valuesOf(initial.entries[0]),title:'Basic edit'}},{...meta,expectedRevision:0});
 const current=buildCatalogueSnapshot({...baseInputs,history,store});assert.equal(current.entries[0].title,'Basic edit');assert.equal(current.formalById.get('formal').displayTitle,'Basic edit');
 const later=structuredClone(history);later.records.formal.overrides.title='Later formal edit';later.records.formal.recent.push({at:'2026-11-11T14:00:00Z',before:{title:'Formal edit'},after:{title:'Later formal edit'}});
 const refreshed=buildCatalogueSnapshot({...baseInputs,history:later,store});assert.equal(refreshed.entries[0].title,'Later formal edit');assert.equal(refreshed.formalById.get('formal').displayTitle,'Later formal edit');
 const restored=undoLast(store,store.revision);assert.equal(buildCatalogueSnapshot({...baseInputs,history,store:restored}).entries[0].title,'Formal edit');
 const sourceStore=applyChange(emptyStore(),[work],{type:'edit',id:'formal',values:{...valuesOf(work),title:'Manual'}},{...meta,expectedRevision:0});
 assert.equal(projectEntries([{...work,group:'Reviewed source maker'}],sourceStore)[0].group,'Reviewed source maker');
});

test('the persisted-year contract includes early history and future unverified dates without admitting future releases',()=>{
 assert.deepEqual(DATE_CONTRACT,JSON.parse(readFileSync(new URL('../data/date-contract.json',import.meta.url))));
 for(const year of [1965,1967,1975,2050,null])assert.equal(isRecordedYear(year),true);
 for(const year of [true,'1965',1965.5,1899,2201])assert.equal(isRecordedYear(year),false);
 assert.equal(isPublishedYear(1965,2026),true);assert.equal(isPublishedYear(2050,2026),false);
 assert.deepEqual(recordedDate(2050),{year:2050,status:'unverified'});assert.throws(()=>recordedDate(2050,'published'),/日期状态/);
 const result=applyChange(emptyStore(),[work],{type:'edit',id:work.id,values:{...valuesOf(work),group:'Corrected maker'}},{...meta,expectedRevision:0});
 assert.equal(result.records.formal.values.firstYear,1965);
});

function fixture(){
 const api=gitFixture();api.changeFile('data/source.json','original');return {api,lease:api.lease(['data/source.json'])};
}
test('a changed source stops stale basic commands even when the edit snapshot SHA is unchanged',async()=>{
 const {api,lease}=fixture(),repo=createBasicRepository('test-only',api.fetch,{sourceLease:lease}),opened=await repo.read();
 api.changeFile('data/source.json','reviewed source');const posts=api.calls.filter(c=>c.method==='POST').length;
 await assert.rejects(commitBasicCommand({repository:repo,snapshot:opened,base:[work],action:{type:'edit',id:work.id,values:{...valuesOf(work),title:'New name'}},meta}),error=>error.code==='SOURCE_CHANGED');
 assert.equal(api.store.revision,0);assert.equal(api.calls.filter(c=>c.method==='POST').length,posts);
});
test('a source change racing the final ref update is detected on retry without covering the new source',async()=>{
 const {api,lease}=fixture(),repo=createBasicRepository('test-only',api.fetch,{sourceLease:lease}),opened=await repo.read();
 api.onRef(api=>api.changeFile('data/source.json','concurrent source'));
 await assert.rejects(commitBasicCommand({repository:repo,snapshot:opened,base:[work],action:{type:'edit',id:work.id,values:{...valuesOf(work),title:'New name'}},meta}),error=>error.code==='SOURCE_CHANGED');
 assert.equal(api.store.revision,0);assert.equal(api.file('data/source.json'),'concurrent source');
});
test('formal history uses the same source guard and a non-forced atomic Git commit',async()=>{
 const {api}=fixture();api.changeFile('data/work-edit-history.json',JSON.stringify({schemaVersion:1,records:{}}));const lease=api.lease(['data/source.json','data/work-edit-history.json']);
 const client=createEditClient('test-only',api.fetch,{sourceLease:lease}),opened=await client.read();
 const result=await client.write({schemaVersion:1,records:{formal:{note:'current'}}},opened.sha,'test');
 assert.ok(result.commit);assert.equal(api.calls.at(-1).method,'PATCH');assert.equal(api.calls.at(-1).body.force,false);
 assert.equal(api.calls.filter(c=>c.method==='PUT').length,0);
 const again=await client.read();await client.write({schemaVersion:1,records:{formal:{note:'second'}}},again.sha,'second');
 api.changeFile('data/source.json','new source');await assert.rejects(client.read(),error=>error.code==='SOURCE_CHANGED');
});
