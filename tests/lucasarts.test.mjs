import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const games=read('games.json');
const company=read('company-coverage.json').companies.find(c=>c.id==='lucasarts');
const model=read('entities.json');
const org=read('organizations.json');

test('LucasArts dossier shares old works and gives each new original one debut',()=>{
  assert.equal(company.workIds.length,14);
  assert.deepEqual(company.workIds.slice(-3),['g975','g976','g977']);
  for(let n=1288;n<=1298;n++){
    const id=`g${n}`;
    assert.equal(games.works.filter(w=>w.id===id).length,1);
    assert.deepEqual(games.contentVersions.filter(v=>v.workId===id).map(v=>v.id),[`${id}-c-original`]);
    assert.deepEqual(games.platformReleases.filter(r=>r.workId===id).map(r=>r.releaseRole),['contentDebut']);
  }
});

test('historical team, company and current brand remain separate identities',()=>{
  assert.equal(model.dossiers.find(d=>d.id==='lucasarts').entityIds[0],'entity-name-57509c825879');
  assert.equal(model.entities.find(e=>e.id==='entity-lucasfilm_games_legacy').type,'team');
  const family=org.families.find(f=>f.id==='lucasarts');
  assert.ok(family.entityIds.includes('preview-lucasfilm-games-2021'));
  assert.ok(family.entityIds.includes('entity-name-57509c825879'));
  assert.ok(org.organizationEvents.some(e=>e.id==='lucasarts-1982-team'));
});
