import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/games.json');
const co=read('data/company-coverage.json').companies.find(c=>c.id==='sinclair');
const refs=read('data/gameplay-catalogues.json').companies.sinclair;
const rows=refs.groups.flatMap(g=>g.rows);
const page=readFileSync(new URL('../sinclair.html',import.meta.url),'utf8');
test('Sinclair reuses four existing parser identities without duplicating QL adaptations',()=>{
 assert.deepEqual(co.workIds,['g113','g135','g089','g137']);
 assert.deepEqual(co.legacyCommandWorkIds,co.workIds);
 assert.ok(co.workContexts.g089.includes('1985'));
 assert.ok(co.workContexts.g137.includes('Sinclair'));
 assert.ok(!data.works.some(w=>/^sinclair-/.test(w.id)));
 assert.ok(!data.platformReleases.some(v=>v.workId==='g089'&&v.platform==='Sinclair QL'));
});
test('Fantasy Games and Artic input narratives remain bibliography only',()=>{
 assert.equal(co.dossierOnlyWorks.length,6);
 for(const w of co.dossierOnlyWorks){
  assert.deepEqual(w.interactionModes,['文字输入']);
  assert.ok(w.interactionNote&&w.interactionSources.length);
  assert.ok(!('contentVersions' in w)&&!('platformReleases' in w));
  assert.ok(!data.works.some(x=>x.id===w.id));
 }
 for(const id of ['sinclair-perilous-swamp','sinclair-sorcerers-island']){
  const w=co.dossierOnlyWorks.find(w=>w.id===id);
  assert.ok(w.interactionSources.some(s=>s.endsWith('FantasyGames.Inside.jpg')));
  assert.ok(w.interactionNote.includes('英文'));
 }
});
test('Sinclair gameplay references cover body once and leave unknown controls and compilations outside cards',()=>{
 assert.equal(rows.length,117);
 const links=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.equal(links.length,10);
 assert.equal(new Set(links).size,10);
 assert.deepEqual(new Set(links),new Set([...co.workIds,...co.dossierOnlyWorks.map(w=>w.id)]));
 const journey=rows.find(r=>r.title==='Journey into Danger');
 assert.ok(!journey.workId&&journey.type.includes('待核'));
 for(const title of ['Fantasy Games','QL Classic Adventures','Treasure Island','Castle Spellerous'])assert.ok(!rows.find(r=>r.title===title).workId);
 assert.equal((page.match(/<article class="card"/g)||[]).length,10);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 assert.ok(page.includes('GAMEPLAY REFERENCE · 2026-10-17'));
});
