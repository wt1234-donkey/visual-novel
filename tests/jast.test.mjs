import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=n=>JSON.parse(readFileSync(new URL('../data/'+n,import.meta.url),'utf8'));
const data=read('games.json'),co=read('company-coverage.json').companies.find(c=>c.id==='jast');
const table=read('gameplay-catalogues.json').companies.jast;

test('JAST admits menu Special II and chapter combat Justice Slave with one original batch each',()=>{
 const main=data.works.find(w=>w.id==='g1215'),related=co.relatedGames.find(w=>w.id==='jast-justice-slave');
 assert.deepEqual(main.interactionModes,['菜单指令']);
 assert.match(main.interactionNote,/GO.*LOOK.*SPEAK.*ACTION/);
 assert.deepEqual(related.interactionModes,['阅读推进','选项分支','战斗指令']);
 assert.match(related.interactionNote,/第三章.*不据此声称/);
 for(const w of [main,related]){
  assert.ok(!w.interactionModes.includes('文字输入'));
  const cs=w.contentVersions??data.contentVersions.filter(c=>c.workId===w.id);
  const rs=w.platformReleases??data.platformReleases.filter(r=>r.workId===w.id);
  assert.equal(cs.length,1);assert.equal(rs.length,1);
  assert.equal(cs[0].basis,'original');assert.deepEqual(cs[0].evidenceReleaseIds,[rs[0].id]);
  assert.equal(rs[0].contentVersionId,cs[0].id);assert.equal(rs[0].releaseRole,'contentDebut');
  assert.deepEqual(rs[0].publisherCompanies,['JAST（日本）']);assert.equal(rs[0].voice,'未核实');
 }
 assert.equal(related.platformReleases[0].publisher,'Tiare');
 assert.match(related.notes,/8月13日.*8月23日/);
 assert.ok(!data.works.some(w=>w.id===related.id));
});

test('JAST parser shortcuts remain excluded and original identities are reused',()=>{
 assert.deepEqual(co.dossierOnlyWorks.map(w=>w.id),['jast-erika','jast-star-trap','jast-tenshi2']);
 for(const w of co.dossierOnlyWorks){
  assert.ok(w.interactionModes.includes('文字输入'));
  assert.ok(!('contentVersions' in w));assert.ok(!('platformReleases' in w));
  assert.ok(!data.works.some(x=>x.id===w.id));
 }
 assert.equal(co.dossierOnlyWorks.find(w=>w.id==='jast-star-trap').firstYear,1986);
 assert.match(co.dossierOnlyWorks.find(w=>w.id==='jast-star-trap').interactionNote,/菜单快捷功能不能抵消/);
 assert.ok(co.workIds.includes('g015'));assert.ok(co.workIds.includes('g652'));
 assert.ok(co.workIds.includes('g662'));assert.ok(co.workIds.includes('g678'));
 assert.ok(!co.publisherWorkIds.includes('g678'));
 assert.equal(co.relatedGames.find(w=>w.id==='jast-smiles').interactionBasis,'既有资料归纳');
});

test('JAST appendix covers each dossier identity once while sparse and board references stay out',()=>{
 const ids=[...co.workIds,...co.relatedGames.map(w=>w.id),...co.dossierOnlyWorks.map(w=>w.id)];
 const rows=table.groups.flatMap(g=>g.rows),refs=rows.filter(r=>r.workId).map(r=>r.workId);
 assert.equal(ids.length,44);assert.equal(co.workIds.length,33);assert.equal(co.relatedGames.length,8);
 assert.equal(rows.length,68);assert.equal(table.groups.length,7);
 assert.deepEqual([...refs].sort(),[...ids].sort());
 const page=readFileSync(new URL('../jast.html',import.meta.url),'utf8');
 for(const id of ids)assert.equal(page.split(`class="card" id="${id}"`).length-1,1,id);
 assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
 for(const title of ['CRISIS（1988／1989异文）','天使人形（Angel Doll）','彼岸花の追憶／彼岸花の記憶']){
  const row=rows.find(r=>r.title===title);assert.ok(row&&!row.workId);
 }
 assert.equal(co.entries.length,co.catalogueEntryCount);
 assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="jast.html"'));
});
