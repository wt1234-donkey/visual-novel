import {STYLE_GROUPS,styleState} from './basic-style-tags.mjs';
export {styleName,styleState,STYLE_DIMENSIONS,styleDimension} from './basic-style-tags.mjs';

export const normalizeFilterText=value=>String(value??'').normalize('NFKC').trim().replace(/\s+/g,' ').toLowerCase();
export const manufacturerKey=normalizeFilterText;
const order=new Intl.Collator('zh-Hans-CN',{numeric:true,sensitivity:'base'});
export const REGION_LABELS={japan:'日本厂商',other:'非日本厂商',unknown:'地区待核'};
export const MANUFACTURER_OPTION_LIMIT=200;
export function manufacturerNames(work){return [...new Set([work.group,...(work.groups||[])].filter(x=>typeof x==='string'&&x.trim()).map(x=>x.trim()))];}
export function createManufacturerIndex(works,metadata={entries:[]}){
 const regions=new Map();
 for(const row of metadata.entries||[])for(const name of row.names||[]){const key=manufacturerKey(name);if(!key)continue;const region=['japan','other'].includes(row.region)?row.region:'unknown';regions.set(key,regions.has(key)&&regions.get(key)!==region?'unknown':region);}
 const byKey=new Map();
 for(const work of works){const seen=new Set();for(const name of manufacturerNames(work)){const key=manufacturerKey(name);if(!byKey.has(key))byKey.set(key,{key,count:0,variants:new Map(),region:regions.get(key)||'unknown'});const item=byKey.get(key);item.variants.set(name,(item.variants.get(name)||0)+1);if(!seen.has(key)){item.count++;seen.add(key);}}}
 return [...byKey.values()].map(item=>{const variants=[...item.variants].sort((a,b)=>b[1]-a[1]||order.compare(a[0],b[0])||a[0].localeCompare(b[0]));return {...item,label:variants[0][0],variants:variants.map(([name])=>name),search:variants.map(([name])=>normalizeFilterText(name)).join('\n')};}).sort((a,b)=>b.count-a.count||order.compare(a.label,b.label));
}
export function matchingManufacturers(index,{region='',query=''}={}){const q=normalizeFilterText(query);return index.filter(item=>(!region||item.region===region)&&(!q||item.search.includes(q)));}
export function manufacturerOptions(index,filters={},selected='',limit=MANUFACTURER_OPTION_LIMIT){const matches=matchingManufacturers(index,filters),visible=matches.slice(0,limit),chosen=matches.find(item=>item.key===selected);if(chosen&&!visible.includes(chosen))visible[visible.length-1]=chosen;return {total:matches.length,visible:visible.sort((a,b)=>order.compare(a.label,b.label))};}

