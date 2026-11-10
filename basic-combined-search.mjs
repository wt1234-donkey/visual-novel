import {gameplayKeys,normalizeFilterText,MISSING_STYLE} from './basic-catalogue-filters.mjs?v=20261110-flex-tags';
import {styleName,styleDimension} from './basic-style-tags.mjs?v=20261110-flex-tags';

export const SEARCH_FIELDS={
 gameplay:{label:'主要玩法',kind:'gameplay'}, style:{label:'作品特征标签',kind:'style'},
 theme:{label:'故事题材',kind:'theme'}, year:{label:'原作首发年份',kind:'range'},
 manufacturer:{label:'关联厂商',kind:'text'}, productionRegion:{label:'制作地区',kind:'region'},
 creator:{label:'创作者',kind:'text'}, character:{label:'角色',kind:'text'}, series:{label:'系列',kind:'text'},
 language:{label:'资料记录语言',kind:'language'}, duration:{label:'平均游玩分钟',kind:'range'},
 contentCount:{label:'已编目内容版本数',kind:'range'},
 position:{label:'叙事定位',kind:'text'}, structure:{label:'叙事结构',kind:'text'},
 interaction:{label:'正式档案互动方式',kind:'text'}, brand:{label:'制作／原发行品牌',kind:'text'},
 developer:{label:'开发方',kind:'text'}, participant:{label:'参与主体',kind:'text'},
 platform:{label:'发行平台',kind:'text',release:true}, releaseYear:{label:'发行年份',kind:'range',release:true},
 releaseRegion:{label:'发行地区',kind:'region',release:true}, publisher:{label:'发行方',kind:'text',release:true},
 voice:{label:'配音',kind:'voice',release:true}, contentRelation:{label:'内容关系',kind:'relation',release:true}
};
export const REGION_VALUES={japan:'日本',other:'非日本',northAmerica:'北美',europe:'欧洲',oceania:'大洋洲',worldwide:'全球'};
const relationValues={original:'原作',added:'新增内容',same:'同内容',unverified:'待核'};
const languageNames={ja:['日语','日文','Japanese','jpn'],en:['英语','英文','English','eng'],'zh-hans':['简体中文','简中','zh-cn'],'zh-hant':['繁体中文','繁中','zh-tw','zh-hk'],zh:['中文','汉语','Chinese','zho'],ko:['韩语','韩文','Korean'],fr:['法语','French'],de:['德语','German'],es:['西班牙语','Spanish'],it:['意大利语','Italian'],ru:['俄语','Russian'],pt:['葡萄牙语','Portuguese','pt-br'],nl:['荷兰语','Dutch'],cs:['捷克语','Czech'],pl:['波兰语','Polish'],sv:['瑞典语','Swedish'],uk:['乌克兰语','Ukrainian']};
const langByName=new Map(Object.entries(languageNames).flatMap(([key,aliases])=>[key,...aliases].map(v=>[normalizeFilterText(v),key])));
const regionByName=new Map(Object.entries(REGION_VALUES).flatMap(([key,label])=>[[normalizeFilterText(key),key],[label,key]]));
const relationByName=new Map(Object.entries(relationValues).flatMap(([key,label])=>[[key,key],[label,key]]));
export const normalizeLanguage=value=>langByName.get(normalizeFilterText(value))||normalizeFilterText(value);
export const searchValues=text=>[...new Set(text.split(/[,，、;；|\n]+/).map(v=>v.trim()).filter(Boolean))];
const simpleFields=new Set(['gameplay','style','year','manufacturer']);
export const needsAdvancedIndex=groups=>groups.some(group=>group.some(rule=>!simpleFields.has(rule.field)||rule.field==='style'&&rule.values.some(value=>styleDimension(value)==='theme')));

