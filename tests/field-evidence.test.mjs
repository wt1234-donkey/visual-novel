import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtempSync,mkdirSync,readFileSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,dirname} from 'node:path';
import {spawnSync} from 'node:child_process';
import {emptyFieldStore,applyFieldCommand,validateFieldStore,fieldProjection,fieldKey,fieldHistory,chosenFields,evidenceCsv,fieldCounts,scopeKey} from '../src/domain/catalogue/field-evidence.mjs';
import {buildEffectiveCatalogue,displayTitle} from '../src/domain/catalogue/effective.mjs';
import {buildSourceIdentityCatalogue} from '../src/domain/catalogue/source-identities.mjs';
import {createFieldContext} from '../src/infrastructure/filesystem/field-evidence.mjs';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {emptyStore,valuesOf} from '../basic-catalogue-model.mjs';
import {buildCatalogueSnapshot} from '../src/application/catalogue/snapshot.mjs';
import {createCatalogueView} from '../src/application/catalogue/view.mjs';
import {planCommand} from '../src/application/commands/execute.mjs';
import {executeCommand,receiptPath} from '../src/infrastructure/filesystem/command-executor.mjs';
import {sourceLeaseSync,loadEffectiveInputsSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {createCommandSession} from '../src/application/commands/session.mjs';
import {createFieldEvidenceReader} from '../src/infrastructure/storage/field-evidence-reader.mjs';
import {buildFieldEvidenceDirectory,verifyFieldReceipts} from '../scripts/build_field_evidence.mjs';
import {gitBlobHash} from '../src/infrastructure/filesystem/basic-store.mjs';
const work={id:'g001',title:'Original',firstYear:1990,interactionModes:['选项分支']},content={id:'c1',workId:'g001',label:'Original content',firstYear:1990,basis:'original',source:'https://example.org/content',evidence:'Original content evidence',addedContent:[]},release={id:'r1',workId:'g001',year:1990,publisher:'Same Studio',platform:'PC',contentVersionId:'c1'},row={id:'g001',indexId:'index-1',title:'Original',firstYear:1990,group:'Same Studio',gameplay:'ADV',source:'https://example.org/source',mainPlacement:'existing-complete',linkedRecordId:'g001'};
const main={works:[work],contentVersions:[content],platformReleases:[release]},registry={works:[row],identityReview:[],summary:{accepted:1}};
const people=[{id:'p1',name:'Same Name'},{id:'p2',name:'Same Name'}],entities=[{id:'e1',name:'Same Studio',type:'company'},{id:'e2',name:'Same Studio',type:'brand'}];
const context=createFieldContext({identity:buildSourceIdentityCatalogue({registry,formalWorks:[work]}),main,entities,people});
const scope={type:'work',workId:'g001',id:'g001'};
const meta=(id,revision)=>({id,at:'2026-11-13T05:00:00Z',actor:'tester',reason:'核对多项来源和选用范围',sources:['https://example.org/evidence'],expectedRevision:revision});
const assertion=(id,value=1991,extra={})=>({id,scope,field:'firstYear',value,sources:['https://example.org/'+id],sourceIds:['g001'],status:'supported',subjects:[],...extra});
const apply=(s,action,id,ctx=context)=>applyFieldCommand(s,ctx,action,meta(id,s.revision));
function seeded(){let s=apply(emptyFieldStore(),{type:'assert',assertion:assertion('old',1990)},'add-old');return apply(s,{type:'assert',assertion:assertion('new',1991)},'add-new');}
function selected(){return apply(seeded(),{type:'select',assertionId:'old'},'select-old');}

test('optional empty evidence leaves complete formal/basic projections and visible counts unchanged',()=>{
 const before=buildEffectiveCatalogue({main}),after=buildEffectiveCatalogue({main,fieldEvidence:fieldProjection(emptyFieldStore())});assert.deepEqual(after,before);
 const inputs={registry,main,store:emptyStore()};assert.deepEqual(buildCatalogueSnapshot({...inputs,fieldEvidence:fieldProjection(emptyFieldStore())}),buildCatalogueSnapshot(inputs));
});
test('multiple sources coexist and later collection never silently replaces an explicit earlier choice',()=>{
 const s=selected(),raw=structuredClone(main);assert.equal(fieldCounts(s).assertions,2);assert.equal(fieldCounts(s).conflicts,1);
 const plan=fieldProjection(s),effective=buildEffectiveCatalogue({main,fieldEvidence:plan});assert.equal(effective.main.works[0].firstYear,1990);assert.equal(chosenFields(plan,'work','g001').firstYear.selection.reason,meta('x',0).reason);assert.deepEqual(main,raw);
 const next=apply(s,{type:'assert',assertion:assertion('later',2000)},'add-later');assert.equal(chosenFields(fieldProjection(next),'work','g001').firstYear.value,1990);assert.equal(Object.keys(next.assertions).length,3);
});
test('work, content and release values are isolated by stable IDs and one shared projection feeds CSV',()=>{
 let s=seeded();for(const a of [assertion('name','Selected Name',{field:'title'}),assertion('content-year',1992,{scope:{type:'content',workId:'g001',id:'c1'}}),assertion('publisher','Other publisher',{field:'publisher',scope:{type:'release',workId:'g001',id:'r1'},subjects:[{kind:'entity',id:'e2',signature:'Other publisher'}]})]){s=apply(s,{type:'assert',assertion:a},'add-'+a.id);s=apply(s,{type:'select',assertionId:a.id},'select-'+a.id);}
 const before=structuredClone(main),e=buildEffectiveCatalogue({main,fieldEvidence:fieldProjection(s)}).main;
 assert.equal(displayTitle(e.works[0]),'Selected Name');assert.equal(e.works[0].firstYear,1990);assert.equal(e.contentVersions[0].firstYear,1992);assert.equal(e.platformReleases[0].year,1990);assert.equal(e.platformReleases[0].publisher,'Other publisher');assert.deepEqual(main,before);
 const py=spawnSync('python3',['-c',"import sys,json;sys.path.insert(0,'scripts');from export_content_csv import content_rows;rows=list(content_rows(json.load(sys.stdin)));print(json.dumps(rows))"],{input:JSON.stringify(e),encoding:'utf8'});assert.equal(py.status,0,py.stderr);const csv=JSON.parse(py.stdout);assert.equal(csv[0]['作品名称'],'Selected Name');assert.equal(csv[0]['内容首次年份'],1992);
 const wrong=assertion('bad',2000,{scope:{type:'release',workId:'g-other',id:'r1'},field:'year'});assert.throws(()=>apply(s,{type:'assert',assertion:wrong},'bad'),/不属于/);
});
test('same-named companies, brands and people stay distinct and only explicit IDs attach a subject',()=>{
 let s=apply(emptyFieldStore(),{type:'assert',assertion:assertion('maker','Same Studio',{field:'group',subjects:[{kind:'entity',id:'e1',signature:'Same Studio'}]})},'add-maker');s=apply(s,{type:'assert',assertion:assertion('brand','Same Studio',{field:'group',subjects:[{kind:'entity',id:'e2',signature:'Same Studio'}]})},'add-brand');
 assert.equal(s.assertions.maker.subjects[0].id,'e1');assert.equal(s.assertions.brand.subjects[0].id,'e2');assert.equal(context.subjects.entity.size,2);assert.equal(context.subjects.person.size,2);assert.equal(fieldCounts(s).selections,0);
 assert.throws(()=>apply(s,{type:'assert',assertion:assertion('unknown-subject','X',{field:'group',subjects:[{kind:'entity',id:'Same Studio',signature:'X'}]})},'bad'),/主体ID不存在/);
});
test('source-free creator names remain manual, need no evidence and never infer a same-name person ID',()=>{
 const a=assertion('manual',['Same Name'],{field:'writerNames',sources:[],sourceIds:[],status:'manual'});const s=apply(emptyFieldStore(),{type:'assert',assertion:a},'manual');assert.deepEqual(s.assertions.manual.subjects,[]);assert.equal(s.assertions.manual.status,'manual');
 assert.throws(()=>apply(emptyFieldStore(),{type:'assert',assertion:{...a,status:'supported'}},'unsupported'),/手动添加/);
 const real=JSON.parse(readFileSync(new URL('../data/games.json',import.meta.url))).works.find(w=>w.id==='g039'),taxonomy=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url)));
 const cmd={schemaVersion:1,kind:'formal',operationId:'manual-existing',actor:'tester',at:meta('x',0).at,reason:'添加剧作姓名保留无来源权限',sources:[],expectedRevision:0,sourceLease:{schemaVersion:1,files:{'data/source.json':'a'.repeat(40)}},action:{type:'creators',workId:real.id,names:{writerNames:['Manual Writer'],artistNames:[],musicianNames:[]}}};
 const r=planCommand(cmd,{sourceLease:cmd.sourceLease,formalStore:{schemaVersion:1,records:{}},formalWorks:[real],reservedWorks:[real],taxonomy},'tester');assert.deepEqual(r.store.records[real.id].overrides.writerNames,['Manual Writer']);
});
test('undo is an independent event, preserves later unrelated additions and retains complete history beyond three edits',()=>{
 let s=selected();for(let i=0;i<9;i++)s=apply(s,{type:'assert',assertion:assertion('extra-'+i,1990+i)},'extra-'+i);
 const n=s.events.length;s=apply(s,{type:'undo',targetId:'select-old'},'undo');assert.equal(s.events.length,n+1);assert.equal(Object.keys(s.assertions).length,11);assert.equal(Object.keys(s.choices).length,0);assert.equal(s.events.at(-1).undoOf,'select-old');
 assert.equal(fieldHistory(s,{workId:'g001'}).events.length,13);validateFieldStore(s);
});
test('later reaffirmation or changed selection prevents an old undo from replacing the latest conclusion',()=>{
 let s=selected();s=apply(s,{type:'select',assertionId:'old'},'reaffirm');assert.throws(()=>apply(s,{type:'undo',targetId:'select-old'},'old-undo'),/后续/);
 s=apply(s,{type:'clear',scope,field:'firstYear'},'clear');assert.equal(Object.keys(s.choices).length,0);s=apply(s,{type:'undo',targetId:'clear'},'undo-clear');assert.equal(s.choices[fieldKey(scope,'firstYear')].operationId,'reaffirm');
});
test('removing an assertion cannot leave a dangling selected value and unsupported disputed values cannot be selected',()=>{
 const s=selected();assert.throws(()=>apply(s,{type:'undo',targetId:'add-old'},'remove-selected'),/不存在/);
 const disputed=apply(emptyFieldStore(),{type:'assert',assertion:assertion('dispute',1990,{status:'disputed'})},'add');assert.throws(()=>apply(disputed,{type:'select',assertionId:'dispute'},'select'),/争议/);
});
test('replay rejects modified before-values, current values, reasons, undo targets and duplicate operation IDs',()=>{
 const good=apply(selected(),{type:'undo',targetId:'select-old'},'undo');
 for(const mutate of [s=>s.events[0].changes[0].before={},s=>s.assertions.old.value=1980,s=>s.events[2].changes[0].after.reason='篡改了选用理由',s=>s.events.at(-1).undoOf='add-old',s=>s.events.at(-1).id=s.events[0].id]){const s=structuredClone(good);mutate(s);assert.throws(()=>validateFieldStore(s));}
 assert.throws(()=>apply(seeded(),{type:'assert',assertion:assertion('old',2000)},'overwrite'),/不能覆盖/);
});
test('unknown sources, unsafe scopes, stale revisions and future shipped-release years are refused',()=>{
 for(const a of [assertion('missing',1990,{sourceIds:['unknown']}),assertion('unsafe','x',{scope:{type:'constructor',workId:'g001',id:'g001'},field:'name'}),assertion('future',2200,{scope:{type:'release',workId:'g001',id:'r1'},field:'year'})])assert.throws(()=>apply(emptyFieldStore(),{type:'assert',assertion:a},'bad'));
 assert.throws(()=>applyFieldCommand(seeded(),context,{type:'select',assertionId:'old'},meta('stale',0)),/修订/);
});
function fixture(){const root=mkdtempSync(join(tmpdir(),'field-evidence-'));const put=(path,value)=>{mkdirSync(dirname(join(root,path)),{recursive:true});writeFileSync(join(root,path),JSON.stringify(value));};
 for(const [name,value] of Object.entries({'main-adv-rpg-works-20261031.json':registry,'games.json':main,'non-rpg-creator-supplement-20261030.json':{works:[]},'work-edit-history.json':{schemaVersion:1,records:{}},'basic-catalogue-edits.json':emptyStore(),'company-coverage.json':{companies:[]},'entities.json':{entities},'creator-credits.json':{people},'field-evidence.json':emptyFieldStore(),'taxonomy.json':{}}))put('data/'+name,value);
 for(const n of ['adv-rpg-minimal-index-20261031','adv-rpg-next-studio-review-20261031','adv-rpg-round3-review-20261031'])put('data/'+n+'.json',{records:[]});return {root,put};}