// These are browsing categories, not inferred controls or new source classifications.
export const GAMEPLAY_TYPES=[
 ['visual-novel','视觉小说',['视觉小说','Visual Novel','VN']],
 ['adventure','冒险（ADV）',['ADV','Adventure','冒险','冒险游戏','冒险（玩法待核）','其他冒险候选']],
 ['interactive-fiction','文字冒险／互动小说',['互动小说','互动小说（玩法待核）','纯文字冒险','文字冒险','文本冒险','Interactive Fiction','Text Adventure','Text-based Adventure']],
 ['graphic-adventure','图文／图形冒险',['图文冒险','图形冒险','动画图文冒险','Graphic Adventure','Graphical Adventure']],
 ['text-input','文字输入',['文字输入','Parser']],
 ['point-click','点击调查',['点击调查','点击调查冒险','Point-and-click','Point & Click']],
 ['choices','选项分支',['选项分支','选项式冒险','选择式冒险']],
 ['menu','菜单指令',['菜单指令','Menu-Driven','Menu Driven']],
 ['movie','互动电影／动画',['互动电影ADV','互动电影','互动动画','FMV']],
 ['rpg','角色扮演（RPG）',['RPG','Role-playing (RPG)','角色扮演','纯RPG','纯角色扮演','二维RPG候选','三维RPG候选']],
 ['action','动作／直接操控',['Action','动作','直接操控','直接移动','直接操控冒险候选']],
 ['strategy','策略／战术',['Strategy / tactics','Strategy','策略','战术策略']],
 ['simulation','模拟／养成／经营',['Simulation','模拟','养成','日程养成','资源经营']],
 ['puzzle','解谜',['Puzzle','解谜','谜题操作']],
 ['sports','体育',['Sports','体育']],
 ['racing','竞速／驾驶',['Racing / Driving','Racing','驾驶操控','竞速']],
 ['board','棋牌／规则对战',['Gambling','棋牌','卡牌棋盘','规则对战']],
 ['music','音乐／节奏',['音乐游戏','节奏演奏','Rhythm']],
 ['education','教育／问答',['Educational','教育','知识问答']],
 ['collection','合集／Fan Disc／特别版',['Compilation','Special edition','合集','特别版']],
 ['adult-pending','Galgame／成人向（玩法待核）',['Galgame','Galgame（玩法待核）','拔作','成人向（玩法待核）']],
 ['tools','剧情创作工具',['剧情编辑工具']],
 ['other','其他／跨类型',['跨类型叙事','跨类型游戏']],
 ['unknown','玩法待核',['玩法待核','待核实','Unknown']]
];
export const GAMEPLAY_OPTIONS=GAMEPLAY_TYPES.map(([,label])=>label);
const gameplayAliases=new Map();
for(const [key,label,aliases] of GAMEPLAY_TYPES)for(const alias of [key,label,...aliases])gameplayAliases.set(normalizeFilterText(alias),[key]);
for(const [alias,keys] of [['ARPG',['rpg','action']],['动作RPG',['rpg','action']],['SRPG',['rpg','strategy']],['策略RPG',['rpg','strategy']],['ADV／策略RPG',['adventure','rpg','strategy']]])gameplayAliases.set(normalizeFilterText(alias),keys);
const historicalGameplayGroups=[
 [['rpg'],['RPG／叙事关联','角色扮演／剧情关联','剧情RPG','剧情 RPG','迷宫角色扮演','迷宫RPG','故事型RPG','事件探索RPG','手机 RPG','程序生成迷宫RPG','纯文本RPG','探索RPG','选择与战斗RPG','成人向迷宫RPG','剧情探索RPG','分章故事RPG','声音小说型RPG','无文字共生探索RPG','在线RPG','角色扮演游戏','在线 RPG','魔法学园 RPG']],
 [['rpg','strategy'],['角色扮演／战略模拟','策略角色扮演','战术RPG']],
 [['rpg','action'],['动作角色扮演','剧情动作RPG']],
 [['rpg','education'],['教育探索RPG']],
 [['rpg','adventure'],['冒险RPG','迷宫 RPG／ADV']],
 [['rpg','simulation'],['经营角色扮演']],
 [['rpg','puzzle'],['益智 RPG']],
 [['strategy'],['策略／叙事关联','策略游戏','剧情即时战略','剧情战术模拟','剧情策略','策略／角色叙事关联','策略叙事']],
 [['strategy','simulation'],['策略与养成']],
 [['strategy','action'],['策略与动作叙事','动作策略']],
 [['action'],['剧情动作','动作／叙事关联','动作／休闲游戏','剧情动作游戏','剧情平台动作','剧情动作探索','动作叙事']],
 [['action','adventure'],['动作冒险']],
 [['music','action'],['剧情节奏动作']],
 [['visual-novel','action'],['小说／3D 机器人动作']],
 [['visual-novel'],['移动游戏小说']],
 [['interactive-fiction'],['文字冒险（仅专题）','书籍附带纯文字冒险']],
 [['text-input'],['文字输入／仅专题']],
 [['education','adventure'],['问答冒险']],
 [['simulation'],['经营／职业模拟','养成模拟','剧情模拟','音乐恋爱育成','恋爱模拟']],
 [['simulation','adventure'],['沟通养成冒险']],
 [['board'],['剧情棋盘','棋牌游戏']],
 [['puzzle','board'],['益智／桌面游戏']],
 [['puzzle','adventure'],['益智冒险']],
 [['adventure'],['反RPG探索冒险','探索冒险']],
 [['collection'],['杂集／Fan Disc']]
];
for(const [keys,aliases] of historicalGameplayGroups)for(const alias of aliases)gameplayAliases.set(normalizeFilterText(alias),keys);
export function gameplayKeys(raw){
 const value=String(raw??'').trim();if(!value)return ['unknown'];
 const direct=gameplayAliases.get(normalizeFilterText(value));if(direct)return [...direct];
 return [...new Set(value.split(/[,，;；\n]+/).map(x=>x.trim()).filter(Boolean).flatMap(part=>gameplayAliases.get(normalizeFilterText(part))||['custom:'+normalizeFilterText(part)]))];
}
const plainRpgLabels=new Set(['RPG','Role-playing (RPG)','角色扮演（RPG）','角色扮演','角色扮演游戏','纯RPG','纯角色扮演'].map(normalizeFilterText));
export function gameplayLabel(key){return GAMEPLAY_TYPES.find(([id])=>id===key)?.[1]||key.replace(/^custom:/,'');}
const catalogueGameplay=work=>[...new Set([...gameplayKeys(work.gameplay),...(work.gameplayTags||[])])];
export function gameplayOptions(works){const counts=new Map(),customLabels=new Map();for(const work of works){for(const key of catalogueGameplay(work)){counts.set(key,(counts.get(key)||0)+1);if(key.startsWith('custom:'))for(const part of String(work.gameplay||'').split(/[,，;；\n]+/))if('custom:'+normalizeFilterText(part)===key&&!customLabels.has(key))customLabels.set(key,part.trim());}}return [...GAMEPLAY_TYPES.filter(([key])=>counts.has(key)).map(([key,label])=>({key,label,count:counts.get(key)})),...[...customLabels].sort((a,b)=>order.compare(a[1],b[1])).map(([key,label])=>({key,label,count:counts.get(key)}))];}
export function gameplayDisplay(raw,gameplayTags){const keys=catalogueGameplay({gameplay:raw,gameplayTags});return keys.map(key=>key.startsWith('custom:')?String(raw).split(/[,，;；\n]+/).find(x=>'custom:'+normalizeFilterText(x)===key)?.trim()||gameplayLabel(key):gameplayLabel(key)).join(' / ');}

