import {GAMEPLAY_OPTIONS,manufacturerKey} from './basic-catalogue-filters.mjs?v=20261109-style-tags';
import {createEditClient,TOKEN_SETUP_URL} from './work-edit-api.mjs?v=20261104-permissions';
import {validateStore,valuesOf,applyChange,undoLast,projectEntries,parseImport,workKey} from './basic-catalogue-model.mjs?v=20261109-style-tags';
import {styleName,styleState} from './basic-style-tags.mjs';
import {createStyleWorkbench,styleInputs,readStyleInputs} from './basic-style-workbench.mjs?v=20261109-index';
import {withBasicDetails} from './basic-catalogue-index.mjs';
import {makeProposal,offerEditorialProposal,basicProposalPreview,EDITORIAL_URL} from './editorial-proposal.mjs';
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const HISTORY='data/basic-catalogue-edits.json';
const randomId=()=>crypto.randomUUID?.()||Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
export function createBasicEditor(base,initial,onChange,loadDetails=async()=>new Map()){
 let snapshot={store:validateStore(initial),sha:null},actor='',busy=false,pendingImport=null,returnFocus=null,entries=[];
 const clientFor=token=>createEditClient(token,fetch,{historyPath:HISTORY,validate:validateStore});let client=clientFor('');
 const dialog=document.createElement('dialog');dialog.id='basic-editor';document.body.append(dialog);
 const $=s=>dialog.querySelector(s);
 const all=()=>entries;
 const get=id=>entries.find(w=>w._key===id);
 async function hydrate(rows){
  const details=await loadDetails(rows);
  return rows.map(row=>withBasicDetails(row,details.get(row.slot),snapshot.store));
 }
 async function prepareBase(action){
  if(action.type==='add')return base;
  const ids=new Set(action.rows?.map(row=>row.id)||action.ids||[action.id]);
  if(action.mainId)ids.add(action.mainId);
  if(action.type==='merge')for(const row of entries)if(action.ids.includes(row.parentId))ids.add(row._key);
  const targets=base.filter(row=>ids.has(workKey(row)));
  const details=await loadDetails(targets);
  return base.map(row=>details.has(row.slot)?{...row,...details.get(row.slot)}:row);
 }
 function update(){
  entries=projectEntries(base,snapshot.store,{includeChildren:true});
  onChange(entries.filter(w=>!w.parentId),entries,snapshot.store);document.getElementById('basic-connection').textContent=actor?'已连接 '+actor:'连接写入权限';}
 function message(s,error=false){$('#be-message').textContent=s;$('#be-message').className='be-message'+(error?' error':'');}
 function close(){if(!busy){dialog.close();returnFocus?.focus();}}
 function shell(title,body){
  if(busy)return;if(!dialog.open)returnFocus=document.activeElement;pendingImport=null;
  dialog.innerHTML=`<div class="be-head"><h2>${safe(title)}</h2><button type="button" data-close aria-label="关闭窗口">×</button></div>
   <details class="be-auth"><summary>管理员直连 · ${actor?safe(actor):'GitHub 备用入口'}</summary><p class="minor">凭证仅在当前页面内存保留，刷新后清除。</p><ol class="minor"><li>使用拥有仓库权限的 GitHub 账号；Resource owner 应为 <b>wt1234-donkey</b>。</li><li>Repository access 选择 <b>Only select repositories</b>，再选择 <b>visual-novel</b>。Public repositories 只有读取权限。</li><li>Repository permissions 中将 <b>Contents</b> 设为 <b>Read and write</b>，然后生成凭证。</li></ol><p class="minor">连接成功表示账号和读取校验通过，GitHub 会在保存时核验凭证的实际写入权限。</p><p><a href="${TOKEN_SETUP_URL}" target="_blank" rel="noopener noreferrer">创建仓库专用凭证 ↗</a></p><label>GitHub 写入凭证<input id="be-token" type="password" autocomplete="off" spellcheck="false"></label><div class="be-actions"><button id="be-connect" type="button">连接</button><button id="be-disconnect" type="button" ${actor?'':'disabled'}>断开</button><button id="be-refresh" type="button">重新读取网站修改</button></div></details>
   <div id="be-message" class="be-message" role="status" aria-live="polite"></div>${body}`;
  dialog.setAttribute('aria-label',title);if(!dialog.open)dialog.showModal();
 }
 const disabledBefore=new Map();
 function lock(v){if(!v&&!busy)return;busy=v;dialog.querySelectorAll('button,input,select,textarea').forEach(el=>{if(v){disabledBefore.set(el,el.disabled);el.disabled=true;}else{el.disabled=disabledBefore.get(el)??false;}});if(!v)disabledBefore.clear();dialog.setAttribute('aria-busy',String(v));if(!v&&$('#be-disconnect'))$('#be-disconnect').disabled=!actor;}
 async function commit(action,reason,undo=false){
  if(busy)return false;
  try{
   const meta={id:randomId(),at:new Date().toISOString(),actor:actor||'送审预览',reason,expectedRevision:snapshot.store.revision};
   lock(true);message('正在检查最新记录并保存…');
   const next=undo?undoLast(snapshot.store,snapshot.store.revision):applyChange(snapshot.store,await prepareBase(action),action,meta);
   if(!actor){
    const change=undo?{type:'undo'}:action;
    const sources=[change.values?.source,change.relation?.source,...(change.works||[]).map(w=>w.source),
     ...(change.rows||[]).flatMap(row=>Object.values(row.evidence||{}).map(item=>item.source))];
    const proposal=makeProposal('basic',reason,{expectedRevision:meta.expectedRevision,action:change},
     basicProposalPreview(snapshot.store,next,change),sources);
    message('');offerEditorialProposal($('#be-message'),proposal);
    return false;
   }
   const live=await client.read();if(JSON.stringify(live.store)!==JSON.stringify(snapshot.store))throw Error('基础库已在其他页面修改。请先“重新读取网站修改”，再核对并保存；当前输入仍保留');
   let result;
   try{result=await client.write(next,live.sha,'Basic catalogue: '+reason.slice(0,100));}
   catch(error){if(error.status)throw error;try{const actual=await client.read();if(JSON.stringify(actual.store)!==JSON.stringify(next))throw error;result={sha:actual.sha};}catch{throw error;}}
   snapshot={store:next,sha:result.sha};update();message('已保存到网站，当前页面已更新；其他设备在网站发布后刷新即可看到。');return true;
  }catch(e){message(e.message,true);if(e.code==='PERMISSION_DENIED'||e.code==='NOT_FOUND')$('.be-auth').open=true;return false;}finally{lock(false);}
 }
 const input=(key,label,value,extra='')=>`<label>${label}<input name="${key}" value="${safe(value)}" ${extra}></label>`;
 async function edit(id=null){
  let w=id?get(id):null;
  if(id&&!w)return;
  if(w&&Number.isInteger(w.slot)){
   shell('读取作品详情', '<p>正在读取该作品的资料…</p>');
   lock(true);
   try{[w]=await hydrate([w]);}
   catch(error){message(error.message,true);return;}
   finally{lock(false);}
  }
  const v=w?valuesOf(w):{title:'',firstYear:null,group:'',gameplay:'',plotStyles:[],source:''};
  const {tags,legacy}=styleState(v);
  const children=w?all().filter(x=>x.parentId===id):[];
  shell(w?'修改作品 · '+w.title:'直接添加作品',`<form id="be-edit" data-id="${safe(id||'')}"><div class="be-grid">
   ${input('title','作品名称',v.title,'required maxlength="500"')}
   <label>首发年份（未知可留空）<input name="firstYear" type="number" min="1970" max="${new Date().getFullYear()+10}" step="1" list="be-years" value="${v.firstYear??''}"><datalist id="be-years">${Array.from({length:new Date().getFullYear()+11-1970},(_,i)=>`<option value="${1970+i}"></option>`).join('')}</datalist></label>
   ${input('group','厂商／创作主体',v.group,'required list="be-groups" maxlength="500"')}<datalist id="be-groups">${[...new Map(base.filter(x=>x.group).map(x=>[manufacturerKey(x.group),x.group])).values()].map(x=>`<option value="${safe(x)}"></option>`).join('')}</datalist>
   ${input('gameplay','主要玩法',v.gameplay,'required list="be-gameplay" maxlength="500"')}<datalist id="be-gameplay">${GAMEPLAY_OPTIONS.map(x=>`<option value="${safe(x)}"></option>`).join('')}</datalist></div>
   <fieldset><legend>剧情风格标签 · 六个维度各选一项</legend>${styleInputs(tags)}
   <p class="minor">资料不足的维度可留空。</p>
   ${Object.entries(v.plotTagEvidence||{}).map(([key,{quote,source,model}])=>'<p class="minor">'+safe(tags[key])+' · '+safe(quote)+' · '+safe(model)+' <a href="'+safe(source)+'" target="_blank" rel="noopener noreferrer">资料来源 ↗</a></p>').join('')}
   ${legacy.length?'<p class="minor">旧标签待整理：'+safe(legacy.join('、'))+'</p><label class="be-candidate"><input type="checkbox" name="removeLegacy">移除这些待整理旧标签</label>':''}</fieldset>
   ${input('source','资料来源（可选）',v.source,'type="url"')}
   ${input('reason','修改说明',w?'更正基础作品资料':'直接添加基础作品','required maxlength="300"')}
   <div class="be-actions"><button class="primary" type="submit">${actor?(w?'保存修改':'添加到基础库'):'预览并送审'}</button>${w?'<button type="button" class="danger" data-delete="'+safe(id)+'">删除作品</button>':''}${w?.parentId?'<button type="button" data-detach="'+safe(id)+'">解除与主作品的合并</button>':''}</div></form>
   ${w?.parentId?`<p class="minor">所属主作品：${safe(get(w.parentId)?.title||w.parentId)} · ${safe(w.relation?.label)} · ${safe(w.relation?.note||'内容关系待核')}</p>`:''}
   ${children.length?'<h3>关联版本（'+children.length+'）</h3><ul class="be-version-list">'+children.map(c=>`<li><button type="button" data-edit="${safe(c._key)}">${safe(c.title)}</button> <span class="minor">${c.year??'年份待核'} · ${safe(c.relation?.label)} · ${safe(({unverified:'内容关系待核',same:'同内容版本',added:'新增内容版本'})[c.relation?.type])}</span>${c.relation?.note?'<p>'+safe(c.relation.note)+'</p>':''}</li>`).join('')+'</ul>':''}`);
 }
 function importWindow(){shell('导入作品信息',`<p class="minor">使用固定模板，CSV为UTF-8编码；每次最多500部。先校验并预览，再确认写入。相同名称和年份的记录会提示冲突。</p><div class="be-actions"><a href="templates/basic-works-import.csv" download>下载 CSV 模板</a><a href="templates/basic-works-import.json" download>下载 JSON 模板</a><a href="data/basic-catalogue-guide.md" target="_blank">填写说明</a></div><label>选择文件<input type="file" id="be-file" accept=".csv,.json,text/csv,application/json"></label><label>或粘贴模板格式的内容<textarea id="be-import-text" rows="7"></textarea></label><label>格式<select id="be-format"><option value="csv">CSV</option><option value="json">JSON</option></select></label><div class="be-actions"><button id="be-validate" type="button">校验并预览</button><button id="be-import-confirm" class="primary" type="button" disabled>确认导入</button></div><div id="be-import-preview"></div>`);}
 function merge(ids){
  const selected=all().filter(w=>ids.includes(w._key)&&!w.parentId);if(selected.length<2){shell('合并作品','<p>请先勾选至少两部作品，再选择主作品。</p>');return;}
  shell('合并为主作品的不同版本',`<form id="be-merge"><p>选择保留在列表中的主作品，其他作品归入它的关联版本。各版本名称、年份和来源保留，可以解除合并。</p><label>主作品<select name="mainId">${selected.map(w=>`<option value="${safe(w._key)}">${safe(w.title)} · ${w.year??'年份待核'}</option>`).join('')}</select></label><input type="hidden" name="ids" value="${safe(JSON.stringify(selected.map(w=>w._key)))}"><p class="minor">本次共选择 ${selected.length} 部作品。若被合并作品已有版本，这些版本也会归入所选主作品。</p><label>版本内容关系<select name="relation"><option value="unverified">待核实（暂不认定新增内容）</option><option value="same">已核实：相同内容／普通移植或再版</option><option value="added">已核实：新增内容</option></select></label><label>具体差异或合并依据<textarea name="note" rows="3"></textarea></label>${input('source','支持版本关系的来源（已核实关系必填）','','type="url"')}<p class="minor">每个版本沿用其原作品名。新增剧情、路线、人物、素材等须写清具体差异；普通移植不自动视为新增内容。</p><button type="submit" class="primary">确认合并所选作品</button></form>`);
 }
 function connection(){shell('写入连接与最近操作',`<p>编辑后可预览并送审。管理员可在上方使用原有直连入口。</p><p><a href="${EDITORIAL_URL}" target="_blank" rel="noopener noreferrer">查看编目审核队列 ↗</a></p><div id="be-history">${[...snapshot.store.recent].reverse().map(r=>`<p>${safe(r.reason)}<br><span class="minor">${safe(r.at)} · ${safe(r.actor)}</span></p>`).join('')||'<p class="minor">还没有网页修改记录。</p>'}</div><button type="button" id="be-undo" ${snapshot.store.recent.length?'':'disabled'}>撤销最近一次操作</button>`);}
 dialog.addEventListener('cancel',e=>{e.preventDefault();close();});
 dialog.addEventListener('input',e=>{if(['be-import-text','be-format'].includes(e.target.id)){pendingImport=null;$('#be-import-confirm').disabled=true;}});
 dialog.addEventListener('change',async e=>{if(e.target.id==='be-file'){try{const file=e.target.files[0];if(!file)return;if(file.size>5e6)throw Error('文件超过5MB，请分批导入');$('#be-import-text').value=await file.text();$('#be-format').value=file.name.toLowerCase().endsWith('.json')?'json':'csv';pendingImport=null;$('#be-import-confirm').disabled=true;message('文件已读取，请校验并预览');}catch(err){message(err.message,true);}}});
 dialog.addEventListener('submit',async e=>{
  const form=e.target;if(!['be-edit','be-merge'].includes(form.id))return;
  e.preventDefault();if(busy)return;const f=new FormData(form);
  if(form.id==='be-edit'){
   const id=form.dataset.id,plotTags=readStyleInputs(f);
   let previous=id?get(id):null;
   if(previous&&Number.isInteger(previous.slot)){
    lock(true);
    try{[previous]=await hydrate([previous]);}
    catch(error){message(error.message,true);return;}
    finally{lock(false);}
   }
   const {legacy}=styleState(previous||{});
   const plotStyles=f.has('removeLegacy')?[]:legacy.filter(tag=>!Object.values(plotTags).includes(styleName(tag)));
   const plotTagEvidence=Object.fromEntries(Object.entries(previous?.plotTagEvidence||{}).filter(([key])=>plotTags[key]===previous.plotTags[key]));
   const v={title:String(f.get('title')).trim(),firstYear:f.get('firstYear')?Number(f.get('firstYear')):null,group:String(f.get('group')).trim(),gameplay:String(f.get('gameplay')).trim(),plotStyles,plotTags,plotTagEvidence,source:String(f.get('source')||'').trim()};
   const saved=await commit(id?{type:'edit',id,values:v}:{type:'add',works:[{id:'manual-'+randomId(),...v}]},String(f.get('reason')));
   if(saved&&!id&&getLastAdded(v.title)){form.dataset.id=getLastAdded(v.title)._key;form.querySelector('button[type=submit]').textContent='保存修改';}
  }else if(form.id==='be-merge'){
   const mainId=String(f.get('mainId')),ids=JSON.parse(f.get('ids')).filter(id=>id!==mainId);
   if(await commit({type:'merge',mainId,ids,relation:{type:f.get('relation'),label:'关联版本',note:String(f.get('note')||'').trim(),source:String(f.get('source')||'').trim()}},'合并 '+ids.length+' 部作品为关联版本'))form.querySelector('button[type=submit]').disabled=true;
  }
 });
 function getLastAdded(title){return all().find(w=>w.title===title&&w._key===snapshot.store.additions.at(-1)?.id);}
 dialog.addEventListener('click',async e=>{
  const b=e.target.closest('button');if(!b||busy)return;
  if(b.hasAttribute('data-close'))close();
  else if(b.dataset.edit)edit(b.dataset.edit);
  else if(b.id==='be-connect'){
   const token=$('#be-token').value.trim();$('#be-token').value='';try{lock(true);const nextClient=clientFor(token),login=await nextClient.connect(),fresh=await nextClient.read();client=nextClient;actor=login;snapshot=fresh;update();$('summary').textContent='写入权限 · '+actor;$('.be-auth').open=false;message('已连接账号 '+actor+'，并读取最新基础库修改。保存时会核验当前凭证的 Contents 写入权限。');}catch(err){message(err.message,true);}finally{lock(false);}
  }else if(b.id==='be-disconnect'){client=clientFor('');actor='';update();$('summary').textContent='写入权限 · 连接 GitHub';$('.be-auth').open=true;b.disabled=true;message('已断开连接');}
  else if(b.id==='be-refresh'){try{lock(true);snapshot=await client.read();update();message('已读取最新网站修改。当前表单输入保留，请核对后保存。');}catch(err){message(err.message,true);}finally{lock(false);}}
  else if(b.dataset.delete){if(confirm('删除“'+get(b.dataset.delete)?.title+'”？可通过最近操作撤销。')){if(await commit({type:'delete',id:b.dataset.delete},'删除作品 '+get(b.dataset.delete)?.title)){close();}}}
  else if(b.dataset.detach){if(await commit({type:'detach',id:b.dataset.detach},'解除版本合并'))edit(b.dataset.detach);}
  else if(b.id==='be-undo'){if(confirm('撤销最近一次“'+snapshot.store.recent.at(-1)?.reason+'”？'))if(await commit(null,'撤销最近操作',true))connection();}
  else if(b.id==='be-validate'){
   try{pendingImport=null;$('#be-import-confirm').disabled=true;const rows=parseImport($('#be-import-text').value,$('#be-format').value);pendingImport=rows.map(v=>({id:'manual-'+randomId(),...v}));applyChange(snapshot.store,base,{type:'add',works:pendingImport},{actor:'preview',reason:'预览导入',expectedRevision:snapshot.store.revision});$('#be-import-preview').innerHTML='<p>校验通过，将添加 '+rows.length+' 部。预览前20部：</p><ul>'+rows.slice(0,20).map(w=>'<li>'+safe(w.title)+' · '+(w.firstYear??'年份待核')+' · '+safe(w.group)+' · '+safe(w.gameplay)+' · '+safe([...Object.values(styleState(w).tags),...styleState(w).legacy].join('、'))+'</li>').join('')+'</ul>';$('#be-import-confirm').disabled=false;message('请核对预览，再确认导入');}catch(err){pendingImport=null;$('#be-import-preview').textContent='';message(err.message,true);}
  }else if(b.id==='be-import-confirm'&&pendingImport){if(await commit({type:'add',works:pendingImport},'模板导入 '+pendingImport.length+' 部作品')){pendingImport=null;b.disabled=true;}}
 });
 const styles=createStyleWorkbench({dialog,shell,all,hydrate,revision:()=>snapshot.store.revision,commit,message,lock,isBusy:()=>busy});
 update();return {styles,edit,add:()=>edit(),importWindow,merge,connection,getChildren:id=>all().filter(w=>w.parentId===id)};
}
