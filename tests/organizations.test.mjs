import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {creatorNodes,worksFor,layoutFamily} from '../relationships-preview.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/organizations.json');
const formal=read('data/entities.json'),credits=read('data/credits.json');
test('every formal entity is reachable from an organization family without identity merging',()=>{
  for(const entity of formal.entities){
    const node=data.nodes.find(n=>n.id===entity.id);assert.equal(node.type,entity.type);
    assert.ok(data.families.some(f=>[f.root,...f.entityIds].includes(entity.id)),entity.id);
  }
  assert.equal(data.nodes.filter(n=>!n.previewOnly).length,formal.entities.length);
  const main=new Set(Object.values(data.works).filter(w=>w.placement==='main').map(w=>w.id));
  for(const node of data.nodes.filter(n=>!n.previewOnly)){
    const direct=new Set(credits.credits.filter(c=>c.entityId===node.id&&main.has(c.workId)).map(c=>c.workId));
    assert.equal(node.stats.main,direct.size,node.id);
    for(const position of ['related','bibliography']){
      const expected=new Set(credits.credits.filter(c=>c.entityId===node.id&&data.works[c.workId].placement===position).map(c=>c.workId));
      assert.equal(node.stats[position],expected.size,node.id+' '+position);
    }
  }
});
test('creation groups exactly match resolved creation credits, not publisher or port development roles',()=>{
  for(const node of data.nodes.filter(n=>!n.previewOnly)){
    const expected=new Set(credits.credits.filter(c=>c.entityId===node.id&&data.creationRoles.includes(c.role)&&!['pendingRole','unresolved','pending'].includes(c.status)).map(c=>c.workId));
    assert.deepEqual(new Set(node.groups.creation.map(r=>r.workId)),expected,node.id);
    for(const group of Object.values(node.groups))for(const r of group){
      assert.ok(data.works[r.workId]);for(const id of r.creditIds)assert.equal(data.credits[id].entityId,node.id);
    }
  }
  const publisher=data.nodes.find(n=>n.id==='entity-microsoft');assert.equal(worksFor(data,publisher,'creation').length,0);
  const originalBrand=data.nodes.find(n=>n.id==='entity-yuzusoft');assert.ok(worksFor(data,originalBrand,'originalBrand').length);assert.equal(worksFor(data,originalBrand).length,0);
});
test('unresolved dossier duties retain their original source and are not promoted by identity relationships',()=>{
  for(const membership of credits.dossierMemberships.filter(m=>m.status==='pendingRole')){
    const dossier=formal.dossiers.find(d=>d.id===membership.dossierId);
    for(const eid of dossier.entityIds){
      const node=data.nodes.find(n=>n.id===eid);
      const record=Object.values(node.groups).flat().find(r=>r.workId===membership.workId);
      assert.ok(record.pendingRefs.some(ref=>ref.dossierId===membership.dossierId&&ref.source===membership.source));
      if(!node.groups.creation.includes(record))assert.ok(node.groups.pending.includes(record));
    }
  }
  const parent=data.nodes.find(n=>n.id==='preview-tencent');assert.equal(worksFor(data,parent).length,0);
});
test('creator browsing supports names and aliases, pending brands, explicit creation-only view and placements',()=>{
  assert.ok(creatorNodes(data,{kind:'all',query:'ゆずソフト'}).some(n=>n.id==='entity-yuzusoft'));
  assert.ok(!creatorNodes(data,{kind:'creators',query:'ゆずソフト'}).some(n=>n.id==='entity-yuzusoft'));
  assert.ok(creatorNodes(data,{kind:'brand',query:'Key'}).some(n=>n.id==='entity-key'));
  const key=data.nodes.find(n=>n.id==='entity-key');assert.equal(worksFor(data,key,'creation','main').length,21);
  for(const row of worksFor(data,key,'creation','related'))assert.equal(data.works[row.workId].placement,'related');
  assert.ok(worksFor(data,key,'creation','main','CLANNAD').length);
});
test('tree counts do not roll brand creation up to operating companies',()=>{
  const key=data.nodes.find(n=>n.id==='entity-key'),va=data.nodes.find(n=>n.id==='entity-visualarts');
  assert.equal(key.productionCount,21);assert.equal(va.productionCount,0);
  const tree=layoutFamily(data,data.families.find(f=>f.id==='visualarts'));assert.equal(tree.nodes.length,3);
});
test('family list and search results sort A to Z, folding accents and leaving nonletters last',async()=>{
  const {sortFamilies,searchFamilies}=await import('../relationships-preview.mjs');
  const input=[{id:'z',title:'Zoo'},{id:'n',title:'5pb.'},{id:'a2',title:'âge'},{id:'b',title:'beta'},{id:'a1',title:'Accolade'}];
  assert.deepEqual(sortFamilies(input).map(f=>f.id),['a1','a2','b','z','n']);
  assert.equal(input[0].id,'z');
  const all=searchFamilies(data,'');assert.equal(all[0].title,'Accolade');assert.equal(all[1].title,'Activision');
  const found=searchFamilies(data,'Addison');assert.deepEqual(found.map(f=>f.title),['Addison-Wesley Productions','Addison-Wesley Publishing Company']);
  assert.ok(searchFamilies(data,'age').some(f=>f.entityIds.includes('entity-name-f0d25e9c6d82')));
});
