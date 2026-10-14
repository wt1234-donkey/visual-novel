import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import {filterCatalogue,publisherWorkCounts,visibleVoiceNote} from '../filter.mjs';

const data=JSON.parse(readFileSync(new URL('../data/games.json',import.meta.url),'utf8'));

test('SORAHANE three originals preserve names, publisher filters and original years',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='sorahane');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  assert.equal(dossier.workIds.length,3);assert.equal(publisherWorkCounts(data).get('SORAHANE'),3);
  for(const name of ['SORAHANE','ソラハネ','SORAHANE-ソラハネ-','Sorahane'])assert.deepEqual(new Set(filterCatalogue(data,{company:aliases[name]}).map(({work})=>work.id)),new Set(dossier.workIds));
  for(const [query,id] of [['水之羁绊 AQUA','g903'],['樱花已然绽放。','g904'],['遥远彼方','g905']])assert.equal(filterCatalogue(data,{query})[0].work.id,id);
  assert.deepEqual(data.works.filter(w=>dossier.workIds.includes(w.id)).map(w=>w.firstYear),[2011,2012,2014]);
  assert.ok(data.works.find(w=>w.id==='g905').characters.includes('七海かなた'));
});

test('SORAHANE mobile batches preserve actual historical credits and differing voice states',()=>{
  const aqua=filterCatalogue(data,{company:'萌えAPP'}).find(({work})=>work.id==='g903');assert.equal(aqua.versions.length,3);
  for(const [platform,date] of [['Android','2015/04/10'],['Android（Google Play）','2015/08/21'],['iOS','2016/04/28']]){
    const v=aqua.versions.find(v=>v.platform===platform);assert.ok(v.differences.includes(date));assert.equal(v.voice,'有');assert.ok(v.publisher.includes('ハブロッツ'));
  }
  const saku=filterCatalogue(data,{company:'萌えAPP'}).find(({work})=>work.id==='g904');assert.equal(saku.versions.length,1);assert.equal(saku.versions[0].voice,'无');assert.ok(saku.versions[0].publisher.includes('ジャックインザボックス'));assert.ok(saku.versions[0].differences.includes('2013/12/20'));
  assert.equal(data.versions.find(v=>v.workId==='g904'&&v.kind==='Windows日文原版').voice,'有');
  assert.equal(data.versions.filter(v=>v.workId==='g904'&&v.platform==='iOS').length,0);
  assert.equal(filterCatalogue(data,{company:'SORAHANE',platform:'iOS'}).length,0);
});

test('SORAHANE extra stories use the original program and exclude visual patches and plans',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='sorahane');
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,11);
  const stories=data.versions.filter(v=>v.workId==='g904'&&v.kind.startsWith('本体内免费追加'));assert.equal(stories.length,3);
  assert.ok(stories.every(v=>v.voice==='有'&&v.differences.includes('不是独立程序')));
  for(const date of ['2013/06/28','2013/07/19','2013/08/09'])assert.ok(stories.some(v=>v.differences.includes(date)));
  assert.equal(data.works.filter(w=>w.originalTitle==='Dream of Human'||w.originalTitle==='TOKI＊SORA').length,0);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)&&/macOS|Steam/.test(v.platform)).length,0);
  assert.deepEqual(dossier.entries.find(e=>e.title==='SORAKAZE与TOKI＊SORA').workIds,[]);
  const page=readFileSync(new URL('../sorahane.html',import.meta.url),'utf8');for(const id of dossier.workIds)assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="sorahane.html"'));
});

test('HARUKAZE four originals are searchable without replacing actual port publishers',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='harukaze');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  assert.equal(dossier.workIds.length,4);
  for(const name of ['HARUKAZE','HARU❀KAZE','HARU*KAZE','はるかぜ','ハルカゼ']) assert.deepEqual(new Set(filterCatalogue(data,{company:aliases[name]}).map(({work})=>work.id)),new Set(dossier.workIds));
  assert.equal(publisherWorkCounts(data).get('HARUKAZE'),4);
  for(const [query,id] of [['恋爱皇帝 of LOVE!','g899'],['野良与皇女与流浪猫之心2','g901'],['猴子们！','g902']]) assert.equal(filterCatalogue(data,{query})[0].work.id,id);
  for(const [company,platform,date] of [['ENTERGRAM','PlayStation Vita','2017/05/25'],['iMel','Nintendo Switch','2022/03/17']]){
    const row=filterCatalogue(data,{company,platform}).find(({work})=>work.id==='g899');assert.equal(row.versions.length,1);assert.ok(row.versions[0].differences.includes(date));assert.equal(row.work.firstYear,2013);
  }
  for(const company of ['TOKYOTOON','Fruitbat Factory']) for(const id of ['g900','g901']){
    const row=filterCatalogue(data,{company,platform:'Steam'}).find(({work})=>work.id===id);assert.equal(row.versions.length,1);assert.equal(row.versions[0].voice,'有');
  }
});

test('HARUKAZE compilations, VFB and paid stories keep explicit content identities',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='harukaze');
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,26);
  for(const kind of ['1+2パック合集收录','五周年1+2完整套装收录']) assert.deepEqual(new Set(data.versions.filter(v=>v.kind===kind).map(v=>v.workId)),new Set(['g900','g901']));
  const hundred=data.versions.filter(v=>v.kind==='猫的想法100连发付费追加');assert.equal(hundred.length,1);assert.equal(hundred[0].workId,'g900');assert.ok(hundred[0].differences.includes('不能独立启动'));
  const vfb=data.versions.find(v=>v.kind==='VFB附属短篇内容');assert.equal(vfb.year,2016);assert.equal(vfb.voice,'有');assert.ok(vfb.differences.includes('是否无需本体待核'));
  assert.equal(data.works.filter(w=>w.originalTitle.includes('1+2パック')).length,0);
  const noel=data.versions.filter(v=>v.workId==='g901'&&['PlayStation Vita','PlayStation 4','Nintendo Switch'].includes(v.platform));assert.equal(noel.length,3);assert.ok(noel.every(v=>v.year===2019&&v.publisher==='HARUKAZE'&&v.differences.includes('诺艾尔新路线')));
  const page=readFileSync(new URL('../harukaze.html',import.meta.url),'utf8');
  for(const id of dossier.workIds)assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="harukaze.html"'));
});

test('HARUKAZE future Steam and browser devices do not become shipped native versions',()=>{
  const monkeys=data.versions.filter(v=>v.workId==='g902');assert.equal(monkeys.length,3);assert.ok(monkeys.every(v=>v.year===2021));
  assert.equal(monkeys.filter(v=>/Steam|Android|iOS|macOS/.test(v.platform)).length,0);
  const web=monkeys.find(v=>v.platform.startsWith('Web'));assert.equal(web.voice,'未核实');assert.ok(web.differences.includes('2021/10/29'));
  const android=data.versions.filter(v=>v.workId==='g900'&&v.platform==='Android');assert.equal(android.length,1);assert.ok(android[0].differences.includes('2017/03/30'));assert.equal(android[0].voice,'未核实');
  assert.deepEqual(data.works.filter(w=>['g899','g900','g901','g902'].includes(w.id)).map(w=>w.firstYear),[2013,2016,2017,2021]);
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='harukaze');
  const future=dossier.entries.find(e=>e.title==='Monkeys!¡ Steam版与试玩');assert.ok(future.status.includes('未来'));assert.ok(future.reason.includes('2026/11/16'));
  assert.deepEqual(dossier.entries.find(e=>e.title==='ネコのお考え特別編、录音剧与跨游戏联动').workIds,[]);
});

test('HULOTTE brand family and Chinese aliases find the completed catalogue',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='hulotte');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  for(const company of ['HULOTTE','ユロット','HULOTTE ROI']){
    assert.deepEqual(new Set(filterCatalogue(data,{company:aliases[company]||company}).map(({work})=>work.id)),new Set(dossier.workIds));
  }
  assert.equal(dossier.workIds.length,11);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,23);
  assert.equal(filterCatalogue(data,{query:'心之形、色与音'})[0].work.id,'g850');
  assert.equal(data.versions.find(v=>v.workId==='g850').publisher,'HULOTTE ROI');
});

test('HULOTTE international versions preserve actual publisher and language evidence',()=>{
  for(const [query,id,company,year] of [['KamiYaba','g847','Shiravune',2022],['My Klutzy Cupid','g851','NekoNyan Ltd.',2023]]){
    const row=filterCatalogue(data,{query,company})[0];
    assert.equal(row.work.id,id);
    assert.equal(row.versions.length,1);
    assert.equal(row.versions[0].year,year);
    assert.equal(row.versions[0].platform,'Windows（Steam）');
    assert.equal(row.versions[0].voice,'有');
  }
  assert.equal(filterCatalogue(data,{query:'KamiYaba',company:'NekoNyan Ltd.'}).length,0);
  assert.equal(filterCatalogue(data,{query:'My Klutzy Cupid',company:'Shiravune'}).length,0);
});

