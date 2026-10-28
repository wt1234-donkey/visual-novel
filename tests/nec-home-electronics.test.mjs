import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const games=read('games.json'), company=read('company-coverage.json').companies.find(c=>c.id==='nec_he');
const model=read('entities.json'), credits=read('credits.json'), org=read('organizations.json');

test('the 1993 interactive story has one original content batch and a publisher-only company credit',()=>{
  assert.equal(games.works.filter(w=>w.id==='g1302').length,1);
  assert.deepEqual(games.works.find(w=>w.id==='g1302').interactionModes,['阅读推进','点击调查']);
  assert.deepEqual(games.contentVersions.filter(v=>v.workId==='g1302').map(v=>v.id),['g1302-c-original']);
  assert.deepEqual(games.platformReleases.filter(r=>r.workId==='g1302').map(r=>[r.id,r.publisher,r.releaseRole]),[['g1302-v1','NEC Home Electronics','contentDebut']]);
  assert.ok(credits.credits.some(c=>c.entityId==='entity-nec_he'&&c.workId==='g1302'&&c.role==='publisher'));
  assert.ok(!credits.credits.some(c=>c.entityId==='entity-nec_he'&&c.workId==='g1302'&&['developer','originalProduction'].includes(c.role)));
});

test('the existing school-trip work and its original PC-FX release are reused once',()=>{
  assert.ok(company.workIds.includes('g923'));
  assert.equal(games.works.filter(w=>w.id==='g923').length,1);
  assert.equal(games.platformReleases.filter(r=>r.id==='g923-v1'&&r.publisher==='NEC Home Electronics').length,1);
  assert.ok(company.relatedGames.some(w=>w.id==='neche-magicoal'));
  assert.ok(company.relatedGames.some(w=>w.id==='neche-miraculum'));
  assert.ok(company.relatedGames.every(w=>!games.works.some(m=>m.id===w.id)));
});

test('the NEC company, two sister businesses and HuneX joint venture retain separate identities',()=>{
  const family=org.families.find(f=>f.id==='nec_avenue');
  for(const id of ['entity-nec_he','entity-name-0b22f68e63fb','entity-name-46fe3a3fcf5f','entity-hunex','preview-human-corporation'])assert.ok(family.entityIds.includes(id));
  assert.equal(model.dossiers.find(d=>d.id==='nec_he').entityIds[0],'entity-nec_he');
  assert.equal(org.edges.filter(e=>e.child==='entity-hunex'&&e.kind==='parent'&&e.status==='previewReviewed').length,2);
  for(const id of ['nec-he-founded-1953','nec-he-renamed-1983','nec-he-hunex-joint-venture-1992','nec-he-interchannel-1995','nec-he-business-end-2000','nec-he-dissolved-2001'])assert.ok(org.organizationEvents.some(e=>e.id===id));
});
