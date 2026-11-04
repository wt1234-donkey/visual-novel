import {createBasicEditor} from './basic-catalogue-editor.mjs?v=20261104-permissions';
import {workKey,validateStore} from './basic-catalogue-model.mjs';
const $=id=>document.getElementById(id);
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kind={'manual-basic':'网页新增基础身份','new-basic':'待提升基础索引','main-linked':'完整主库已有','dossier-linked':'厂商专题已有','promoted-basic':'主库基础身份已纳入','promoted-dossier':'主库已关联专题','identity-review':'作品与版本身份待核','eligibility-review':'叙事与玩法主次待核','main-registry-linked':'已关联主库身份'};
let entries=[],baseEntries=[],allEntries=[],filtered=[],page=0,editor;
let childrenByMain=new Map();
const selection=new Set();
const size=25;
const nameOrder=new Intl.Collator('zh-Hans-CN',{numeric:true,sensitivity:'base'});
function compareDefaultOrder(a,b){
    const ay=Number.isInteger(a.year)?a.year:Infinity;
    const by=Number.isInteger(b.year)?b.year:Infinity;
    return ay-by||nameOrder.compare(a.title,b.title)||nameOrder.compare(a.id||'',b.id||'');
}
function optionBox(element,values){
    const old=element.value;
    const opts=[element.options[0].outerHTML,...[...new Set(values)].sort((a,b)=>a.localeCompare(b,'zh-Hans-CN')).map(x=>'<option value="'+safe(x)+'">'+safe(x)+'</option>')];
    element.innerHTML=opts.join('');
    if([...element.options].some(x=>x.value===old))element.value=old;
}
function filterAndDraw(){
    const q=$('q').value.trim().normalize('NFKC').toLowerCase(),gp=$('gameplay').value,g=$('group').value,s=$('status').value,year=$('year').value,style=$('style').value;
    filtered=entries.filter(r=>{
      const children=(childrenByMain.get(r._key)||[]);
      const hay=[r.title,...(r.aliases||[]),r.group,...(r.groups||[]),...(r.plotStyles||[]),...children.flatMap(c=>[c.title,...(c.aliases||[])])].join(' ').normalize('NFKC').toLowerCase();
      return (!style||(r.plotStyles||[]).includes(style))&&(!year||(year==='unknown'?!Number.isInteger(r.year):Number.isInteger(r.year)&&r.year===Number(year)))&&(!q||hay.includes(q))&&(!gp||r.gameplay===gp)&&(!g||r.group===g||(r.groups||[]).includes(g))&&(!s||r.status===s);
    });
    page=0;render();
}
function render(){
    const total=filtered.length,n=Math.max(1,Math.ceil(total/size));page=Math.min(Math.max(page,0),n-1);
    const rows=filtered.slice(page*size,(page+1)*size);
    $('rows').innerHTML=rows.map(r=>{
      const alias=(r.aliases||[]).length?'<div class="minor">'+safe(r.aliases.slice(0,3).join(' / '))+'</div>':'';
      const year=Number.isInteger(r.year)?r.year:'—';
      const label=kind[r.status]||'专题已有';
      const link=/^https?:\/\//.test(r.source||'')?'<a href="'+safe(r.source)+'" target="_blank" rel="noopener noreferrer">资料</a>':'待核';
      const children=(childrenByMain.get(r._key)||[]);
      return '<tr><td class="select-cell"><input type="checkbox" data-select="'+safe(r._key)+'" aria-label="选择 '+safe(r.title)+'" '+(selection.has(r._key)?'checked':'')+'></td><td class="title-cell"><button type="button" class="work-title" data-edit="'+safe(r._key)+'">'+safe(r.title)+'</button>'+alias+(children.length?'<div class="minor">含 '+children.length+' 个关联版本</div>':'')+'</td><td data-label="首发年份">'+year+'</td><td data-label="主要玩法">'+safe(r.gameplay)+(r.gameplayNote?'<div class="minor">'+safe(r.gameplayNote)+'</div>':'')+'</td><td data-label="剧情风格">'+((r.plotStyles||[]).map(t=>'<span class="pill">'+safe(t)+'</span>').join(' ')||'<span class="minor">待补充</span>')+'</td><td data-label="厂商关联">'+safe(r.group)+'</td><td data-label="编目状态"><span class="pill">'+safe(label)+'</span>'+(r.reason?'<div class="minor">'+safe(r.reason)+'</div>':'')+(r.matchedWorkId?'<div class="minor">'+safe(r.matchedWorkId)+'</div>':'')+'</td><td data-label="依据">'+link+'</td></tr>';
    }).join('')||'<tr><td colspan="8">未找到符合筛选条件的作品</td></tr>';
    $('count').textContent='找到 '+total+' 条记录，显示第 '+(total? page*size+1:0)+'—'+Math.min((page+1)*size,total)+' 条';
    $('pagination').textContent='第 '+(page+1)+' / '+n+' 页';
    $('prev').disabled=page===0;
    $('next').disabled=page>=n-1;
}
async function start(){
 try{
   const response=await fetch('data/adv-rpg-minimal-index-20261031.json',{cache:'no-store'});
   if(!response.ok)throw Error('HTTP '+response.status);
   const obj=await response.json();
   if(!Array.isArray(obj.records)||!obj.summary)throw Error('档案格式无效');
   entries=obj.records;
   const registryPromise=fetch('data/main-adv-rpg-works-20261031.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('无法读取统一基础库');return r.json();});
   // Editing requires the complete base, never a partially loaded candidate list.
   const loadedRegistry=await registryPromise;
   if(!Array.isArray(loadedRegistry.works)||!loadedRegistry.summary)throw Error('统一基础库格式无效，管理功能未开启');
   try{
     {
       const main=await registryPromise;
       const statusByIndex=new Map(main.works.map(w=>[w.indexId,w.mainPlacement]));
       const identityByIndex=new Map(main.works.map(w=>[w.indexId,w.id]));
       const holding=new Set(main.identityReview.map(w=>w.indexId));
       entries=entries.map(w=>{
         w={...w,matchedWorkId:identityByIndex.get(w.id)||w.matchedWorkId};
         if(holding.has(w.id))return {...w,status:'identity-review'};
         const placement=statusByIndex.get(w.id);
         return placement==='promoted-basic'?{...w,status:'promoted-basic'}:placement==='promoted-dossier'?{...w,status:'promoted-dossier'}:w;
       });
       $('stat-new').textContent=main.summary.promotedBasic.toLocaleString('zh-CN');
       $('stat-linked').textContent=(main.summary.existingComplete+main.summary.promotedDossier).toLocaleString('zh-CN');
     }
   }catch(err){console.warn('主库基础身份层暂不可用',err);}
   for(const [batch,path] of [['batch2','data/adv-rpg-next-studio-review-20261031.json'],['batch3','data/adv-rpg-round3-review-20261031.json']])try{
     const next=await fetch(path,{cache:'no-store'});
     if(next.ok){
       const add=await next.json();
       const normal=t=>String(t||'').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');
       const existing=new Set(entries.map(x=>normal(x.title)+'|'+x.year));
       for(const r of add.records){
         const key=normal(r.title)+'|'+r.year;
         const canonical=r.registryId&&entries.find(x=>x.matchedWorkId===r.registryId);
         if(canonical){
           canonical.aliases=[...new Set([...(canonical.aliases||[]),r.title,...(r.aliases||[])])].filter(t=>t!==canonical.title);
           canonical.groups=[...new Set([...(canonical.groups||[]),canonical.group,r.group])];
           canonical.gameplayNote=canonical.gameplayNote||r.gameplayNote;
           continue;
         }
         if(existing.has(key))continue;
         entries.push({...r,id:batch+'-'+key,matchedWorkId:r.registryId,
           status:r.status==='existing-complete'?'main-linked':r.status==='linked-existing-registry'||r.status==='linked-existing-full-or-dossier'?'main-registry-linked':r.status});
         existing.add(key);
       }
     }
   }catch(err){console.warn('ADV/RPG后续批次审核表尚不可用',err);}
   // The historical minimal index is only an original candidate pool.
   // Pull every subsequently appended identity from the unified basic registry.
   // Existing full/dossier identities are represented once, never doubled by aliases.
   try{
     const registry=await registryPromise;
     const normalizeName=t=>String(t||'').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');
     const representedIds=new Set(entries.flatMap(r=>[r.matchedWorkId,r.registryId].filter(Boolean)));
     const representedIndexIds=new Set(entries.map(r=>r.id));
     const nameYears=new Set(entries.map(r=>normalizeName(r.title)+'|'+r.year));
     for(const w of registry.works){
       const nameKey=normalizeName(w.title)+'|'+w.firstYear;
       if(representedIds.has(w.id)||representedIndexIds.has(w.indexId)||(w.intakePolicy!=='append-without-deduplication'&&nameYears.has(nameKey)))continue;
       const status=w.mainPlacement==='existing-complete'?'main-linked':w.mainPlacement;
       entries.push({
         id:w.indexId,matchedWorkId:w.id,title:w.title,aliases:w.aliases||[],
         year:w.firstYear,gameplay:w.gameplay||'玩法待核',gameplayNote:w.gameplayNote||'',
         group:w.group||'来源关联待核',source:w.source,status,reason:w.intakePolicy==='append-without-deduplication'?('未去重导入 · 来源状态：'+(w.sourceDevelopmentStatus||'未提供')):''
       });
       representedIds.add(w.id);
       representedIndexIds.add(w.indexId);
       nameYears.add(nameKey);
     }
   }catch(err){console.warn('统一基础身份层完整记录暂不可用',err);}
   entries.sort(compareDefaultOrder);
   $('stat-total').textContent=entries.length.toLocaleString('zh-CN');
   try{const mainReg=await registryPromise;$('stat-new').textContent=mainReg.summary.promotedBasic.toLocaleString('zh-CN');$('stat-linked').textContent=(mainReg.summary.promotedDossier+mainReg.summary.existingComplete).toLocaleString('zh-CN')}catch(err){console.warn('主库统计暂不可用',err)}
   if(!$('stat-linked').textContent.match(/[0-9]/))$('stat-linked').textContent=(obj.summary.alreadyMain+obj.summary.alreadyDossier+obj.summary.identityReview).toLocaleString('zh-CN');
   $('stat-groups').textContent=(new Set(entries.flatMap(x=>[x.group,...(x.groups||[])]))).size.toLocaleString('zh-CN');
   const years=[...new Set(entries.map(r=>r.year).filter(Number.isInteger))].sort((a,b)=>a-b);
   $('year').innerHTML='<option value="">全部年份</option><option value="unknown">年份待核</option>'+years.map(y=>'<option value="'+y+'">'+y+' 年</option>').join('');
   optionBox($('gameplay'),entries.map(r=>r.gameplay));
   optionBox($('group'),entries.flatMap(r=>[r.group,...(r.groups||[])]));
   $('q').addEventListener('input',filterAndDraw);
   for(const id of ['year','gameplay','group','status','style'])$(id).addEventListener('change',filterAndDraw);
   $('prev').addEventListener('click',()=>{page--;render()});
   $('next').addEventListener('click',()=>{page++;render()});
   baseEntries=entries;
   try{
     const res=await fetch('data/basic-catalogue-edits.json',{cache:'no-store'});if(!res.ok)throw Error('修改记录 HTTP '+res.status);
     editor=createBasicEditor(baseEntries,validateStore(await res.json()),refreshManaged);
     for(const id of ['basic-add','basic-import','basic-clear','basic-connection'])$(id).disabled=false;
     $('basic-add').addEventListener('click',()=>editor.add());
     $('basic-import').addEventListener('click',()=>editor.importWindow());
     $('basic-merge').addEventListener('click',()=>editor.merge([...selection]));
     $('basic-clear').addEventListener('click',()=>{selection.clear();refreshSelection();render();});
     $('basic-connection').addEventListener('click',()=>editor.connection());
     $('rows').addEventListener('click',e=>{const button=e.target.closest('[data-edit]');if(button)editor.edit(button.dataset.edit);});
     $('rows').addEventListener('change',e=>{const id=e.target.dataset.select;if(id){if(e.target.checked)selection.add(id);else selection.delete(id);refreshSelection();}});
     $('basic-management-status').textContent='修改可保存到网站；支持撤销最近3次操作。剧情风格和版本关系均由人工填写。';
   }catch(err){$('basic-management-status').textContent='基础库修改记录读取失败：'+err.message+'。请刷新重试；为避免显示过期数据，管理功能已停用。';throw err;}
   filterAndDraw();
 }catch(err){$('count').textContent='无法读取基础作品数据：'+err.message;}
}
function refreshSelection(){
 $('basic-selected').textContent='已选择'+selection.size+'部';$('basic-merge').disabled=selection.size<2;
}
function refreshManaged(main,all,store){
 entries=main.sort(compareDefaultOrder);allEntries=all;
 childrenByMain=new Map();for(const w of all)if(w.parentId){if(!childrenByMain.has(w.parentId))childrenByMain.set(w.parentId,[]);childrenByMain.get(w.parentId).push(w);}
 const ids=new Set(entries.map(workKey));for(const id of selection)if(!ids.has(id))selection.delete(id);
 $('stat-total').textContent=entries.length.toLocaleString('zh-CN');
 $('stat-groups').textContent=new Set(entries.map(w=>w.group)).size.toLocaleString('zh-CN');
 const oldYear=$('year').value,years=[...new Set(entries.map(w=>w.year).filter(Number.isInteger))].sort((a,b)=>a-b);
 $('year').innerHTML='<option value="">全部年份</option><option value="unknown">年份待核</option>'+years.map(y=>'<option value="'+y+'">'+y+' 年</option>').join('');$('year').value=years.includes(Number(oldYear))||oldYear==='unknown'?oldYear:'';
 optionBox($('gameplay'),entries.map(r=>r.gameplay));optionBox($('group'),entries.flatMap(r=>[r.group,...(r.groups||[])]));optionBox($('style'),entries.flatMap(r=>r.plotStyles||[]));
 refreshSelection();filterAndDraw();
}
start();
