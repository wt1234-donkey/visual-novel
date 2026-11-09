import {STYLE_DIMENSIONS,STYLE_KEYS,styleState,validateStyleTags,isSourceURL} from './basic-style-tags.mjs';

export const STYLE_QUEUE_KEY='visual-novel-basic-style-review-v1';
export const MAX_STYLE_BATCH=500;
const missingSynopsis=/^(?:简介|剧情|故事|内容|作品剧情简介|官方剧情简介)?[：:\s]*(?:未录入|暂无|待核|待补充|待整理|待依据|待补|暂缺|资料不足)|尚未(?:整理|录入|核实)|尚待(?:补充|核实)/;

export function buildStyleRequest(works,fullWorks,editorial){
 const byId=new Map(fullWorks.map(work=>[work.id,work]));
 const items=[],issues=[];
 for(const work of works){
  const archive=byId.get(work._key)||byId.get(work.linkedRecordId);
  const synopsis=(archive?.synopsis||'').replace(/\s+/g,' ').trim().slice(0,4500);
  const sources=[...new Set([archive?.source,...(editorial[archive?.id]?.sources||[]),work.source].filter(s=>typeof s==='string'&&s.length<=2048&&isSourceURL(s)))].slice(0,8);
  const identity={id:work._key,title:work.title};
  const dimensions=STYLE_KEYS.filter(key=>!Object.hasOwn(styleState(work).tags,key));
  if(!dimensions.length)issues.push({...identity,reason:'六个维度均已有标签'});
  else if(synopsis.length<10||missingSynopsis.test(synopsis)||!sources.length)issues.push({...identity,reason:'缺少可用于识别的剧情简介或资料来源'});
  else items.push({...identity,synopsis,sources,dimensions});
 }
 return {schemaVersion:1,items,issues};
}

function validateIdentity(item,seen){
 if(typeof item?.id!=='string'||!item.id.trim()||item.id.length>200||
  typeof item.title!=='string'||!item.title.trim()||item.title.length>500||seen.has(item.id))throw Error('作品ID或名称无效，或文件存在重复ID');
 seen.add(item.id);
}

function validateEvidenceInput(item){
 if(typeof item.synopsis!=='string'||item.synopsis.length<10||item.synopsis.length>4500||missingSynopsis.test(item.synopsis)||
  !Array.isArray(item.sources)||!item.sources.length||item.sources.length>8||
  item.sources.some(s=>typeof s!=='string'||s.length>2048||!isSourceURL(s)))throw Error('候选缺少有效的简介与来源：'+item.id);
}

function validateBatch(data){
 if(data?.schemaVersion!==1||!Array.isArray(data.items)||!Array.isArray(data.issues)||
  data.items.length+data.issues.length>MAX_STYLE_BATCH)throw Error('文件须符合风格标注格式，每批最多500部');
 const seen=new Set();
 for(const item of [...data.items,...data.issues])validateIdentity(item,seen);
 for(const issue of data.issues)if(typeof issue.reason!=='string'||!issue.reason.trim()||issue.reason.length>500)throw Error('待补资料记录格式无效');
}

export function validateStyleRequest(data){
 validateBatch(data);
 for(const item of data.items){
  validateEvidenceInput(item);
  if(!Array.isArray(item.dimensions)||!item.dimensions.length||new Set(item.dimensions).size!==item.dimensions.length||
   item.dimensions.some(key=>!STYLE_KEYS.includes(key)))throw Error('待识别维度无效：'+item.id);
 }
 return data;
}

export function validateCandidates(item,candidates,allowed=STYLE_KEYS){
 if(!Array.isArray(candidates)||candidates.length>allowed.length)throw Error('候选格式无效');
 const seen=new Set();
 for(const candidate of candidates){
  const {dimension,tag,quote,source}=candidate||{};
  if(!allowed.includes(dimension)||seen.has(dimension))throw Error('候选维度重复或超出范围：'+item.id);
  if(typeof quote!=='string'||quote.trim().length<4||quote.length>500||!item.synopsis.includes(quote))
   throw Error('候选摘录与已有简介不符：'+item.id);
  if(!item.sources.includes(source))throw Error('候选来源与已有资料不符：'+item.id);
  validateStyleTags({[dimension]:tag});
  seen.add(dimension);
 }
 return candidates;
}

export function parseStyleReview(text){
 const data=JSON.parse(text.replace(/^\uFEFF/,''));
 validateBatch(data);
 if(typeof data.model!=='string'||!data.model.trim()||data.model.length>120)throw Error('缺少候选模型名称');
 for(const item of data.items){
  validateEvidenceInput(item);
  if(!validateCandidates(item,item.candidates).length)throw Error('候选为空：'+item.id);
 }
 return data;
}

export function styleReviewRows(items,selected){
 return items.flatMap(item=>{
  const approved=item.candidates.filter(candidate=>selected.get(item.id)?.has(candidate.dimension));
  if(!approved.length)return [];
  return [{
   id:item.id,title:item.title,mode:'fill',
   tags:Object.fromEntries(approved.map(({dimension,tag})=>[dimension,tag])),
   evidence:Object.fromEntries(approved.map(({dimension,quote,source})=>[dimension,{quote,source,model:item.model}]))
  }];
 });
}

export function styleCandidateFormat(dimensions){
 return {type:'object',required:['candidates'],additionalProperties:false,properties:{candidates:{
  type:'array',maxItems:dimensions.length,items:{oneOf:dimensions.map(key=>({
   type:'object',required:['dimension','tag','quote'],additionalProperties:false,properties:{
    dimension:{type:'string',enum:[key]},tag:{type:'string',enum:STYLE_DIMENSIONS[key].tags},quote:{type:'string'}
   }
  }))}
 }}};
}
