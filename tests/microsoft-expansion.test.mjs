import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const games=read('games.json'),model=read('entities.json'),credits=read('credits.json'),org=read('organizations.json');

test('Microsoft expansion adds two distinct originals without multiplying retail episodes or channels',()=>{
  const newIds=['g1300','g1301'];
  assert.deepEqual(games.works.filter(w=>newIds.includes(w.id)).map(w=>[w.id,w.originalTitle,w.subcategory]),[
    ['g1300','Fable II','选择式动作RPG'],['g1301','Avowed','选择式动作RPG']]);
  for(const wid of newIds){
    assert.deepEqual(games.contentVersions.filter(c=>c.workId===wid).map(c=>c.basis),['original']);
    const releases=games.platformReleases.filter(r=>r.workId===wid);
    assert.equal(releases.length,1);assert.equal(releases[0].contentVersionId,`${wid}-c-original`);
    assert.equal(releases[0].releaseRole,'contentDebut');
  }
  assert.equal(games.platformReleases.find(r=>r.id==='g1300-v1').publisher,'Microsoft Game Studios');
  assert.equal(games.platformReleases.find(r=>r.id==='g1301-v1').publisher,'Xbox Game Studios');
  assert.equal(games.works.find(w=>w.id==='g962').originalTitle,'D4: Dark Dreams Don’t Die');
});

test('Lionhead and Obsidian retain direct creation while Microsoft retains publishing and dated organization links',()=>{
  for(const [entityId,workId] of [['entity-lionhead','g1300'],['entity-obsidian','g1301']]){
    assert.equal(model.entities.find(e=>e.id===entityId).type,'company');
    assert.ok(credits.credits.some(c=>c.entityId===entityId&&c.workId===workId&&c.role==='originalProduction'&&c.status==='sourceReviewed'));
    assert.ok(!credits.credits.some(c=>c.entityId==='entity-microsoft'&&c.workId===workId&&c.role==='originalProduction'));
  }
  for(const [child,start] of [['entity-lionhead',2006],['entity-obsidian',2018],['entity-xbox_game_studios',2019]]){
    const relation=model.relations.find(r=>r.from===child&&r.to==='entity-microsoft');
    assert.equal(relation.period.from,start);assert.equal(relation.status,'sourceReviewed');
  }
  assert.deepEqual(org.organizationEvents.filter(e=>e.id.startsWith('microsoft-')).map(e=>e.year),[2000,2006,2018,2019]);
  const family=org.families.find(f=>f.id==='microsoft');
  assert.ok(['entity-lionhead','entity-obsidian'].every(id=>family.entityIds.includes(id)));
});
