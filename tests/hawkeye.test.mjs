import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';

const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const db=read('games.json');
const companies=read('company-coverage.json').companies;
const hawk=companies.find(c=>c.id==='hawkeye');
const minato=companies.find(c=>c.id==='minatosoft');
const miraiIds=['g1266','g1267','g1268','g1269','g1270','g1271'];

test('the Hawk Eye company dossier reuses Minato works and adds searchable mirai identities',()=>{
  assert.ok(hawk);
  assert.equal(hawk.workIds.length,30);
  assert.deepEqual(hawk.workIds.slice(0,24),minato.workIds);
  assert.deepEqual(hawk.workIds.slice(24),miraiIds);
  for(const id of miraiIds){
    const work=db.works.find(w=>w.id===id);
    assert.ok(work);
    for(const query of [work.chineseTitle,work.originalTitle]){
      assert.ok(filterCatalogue(db,{query}).some(x=>x.work.id===id),query);
    }
    assert.equal(db.contentVersions.filter(c=>c.workId===id).length,1);
    assert.equal(db.platformReleases.filter(r=>r.workId===id).length,1);
  }
  assert.equal(hawk.dossierGroups.length,7);
  assert.deepEqual(hawk.dossierGroups[5].workIds,miraiIds);
  const page=readFileSync(new URL('../hawkeye.html',import.meta.url),'utf8');
  for(const id of hawk.workIds)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
  assert.ok(page.includes('minatosoft.html#minato-collaborations'));
});

test('Fujiko debut, bonus disc and FuRyu collaboration preserve content and credits',()=>{
  const fujiko=db.works.find(w=>w.id==='g1271');
  assert.equal(fujiko.firstYear,2020);
  assert.equal(fujiko.releaseContext,'bundledSample');
  assert.deepEqual(db.platformReleases.filter(r=>r.workId===fujiko.id).map(r=>r.year),[2020]);
  assert.match(fujiko.notes,/6月19日.*同篇/);
  const aarin=db.works.find(w=>w.id==='g1267');
  assert.equal(aarin.releaseContext,'bundledSample');
  assert.match(aarin.bundledWith,/ビジュアルファンブック/);
  const han=db.works.find(w=>w.id==='g1266');
  assert.ok(han.interactionModes.includes('战斗指令'));
  const related=hawk.relatedGames;
  assert.deepEqual(related.map(w=>w.id),['hawkeye-jukai']);
  assert.equal(related[0].platformReleases[0].publisher,'フリュー');
  assert.ok(related[0].interactionModes.includes('即时动作'));
  assert.ok(!db.works.some(w=>w.id===related[0].id));
  assert.deepEqual(minato.relatedGames.map(w=>w.id),['minatosoft-hanayui','minatosoft-spyce','minatosoft-climax']);
  const rows=read('gameplay-catalogues.json').companies.hawkeye.groups.flatMap(g=>g.rows);
  assert.equal(rows.filter(r=>r.workId).length,31);
  assert.ok(rows.some(r=>r.title?.includes('BugBug EDITION')&&!r.workId));
  assert.ok(rows.some(r=>r.title?.includes('クロガネ回姫雀')&&!r.workId));
});