function range(value){
 const match=/^(?:(>=|<=|>|<|=)\s*)?(\d+(?:\.\d+)?)(?:\s*(?:\.\.|[-–—~～至])\s*(\d+(?:\.\d+)?))?$/.exec(value);
 if(!match||match[1]&&match[3]||match[3]&&Number(match[3])<Number(match[2]))throw Error('数字条件可填写 1990、1980..1999 或 >= 2');
 const [,operator,start,end]=match,a=Number(start),b=end===undefined?a:Number(end);
 if(!Number.isFinite(a)||!Number.isFinite(b))throw Error('数字条件超出范围');
 return n=>Number.isFinite(n)&&(operator==='>='?n>=a:operator==='>'?n>a:operator==='<='?n<=a:operator==='<'?n<a:n>=a&&n<=b);
}
function valueMatcher(rule,value){
 const {field}=rule,{kind}=SEARCH_FIELDS[field];
 const norm=normalizeFilterText(value);
 if(kind==='range')return range(value);
 if(kind==='gameplay'){
  if(norm==='纯rpg'||norm==='pure-rpg')return (list,row)=>row?.pureRpg===true;
  const keys=norm.startsWith('custom:')?[norm]:gameplayKeys(value);
  return list=>keys.every(key=>list.includes(key));
 }
 if(kind==='style'){
  if(norm===MISSING_STYLE)return list=>list.length===0;
  const tag=styleName(value);
  const dimension=styleDimension(tag);
  if(!dimension)throw Error('作品特征标签须填写词表中的标签');
  const theme=dimension==='theme'?normalizeFilterText(tag):null;
  return (list,row,meta)=>list.includes(tag)||!!(theme&&meta?.theme?.includes(theme));
 }
 if(kind==='language'){
  const code=normalizeLanguage(value);
  return list=>list.some(v=>v===code||code==='zh'&&v.startsWith('zh-'));
 }
 if(kind==='region'){
  const key=regionByName.get(norm);
  if(!key)throw Error('可用地区包括日本、非日本、北美、欧洲、大洋洲、全球');
  return list=>list.includes(key);
 }
 if(kind==='relation'){
  const key=relationByName.get(norm);
  if(!key)throw Error('内容关系可填写原作、新增内容、同内容、待核');
  return list=>list.includes(key);
 }
 if(kind==='voice')return list=>list.some(v=>v.startsWith(norm));
 if(kind==='theme')return list=>list.includes(normalizeFilterText(styleName(value)));
 return list=>list.some(v=>v.includes(norm));
}
function compileRule(rule){
 const {field,mode,values}=rule;
 if(!Object.hasOwn(SEARCH_FIELDS,field)||!['any','all','none'].includes(mode)||!values.length)throw Error('检索条件不完整');
 const checks=values.map(value=>valueMatcher(rule,value));
 const {kind,release}=SEARCH_FIELDS[field];
 const match=(value,row,meta)=>{
  const data=kind==='range'?value:value||[];
  return mode==='all'?checks.every(check=>check(data,row,meta)):checks.some(check=>check(data,row,meta));
 };
 return {field,release,exclude:mode==='none',match};
}
export function compileCombinedSearch(groups){
 if(!groups.length)return ()=>true;
 const compiled=groups.map(group=>{
  const rules=group.map(compileRule);
  return {work:rules.filter(r=>!r.release),release:rules.filter(r=>r.release&&!r.exclude),excluded:rules.filter(r=>r.release&&r.exclude)};
 });
 return (row,meta)=>compiled.some(({work,release,excluded})=>{
  const get=field=>field==='style'?row.styles:field==='manufacturer'?row.manufacturers:
   field==='theme'?[...row.themes,...(meta?.theme||[])]:simpleFields.has(field)?row[field]:meta?.[field];
  const releases=meta?.releases||[];
  return work.every(rule=>rule.match(get(rule.field),row,meta)!==rule.exclude)&&
   excluded.every(rule=>!releases.some(r=>rule.match(r[rule.field])))&&
   (!release.length||releases.some(r=>release.every(rule=>rule.match(r[rule.field]))));
 });
}
