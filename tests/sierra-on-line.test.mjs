import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/games.json');
const companies=read('data/company-coverage.json').companies;
const co=companies.find(c=>c.id==='sierra_on_line');
const early=companies.find(c=>c.id==='sierra');
const page=readFileSync(new URL('../sierra_on_line.html',import.meta.url),'utf8');
const all=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
const byTitle=t=>data.works.find(w=>w.originalTitle===t);

test('Sierra brand dossier excludes every early identity and preserves the existing parser sequel',()=>{
  const excludedIds=new Set([...early.workIds,...early.relatedGames.map(w=>w.id),...early.dossierOnlyWorks.map(w=>w.id)]);
  assert.ok(all.every(id=>!excludedIds.has(id)));
  assert.equal(all.length,84);
  assert.equal(new Set(all).size,84);
  assert.deepEqual(co.legacyCommandWorkIds,['g061']);
  assert.equal(co.workIds.filter(id=>id==='g061').length,1);
  assert.ok(data.works.find(w=>w.id==='g061').interactionModes.includes('文字输入'));
  const grouped=co.dossierGroups.flatMap(g=>g.workIds);
  assert.deepEqual(new Set(grouped),new Set(all));
  assert.equal(grouped.length,all.length);
  assert.equal((page.match(/<article class="card"/g)||[]).length,84);
});

test('new Sierra main narratives have no parser input and remain searchable by documented controls',()=>{
  const added=co.workIds.filter(id=>id!=='g061');
  assert.equal(added.length,44);
  for(const id of added){
    const w=data.works.find(w=>w.id===id);
    assert.ok(!w.interactionModes.includes('文字输入'));
    const matches=filterCatalogue(data,{query:w.originalTitle,interaction:w.interactionModes[0]});
    assert.ok(matches.some(r=>r.work.id===id),w.originalTitle);
    assert.ok(!filterCatalogue(data,{query:w.originalTitle,interaction:'文字输入'}).some(r=>r.work.id===id));
    assert.equal(data.contentVersions.filter(c=>c.workId===id && c.basis==='original').length,1);
    assert.ok(data.platformReleases.filter(r=>r.workId===id).every(r=>r.releaseRole==='contentDebut'));
  }
});

test('click interfaces with MAD, police queries, Other verbs and SIDNEY remain bibliography only',()=>{
  assert.equal(co.dossierOnlyWorks.length,26);
  for(const key of ['manhunter1','manhunter2','pq3','pq4','larry7','gk3']){
    const w=co.dossierOnlyWorks.find(w=>w.id==='sierra-on-line-'+key);
    assert.ok(w.interactionModes.includes('文字输入'));
    assert.ok(w.interactionModes.includes('点击调查'));
  }
  for(const w of co.dossierOnlyWorks){
    assert.ok(w.interactionModes.includes('文字输入'));
    assert.ok(!data.works.some(x=>x.id===w.id));
    assert.ok(!data.contentVersions.some(x=>x.workId===w.id));
    assert.ok(!data.platformReleases.some(x=>x.workId===w.id));
    assert.ok(!('contentVersions' in w) && !('platformReleases' in w));
  }
  const gk1=byTitle('Gabriel Knight: Sins of the Fathers');
  assert.ok(gk1.interactionModes.includes('谜题操作'));
  assert.ok(gk1.interactionNote.includes('符号板'));
  assert.ok(gk1.interactionNote.includes('短语表'));
});

test('pre-authored Playtoons stories have product identity without admitting a shared writing editor',()=>{
  const samples=data.works.filter(w=>co.workIds.includes(w.id) && w.releaseContext==='bundledSample');
  assert.equal(samples.length,5);
  assert.deepEqual(new Set(samples.map(w=>w.id)),new Set(co.bundledSampleWorkIds));
  assert.equal(new Set(samples.map(w=>w.bundledWith)).size,5);
  for(const w of samples){
    assert.equal(w.subcategory,'互动绘本');
    assert.ok(w.interactionModes.includes('阅读推进'));
    assert.ok(w.interactionNote.includes('只归档预制故事'));
    assert.ok(!w.interactionModes.includes('文字输入'));
  }
  assert.ok(read('data/taxonomy.json').subcategories['互动动画'].includes('互动绘本'));
});

test('RPG first publishers and Hellfire dependency survive the Sierra association',()=>{
  assert.equal(co.relatedGames.length,13);
  for(const [id,pub] of [['sorcerian','日本ファルコム'],['zeliard','Game Arts']]){
    const w=co.relatedGames.find(w=>w.id==='sierra-on-line-'+id);
    assert.equal(w.firstYear,1987);
    assert.equal(w.platformReleases[0].publisher,pub);
    assert.equal(w.platformReleases.length,1);
    assert.ok(!data.works.some(x=>x.id===w.id));
  }
  const diablo=co.relatedGames.find(w=>w.id==='sierra-on-line-diablo-hellfire');
  assert.equal(diablo.firstYear,1996);
  assert.equal(diablo.platformReleases[0].publisher,'Blizzard Entertainment');
  const add=diablo.contentVersions.find(c=>c.basis==='added');
  assert.equal(add.comparedTo,diablo.contentVersions.find(c=>c.basis==='original').id);
  assert.ok(add.addedContent[0].description.includes('Monk'));
  assert.equal(diablo.platformReleases.find(r=>r.contentVersionId===add.id).publisher,'Sierra On-Line');
  assert.ok(!all.some(id=>id==='hellfire'));
});

test('new content needs concrete media or playable additions and correct original OS',()=>{
  const goose=byTitle('Mixed-Up Mother Goose');
  const add=data.contentVersions.find(c=>c.workId===goose.id && c.basis==='added');
  assert.equal(add.firstYear,1995);
  assert.ok(add.addedContent[0].description.includes('角色语音'));
  assert.equal(data.platformReleases.find(r=>r.contentVersionId===add.id).platform,'Windows');
  for(const title of ['King’s Quest VII: The Princeless Bride','Shivers','Shivers Two: Harvest of Souls','Phantasmagoria: A Puzzle of Flesh','Urban Runner','Stay Tooned!']){
    const w=byTitle(title);
    assert.equal(data.platformReleases.find(r=>r.workId===w.id).platform,'Windows',title);
  }
});

test('170 gameplay references cannot add cards or duplicate the old excluded titles',()=>{
  const appendix=read('data/gameplay-catalogues.json').companies.sierra_on_line;
  const rows=appendix.groups.flatMap(g=>g.rows);
  assert.equal(rows.length,254);
  assert.equal(rows.filter(r=>r.workId).length,84);
  const refs=rows.filter(r=>!r.workId);
  assert.equal(refs.length,170);
  for(const title of ['Inca','Inca II: Wiracocha','The Last Dynasty','David Wolf: Secret Agent','Police Quest: SWAT','Half-Life']){
    assert.ok(refs.some(r=>r.title===title));
    assert.ok(!co.entries.find(e=>e.title===title).workIds.length);
  }
  assert.ok(!refs.some(r=>['Mystery House','The Dark Crystal','Gelfling Adventure'].includes(r.title)));
  assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
});