function cmd(root,action,id,revision){return {schemaVersion:1,kind:'field',operationId:id,actor:'tester',at:meta(id,revision).at,reason:meta(id,revision).reason,sources:meta(id,revision).sources,expectedRevision:revision,sourceLease:sourceLeaseSync(root),action};}
test('trusted filesystem writes journal and receipt together; original retry after later edits does not rewrite them',()=>{
 const f=fixture();try{const original=readFileSync(join(f.root,'data/main-adv-rpg-works-20261031.json'),'utf8'),first=cmd(f.root,{type:'assert',assertion:assertion('a')},'first',0);const r=executeCommand(f.root,first,'tester');assert.deepEqual(r.paths,['data/field-evidence.json',receiptPath('first')]);
 executeCommand(f.root,cmd(f.root,{type:'assert',assertion:assertion('b',1992)},'later',1),'tester');const later=readFileSync(join(f.root,'data/field-evidence.json'),'utf8');assert.equal(executeCommand(f.root,first,'tester').alreadyApplied,true);assert.equal(readFileSync(join(f.root,'data/field-evidence.json'),'utf8'),later);assert.equal(readFileSync(join(f.root,'data/main-adv-rpg-works-20261031.json'),'utf8'),original);assert.equal(verifyFieldReceipts(f.root,loadCatalogueSnapshot(f.root).snapshot.fieldCatalogue.store),2);assert.throws(()=>verifyFieldReceipts(f.root,emptyFieldStore()),/回执与审计/);
 }finally{rmSync(f.root,{recursive:true,force:true});}
});
test('basic unrelated edits do not copy a pinned value into legacy corrections, and clearing selection restores their original value',()=>{
 const f=fixture();try{const picked=apply(seeded(),{type:'select',assertionId:'new'},'pick');f.put('data/field-evidence.json',picked);let {snapshot,inputs}=loadCatalogueSnapshot(f.root);assert.equal(snapshot.entries[0].year,1991);
 const values={...valuesOf(snapshot.entries[0]),gameplay:'Narrative RPG'},command={...cmd(f.root,{},'ordinary',inputs.store.revision),kind:'basic',action:{type:'edit',id:'g001',values}};
 executeCommand(f.root,command,'tester');({snapshot,inputs}=loadCatalogueSnapshot(f.root));assert.equal(inputs.store.records.g001.values.firstYear,1990);assert.equal(snapshot.entries[0].year,1991);assert.equal(snapshot.entries[0].gameplay,'Narrative RPG');
 assert.throws(()=>executeCommand(f.root,{...command,operationId:'wrong',sourceLease:sourceLeaseSync(f.root),expectedRevision:inputs.store.revision,action:{...command.action,values:{...values,firstYear:1980}}},'tester'),/显式选用/);
 executeCommand(f.root,cmd(f.root,{type:'clear',scope,field:'firstYear'},'clear',picked.revision),'tester');assert.equal(loadCatalogueSnapshot(f.root).snapshot.entries[0].year,1990);
 }finally{rmSync(f.root,{recursive:true,force:true});}
});
test('browser basic view and the build-time/formal projection use the same selected fields',()=>{
 const s=apply(seeded(),{type:'select',assertionId:'new'},'pick'),plan=fieldProjection(s),snap=buildCatalogueSnapshot({registry,main,fieldEvidence:plan});const view=createCatalogueView(snap.sourceRows,emptyStore());assert.equal(view.entries[0].year,1991);assert.equal(snap.formalById.get('g001').firstYear,1991);assert.equal(view.entries[0].fieldEvidence.firstYear.id,'new');
 const csv=evidenceCsv(s);assert.ok(csv.includes('old'));assert.ok(csv.includes('new'));assert.ok(csv.includes('"是"'));assert.ok(csv.includes(meta('x',0).reason));
});
test('field page reads one hashed target bucket and never loads original source shards',async()=>{
 const f=fixture();try{const loaded=loadCatalogueSnapshot(f.root),files=new Map(),revision='a'.repeat(40);const save=async(name,value)=>{const text=JSON.stringify(value),path=`catalogue-web/${revision}/${name}.json`;files.set('data/'+path,text);return {path,sha:gitBlobHash(text)};};const ref=await buildFieldEvidenceDirectory('',revision,loaded,buildEffectiveCatalogue({main}),save);
 const state=JSON.stringify(emptyFieldStore()),resource='catalogue-web/'+revision+'/store.json';files.set('data/'+resource,state);const release={schemaVersion:1,revision,catalogues:{fieldEvidence:ref},resources:{'data/field-evidence.json':{path:resource,sha:gitBlobHash(state)}}};let rawReads=0;const calls=[];
 const fetcher=async url=>{const path=String(url).replace(/^\.\//,'');calls.push(path);if(path.includes('basic-registry'))rawReads++;return new Response(path==='data/catalogue-release.json'?JSON.stringify(release):files.get(path));};const reader=createFieldEvidenceReader(fetcher);await reader.info();await reader.store();assert.equal(calls.filter(p=>p.includes('field-targets')).length,0);const result=await reader.targets('g001');assert.equal(result.targets.length,3);assert.equal(calls.filter(p=>p.includes('field-targets')).length,1);assert.equal(rawReads,0);
 }finally{rmSync(f.root,{recursive:true,force:true});}
});
test('ambiguous save results retain the immutable field command across reloads',async()=>{
 const map=new Map(),storage={getItem:k=>map.get(k)||null,setItem:(k,v)=>map.set(k,v),removeItem:k=>map.delete(k)},command={schemaVersion:1,kind:'field',operationId:'same-id',actor:'tester',at:meta('x',0).at,reason:meta('x',0).reason,sources:[],expectedRevision:0,sourceLease:{schemaVersion:1,files:{'data/source.json':'a'.repeat(40)}},action:{type:'assert',assertion:assertion('candidate')}};
 await assert.rejects(()=>createCommandSession({kind:'field',storage}).execute(command,async()=>{throw Error('lost response');}));const recovered=createCommandSession({kind:'field',storage});const r=await recovered.execute({...command,operationId:'replacement'},async original=>original);assert.equal(r.operationId,'same-id');assert.equal(map.size,0);
});


test('an undone assertion ID cannot be reused for a different claim or invalidate an older admission reference',()=>{
 let s=apply(emptyFieldStore(),{type:'assert',assertion:assertion('permanent-id',1990)},'first');s=apply(s,{type:'undo',targetId:'first'},'undo-first');assert.throws(()=>apply(s,{type:'assert',assertion:assertion('permanent-id',1992)},'reuse'),/不能覆盖/);
});

test('clearing a work-level maker or manual-name choice retains the underlying basic maker and empty name list in the target directory',async()=>{
 const f=fixture();try{let s=apply(emptyFieldStore(),{type:'assert',assertion:assertion('maker-pin','Selected Maker',{field:'group'})},'add-maker');s=apply(s,{type:'select',assertionId:'maker-pin'},'pick-maker');s=apply(s,{type:'assert',assertion:assertion('writer-pin',['Manual Writer'],{field:'writerNames',sources:[],sourceIds:[],status:'manual'})},'add-writer');s=apply(s,{type:'select',assertionId:'writer-pin'},'pick-writer');f.put('data/field-evidence.json',s);
 const loaded=loadCatalogueSnapshot(f.root),effective=buildEffectiveCatalogue(loadEffectiveInputsSync(f.root)),parts=new Map(),save=async(name,value)=>{parts.set(name,value);return {path:'catalogue-web/'+('a'.repeat(40))+'/'+name+'.json',sha:'a'.repeat(40)};};await buildFieldEvidenceDirectory('','a'.repeat(40),loaded,effective,save);const targets=[...parts].find(([name,value])=>name.startsWith('field-targets-')&&value.g001)[1].g001,base=targets.find(t=>t.scope.type==='work');assert.equal(base.values.group,'Same Studio');assert.deepEqual(base.values.writerNames,[]);
 }finally{rmSync(f.root,{recursive:true,force:true});}
});
