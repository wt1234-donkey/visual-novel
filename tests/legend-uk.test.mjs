import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='legend_uk');
const table=read('gameplay-catalogues.json').companies.legend_uk;

test('British Legend reuses the parser original and keeps the menu management game separate',()=>{
  assert.equal(co.foundedAt,'1981-09');
  assert.deepEqual(co.workIds,['g114']);
  assert.deepEqual(co.legacyCommandWorkIds,['g114']);
  assert.equal(data.works.filter(w=>w.originalTitle==='Valhalla').length,1);
  assert.deepEqual(filterCatalogue(data,{company:'Legend'}).map(x=>x.work.id),['g114']);
  const game=co.relatedGames[0];
  assert.equal(game.originalTitle,'The Great Space Race');
  assert.ok(!data.works.some(w=>w.id===game.id));
  assert.ok(!game.interactionModes.includes('文字输入'));
  assert.deepEqual(game.interactionModes,['菜单指令','资源经营','战术策略']);
  assert.ok(game.interactionSources.some(s=>s.includes('YourSpectrum13')));
  assert.equal(game.contentVersions.length,1);
  assert.equal(game.platformReleases.length,1);
  assert.equal(game.platformReleases[0].platform,'ZX Spectrum');
  assert.equal(game.platformReleases[0].releaseRole,'contentDebut');
  assert.equal(game.contentVersions[0].evidenceReleaseIds[0],game.platformReleases[0].id);
});

test('Legend unissued sequels, ports and pure shooting stay references',()=>{
  const rows=table.groups.flatMap(g=>g.rows);
  assert.equal(rows.length,7);
  assert.deepEqual(rows.filter(r=>r.workId).map(r=>r.workId),['g114','legend-uk-great-space-race']);
  for(const name of ['Komplex（1985）','Komplex City','Valhalla 2','The Great Space Race（Commodore 64计划）']){
    const row=rows.find(r=>r.title===name);
    assert.ok(row&&!row.workId);
    assert.ok(!co.relatedGames.some(w=>w.originalTitle===name));
  }
  assert.match(rows.find(r=>r.title==='Komplex City').relation,/未商业发行/);
  assert.deepEqual(co.dossierOnlyWorks,[]);
  const page=readFileSync(new URL('../legend_uk.html',import.meta.url),'utf8');
  assert.equal(page.split('<article class="card"').length-1,2);
  assert.ok(page.includes('id="g114"')&&page.includes('id="legend-uk-great-space-race"'));
  assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="legend_uk.html">Legend（英国）社</a>'));
});
