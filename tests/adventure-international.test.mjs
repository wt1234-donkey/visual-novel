import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/games.json');
const co=read('data/company-coverage.json').companies.find(c=>c.id==='adventure_international');
const page=readFileSync(new URL('../adventure_international.html',import.meta.url),'utf8');

test('Adventure International narrative groups cover main references and dossier-only books once',()=>{
  const ids=[...co.workIds,...co.dossierOnlyWorks.map(w=>w.id)];
  const grouped=co.dossierGroups.flatMap(g=>g.workIds);
  assert.equal(ids.length,40);
  assert.equal(new Set(grouped).size,grouped.length);
  assert.deepEqual(new Set(grouped),new Set(ids));
  assert.equal((page.match(/<article class="card"/g)||[]).length,40);
  for(const id of ids)assert.equal(page.split(`<article class="card" id="${id}">`).length,2);
});

test('parser books stay out of the database and do not manufacture release/content identities',()=>{
  for(const w of co.dossierOnlyWorks){
    assert.ok(w.interactionModes.includes('文字输入'));
    assert.ok(!data.works.some(x=>x.id===w.id));
    assert.ok(!data.contentVersions.some(x=>x.workId===w.id));
    assert.ok(!data.platformReleases.some(x=>x.workId===w.id));
    const card=page.split(`<article class="card" id="${w.id}">`)[1].split('</article>')[0];
    assert.ok(card.includes('仅专题收录'));
    assert.ok(!card.includes('class="version-panel"'));
  }
  const matches=filterCatalogue(data,{query:'Nightwalker',company:'Adventure International'});
  assert.deepEqual(matches.map(x=>x.work.id),['g1080']);
  assert.ok(matches[0].work.interactionModes.includes('菜单指令'));
  assert.ok(matches[0].work.interactionModes.includes('选项分支'));
  assert.ok(matches[0].work.interactionModes.includes('直接移动'));
  assert.equal(filterCatalogue(data,{query:'Nightwalker',interaction:'文字输入'}).length,0);
  assert.equal(filterCatalogue(data,{query:'夜行者',interaction:'菜单指令'}).length,1);
});

test('UK originals carry UK labels without copying parser works or altering existing publisher credits',()=>{
  const uk=co.dossierGroups.find(g=>g.id==='ai-uk');
  assert.equal(uk.workIds.length,4);
  for(const id of uk.workIds){
    const card=page.split(`<article class="card" id="${id}">`)[1].split('</article>')[0];
    assert.ok(card.includes(' · UK</span>'));
  }
  const supergran=co.dossierOnlyWorks.find(w=>w.originalTitle==='Super Gran: The Adventure');
  assert.ok(supergran.notes.includes('实际发行方Tynesoft'));
  assert.equal(data.platformReleases.find(r=>r.workId==='g138').publisher,'Adventure International');
});

test('Classic Adventure reuses Colossal Cave and excluded games never become dossier cards',()=>{
  assert.ok(co.workIds.includes('g089'));
  assert.ok(co.workContexts.g089.includes('Classic Adventure'));
  assert.ok(!co.dossierOnlyWorks.some(w=>w.originalTitle==='Classic Adventure'));
  assert.equal(data.works.find(w=>w.id==='g089').firstYear,1976);
  const names=co.dossierOnlyWorks.map(w=>w.originalTitle).join('\n');
  assert.ok(!/Kid.?Venture|Little Red Riding Hood|Old McDonald|Treasure Quest|Balrog|Sisyphus|Morton|Reign of the Red Dragon|Rebel Planet|Kayleth/.test(names));
  assert.equal(co.relatedGames.length,0);
});
