const $=id=>document.getElementById(id);
const stateLabels={pending:'待审核',approved:'已审核',publishing:'发布中',published:'已发布',rejected:'已退回',failed:'发布失败／冲突'};
const roleLabels={owner:'管理员',editor:'编辑者',reviewer:'审核者',publisher:'发布者'};
const kindLabels={basic:'基础身份',work:'正式作品',management:'资料管理'};
const draftKey='editorial-draft-v1';
let draft,role,ready=false,page=0,busy=false;
function say(text,error=false){$('notice').textContent=text;$('notice').classList.toggle('error',error);}
function node(tag,text='',className=''){
 const el=document.createElement(tag);el.textContent=text;if(className)el.className=className;return el;
}
function addLink(parent,href,label){
 try{
  const url=new URL(href);
  if(!['http:','https:'].includes(url.protocol))return;
  const link=node('a',label);
  link.href=url.href;link.target='_blank';link.rel='noopener noreferrer';
  parent.append(link,' ');
 }catch{}
}
async function api(path,body){
 const res=await fetch('/api/'+path,body===undefined?undefined:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
 if(res.status===401)$('signin').hidden=false;
 const data=await res.json();
 if(!res.ok)throw Error(data.error||'审核服务暂不可用');
 return data;
}
function renderProposal(p){
 const box=node('div');
 box.append(node('h3',kindLabels[p.kind]+' · '+p.reason));
 const sources=node('p','资料来源　');
 if(p.sources.length)for(const [i,url] of p.sources.entries())addLink(sources,url,'来源 '+(i+1)+' ↗');
 else sources.append('此提案未附单独来源');
 box.append(sources);
 const changes=node('details');changes.open=true;
 changes.append(node('summary',p.preview.length+' 项修改前后对比'));
 for(const row of p.preview){
  const diff=node('div','','diff');
  for(const [label,value] of [['修改前',row.before],['修改后',row.after]]){
   const column=node('div');column.append(node('small',label),node('pre',JSON.stringify(value,null,2)??'空'));
   diff.append(column);
  }
  if(row.id)changes.append(node('p',row.id,'muted'));
  changes.append(diff);
 }
 const raw=node('details');
 raw.append(node('summary','核对将执行的实际操作'),node('pre',JSON.stringify(p.change,null,2)));
 box.append(changes,raw);
 return box;
}
function setDraft(input){
 const p=JSON.parse(input);
 if(!p||p.schemaVersion!==1||!kindLabels[p.kind]||!Array.isArray(p.preview)||!Array.isArray(p.sources)||
  new TextEncoder().encode(input).length>55000)throw Error('提案格式不正确，请从资料编辑页重新生成');
 sessionStorage.setItem(draftKey,JSON.stringify(p));
 draft=p;
 $('draft-preview').replaceChildren(renderProposal(p));
 $('submit').disabled=!role;$('clear').disabled=false;
}
function clearDraft(){
 draft=null;sessionStorage.removeItem(draftKey);
 $('draft-preview').replaceChildren(node('p','从作品编辑页打开提案，或恢复已复制的提案。','muted'));
 $('submit').disabled=true;$('clear').disabled=true;
}
function renderQueue(data){
 role=data.role;ready=data.ready;
 $('role').textContent=roleLabels[role];
 $('queue').hidden=false;$('members').hidden=role!=='owner';
 $('submit').disabled=!draft;
 $('review-controls').hidden=!['owner','reviewer'].includes(role)||$('state').value!=='pending';
 $('publish-controls').hidden=!['owner','publisher'].includes(role)||$('state').value!=='approved';
 $('bridge-note').textContent=ready?'发布前会重新校验最新主库资料和冲突。':'发布凭据尚未配置。已审核提案会留在队列中。';
 $('publish').disabled=!ready;
 const box=$('rows');box.replaceChildren();
 if(!data.rows.length)box.append(node('p','此状态下暂无提案。','muted'));
 for(const row of data.rows){
  const item=node('article');
  if(!$('review-controls').hidden||!$('publish-controls').hidden){
   const label=node('label','选择本条提案 ');
   const select=node('input');select.type='checkbox';select.value=row.id;label.append(select);item.append(label);
  }
  item.append(node('p',stateLabels[row.state]+' · '+new Date(row.submittedAt).toLocaleString('zh-CN'),'muted'));
  const detail=node('details');
  detail.append(node('summary',kindLabels[row.proposal.kind]+' · '+row.proposal.reason),renderProposal(row.proposal));
  item.append(detail);
  if(row.reviewedAt)item.append(node('p','核实时间 '+new Date(row.reviewedAt).toLocaleString('zh-CN')+' · '+row.note));
  if(row.batchId&&row.state==='publishing'&&role!=='editor'){
   const sync=node('button','同步发布状态');sync.type='button';
   sync.onclick=()=>run(async()=>{const result=await api('sync',{id:row.batchId});await reload();say(stateLabels[result.state]||'GitHub 正在处理该批次。');});
   item.append(sync);
  }
  if(row.runId)addLink(item,'https://github.com/wt1234-donkey/visual-novel/actions/runs/'+row.runId,'查看发布或冲突日志 ↗');
  box.append(item);
 }
 $('previous').disabled=page===0;$('next').disabled=!data.more;
}
async function reload(){renderQueue(await api('queue?state='+$('state').value+'&page='+page));}
async function run(action){
 if(busy)return;
 busy=true;
 try{await action();}
 catch(error){say(error.message,true);}
 finally{busy=false;}
}
const checked=()=>[...$('rows').querySelectorAll('input:checked')].map(el=>el.value);
$('submit').onclick=()=>run(async()=>{await api('submit',draft);clearDraft();$('state').value='pending';page=0;await reload();say('提案已送审。');});
$('clear').onclick=clearDraft;
$('restore').onclick=()=>run(async()=>{setDraft($('restore-data').value.trim());say('已恢复提案预览。');});
$('reload').onclick=()=>run(reload);
$('state').onchange=()=>{page=0;run(reload);};
$('previous').onclick=()=>{page=Math.max(0,page-1);run(reload);};
$('next').onclick=()=>{page++;run(reload);};
for(const [id,decision] of [['approve','approved'],['reject','rejected']]){
 $(id).onclick=()=>run(async()=>{
  const result=await api('review',{ids:checked(),decision,note:$('note').value});
  $('note').value='';await reload();say('已记录 '+result.ids.length+' 条审核决定。');
 });
}
$('publish').onclick=()=>run(async()=>{const ids=checked();if(!ids.length)throw Error('请先勾选已审核的提案');if(!confirm('发布所选 '+ids.length+' 条已审核提案？'))return;await api('publish',{ids});$('state').value='publishing';page=0;await reload();say('已发起发布。');});
$('member-form').onsubmit=event=>{event.preventDefault();run(async()=>{await api('member',Object.fromEntries(new FormData(event.target)));event.target.reset();say('角色已保存。');});};
try{
 if(location.hash.startsWith('#draft=')){
  setDraft(decodeURIComponent(location.hash.slice(7)));
  history.replaceState(null,'',location.pathname+location.search);
 }else if(sessionStorage.getItem(draftKey))setDraft(sessionStorage.getItem(draftKey));
 else clearDraft();
}catch(error){say(error.message,true);}
run(reload);
