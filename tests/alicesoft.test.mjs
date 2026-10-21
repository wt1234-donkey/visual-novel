import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
const read=p=>JSON.parse(readFileSync(new URL('../data/'+p,import.meta.url),'utf8'));
const data=read('games.json');
const company=read('company-coverage.json').companies.find(c=>c.id==='alicesoft');
const review=read('alicesoft-source-review.json');
const works=new Map([...data.works,...company.relatedGames].map(w=>[w.id,w]));
test('Alicesoft remakes reuse work IDs and every admitted addition has a comparison and release',()=>{
  assert.equal(company.workIds.length,126);
  assert.equal(company.relatedGames.length,108);
  assert.equal(review.newWorkCount,0);
  assert.equal(review.changes.length,9);
  for(const row of review.changes){
    const w=works.get(row.workId);
    const contents=w.contentVersions??data.contentVersions.filter(c=>c.workId===w.id);
    const releases=w.platformReleases??data.platformReleases.filter(r=>r.workId===w.id);
    const c=contents.find(c=>c.id===row.contentId);
    assert.equal(c.basis,'added');
    assert.ok(contents.some(p=>p.id===c.comparedTo));
    assert.ok(c.addedContent.every(a=>a.description.length>10&&a.source.startsWith('https://')));
    assert.equal(releases.find(r=>r.id===row.releaseId).contentVersionId,c.id);
  }
});
test('Magnum is dependent 2012 content and its 2018 bundle does not create a second addition',()=>{
  const q=works.get('alicesoft-extra-rancequest');
  const first=q.platformReleases.find(r=>r.year===2012);
  const bundle=q.platformReleases.find(r=>r.year===2018);
  assert.equal(first.releaseRole,'contentDebut');
  assert.equal(first.voice,'无');
  assert.equal(bundle.contentVersionId,first.contentVersionId);
  assert.equal(bundle.contentRelation,'same');
  assert.deepEqual(q.contentVersions.map(c=>c.firstYear),[2011,2012]);
});
test('new recordings and playable characters qualify independently of higher resolution',()=>{
  assert.match(works.get('alicesoft-extra-yorugakuru').contentVersions[1].evidence,/故事无增删.*声音全部重新录制/);
  assert.match(works.get('alicesoft-extra-mamanyonyo').contentVersions[1].evidence,/新角色内容/);
  const rows=read('gameplay-catalogues.json').companies.alicesoft.groups.flatMap(g=>g.rows);
  const box=rows.find(r=>r.title==='Rance35th Anniversary Box');
  assert.ok(!box.workId);
  assert.ok(![...works.values()].some(w=>w.originalTitle==='Rance35th Anniversary Box'));
});