test('HULOTTE standalone stories differ from patches and compilation entries reuse identities',()=>{
  const base=data.versions.filter(v=>v.workId==='g843');
  assert.equal(base.length,2);
  assert.equal(base.find(v=>v.kind==='四话追加剧情补丁').year,2011);
  const standalone=data.works.find(w=>w.id==='g853');
  assert.equal(standalone.firstYear,2012);
  assert.equal(data.versions.find(v=>v.workId==='g853').kind,'免费独立短篇集');
  assert.equal(data.versions.find(v=>v.workId==='g853').voice,'未核实');
  const pack=data.versions.filter(v=>v.kind==='ヤバいComplete Pack合集收录');
  assert.deepEqual(new Set(pack.map(v=>v.workId)),new Set(['g844','g845','g846','g847']));
  assert.ok(pack.every(v=>v.year===2020));
  assert.equal(data.works.filter(w=>w.originalTitle.includes('ヤバいコンプリートパック')).length,0);
  const page=readFileSync(new URL('../hulotte.html',import.meta.url),'utf8');
  for(let id=843;id<=853;id++) assert.equal(page.split(`<article class="card" id="g${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="hulotte.html"'));
});

test('Nitroplus completion separates shipped platforms, planned releases and publisher credits',()=>{
  const reboot=filterCatalogue(data,{query:'STEINS;GATE RE:BOOT',from:'2026',company:'MAGES.'});
  assert.deepEqual(reboot.map(({work})=>work.id),['g054']);
  assert.deepEqual(new Set(reboot[0].versions.map(v=>v.platform)),new Set(['Nintendo Switch 2','Nintendo Switch','PlayStation 5','PlayStation 4']));
  assert.equal(filterCatalogue(data,{query:'RE:BOOT',from:'2026',platform:'Xbox Series'}).length,0);
  const steam=filterCatalogue(data,{query:'RE:BOOT',from:'2026',company:'Spike Chunsoft'});
  assert.deepEqual(steam.map(({work})=>work.id),['g054']);
  assert.equal(steam[0].versions.length,1);
  assert.equal(steam[0].versions[0].platform,'Windows（Steam）');
  assert.ok(data.versions.filter(v=>v.workId==='g054').every(v=>v.platform!=='PlayStation 4 / Steam'));
  assert.deepEqual(filterCatalogue(data,{query:'機神咆吼デモンベイン'}).map(({work})=>work.id),['g600']);
  assert.deepEqual(filterCatalogue(data,{query:'ROBOTICS;NOTES ELITE',company:'Spike Chunsoft'}).map(({work})=>work.id),['g619']);
  assert.ok(filterCatalogue(data,{query:'咲畑梨深'}).some(({work})=>work.id==='g618'));
  for(const id of ['g603-v1','g608-v1','g610-v1','g611-v2','g621-v1']) assert.equal(data.versions.find(v=>v.id===id).voice,'有');
  for(const id of ['g597-v1','g613-v1','g615-v1']) assert.equal(data.versions.find(v=>v.id===id).voice,'未核实');
});

test('Nitroplus dossier reuses originals and keeps remakes, aliases and actual publishers together',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='nitroplus');
  assert.equal(dossier.workIds.length,48);
  assert.equal(new Set(dossier.workIds).size,48);
  for(const id of ['g054','g162','g163','g169']) assert.ok(dossier.workIds.includes(id));
  for(const [query,id] of [['幻灵：地狱之影','g597'],['Phantom INTEGRATION','g597'],['CHAOS;HEAD NOAH','g618'],['你与她与她之恋。','g614'],['君と彼女と彼女の恋。','g614']]){
    assert.deepEqual(filterCatalogue(data,{query}).map(({work})=>work.id),[id]);
  }
  assert.equal(data.versions.filter(v=>v.workId==='g597').length,8);
  assert.deepEqual(filterCatalogue(data,{query:'Phantom',company:'プリンセスソフト'}).map(({versions})=>versions.map(v=>v.year)),[[2003]]);
  assert.equal(filterCatalogue(data,{query:'ROBOTICS;NOTES',company:'Nitroplus'}).length,0);
  assert.equal(filterCatalogue(data,{query:'ROBOTICS;NOTES',company:'5pb.'}).length,2);
  assert.deepEqual(new Set(dossier.publisherWorkIds),new Set(filterCatalogue(data,{company:'Nitroplus'}).map(({work})=>work.id)));
  assert.equal(data.versions.find(v=>v.id==='g600-v1').voice,'有（部分）');
  assert.equal(data.versions.find(v=>v.workId==='g163'&&v.platform==='Android').publisher,'株式会社エイシス');
  assert.equal(dossier.relatedGames.length,25);
  assert.ok(!data.works.some(w=>w.originalTitle==='機神飛翔デモンベイン'));
  assert.equal(data.works.filter(w=>w.originalTitle.includes('変移空間')).length,1);
  assert.deepEqual(filterCatalogue(data,{query:'缓慢损伤：清扫者'}).map(({work})=>work.id),['g628']);
  assert.deepEqual(filterCatalogue(data,{query:'咎狗の血 True Blood'}).map(({work})=>work.id),['g622']);
  assert.equal(data.versions.filter(v=>v.workId==='g625'&&v.kind.includes('re:code')&&v.platform.includes('Steam')).length,0);
  const page=readFileSync(new URL('../nitroplus.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  const links=[...readFileSync(new URL('../index.html',import.meta.url),'utf8').matchAll(/class="secondary-link" href="[^\"]+\.html">([^<]+)<\/a>/g)];
  assert.equal(links.length,JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.length);
  assert.ok(links.every(([,name])=>name.endsWith('社')));
});

test('historical Japanese JAST and international publishers stay independent',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='jast');
  const old=filterCatalogue(data,{company:'JAST（日本）'});
  assert.deepEqual(new Set(old.map(({work})=>work.id)),new Set(dossier.publisherWorkIds));
  assert.ok(old.every(({work})=>dossier.workIds.includes(work.id)));
  assert.equal(filterCatalogue(data,{query:'SEASON2001',company:'JAST（日本）'}).length,0);
  assert.equal(filterCatalogue(data,{query:'SEASON2001',company:'Purple software'}).length,1);
  const japanese=filterCatalogue(data,{query:'Runaway City',company:'JAST（日本）'})[0];
  const english=filterCatalogue(data,{query:'Runaway City',company:'JAST USA'})[0];
  assert.equal(japanese.work.id,english.work.id);
  assert.ok(japanese.versions.every(v=>v.publisher==='Tiare'));
  assert.ok(english.versions.every(v=>v.publisher==='JAST USA'));
  assert.ok(!old.some(({versions})=>versions.some(v=>v.publisher==='JAST')));
});

test('JAST remakes, collections and non-narrative discs preserve work identity',()=>{
  const original=filterCatalogue(data,{query:'天使们的午后：转校生'})[0];
  assert.deepEqual(filterCatalogue(data,{query:'もんもん学園'}).map(({work})=>work.id),[original.work.id]);
  assert.equal(original.versions.filter(v=>v.kind.startsWith('重制')).length,1);
  assert.equal(filterCatalogue(data,{query:'エロでん'}).length,2);
  assert.equal(data.works.filter(w=>w.originalTitle==='エロでん').length,0);
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='jast');
  assert.ok(dossier.relatedGames.some(w=>w.id==='jast-vanishing'&&w.category==='角色扮演'));
  assert.equal(filterCatalogue(data,{query:'Vanishing Point'}).length,0);
  assert.ok(dossier.entries.some(e=>e.title.includes('SpecialII')&&e.workIds.length===0));
  const page=readFileSync(new URL('../jast.html',import.meta.url),'utf8');
  for(const id of [...dossier.workIds,...dossier.relatedGames.map(w=>w.id)]) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  const pride=filterCatalogue(data,{query:'梦日记：遥远的天空之下'})[0];
  assert.equal(pride.work.firstYear,2000);
  assert.equal(pride.versions[0].publisher,'pride');
  assert.equal(pride.versions[0].voice,'有');
  const upgrade=data.versions.find(v=>v.workId==='g015'&&v.kind==='语音外设对应升级版');
  assert.equal(upgrade.voice,'有（部分）');
  assert.ok(upgrade.differences.includes('另购 JAST SOUND'));
});

test('Chinese titles and alternate spellings find the same work without losing original name search',()=>{
  for(const query of ['白色相簿','白色相簿 2','白色相册','WHITE ALBUM2']){
    assert.ok(filterCatalogue(data,{query}).some(({work})=>work.id==='g039'),query);
  }
  assert.equal(data.works.find(w=>w.id==='g039').chineseTitle,'白色相簿2');
  assert.ok(filterCatalogue(data,{query:'缘之空'}).some(({work})=>work.id==='g419'));
  assert.ok(filterCatalogue(data,{query:'仓野家的双胞胎'}).some(({work})=>work.id==='g410'));
});

test('version label appears only for explicitly unvoiced releases',()=>{
  for(const voice of ['有','有（部分）','有（主角部分）','未核实']){
    assert.equal(visibleVoiceNote({voice}),'');
  }
  assert.equal(visibleVoiceNote({voice:'无'}),'无角色配音');
});

test('Palette chapters, editorial Chinese names, and original spellings stay searchable',()=>{
  const chapter=filterCatalogue(data,{query:'9-nine-雪色雪花雪之痕'});
  assert.deepEqual(chapter.map(({work})=>work.id),['g438']);
  assert.ok(filterCatalogue(data,{query:'9-nine-ゆきいろゆきはなゆきのあと'}).some(({work})=>work.id==='g438'));
  const title=filterCatalogue(data,{query:'偷走我的心：月光狂想曲'})[0].work;
  assert.equal(title.chineseTitleType,'站内编辑译名');
  assert.equal(title.originalTitle,'すてぃーるMyはぁと～Rhapsody of moonlight～');
  assert.equal(publisherWorkCounts(data).get('ぱれっと'),18);
});

test('Silky’s new Chinese names preserve original search and studio credit',()=>{
  const chinese=filterCatalogue(data,{query:'姬骑士安洁莉卡',company:'Silky’s'});
  const original=filterCatalogue(data,{query:'姫騎士アンジェリカ',company:'Silky’s'});
  assert.equal(chinese.length,1);
  assert.equal(original[0].work.id,chinese[0].work.id);
  assert.equal(chinese[0].work.chineseTitleType,'站内编辑译名');
  assert.ok(chinese[0].work.characters.includes('アンジェリカ・ロートシルト'));
  assert.equal(publisherWorkCounts(data).get('Silky’s'),29);
  assert.equal(filterCatalogue(data,{query:'Premium',company:'Silky’s'}).length,0);
});

test('Silky’s audit keeps narrative games and removes command adventures',()=>{
  const ids=filterCatalogue(data,{company:'Silky’s'}).map(({work})=>work.id);
  for(const id of ['g441','g443','g446']) assert.ok(!ids.includes(id));
  for(const id of ['g464','g465','g466','g467']) assert.ok(ids.includes(id));
  assert.ok(filterCatalogue(data,{query:'羽翼翩跹'}).some(({work})=>work.id==='g447'));
  assert.ok(filterCatalogue(data,{query:'清洗四肢'}).some(({work})=>work.id==='g452'));
  const remake=filterCatalogue(data,{query:'野野村',company:'FG REMAKE'});
  assert.equal(remake.length,1);
  assert.ok(remake[0].versions.every(v=>v.year===2025));
});

test('a 1999 PlayStation query selects ToHeart port, not its 1997 Windows original',()=>{
  const result=filterCatalogue(data,{query:'ToHeart',platform:'PlayStation',from:1999,to:1999});
  assert.equal(result.length,1);
  assert.equal(result[0].work.title,'ToHeart');
  assert.deepEqual(result[0].versions.map(v=>v.year),[1999]);
  assert.equal(result[0].versions[0].voice,'有');
  const original=data.versions.find(v=>v.workId===result[0].work.id && v.year===1997);
  assert.equal(original.voice,'无');
});

test('all cross-era interactive animation versions can be filtered independently',()=>{
  const r=filterCatalogue(data,{category:'互动动画',platform:'Nintendo Switch',from:2023,to:2025});
  assert.ok(r.some(({work})=>work.title==='时间少女'));
  assert.ok(r.every(({versions})=>versions.every(v=>v.platform.includes('Nintendo Switch') && v.year>=2023)));
});

test('publisher and main character are independently searchable',()=>{
  assert.ok(filterCatalogue(data,{query:'G-MODE'}).some(({work})=>work.title.includes('鄂霍次克')));
  assert.ok(filterCatalogue(data,{query:'远坂凛'}).some(({work})=>work.title==='Fate/stay night'));
});

test('999 first edition and voiced collection keep separate years and voice states',()=>{
  const original=filterCatalogue(data,{query:'9 小时 9 人 9 扇门',platform:'Nintendo DS',from:2009,to:2009});
  assert.equal(original.length,1);
  assert.deepEqual(original[0].versions.map(v=>v.voice),['无']);
  const collection=filterCatalogue(data,{query:'9 小时 9 人 9 扇门',platform:'Steam',from:2017,to:2017});
  assert.equal(collection.length,1);
  assert.deepEqual(collection[0].versions.map(v=>v.voice),['有']);
});

test('Dōkyūsei original and console remake remain distinct',()=>{
  const original=filterCatalogue(data,{query:'同级生',platform:'PC-9800',from:1992,to:1992});
  const remake=filterCatalogue(data,{query:'同级生',platform:'Nintendo Switch',from:2024,to:2024});
  assert.equal(original[0].versions[0].voice,'无');
  assert.equal(remake[0].versions[0].voice,'有');
});

test('early Wingman versions retain their distinct PC-8801 and FM-7 years',()=>{
  const pc=filterCatalogue(data,{query:'ウイングマン',platform:'PC-8801',from:1984,to:1984});
  const fm=filterCatalogue(data,{query:'ウイングマン',platform:'FM-7',from:1985,to:1985});
  assert.equal(pc.length,1);
  assert.equal(fm.length,1);
  assert.deepEqual(pc[0].versions.map(v=>v.year),[1984]);
  assert.deepEqual(fm[0].versions.map(v=>v.year),[1985]);
});

test('an early PC work and its later console adaptation have separate dates',()=>{
  const pc=filterCatalogue(data,{query:'サラダの国のトマト姫',platform:'PC-8801',from:1984,to:1984});
  const consoleVersion=filterCatalogue(data,{query:'サラダの国のトマト姫',platform:'红白机',from:1988,to:1988});
  assert.equal(pc.length,1);
  assert.equal(consoleVersion.length,1);
  assert.equal(consoleVersion[0].versions[0].kind,'主机改编');
});

test('1970s origins and later commercial edition are separate works',()=>{
  const original=filterCatalogue(data,{query:'Zork (MIT PDP-10 original)',from:1977,to:1977});
  const commercial=filterCatalogue(data,{query:'Zork I: The Great Underground Empire',from:1980,to:1980});
  assert.equal(original.length,1);
  assert.equal(commercial.length,1);
  assert.notEqual(original[0].work.id,commercial[0].work.id);
  assert.deepEqual(original[0].versions.map(v=>v.platform),['PDP-10']);
});

test('identical Mystery House names do not merge two different games',()=>{
  const micro=filterCatalogue(data,{query:'ミステリーハウスⅠ',platform:'MZ-80B',from:1982,to:1982});
  const sierra=filterCatalogue(data,{query:'Mystery House',platform:'PC-8801',from:1983,to:1983});
  assert.equal(micro.length,1);
  assert.equal(sierra.length,1);
  assert.notEqual(micro[0].work.id,sierra[0].work.id);
});

test('Mystery House II uses dated FM-8 and FM-7 releases independently',()=>{
  const fm8=filterCatalogue(data,{query:'ミステリーハウスⅡ',platform:'FM-8',from:1982,to:1982});
  const fm7=filterCatalogue(data,{query:'ミステリーハウスⅡ',platform:'FM-7',from:1983,to:1983});
  assert.equal(fm8.length,1);
  assert.equal(fm7.length,1);
  assert.deepEqual(fm8[0].versions.map(v=>v.year),[1982]);
  assert.deepEqual(fm7[0].versions.map(v=>v.year),[1983]);
});

test('Sherlock separates its 1984 Spectrum and 1985 Commodore releases',()=>{
  const zx=filterCatalogue(data,{query:'Sherlock',platform:'ZX Spectrum',from:1984,to:1984});
  const c64=filterCatalogue(data,{query:'Sherlock',platform:'Commodore 64',from:1985,to:1985});
  assert.deepEqual(zx[0].versions.map(v=>v.year),[1984]);
  assert.deepEqual(c64[0].versions.map(v=>v.year),[1985]);
  assert.equal(filterCatalogue(data,{query:'Sherlock',platform:'Commodore 64',from:1984,to:1984}).length,0);
});

test('shared FM tape is a single version while Alice has a separate original machine',()=>{
  const dorm=filterCatalogue(data,{query:'女子寮パニック',from:1983,to:1983});
  assert.deepEqual(dorm[0].versions.map(v=>v.platform),['FM-8／FM-7']);
  const alice=filterCatalogue(data,{query:'不思議の国のアリス',platform:'PC-8001',from:1984,to:1984});
  assert.deepEqual(alice[0].versions.map(v=>v.publisher),['マイクロキャビン']);
});

test('subcategories select only works within the chosen parent class',()=>{
  const matches=filterCatalogue(data,{category:'互动动画',subcategory:'激光影碟·射击／驾驶'});
  assert.equal(matches.length,4);
  assert.ok(matches.some(({work})=>work.id==='g906'));
  assert.ok(matches.every(({work})=>work.category==='互动动画' && work.subcategory==='激光影碟·射击／驾驶'));
  assert.equal(filterCatalogue(data,{category:'视觉小说',subcategory:'激光影碟·射击／驾驶'}).length,0);
});

test('publisher aliases group versions without replacing their original credit',()=>{
  const matches=filterCatalogue(data,{company:'Enix（艾尼克斯）'});
  assert.ok(matches.some(({work})=>work.title==='波多比亚连续杀人事件'));
  assert.ok(matches.some(({work})=>work.title==='女子宿舍危机'));
  assert.ok(matches.flatMap(({versions})=>versions).some(v=>v.publisher==='エニックス'));
  assert.ok(matches.flatMap(({versions})=>versions).some(v=>v.publisher==='艾尼克斯'));
});

test('joint publisher filtering keeps only credited versions of each work',()=>{
  const matches=filterCatalogue(data,{query:'ToHeart',company:'AQUAPLUS'});
  assert.ok(matches.length>0);
  assert.ok(matches.every(({versions})=>versions.every(v=>v.publisherCompanies.includes('AQUAPLUS'))));
  const original=filterCatalogue(data,{query:'Colossal Cave Adventure',company:'__unattributed__',from:1976,to:1977});
  assert.deepEqual(original[0].versions.map(v=>v.year),[1976,1977]);
});

test('publisher index counts unique games across platforms and credits the actual port publisher',()=>{
  const counts=publisherWorkCounts(data);
  assert.equal(counts.get('Key'),filterCatalogue(data,{company:'Key'}).length);
  assert.ok(data.versions.filter(v=>v.workId==='g148').length>1);
  assert.equal(counts.get('PROTOTYPE'),filterCatalogue(data,{company:'PROTOTYPE'}).length);
  assert.ok(counts.get('PROTOTYPE')>=1);
  assert.equal(counts.get('__unattributed__'),filterCatalogue(data,{company:'__unattributed__'}).length);
});

test('publisher aliases preserve historical credit and count games across platform releases',()=>{
  const historical=filterCatalogue(data,{query:'善人シボウデス',company:'Chunsoft'});
  assert.equal(historical.length,1);
  assert.deepEqual(historical[0].versions.map(v=>v.platform),['Nintendo 3DS','PS Vita']);
  assert.ok(historical[0].versions.every(v=>v.publisher==='CHUNSOFT'));
  assert.equal(filterCatalogue(data,{query:'善人シボウデス',company:'Spike Chunsoft'}).length,0);
  const counts=publisherWorkCounts(data);
  assert.equal(counts.get('Chunsoft'),filterCatalogue(data,{company:'Chunsoft'}).length);
  assert.equal(counts.get('Capcom'),filterCatalogue(data,{company:'Capcom'}).length);
  assert.ok(filterCatalogue(data,{company:'Capcom'}).some(({work})=>work.id==='g049'));
  assert.equal(counts.has('CAPCOM'),false);
  assert.equal(counts.has('CHUNSOFT'),false);
  assert.deepEqual(new Set(filterCatalogue(data,{company:'Konami'}).filter(({work})=>work.originalTitle.startsWith('ときめきメモリアル')).map(({work})=>work.id)),new Set(['g023','g175','g176','g177','g937','g938','g939','g940']));
});

test('Silkys Plus dossier, Chinese searches and original-brand separation',()=>{
  const plus=filterCatalogue(data,{company:'Silky’s Plus'});
  assert.equal(plus.length,14);
  assert.ok(plus.every(({work})=>!['纯文本指令','图文指令'].includes(work.subcategory)));
  for(const [query,id] of [['七色轮回','g468'],['なないろリンカネーション','g468'],['寻蝶者','g473'],['魅魔星奏2','g480'],['莉露卡','g481'],["Silky's Plus",'g481']]) {
    assert.ok(filterCatalogue(data,{query}).some(({work})=>work.id===id),query);
  }
  assert.ok(filterCatalogue(data,{company:'Silky’s'}).every(({work})=>!plus.some(p=>p.work.id===work.id)));
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='silkys_plus');
  assert.deepEqual(new Set(dossier.workIds),new Set(plus.map(p=>p.work.id)));
});

test('Alicesoft batches are searchable in Chinese and retain their Japanese titles',()=>{
  const found=filterCatalogue(data,{company:'Alicesoft'});
  assert.equal(found.length,91);
  for(const [query,id] of [['妻中蜜3','g482'],['妻みぐい3','g482'],['超昂神骑爱克希尔','g486'],['母烂漫','g487'],['夫人的恢复术','g488'],['超昂闪忍遥','g490'],['胸部消失的王国','g491'],['桃色守护者','g492'],['母娘乱馆','g493'],['馋嘴龙','g494'],['どらぺこ','g494'],['魅魔姐妹','g495'],['しまいま','g495'],['贪婪的仙人掌','g496'],['双教师同居生活','g497'],['だぶる先生','g497']]){
    assert.ok(filterCatalogue(data,{query}).some(({work})=>work.id===id),query);
  }
  assert.ok(found.some(({work})=>work.subcategory==='图文指令'));
  assert.equal(visibleVoiceNote(data.versions.find(v=>v.id==='g501-v1')),'无角色配音');
  assert.equal(visibleVoiceNote(data.versions.find(v=>v.id==='g501-v2')),'');
  assert.equal(visibleVoiceNote(data.versions.find(v=>v.id==='g499-v1')),'');
  for (const [query,id] of [['Atlach-Nacha','g498'],['迪亚波利卡','g499'],['海之青','g500'],['妻中蜜','g501'],['超昂天使','g502'],['妻中蜜2','g503'],['雪尔·克莱尔','g504'],['魔女的赎罪','g505'],['妻榨','g506'],['只有我的保健室','g507'],['巫女的圣域','g508']]) {
    assert.ok(filterCatalogue(data,{query,company:'Alicesoft'}).some(({work})=>work.id===id),query);
  }
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='alicesoft');
  assert.deepEqual(new Set(dossier.publisherWorkIds),new Set(found.map(({work})=>work.id)));
  const predecessorIds = new Set(data.versions.filter(v=>v.publisherCompanies.includes('チャンピオンソフト')).map(v=>v.workId));
  assert.equal(predecessorIds.size,30);
  assert.equal(dossier.workIds.length,126);
  assert.ok([...predecessorIds].every(id=>dossier.workIds.includes(id)));
  assert.equal(dossier.workIds.length,new Set(dossier.workIds).size);
});

test('Alicesoft narrative migration has one searchable record per work and keeps old dossier links',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='alicesoft');
  const anchors=Object.entries(dossier.legacyAnchors);
  const movedIds=new Set(anchors.map(([,id])=>id));
  const page=readFileSync(new URL('../alicesoft.html',import.meta.url),'utf8');
  assert.equal(anchors.length,88);
  assert.equal(movedIds.size,88);
  assert.equal(data.versions.filter(v=>movedIds.has(v.workId)).length,186);
  for(const [oldId,id] of anchors){
    const records=data.works.filter(w=>w.id===id);
    assert.equal(records.length,1,id);
    assert.ok(dossier.workIds.includes(id));
    assert.ok(!dossier.relatedGames.some(w=>w.id===oldId));
    assert.equal(page.split(`id="${oldId}"`).length-1,1,oldId);
    assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1,id);
    const work=records[0];
    for(const query of [work.originalTitle,work.chineseTitle,...work.titleAliases]){
      assert.equal(filterCatalogue(data,{query}).filter(({work:w})=>w.id===id).length,1,query);
    }
  }
  assert.ok(!dossier.relatedGames.some(w=>w.category==='叙事／养成冒险'));
  for(const [query,subcategory] of [['Little PRINCESS','图文指令'],['Intruder','图文指令'],['守护神大人','恋爱模拟']]){
    assert.ok(filterCatalogue(data,{query,subcategory}).some(({work})=>movedIds.has(work.id)),query);
  }
});

test('OVERDRIVE separates independent stories from enhanced releases and original publishers',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='overdrive');
  assert.equal(dossier.workIds.length,11);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,31);
  for(const [query,id] of [['超電激ストライカー','g646'],['煌煌舞台：谢幕','g643'],['Cross the Future','g648'],['Go! Go! Nippon! 2016','g647'],['OVERDRIVE EDITION','g650']]){
    assert.deepEqual(filterCatalogue(data,{query}).map(({work})=>work.id),[id]);
  }
  assert.equal(data.works.find(w=>w.id==='g650').firstYear,2001);
  assert.equal(data.versions.find(v=>v.id==='g650-v1').publisher,'GROOVER');
  assert.equal(data.versions.find(v=>v.id==='g650-v2').publisher,'OVERDRIVE');
  assert.equal(filterCatalogue(data,{query:'Go! Go! Nippon!',company:'OVERDRIVE'}).length,0);
  assert.equal(dossier.publisherWorkIds.length,10);
  assert.equal(data.versions.find(v=>v.id==='g647-v3').voice,'无');
  const page=readFileSync(new URL('../overdrive.html',import.meta.url),'utf8');
  for(const id of dossier.workIds){
    assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
    assert.ok(!['纯文本指令','图文指令'].includes(data.works.find(w=>w.id===id).subcategory));
  }
});


test('Cocktail Soft menu games, remasters and publisher credits remain distinct',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='cocktailsoft');
  assert.ok(dossier);
  const primo=filterCatalogue(data,{query:'Can Can Bunny Primo'});
  assert.equal(primo.length,1);
  assert.equal(primo[0].work.firstYear,1989);
  assert.ok(primo[0].versions.some(v=>v.year===1997 && v.kind==='重制'));
  assert.ok(!primo[0].versions.some(v=>v.platform==='MSX2'));
  const premiere=data.works.find(w=>w.originalTitle==='きゃんきゃんバニープルミエール');
  assert.ok(!data.versions.some(v=>v.workId===premiere.id && v.platform==='MSX2'));
  const chat=filterCatalogue(data,{query:'CHATのススメ'});
  assert.equal(chat.length,1);
  assert.equal(chat[0].work.subcategory,'图文选项／调查');
  assert.ok(chat[0].work.notes.includes('图标组合'));
  const se=filterCatalogue(data,{query:'Pia♥キャロットへようこそ!!G.O.SE'});
  assert.equal(se.length,1);
  assert.equal(se[0].work.firstYear,2006);
  assert.ok(se[0].versions.some(v=>v.year===2008 && v.kind==='增强版'));
  const pia22=filterCatalogue(data,{query:'Pia♥キャロットへようこそ!!2.2'});
  assert.equal(pia22.length,1);
  assert.equal(filterCatalogue(data,{query:'Pia♥キャロットへようこそ!!2.2',company:'Cocktail Soft'}).length,0);
  assert.deepEqual(new Set(dossier.publisherWorkIds),new Set(filterCatalogue(data,{company:'Cocktail Soft'}).map(({work})=>work.id)));
  const petit=filterCatalogue(data,{query:'ぴあきゃろPetitBox'});
  assert.equal(petit.length,1);
  assert.equal(petit[0].work.firstYear,2017);
  assert.ok(dossier.relatedGames.some(g=>g.originalTitle==='プリンセスメモリー'));
  assert.ok(!data.works.some(w=>w.originalTitle==='プリンセスメモリー・トゥルータイピング'));
  const page=readFileSync(new URL('../cocktailsoft.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
});

test('Macadamia icon and action works retain platform credit and exclude typed commands',()=>{
  const coverage=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8'));
  const dossier=coverage.companies.find(c=>c.id==='macadamia');
  const macadam=filterCatalogue(data,{query:'二人爱戏'});
  assert.equal(macadam.length,1);
  for(const query of ['マカダム','Macadam - Futari Yogari']){
    assert.deepEqual(filterCatalogue(data,{query}).map(({work})=>work.id),[macadam[0].work.id]);
  }
  const parent=filterCatalogue(data,{query:'二人爱戏',company:'dB-SOFT'});
  const brand=filterCatalogue(data,{query:'二人爱戏',company:'Macadamia Soft'});
  assert.deepEqual(parent[0].versions.map(v=>v.platform),['PC-88']);
  assert.deepEqual(brand[0].versions.map(v=>v.platform),['PC-98']);
  const game177=filterCatalogue(data,{query:'１７７',company:'Macadamia Soft'});
  assert.equal(game177.length,1);
  assert.deepEqual(new Set(game177[0].versions.map(v=>v.platform)),new Set(['PC-88','PC-98','X1']));
  assert.ok(game177[0].work.genre.includes('动作'));
  assert.ok(!macadam[0].versions.some(v=>v.platform==='MZ-2500'));
  assert.ok(dossier.entries.some(e=>e.title.includes('MZ-2500')&&e.reason.includes('年份')));
  assert.ok(dossier.entries.some(e=>e.title.includes('Don Juan')&&e.workIds.length===0&&e.status.includes('排除')));
  assert.ok(!data.works.some(w=>w.originalTitle==='ドンファン'));
  assert.deepEqual(new Set(dossier.publisherWorkIds),new Set(filterCatalogue(data,{company:'Macadamia Soft'}).map(({work})=>work.id)));
  const page=readFileSync(new URL('../macadamia.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
});


test('FairyTale keeps menu adventures, credited ports and separate playable volumes',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='fairytale');
  const saori=filterCatalogue(data,{query:'沙织'})[0];
  assert.equal(saori.work.originalTitle,'沙織 -美少女達の館-');
  assert.equal(saori.work.subcategory,'图文选项／调查');
  assert.ok(saori.versions.some(v=>v.platform==='X68000'&&v.year===1991));
  assert.ok(dossier.workIds.includes('g690'));
  assert.equal(data.works.filter(w=>w.originalTitle==='きゃんきゃんバニー').length,1);
  const natural=filterCatalogue(data,{query:'ナチュラル２デュオ～桜色の季節～',company:'KADOKAWA'})[0];
  assert.equal(natural.work.originalTitle,'Natural2 -DUO-');
  assert.equal(natural.versions[0].platform,'PlayStation 2');
  assert.ok(!natural.versions.some(v=>v.publisherCompanies.includes('フェアリーテール')));
  assert.equal(data.works.filter(w=>w.originalTitle.startsWith('セーラー服美少女図鑑 其の')).length,6);
  assert.equal(data.works.filter(w=>w.originalTitle.startsWith('校内写生')).length,3);
  assert.ok(dossier.relatedGames.some(w=>w.originalTitle==='MOON GATE'&&w.category==='策略游戏'));
  assert.ok(dossier.entries.some(e=>e.title.includes('リップスティックV2')&&e.workIds.length===0&&e.reason.includes('缺少')));
  assert.ok(dossier.entries.some(e=>e.title.includes('ほっとMILK')&&e.workIds.length===1));
  assert.ok(dossier.workIds.every(id=>!['纯文本指令','图文指令'].includes(data.works.find(w=>w.id===id).subcategory)));
  const page=readFileSync(new URL('../fairytale.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
});


test('GAINA remains an independent empty dossier without invented game credits',()=>{
  const coverage=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8'));
  const company=coverage.companies.find(c=>c.id==='gaina');
  assert.deepEqual(company.workIds,[]);
  assert.deepEqual(company.relatedGames,[]);
  assert.ok(company.publisherNote.includes('BENTEN Film'));
  assert.equal(filterCatalogue(data,{company:'GAINA'}).length,0);
  const page=readFileSync(new URL('../gaina.html',import.meta.url),'utf8');
  assert.ok(page.includes('暂未找到可确认'));
  assert.ok(page.includes('<strong>—</strong>'));
  assert.ok(!page.includes('class="card"'));
  assert.ok(!/undefined|NaN|Infinity/.test(page));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="gaina.html"'));
});

test('GAINAX collaboration dossiers retain actual publisher filtering',()=>{
  const gainax=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='gainax');
  assert.deepEqual(new Set(filterCatalogue(data,{company:'GAINAX'}).map(({work})=>work.id)),new Set(gainax.publisherWorkIds));
  const dream=filterCatalogue(data,{query:'仲夏夜之梦',company:'TinMachine'});
  assert.equal(dream.length,1);
  assert.equal(dream[0].work.firstYear,2005);
  assert.equal(filterCatalogue(data,{query:'仲夏夜之梦',company:'GAINAX'}).length,0);
  const steel=filterCatalogue(data,{query:'Girlfriend of Steel',platform:'PSP',company:'CyberFront'});
  assert.equal(steel.length,2);
  const second=filterCatalogue(data,{query:'钢铁女友2nd',platform:'PlayStation 2',company:'BROCCOLI'});
  assert.equal(second.length,1);
  assert.equal(second[0].versions[0].year,2005);
  assert.equal(filterCatalogue(data,{query:'钢铁女友2nd',platform:'PlayStation 2',company:'GAINAX'}).length,0);
});

test('GAINAX enhanced editions and Nadia mobile chapters preserve work identity',()=>{
  for(const [query,id] of [['MIGHTYバトルスキンパニック','g812'],['鋼鉄のガールフレンド 特別編','g815'],['Princess Maker Refine','g820'],['綾波育成計画 with アスカ補完計画','g825']]){
    assert.deepEqual(filterCatalogue(data,{query}).map(({work})=>work.id),[id]);
  }
  const nadia=filterCatalogue(data,{query:'蓝宝石之谜',company:'TinMachine'});
  assert.equal(nadia.length,1);
  assert.equal(nadia[0].work.firstYear,1992);
  assert.equal(nadia[0].versions.length,3);
  assert.ok(nadia[0].versions.every(v=>v.year===2006&&v.kind.startsWith('分割移植')));
  const three=filterCatalogue(data,{query:'Princess Maker 3',platform:'Windows',from:1997,to:1997});
  assert.equal(three.length,0);
  assert.equal(filterCatalogue(data,{query:'Princess Maker 3',platform:'Windows',from:1998,to:1998}).length,1);
  const five=filterCatalogue(data,{query:'Princess Maker 5',platform:'PSP'})[0];
  assert.equal(five.versions[0].year,2008);
});

test('GAINAX related games have explicit non-VN categories and unique page anchors',()=>{
  const gainax=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='gainax');
  const page=readFileSync(new URL('../gainax.html',import.meta.url),'utf8');
  for(const id of [...gainax.workIds,...gainax.relatedGames.map(w=>w.id)]) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  for(const related of gainax.relatedGames){
    assert.ok(!data.works.some(w=>w.id===related.id));
    assert.ok(!['文字冒险','视觉小说','互动动画','Galgame'].includes(related.category));
  }
  assert.ok(gainax.entries.some(e=>e.status==='跨类型后续补查'));
});

test('Japan Home Video filtering preserves other publishers and original release years',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='jhv');
  const published=filterCatalogue(data,{company:'Japan Home Video'});
  assert.deepEqual(new Set(published.map(({work})=>work.id)),new Set(dossier.publisherWorkIds));
  assert.equal(published.length,5);
  assert.equal(publisherWorkCounts(data).get('Japan Home Video'),5);
  const cross=filterCatalogue(data,{query:'Crossworld',company:'Japan Home Video'})[0];
  assert.equal(cross.work.firstYear,1996);
  assert.deepEqual(cross.versions.map(v=>[v.year,v.platform]),[[1997,'Windows']]);
  assert.equal(filterCatalogue(data,{query:'Crossworld',platform:'PlayStation',company:'Japan Home Video'}).length,0);
  const fx=filterCatalogue(data,{query:'Neo Generation',platform:'PC-FX',company:'NEC Home Electronics'});
  assert.equal(fx.length,1);
  assert.equal(filterCatalogue(data,{query:'Neo Generation',platform:'PC-FX',company:'Riverhill Soft'}).length,0);
  assert.equal(filterCatalogue(data,{query:'Graduation',company:'IRIコマース&テクノロジー'}).length,2);
});

test('JHV enhanced names, English localization and compilation reuse original works',()=>{
  for(const [query,id] of [['卒業FINAL','g830'],['卒業S','g830'],["卒業 '93",'g830'],['卒業II FX','g831'],['Graduation for Windows 95','g831'],['生于M15行星','g833']]){
    assert.deepEqual(filterCatalogue(data,{query}).map(({work})=>work.id),[id]);
  }
  for(const id of ['g830','g831']){
    assert.equal(data.versions.filter(v=>v.workId===id).length,9);
    const reprint=data.versions.filter(v=>v.workId===id&&v.kind==='卒業復刻版合集收录');
    assert.equal(reprint.length,1);
    assert.equal(reprint[0].year,2004);
    assert.deepEqual(reprint[0].publisherCompanies,['IRIコマース&テクノロジー']);
  }
  assert.equal(data.works.filter(w=>w.originalTitle==='卒業復刻版').length,0);
  const urm=filterCatalogue(data,{query:'URM M15'})[0];
  assert.equal(urm.work.firstYear,1994);
  assert.equal(urm.versions.filter(v=>v.platform==='FM TOWNS').length,1);
  assert.ok(urm.versions.find(v=>v.platform==='FM TOWNS').differences.includes('1995/01/27'));
});

test('JHV separates cross genres, pending evidence and unrelated same-IP titles',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='jhv');
  assert.equal(dossier.relatedGames.length,4);
  assert.equal(dossier.relatedGames.flatMap(w=>w.versions).length,8);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,25);
  for(const related of dossier.relatedGames){
    assert.ok(!data.works.some(w=>w.id===related.id));
    assert.ok(!['文字冒险','视觉小说','互动动画','Galgame'].includes(related.category));
  }
  const pending=dossier.entries.find(e=>e.title==='Sensual Angels');
  assert.deepEqual(pending.workIds,[]);
  assert.deepEqual(pending.relatedIds,[]);
  assert.ok(pending.status.includes('待核'));
  const star=dossier.relatedGames.find(w=>w.id==='jhv-star2');
  assert.equal(star.firstYear,1993);
  assert.equal(star.versions.find(v=>v.year===1993).publisher,'Arsys Software');
  assert.equal(star.versions.filter(v=>v.publisher==='JHV').length,2);
  const page=readFileSync(new URL('../jhv.html',import.meta.url),'utf8');
  for(const id of [...dossier.workIds,...dossier.relatedGames.map(w=>w.id)]) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));
});

test('Cabbage Soft original catalogue and localized versions retain publisher credits',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='cabbage');
  const originals=filterCatalogue(data,{company:'きゃべつそふと'});
  assert.deepEqual(new Set(originals.map(({work})=>work.id)),new Set(dossier.workIds));
  assert.equal(originals.length,8);
  const grace=filterCatalogue(data,{query:'奇异恩典',company:'Shiravune'})[0];
  assert.equal(grace.work.id,'g836');
  assert.equal(grace.versions.length,1);
  assert.equal(grace.versions[0].year,2024);
  assert.equal(filterCatalogue(data,{query:'奇异恩典',company:'Sekai Project'}).length,0);
  for(const [query,id,year] of [['巧克甜恋','g837',2020],['巧克甜恋2','g839',2023],['巧克甜恋3','g841',2025]]){
    const row=filterCatalogue(data,{query,company:'Sekai Project'}).find(({work})=>work.id===id);
    assert.equal(row.versions.length,1);
    assert.equal(row.versions[0].year,year);
    assert.equal(row.versions[0].platform,'Windows（Steam）');
  }
});

test('Cabbage console publisher transitions and compilations reuse work identity',()=>{
  for(const [id,firstYear,portYear] of [['g838',2020,2021],['g840',2022,2024]]){
    assert.equal(data.works.find(w=>w.id===id).firstYear,firstYear);
    const credited=data.versions.filter(v=>v.workId===id);
    assert.deepEqual(credited.filter(v=>v.kind==='主机移植').map(v=>[v.year,v.publisher]),[[portYear,'ENTERGRAM'],[portYear,'ENTERGRAM']]);
    const moved=credited.filter(v=>v.kind==='下载版销售移行');
    assert.equal(moved.length,2);
    assert.ok(moved.every(v=>v.year===2025&&v.publisher==='HuneX'));
    assert.deepEqual(new Set(moved.map(v=>v.platform)),new Set(['PlayStation 4','Nintendo Switch']));
    const pack=credited.filter(v=>v.kind==='双作包合集收录');
    assert.equal(pack.length,1);
    assert.equal(pack[0].platform,'Nintendo Switch');
    assert.equal(pack[0].year,2024);
  }
  const hune=filterCatalogue(data,{query:'宝石心学院',company:'HuneX'})[0];
  assert.equal(hune.work.id,'g840');
  assert.equal(hune.versions.length,2);
  for(const id of ['g837','g839','g841']) assert.equal(data.versions.filter(v=>v.workId===id&&v.kind==='1・2・3 Complete Pack合集收录').length,1);
  assert.equal(data.works.filter(w=>w.originalTitle.includes('Complete Pack')).length,0);
});

test('Cabbage future releases and music remain outside shipped version counts',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='cabbage');
  const shipped=data.versions.filter(v=>dossier.workIds.includes(v.workId));
  assert.equal(shipped.length,29);
  assert.ok(shipped.every(v=>v.year<2026));
  assert.equal(shipped.filter(v=>v.workId==='g840'&&v.platform==='Windows（Steam）').length,0);
  assert.equal(shipped.filter(v=>['g839','g841'].includes(v.workId)&&v.platform==='Nintendo Switch').length,0);
  const music=dossier.entries.find(e=>e.title==='きゃべつそふと Consumer Collection');
  assert.deepEqual(music.workIds,[]);
  assert.ok(music.status.includes('音乐'));
  const page=readFileSync(new URL('../cabbage.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="cabbage.html"'));
  assert.ok(!/undefined|NaN|Infinity/.test(page));
});

test('Laplacian catalogue preserves original and international publisher filters',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='laplacian');
  assert.deepEqual(new Set(filterCatalogue(data,{company:'Laplacian'}).map(({work})=>work.id)),new Set(dossier.workIds));
  assert.equal(dossier.workIds.length,8);
  for(const [query,id,company,count] of [['牛顿与苹果树','g855','Sol Press',3],['牛顿与苹果树','g855','Syawase Works China',1],['未来广播与人工鸽','g856','HIKARI FIELD',1],['工口伦子','g857','JAST USA',1]]){
    const row=filterCatalogue(data,{query,company})[0];
    assert.equal(row.work.id,id);assert.equal(row.versions.length,count);
  }
  assert.equal(filterCatalogue(data,{query:'花坂结衣',company:'Laplacian'})[0].work.id,'g859');
  assert.equal(filterCatalogue(data,{query:'花坂结衣',company:'株式会社さかさうま工房'}).length,0);
});

test('Laplacian DLC and regional releases retain work identity',()=>{
  const rows=data.versions.filter(v=>v.workId==='g855');
  assert.equal(rows.length,5);
  assert.equal(rows.filter(v=>v.kind.includes('内容恢复DLC')).length,2);
  assert.equal(data.works.filter(w=>w.title.includes('内容恢复DLC')).length,0);
  const white=data.versions.filter(v=>v.workId==='g858'&&v.platform==='Nintendo Switch');
  assert.equal(white.length,3);
  assert.deepEqual(white.map(v=>v.year),[2022,2026,2026]);
  assert.ok(white[1].differences.includes('2026/03/12'));
  assert.ok(white[2].differences.includes('2026/03/19'));
  assert.equal(data.works.find(w=>w.id==='g858').firstYear,2020);
  assert.equal(filterCatalogue(data,{query:'Harmonic Reflections'})[0].work.id,'g860');
});

test('Laplacian pending projects and non-game media stay outside shipped counts',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='laplacian');
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,20);
  for(const title of ['MONOCHROME SERENADE','アイソメリカ']){
    assert.deepEqual(dossier.entries.find(e=>e.title===title).workIds,[]);
    assert.equal(data.works.filter(w=>w.title===title).length,0);
  }
  assert.ok(dossier.entries.find(e=>e.title==='MONOCHROME SERENADE').reason.includes('2027'));
  assert.equal(data.works.filter(w=>w.title==='ラビとラビとのガッタイ作戦').length,0);
  const page=readFileSync(new URL('../laplacian.html',import.meta.url),'utf8');
  for(const id of dossier.workIds)assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));
});

test('Applique main brand, sister brand and port publishers remain distinct',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='applique');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  assert.equal(dossier.workIds.length,13);
  for(const name of ['あっぷりけ','Applique','APPLIQUE']) assert.deepEqual(new Set(filterCatalogue(data,{company:aliases[name]||name}).map(({work})=>work.id)),new Set(dossier.publisherWorkIds));
  assert.deepEqual(new Set(filterCatalogue(data,{company:'あっぷりけ-妹-'}).map(({work})=>work.id)),new Set(['g871','g872','g873','g874']));
  assert.equal(publisherWorkCounts(data).get('あっぷりけ'),9);
  for(const [company,platform,year] of [['萌えAPP','Android',2011],['CyberFront','PSP',2013]]){
    const row=filterCatalogue(data,{query:'妹药',company,platform})[0];
    assert.equal(row.work.id,'g864');assert.equal(row.work.firstYear,2010);
    assert.equal(row.versions.length,1);assert.equal(row.versions[0].year,year);
  }
  for(const id of ['g867','g869','g870']){
    const row=filterCatalogue(data,{company:'HIKARI FIELD',platform:'Steam'}).find(({work})=>work.id===id);
    assert.equal(row.versions.length,1);assert.equal(row.versions[0].voice,'有');
  }
  assert.equal(filterCatalogue(data,{query:'编织时间的约定',company:'HIKARI FIELD'}).length,0);
});

test('Applique free LVN, expansion and compilations retain original work identity',()=>{
  for(const query of ['月影魅像-解放之羽-','月影のシミュラクル -解放の羽-']){
    const row=filterCatalogue(data,{query}).find(({work})=>work.id==='g869');assert.ok(row);assert.equal(row.work.firstYear,2016);
  }
  assert.equal(data.versions.filter(v=>v.workId==='g869'&&v.year===2016).length,2);
  assert.equal(data.versions.filter(v=>v.workId==='g869'&&v.kind==='解放の羽扩充版')[0].year,2017);
  for(const [kind,ids] of [['あっぷりけコレクション合集收录',['g862','g863','g864']],['あっぷりけコレクション2合集收录',['g867','g868','g869']]]) assert.deepEqual(new Set(data.versions.filter(v=>v.kind===kind).map(v=>v.workId)),new Set(ids));
  assert.equal(data.works.filter(w=>w.originalTitle.startsWith('あっぷりけコレクション')).length,0);
  assert.equal(filterCatalogue(data,{query:'Fake Azure Arcology'})[0].work.id,'g872');
  assert.equal(filterCatalogue(data,{query:'Rebirth colony'})[0].work.id,'g865');
  const cross=data.versions.filter(v=>v.workId==='g870');
  assert.equal(cross.length,3);assert.ok(cross.find(v=>v.kind==='众筹回报实体版').differences.includes('2019/09/27'));
  assert.ok(cross.find(v=>v.kind==='Windows日文原版').differences.includes('2019/10/25'));
});

test('Applique dossier includes the narrative Fan Disc and explicit pending evidence',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='applique');
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,29);
  const fd=data.works.find(w=>w.id==='g866');assert.ok(fd.notes.includes('麻将为可关闭'));
  assert.equal(data.works.filter(w=>w.originalTitle==='Wish After').length,0);
  assert.ok(dossier.entries.find(e=>e.title==='Cross众筹下载与Append').status.includes('待核'));
  assert.equal(data.versions.filter(v=>['g867','g870'].includes(v.workId)&&v.year===2026).length,0);
  const page=readFileSync(new URL('../applique.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="applique.html"'));
});

test('Clochette aliases and Chinese titles find its ten independent works',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='clochette');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  assert.equal(dossier.workIds.length,10);
  for(const name of ['Clochette','クロシェット','CLOCHETTE']) assert.deepEqual(new Set(filterCatalogue(data,{company:aliases[name]}).map(({work})=>work.id)),new Set(dossier.workIds));
  assert.equal(publisherWorkCounts(data).get('Clochette'),10);
  for(const [query,id] of [['铃音七重奏！甜蜜恋人协奏曲','g877'],['在天津御空之中','g878'],['Kokonatsu','g882'],['心音＝钟摆！','g884']]) assert.equal(filterCatalogue(data,{query})[0].work.id,id);
});

test('Clochette enhanced ports retain original identity and actual publishers',()=>{
  for(const [id,company,platform,year] of [['g876','Alchemist','PlayStation 2',2010],['g876','Alchemist','PSP',2014],['g878','PROTOTYPE','PSP',2012],['g878','PROTOTYPE','PlayStation Vita',2015]]){
    const row=filterCatalogue(data,{company,platform}).find(({work})=>work.id===id);
    assert.ok(row);assert.equal(row.versions.length,1);assert.equal(row.versions[0].year,year);assert.equal(row.versions[0].voice,'有');
  }
  assert.equal(filterCatalogue(data,{query:'Suzunone Seven!',company:'PROTOTYPE'}).length,0);
  assert.equal(filterCatalogue(data,{query:'Amatsumi Sora ni!',company:'Alchemist'}).length,0);
  assert.equal(data.works.filter(w=>w.originalTitle.includes('Rebirth knot')).length,0);
  assert.equal(data.versions.filter(v=>v.workId==='g877').length,1);
  assert.ok(data.works.find(w=>w.id==='g877').notes.includes('八组故事'));
});

test('Clochette dossier distinguishes downloads, in-fiction games and non-game media',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='clochette');
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,17);
  for(const [id,year] of [['g882',2018],['g883',2018],['g884',2019]]){
    const rows=data.versions.filter(v=>v.workId===id);assert.equal(rows.length,2);assert.equal(rows[1].year,year);
  }
  assert.ok(data.works.find(w=>w.id==='g881').notes.includes('剧情内'));
  assert.equal(data.works.filter(w=>w.originalTitle==='Wizard Generation').length,0);
  assert.deepEqual(dossier.entries.find(e=>e.title==='ASMR、漫画、音乐与游戏联动').workIds,[]);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)&&v.year===2026).length,0);
  const page=readFileSync(new URL('../clochette.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="clochette.html"'));
});

test('NanaWind dossier keeps its ten releases and four Luna System collaborations distinct',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='nanawind');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  assert.equal(dossier.workIds.length,14);
  assert.equal(publisherWorkCounts(data).get('NanaWind'),10);
  for(const name of ['NanaWind','ナナウィンド','七风社']) assert.deepEqual(new Set(filterCatalogue(data,{company:aliases[name]}).map(({work})=>work.id)),new Set(dossier.publisherWorkIds));
  assert.deepEqual(new Set(filterCatalogue(data,{company:'Luna System'}).map(({work})=>work.id)),new Set(['g895','g896','g897','g898']));
  assert.equal(filterCatalogue(data,{query:'草津',company:'NanaWind'}).length,0);
  assert.equal(filterCatalogue(data,{query:'草津',company:'Luna System'})[0].work.id,'g898');
  for(const [id,cn] of [['g886','爱丽娅的明日盛典！'],['g888','春音爱丽丝＊篇章'],['g893','花钟奏鸣＊篇章 第4章 绫世奏 -最终章-']]) assert.equal(filterCatalogue(data,{query:cn})[0].work.id,id);
});

test('NanaWind independent chapters and Fan Discs are not duplicated by W packages or update discs',()=>{
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='nanawind');
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,41);
  assert.deepEqual(data.works.filter(w=>['g890','g891','g892','g893'].includes(w.id)).map(w=>w.firstYear),[2021,2022,2024,2026]);
  assert.ok(data.versions.find(v=>v.workId==='g890').differences.includes('2021/11/26'));
  assert.ok(data.versions.find(v=>v.workId==='g893').differences.includes('2026/01/30'));
  assert.deepEqual(new Set(data.versions.filter(v=>v.kind==='十周年W化DISK追加更新').map(v=>v.workId)),new Set(['g886','g887','g888','g889']));
  assert.equal(data.works.filter(w=>w.originalTitle==='春音アリス＊グラムＷパッケージ化DISK').length,0);
  assert.equal(data.works.filter(w=>w.originalTitle==='花鐘カナデ＊グラム').length,0);
  assert.equal(data.works.find(w=>w.id==='g894').firstYear,2023);
  for(const id of ['g895','g896','g897','g898']) assert.ok(data.versions.filter(v=>v.workId===id).every(v=>v.voice==='无'));
});

test('NanaWind ports, localized releases and mobile batches preserve publisher and evidence',()=>{
  for(const [id,company,platform,year] of [['g886','dramatic create','PlayStation Vita',2015],['g887','dramatic create','PlayStation 4',2019],['g888','ENTERGRAM','PlayStation Vita',2019],['g889','ENTERGRAM','Nintendo Switch',2025],['g886','HIKARI FIELD','Steam',2019],['g887','HIKARI FIELD','Steam',2023]]){
    const row=filterCatalogue(data,{company,platform}).find(({work})=>work.id===id);
    assert.ok(row);assert.equal(row.versions.length,1);assert.equal(row.versions[0].year,year);
  }
  assert.equal(filterCatalogue(data,{query:'Haruoto',company:'HIKARI FIELD'}).length,0);
  const mobile=data.versions.filter(v=>v.workId==='g886'&&v.publisher==='萌えAPP');
  assert.equal(mobile.length,3);assert.ok(mobile[0].differences.includes('2015/04/24'));assert.ok(mobile.slice(1).every(v=>v.differences.includes('2015/06/12')));
  assert.ok(mobile.every(v=>v.voice==='未核实'));
  const dossier=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies.find(c=>c.id==='nanawind');
  assert.ok(dossier.entries.find(e=>e.title==='当前iMel销售与移管时间').status.includes('日期待核'));
  const page=readFileSync(new URL('../nanawind.html',import.meta.url),'utf8');
  for(const id of dossier.workIds) assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(!/undefined|NaN|Infinity/.test(page));
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="nanawind.html"'));
});

test('Data East reuses three interactive animations and lists only the content-added Mega-CD edition',()=>{
  const coverage=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8'));
  const dossier=coverage.companies.find(c=>c.id==='dataeast');
  assert.ok(dossier);assert.equal(dossier.foundedAt,'1976-04-20');
  assert.deepEqual(dossier.workIds,['g082','g083','g085']);
  assert.deepEqual(dossier.publisherWorkIds,['g082','g083','g085']);
  assert.equal(data.works.length,975);assert.equal(data.versions.length,2100);
  for(const [query,id] of [['幻魔大战','g082'],['贝加之战','g082'],['Thunder Storm','g083'],['Road Avenger','g085']]){
    assert.ok(filterCatalogue(data,{query}).some(({work})=>work.id===id),query);
  }
  const road=data.versions.filter(v=>v.workId==='g085');assert.deepEqual(road.map(v=>v.id),['g085-v1','g085-v2']);
  const cd=road[1];assert.equal(cd.platform,'Mega-CD');assert.equal(cd.publisher,'Wolf Team');assert.ok(cd.differences.includes('J-WALK'));
  const dataEast=filterCatalogue(data,{company:'Data East'}).find(({work})=>work.id==='g085');
  assert.equal(dataEast.versions.length,1);assert.equal(dataEast.versions[0].id,'g085-v1');
  const wolfTeam=filterCatalogue(data,{company:'Wolf Team'}).find(({work})=>work.id==='g085');
  assert.equal(wolfTeam.versions.length,1);assert.equal(wolfTeam.versions[0].id,'g085-v2');
  const page=readFileSync(new URL('../dataeast.html',import.meta.url),'utf8');
  for(const id of dossier.workIds)assert.equal(page.split(`<article class=\"card\" id=\"${id}\">`).length-1,1);
  assert.ok(page.includes('J-WALK'));assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href=\"dataeast.html\"'));
});

test('Konami content chronology avoids recycled characters and previously released DLC bundles',()=>{
  const coverage=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies;
  const dossier=coverage.find(c=>c.id==='konami');
  assert.equal(dossier.foundedAt,'1969-03-21');
  assert.ok(coverage.indexOf(dossier)<coverage.findIndex(c=>c.id==='sinclair'));
  assert.equal(dossier.workIds.length,11);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,36);
  const premium=data.versions.find(v=>v.id==='g939-v2');
  assert.equal(premium.year,2012);assert.ok(premium.differences.includes('蓮見達也'));
  assert.ok(!data.versions.some(v=>['g937','g938','g939'].includes(v.workId)&&v.year===2024));
  assert.ok(dossier.entries.find(e=>e.title==='Girl’s Side 2024 Switch高清版').reason.includes('2012'));
  const music=data.versions.filter(v=>v.workId==='g177').slice(1);
  assert.equal(music.length,4);assert.ok(music.every(v=>v.differences.includes('依赖本体')));
  assert.ok(!music.some(v=>v.differences.includes('2010/01/14')));
  const gs4=data.versions.filter(v=>v.workId==='g940');
  assert.equal(gs4.length,8);assert.ok(gs4.slice(1).every(v=>v.differences.includes('不是独立游戏')));
  assert.ok(gs4.some(v=>v.differences.includes('巴征道')));
  assert.ok(gs4.some(v=>v.differences.includes('大成功')));
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  assert.equal(aliases['科乐美'],'Konami');assert.equal(aliases['Konami Digital Entertainment'],'Konami');
  const filtered=filterCatalogue(data,{company:aliases['科乐美']});
  for(const id of dossier.workIds)assert.ok(filtered.some(({work})=>work.id===id));
  assert.equal(data.versions.find(v=>v.id==='g940-v1').publisher,'Konami Digital Entertainment');
  const page=readFileSync(new URL('../konami.html',import.meta.url),'utf8');
  for(const id of dossier.workIds)assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="konami.html"'));
});

test('Hudson reuses originals, separates independent afterstories and credits content-added ports',()=>{
  const coverage=JSON.parse(readFileSync(new URL('../data/company-coverage.json',import.meta.url),'utf8')).companies;
  const dossier=coverage.find(c=>c.id==='hudson');
  assert.equal(dossier.foundedAt,'1973-05-18');
  assert.ok(coverage.indexOf(dossier)>coverage.findIndex(c=>c.id==='konami'));
  assert.ok(coverage.indexOf(dossier)<coverage.findIndex(c=>c.id==='sinclair'));
  assert.equal(dossier.workIds.length,21);
  assert.equal(data.versions.filter(v=>dossier.workIds.includes(v.workId)).length,26);
  assert.equal(publisherWorkCounts(data).get('Hudson Soft（哈德森）'),21);
  for(const id of ['g074','g077','g019','g020'])assert.ok(dossier.workIds.includes(id));
  const murder=data.versions.filter(v=>v.workId==='g942');
  assert.equal(murder.length,2);
  assert.deepEqual(murder.map(v=>v.publisherCompanies[0]),['リバーヒルソフト','Hudson Soft（哈德森）']);
  assert.equal(filterCatalogue(data,{query:'殺人倶楽部',company:'Hudson Soft（哈德森）'})[0].versions[0].year,1990);
  const remix=data.versions.find(v=>v.id==='g948-v2');
  assert.ok(remix.differences.includes('お月様とダンス'));assert.equal(remix.year,1996);
  assert.ok(!data.versions.some(v=>['g948','g950'].includes(v.workId)&&v.platform==='PSP'));
  for(const id of ['g953','g956','g958'])assert.equal(data.versions.filter(v=>v.workId===id).length,1);
  assert.equal(data.works.find(w=>w.id==='g956').firstYear,1999);
  assert.ok(data.works.find(w=>w.id==='g958').notes.includes('可单独享受')||data.works.find(w=>w.id==='g958').notes.includes('单独体验'));
  for(const id of ['g943','g944'])assert.equal(data.works.find(w=>w.id===id).subcategory,'图文选项／调查');
  const aliases=JSON.parse(readFileSync(new URL('../data/taxonomy.json',import.meta.url),'utf8')).publisherAliases;
  for(const name of ['Hudson Soft','HUDSON','ハドソン','哈德森'])assert.equal(aliases[name],dossier.name);
  const page=readFileSync(new URL('../hudson.html',import.meta.url),'utf8');
  for(const id of dossier.workIds)assert.equal(page.split(`<article class="card" id="${id}">`).length-1,1);
  assert.ok(readFileSync(new URL('../index.html',import.meta.url),'utf8').includes('href="hudson.html"'));
});
