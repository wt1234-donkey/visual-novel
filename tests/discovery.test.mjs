import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createEntityIndex} from '../entities.mjs';
import {filterCatalogue} from '../filter.mjs';
import {createAtlas,filterAtlas,creatorCredits,creatorWorkIds,creditScope,metadataValues,PENDING,titleOf,narrativeState,narrativeCounts} from '../discovery-model.mjs';
const read=path=>JSON.parse(readFileSync(new URL('../data/'+path+'.json',import.meta.url),'utf8'));
const data=read('games'),catalogue=read('entity-catalogue'),editorial=read('discovery-editorial'),creators=read('creator-credits');
const atlas=createAtlas(data,catalogue,editorial,creators,read('work-notes'));
const index=createEntityIndex(data,catalogue.model,catalogue);
test('new discovery uses the entire authoritative main catalogue and preserves records',()=>{
 const snapshot=JSON.stringify(data);
 assert.equal(filterAtlas(atlas).length,data.works.length);
 assert.ok(data.works.length>1000);
 assert.equal(new Set(filterAtlas(atlas).map(w=>w.id)).size,data.works.length);
 assert.equal(filterAtlas(atlas)[0].id,'g039');
 filterAtlas(atlas,{sort:'newest'});filterAtlas(atlas,{sort:'oldest'});
 assert.equal(JSON.stringify(data),snapshot);
});
test('content filters keep uncurated distinct from no matching narrative content',()=>{
 const ids=Object.keys(editorial.works);
 assert.ok(ids.length>=8);
 const pending=filterAtlas(atlas,{facets:{theme:PENDING}});
 assert.equal(pending.length,data.works.filter(w=>!metadataValues(atlas,w,'theme').length).length);
 assert.ok(!pending.some(w=>w.id==='g039'));
 assert.ok(filterAtlas(atlas,{facets:{theme:'科幻'}}).some(w=>w.id==='g054'));
 assert.ok(filterAtlas(atlas,{facets:{gameplay:'战术策略'}}).some(w=>w.id==='g151'));
 for(const w of pending)assert.deepEqual(metadataValues(atlas,w,'theme'),[]);
});
test('work, character and personal name aliases are searchable',()=>{
 assert.ok(filterAtlas(atlas,{query:'WHITE ALBUM 2'}).some(w=>w.id==='g039'));
 assert.ok(filterAtlas(atlas,{query:'小木曾雪菜'}).some(w=>w.id==='g039'));
 assert.ok(filterAtlas(atlas,{query:'丸户史明'}).some(w=>w.id==='g039'));
 assert.ok(filterAtlas(atlas,{query:'clannad'}).some(w=>w.id==='g030'));
 assert.equal(filterAtlas(atlas,{query:'__no_such_work__'}).length,0);
});
test('personal music and writing roles use separate work sets',()=>{
 assert.deepEqual([...creatorWorkIds(atlas,'person','jun','writer')].sort(),['g029','g030']);
 assert.deepEqual([...creatorWorkIds(atlas,'person','jun','musician')],['g030']);
 assert.equal(creatorCredits(atlas,'g039','musician').length,0);
 assert.equal(creatorCredits(atlas,'g039','artist')[0].label,'角色设计 / 雪菜、和纱原画');
});
test('official edition credits retain scope without adding ordinary ports',()=>{
 const allReleaseIds=new Set(data.platformReleases.map(r=>r.id));
 const clannad=creators.credits.filter(c=>c.workId==='g030');
 assert.ok(clannad.every(c=>c.scope.type==='externalEdition'&&c.scope.platform==='PlayStation Vita'&&c.scope.year===2014));
 assert.ok(!data.platformReleases.some(r=>r.workId==='g030'&&r.year===2014&&r.platform==='PlayStation Vita'));
 const air=creators.credits.filter(c=>c.workId==='g029');
 assert.ok(air.every(c=>c.scope.type==='release'&&allReleaseIds.has(c.scope.releaseId)));
 assert.match(creditScope(atlas,air[0]),/2021.*Nintendo Switch/);
 assert.match(creditScope(atlas,clannad[0]),/2014.*PlayStation Vita/);
});
test('all new editorial and personal records have valid identities, roles and source scope',()=>{
 assert.equal(new Set(creators.people.map(p=>p.id)).size,creators.people.length);
 assert.equal(new Set(creators.credits.map(c=>c.id)).size,creators.credits.length);
 const personIds=new Set(creators.people.map(p=>p.id));
 for(const c of creators.credits){
  assert.ok(atlas.works.has(c.workId));assert.ok(personIds.has(c.personId));
  assert.ok(['writer','artist','musician'].includes(c.role));
  assert.ok(creators.people.find(p=>p.id===c.personId).roles.includes(c.role));
  assert.equal(c.status,'sourceReviewed');assert.match(c.source,/^https:\/\//);
  assert.ok(c.note&&c.scopeLabel);assert.ok(['release','externalEdition','documentedWork'].includes(c.scope.type));
  if(c.scope.type==='release')assert.equal(data.platformReleases.find(r=>r.id===c.scope.releaseId)?.workId,c.workId);
 }
 for(const [wid,m] of Object.entries(editorial.works)){
  assert.ok(atlas.works.has(wid));assert.ok(['editorialObservation','partial'].includes(m.status));
  assert.ok(m.basis&&m.sources.length);
  if(narrativeState(atlas,atlas.works.get(wid))!=='complete')assert.ok(m.openQuestions?.length);
 }
});
test('publishing, release-only port work and parent relations do not become original creative credits',()=>{
 const synthetic=structuredClone(catalogue);
 synthetic.model.entities.push({id:'test-publisher',type:'brand',name:'Only publisher',aliases:[]});
 synthetic.credits.push({entityId:'test-publisher',workId:'g030',targetType:'release',targetId:'g030-v1',role:'publisher'});
 synthetic.credits.push({entityId:'test-publisher',workId:'g029',targetType:'release',targetId:'g029-v2',role:'developer'});
 const a=createAtlas(data,synthetic,editorial,creators);
 assert.equal(creatorWorkIds(a,'entity','test-publisher').size,0);
 const direct=new Set(catalogue.credits.filter(c=>c.entityId==='entity-key'&&['productionBrand','originalProduction','developer','coDeveloper'].includes(c.role)&&['work','content'].includes(c.targetType)).map(c=>c.workId));
 assert.deepEqual(creatorWorkIds(atlas,'entity','entity-key'),direct);
});
test('collaboration candidates use actual joint-credit intersection without creating team identity',()=>{
 const c=creators.collaborations[0];assert.equal(c.status,'candidate');
 assert.deepEqual([...creatorWorkIds(atlas,'cooperation',c.id)].sort(),['g029','g030']);
 assert.ok(!catalogue.model.entities.some(e=>e.id===c.id));
 const limited=structuredClone(creators);limited.credits=limited.credits.filter(row=>!(row.workId==='g029'&&row.personId==='itaru'));
 assert.deepEqual([...creatorWorkIds(createAtlas(data,catalogue,editorial,limited),'cooperation',c.id)],['g030']);
});
test('legacy entity URLs still apply the same scoped filters on the full catalogue',()=>{
 for(const legacy of [{brand:'entity-key'},{publisher:'entity-aquaplus'},{dossier:'leaf'},{participant:'entity-nitroplus',participantRole:'developer'}]){
  const expected=new Set(filterCatalogue(data,legacy,index).map(r=>r.work.id));
  assert.deepEqual(new Set(filterAtlas(atlas,{legacy},index).map(w=>w.id)),expected);
 }
});
test('both homepage and retained advanced catalogue keep all existing dossier links and periods',()=>{
 const home=readFileSync(new URL('../index.html',import.meta.url),'utf8');
 const advanced=readFileSync(new URL('../catalogue.html',import.meta.url),'utf8');
 for(const page of [home,advanced]){
  for(const d of catalogue.model.dossiers)assert.ok(page.includes(`href="${d.id}.html"`),d.id);
  assert.ok(page.includes('company-dossiers:start')&&page.includes('company-dossiers:end'));
  assert.match(page,/每5年一组/);
  const ids=[...page.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(ids.length,new Set(ids).size);
 }
 assert.equal((home.match(/data-page="/g)||[]).length,4);
 assert.ok(home.includes('discovery.mjs'));
 assert.ok(advanced.includes('app.mjs'));
 assert.ok(home.includes('href="catalogue.html"'));
 assert.ok(home.includes('href="organizations.html"')||readFileSync(new URL('../discovery.mjs',import.meta.url),'utf8').includes('organizations.html'));
});

test('completion is counted per work, not by existence of an editorial object',()=>{
 const selected=data.works.find(w=>!['g039','g030','g192','g054','g227','g151','g029','g032'].includes(w.id));
 const base=structuredClone(editorial);
 base.works[selected.id]={position:'叙事与解谜并重',style:['探索'],theme:['奇幻']};
 const partial=createAtlas(data,catalogue,base,creators);
 assert.equal(narrativeState(partial,selected),'partial');
 assert.ok(filterAtlas(partial,{cataloguing:'partial'}).some(w=>w.id===selected.id));
 assert.ok(!filterAtlas(partial,{cataloguing:'complete'}).some(w=>w.id===selected.id));
 assert.ok(filterAtlas(partial,{facets:{structure:PENDING}}).some(w=>w.id===selected.id));
 base.works[selected.id].structure=['目标驱动'];
 const complete=createAtlas(data,catalogue,base,creators);
 assert.equal(narrativeState(complete,selected),'complete');
 const counts=narrativeCounts(complete);assert.equal(counts.complete+counts.partial+counts.missing,data.works.length);
 delete base.works[selected.id];
 const missing=createAtlas(data,catalogue,base,creators);
 assert.equal(narrativeState(missing,selected),'missing');
 assert.ok(filterAtlas(missing,{cataloguing:'missing'}).some(w=>w.id===selected.id));
});
test('narrative annotations are searched without auto-inferencing topology from play modes',()=>{
 const d=structuredClone(editorial);const w=data.works.find(w=>w.interactionModes.includes('文字输入'));
 delete d.works[w.id];
 const a=createAtlas(data,catalogue,d,creators);
 assert.deepEqual(metadataValues(a,w,'structure'),[]);
 d.works[w.id]={position:'叙事与解谜并重',style:['本测试独有叙事风格'],theme:['寻宝'],structure:['目标驱动']};
 const b=createAtlas(data,catalogue,d,creators);
 assert.deepEqual(filterAtlas(b,{query:'本测试独有叙事风格'}).map(x=>x.id),[w.id]);
 assert.deepEqual(metadataValues(b,w,'structure'),['目标驱动']);
});
