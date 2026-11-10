// A work can use up to six controlled tags across any combination of dimensions.
export const MAX_WORK_TAGS=6;
export const STYLE_DIMENSIONS = {
 tone: {label:'剧情基调', tags:['喜剧','悲剧','轻松','黑暗','温情','感伤','黑色幽默','唯美','严肃','忧郁','浪漫','怪诞','冷峻','荒凉']},
 emotion: {label:'情绪体验', tags:['治愈','催泪','致郁','压抑','热血','燃系','惊悚','恐怖','紧张','感动','孤独感','不安','希望感','怀旧','沉浸感']},
 expression: {label:'叙事表达', tags:['群像','意识流','荒诞','讽刺','元叙事','实验性','哲思','史诗','寓言','象征','纪实风格','诗意表达','留白']},
 relationship: {label:'人物关系', tags:['恋爱','纯爱','亲情','友情','百合','耽美','三角关系','病娇','师徒','搭档','宿敌','家族关系','羁绊','群体对立']},
 theme: {label:'故事题材', tags:['科幻','奇幻','历史','战争','犯罪','末世','悬疑','推理','心理','复仇','生存','冒险','超自然','武侠','赛博朋克','日常','青春','成长','社会议题','政治斗争','身份认同','记忆与失忆','时间旅行','宗教与信仰','伦理困境','侦探调查','神话传说','都市传说','职场','体育','音乐','灵异','魔幻现实']},
 content: {label:'内容提示', tags:['成人向','色情','NTR','乱伦','背德','禁忌关系','猎奇','暴力','血腥','虐待','性暴力','自伤与自杀','成瘾','歧视','战争创伤','身体恐怖']},
 perspective: {label:'叙事视角', tags:['第一人称','第二人称','第三人称','多视角','全知视角','限制视角','不可靠叙述者','旁观者视角','非人类视角']},
 structure: {label:'叙事结构', tags:['线性叙事','非线性叙事','倒叙','插叙','多线并行','多结局','单一结局','章节式','单元剧','框架叙事','循环叙事','碎片化叙事','开放式结局','分支叙事','多周目解锁']},
 setting: {label:'故事背景', tags:['校园','都市','乡村','架空世界','异世界','近未来','太空','反乌托邦','蒸汽朋克','封闭空间','战时社会','古代','近现代','当代','平行世界','虚拟世界','废土','历史架空']}
};
export const STYLE_GROUPS = Object.fromEntries(Object.values(STYLE_DIMENSIONS).map(({label,tags})=>[label,tags]));
export const STYLE_OPTIONS = Object.values(STYLE_GROUPS).flat();
export const STYLE_KEYS = Object.keys(STYLE_DIMENSIONS);
const normalize = value=>String(value??'').normalize('NFKC').trim().toLowerCase();
const aliases = new Map([
 ...STYLE_OPTIONS.map(tag=>[normalize(tag),tag]),
 ['疗愈','治愈'],['治癒','治愈'],['暗黑','黑暗'],['寝取られ','NTR'],
 ['第一人称叙事','第一人称'],['第二人称叙事','第二人称'],['第三人称叙事','第三人称'],['多重视角','多视角']
]);
export const styleName = value=>aliases.get(normalize(value))||String(value??'').trim();
const dimensionsByTag = new Map(STYLE_KEYS.flatMap(key=>STYLE_DIMENSIONS[key].tags.map(tag=>[tag,key])));
export const styleDimension = tag=>dimensionsByTag.get(styleName(tag));
export const styleList = value=>Array.isArray(value)?value:typeof value==='string'?[value]:[];
export const styleLabels = tags=>Object.values(tags||{}).flatMap(styleList);
// Keep the established scalar encoding when only one tag is present.
export const styleValue = list=>list.length===1?list[0]:list;

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
 const selected=styleLabels(tags);
 return {tags,legacy:legacy.filter(tag=>!selected.includes(styleName(tag)))};
}

export function validateStyleTags(tags, {allowClear=false}={}) {
 if(!tags||typeof tags!=='object'||Array.isArray(tags))throw Error('标签须按维度填写');
 for(const [key,value] of Object.entries(tags)){
  if(!Object.hasOwn(STYLE_DIMENSIONS,key))throw Error('未知的标签维度：'+key);
  if(value===null&&allowClear)continue;
  const list=styleList(value),{label,tags:allowed}=STYLE_DIMENSIONS[key];
  if(!list.length||new Set(list).size!==list.length||list.some(tag=>!allowed.includes(tag)))
   throw Error(label+'须选用该维度词表中的标签，且不能重复');
 }
 if(styleLabels(tags).length>MAX_WORK_TAGS)throw Error('每部作品最多选择'+MAX_WORK_TAGS+'个标签');
 return tags;
}

function evidenceTag(key,tags){
 const values=styleList(tags[key]);
 if(Object.hasOwn(STYLE_DIMENSIONS,key))return values.length===1?values[0]:undefined;
 const dimension=styleDimension(key);
 return dimension&&styleList(tags[dimension]).includes(key)?key:undefined;
}
export function styleEvidenceEntries(tags,evidence={}){
 return Object.entries(evidence).map(([key,item])=>[evidenceTag(key,tags),item]).filter(([tag])=>tag);
}
export function packStyleEvidence(tags,evidence){
 return Object.fromEntries(styleLabels(tags).filter(tag=>evidence.has(tag)).map(tag=>{
  const key=styleDimension(tag);
  return [styleList(tags[key]).length===1?key:tag,evidence.get(tag)];
 }));
}
export function validateStyleEvidence(evidence,tags) {
 if(!evidence||typeof evidence!=='object'||Array.isArray(evidence))throw Error('标签依据格式无效');
 const seen=new Set();
 for(const [key,item] of Object.entries(evidence)){
  const tag=evidenceTag(key,tags);
  if(!tag||seen.has(tag)||!item||typeof item!=='object'||Array.isArray(item)||
   !['quote','source','model'].every(field=>typeof item[field]==='string'&&item[field].trim())||
   item.quote.length>500||item.source.length>2048||item.model.length>120||!isSourceURL(item.source))
   throw Error('标签依据须对应所选标签，并含有效来源、简介摘录和模型名');
  seen.add(tag);
 }
 return evidence;
}

export function isSourceURL(value) {
 try{return ['https:','http:'].includes(new URL(value).protocol);}catch{return false;}
}
