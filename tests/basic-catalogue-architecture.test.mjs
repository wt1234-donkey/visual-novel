import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {emptyStore,applyChange,valuesOf} from '../basic-catalogue-model.mjs';
import {buildCatalogueSnapshot} from '../src/application/catalogue/snapshot.mjs';
import {createCatalogueView} from '../src/application/catalogue/view.mjs';
import {createCatalogueQuery,queryCatalogueRows} from '../src/application/catalogue/query.mjs';
import {buildIdentityMap} from '../src/domain/catalogue/identity.mjs';

const first={id:'work-a',indexId:'source-a',title:'Shared name',firstYear:1990,group:'Studio A',gameplay:'ADV',mainPlacement:'promoted-basic'};
const second={...first,id:'work-b',indexId:'source-b',group:'Studio B'};
const registry={works:[first,second],identityReview:[],summary:{accepted:2}};
const inputs={registry,initial:[{id:'source-a',title:first.title,year:1990,group:first.group,gameplay:'ADV'}],batches:[]};
const meta=store=>({id:'op-'+store.revision,at:'2026-11-11T08:00:00Z',actor:'test',reason:'核对作品信息',expectedRevision:store.revision});

test('snapshot preserves homonyms, explicit source mappings and input bytes',()=>{
 const original=JSON.stringify(inputs),snapshot=buildCatalogueSnapshot(inputs);
 assert.equal(snapshot.entries.length,2);
 assert.equal(snapshot.home.rows.length,2);
 assert.equal(snapshot.identities.sourceToWork.get('source-a'),'work-a');
 assert.equal(snapshot.identities.sourceToWork.get('source-b'),'work-b');
 assert.deepEqual(snapshot.identityCandidates[0].ids,['work-a','work-b']);
 assert.equal(JSON.stringify(inputs),original);
 assert.throws(()=>buildIdentityMap([{id:'source',matchedWorkId:'a'},{id:'source',matchedWorkId:'b'}]),/映射冲突/);
});

test('same-name source batch records retain distinct registry identities',()=>{
 const snapshot=buildCatalogueSnapshot({registry:{works:[],identityReview:[]},batches:[['batch',[
  {title:'Same',year:2000,registryId:'a',group:'A',gameplay:'ADV'},
  {title:'Same',year:2000,registryId:'b',group:'B',gameplay:'ADV'}
 ]]]});
 assert.deepEqual(snapshot.entries.map(row=>row._key),['a','b']);
 assert.equal(new Set(snapshot.sourceRows.map(row=>row.id)).size,2);
});

test('manual edits and merged versions use the same snapshot and query projection',()=>{
 const initial=buildCatalogueSnapshot(inputs);
 let store=emptyStore();
 store=applyChange(store,initial.sourceRows,{type:'edit',id:'work-a',values:{...valuesOf(first),title:'Revised',firstYear:1980}},meta(store));
 store=applyChange(store,initial.sourceRows,{type:'merge',mainId:'work-a',ids:['work-b'],relation:{type:'unverified',label:'待核版本'}},meta(store));
 const snapshot=buildCatalogueSnapshot({...inputs,store});
 const query=createCatalogueQuery(initial.sourceRows,store);
 assert.equal(snapshot.entries.length,1);
 assert.equal(snapshot.home.rows.length,1);
 assert.equal(snapshot.home.rows[0].title,'Revised');
 assert.equal(snapshot.home.rows[0].firstYear,1980);
 assert.ok(snapshot.home.rows[0].aliases.includes(second.title));
 assert.deepEqual(query.entries,snapshot.entries);
 assert.deepEqual(queryCatalogueRows(query.filterRows,{q:'studio b',year:'1990'}),[0]);
 assert.equal(query.childrenByMain.get('work-a')[0]._key,'work-b');
 assert.equal(query.byId.size,2);
 assert.equal(store.records['work-b'].relation.type,'unverified');
});

test('formal linkage excludes only explicit identities from the homepage',()=>{
 const snapshot=buildCatalogueSnapshot({...inputs,main:{works:[{id:'formal-a',title:'Shared name',firstYear:1990}]}});
 assert.equal(snapshot.home.rows.length,2);
 const linked=structuredClone(inputs);linked.registry.works[0].linkedRecordId='formal-a';
 const resolved=buildCatalogueSnapshot({...linked,main:{works:[{id:'formal-a',title:'Formal'}]}});
 assert.deepEqual(resolved.home.rows.map(row=>row._key),['work-b']);
 assert.equal(resolved.formalIdByWorkId.get('work-a'),'formal-a');
});

test('invalid parents are visible in tolerant views and block strict publication',()=>{
 const store=emptyStore();
 store.records['work-b']={parentId:'missing',relation:{type:'unverified',label:'待核'}};
 const source=buildCatalogueSnapshot(inputs).sourceRows;
 const view=createCatalogueView(source,store);
 assert.equal(view.entries.length,2);
 assert.equal(view.issues[0].type,'invalid-parent');
 assert.throws(()=>buildCatalogueSnapshot({...inputs,store}),/关系校验失败/);
 const missing=emptyStore();missing.records['unknown']={deleted:true};
 assert.throws(()=>createCatalogueView(source,missing,{strict:true}),/missing-identity/);
});

test('domain modules have no application, persistence or browser dependencies',()=>{
 const root=resolve(fileURLToPath(new URL('../src/domain/',import.meta.url)));
 function inspect(dir){for(const item of readdirSync(dir,{withFileTypes:true})){
  const file=resolve(dir,item.name);if(item.isDirectory()){inspect(file);continue;}
  if(!item.name.endsWith('.mjs'))continue;
  const source=readFileSync(file,'utf8');
  for(const [,specifier] of source.matchAll(/(?:from\s*|import\s*)['"]([^'"]+)['"]/g))assert.ok(resolve(dirname(file),specifier).startsWith(root+'/'),file+' -> '+specifier);
  assert.doesNotMatch(source,/\b(?:document|window|localStorage)\s*[.[]|\bfetch\s*\(|node:|api\.github\.com/);
 }}inspect(root);
});
