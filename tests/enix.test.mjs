import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const enix=read('company-coverage.json').companies.find(c=>c.id==='enix');
const tables=read('gameplay-catalogues.json').companies.enix;

test('Enix new narratives exclude parser input while old identities remain intact',()=>{
  const main=data.works.find(w=>w.id==='g1162');
  assert.equal(main.originalTitle,'鈴木爆発');
  assert.equal(main.subcategory,'动作解谜融合');
  assert.ok(main.interactionModes.includes('谜题操作'));
  assert.equal(enix.relatedGames.length,45);
  const fresh=enix.relatedGames.filter(w=>w.id!=='enix-nanatsukaze');
  assert.equal(fresh.length,44);
  assert.ok([main,...fresh].every(w=>!w.interactionModes.includes('文字输入')));
  assert.equal(enix.dossierOnlyWorks.length,1);
  assert.equal(enix.dossierOnlyWorks[0].id,'enix-seiko');
  assert.ok(!data.works.some(w=>w.id==='enix-seiko'));
  assert.ok(!data.contentVersions.some(v=>v.workId==='enix-seiko'));
  assert.match(enix.workContexts.g017,/键入人名、地名/);
  for(const id of ['g007','g079','g996','g999'])assert.ok(enix.workIds.includes(id));
});

test('Enix content additions have specific increments and retain later publisher credits',()=>{
  for(const id of ['enix-so3','enix-wonderj2','enix-dqm2']){
    const w=enix.relatedGames.find(w=>w.id===id);
    assert.equal(w.contentVersions.length,2);
    const extra=w.contentVersions.find(c=>c.basis==='added');
    assert.equal(extra.comparedTo,id+'-c-original');
    assert.ok(extra.addedContent[0].description.length>30);
    assert.equal(w.platformReleases.length,2);
    assert.ok(w.platformReleases.every(v=>v.releaseRole==='contentDebut'));
    if(id!=='enix-dqm2')assert.equal(w.platformReleases[1].publisher,'スクウェア・エニックス');
  }
  const laika=enix.relatedGames.find(w=>w.id==='enix-laika');
  assert.ok(laika.interactionModes.includes('即时动作'));
  assert.ok(!laika.interactionModes.includes('战斗指令'));
  const endo=enix.relatedGames.find(w=>w.id==='enix-endonesia');
  assert.ok(!endo.interactionModes.includes('战斗指令'));
});

test('Enix reference rows cannot silently admit sports, raising, ordinary ports or uncertain controls',()=>{
  const rows=tables.groups.flatMap(g=>g.rows);
  assert.equal(rows.length,174);
  const ids=rows.filter(r=>r.workId).map(r=>r.workId);
  assert.equal(ids.length,75);
  assert.equal(new Set(ids).size,75);
  for(const title of ['Command Master／指令大师','Grandia II','手天童子','Cross Gate／魔力宝贝','Astronoka／アストロノーカ']){
    const row=rows.find(r=>r.title===title);
    assert.ok(row && !row.workId);
    assert.ok(!enix.relatedGames.some(w=>w.title===title));
  }
  const page=readFileSync(new URL('../enix.html',import.meta.url),'utf8');
  assert.equal(page.split('<article class="card"').length-1,75);
  assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
  assert.ok(!/undefined|NaN|Infinity/.test(page));
});
