import {readReleaseJson} from './src/infrastructure/storage/release-reader.mjs';
import {STYLE_KEYS,STYLE_DIMENSIONS,MAX_WORK_TAGS,styleState,styleList,styleValue,styleLabels} from './basic-style-tags.mjs?v=20261110-flex-tags';
import {STYLE_UPDATE_HEADERS,parseStyleUpdates,planStyleUpdates} from './basic-catalogue-model.mjs?v=20261110-flex-tags';
import {STYLE_QUEUE_KEY,MAX_STYLE_BATCH,buildStyleRequest,parseStyleReview,styleReviewRows} from './basic-style-review.mjs?v=20261110-flex-tags';
import {applyWorkEdits} from './work-edit-model.mjs';

const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const labels=Object.fromEntries(STYLE_KEYS.map(key=>[key,STYLE_DIMENSIONS[key].label]));
const tagList=tags=>STYLE_KEYS.filter(key=>tags[key]).map(key=>labels[key]+' · '+styleList(tags[key]).join('、')).join('；')||'空白';

export function styleInputs(tags={}){
 const selected=styleLabels(tags);
 return '<div class="be-style-picker"><p class="minor" data-style-count role="status">已选 '+selected.length+' / '+MAX_WORK_TAGS+' 个</p><div class="be-grid be-styles">'+STYLE_KEYS.map(key=>{
  const {label,tags:allowed}=STYLE_DIMENSIONS[key],current=styleList(tags[key]);
  return '<details class="be-style-group"'+(current.length?' open':'')+'><summary>'+label+' <span class="minor" data-dimension-count>（'+current.length+'）</span></summary><div class="be-style-choices">'+
   allowed.map(tag=>'<label class="be-candidate"><input type="checkbox" name="style-'+key+'" value="'+safe(tag)+'"'+(current.includes(tag)?' checked':selected.length>=MAX_WORK_TAGS?' disabled':'')+'>'+safe(tag)+'</label>').join('')+'</div></details>';
 }).join('')+'</div></div>';
}

export function readStyleInputs(formData){
 return Object.fromEntries(STYLE_KEYS.flatMap(key=>{
  const values=formData.getAll('style-'+key);
  return values.length?[[key,styleValue(values)]]:[];
 }));
}

export function refreshStylePicker(picker){
 const inputs=[...picker.querySelectorAll('input[type=checkbox]')];
 const count=inputs.filter(input=>input.checked).length;
 picker.querySelector('[data-style-count]').textContent='已选 '+count+' / '+MAX_WORK_TAGS+' 个'+(count===MAX_WORK_TAGS?' · 取消一项后可继续选择':'');
 for(const input of inputs)input.disabled=!input.checked&&count>=MAX_WORK_TAGS;
 for(const group of picker.querySelectorAll('.be-style-group'))group.querySelector('[data-dimension-count]').textContent='（'+group.querySelectorAll('input:checked').length+'）';
}

function download(filename,text,type){
 const url=URL.createObjectURL(new Blob([text],{type}));
 const link=document.createElement('a');
 link.href=url;link.download=filename;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}

const previewControls='<div class="be-actions"><button type="submit">校验并预览</button><button type="button" id="bs-save" class="primary" disabled>确认写入</button></div><div id="bs-preview" class="be-preview"></div>';
const fileInput=(id,ext,label)=>'<label>'+label+'<input type="file" id="'+id+'" accept="'+ext+'"></label>';

