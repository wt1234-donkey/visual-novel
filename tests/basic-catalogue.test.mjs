import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {emptyStore,applyChange,projectEntries,projectRegistry,valuesOf,validateValues,validateStore,undoLast,parseImport,parseCSV} from '../basic-catalogue-model.mjs';
import {createEditClient} from '../work-edit-api.mjs';
const base=[{id:'a',title:'Original',year:1990,group:'Studio',gameplay:'ADV',source:'https://example.com/a',aliases:['原作']},{id:'b',title:'Remake',year:2000,group:'Studio',gameplay:'ADV',source:'https://example.com/b'},{id:'c',title:'Expanded',year:2005,group:'Other',gameplay:'RPG',source:'https://example.com/c'}];
const change=(s,action)=>applyChange(s,base,action,{id:'r'+s.revision,actor:'test',at:'2026-11-03',reason:'test change',expectedRevision:s.revision});
const merge=(s,mainId,ids)=>change(s,{type:'merge',mainId,ids,relation:{type:'unverified',label:'version',note:'',source:''}});
test('edits update year, title, studio, gameplay and three styles without mutating original evidence',()=>{
 const before=structuredClone(base),s=change(emptyStore(),{type:'edit',id:'a',values:{...valuesOf(base[0]),title:'Corrected',firstYear:1991,group:'Team',gameplay:'Novel',plotStyles:['悬疑','推理','黑暗']}});
 const w=projectEntries(base,s)[0];assert.equal(w.year,1991);assert.equal(w.title,'Corrected');assert.equal(w.group,'Team');assert.deepEqual(w.plotStyles,['悬疑','推理','黑暗']);assert.ok(w.aliases.includes('Original'));assert.deepEqual(base,before);
 assert.throws(()=>validateValues({...valuesOf(base[0]),plotStyles:['a','b','c','d']}),/最多3个/);assert.throws(()=>validateValues({...valuesOf(base[0]),firstYear:0}),/年份/);assert.throws(()=>validateValues({...valuesOf(base[0]),source:'javascript:alert(1)'}),/来源/);
});
test('merge retains source identities, folds child aliases into shared registry and can detach',()=>{
 const s=merge(emptyStore(),'a',['b']);assert.equal(projectEntries(base,s).length,2);const all=projectEntries(base,s,{includeChildren:true});assert.equal(all.find(w=>w.id==='b').source,base[1].source);assert.equal(all.find(w=>w.id==='b').year,2000);
 const registry=projectRegistry({works:base.map(w=>({...w,firstYear:w.year})),summary:{}},s);assert.equal(registry.works.length,2);assert.ok(registry.works[0].aliases.includes('Remake'));assert.ok(!('versions' in registry));
 assert.equal(projectEntries(base,change(s,{type:'detach',id:'b'})).length,3);assert.throws(()=>change(s,{type:'delete',id:'a'}),/关联版本/);
});
test('merge reparents existing children, rejects cycles and requires evidence for confirmed content',()=>{
 let s=merge(emptyStore(),'a',['b']);s=merge(s,'c',['a']);assert.equal(projectEntries(base,s).length,1);assert.ok(projectEntries(base,s,{includeChildren:true}).filter(w=>w.parentId).every(w=>w.parentId==='c'));
 assert.throws(()=>merge(s,'a',['c']),/主作品/);
 assert.throws(()=>change(emptyStore(),{type:'merge',mainId:'a',ids:['b'],relation:{type:'added',label:'Remake'}}),/依据与来源/);
 const malformed=emptyStore();malformed.records={a:{parentId:'b',relation:{type:'unverified',label:'a'}},b:{parentId:'a',relation:{type:'unverified',label:'b'}}};assert.throws(()=>validateStore(malformed),/循环/);
});
test('batch add, delete and merge survive JSON reload and undo atomically over three operations',()=>{
 const original=emptyStore();let s=change(original,{type:'add',works:[{id:'manual-test',...valuesOf(base[0]),title:'New',firstYear:null}]});s=merge(s,'a',['b']);s=change(s,{type:'delete',id:'c'});s=JSON.parse(JSON.stringify(s));assert.equal(projectEntries(base,s).length,2);
 s=undoLast(s,s.revision);assert.equal(projectEntries(base,s).length,3);s=undoLast(s,s.revision);assert.equal(projectEntries(base,s).length,4);s=undoLast(s,s.revision);assert.equal(projectEntries(base,s).length,3);assert.deepEqual(original,emptyStore());assert.equal(s.revision,6);
 assert.throws(()=>applyChange(s,base,{type:'delete',id:'a'},{actor:'x',reason:'x',expectedRevision:0}),/其他页面/);
});
test('fixed CSV template parses BOM, CRLF, quotes, commas, newlines, blank year and max styles',()=>{
 const header='名称,年份,厂商,主要玩法,剧情风格1,剧情风格2,剧情风格3,来源';const rows=parseImport('\uFEFF'+header+'\r\n"A, B",,Team,ADV,悬疑,推理,,https://example.com\r\n','csv');assert.equal(rows[0].title,'A, B');assert.equal(rows[0].firstYear,null);assert.deepEqual(rows[0].plotStyles,['悬疑','推理']);assert.deepEqual(parseCSV('"A""B\nC",x'),[['A"B\nC','x']]);
 assert.throws(()=>parseImport(header+'\na,2000,b,c,x,y,z,https://x\nb,wrong,b,c,,,,','csv'),/第2部.*年份/);assert.throws(()=>parseImport('wrong\nx','csv'),/表头/);assert.throws(()=>parseImport(header+'\n"bad','csv'),/引号/);
});
test('templates validate; invalid or duplicate import rejects the whole batch',()=>{
 for(const ext of ['json','csv'])assert.equal(parseImport(readFileSync(new URL('../templates/basic-works-import.'+ext,import.meta.url),'utf8'),ext).length,1);
 const s=emptyStore();assert.throws(()=>change(s,{type:'add',works:[{id:'manual-first',...valuesOf(base[0]),title:'Unique'},{id:'manual-second',...valuesOf(base[0])}]}),/同名同年/);assert.equal(s.additions.length,0);
 assert.throws(()=>parseImport(JSON.stringify([{...valuesOf(base[0]),plotStyles:['a','b','c','d']}]),'json'),/最多3个/);
});
test('basic API uses its own file and SHA lease; conflicts never report success',async()=>{
 const calls=[];const client=createEditClient('test-only',async(url,options)=>{calls.push({url,options});return {ok:true,json:async()=>({content:{sha:'new'},commit:{sha:'commit'}})};},{historyPath:'data/basic-catalogue-edits.json',validate:validateStore});
 await client.write(emptyStore(),'expected','test');assert.ok(calls[0].url.endsWith('/contents/data/basic-catalogue-edits.json'));assert.equal(JSON.parse(calls[0].options.body).sha,'expected');assert.ok(!JSON.stringify(emptyStore()).includes('test-only'));
 await assert.rejects(()=>createEditClient('test',async()=>({ok:false,status:409}),{historyPath:'data/basic-catalogue-edits.json',validate:validateStore}).write(emptyStore(),'old','test'),/冲突/);
});

test('candidate identities absent from raw registry remain visible when edited or chosen as merge primary',()=>{
 const extended=[...base,{id:'candidate',title:'Held candidate',year:1999,group:'Team',gameplay:'ADV',source:'https://example.com/held',status:'eligibility-review'}];
 const s=applyChange(emptyStore(),extended,{type:'merge',mainId:'candidate',ids:['a'],relation:{type:'unverified',label:'version'}},{actor:'test',reason:'link held candidate',expectedRevision:0});
 const result=projectRegistry({works:base.map(w=>({...w,firstYear:w.year})),summary:{}},s);
 assert.ok(result.works.some(w=>w.id==='candidate'&&w.aliases.includes('Original')));
 assert.ok(!result.works.some(w=>w.id==='a'));
 const actual=JSON.parse(readFileSync(new URL('../data/basic-catalogue-edits.json',import.meta.url),'utf8'));assert.ok(validateStore(actual));
});
