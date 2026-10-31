import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {searchWorks,packageChanges,validatePackage,restoreHistorical,same,validURL} from '../management-model.mjs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n+'.json',import.meta.url),'utf8'));
const data={games:read('games'),editorial:read('discovery-editorial'),creators:read('creator-credits'),notes:read('work-notes')};
test('Chinese, original title and IDs match existing identities',()=>{
 for(const q of ['白色相簿2','WHITE ALBUM 2','g039'])assert.ok(searchWorks(data.games.works,q,data.editorial).some(w=>w.id==='g039'));
});
test('unchanged dataset produces no edits; key ordering does not cause conflicts',()=>{
 assert.equal(packageChanges(data,structuredClone(data),'整理','2026-10-31').operations.length,0);
 assert.ok(same({a:1,b:2},{b:2,a:1}));
});
test('one changed record has exact before and after values, and round trips through history',()=>{
 const changed=structuredClone(data);changed.editorial.works.g089.basis+=' 测试补充说明。';
 const p=packageChanges(data,changed,'来源限定补充','2026-10-31');
 assert.equal(p.operations.length,1);assert.equal(p.operations[0].key,'g089');
 assert.deepEqual(validatePackage(p),[]);
 assert.deepEqual(restoreHistorical(changed,{batches:[p]}),data);
});
test('invalid sources and missing evidence block submission',()=>{
 const changed=structuredClone(data);changed.editorial.works.g089.fieldEvidence.style.sources=['javascript:alert(1)'];
 assert.ok(validatePackage(packageChanges(data,changed,'核查','2026-10-31')).length);
 assert.ok(!validURL('data:text/html,bad'));
});
