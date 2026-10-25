import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue} from '../filter.mjs';
import {createEntityIndex,creditsForRelease,relatedEntityIds} from '../entities.mjs';
const read=name=>JSON.parse(readFileSync(new URL('../data/'+name,import.meta.url),'utf8'));
const data=read('games.json'),model=read('entities.json'),credits=read('credits.json');
const index=createEntityIndex(data,model,credits,read('work-classification.json'));
const find=f=>filterCatalogue(data,f,index);

test('brand browsing follows the original work while publisher, year and platform match one release',()=>{
  const key=find({brand:'entity-key',query:'Kanon',platform:'Nintendo Switch'});assert.equal(key.length,1);assert.equal(key[0].work.id,'g028');
  const publisher=find({publisher:'entity-prototype',query:'Kanon',platform:'Nintendo Switch'});assert.equal(publisher.length,1);assert.ok(publisher[0].platformReleases.every(r=>r.publisher==='PROTOTYPE'));
  assert.equal(find({publisher:'entity-prototype',query:'Kanon',platform:'Windows',from:1999,to:1999}).length,0);
});
test('ATRI co-production and publishing brand stay distinct from iMel port releases',()=>{
  for(const developer of ['entity-frontwing','entity-makura'])assert.equal(find({developer,query:'ATRI'}).length,1);
  assert.equal(find({developer:'entity-aniplex_exe',query:'ATRI'}).length,0);
  assert.equal(find({brand:'entity-aniplex_exe',publisher:'entity-imel',query:'ATRI',platform:'Nintendo Switch'}).length,1);
  assert.equal(find({publisher:'entity-imel',query:'ATRI',platform:'Windows'}).length,0);
});
test('Leaf later content is not assigned retrospectively to the ToHeart2 PS2 original',()=>{
  assert.equal(find({brand:'entity-leaf',query:'ToHeart2',platform:'PlayStation 2',from:2004,to:2004}).length,0);
  assert.ok(find({brand:'entity-leaf',query:'ToHeart2',platform:'Windows'}).some(x=>x.work.id==='g159'));
});
test('a child brand remains independently searchable without changing the legacy corporate index',()=>{
  assert.ok(find({brand:'entity-nitrochiral',query:'DRAMAtical Murder'}).some(x=>x.work.id==='g625'));
  assert.ok(filterCatalogue(data,{company:'Nitroplus',query:'DRAMAtical Murder'}).some(x=>x.work.id==='g625'));
  const raw=credits.credits.filter(c=>c.targetType==='release'&&c.rawCredit==='Nitro+CHiRAL');assert.ok(raw.length);assert.ok(raw.every(c=>c.entityId==='entity-nitrochiral'));
});
test('GAINAX production excludes IP-only and supervised works but dossier affiliation preserves them',()=>{
  const made=find({developer:'entity-gainax'}).map(x=>x.work.id);assert.ok(made.includes('g1277'));for(const id of ['g827','g828','g829','g927','g1276'])assert.ok(!made.includes(id));
  const dossier=find({dossier:'gainax'}).map(x=>x.work.id);assert.equal(dossier.length,21);assert.ok(dossier.includes('g927'));
  assert.deepEqual(find({participant:'entity-gainax',participantRole:'supervisor'}).map(x=>x.work.id),['g829']);
});
test('added animation credits affect only their recorded content and never the original release',()=>{
  const results=find({participant:'entity-yonago_gainax',query:'Princess Maker 2'});assert.equal(results.length,1);assert.ok(results[0].platformReleases.every(r=>r.year===2024));
  assert.equal(find({participant:'entity-yonago_gainax',from:1993,to:1993}).length,0);
});
test('affiliation expansion is explicit, cycle safe and does not imply direct production',()=>{
  assert.equal(find({developer:'entity-visualarts',query:'Kanon'}).length,0);
  assert.equal(find({developer:'entity-visualarts',includeAffiliates:true,query:'Kanon'}).length,1);
  const cyclic={...index,model:{...model,relations:[...model.relations,{from:'entity-visualarts',to:'entity-key',type:'operatedBy'}]}};
  assert.ok(relatedEntityIds(cyclic,'entity-key',true).has('entity-visualarts'));
});
test('unfiltered entity-aware catalogue preserves every existing work, content and release',()=>{
  const old=filterCatalogue(data),current=find({});assert.deepEqual(current,old);
  const raw=read('entity-catalogue.json');const compact=createEntityIndex(data,raw.model,raw);assert.deepEqual(filterCatalogue(data,{brand:'entity-key'},compact),find({brand:'entity-key'}));
  const r=data.platformReleases.find(r=>r.workId==='g200'&&r.platform==='Windows');assert.ok(creditsForRelease(index,'g200',r).some(c=>c.entityId==='entity-frontwing'));
});
test('reviewed production can be found without promoting corporate parents or related RPGs into the main catalogue',()=>{
  assert.ok(find({developer:'entity-minatosoft'}).some(x=>x.work.id==='g1251'));
  assert.ok(!find({developer:'entity-hawkeye'}).some(x=>x.work.id==='g1251'));
  assert.ok(!find({developer:'entity-nitroplus'}).some(x=>x.work.id==='g622'));
  for(const id of ['key-rpg-hbr','august-rpg-imys','minatosoft-climax'])assert.ok(!find({}).some(x=>x.work.id===id));
  assert.ok(!credits.credits.some(c=>c.entityId==='entity-name-5caee77c6090'&&c.targetType==='work'&&['developer','localizer'].includes(c.role)));
  assert.ok(!credits.credits.some(c=>c.entityId==='entity-name-5caee77c6090'&&c.role==='localizer'));
});

