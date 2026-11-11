import test from 'node:test';
import assert from 'node:assert/strict';
import {createBasicWebIndex,createHomeSearch,slotPage,withBasicDetails} from '../basic-catalogue-index.mjs';
import {basicFilterRows,matchingBasicPositions} from '../basic-catalogue-filters.mjs';

const legacyIndex=fetcher=>createBasicWebIndex(fetcher,{release:null});
const revision='a'.repeat(40);
const manifest={schema:1,revision,shardSize:2,basic:{total:3},home:{total:3}};
const home=[{title:'甲'},{title:'乙'},{title:'丙'}];
const packed={groups:['甲社','乙社'],gameplay:['ADV'],statuses:['promoted-basic'],rows:[
 ['index-a','a','甲',1980,0,0,0,['Alias'],[1]],['index-b','b','乙',1990,0,0,0],['index-c','c','丙',null,1,0,0]
]};

test('opening and paging the homepage downloads only the needed detail shards',async()=>{
 const requests=[];
 const index=legacyIndex(async path=>{
  requests.push(path);
  const key=path.split('/').at(-1),data={
   'manifest.json':manifest,'home-0.json':home.slice(0,2),'home-1.json':home.slice(2),
   'home-search.json':['甲','乙','丙 alias'],
  }[key];
  return {ok:data!==undefined,json:async()=>data};
 });
 assert.equal((await index.meta()).home.total,3);
 assert.deepEqual([...await index.details('home',slotPage(3,1,2).slots)],[[0,home[0]],[1,home[1]]]);
 assert.deepEqual([...await index.details('home',[1])],[[1,home[1]]]);
 assert.deepEqual(requests.map(p=>p.split('/').at(-1)),['manifest.json','home-0.json']);
 const search=createHomeSearch(index);
 assert.deepEqual(await search('alias',1,2),{total:1,page:1,slots:[2]});
 assert.deepEqual([...await index.details('home',[2])],[[2,home[2]]]);
 assert.equal(requests.filter(path=>path.endsWith('home-search.json')).length,1);
 await assert.rejects(index.details('home',[3]),/已变化/);
});

test('basic filtering works from index values and edited source survives detail hydration',async()=>{
 const requests=[];
 const index=legacyIndex(async path=>{
  requests.push(path);
  const key=path.split('/').at(-1),data={'manifest.json':manifest,'basic-index.json':packed,
   'basic-0.json':[{source:'https://example.org/a'},{}]}[key];
  return {ok:data!==undefined,json:async()=>data};
 });
 const rows=await index.basicRows();
 assert.equal(rows[0].source,undefined);
 assert.ok(requests.every(p=>!p.endsWith('basic-0.json')));
 const entries=rows.map(row=>({...row,_key:row.matchedWorkId}));
 const filters=basicFilterRows(entries,new Map([['a',[{title:'版本旧名'}]]]));
 assert.deepEqual(matchingBasicPositions(filters,{q:'版本旧名',year:'1980',group:'乙社'}),[0]);
 const detail=(await index.details('basic',[0])).get(0);
 assert.equal(withBasicDetails(entries[0],detail,{records:{}}).source,detail.source);
 assert.equal(withBasicDetails({...entries[0],source:''},detail,{records:{a:{values:{}}}}).source,'');
 await assert.rejects(index.basicRows('b'.repeat(40)),/索引版本已更新/);
});


test('merged version metadata remains searchable without creating a separate row',()=>{
 const main={id:'a',_key:'a',title:'King Tut',year:1978,group:'Mad Hatter',gameplay:'ADV',status:'promoted-basic',aliases:[]};
 const version={id:'b',_key:'b',parentId:'a',title:'King Tut - Apple II',year:1979,group:'Another Studio',gameplay:'RPG',status:'identity-review',aliases:['古墓版']};
 const rows=basicFilterRows([main],new Map([['a',[version]]]));
 assert.equal(rows.length,1);
 assert.deepEqual(matchingBasicPositions(rows,{q:'古墓版',year:'1979',group:'another studio',gameplay:'rpg'}),[0]);
 assert.deepEqual(matchingBasicPositions(rows,{q:'apple ii',year:'1979',status:'identity-review'}),[0]);
 assert.deepEqual(matchingBasicPositions(rows,{year:'1977'}),[]);
});
test('advanced metadata is fetched on demand and remains bound to the same release revision',async()=>{
 const requests=[];
 const index=legacyIndex(async path=>{
  requests.push(path.split('/').at(-1));
  const data={'manifest.json':manifest,'basic-index.json':packed,'basic-advanced.json':{1:{series:['series']}}}[requests.at(-1)];
  return {ok:data!==undefined,json:async()=>data};
 });
 await index.basicRows(revision);
 assert.ok(requests.includes('basic-index.json'));
 assert.ok(requests.every(path=>!path.startsWith('basic-advanced.json')));
 assert.deepEqual(await index.advancedRows(revision),{1:{series:['series']}});
 await index.advancedRows(revision);
 assert.equal(requests.filter(path=>path==='basic-advanced.json').length,1);
 await assert.rejects(index.advancedRows('b'.repeat(40)),/索引版本已更新/);
});
