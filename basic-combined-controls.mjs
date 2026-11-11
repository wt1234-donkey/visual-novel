import {SEARCH_FIELDS,searchValues} from './basic-combined-search.mjs?v=20261110-flex-tags';

const $=id=>document.getElementById(id);
const create=(tag,text,attributes={})=>{
 const node=document.createElement(tag);
 if(text!==undefined)node.textContent=text;
 for(const [key,value] of Object.entries(attributes))node.setAttribute(key,value);
 return node;
};
const select=(options,label)=>{
 const node=create('select',undefined,{'aria-label':label});
 for(const [value,text] of options)node.append(create('option',text,{value}));
 return node;
};
const button=(text,label)=>create('button',text,{type:'button',...(label?{'aria-label':label}:{})});
const makeFacetRule=(field,mode,values)=>values.length?{field,mode,values}:null;
const checkedValues=node=>Array.from(node.querySelectorAll('input:checked'),input=>input.value);
const hints={range:'如 1980..1999 或 >= 2',gameplay:'如 图文冒险、纯RPG',style:'如 黑暗、哲思',theme:'如 悬疑、科幻、历史',language:'如 日语、en',region:'如 日本、北美、欧洲',voice:'如 有、无',relation:'如 原作、新增内容、同内容、待核'};

export function setupCombinedControls(onSearch){
 const groupHost=$('query-groups');
 let applied=[];
 function addRule(host,initial={}){
  const row=create('div',undefined,{class:'query-rule'});
  const field=select(Object.entries(SEARCH_FIELDS).map(([key,meta])=>[key,meta.label]),'条件字段');
  const mode=select([['any','任一值 ANY'],['all','全部值 ALL'],['none','排除值 NOT']],'同一条件的匹配方式');
  const values=create('input',undefined,{'aria-label':'条件值',type:'text',maxlength:'300'});
  const setHint=()=>{values.placeholder=hints[SEARCH_FIELDS[field.value].kind]||'多个值用顿号或逗号分隔';};
  field.addEventListener('change',setHint);
  field.value=initial.field||'creator';mode.value=initial.mode||'any';values.value=initial.value||'';setHint();
  const remove=button('移除','移除该条件');
  remove.addEventListener('click',()=>{row.remove();if(!host.querySelector('.query-rule'))addRule(host);});
  row.append(field,mode,values,remove);host.append(row);
 }
 function numberGroups(){
  for(const [i,fieldset] of Array.from(groupHost.children).entries())fieldset.firstElementChild.textContent='条件组 '+(i+1)+' · 组内全部满足（AND）';
  $('query-add-group').disabled=groupHost.children.length>=8;
 }
 function addGroup(initial=[{}]){
  const fieldset=create('fieldset',undefined,{class:'query-group'}),host=create('div'),toolbar=create('div',undefined,{class:'query-actions'});
  const add=button('＋ 添加条件'),remove=button('移除本组');
  add.addEventListener('click',()=>{if(host.children.length<12)addRule(host);});
  remove.addEventListener('click',()=>{fieldset.remove();if(!groupHost.children.length)addGroup();numberGroups();});
  toolbar.append(add,remove);fieldset.append(create('legend'),host,toolbar);groupHost.append(fieldset);
  for(const row of initial)addRule(host,row);
  numberGroups();
 }
 function quickRules(){
  const plays=checkedValues($('gameplay')),styles=checkedValues($('style'));
  const playMode=$('gameplay-mode').value,styleMode=$('style-mode').value;
  const from=$('year-from').value,to=$('year-to').value;
  if(from&&to&&Number(from)>Number(to))throw Error('起始年份不能晚于结束年份');
  const period=from||to?{field:'year',mode:'any',values:[from&&to?from+'..'+to:from?'>='+from:'<='+to]}:null;
  return [makeFacetRule('gameplay',playMode,plays),makeFacetRule('style',styleMode,styles),period].filter(Boolean);
 }
 function readAdvanced(){
  return Array.from(groupHost.children,group=>Array.from(group.querySelectorAll('.query-rule'),row=>{
   const [field,mode,input]=row.children;
   return makeFacetRule(field.value,mode.value,searchValues(input.value));
  }).filter(Boolean)).filter(group=>group.length);
 }
 function updateCount(id){const node=$(id);node.firstElementChild.textContent=node.dataset.label+'（已选 '+checkedValues(node).length+'）';}
 for(const id of ['gameplay','style'])$(id).addEventListener('change',()=>{updateCount(id);onSearch();});
 for(const id of ['gameplay-mode','style-mode','year-from','year-to'])$(id).addEventListener('change',onSearch);
 $('query-add-group').addEventListener('click',()=>addGroup());
 $('query-form').addEventListener('submit',event=>{event.preventDefault();applied=readAdvanced();onSearch();});
 $('query-example').addEventListener('click',()=>{
  $('filter-reset').click();
  $('year-from').value='1980';$('year-to').value='1999';
  for(const input of $('gameplay').querySelectorAll('input'))input.checked=['interactive-fiction','graphic-adventure'].includes(input.value);
  updateCount('gameplay');groupHost.replaceChildren();
  addGroup([{field:'theme',value:'悬疑、科幻、历史'},{field:'productionRegion',value:'日本'},{field:'gameplay',mode:'none',value:'纯RPG'}]);
  applied=readAdvanced();onSearch();
 });
 addGroup();
 return {
  snapshot(){return {applied,draft:Array.from(groupHost.children,group=>Array.from(group.querySelectorAll('.query-rule'),row=>({field:row.children[0].value,mode:row.children[1].value,value:row.children[2].value}))),quick:Object.fromEntries(['gameplay','style'].map(id=>[id,checkedValues($(id))])),values:Object.fromEntries(['gameplay-mode','style-mode','year-from','year-to'].map(id=>[id,$(id).value]))};},
  restore(saved={}){
   if(!Array.isArray(saved.draft)||saved.draft.length>8||saved.draft.some(group=>!Array.isArray(group)||group.length>12||group.some(rule=>!SEARCH_FIELDS[rule.field]||!['any','all','none'].includes(rule.mode)||typeof rule.value!=='string'||rule.value.length>300)))throw Error('恢复的检索条件无效');
   groupHost.replaceChildren();for(const group of saved.draft)addGroup(group);if(!saved.draft.length)addGroup();
   applied=Array.isArray(saved.applied)?saved.applied.filter(group=>Array.isArray(group)&&group.every(rule=>SEARCH_FIELDS[rule.field]&&['any','all','none'].includes(rule.mode)&&Array.isArray(rule.values)&&rule.values.every(value=>typeof value==='string'))):[];
   for(const id of ['gameplay','style']){for(const input of $(id).querySelectorAll('input'))input.checked=(saved.quick?.[id]||[]).includes(input.value);updateCount(id);}
   for(const id of ['gameplay-mode','style-mode','year-from','year-to'])if(typeof saved.values?.[id]==='string')$(id).value=saved.values[id];
  },
  groups(){const quick=quickRules();return applied.length?applied.map(group=>[...quick,...group]):quick.length?[quick]:[];},
  reset(){
   for(const id of ['gameplay','style']){for(const box of $(id).querySelectorAll('input:checked'))box.checked=false;updateCount(id);}
   for(const id of ['gameplay-mode','style-mode'])$(id).value='any';
   $('year-from').value=$('year-to').value='';applied=[];groupHost.replaceChildren();addGroup();
  },
  options(id,groups){
   const node=$(id),selected=new Set(checkedValues(node)),host=node.lastElementChild;
   host.replaceChildren();
   for(const {label,options} of groups){
    if(!options.length)continue;
    const group=create('fieldset',undefined,{class:'query-options'});
    if(label)group.append(create('legend',label));
    for(const option of options){
     const label=create('label'),input=create('input',undefined,{type:'checkbox',value:option.key});
     input.checked=selected.has(option.key);
     label.append(input,create('span',option.label));group.append(label);
    }
    host.append(group);
   }
   updateCount(id);
  }
 };
}
