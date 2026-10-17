import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const co=read('company-coverage.json').companies.find(c=>c.id==='legend_entertainment');
const table=read('gameplay-catalogues.json').companies.legend_entertainment;

test('American Legend admits four menu adventures and isolates nine input works',()=>{
  assert.equal(co.foundedAt,'1989');
  assert.deepEqual(co.workIds,['g1169','g1170','g1171','g1172']);
  for(const id of co.workIds){
    const w=data.works.find(w=>w.id===id);
    assert.ok(!w.interactionModes.includes('文字输入'));
    assert.ok(w.interactionModes.includes('点击调查'));
  }
  assert.equal(co.dossierOnlyWorks.length,9);
  for(const w of co.dossierOnlyWorks){
    assert.ok(w.interactionModes.includes('文字输入'));
    assert.ok(!data.works.some(x=>x.id===w.id));
    assert.ok(!('contentVersions' in w)&&!('platformReleases' in w));
  }
  assert.match(co.dossierOnlyWorks.find(w=>w.id.endsWith('callahans')).interactionNote,/谜底/);
  assert.match(co.dossierOnlyWorks.find(w=>w.id.endsWith('blackstone')).interactionNote,/Mandy Lee/);
  assert.deepEqual(filterCatalogue(data,{company:'Legend Entertainment'}).map(x=>x.work.id),co.workIds);
  assert.deepEqual(filterCatalogue(data,{company:'Legend'}).map(x=>x.work.id),['g114']);
  assert.match(data.works.find(w=>w.id==='g1172').notes,/Triton Interactive、FAR Productions/);
});

test('voice additions and dependent Na Pali have explicit comparison identities',()=>{
  const xanth=data.contentVersions.filter(c=>c.workId==='g1169');
  assert.equal(xanth.length,2);
  assert.equal(xanth[1].firstYear,1994);
  assert.equal(xanth[1].comparedTo,xanth[0].id);
  assert.match(xanth[1].addedContent[0].description,/录音/);
  assert.equal(co.relatedGames.length,5);
  const unreal=co.relatedGames.find(w=>w.originalTitle==='Unreal');
  assert.equal(unreal.firstYear,1998);
  assert.match(unreal.notes,/Epic MegaGames与Digital Extremes/);
  const added=unreal.contentVersions.find(c=>c.basis==='added');
  assert.equal(added.firstYear,1999);
  assert.equal(added.comparedTo,unreal.contentVersions[0].id);
  assert.match(added.addedContent[0].description,/新武器/);
  assert.ok(!co.relatedGames.some(w=>w.originalTitle==='Unreal Mission Pack I: Return to Na Pali'));
  const hob=co.relatedGames.find(w=>w.originalTitle==='Superhero League of Hoboken');
  assert.deepEqual(hob.platformReleases.map(r=>[r.year,r.voice]),[[1994,'无'],[1995,'有']]);
  assert.equal(co.relatedGames.flatMap(w=>w.contentVersions).length,7);
  assert.equal(co.relatedGames.flatMap(w=>w.platformReleases).length,7);
  for(const w of co.relatedGames){
    assert.ok(!w.interactionModes.includes('文字输入'));
    assert.ok(!data.works.some(x=>x.id===w.id));
    assert.ok(w.platformReleases.every(r=>r.releaseRole==='contentDebut'));
  }
  assert.equal(co.relatedGames.find(w=>w.originalTitle==='Unreal II: The Awakening').platformReleases[0].publisher,'Infogrames');
});

test('dossier covers the catalogue without duplicating expansions or competitive works',()=>{
  const rows=table.groups.flatMap(g=>g.rows);
  assert.equal(rows.length,26);
  assert.equal(rows.filter(r=>r.workId).length,18);
  const xmp=rows.find(r=>r.title?.includes('eXpanded MultiPlayer'));
  assert.ok(xmp&&!xmp.workId);
  assert.match(xmp.relation,/排除纯多人/);
  assert.ok(rows.find(r=>r.title?.startsWith('Terminator 3'))&&!rows.find(r=>r.title?.startsWith('Terminator 3')).workId);
  const page=readFileSync(new URL('../legend_entertainment.html',import.meta.url),'utf8');
  assert.equal(page.split('<article class="card"').length-1,18);
  assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="legend_entertainment.html">Legend Entertainment（美国）社</a>'));
});
