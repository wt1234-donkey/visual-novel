export const EDITORIAL_URL='https://story-atlas-editorial.wwangtao833.chatgpt.site';
export const EDITORIAL_REPO='wt1234-donkey/visual-novel';
export const EDITORIAL_LIMIT=55000;
export const EDITORIAL_BATCH_LIMIT=20;
const editorialKinds=new Set(['basic','work','management']);
const uuidPattern=/^[a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i;
export const editorialId=value=>typeof value==='string'&&uuidPattern.test(value);
const plain=value=>value&&typeof value==='object'&&!Array.isArray(value);
const workId=value=>typeof value==='string'&&/^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,199}$/.test(value)&&!['constructor','prototype'].includes(value);
function editorialURL(value){
 try{return typeof value==='string'&&value.length<=2048&&['https:','http:'].includes(new URL(value).protocol);}catch{return false;}
}
export function validateProposal(p){
 if(!plain(p)||p.schemaVersion!==1||!editorialId(p.id)||!editorialKinds.has(p.kind)||
    typeof p.reason!=='string'||!p.reason.trim()||p.reason.length>2000||
    !Array.isArray(p.sources)||p.sources.length>30||!p.sources.every(editorialURL)||
    !plain(p.change)||!Array.isArray(p.preview)||!p.preview.length||p.preview.length>500)
  throw Error('提案格式无效，请从资料编辑页重新生成');
 if(new TextEncoder().encode(JSON.stringify(p)).length>EDITORIAL_LIMIT)throw Error('提案超过 55 KB，请拆成小批次');
 const c=p.change;
 if(p.kind==='basic'&&(!Number.isSafeInteger(c.expectedRevision)||c.expectedRevision<0||!plain(c.action)||
    !['add','edit','style-update','merge','detach','delete','undo'].includes(c.action.type)))throw Error('基础作品操作无效');
 if(p.kind==='work'&&(!workId(c.workId)||!Number.isSafeInteger(c.expectedRevision)||c.expectedRevision<0||
    (!plain(c.after)&&!editorialId(c.undo))))throw Error('正式作品操作无效');
 if(p.kind==='management'&&(!plain(c.package)||!Array.isArray(c.package.operations)||
    !c.package.operations.length||c.package.operations.length>30))throw Error('资料管理操作无效');
 return p;
}
export function makeProposal(kind,reason,change,preview,sources=[]){
 return validateProposal({schemaVersion:1,id:crypto.randomUUID(),kind,reason:reason.trim(),change,preview,
  sources:[...new Set(sources.filter(editorialURL))].slice(0,30)});
}
export function editorialDraftURL(p){
 return EDITORIAL_URL+'/#draft='+encodeURIComponent(JSON.stringify(validateProposal(p)));
}
export function offerEditorialProposal(element,p){
 const url=editorialDraftURL(p);
 const wrap=document.createElement('p');
 const link=document.createElement('a');
 link.href=url;link.target='_blank';link.rel='noopener noreferrer';link.textContent='打开审核台并确认送审 ↗';
 const copy=document.createElement('button');
 copy.type='button';copy.textContent='复制提案备用';
 copy.addEventListener('click',async()=>{
  try{await navigator.clipboard.writeText(JSON.stringify(p));copy.textContent='已复制';}
  catch{const box=document.createElement('textarea');box.value=JSON.stringify(p);box.readOnly=true;wrap.after(box);box.select();}
 });
 wrap.append(link,' ',copy);
 element.replaceChildren('资料已校验。请在审核台核对差异和证据，再提交。',wrap);
}

export function basicProposalPreview(previous,next,action){
 const event=next.recent.at(-1);
 if(action.type==='undo'){
  return [{before:previous.recent.at(-1),after:'回撤最近一次基础库操作'}];
 }
 const rows=event.changes.map(({id,before,after})=>({id,before,after}));
 for(const id of event.added)rows.push({id,before:null,after:next.additions.find(work=>work.id===id)});
 return rows;
}

export function managementProposal(p){
 const sources=p.operations.flatMap(({after})=>[after?.source,after?.work?.source,...(after?.sources||[]),
  ...(Array.isArray(after)?after.map(row=>row.source):[]),
  ...(after?.platformReleases||[]).map(row=>row.source)]);
 return makeProposal('management',p.reason,{package:p},p.operations.map(op=>({id:op.resource+'/'+op.key,before:op.before,after:op.after})),sources);
}