test('third review confirms named production while preserving same-name company and publisher scopes',()=>{
  assert.ok(find({developer:'entity-overdrive',query:'Go! Go! Nippon!'}).some(x=>x.work.id==='g647'));
  assert.equal(find({developer:'entity-name-85a1fd56da66',query:'Go! Go! Nippon!'}).length,0);
  for(const [wid,query] of [['g163','The Song of Saya'],['g614','YOU and ME and HER']]){
    assert.ok(find({participant:'entity-nitroplus_brand',participantRole:'productionBrand',query}).some(x=>x.work.id===wid));
    assert.equal(find({developer:'entity-nitroplus',query}).length,0);
    assert.equal(find({participant:'entity-nitroplus',participantRole:'productionBrand',query}).length,0);
  }
});

test('reviewed Micro Cabin book production never admits parser books to the main catalogue',()=>{
  for(const query of ['ダイヤモンドアドベンチャー','ドリームランド']){
    assert.equal(find({developer:'entity-microcabin',query}).length,0);
  }
  for(const wid of ['microcabin-diamond','microcabin-dream']){
    const member=credits.dossierMemberships.find(m=>m.dossierId==='microcabin'&&m.workId===wid);
    assert.equal(member.group,'original');assert.equal(member.placement,'bibliography');
  }
});

test('anniversary development is limited to added content and never the 1992 Night Trap original',()=>{
  const developer='entity-name-d05eacc25c69';
  const made=find({developer});
  assert.equal(made.length,1);
  assert.equal(made[0].work.id,'g934');
  assert.deepEqual(made[0].platformReleases.map(r=>r.id),['g934-v2']);
  assert.equal(find({developer,from:1992,to:1992}).length,0);
  assert.equal(find({developer,from:2017,to:2017}).length,1);
  const original=data.platformReleases.find(r=>r.id==='g934-v1');
  const later=data.platformReleases.find(r=>r.id==='g934-v2');
  assert.ok(!creditsForRelease(index,'g934',original).some(c=>c.entityId===developer&&c.role==='developer'));
  assert.ok(creditsForRelease(index,'g934',later).some(c=>c.entityId===developer&&c.role==='developer'&&c.targetType==='content'));
});

