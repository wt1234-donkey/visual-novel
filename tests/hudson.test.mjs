import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const h=read('company-coverage.json').companies.find(c=>c.id==='hudson');
const table=read('gameplay-catalogues.json').companies.hudson;

test('Hudson separates new non-parser narratives, RPGs and input bibliography',()=>{
  const fresh=data.works.filter(w=>['g1163','g1164','g1165','g1166','g1167','g1168'].includes(w.id));
  assert.equal(fresh.length,6);
  assert.equal(h.relatedGames.length,37);
  assert.ok([...fresh,...h.relatedGames].every(w=>!w.interactionModes.includes('文字输入')));
  assert.ok(h.workIds.includes('g074')&&h.workIds.includes('g077'));
  assert.equal(h.dossierOnlyWorks[0].id,'hudson-dezeni-world');
  assert.equal(h.dossierOnlyWorks[0].firstYear,1985);
  assert.ok(!data.contentVersions.some(c=>c.workId==='hudson-dezeni-world'));
  const rows=table.groups.flatMap(g=>g.rows);
  const robot=rows.find(r=>r.title?.startsWith('机器人波恩科茨 SUN'));
  assert.ok(robot&&!robot.workId);
  assert.match(robot.note,/文本消息/);
  assert.ok(!h.relatedGames.some(w=>w.id==='ascii-anearth'));
  assert.ok(!h.workIds.includes('g814'));
});

test('Hudson content and publisher identities follow first added-content batches',()=>{
  for(const id of ['hudson-ziria','hudson-tengai2']){
    const w=h.relatedGames.find(w=>w.id===id);
    assert.equal(w.contentVersions.length,2);
    assert.equal(w.contentVersions[1].comparedTo,id+'-c-original');
    assert.ok(w.contentVersions[1].addedContent[0].description.length>40);
    assert.ok(w.platformReleases.every(v=>v.releaseRole==='contentDebut'));
  }
  const two=h.relatedGames.find(w=>w.id==='hudson-tengai2');
  assert.equal(two.platformReleases[1].platform,'Nintendo GameCube');
  assert.ok(!two.platformReleases.some(v=>v.platform==='PlayStation 2'));
  const wars=h.relatedGames.find(w=>w.id==='hudson-bomberwars');
  assert.equal(wars.contentVersions.length,1);
  assert.equal(wars.platformReleases.length,2);
  assert.equal(new Set(wars.platformReleases.map(v=>v.contentVersionId)).size,1);
  const oriental=h.relatedGames.find(w=>w.id==='hudson-orientalblue');
  assert.equal(oriental.platformReleases[0].publisher,'任天堂');
  assert.equal(data.platformReleases.find(v=>v.workId==='g1167').publisher,'Hudson Entertainment');
  assert.equal(data.works.find(w=>w.id==='g1165').interactionModes.includes('瞄准射击'),true);
  const wataru=h.relatedGames.find(w=>w.id==='hudson-wataru');
  assert.ok(wataru.interactionModes.includes('即时动作'));
  assert.ok(!wataru.interactionModes.includes('战斗指令'));
});

test('Hudson appendix preserves one link per work and excludes pure competitive references',()=>{
  const rows=table.groups.flatMap(g=>g.rows);
  assert.equal(rows.length,138);
  const linked=rows.filter(r=>r.workId).map(r=>r.workId);
  assert.equal(linked.length,65);
  assert.equal(new Set(linked).size,65);
  const page=readFileSync(new URL('../hudson.html',import.meta.url),'utf8');
  assert.equal(page.split('<article class="card"').length-1,65);
  assert.ok(page.indexOf('id="gameplay-catalogue"')>page.indexOf('id="coverage"'));
  for(const title of ['Hyper Wars','桃太郎电铁系列','大贝兽物语 Miracle of the Zone I·II']){
    assert.ok(rows.some(r=>r.title===title&&!r.workId));
  }
});
