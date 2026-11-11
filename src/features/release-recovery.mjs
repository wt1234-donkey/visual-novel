const KEY='catalogue-release-recovery-v1';
let pageState={capture:()=>({}),restore:async()=>{}},handling=false;
const editors=new Map();
export const registerPageRecovery=adapter=>{pageState=adapter;};
export const registerDraftEditor=(id,adapter)=>editors.set(id,adapter);
const same=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
function fieldValue(field,initial=false){
 if(['checkbox','radio'].includes(field.type))return initial?field.defaultChecked:field.checked;
 if(field.tagName==='SELECT'){
  let values=Array.from(field.options).filter(option=>initial?option.defaultSelected:option.selected).map(option=>option.value);
  if(initial&&!values.length&&!field.multiple&&field.options.length)values=[field.options[0].value];
  return field.multiple?values:values[0]??'';
 }
 return initial?field.defaultValue:field.value;
}
export function captureChangedFields(container){
 return Array.from(container.querySelectorAll('input,select,textarea')).filter(field=>
  (field.name||field.id)&&!['password','file','hidden'].includes(field.type)&&!/(token|credential|password)/i.test(field.name||field.id)&&field.name!=='confirmed'
 ).map(field=>({name:field.name,id:field.id,type:field.type,option:['checkbox','radio'].includes(field.type)?field.value:null,before:fieldValue(field,true),value:fieldValue(field)})).filter(field=>!same(field.before,field.value));
}
function drafts(){
 return Array.from(document.querySelectorAll('dialog[open]')).map(dialog=>({editor:dialog.id,target:dialog.dataset.recoveryWorkId||'',mode:dialog.dataset.recoveryMode||'',fields:captureChangedFields(dialog),fileSelected:Array.from(dialog.querySelectorAll('input[type=file]')).some(field=>field.files?.length)})).filter(draft=>draft.fields.length||draft.fileSelected);
}
function banner(message,action){
 let node=document.getElementById('catalogue-recovery');
 if(!node){node=document.createElement('aside');node.id='catalogue-recovery';node.setAttribute('role','alert');node.style.cssText='position:sticky;top:0;z-index:10000;padding:12px;background:#fff4d8;color:#493c20;border-bottom:1px solid #d6b365;font:14px/1.6 system-ui';(document.querySelector('dialog[open]')||document.body).prepend(node);}
 const dialog=document.querySelector('dialog[open]');if(dialog&&!dialog.contains(node))dialog.prepend(node);
 node.replaceChildren();const text=document.createElement('span');text.textContent=message;node.append(text);
 if(action){const button=document.createElement('button');button.type='button';button.textContent='保留草稿并恢复新发布';button.style.marginLeft='12px';button.addEventListener('click',action);node.append(button);}
}
function exportRecovery(payload){
 const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='catalogue-recovery-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function installReleaseRecovery(){
 const recover=event=>{
  if(handling)return;
  const next=event.detail?.nextRevision;if(!/^[a-f0-9]{40}$/.test(next||''))return;
  handling=true;
  let payload;
  try{
   payload={schemaVersion:1,path:location.pathname,at:Date.now(),nextRevision:next,state:pageState.capture(),drafts:drafts()};
   const previous=JSON.parse(sessionStorage.getItem(KEY)||'null');
   if(previous?.nextRevision===next&&new URL(location.href).searchParams.get('release')===next&&Date.now()-previous.at<60000){banner('版本恢复尚未完成；当前输入保留，请稍后重试或导出草稿。');handling=false;return;}
   sessionStorage.setItem(KEY,JSON.stringify(payload));
  }catch{banner('无法保存恢复草稿，已停止刷新。当前查询与输入仍在本页，请先导出草稿。');if(payload){const button=document.createElement('button');button.textContent='导出恢复草稿';button.addEventListener('click',()=>exportRecovery(payload));document.getElementById('catalogue-recovery').append(button);}handling=false;return;}
  const go=()=>{const url=new URL(location.href);url.searchParams.set('release',next);location.replace(url.href);};
  if(payload.drafts.some(draft=>draft.fileSelected||!editors.has(draft.editor)||editors.get(draft.editor).canRestore&&!editors.get(draft.editor).canRestore(draft.mode))){
   banner('网站已更新。当前窗口包含尚不能自动恢复的输入，已停止刷新，请先导出草稿。');
   const button=document.createElement('button');button.textContent='导出恢复草稿';button.addEventListener('click',()=>exportRecovery(payload));document.getElementById('catalogue-recovery').append(button);handling=false;return;
  }
  if(payload.drafts.length){banner('网站已更新，未保存输入已保留；恢复后须核对新来源再保存。',go);handling=false;}
  else go();
 };
 window.addEventListener('catalogue-release-change',recover);
 if(window.__catalogueReleaseChange)recover({detail:window.__catalogueReleaseChange});
}
export async function restoreReleaseState(){
 let payload;
 try{payload=JSON.parse(sessionStorage.getItem(KEY)||'null');}catch{return;}
 if(!payload||payload.schemaVersion!==1||payload.path!==location.pathname||Date.now()-payload.at>86400000)return;
 try{
  await pageState.restore(payload.state||{});
  for(const draft of payload.drafts||[]){
   const adapter=editors.get(draft.editor);
   if(!adapter||draft.fileSelected||typeof draft.target!=='string'||draft.target.length>2000||!Array.isArray(draft.fields)||draft.fields.length>500)throw Error('草稿需要手动核对');
   await adapter.open(draft.target,draft.mode);
   const container=document.getElementById(draft.editor);if(!container?.open||container.dataset.recoveryWorkId!==draft.target)throw Error('草稿目标已变化，请先核对作品身份');
   const changes=[];
   for(const saved of draft.fields){
    const field=Array.from(container.querySelectorAll('input,select,textarea')).find(field=>saved.name?field.name===saved.name&&(!['checkbox','radio'].includes(field.type)||field.value===saved.option):field.id===saved.id);
    if(!field||['password','file','hidden'].includes(field.type)||field.name==='confirmed')continue;
    changes.push({field:saved.name||saved.id,latest:fieldValue(field),draft:saved.value});
    if(['checkbox','radio'].includes(field.type))field.checked=!!saved.value;
    else if(field.multiple){for(const option of field.options)option.selected=Array.isArray(saved.value)&&saved.value.includes(option.value);}
    else field.value=String(saved.value??'');
    field.dispatchEvent(new Event('input',{bubbles:true}));field.dispatchEvent(new Event('change',{bubbles:true}));
   }
   for(const box of container.querySelectorAll('[name=confirmed]'))box.checked=false;
   const form=container.querySelector('form');if(!form)throw Error('恢复表单不可用');
   const review=document.createElement('fieldset'),legend=document.createElement('legend'),pre=document.createElement('pre'),label=document.createElement('label'),check=document.createElement('input');
   legend.textContent='恢复草稿：核对当前值与原输入';pre.textContent=JSON.stringify(changes,null,2);pre.style.cssText='white-space:pre-wrap;max-height:180px;overflow:auto';check.type='checkbox';check.required=true;
   label.append(check,document.createTextNode('我已核对当前来源与恢复的输入'));review.append(legend,pre,label);form.prepend(review);
   container.addEventListener('submit',event=>{if(!check.checked){event.preventDefault();event.stopImmediatePropagation();check.reportValidity();}},{capture:true});
  }
  sessionStorage.removeItem(KEY);banner('已恢复到新发布，查询与选择已保留。'+(payload.drafts?.length?'恢复的编辑草稿需核对后保存。':''));
 }catch(error){banner('恢复草稿仍保留：'+error.message+'。请导出核对，当前输入不会自动提交。');const button=document.createElement('button');button.textContent='导出恢复草稿';button.addEventListener('click',()=>exportRecovery(payload));document.getElementById('catalogue-recovery').append(button);}
}
