import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const games=read('games.json');
const company=read('company-coverage.json').companies.find(c=>c.id==='nec_avenue');
const model=read('entities.json');
const org=read('organizations.json');

test('Avenue reuses existing releases and adds only the Cal III original batch',()=>{
  assert.deepEqual(company.workIds,['g830','g959','g304','g1299']);
  assert.equal(games.works.filter(w=>w.id==='g1299').length,1);
  assert.deepEqual(games.contentVersions.filter(v=>v.workId==='g1299').map(v=>v.id),['g1299-c-original']);
  assert.deepEqual(games.platformReleases.filter(r=>r.workId==='g1299').map(r=>[r.publisher,r.releaseRole]),[['NEC Avenue','contentDebut']]);
  assert.equal(company.relatedGames.length,2);
  assert.ok(company.relatedGames.every(w=>!games.works.some(main=>main.id===w.id)));
});

test('Avenue identity, NEC Home Electronics and later Interchannel stay distinguishable',()=>{
  assert.deepEqual(model.dossiers.find(d=>d.id==='nec_avenue').entityIds,['entity-name-0b22f68e63fb']);
  const family=org.families.find(f=>f.id==='nec_avenue');
  assert.ok(family.entityIds.includes('entity-nec_he'));
  assert.ok(family.entityIds.includes('entity-name-46fe3a3fcf5f'));
  assert.ok(org.organizationEvents.some(e=>e.id==='nec-avenue-founded-1987'));
  assert.ok(org.nameHistory.some(h=>h.id==='nec-interchannel-name-2004'));
});
