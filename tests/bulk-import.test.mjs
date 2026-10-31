import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {scanRegistry,emptyValues,makeBasicBundle,prepareBulk,mergeMetadata} from '../bulk-import-model.mjs';
const taxonomy=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url)));
const identity=(n=1)=>({id:'basic-'+n,indexId:'basic-index-'+n,title:'Unique Bulk Story '+n,aliases:['独立测试故事'+n],firstYear:2026,source:'https://example.org/story/'+n,sourceRefs:['vndb:v'+(900000+n)],mainPlacement:'promoted-basic'});
const complete=w=>({identity:w,confirmed:true,values:{...emptyValues(w),category:'视觉小说',subcategory:'单线视觉小说',genre:'测试叙事',synopsis:'独立叙事的隔离测试资料。',characters:'主人公',modes:['阅读推进'],'interaction-note':'通过阅读推进故事。','content-evidence':'原作内容及首次发行的独立测试证据。','content-source':w.source,platforms:'Windows\nLinux',publisher:'Key','release-evidence':'此两平台属于首次发行批次。','release-source':w.source}});
test('NFKC aliases, external IDs, years and dossier identities are deduplicated',()=>{
 const w=identity();
 assert.equal(scanRegistry({works:[w]},[{id:'g900',title:'Ｕｎｉｑｕｅ Bulk Story 1',firstYear:2026}])[0].status,'existing');
 assert.equal(scanRegistry({works:[w]},[{id:'g900',title:'Other name',firstYear:2026,sourceRefs:w.sourceRefs}])[0].status,'existing');
 assert.equal(scanRegistry({works:[w]},[{id:'g900',title:w.aliases[0],firstYear:2025}])[0].status,'conflict');
 assert.equal(scanRegistry({works:[{...w,mainPlacement:'promoted-dossier'}]},[])[0].status,'conflict');
 const other={...identity(2),sourceRefs:w.sourceRefs};assert.ok(scanRegistry({works:[w,other]},[]).every(r=>r.status==='conflict'));
});
test('title/year alone cannot be submitted; ready bundles preserve provenance and one original content',()=>{
 const w=identity();assert.throws(()=>makeBasicBundle({identity:w,values:emptyValues(w),confirmed:false},'g900',taxonomy));
 const bundle=makeBasicBundle(complete(w),'g900',taxonomy);assert.deepEqual(bundle.work.titleAliases,w.aliases);assert.deepEqual(bundle.work.sourceRefs,w.sourceRefs);assert.equal(bundle.work.basicRegistryId,w.indexId);assert.equal(bundle.contentVersions.length,1);assert.equal(bundle.platformReleases.length,2);assert.equal(bundle.platformReleases[0].contentVersionId,bundle.platformReleases[1].contentVersionId);
});
test('large batches split at 30 operations and 60000 characters without ID collisions',()=>{
 const works=Array.from({length:65},(_,i)=>identity(i+1));const records=works.map(complete);const result=prepareBulk(records,scanRegistry({works},[]),[],taxonomy,'批量原作核查','2026-11-01');
 assert.deepEqual(result.errors,[]);assert.equal(result.ready,65);assert.equal(new Set(result.packages.flatMap(p=>p.operations.map(o=>o.key))).size,65);assert.ok(result.packages.every(p=>p.operations.length<=30&&JSON.stringify(p).length<=60000));
});
test('concurrent imports, stale source data and within-batch aliases are held',()=>{
 const w=identity(),r=complete(w);assert.equal(prepareBulk([r],scanRegistry({works:[w]},[{id:'g900',...w}]),[{id:'g900',...w}],taxonomy,'test','2026-11-01').errors.length,1);
 r.identity={...w,title:'Stale title'};assert.match(prepareBulk([r],scanRegistry({works:[w]},[]),[],taxonomy,'test','2026-11-01').errors[0].message,/已变化/);
});
test('metadata backfill validates atomically and preserves unrelated drafts',()=>{
 const a=identity(),b=identity(2),scan=scanRegistry({works:[a,b]},[]),before=[complete(a)];const next=mergeMetadata(before,{schemaVersion:1,records:[complete(b)]},scan);assert.equal(next.length,2);assert.equal(before.length,1);
 assert.throws(()=>mergeMetadata(before,{schemaVersion:1,records:[complete(b),complete(b)]},scan),/重复/);assert.equal(before.length,1);
 assert.throws(()=>mergeMetadata(before,{schemaVersion:1,records:[{...complete(b),identity:{...b,firstYear:2025}}]},scan),/已变化/);
});
