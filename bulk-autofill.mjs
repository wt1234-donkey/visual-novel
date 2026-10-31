import {same,validURL,lines} from './management-model.mjs';
const unique=rows=>[...new Set(rows.filter(x=>typeof x==='string'&&x.trim()).map(x=>x.trim()))];
const text=x=>typeof x==='string'?x.trim():'';
const stringList=x=>Array.isArray(x)?unique(x.map(v=>typeof v==='string'?v:v?.name||'')):[];
export function legacyDefaults(w){return {title:w.title,originalTitle:w.title,year:String(w.firstYear),source:w.source,category:'',subcategory:'',genre:'',synopsis:'',characters:'',notes:'',modes:['待核实'],'interaction-note':'','interaction-sources':w.source,'content-evidence':'','content-source':'',platforms:'',publisher:'',voice:'未核实','release-evidence':'','release-source':''};}
export function prefillBasicValues(w,details=null){
 const v=legacyDefaults(w),sources=unique([w.source,...(w.additionalSources||[]),...(w.interactionSources||[])]).filter(validURL);
 const noteParts=[text(w.notes),w.gameplay?'基础库玩法：'+w.gameplay:'',w.group?'基础库关联品牌／团队（关联不代表发行署名）：'+w.group:'',w.yearBasis?'原作年份依据：'+w.yearBasis:'',text(w.associationNote),text(w.identityNote)];
 Object.assign(v,{originalTitle:text(w.originalTitle)||text(details?.originalTitle)||w.title,category:text(w.category),subcategory:text(w.subcategory),genre:text(w.genre)||text(w.gameplay),synopsis:text(w.synopsis)||text(w.description)||text(w.summary),characters:stringList(w.characters).join('\n'),modes:stringList(w.interactionModes).length?stringList(w.interactionModes):['待核实'],'interaction-note':text(w.interactionNote)||text(w.gameplayNote)||(w.gameplay?'基础库玩法原文：'+w.gameplay+'；具体互动操作尚待核实。':''),'interaction-sources':sources.join('\n')});
 const original=(w.contentVersions||[]).filter(c=>c.basis==='original');
 if(original.length===1&&original[0].firstYear===w.firstYear){const c=original[0];v['content-evidence']=text(c.evidence);v['content-source']=text(c.source);const releases=(w.platformReleases||[]).filter(r=>r.contentVersionId===c.id&&r.releaseRole==='contentDebut'&&r.contentRelation==='original'&&r.year===w.firstYear);if(releases.length&&new Set(releases.map(r=>r.publisher)).size===1&&new Set(releases.map(r=>r.source)).size===1&&releases.every(r=>text(r.platform)&&text(r.publisher)&&text(r.contentNote)&&validURL(r.source))){v.platforms=unique(releases.map(r=>r.platform)).join('\n');v.publisher=releases[0].publisher;v['release-source']=releases[0].source;v['release-evidence']=unique(releases.map(r=>r.contentNote)).join('\n');const voices=unique(releases.map(r=>r.voice));if(voices.length===1)v.voice=voices[0];}}
 if(details?.releaseDate)noteParts.push('来源详情记录的发布日期：'+details.releaseDate+'（平台及地区首发范围仍需核对）');
 if(details?.aliases?.length){const added=details.aliases.filter(a=>a!==w.title&&!(w.aliases||[]).includes(a));if(added.length)noteParts.push('来源详情补充题名／别名：'+added.join('／'));}
 v.notes=unique(noteParts).join('\n');return v;
}
export function autoFillRecord(record,details=record.sourceDetails||null){
 const result=structuredClone(record),incoming=prefillBasicValues(record.identity,details),oldDefaults=legacyDefaults(record.identity),changed=[],preserved=[];
 result.autoFilled??={};
 for(const [key,value]of Object.entries(incoming)){
  const current=result.values[key],blank=Array.isArray(current)?!current.length:typeof current!=='string'||!current.trim();
  const automatic=Object.hasOwn(result.autoFilled,key)?same(current,result.autoFilled[key]):same(current,oldDefaults[key]);
  const hasValue=Array.isArray(value)?value.length>0:Boolean(value);
  if(hasValue&&(blank||automatic)){if(!same(current,value)){result.values[key]=structuredClone(value);changed.push(key);}result.autoFilled[key]=structuredClone(value);}
  else if(hasValue&&!same(current,value))preserved.push(key);
 }
 if(details)result.sourceDetails=structuredClone(details);
 if(changed.length)result.confirmed=false;
 return {record:result,changed,preserved};
}
export function createBasicRecord(work){const values=prefillBasicValues(work);return {identity:structuredClone(work),values,autoFilled:structuredClone(values),confirmed:false};}
export function missingBasicFields(values){const labels={originalTitle:'原名',category:'主分类',subcategory:'细分类',genre:'类型',synopsis:'剧情简介',characters:'主要角色','interaction-note':'玩法说明','content-evidence':'原作内容依据','content-source':'原作内容来源',platforms:'首批平台',publisher:'首批发行署名','release-evidence':'首批发行依据','release-source':'首批发行来源'};return Object.entries(labels).filter(([key])=>!values[key]?.trim()).map(([,label])=>label);}
export function nextMoeDetailURL(w){try{const u=new URL(w.source);if(u.origin==='https://api.nextmoe.dev'&&/^\/v2\/catalog\/works\/\d+\/?$/.test(u.pathname))return u.origin+u.pathname.replace(/\/$/,'')+'?include=titles,refs';}catch{}return null;}
export function normalizeNextMoeDetails(w,payload){
 const url=nextMoeDetailURL(w),id=url?.match(/\/works\/(\d+)/)?.[1];
 if(!url||payload?.object!=='work'||String(payload.id)!==id)throw Error('来源作品身份不匹配，未回填');
 const release=text(payload.release_date);if(release&&Number(release.slice(0,4))!==w.firstYear)throw Error('来源年份与基础身份冲突，未回填');
 const vndb=(payload.refs||[]).filter(r=>r.source==='vndb'&&/^v\d+$/.test(r.external_id)).map(r=>'vndb:'+r.external_id);
 const expected=(w.sourceRefs||[]).filter(r=>/^vndb:v\d+$/.test(r));if(expected.some(r=>!vndb.includes(r)))throw Error('来源 VNDB 身份已变化，未回填');
 const local=payload.localized?.[payload.olang],localized=typeof local==='string'?local:local&&!local.is_machine?local.value:'';
 const originalTitle=text(localized)||text((payload.titles||[]).find(t=>t.lang===payload.olang&&t.title_kind==='official'&&!t.is_machine)?.title);
 const aliases=unique([(payload.display_name),...(payload.titles||[]).filter(t=>!t.is_machine).map(t=>t.title),...Object.values(payload.localized||{}).filter(t=>typeof t==='string'||!t.is_machine).map(t=>typeof t==='string'?t:t.value)]);
 return {source:url,sourceId:id,originalTitle,aliases,releaseDate:release,originalLanguage:text(payload.olang),sourceRefs:vndb,readAt:new Date().toISOString()};
}
export async function fetchSourceDetails(work,fetcher=fetch){const url=nextMoeDetailURL(work);if(!url)throw Error('此来源暂无自动详情接口，基础库已保存的资料仍可自动导入');const response=await fetcher(url,{headers:{Accept:'application/json'},signal:AbortSignal.timeout(15000)});if(!response.ok)throw Error('来源 HTTP '+response.status+'，未改动现有资料');return normalizeNextMoeDetails(work,await response.json());}
