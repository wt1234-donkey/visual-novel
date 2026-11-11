import {GAMEPLAY_OPTIONS,manufacturerKey} from './basic-catalogue-filters.mjs?v=20261111-architecture';
import {createBasicRepository,TOKEN_SETUP_URL} from './src/infrastructure/github/basic-repository.mjs';
import {createCatalogueService} from './src/application/catalogue/service.mjs';
import {valuesOf,versionGroup,parseImport,reconcileBasicEdit} from './basic-catalogue-model.mjs?v=20261111-architecture';
import {styleName,styleState,styleLabels,styleEvidenceEntries,packStyleEvidence} from './basic-style-tags.mjs?v=20261111-architecture';
import {createStyleWorkbench,styleInputs,readStyleInputs,refreshStylePicker} from './basic-style-workbench.mjs?v=20261111-architecture';
import {withBasicDetails} from './basic-catalogue-index.mjs?v=20261111-architecture';
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const randomId=()=>crypto.randomUUID?.()||Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join('');
export function createBasicEditor(base,initial,onChange,loadDetails=async()=>new Map(),{sourceLease=null}={}){
 if(!sourceLease)throw Error('索引缺少来源版本，请刷新页面后重试');
 let actor='',busy=false,pendingImport=null,returnFocus=null,entries=[],catalogueView,editBaseline=null,historyCursor=null,historyRequest=0;
 const clientFor=token=>createBasicRepository(token,fetch,{sourceLease});
 const service=createCatalogueService({base,initial,repository:clientFor(''),loadDetails,makeMeta:()=>({id:randomId(),at:new Date().toISOString()})});
 const dialog=document.createElement('dialog');dialog.id='basic-editor';document.body.append(dialog);
 const $=s=>dialog.querySelector(s);
 const all=()=>entries;
 const get=id=>catalogueView.byId.get(id);
 async function hydrate(rows){
  const details=await loadDetails(rows);
  return rows.map(row=>withBasicDetails(row,details.get(row.slot),service.snapshot.store));
 }
 function update(){
  actor=service.actor;catalogueView=service.view;
  entries=catalogueView.all;
  onChange(catalogueView.entries,entries,service.snapshot.store,catalogueView);document.getElementById('basic-connection').textContent=actor?'直接保存已连接 · '+actor:'连接 GitHub 直接保存';}
 function message(s,error=false){$('#be-message').textContent=s;$('#be-message').className='be-message'+(error?' error':'');}
 function close(){if(!busy){historyRequest++;dialog.close();returnFocus?.focus();}}
 function shell(title,body){
  if(busy)return;historyRequest++;if(!dialog.open)returnFocus=document.activeElement;pendingImport=null;editBaseline=null;
  dialog.innerHTML=`<div class="be-head"><h2>${safe(title)}</h2><button type="button" data-close aria-label="关闭窗口">×</button></div>
   <details class="be-auth"><summary>${actor?'已连接 GitHub · '+safe(actor):'首次保存前：连接 GitHub 写入权限'}</summary><p class="minor">基础身份库取消人工送审。连接后，作品修改、合并与标签操作直接写入仓库，无须另外审核。为保护仓库，公开页面不能匿名写入；凭证只保存在当前页面内存，刷新即清除。</p><ol class="minor"><li>使用有写入权限的 GitHub 账号，Resource owner 选择 <b>wt1234-donkey</b>。</li><li>Repository access 选择 <b>Only select repositories</b> → <b>visual-novel</b>。</li><li>Repository permissions 中将 <b>Contents</b> 设为 <b>Read and write</b>。</li></ol><p><a href="${TOKEN_SETUP_URL}" target="_blank" rel="noopener noreferrer">创建仅限本仓库的写入凭证 ↗</a></p><label>GitHub 写入凭证<input id="be-token" type="password" autocomplete="off" spellcheck="false"></label><div class="be-actions"><button id="be-connect" type="button">连接并启用直接保存</button><button id="be-disconnect" type="button" ${actor?'':'disabled'}>断开</button><button id="be-refresh" type="button">同步 GitHub 最新修改</button></div></details>
   <div id="be-message" class="be-message" role="status" aria-live="polite"></div>${body}`;
  for(const picker of dialog.querySelectorAll('.be-style-picker'))refreshStylePicker(picker);
  dialog.setAttribute('aria-label',title);if(!dialog.open)dialog.showModal();
 }
 const disabledBefore=new Map();
 function lock(v){if(!v&&!busy)return;busy=v;dialog.querySelectorAll('button,input,select,textarea').forEach(el=>{if(v){disabledBefore.set(el,el.disabled);el.disabled=true;}else{el.disabled=disabledBefore.get(el)??false;}});if(!v)disabledBefore.clear();dialog.setAttribute('aria-busy',String(v));if(!v&&$('#be-disconnect'))$('#be-disconnect').disabled=!actor;}
 async function commit(action,reason,undo=false){
  if(busy)return false;
  try{
   if(!actor){
    message('尚未连接 GitHub 写入权限。请展开上方授权区连接账号，再点击原来的保存按钮即可直接写入；当前表单不会清空。',true);
    $('.be-auth').open=true;
    $('#be-token')?.focus();
    return false;
   }
   lock(true);message('正在核验并直接保存到 GitHub…');
   await service.execute(action,reason,{undo});
   update();message('已提交 GitHub 主分支，当前页面数据已更新。Pages 公开网站须在 Actions 构建和部署成功后才更新；请核对发布状态。');return true;
  }catch(e){message(e.message,true);if(['PERMISSION_DENIED','NOT_FOUND','INVALID_TOKEN'].includes(e.code))$('.be-auth').open=true;return false;}finally{lock(false);}
 }
 const input=(key,label,value,extra='')=>`<label>${label}<input name="${key}" value="${safe(value)}" ${extra}></label>`;
 async function edit(id=null){
  let w=id?get(id):null;
  if(id&&!w)return false;
  if(w&&Number.isInteger(w.slot)){
   shell('读取作品详情', '<p>正在读取该作品的资料…</p>');
   lock(true);
   try{[w]=await hydrate([w]);}
   catch(error){message('作品详情读取失败：'+error.message,true);return false;}
   finally{lock(false);}
  }
  const v=w?valuesOf(w):{title:'',firstYear:null,group:'',gameplay:'',plotStyles:[],source:''};
  const {tags,legacy}=styleState(v);
  const archived=id?service.snapshot.store.records[id]?.legacyPlotStyles:undefined;
  const children=w?all().filter(x=>x.parentId===id):[];
  shell(w?'修改作品 · '+w.title:'直接添加作品',`<form id="be-edit" data-id="${safe(id||'')}"><div class="be-grid">
   ${input('title','作品名称',v.title,'required maxlength="500"')}
   <label>首发年份（未知可留空）<input name="firstYear" type="number" min="1900" max="2200" step="1" list="be-years" value="${v.firstYear??''}"><datalist id="be-years">${Array.from({length:new Date().getFullYear()+11-1900},(_,i)=>`<option value="${1900+i}"></option>`).join('')}</datalist></label>
   <label>年份状态<select name="yearStatus">${[['unverified','待核实'],['published','已发行'],['planned','计划发行']].map(([value,label])=>`<option value="${value}" ${v.yearStatus===value||!v.yearStatus&&value==='unverified'?'selected':''}>${label}</option>`).join('')}</select><span class="minor">年份留空表示未知；未来年份不会自动视为已发行。</span></label>
   ${input('group','厂商／创作主体',v.group,'required list="be-groups" maxlength="500"')}<datalist id="be-groups">${[...new Map(base.filter(x=>x.group).map(x=>[manufacturerKey(x.group),x.group])).values()].map(x=>`<option value="${safe(x)}"></option>`).join('')}</datalist>
   ${input('gameplay','主要玩法',v.gameplay,'required list="be-gameplay" maxlength="500"')}<datalist id="be-gameplay">${GAMEPLAY_OPTIONS.map(x=>`<option value="${safe(x)}"></option>`).join('')}</datalist></div>
   <fieldset><legend>作品特征标签 · 跨维度最多六个</legend>${styleInputs(tags)}
   <p class="minor">同一维度可选多个标签，资料不足时可少选。叙事视角指故事由谁讲述。</p>
   ${styleEvidenceEntries(tags,v.plotTagEvidence).map(([tag,{quote,source,model}])=>'<p class="minor">'+safe(tag)+' · '+safe(quote)+' · '+safe(model)+' <a href="'+safe(source)+'" target="_blank" rel="noopener noreferrer">资料来源 ↗</a></p>').join('')}
   ${archived?.length?'<p class="minor">历史标签参考（同维度冲突）：'+safe(archived.join('、'))+'</p>':''}
   ${legacy.length?'<p class="minor">历史标签参考：'+safe(legacy.join('、'))+'</p><label class="be-candidate"><input type="checkbox" name="removeLegacy">移除这些待整理旧标签</label>':''}</fieldset>
   ${input('source','资料来源（可选）',v.source,'type="url"')}
   ${input('reason','修改说明',w?'更正基础作品资料':'直接添加基础作品','required maxlength="300"')}
   <div class="be-actions"><button class="primary" type="submit">${w?'直接保存修改':'直接添加到基础库'}</button>${w?'<button type="button" class="danger" data-delete="'+safe(id)+'">删除作品</button>':''}${w?.parentId?'<button type="button" data-detach="'+safe(id)+'">解除与主作品的合并</button>':''}${w&&((w.parentId)||children.length)?'<button type="button" data-view="'+safe(w.parentId||id)+'">查看版本与来源详情</button>':''}</div></form>
   ${w?.parentId?`<p class="minor">所属主作品：${safe(get(w.parentId)?.title||w.parentId)} · ${safe(w.relation?.label)} · ${safe(w.relation?.note||'内容关系待核')}</p>`:''}
   ${children.length?'<h3>关联版本（'+children.length+'）</h3><ul class="be-version-list">'+children.map(c=>`<li><button type="button" data-edit="${safe(c._key)}">${safe(c.title)}</button> <span class="minor">${c.year??'年份待核'} · ${safe(c.relation?.label)} · ${safe(({unverified:'内容关系待核',same:'同内容版本',added:'新增内容版本'})[c.relation?.type])}</span>${c.relation?.note?'<p>'+safe(c.relation.note)+'</p>':''}</li>`).join('')+'</ul>':''}`);
  editBaseline={id:id||'',revision:service.snapshot.store.revision,values:structuredClone(v)};
  return true;
 }

 const versionRelationLabels={unverified:'内容关系待核',same:'已核实：相同内容',added:'已核实：新增内容'};
 const sourceLink=(url,label)=>/^https?:\/\//i.test(url||'')?
  '<a href="'+safe(url)+'" target="_blank" rel="noopener noreferrer">'+safe(label)+'</a>':'待核';
 function versionCard(w,isMain){
  const styles=[...styleLabels(styleState(w).tags),...(styleState(w).legacy||[])];
  const relation=w.relation||{};
  const source=sourceLink(w.source,'打开资料来源 ↗');
  const heading='<div class="be-version-heading"><strong>'+safe(w.title)+'</strong><span class="pill">'+
   (isMain?'主作品资料':safe(versionRelationLabels[relation.type]||'关联版本'))+'</span></div>';
  const meta='<p class="minor">'+safe(w.year??'年份待核')+' · '+safe(w.group||'创作主体待核')+
   ' · '+safe(w.gameplay||'玩法待核')+'</p>';
  const tags=styles.length?'<p class="minor">作品特征：'+safe([...new Set(styles)].join('、'))+'</p>':'';
  const aliases=w.aliases?.length?'<p class="minor">别名：'+safe(w.aliases.join(' / '))+'</p>':'';
  const evidence=isMain?'':'<p>版本内容关系：'+safe(versionRelationLabels[relation.type]||'内容关系待核')+'</p>'+
   (relation.note?'<p class="be-version-note">'+safe(relation.note)+'</p>':'')+
   '<p class="minor">关系依据：'+sourceLink(relation.source,'查看关系依据 ↗')+'</p>';
  return '<article class="be-version-card">'+heading+meta+aliases+tags+
   '<p class="minor">本条来源：'+source+'</p>'+evidence+
   '<div class="be-actions"><button type="button" data-edit="'+safe(w._key)+'">'+
   (isMain?'编辑主作品':'编辑此版本')+'</button></div></article>';
 }
 async function view(id){
  const root=get(id);
  if(!root||root.parentId||busy)return;
  const group=versionGroup(all(),id);
  shell('作品详情 · '+root.title,'<p class="minor">正在读取主作品与版本的资料…</p>');
  lock(true);
  let details=group,error='';
  try{details=await hydrate(group);}
  catch(e){error=e.message;}
  finally{lock(false);}
  const intro='<p class="minor">基础库列表仅显示一个主作品。这里保留各来源／版本独立的名称、年份、玩法、厂商及依据；“内容关系待核”的记录不自动认定为新增内容版本。</p>';
  shell('作品详情 · '+root.title,intro+
   (error?'<p class="be-message error">部分详情读取失败：'+safe(error)+'；下方为已缓存的信息。</p>':'')+
   '<h3>版本与来源记录（'+details.length+'）</h3>'+details.map((w,i)=>versionCard(w,i===0)).join(''));
 }
 function importWindow(){shell('导入作品信息',`<p class="minor">使用固定模板，CSV为UTF-8编码；每次最多500部。先校验并预览，再确认写入。相同名称和年份的记录会提示冲突。</p><div class="be-actions"><a href="templates/basic-works-import.csv" download>下载 CSV 模板</a><a href="templates/basic-works-import.json" download>下载 JSON 模板</a><a href="data/basic-catalogue-guide.md" target="_blank">填写说明</a></div><label>选择文件<input type="file" id="be-file" accept=".csv,.json,text/csv,application/json"></label><label>或粘贴模板格式的内容<textarea id="be-import-text" rows="7"></textarea></label><label>格式<select id="be-format"><option value="csv">CSV</option><option value="json">JSON</option></select></label><div class="be-actions"><button id="be-validate" type="button">校验并预览</button><button id="be-import-confirm" class="primary" type="button" disabled>确认导入</button></div><div id="be-import-preview"></div>`);}
 function merge(ids){
  const selected=all().filter(w=>ids.includes(w._key)&&!w.parentId);if(selected.length<2){shell('合并作品','<p>请先勾选至少两部作品，再选择主作品。</p>');return;}
  shell('合并为主作品的不同版本',`<form id="be-merge"><p>选择保留在列表中的主作品，其他作品归入它的关联版本。各版本名称、年份和来源保留，可以解除合并。</p><label>主作品<select name="mainId">${selected.map(w=>`<option value="${safe(w._key)}">${safe(w.title)} · ${w.year??'年份待核'}</option>`).join('')}</select></label><input type="hidden" name="ids" value="${safe(JSON.stringify(selected.map(w=>w._key)))}"><p class="minor">本次共选择 ${selected.length} 部作品。若被合并作品已有版本，这些版本也会归入所选主作品。</p><label>版本内容关系<select name="relation"><option value="unverified">待核实（暂不认定新增内容）</option><option value="same">已核实：相同内容／普通移植或再版</option><option value="added">已核实：新增内容</option></select></label><label>具体差异或合并依据<textarea name="note" rows="3"></textarea></label>${input('source','支持版本关系的来源（已核实关系必填）','','type="url"')}<p class="minor">每个版本沿用其原作品名。新增剧情、路线、人物、素材等须写清具体差异；普通移植不自动视为新增内容。</p><button type="submit" class="primary">确认合并所选作品</button></form>`);
 }
 async function historyRows(before=Infinity,append=false){
  const request=++historyRequest;$('#be-history-more').disabled=true;$('#be-history-retry').hidden=true;
  if(!append)$('#be-history').textContent='正在读取操作历史…';
  try{
  const page=await service.history({before,limit:20});
  if(request!==historyRequest||!$('#be-history'))return;
  historyCursor=page.nextBefore;
  const events=page.events;
  const markup=events.map(event=>'<article class="be-history-item"><strong>r'+event.revision+' · '+safe(event.reason)+'</strong><p class="minor">'+safe(event.at)+' · '+safe(event.actor)+' · '+(event.changes.length+event.added.length+event.removed.length)+' 条记录'+(event.undoOf?' · 撤销操作':'')+'</p><details><summary>查看字段变化</summary><pre>'+safe(JSON.stringify({changes:event.changes,added:event.added,removed:event.removed},null,2))+'</pre></details></article>').join('');
  if(append)$('#be-history').insertAdjacentHTML('beforeend',markup);
  else $('#be-history').innerHTML=markup||'<p class="minor">尚无迁移后的操作。迁移前的快捷记录：</p>'+[...service.snapshot.store.recent].reverse().map(event=>'<p>'+safe(event.reason)+'<br><span class="minor">'+safe(event.at)+' · '+safe(event.actor)+'</span></p>').join('');
  $('#be-history-coverage').textContent='完整变更记录从 r'+page.baselineRevision+' 起保留；此前记录可通过 GitHub 提交历史追溯。';
  $('#be-history-more').disabled=historyCursor===null;
  }catch(error){if(request===historyRequest&&$('#be-history')){message('历史暂未读取：'+error.message,true);$('#be-history-retry').hidden=false;}}
 }
 function connection(){
  shell('GitHub 直接保存与操作历史',`<p>作品修改、合并、添加与标签更新直接保存到仓库。最近三次操作可快捷撤销；完整记录保留修改前后值，撤销也会留下独立记录。</p><p id="be-history-coverage" class="minor"></p><div id="be-history"></div><button type="button" id="be-history-retry" hidden>重试读取历史</button><button type="button" id="be-history-more">查看更早记录</button><button type="button" id="be-undo" ${service.snapshot.store.recent.length?'':'disabled'}>撤销最近一次操作</button>`);
  historyRows();
 }
 dialog.addEventListener('cancel',e=>{e.preventDefault();close();});
 dialog.addEventListener('input',e=>{const picker=e.target.closest('.be-style-picker');if(picker)refreshStylePicker(picker);if(['be-import-text','be-format'].includes(e.target.id)){pendingImport=null;$('#be-import-confirm').disabled=true;}});
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
   const {legacy,tags:previousTags}=styleState(previous||{});
   const plotStyles=f.has('removeLegacy')?[]:legacy.filter(tag=>!styleLabels(plotTags).includes(styleName(tag)));
   const plotTagEvidence=packStyleEvidence(plotTags,new Map(styleEvidenceEntries(previousTags,previous?.plotTagEvidence)));
   let v={title:String(f.get('title')).trim(),firstYear:f.get('firstYear')?Number(f.get('firstYear')):null,yearStatus:f.get('firstYear')?String(f.get('yearStatus')||'unverified'):'unknown',group:String(f.get('group')).trim(),gameplay:String(f.get('gameplay')).trim(),plotStyles,plotTags,plotTagEvidence,source:String(f.get('source')||'').trim()};
   if(id&&editBaseline?.id===id&&editBaseline.revision!==service.snapshot.store.revision){
    try{v=reconcileBasicEdit(editBaseline.values,v,valuesOf(previous));}
    catch(error){message(error.message,true);return;}
   }
   const saved=await commit(id?{type:'edit',id,values:v}:{type:'add',works:[{id:'manual-'+randomId(),...v}]},String(f.get('reason')));
   if(saved&&id){
    if(await edit(id))message('最新作品资料已显示。已提交 GitHub；Pages 发布状态仍须在 Actions 中确认。');
   }else if(saved&&!id&&getLastAdded(v.title)){
    if(await edit(getLastAdded(v.title)._key))message('新作品已保存并显示；Pages 发布状态仍须在 Actions 中确认。');
   }
  }else if(form.id==='be-merge'){
   const mainId=String(f.get('mainId')),ids=JSON.parse(f.get('ids')).filter(id=>id!==mainId);
   if(await commit({type:'merge',mainId,ids,relation:{type:f.get('relation'),label:'关联版本',note:String(f.get('note')||'').trim(),source:String(f.get('source')||'').trim()}},'合并 '+ids.length+' 部作品为关联版本'))form.querySelector('button[type=submit]').disabled=true;
  }
 });
 function getLastAdded(title){return all().find(w=>w.title===title&&w._key===service.snapshot.store.additions.at(-1)?.id);}
 dialog.addEventListener('click',async e=>{
  const b=e.target.closest('button');if(!b||busy)return;
  if(b.hasAttribute('data-close'))close();
  else if(b.dataset.view)await view(b.dataset.view);
  else if(b.dataset.edit)edit(b.dataset.edit);
  else if(b.id==='be-connect'){
   const token=$('#be-token').value.trim();$('#be-token').value='';try{lock(true);const login=await service.connect(clientFor(token));update();$('.be-auth summary').textContent='已连接 GitHub · '+actor;$('.be-auth').open=false;message('已连接 '+actor+'，同步至修改记录 r'+service.snapshot.store.revision+'。'+(editBaseline&&editBaseline.revision!==service.snapshot.store.revision?'当前编辑表单来源于旧版本，保存时将检查字段冲突并保留其他字段的最新修改。':'可以直接保存，无须人工送审。'));}catch(err){message(err.message,true);}finally{lock(false);}
  }else if(b.id==='be-disconnect'){service.disconnect(clientFor(''));update();$('.be-auth summary').textContent='首次保存前：连接 GitHub 写入权限';$('.be-auth').open=true;b.disabled=true;message('已断开写入权限；当前资料仍可查看、编辑，重新授权后可保存。');}
  else if(b.id==='be-history-retry')historyRows();
  else if(b.id==='be-history-more'&&historyCursor!==null)historyRows(historyCursor,true);
  else if(b.id==='be-refresh'){try{lock(true);await service.sync();update();message('已同步 GitHub 修改记录 r'+service.snapshot.store.revision+'。当前表单输入保留；'+(editBaseline&&editBaseline.revision!==service.snapshot.store.revision?'保存时将检查字段冲突，不会静默覆盖其他页面的新修改。':'核对后可直接保存。'));}catch(err){message(err.message,true);}finally{lock(false);}}
  else if(b.dataset.delete){if(confirm('删除“'+get(b.dataset.delete)?.title+'”？可通过最近操作撤销。')){if(await commit({type:'delete',id:b.dataset.delete},'删除作品 '+get(b.dataset.delete)?.title)){close();}}}
  else if(b.dataset.detach){if(await commit({type:'detach',id:b.dataset.detach},'解除版本合并'))edit(b.dataset.detach);}
  else if(b.id==='be-undo'){if(confirm('撤销最近一次“'+service.snapshot.store.recent.at(-1)?.reason+'”？'))if(await commit(null,'撤销最近操作',true))connection();}
  else if(b.id==='be-validate'){
   try{pendingImport=null;$('#be-import-confirm').disabled=true;const rows=parseImport($('#be-import-text').value,$('#be-format').value);pendingImport=rows.map(v=>({id:'manual-'+randomId(),...v}));service.preview({type:'add',works:pendingImport});$('#be-import-preview').innerHTML='<p>校验通过，将添加 '+rows.length+' 部。预览前20部：</p><ul>'+rows.slice(0,20).map(w=>'<li>'+safe(w.title)+' · '+(w.firstYear??'年份待核')+' · '+safe(w.group)+' · '+safe(w.gameplay)+' · '+safe([...styleLabels(styleState(w).tags),...styleState(w).legacy].join('、'))+'</li>').join('')+'</ul>';$('#be-import-confirm').disabled=false;message('请核对预览，再确认导入');}catch(err){pendingImport=null;$('#be-import-preview').textContent='';message(err.message,true);}
  }else if(b.id==='be-import-confirm'&&pendingImport){if(await commit({type:'add',works:pendingImport},'模板导入 '+pendingImport.length+' 部作品')){pendingImport=null;b.disabled=true;}}
 });
 const styles=createStyleWorkbench({dialog,shell,all,hydrate,revision:()=>service.snapshot.store.revision,commit,message,lock,isBusy:()=>busy});
 update();return {styles,edit,view,add:()=>edit(),importWindow,merge,connection,getChildren:id=>all().filter(w=>w.parentId===id)};
}
