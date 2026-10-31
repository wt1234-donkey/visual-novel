const $=id=>document.getElementById(id);
const safe=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const kind={'new-basic':'本轮新增','main-linked':'主库已有','dossier-linked':'厂商专题已有','identity-review':'身份待核'};
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
   $('stat-total').textContent=obj.summary.displayTotal.toLocaleString('zh-CN');
   $('stat-new').textContent=obj.summary.newBasic.toLocaleString('zh-CN');
   $('stat-linked').textContent=(obj.summary.alreadyMain+obj.summary.alreadyDossier+obj.summary.identityReview).toLocaleString('zh-CN');
   $('stat-groups').textContent=obj.summary.groups.toLocaleString('zh-CN');
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