export function createStyleWorkbench({dialog,shell,all,hydrate,revision,commit,message,lock,isBusy}){
 const $=selector=>dialog.querySelector(selector);
 let pending=null,scope=[],queue={items:[],issues:[]};
 let queueError='';
 try{
  const saved=JSON.parse(localStorage.getItem(STYLE_QUEUE_KEY));
  if(saved){
   if(!Array.isArray(saved.items)||!Array.isArray(saved.issues))throw Error();
   for(const item of saved.items)parseStyleReview(JSON.stringify({schemaVersion:1,model:item.model,items:[item],issues:[]}));
   queue=saved;
  }
 }catch{queueError='无法读取本机审核队列';}
 const chosen=ids=>{
  const keys=new Set(ids);
  if(!keys.size||keys.size>MAX_STYLE_BATCH)throw Error('请在基础库勾选1至500部作品');
  const works=all().filter(work=>keys.has(work._key));
  if(works.length!==keys.size)throw Error('选择包含不可编辑的作品，请重新选择');
  return works;
 };

 function invalidate(){
  pending=null;
  if($('#bs-save'))$('#bs-save').disabled=true;
  if($('#bs-preview'))$('#bs-preview').replaceChildren();
 }
 function open(title,body){
  invalidate();shell(title,body);
 }
 function bulk(ids){
  scope=ids;
  if(!ids.length||ids.length>MAX_STYLE_BATCH){
   open('批量编辑标签','<p>请先勾选1至500部作品。</p>');return;
  }
  open('批量编辑标签',`<form id="bs-bulk">
   <p>已选择 ${ids.length} 部。可跨维度选择，最终每部最多六个。留空时跳过该维度。</p>
   <label>操作<select name="mode"><option value="append">追加标签（保留原标签）</option><option value="fill">仅补充空白维度</option><option value="set">替换所选维度的标签</option><option value="remove">删除所选标签</option><option value="clear">清空全部特征标签</option></select></label>
   ${styleInputs()}${previewControls}</form>`);
 }
 function csv(ids){
  scope=ids;
  open('CSV 更新已有作品标签',`<form id="bs-csv">
   <p>使用作品 ID 匹配，作品名可留空。维度留空时保留现值，填「清空」移除该维度全部标签。填写多个标签时用顿号「、」分隔，替换该维度现值。每部最多六个，每批最多500部。</p>
   <div class="be-actions"><a href="templates/basic-style-update.csv" download>下载 CSV 空白模板</a>
   <a href="templates/basic-style-update-example.csv" download>下载 CSV 填写示例</a>
   <button type="button" id="bs-csv-export" ${ids.length&&ids.length<=MAX_STYLE_BATCH?'':'disabled'}>导出所选作品的更新模板</button></div>
   <p class="minor">填写示例用一行演示保留、清空和写入三种操作。正式更新前，请换成要修改的作品 ID 和标签。</p>
   ${fileInput('bs-csv-file','.csv,text/csv','导入 UTF-8 CSV')}
   <label>或粘贴 CSV 内容<textarea id="bs-csv-text" rows="7" spellcheck="false"></textarea></label>
   ${previewControls}</form>`);
 }
 function showPreview(rows,reason,reviewSelections){
  const {updates,unchanged}=planStyleUpdates(all(),rows);
  const preview=$('#bs-preview');
  preview.innerHTML='<p>将修改 '+updates.length+' 部，跳过 '+unchanged.length+' 部无实际变化的作品。</p>'+
   '<ul>'+updates.map(({id,title,before,after})=>'<li><strong>'+safe(title)+'</strong> <span class="minor">'+safe(id)+
    '</span><br>当前 '+safe(tagList(before))+'<br>修改后 '+safe(tagList(after))+'</li>').join('')+'</ul>';
  if(updates.length){
   pending={revision:revision(),rows,reason:reason+' '+updates.length+' 部',reviewSelections};
   $('#bs-save').disabled=false;
  }
 }

 function persistQueue(next){
  localStorage.setItem(STYLE_QUEUE_KEY,JSON.stringify(next));
  queue=next;
 }
 function review(ids){
  scope=ids;
  open('AI 标签候选审核',`<form id="bs-review">
   <p>先勾选作品并导出识别请求，在本机运行 Ollama 生成候选 JSON，再导入此处。只为有简介和来源的作品生成请求。候选逐个标签勾选后预览，通过写入的标签附上简介摘录和来源。</p>
   <div class="be-actions"><a href="templates/basic-style-candidates-example.json" download>下载候选 JSON 模板（含示例）</a><button type="button" id="bs-ai-export" ${ids.length&&ids.length<=MAX_STYLE_BATCH?'':'disabled'}>导出所选作品的识别请求</button><a href="data/basic-catalogue-guide.md#ai-标签候选" target="_blank" rel="noopener">查看运行命令</a></div>
   <p class="minor">如需手动整理候选，可从识别请求复制作品 ID、名称、简介和来源，按模板填写模型名及各维度的候选。摘录须出现在现有简介中。</p>
   ${fileInput('bs-ai-file','.json,application/json','导入候选 JSON（待审队列保存在本浏览器）')}
   <button type="button" id="bs-select-review">勾选全部可补充的候选</button>
   <div id="bs-queue" class="be-preview"></div>${previewControls}
   <div class="be-actions"><button type="button" id="bs-reject">退回已勾选的候选</button><button type="button" id="bs-clear-issues">清空待补资料清单</button></div></form>`);
  drawQueue();
  if(queueError)message(queueError,true);
 }

 function drawQueue(){
  const ids=new Set(queue.items.map(item=>item.id));
  const works=new Map(ids.size?all().filter(w=>ids.has(w._key)).map(w=>[w._key,w]):[]);
  $('#bs-queue').innerHTML='<p>待审候选 '+queue.items.length+' 部 · 未生成候选 '+queue.issues.length+' 部</p>'+
   queue.items.map(item=>{
    const work=works.get(item.id),tags=work?styleState(work).tags:{};
    const selected=styleLabels(tags),remaining=MAX_WORK_TAGS-selected.length;
    return '<fieldset data-remaining="'+remaining+'"><legend>'+safe(item.title)+' · '+safe(item.id)+'</legend><p class="minor">模型 '+safe(item.model)+'</p>'+
     item.candidates.map(candidate=>{
      const {dimension,tag,source,quote}=candidate;
      const occupied=selected.includes(tag);
      const note=!work?' · 作品已删除':work.title!==item.title?' · 作品名称已变化':occupied?' · 当前已有此标签':remaining<=0?' · 已有六个标签':'';
      return '<label class="be-candidate"><input type="checkbox" data-work="'+safe(item.id)+'" data-tag="'+safe(tag)+'"'+(note?'':' data-eligible')+'>'+
       '<span>'+safe(labels[dimension]+' · '+tag+note)+'<br><span class="minor">'+safe(quote)+'</span></span></label>'+
       '<a class="minor" href="'+safe(source)+'" target="_blank" rel="noopener noreferrer">查看资料来源 ↗</a>';
     }).join('')+'</fieldset>';
   }).join('')+
   (queue.issues.length?'<details><summary>查看待补资料或识别失败的作品</summary><ul>'+queue.issues.map(item=>'<li>'+safe(item.title)+' · '+safe(item.reason)+'</li>').join('')+'</ul></details>':'');
  $('#bs-select-review').disabled=!$('#bs-queue').querySelector('[data-eligible]');
  $('#bs-reject').disabled=!queue.items.length;
  $('#bs-clear-issues').disabled=!queue.issues.length;
 }
 function reviewSelections(){
  const selected=new Map();
  for(const box of dialog.querySelectorAll('#bs-queue input:checked')){
   if(!selected.has(box.dataset.work))selected.set(box.dataset.work,new Set());
   selected.get(box.dataset.work).add(box.dataset.tag);
  }
  if(!selected.size)throw Error('请先勾选要处理的候选');
  return selected;
 }
 function removeCandidates(selected){
  persistQueue({...queue,items:queue.items.flatMap(item=>{
   const candidates=item.candidates.filter(candidate=>!selected.get(item.id)?.has(candidate.tag));
   return candidates.length?[{...item,candidates}]:[];
  })});
  drawQueue();
 }
 async function loadEvidence(works,options){
  const paths=['games.json','non-rpg-creator-supplement-20261030.json','discovery-editorial.json','work-edit-history.json'];
  const [main,supplement,editorial,edits]=await Promise.all(paths.map(path=>readReleaseJson('data/'+path)));
  const merged=new Map([...supplement.works,...main.works].map(work=>[work.id,work]));
  const {works:archive}=applyWorkEdits({works:[...merged.values()]},edits);
  return buildStyleRequest(works,archive,editorial.works,options);
 }
 async function importReview(file){
  const data=parseStyleReview(await file.text());
  const sourceIds=new Set(data.items.map(item=>item.id));
  if(sourceIds.size){
   const current=await loadEvidence(await hydrate(chosen(sourceIds)),{includeFull:true});
   const byId=new Map(current.items.map(item=>[item.id,item]));
   for(const item of data.items){
    const source=byId.get(item.id);
    if(!source||source.title!==item.title||source.synopsis!==item.synopsis||
     item.candidates.some(candidate=>!source.sources.includes(candidate.source)))
     throw Error('候选与当前简介或来源不一致，请重新导出该批次：'+item.title);
   }
  }
  const incoming=new Set([...data.items,...data.issues].map(item=>item.id));
  const items=[...queue.items.filter(item=>!incoming.has(item.id)),...data.items.map(item=>({...item,model:data.model}))];
  const issues=[...queue.issues.filter(item=>!incoming.has(item.id)),...data.issues];
  if(items.length+issues.length>MAX_STYLE_BATCH)throw Error('本机队列最多保存500部，请先处理现有队列');
  persistQueue({items,issues});
 }

 dialog.addEventListener('input',event=>{if(event.target.closest('#bs-bulk,#bs-csv,#bs-review'))invalidate();});
 dialog.addEventListener('submit',event=>{
  const form=event.target;
  if(!['bs-bulk','bs-csv','bs-review'].includes(form.id))return;
  event.preventDefault();
  if(isBusy())return;
  invalidate();
  try{
   if(form.id==='bs-csv')showPreview(parseStyleUpdates($('#bs-csv-text').value),'CSV 更新标签');
   else if(form.id==='bs-bulk'){
    const data=new FormData(form),mode=data.get('mode'),clear=mode==='clear';
    const tags=clear?Object.fromEntries(STYLE_KEYS.map(key=>[key,null])):readStyleInputs(data);
    if(!Object.keys(tags).length)throw Error('请选择至少一个维度的标签');
    showPreview(chosen(scope).map(w=>({id:w._key,mode:clear?'set':mode,tags})),clear?'批量清空标签':'批量编辑标签');
   }else{
    const selected=reviewSelections();
    showPreview(styleReviewRows(queue.items,selected),'审核 AI 标签',selected);
   }
  }catch(error){message(error.message,true);return;}
  message('请核对预览。');
 });

 dialog.addEventListener('change',async event=>{
  const input=event.target;
  if(!['bs-csv-file','bs-ai-file'].includes(input.id)||!input.files[0]||isBusy())return;
  try{
   invalidate();
   const file=input.files[0];
   if(file.size>5e6)throw Error('文件超过5MB，请分批处理');
   lock(true);
   if(input.id==='bs-csv-file'){
    $('#bs-csv-text').value=await file.text();
    message('已读取 CSV，请校验并预览。');
   }else{
    await importReview(file);
    message('已导入候选，请勾选要审核的标签。');
   }
  }catch(error){message(error.message,true);}
  finally{lock(false);input.value='';if(input.id==='bs-ai-file')drawQueue();}
 });

 dialog.addEventListener('click',async event=>{
  const id=event.target.closest('button')?.id;
  if(!id?.startsWith('bs-')||isBusy())return;
  try{
   if(id==='bs-save'){
    if(!pending||pending.revision!==revision()){
     invalidate();throw Error('基础库已更新，请重新预览');
    }
    const {rows,reason,reviewSelections:selected}=pending;
    if(await commit({type:'style-update',rows},reason)){
     invalidate();
     if(selected){
      try{removeCandidates(selected);}
      catch{message('标签已写入。浏览器队列更新失败，请手动移除已处理的候选。',true);}
     }
    }
   }else if(id==='bs-csv-export'){
    const cells=[STYLE_UPDATE_HEADERS,...chosen(scope).map(w=>[w._key,/^[\s\uFEFF]*[=+@-]/.test(w.title)?'':w.title,...STYLE_KEYS.map(()=> '')])];
    download('basic-style-update.csv','\uFEFF'+cells.map(row=>row.map(cell=>'"'+cell.replaceAll('"','""')+'"').join(',')).join('\r\n')+'\r\n','text/csv;charset=utf-8');
   }else if(id==='bs-ai-export'){
    lock(true);
    const request=await loadEvidence(await hydrate(chosen(scope)));
    download('basic-style-request.json',JSON.stringify(request,null,2)+'\n','application/json');
    message('导出 '+request.items.length+' 部可识别作品，另有 '+request.issues.length+' 部暂未生成识别请求。');
   }else if(id==='bs-select-review'){
    for(const work of dialog.querySelectorAll('#bs-queue [data-remaining]')){
     let remaining=Number(work.dataset.remaining);
     for(const input of work.querySelectorAll('input[data-work]')){
      input.checked=input.hasAttribute('data-eligible')&&remaining>0;
      if(input.checked)remaining--;
     }
    }
    invalidate();
   }else if(id==='bs-reject'){
    removeCandidates(reviewSelections());invalidate();message('已从本机审核队列移除所选候选。');
   }else if(id==='bs-clear-issues'){
    persistQueue({...queue,issues:[]});drawQueue();
   }
  }catch(error){message(error.message,true);}finally{if(id==='bs-ai-export')lock(false);}
 });

 return {bulk,csv,review,invalidate};
}
