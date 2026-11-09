import {normalizeFilterText,manufacturerKey,manufacturerNames,createManufacturerIndex,matchingManufacturers,manufacturerOptions,REGION_LABELS,gameplayKeys,gameplayOptions,gameplayDisplay,styleName,styleState,styleDimension,STYLE_DIMENSIONS,styleOptions,LEGACY_STYLE_PREFIX,MISSING_STYLE,pageIndex} from './basic-catalogue-filters.mjs?v=20261109-style-tags';
import {createBasicEditor} from './basic-catalogue-editor.mjs?v=20261109-style-tags';
import {workKey,validateStore} from './basic-catalogue-model.mjs?v=20261109-style-tags';
const $=id=>document.getElementById(id);
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kind={'manual-basic':'网页新增基础身份','new-basic':'待提升基础索引','main-linked':'完整主库已有','dossier-linked':'厂商专题已有','promoted-basic':'主库基础身份已纳入','promoted-dossier':'主库已关联专题','identity-review':'作品与版本身份待核','eligibility-review':'叙事与玩法主次待核','main-registry-linked':'已关联主库身份'};
let entries=[],baseEntries=[],allEntries=[],filtered=[],page=0,editor;
let childrenByMain=new Map(),manufacturerIndex=[],filterCache=null,regionMetadata={entries:[]};
const selection=new Set();
const size=25;
const nameOrder=new Intl.Collator('zh-Hans-CN',{numeric:true,sensitivity:'base'});
function compareDefaultOrder(a,b){
    const ay=Number.isInteger(a.year)?a.year:Infinity;
    const by=Number.isInteger(b.year)?b.year:Infinity;
    return ay-by||nameOrder.compare(a.title,b.title)||nameOrder.compare(a.id||'',b.id||'');
}
function drawManufacturers(){
 const selected=$('group').value,{total,visible}=manufacturerOptions(manufacturerIndex,{region:$('group-region').value,query:$('group-query').value},selected);
 $('group').innerHTML='<option value="">全部匹配厂商</option>'+Object.entries(REGION_LABELS).map(([region,label])=>{const rows=visible.filter(item=>item.region===region);return rows.length?'<optgroup label="'+label+'">'+rows.map(item=>'<option value="'+safe(item.key)+'">'+safe(item.label)+'（'+item.count+'）</option>').join('')+'</optgroup>':'';}).join('');
 $('group').value=visible.some(item=>item.key===selected)?selected:'';
 $('group-count').textContent='匹配 '+total.toLocaleString('zh-CN')+' 个厂商'+(total>visible.length?'；列出其中 '+visible.length+' 个，请输入名称缩小范围':'')+'。大小写重复项已合并。';
}
function rebuildFilters(){
 manufacturerIndex=createManufacturerIndex(entries,regionMetadata);
 filterCache=new Map(entries.map(r=>{
  const {tags,legacy}=styleState(r),styles=Object.values(tags);
  const search=normalizeFilterText([r.title,...(r.aliases||[]),...manufacturerNames(r),...styles,...legacy,...(childrenByMain.get(r._key)||[]).flatMap(c=>[c.title,...(c.aliases||[])])].join(' '));
  return [r,{search,manufacturers:[...new Set(manufacturerNames(r).map(manufacturerKey))],gameplay:gameplayKeys(r.gameplay),styles,legacy:legacy.map(styleName)}];
 }));
 const gameplay=$('gameplay').value,styles=$('style').value;
 $('gameplay').innerHTML='<option value="">全部玩法</option>'+gameplayOptions(entries).map(item=>'<option value="'+safe(item.key)+'">'+safe(item.label)+'（'+item.count+'）</option>').join('');
 if([...$('gameplay').options].some(o=>o.value===gameplay))$('gameplay').value=gameplay;
 const missing=entries.filter(r=>!filterCache.get(r).styles.length).length;
 $('style').innerHTML='<option value="">全部风格</option><option value="'+MISSING_STYLE+'">待补充（'+missing+'）</option>'+styleOptions(entries).map(group=>'<optgroup label="'+safe(group.label)+'">'+group.options.map(item=>'<option value="'+safe(item.key)+'">'+safe(item.label)+'（'+item.count+'）</option>').join('')+'</optgroup>').join('');
 if([...$('style').options].some(o=>o.value===styles))$('style').value=styles;
 $('stat-groups').textContent=manufacturerIndex.length.toLocaleString('zh-CN');
 for(const [key,label] of Object.entries(REGION_LABELS))$('group-region-'+key).textContent=label+'（'+manufacturerIndex.filter(item=>item.region===key).length+'）';
 drawManufacturers();
}
function filterAndDraw(){
 if(!filterCache)return;
 const q=normalizeFilterText($('q').value),gp=$('gameplay').value,g=$('group').value,s=$('status').value,year=$('year').value,style=$('style').value;
 const region=$('group-region').value,query=$('group-query').value.trim(),allowed=region||query?new Set(matchingManufacturers(manufacturerIndex,{region,query}).map(item=>item.key)):null;
 filtered=entries.filter(r=>{const cached=filterCache.get(r);return (!style||(style===MISSING_STYLE?!cached.styles.length:style.startsWith(LEGACY_STYLE_PREFIX)?cached.legacy.includes(style.slice(LEGACY_STYLE_PREFIX.length)):cached.styles.includes(style)))&&(!year||(year==='unknown'?!Number.isInteger(r.year):Number.isInteger(r.year)&&r.year===Number(year)))&&(!q||cached.search.includes(q))&&(!gp||cached.gameplay.includes(gp))&&(!(g||allowed)||cached.manufacturers.some(key=>(!g||key===g)&&(!allowed||allowed.has(key))))&&(!s||r.status===s);});
 page=0;render();
}
function jumpToPage(value){try{page=pageIndex(value,Math.max(1,Math.ceil(filtered.length/size)));render();$('count').scrollIntoView?.({behavior:'smooth',block:'start'});}catch(error){for(const suffix of ['','-bottom'])$('page-error'+suffix).textContent=error.message;}}
function render(){
    const total=filtered.length,n=Math.max(1,Math.ceil(total/size));page=Math.min(Math.max(page,0),n-1);
    const rows=filtered.slice(page*size,(page+1)*size);
    $('rows').innerHTML=rows.map(r=>{
      const alias=(r.aliases||[]).length?'<div class="minor">'+safe(r.aliases.slice(0,3).join(' / '))+'</div>':'';
      const year=Number.isInteger(r.year)?r.year:'—';
      const label=kind[r.status]||'专题已有';
      const link=/^https?:\/\//.test(r.source||'')?'<a href="'+safe(r.source)+'" target="_blank" rel="noopener noreferrer">资料</a>':'待核';
      const children=(childrenByMain.get(r._key)||[]);
      const {tags,legacy}=styleState(r);
      const stylePills=Object.values(tags).map(tag=>'<span class="pill" title="'+safe(STYLE_DIMENSIONS[styleDimension(tag)].label)+'">'+safe(tag)+'</span>').join(' ');
      const styleDetail=(stylePills||'<span class="minor">待补充</span>')+(legacy.length?'<div class="minor">旧标签待整理：'+safe(legacy.join('、'))+'</div>':'');
      return '<tr><td class="select-cell"><input type="checkbox" data-select="'+safe(r._key)+'" aria-label="选择 '+safe(r.title)+'" '+(selection.has(r._key)?'checked':'')+'></td><td class="title-cell"><button type="button" class="work-title" data-edit="'+safe(r._key)+'">'+safe(r.title)+'</button>'+alias+(children.length?'<div class="minor">含 '+children.length+' 个关联版本</div>':'')+'</td><td data-label="首发年份">'+year+'</td><td data-label="主要玩法">'+safe(gameplayDisplay(r.gameplay))+(/待核|候选/.test(r.gameplay)?'<div class="minor">玩法细节待核</div>':'')+(/仅专题|关联/.test(r.gameplay)?'<div class="minor">'+safe(r.gameplay)+'</div>':'')+(r.gameplayNote?'<div class="minor">'+safe(r.gameplayNote)+'</div>':'')+'</td><td data-label="剧情风格">'+styleDetail+'</td><td data-label="厂商关联">'+safe(r.group)+'</td><td data-label="编目状态"><span class="pill">'+safe(label)+'</span>'+(r.reason?'<div class="minor">'+safe(r.reason)+'</div>':'')+(r.matchedWorkId?'<div class="minor">'+safe(r.matchedWorkId)+'</div>':'')+'</td><td data-label="依据">'+link+'</td></tr>';
    }).join('')||'<tr><td colspan="8">未找到符合筛选条件的作品</td></tr>';
    $('basic-select-page').disabled=!editor||!rows.length;
    $('basic-select-filtered').disabled=!editor||!total||total>500;
    $('count').textContent='找到 '+total+' 条记录，显示第 '+(total? page*size+1:0)+'—'+Math.min((page+1)*size,total)+' 条';
    for(const suffix of ['','-bottom']){
      $('pagination'+suffix).textContent='第 '+(page+1)+' / '+n+' 页';
      $('prev'+suffix).disabled=page===0;$('next'+suffix).disabled=page>=n-1;
      $('page-number'+suffix).max=n;$('page-number'+suffix).value=page+1;$('page-number'+suffix).disabled=!total;$('page-go'+suffix).disabled=!total;
      $('page-error'+suffix).textContent='';
    }
}
async function start(){
 try{
   const regions=fetch('data/basic-manufacturer-regions.json',{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('地区索引不可用');return r.json();}).then(data=>{if(data.schemaVersion!==1||!Array.isArray(data.entries))throw Error('地区索引格式无效');return data;}).catch(error=>{console.warn('厂商地区索引暂不可用',error);$('filter-note').textContent='厂商地区索引暂不可用，厂商暂归地区待核；仍可按名称筛选。';return {entries:[]};});
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
       const identityByIndex=new Map(main.works.map(w=>[w.indexId,w]));
       const holding=new Set(main.identityReview.map(w=>w.indexId));
       entries=entries.map(w=>{
         const identity=identityByIndex.get(w.id);
         w={...w,matchedWorkId:identity?.id||w.matchedWorkId,linkedRecordId:identity?.linkedRecordId,
          ...(identity?.plotTags?{plotTags:identity.plotTags}:{}),...(identity?.plotStyles?{plotStyles:identity.plotStyles}:{}),
          ...(identity?.plotTagEvidence?{plotTagEvidence:identity.plotTagEvidence}:{})};
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
         group:w.group||'来源关联待核',plotStyles:w.plotStyles||[],plotTags:w.plotTags,plotTagEvidence:w.plotTagEvidence,linkedRecordId:w.linkedRecordId,source:w.source,status,reason:w.intakePolicy==='append-without-deduplication'?('未去重导入 · 来源状态：'+(w.sourceDevelopmentStatus||'未提供')):''
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
   regionMetadata=await regions;
   $('q').addEventListener('input',filterAndDraw);
   for(const id of ['year','gameplay','group','status','style'])$(id).addEventListener('change',filterAndDraw);
   $('group-query').addEventListener('input',()=>{drawManufacturers();filterAndDraw();});
   $('group-region').addEventListener('change',()=>{drawManufacturers();filterAndDraw();});
   $('filter-reset').addEventListener('click',()=>{for(const id of ['q','year','gameplay','group','status','style','group-query','group-region'])$(id).value='';drawManufacturers();filterAndDraw();});
   for(const suffix of ['','-bottom']){
    $('prev'+suffix).addEventListener('click',()=>{page--;render();});$('next'+suffix).addEventListener('click',()=>{page++;render();});
    $('page-jump'+suffix).addEventListener('submit',event=>{event.preventDefault();jumpToPage($('page-number'+suffix).value);});
   }
   baseEntries=entries;
   try{
     const res=await fetch('data/basic-catalogue-edits.json',{cache:'no-store'});if(!res.ok)throw Error('修改记录 HTTP '+res.status);
     editor=createBasicEditor(baseEntries,validateStore(await res.json()),refreshManaged);
     for(const id of ['basic-add','basic-import','basic-clear','basic-connection','basic-style-csv','basic-style-review'])$(id).disabled=false;
     $('basic-add').addEventListener('click',()=>editor.add());
     $('basic-import').addEventListener('click',()=>editor.importWindow());
     $('basic-style-bulk').addEventListener('click',()=>editor.styles.bulk([...selection]));
     $('basic-style-csv').addEventListener('click',()=>editor.styles.csv([...selection]));
     $('basic-style-review').addEventListener('click',()=>editor.styles.review([...selection]));
     $('basic-select-page').addEventListener('click',()=>selectWorks(filtered.slice(page*size,(page+1)*size)));
     $('basic-select-filtered').addEventListener('click',()=>selectWorks(filtered));
     $('basic-merge').addEventListener('click',()=>editor.merge([...selection]));
     $('basic-clear').addEventListener('click',()=>{selection.clear();refreshSelection();render();});
     $('basic-connection').addEventListener('click',()=>editor.connection());
     $('rows').addEventListener('click',e=>{const button=e.target.closest('[data-edit]');if(button)editor.edit(button.dataset.edit);});
     $('rows').addEventListener('change',e=>{const id=e.target.dataset.select;if(id){if(e.target.checked)selection.add(id);else selection.delete(id);refreshSelection();}});
     $('basic-management-status').textContent='支持六维标签、批量编辑和 CSV 更新。AI 标签需审核后写入，可撤销最近3次操作。';
   }catch(err){$('basic-management-status').textContent='基础库修改记录读取失败：'+err.message+'。请刷新重试；为避免显示过期数据，管理功能已停用。';throw err;}
   filterAndDraw();
 }catch(err){$('count').textContent='无法读取基础作品数据：'+err.message;}
}
function selectWorks(works){
 for(const work of works)selection.add(work._key);
 refreshSelection();render();
}
function refreshSelection(){
 $('basic-selected').textContent='已选择'+selection.size+'部';$('basic-merge').disabled=selection.size<2;$('basic-style-bulk').disabled=!selection.size||selection.size>500;
}
function refreshManaged(main,all,store){
 entries=main.sort(compareDefaultOrder);allEntries=all;
 childrenByMain=new Map();for(const w of all)if(w.parentId){if(!childrenByMain.has(w.parentId))childrenByMain.set(w.parentId,[]);childrenByMain.get(w.parentId).push(w);}
 const ids=new Set(entries.map(workKey));for(const id of selection)if(!ids.has(id))selection.delete(id);
 $('stat-total').textContent=entries.length.toLocaleString('zh-CN');
 const oldYear=$('year').value,years=[...new Set(entries.map(w=>w.year).filter(Number.isInteger))].sort((a,b)=>a-b);
 $('year').innerHTML='<option value="">全部年份</option><option value="unknown">年份待核</option>'+years.map(y=>'<option value="'+y+'">'+y+' 年</option>').join('');$('year').value=years.includes(Number(oldYear))||oldYear==='unknown'?oldYear:'';
 rebuildFilters();
 refreshSelection();filterAndDraw();
}
start();