test('Serenity Forge Plus development excludes original DDLC and mobile releases with unknown content',()=>{
  const developer='entity-name-22015689e48e';
  const made=find({developer});
  assert.equal(made.length,1);
  assert.equal(made[0].work.id,'g056');
  assert.deepEqual(made[0].platformReleases.map(r=>r.id),['g056-v3','g056-v4','g056-v5']);
  assert.equal(find({developer,from:2017,to:2017}).length,0);
  assert.equal(find({developer,from:2021,to:2021}).length,1);
  assert.equal(find({developer,from:2025,to:2025}).length,0);
  for(const rid of ['g056-v1','g056-v2','g056-v6','g056-v7']){
    const release=data.platformReleases.find(r=>r.id===rid);
    assert.ok(!creditsForRelease(index,'g056',release).some(c=>c.entityId===developer&&c.role==='developer'));
  }
  for(const rid of ['g056-v3','g056-v4','g056-v5']){
    const release=data.platformReleases.find(r=>r.id===rid);
    assert.ok(creditsForRelease(index,'g056',release).some(c=>c.entityId===developer&&c.role==='developer'&&c.targetId==='g056-c-3'));
  }
});


test('Shiravune developer credit matches only the 2022 Doukyuusei release even with shared content',()=>{
  const developer='entity-name-5caee77c6090';
  const made=find({developer});
  assert.deepEqual(made.map(x=>x.work.id),['g046']);
  assert.deepEqual(made[0].platformReleases.map(r=>r.id),['g046-v3']);
  for(const release of data.platformReleases.filter(r=>r.workId==='g046')){
    const has=creditsForRelease(index,'g046',release).some(c=>c.entityId===developer&&c.role==='developer');
    assert.equal(has,release.id==='g046-v3');
  }
  const scoped=data.platformReleases.find(r=>r.id==='g046-v3');
  assert.ok(scoped);
  assert.ok(!creditsForRelease(index,'g046',{...scoped,id:'other-release-same-content'})
    .some(c=>c.entityId===developer&&c.role==='developer'));
  assert.equal(find({developer,from:1992,to:1992}).length,0);
  assert.equal(find({developer,from:2021,to:2021}).length,0);
});


test('Sierra originals and A5 production exclude external studios and parent-brand shortcuts',()=>{
  assert.deepEqual(find({developer:'entity-sierra_company'}).map(x=>x.work.id).sort(),['g001','g060','g061']);
  for(const wid of ['g094','g1102','g1103','g1107','g1134']){
    const work=data.works.find(w=>w.id===wid);
    assert.ok(work);
    assert.ok(!find({developer:'entity-sierra_company'}).some(x=>x.work.id===wid));
  }
  assert.deepEqual(find({brand:'entity-silkys_a5',participantRole:'productionBrand'}).map(x=>x.work.id),['g473']);
  assert.equal(find({participant:'entity-silkys_plus',participantRole:'productionBrand'}).length,0);
  assert.equal(find({developer:'entity-silkys'}).length,0);
  assert.ok(find({publisher:'entity-ibm'}).some(x=>x.work.id==='g060'));
});


test('DOLCE and WASABI productions stay separate from Alpha and the parent; Simon retains publisher only',()=>{
  for(const [eid,wid] of [['entity-silkys_dolce','g475'],['entity-silkys_wasabi','g468']]){
    assert.deepEqual(find({participant:eid,participantRole:'productionBrand'}).map(x=>x.work.id),[wid]);
  }
  assert.equal(find({participant:'entity-silkys_plus',participantRole:'productionBrand'}).length,0);
  const alpha='entity-name-8c9d353d6fe9',simon='entity-name-b129f13b41e4';
  assert.equal(find({developer:alpha}).length,0);
  assert.deepEqual(find({publisher:alpha}).map(x=>x.work.id),['g468']);
  assert.deepEqual(find({publisher:alpha})[0].platformReleases.map(r=>r.id),['g468-v2']);
  assert.equal(model.entities.find(e=>e.id===simon).type,'brand');
  assert.equal(find({brand:simon}).length,0);
  assert.equal(find({developer:simon}).length,0);
  assert.deepEqual(find({publisher:simon}).map(x=>x.work.id),['g1188']);
});
