const $=id=>document.getElementById(id);
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kind={'new-basic':'待提升基础索引','main-linked':'完整主库已有','dossier-linked':'厂商专题已有','promoted-basic':'主库基础身份已纳入','promoted-dossier':'主库已关联专题','identity-review':'作品与版本身份待核','main-registry-linked':'已关联主库身份'};
let entries=[],filtered=[],page=0;
const size=25;
function optionBox(element,values){
    const old=element.value;
    const opts=[element.options[0].outerHTML,...[...new Set(values)].sort((a,b)=>a.localeCompare(b,'zh-Hans-CN')).map(x=>'<option value="'+safe(x)+'">'+safe(x)+'</option>')];
    element.innerHTML=opts.join('');
    if([...element.options].some(x=>x.value===old))element.value=old;
}
function filterAndDraw(){
    const q=$('q').value.trim().normalize('NFKC').toLowerCase(),gp=$('gameplay').value,g=$('group').value,s=$('status').value;
    filtered=entries.filter(r=>{
      const hay=[r.title,...(r.aliases||[]),r.group].join(' ').normalize('NFKC').toLowerCase();
      return (!q||hay.includes(q))&&(!gp||r.gameplay===gp)&&(!g||r.group===g)&&(!s||r.status===s);
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
      const link=(r.source||'').startsWith('https://')?'<a href="'+safe(r.source)+'" target="_blank" rel="noopener noreferrer">资料</a>':'待核';
      return '<tr><td>'+safe(r.title)+alias+'</td><td>'+year+'</td><td>'+safe(r.gameplay)+'</td><td>'+safe(r.group)+'</td><td><span class="pill">'+safe(label)+'</span>'+(r.matchedWorkId?'<div class="minor">'+safe(r.matchedWorkId)+'</div>':'')+'</td><td>'+link+'</td></tr>';
    }).join('')||'<tr><td colspan="6">未找到符合筛选条件的作品</td></tr>';
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
   try{
     const promotion=await fetch('data/main-adv-rpg-works-20261031.json',{cache:'no-store'});
     if(promotion.ok){
       const main=await promotion.json();
       const statusByIndex=new Map(main.works.map(w=>[w.indexId,w.mainPlacement]));
       const holding=new Set(main.identityReview.map(w=>w.indexId));
       entries=entries.map(w=>{
         if(holding.has(w.id))return {...w,status:'identity-review'};
         const placement=statusByIndex.get(w.id);
         return placement==='promoted-basic'?{...w,status:'promoted-basic'}:placement==='promoted-dossier'?{...w,status:'promoted-dossier'}:w;
       });
       $('stat-new').textContent=main.summary.promotedBasic.toLocaleString('zh-CN');
       $('stat-linked').textContent=(main.summary.existingComplete+main.summary.promotedDossier).toLocaleString('zh-CN');
     }
   }catch(err){console.warn('主库基础身份层暂不可用',err);}
   try{
     const next=await fetch('data/adv-rpg-next-studio-review-20261031.json',{cache:'no-store'});
     if(next.ok){
       const add=await next.json();
       const normal=t=>String(t||'').normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');
       const existing=new Set(entries.map(x=>normal(x.title)+'|'+x.year));
       for(const r of add.records){
         const key=normal(r.title)+'|'+r.year;
         if(existing.has(key))continue;
         entries.push({...r,id:'batch2-'+key,matchedWorkId:r.registryId,
           status:r.status==='linked-existing-registry'||r.status==='linked-existing-full-or-dossier'?'main-registry-linked':r.status});
         existing.add(key);
       }
     }
   }catch(err){console.warn('第二批ADV/RPG作品审核表尚不可用',err);}
   $('stat-total').textContent=entries.length.toLocaleString('zh-CN');
   try{const mainReg=await (await fetch('data/main-adv-rpg-works-20261031.json',{cache:'no-store'})).json();$('stat-new').textContent=mainReg.summary.promotedBasic.toLocaleString('zh-CN');$('stat-linked').textContent=(mainReg.summary.promotedDossier+mainReg.summary.existingComplete).toLocaleString('zh-CN')}catch(err){console.warn('主库统计暂不可用',err)}
   if(!$('stat-linked').textContent.match(/[0-9]/))$('stat-linked').textContent=(obj.summary.alreadyMain+obj.summary.alreadyDossier+obj.summary.identityReview).toLocaleString('zh-CN');
   $('stat-groups').textContent=(new Set(entries.map(x=>x.group))).size.toLocaleString('zh-CN');
   optionBox($('gameplay'),entries.map(r=>r.gameplay));
   optionBox($('group'),entries.map(r=>r.group));
   $('q').addEventListener('input',filterAndDraw);
   for(const id of ['gameplay','group','status'])$(id).addEventListener('change',filterAndDraw);
   $('prev').addEventListener('click',()=>{page--;render()});
   $('next').addEventListener('click',()=>{page++;render()});
   filterAndDraw();
 }catch(err){$('count').textContent='无法读取基础作品数据：'+err.message;}
}
start();
