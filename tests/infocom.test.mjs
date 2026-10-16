import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {filterCatalogue} from '../filter.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const d=read('data/games.json'),t=read('data/taxonomy.json');
const c=read('data/company-coverage.json').companies.find(c=>c.id==='infocom');
const page=readFileSync(new URL('../infocom.html',import.meta.url),'utf8');

test('Infocom original 52-item scope has 50 unique story identities and two gameplay exclusions',()=>{
  const ids=[...c.workIds,...c.relatedGames.map(w=>w.id),...c.dossierOnlyWorks.map(w=>w.id)];
  assert.equal(ids.length,50);assert.equal(new Set(ids).size,50);
  assert.deepEqual(c.dossierGroups.flatMap(g=>g.workIds).sort(),ids.sort());
  assert.equal((page.match(/<article class="card"/g)||[]).length,50);
  assert.equal(c.dossierGroups.find(g=>g.id==='infocom-classics').workIds.length,35);
  assert.equal(c.dossierGroups.find(g=>g.id==='infocom-comics').workIds.length,4);
  assert.ok(!page.includes('id="g129"')); // 1984 Melbourne House Sherlock is a different work.
  for(const title of ['Fooblitzky','BattleTech: The Crescent Hawks’ Revenge']){
    assert.ok(c.entries.some(e=>e.title===title&&e.status.startsWith('排除')));
    assert.ok(![...d.works,...c.relatedGames,...c.dossierOnlyWorks].some(w=>w.originalTitle===title));
  }
});

test('new parser titles never enter main records, including menu games with free topic input',()=>{
  assert.equal(c.dossierOnlyWorks.length,19);
  for(const w of c.dossierOnlyWorks){
    assert.ok(w.interactionModes.includes('文字输入'));
    for(const collection of [d.works,d.contentVersions,d.platformReleases]){
      assert.ok(!collection.some(x=>(x.workId||x.id)===w.id));
    }
    const card=page.split(`<article class="card" id="${w.id}">`)[1].split('</article>')[0];
    assert.ok(card.includes('仅专题收录'));assert.ok(!card.includes('class="version-panel"'));
  }
  assert.ok(c.dossierOnlyWorks.find(w=>w.id==='infocom-circuits-edge').interactionNote.includes('Talk about'));
  assert.ok(c.dossierOnlyWorks.find(w=>w.id==='infocom-quarterstaff').interactionModes.includes('菜单指令'));
  for(const id of Array.from({length:11},(_,i)=>'g'+(1081+i))){
    const w=d.works.find(w=>w.id===id);assert.ok(w);assert.ok(!w.interactionModes.includes('文字输入'));
    assert.equal(filterCatalogue(d,{query:w.originalTitle,interaction:'文字输入'}).length,0);
  }
});

test('Journey and Infocomics retain the distinction between story choice and viewpoint traversal',()=>{
  assert.ok(d.works.find(w=>w.id==='g1081').interactionModes.includes('菜单指令'));
  assert.ok(t.interactionModes['视角切换'].includes('不据此宣称改变事件或结局'));
  assert.ok(t.subcategories['互动动画'].includes('动画漫画·视角切换'));
  const comics=filterCatalogue(d,{interaction:'视角切换'});
  assert.deepEqual(comics.map(x=>x.work.id).sort(),['g1082','g1083','g1084','g1085']);
  assert.ok(comics.every(x=>!x.work.interactionModes.includes('选项分支')));
});

test('brand associations preserve original identity and real publishers without adding ordinary ports',()=>{
  assert.equal(d.works.find(w=>w.id==='g1086').firstYear,1986);
  assert.ok(filterCatalogue(d,{query:'Tombs & Treasure'}).some(x=>x.work.id==='g1086'));
  assert.deepEqual(d.platformReleases.filter(r=>r.workId==='g1086').map(r=>r.publisher),['Nihon Falcom','Tokyo Shoseki']);
  assert.ok(!d.platformReleases.some(r=>r.workId==='g1086'&&r.year===1991));
  assert.ok(c.workContexts.g1086.includes('1991'));
  assert.equal(c.relatedGames.find(w=>w.id==='infocom-mars-saga').platformReleases[0].publisher,'Electronic Arts');
  for(const id of ['g1090','g1091'])assert.equal(d.platformReleases.find(r=>r.workId===id).publisher,'Activision');
  assert.ok(c.dossierGroups.find(g=>g.id==='infocom-series').cardLabel==='系列延续');
  const additions=d.contentVersions.filter(v=>['g1086','g1088'].includes(v.workId)&&v.basis==='added');
  assert.equal(additions.length,2);
  assert.ok(additions.every(v=>v.comparedTo===v.workId+'-c-original'&&v.addedContent.length));
  assert.equal(d.platformReleases.find(r=>r.workId==='g1087').voice,'有');
});
