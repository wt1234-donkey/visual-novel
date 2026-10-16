import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/games.json');
const co=read('data/company-coverage.json').companies.find(c=>c.id==='psk');
const page=readFileSync(new URL('../psk.html',import.meta.url),'utf8');

test('PSK menu narratives are searchable and parser bibliography stays outside main data',()=>{
  assert.equal(co.workIds.length,3);
  for(const id of co.workIds){
    const w=data.works.find(w=>w.id===id);
    assert.ok(w.interactionModes.includes('菜单指令'));
    assert.ok(!w.interactionModes.includes('文字输入'));
    assert.deepEqual(filterCatalogue(data,{query:w.originalTitle,interaction:'菜单指令'}).map(r=>r.work.id),[id]);
    assert.equal(filterCatalogue(data,{query:w.originalTitle,interaction:'文字输入'}).length,0);
    assert.equal(data.contentVersions.filter(c=>c.workId===id).length,1);
    const releases=data.platformReleases.filter(r=>r.workId===id);
    assert.equal(releases.length,1);
    assert.equal(releases[0].releaseRole,'contentDebut');
  }
  assert.equal(co.dossierOnlyWorks.length,4);
  for(const w of co.dossierOnlyWorks){
    assert.ok(w.interactionModes.includes('文字输入'));
    assert.ok(!data.works.some(x=>x.id===w.id));
    assert.ok(!data.contentVersions.some(x=>x.workId===w.id));
    assert.ok(!data.platformReleases.some(x=>x.workId===w.id));
    assert.ok(!('contentVersions' in w) && !('platformReleases' in w));
  }
});

test('PSK ALICE identity, historical competition, automated combat and unreleased plans remain distinct',()=>{
  const alice=co.dossierOnlyWorks.find(w=>w.id==='psk-alice');
  assert.equal(alice.firstYear,1984);
  assert.notEqual(alice.originalTitle,data.works.find(w=>w.id==='g133').originalTitle);
  assert.ok(!co.workIds.includes('g133') && !co.workIds.includes('g005'));
  assert.ok(data.platformReleases.some(r=>r.workId==='g005' && r.publisher==='PSK'));
  const rpg=co.relatedGames[0];
  assert.equal(rpg.firstYear,1985);
  assert.ok(!rpg.interactionModes.includes('战斗指令'));
  assert.ok(rpg.interactionNote.includes('自动'));
  assert.ok(!data.works.some(w=>w.id===rpg.id));
  assert.equal(co.entries.filter(e=>e.status.startsWith('排除') && !e.title.includes('Super')).length,5);
  const unreleased=co.entries.find(e=>e.title.includes('探険隊2'));
  assert.deepEqual(unreleased.workIds,[]);
  assert.ok(!unreleased.dossierIds?.length && !unreleased.relatedIds?.length);
  assert.ok(co.workContexts['psk-yellow-lemon'].includes('边界'));
});

test('PSK original 13-game list is an appendix and its eight cards are disjoint',()=>{
  const ids=[...co.workIds,...co.dossierOnlyWorks.map(w=>w.id),...co.relatedGames.map(w=>w.id)];
  const groups=co.dossierGroups.flatMap(g=>g.workIds);
  assert.equal(ids.length,8);
  assert.equal(new Set(groups).size,8);
  assert.deepEqual(new Set(groups),new Set(ids));
  assert.equal((page.match(/<article class="card"/g)||[]).length,8);
  const a=read('data/gameplay-catalogues.json').companies.psk;
  assert.equal(a.groups.flatMap(g=>g.rows).length,13);
  assert.equal(a.groups.flatMap(g=>g.rows).filter(r=>!r.workId).length,5);
  assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
  assert.ok(!page.includes('<article class="card" id="g005"'));
});
