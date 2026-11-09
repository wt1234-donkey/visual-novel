import {normalizeFilterText,manufacturerKey,manufacturerNames,createManufacturerIndex,matchingManufacturers,manufacturerOptions,REGION_LABELS,gameplayKeys,gameplayOptions,gameplayDisplay,styleState,styleDimension,STYLE_DIMENSIONS,styleOptions,MISSING_STYLE,pageIndex,basicFilterRows,matchingBasicPositions} from './basic-catalogue-filters.mjs?v=20261109-index';
import {createBasicEditor} from './basic-catalogue-editor.mjs?v=20261109-editorial';
import {workKey,validateStore} from './basic-catalogue-model.mjs?v=20261109-style-tags';
import {compareBasicOrder,createBasicWebIndex,createCatalogueWorker,withBasicDetails} from './basic-catalogue-index.mjs';
const webIndex=createBasicWebIndex(),queryIndex=createCatalogueWorker();
const $=id=>document.getElementById(id);
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kind={'manual-basic':'网页新增基础身份','new-basic':'待提升基础索引','main-linked':'完整主库已有','dossier-linked':'厂商专题已有','promoted-basic':'主库基础身份已纳入','promoted-dossier':'主库已关联专题','identity-review':'作品与版本身份待核','eligibility-review':'叙事与玩法主次待核','main-registry-linked':'已关联主库身份'};
let entries=[],filtered=[],page=0,editor,currentStore,indexRevision,renderVersion=0,filterVersion=0,indexGeneration=0;
let childrenByMain=new Map(),manufacturerIndex=[],filterCache=null,regionMetadata={entries:[]},filtering=false;
const selection=new Set();
const size=25;
const loadDetails=rows=>webIndex.details('basic',rows.filter(w=>Number.isInteger(w.slot)).map(w=>w.slot));
function drawManufacturers(){
 const selected=$('group').value,{total,visible}=manufacturerOptions(manufacturerIndex,{region:$('group-region').value,query:$('group-query').value},selected);
 $('group').innerHTML='<option value="">全部匹配厂商</option>'+Object.entries(REGION_LABELS).map(([region,label])=>{const rows=visible.filter(item=>item.region===region);return rows.length?'<optgroup label="'+label+'">'+rows.map(item=>'<option value="'+safe(item.key)+'">'+safe(item.label)+'（'+item.count+'）</option>').join('')+'</optgroup>':'';}).join('');
 $('group').value=visible.some(item=>item.key===selected)?selected:'';
 $('group-count').textContent='匹配 '+total.toLocaleString('zh-CN')+' 个厂商'+(total>visible.length?'；列出其中 '+visible.length+' 个，请输入名称缩小范围':'')+'。大小写重复项已合并。';
}
function rebuildFilters(){
 manufacturerIndex=createManufacturerIndex(entries,regionMetadata);
 filterCache=null;
 const gameplay=$('gameplay').value,styles=$('style').value;
 $('gameplay').innerHTML='<option value="">全部玩法</option>'+gameplayOptions(entries).map(item=>'<option value="'+safe(item.key)+'">'+safe(item.label)+'（'+item.count+'）</option>').join('');
 if([...$('gameplay').options].some(o=>o.value===gameplay))$('gameplay').value=gameplay;
 const missing=entries.filter(r=>!Object.keys(styleState(r).tags).length).length;
 $('style').innerHTML='<option value="">全部风格</option><option value="'+MISSING_STYLE+'">待补充（'+missing+'）</option>'+styleOptions(entries).map(group=>'<optgroup label="'+safe(group.label)+'">'+group.options.map(item=>'<option value="'+safe(item.key)+'">'+safe(item.label)+'（'+item.count+'）</option>').join('')+'</optgroup>').join('');
 if([...$('style').options].some(o=>o.value===styles))$('style').value=styles;
 $('stat-groups').textContent=manufacturerIndex.length.toLocaleString('zh-CN');
 for(const [key,label] of Object.entries(REGION_LABELS))$('group-region-'+key).textContent=label+'（'+manufacturerIndex.filter(item=>item.region===key).length+'）';
 drawManufacturers();
}
function filterAndDraw(){
 if(!currentStore)return;
 const version=++filterVersion;
 const region=$('group-region').value,query=$('group-query').value.trim();
 const allowed=region||query?new Set(matchingManufacturers(manufacturerIndex,{region,query}).map(item=>item.key)):null;
 const filters={q:normalizeFilterText($('q').value),gameplay:$('gameplay').value,group:$('group').value,status:$('status').value,year:$('year').value,style:$('style').value,allowed};
 const draw=positions=>{
  filtering=false;
  filtered=positions?Array.from(positions,index=>entries[index]):entries;
  page=0;render();
 };
 if(!Object.values(filters).some(Boolean)){draw();return;}
 const local=()=>{
  filterCache??=basicFilterRows(entries,childrenByMain);
  return matchingBasicPositions(filterCache,filters);
 };
 if(typeof Worker==='undefined'||entries.length<5000){draw(local());return;}
 filtering=true;
 $('basic-select-page').disabled=$('basic-select-filtered').disabled=true;
 $('count').textContent='正在筛选基础作品…';
 queryIndex({kind:'basic',revision:indexRevision,generation:indexGeneration,store:currentStore,filters}).then(positions=>{
  if(version===filterVersion)draw(positions||local());
 });
}
function jumpToPage(value){try{page=pageIndex(value,Math.max(1,Math.ceil(filtered.length/size)));render();$('count').scrollIntoView?.({behavior:'smooth',block:'start'});}catch(error){for(const suffix of ['','-bottom'])$('page-error'+suffix).textContent=error.message;}}
function render(){
    const total=filtered.length,n=Math.max(1,Math.ceil(total/size));page=Math.min(Math.max(page,0),n-1);
    const rows=filtered.slice(page*size,(page+1)*size);
    const version=++renderVersion;
    const drawRows=details=>{$('rows').innerHTML=rows.map(row=>{
      const r=withBasicDetails(row,details?.get(row.slot),currentStore);
      const alias=(r.aliases||[]).length?'<div class="minor">'+safe(r.aliases.slice(0,3).join(' / '))+'</div>':'';
      const year=Number.isInteger(r.year)?r.year:'—';
      const label=kind[r.status]||'专题已有';
      const link=/^https?:\/\//.test(r.source||'')?'<a href="'+safe(r.source)+'" target="_blank" rel="noopener noreferrer">资料</a>':'待核';
      const children=(childrenByMain.get(r._key)||[]);
      const {tags,legacy}=styleState(r);
      const stylePills=Object.values(tags).map(tag=>'<span class="pill" title="'+safe(STYLE_DIMENSIONS[styleDimension(tag)].label)+'">'+safe(tag)+'</span>').join(' ');
      const styleDetail=(stylePills||'<span class="minor">待补充</span>')+(legacy.length?'<div class="minor">旧标签待整理：'+safe(legacy.join('、'))+'</div>':'');
      return '<tr><td class="select-cell"><input type="checkbox" data-select="'+safe(r._key)+'" aria-label="选择 '+safe(r.title)+'" '+(selection.has(r._key)?'checked':'')+'></td><td class="title-cell"><button type="button" class="work-title" data-edit="'+safe(r._key)+'">'+safe(r.title)+'</button>'+alias+(children.length?'<div class="minor">含 '+children.length+' 个关联版本</div>':'')+'</td><td data-label="首发年份">'+year+'</td><td data-label="主要玩法">'+safe(gameplayDisplay(r.gameplay))+(/待核|候选/.test(r.gameplay)?'<div class="minor">玩法细节待核</div>':'')+(/仅专题|关联/.test(r.gameplay)?'<div class="minor">'+safe(r.gameplay)+'</div>':'')+(r.gameplayNote?'<div class="minor">'+safe(r.gameplayNote)+'</div>':'')+'</td><td data-label="剧情风格">'+styleDetail+'</td><td data-label="厂商关联">'+safe(r.group)+'</td><td data-label="编目状态"><span class="pill">'+safe(label)+'</span>'+(r.reason?'<div class="minor">'+safe(r.reason)+'</div>':'')+(r.matchedWorkId?'<div class="minor">'+safe(r.matchedWorkId)+'</div>':'')+'</td><td data-label="依据">'+link+'</td></tr>';
    }).join('')||'<tr><td colspan="8">未找到符合筛选条件的作品</td></tr>';};
    drawRows();
    $('basic-detail-status').textContent='';
    if(rows.some(row=>Number.isInteger(row.slot)))loadDetails(rows).then(details=>{
      if(version===renderVersion)drawRows(details);
    }).catch(error=>{
      if(version===renderVersion)$('basic-detail-status').textContent='本页资料未能加载。可再次翻页或刷新重试。'+error.message;
    });
    $('basic-select-page').disabled=!editor||filtering||!rows.length;
    $('basic-select-filtered').disabled=!editor||filtering||!total||total>500;
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
   const [manifest,baseEntries,regionData]=await Promise.all([webIndex.meta(),webIndex.basicRows(),regions]);
   indexRevision=manifest.revision;
   const {promotedBasic,promotedDossier,existingComplete}=manifest.basic;
   $('stat-new').textContent=promotedBasic.toLocaleString('zh-CN');
   $('stat-linked').textContent=(promotedDossier+existingComplete).toLocaleString('zh-CN');
   regionMetadata=regionData;
   $('q').addEventListener('input',filterAndDraw);
   for(const id of ['year','gameplay','group','status','style'])$(id).addEventListener('change',filterAndDraw);
   $('group-query').addEventListener('input',()=>{drawManufacturers();filterAndDraw();});
   $('group-region').addEventListener('change',()=>{drawManufacturers();filterAndDraw();});
   $('filter-reset').addEventListener('click',()=>{for(const id of ['q','year','gameplay','group','status','style','group-query','group-region'])$(id).value='';drawManufacturers();filterAndDraw();});
   for(const suffix of ['','-bottom']){
    $('prev'+suffix).addEventListener('click',()=>{page--;render();});$('next'+suffix).addEventListener('click',()=>{page++;render();});
    $('page-jump'+suffix).addEventListener('submit',event=>{event.preventDefault();jumpToPage($('page-number'+suffix).value);});
   }
   try{
     const res=await fetch('data/basic-catalogue-edits.json',{cache:'no-store'});if(!res.ok)throw Error('修改记录 HTTP '+res.status);
     editor=createBasicEditor(baseEntries,validateStore(await res.json()),refreshManaged,loadDetails);
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
 entries=main.sort(compareBasicOrder);currentStore=store;indexGeneration++;
 childrenByMain=new Map();for(const w of all)if(w.parentId){if(!childrenByMain.has(w.parentId))childrenByMain.set(w.parentId,[]);childrenByMain.get(w.parentId).push(w);}
 const ids=new Set(entries.map(workKey));for(const id of selection)if(!ids.has(id))selection.delete(id);
 $('stat-total').textContent=entries.length.toLocaleString('zh-CN');
 const oldYear=$('year').value,years=[...new Set(entries.map(w=>w.year).filter(Number.isInteger))].sort((a,b)=>a-b);
 $('year').innerHTML='<option value="">全部年份</option><option value="unknown">年份待核</option>'+years.map(y=>'<option value="'+y+'">'+y+' 年</option>').join('');$('year').value=years.includes(Number(oldYear))||oldYear==='unknown'?oldYear:'';
 rebuildFilters();
 refreshSelection();if(editor)filterAndDraw();
}
start();