export const MISSING_STYLE='__missing__';
export function styleOptions(works){
 const counts=new Map();
 for(const work of works)for(const tag of Object.values(styleState(work).tags))counts.set(tag,(counts.get(tag)||0)+1);
 return Object.entries(STYLE_GROUPS).map(([label,styles])=>({label,options:styles.map(tag=>({label:tag,key:tag,count:counts.get(tag)||0}))}));
}

export function pageIndex(value,pageCount){const text=String(value).trim();if(!/^\d+$/.test(text)||!Number.isSafeInteger(Number(text))||Number(text)<1||Number(text)>pageCount)throw Error('请输入 1—'+pageCount+' 范围内的整数页码');return Number(text)-1;}

export function basicFilterRows(entries,childrenByMain){
 return entries.map(row=>{
  const {tags}=styleState(row),styles=Object.values(tags);
  const names=manufacturerNames(row);
  const childNames=(childrenByMain.get(row._key)||[]).flatMap(child=>[child.title,...(child.aliases||[])]);
  return {
   search:normalizeFilterText([row.title,...(row.aliases||[]),...names,...styles,...childNames].join(' ')),
   manufacturers:[...new Set(names.map(manufacturerKey))],gameplay:catalogueGameplay(row),
   pureRpg:plainRpgLabels.has(normalizeFilterText(row.gameplay))&&!row.gameplayTags?.some(key=>key!=='rpg'),styles,themes:tags.theme?[normalizeFilterText(tags.theme)]:[],year:row.year,status:row.status,slot:row.slot
  };
 });
}
export function matchingBasicPositions(rows,{q,gameplay,group,status,year,style,allowed},test=null,advanced=null){
 const matching=[];
 for(let i=0;i<rows.length;i++){
  const row=rows[i];
  if(style&&(style===MISSING_STYLE?row.styles.length:!row.styles.includes(style)))continue;
  if(year&&(year==='unknown'?Number.isInteger(row.year):row.year!==Number(year)))continue;
  if(q&&!row.search.includes(q)||gameplay&&!row.gameplay.includes(gameplay)||status&&row.status!==status)continue;
  if((group||allowed)&&!row.manufacturers.some(key=>(!group||key===group)&&(!allowed||allowed.has(key))))continue;
  if(test&&!test(row,advanced?.[row.slot]))continue;
  matching.push(i);
 }
 return matching;
}
