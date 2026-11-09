// One controlled tag per dimension. Older catalogue values remain available for review.
export const STYLE_DIMENSIONS = {
 tone: {label:'剧情基调', tags:['喜剧','悲剧','轻松','黑暗','温情','感伤','黑色幽默','唯美']},
 emotion: {label:'情绪体验', tags:['治愈','催泪','致郁','压抑','热血','燃系','惊悚','恐怖']},
 expression: {label:'叙事表达', tags:['群像','意识流','荒诞','讽刺','元叙事','实验性','哲思','史诗']},
 relationship: {label:'人物关系', tags:['恋爱','纯爱','亲情','友情','百合','耽美','三角关系','病娇']},
 theme: {label:'故事题材', tags:['科幻','奇幻','历史','战争','犯罪','末世','悬疑','推理','心理','复仇','生存','冒险','魔幻现实','超自然','武侠','赛博朋克','日常','青春','成长']},
 content: {label:'内容提示', tags:['成人向','色情','NTR','乱伦','背德','禁忌关系','猎奇']}
};
export const STYLE_GROUPS = Object.fromEntries(Object.values(STYLE_DIMENSIONS).map(({label,tags})=>[label,tags]));
export const STYLE_OPTIONS = Object.values(STYLE_GROUPS).flat();
export const STYLE_KEYS = Object.keys(STYLE_DIMENSIONS);
const normalize = value=>String(value??'').normalize('NFKC').trim().toLowerCase();
const aliases = new Map([
 ...STYLE_OPTIONS.map(tag=>[normalize(tag),tag]),
 ['疗愈','治愈'],['治癒','治愈'],['暗黑','黑暗'],['寝取られ','NTR']
]);
export const styleName = value=>aliases.get(normalize(value))||String(value??'').trim();
const dimensionsByTag = new Map(STYLE_KEYS.flatMap(key=>STYLE_DIMENSIONS[key].tags.map(tag=>[tag,key])));
export const styleDimension = tag=>dimensionsByTag.get(styleName(tag));

export function styleState(work) {
 const legacy = work.plotStyles||[];
 const tags = {...work.plotTags};
 if(!legacy.length)return {tags,legacy};
 if(!work.plotTags){
  for(const key of STYLE_KEYS){
   const matching=[...new Set(legacy.map(styleName).filter(tag=>styleDimension(tag)===key))];
   if(matching.length===1)tags[key]=matching[0];
  }
 }
 return {tags,legacy:legacy.filter(tag=>!Object.values(tags).includes(styleName(tag)))};
}

export function validateStyleTags(tags, {allowClear=false}={}) {
 if(!tags||typeof tags!=='object'||Array.isArray(tags))throw Error('标签必须按六个维度填写');
 for(const [key,tag] of Object.entries(tags)){
  if(!Object.hasOwn(STYLE_DIMENSIONS,key))throw Error('未知的标签维度：'+key);
  if(tag===null&&allowClear)continue;
  const {label,tags:allowed}=STYLE_DIMENSIONS[key];
  if(!allowed.includes(tag))throw Error(label+'须选用该维度的一个标签：'+tag);
 }
 return tags;
}

export function validateStyleEvidence(evidence,tags) {
 if(!evidence||typeof evidence!=='object'||Array.isArray(evidence))throw Error('标签依据格式无效');
 for(const [key,item] of Object.entries(evidence)){
  if(!Object.hasOwn(tags,key)||!item||typeof item!=='object'||Array.isArray(item)||
   !['quote','source','model'].every(field=>typeof item[field]==='string'&&item[field].trim())||
   item.quote.length>500||item.source.length>2048||item.model.length>120||!isSourceURL(item.source))
   throw Error('标签依据须含有效来源、简介摘录和模型名');
 }
 return evidence;
}

export function isSourceURL(value) {
 try{return ['https:','http:'].includes(new URL(value).protocol);}catch{return false;}
}
