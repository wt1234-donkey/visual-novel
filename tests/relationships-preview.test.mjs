import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {familyEdges,layoutFamily,historiesFor,searchFamilies} from '../relationships-preview.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const data=read('data/relationships-preview.json');
const family=id=>data.families.find(f=>f.id===id);
test('typed ownership, brand family, names and derivation remain separate',()=>{
  assert.ok(familyEdges(data,family('visualarts')).some(e=>e.kind==='parent'&&e.status==='previewReviewed'));
  assert.ok(familyEdges(data,family('alicesoft')).some(e=>e.kind==='family'));
  assert.equal(historiesFor(data,family('microsoft'))[0].oldName,'Microsoft Studios');
  const spin=familyEdges(data,family('silkys')).find(e=>e.kind==='spinOff');
  assert.equal(spin.status,'pending');assert.equal(spin.basis,'previewCandidate');
  assert.equal(familyEdges(data,family('silkys'),false).some(e=>e.kind==='spinOff'),false);
});
test('collapsed nodes and hidden candidates do not reappear as disconnected roots',()=>{
  const collapsed=layoutFamily(data,family('alicesoft'),{collapsed:new Set(['entity-alicesoft'])});
  assert.equal(collapsed.nodes.length,2);
  const hidden=layoutFamily(data,family('silkys'),{showPending:false});
  assert.ok(!hidden.nodes.some(n=>n.id==='entity-silkys_plus'));
  const cyclic={...data,edges:[...data.edges,{id:'cycle',parent:'entity-alice_blue',child:'entity-champion_soft',kind:'family'}]};
  const graph=layoutFamily(cyclic,family('alicesoft'));assert.equal(graph.nodes.length,4);
  assert.equal(new Set(graph.nodes.map(n=>n.id)).size,4);
});
test('search matches explicit old names and aliases without converting them to identity relations',()=>{
  assert.ok(searchFamilies(data,'Novectacle').some(f=>f.id==='novect'));
  assert.ok(searchFamilies(data,'Xbox Game Studios').some(f=>f.id==='microsoft'));
  assert.equal(searchFamilies(data,'不存在的家族').length,0);
  assert.equal(historiesFor(data,family('visualarts')).length,0);
});
test('work totals are direct per-entity counts and preview-only parent receives no inherited credits',()=>{
  const parent=data.nodes.find(n=>n.id==='preview-tencent');assert.equal(parent.productionCount,0);assert.equal(parent.stats.main,0);
  const credits=read('data/credits.json').credits,main=new Set(read('data/games.json').works.map(w=>w.id));
  for(const node of data.nodes.filter(n=>!n.previewOnly)){
    const direct=new Set(credits.filter(c=>c.entityId===node.id&&main.has(c.workId)).map(c=>c.workId));
    assert.equal(node.stats.main,direct.size,node.id);
  }
  const graph=layoutFamily(data,family('nitroplus'));assert.ok(graph.nodes.some(n=>n.id==='entity-nitroplus'));assert.ok(graph.nodes.some(n=>n.id==='entity-nitroplus_brand'));
});
