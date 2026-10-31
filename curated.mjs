const $ = (id) => document.getElementById(id);
const safe = (text) => String(text ?? '').replace(/[&<>"']/g, c => ({
  '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
}[c]));
const statuses = {'editorial-seed':'编辑精选初选','reviewed':'叙事复核通过','watchlist':'精选待评'};
const normalize = value => String(value ?? '').normalize('NFKC').toLocaleLowerCase('zh-CN');
let all = [];
function draw() {
  const query = normalize($('query').value.trim());
  const theme = $('theme').value, sort = $('sort').value;
  const matches = all.filter(item => (!theme || (item.themes || []).includes(theme)) &&
    (!query || normalize([item.title,item.originalTitle,item.whyRead,item.synopsis,
      ...(item.themes||[]),...(item.styles||[]),...(item.structures||[])].join(' ')).includes(query)));
  if(sort==='newest') matches.sort((a,b)=>b.firstYear-a.firstYear||a.order-b.order);
  else if(sort==='oldest') matches.sort((a,b)=>a.firstYear-b.firstYear||a.order-b.order);
  else matches.sort((a,b)=>a.order-b.order);
  $('count').textContent = '显示 '+matches.length+' / '+all.length+' 部精选初选 · 非全库作品数量';
  $('cards').innerHTML = matches.map(w=>'<article class="card">'+
    '<div class="card-head"><span class="year">'+safe(w.firstYear)+' · '+safe(w.narrativePosition)+'</span><span class="pill">'+safe(statuses[w.status]||'待核')+'</span></div>'+
    '<h3>'+safe(w.title)+'</h3>'+
    (w.originalTitle && w.originalTitle!==w.title ? '<p class="original">'+safe(w.originalTitle)+'</p>' : '')+
    '<p class="why">'+safe(w.whyRead)+'</p>'+
    '<p class="summary">'+safe(w.synopsis)+'</p>'+
    '<div class="tags">'+[...(w.themes||[]).slice(0,3),...(w.styles||[]).slice(0,2)].map(v=>'<span class="tag">'+safe(v)+'</span>').join('')+'</div>'+
    '<div class="links"><a href="'+safe(w.detailUrl)+'">查看作品与版本档案 →</a>'+
    '<a target="_blank" rel="noopener noreferrer" href="'+safe(w.source)+'">查看叙事编目依据 ↗</a></div></article>').join('') ||
    '<div class="empty">没有符合搜索条件的精选初选作品。可以到基础作品库扩大搜索范围。</div>';
}
async function start() {
  try{
    const response=await fetch('./data/curated-narrative-works.json?v=20261101',{cache:'no-cache'});
    if(!response.ok)throw new Error('HTTP '+response.status);
    const data=await response.json();
    if(!Array.isArray(data.entries))throw new Error('精选目录格式无效');
    all=data.entries.filter(row=>statuses[row.status] && row.workId && row.title && row.source?.startsWith('https://'));
    const themes=[...new Set(all.flatMap(item=>item.themes||[]))].sort((a,b)=>a.localeCompare(b,'zh'));
    $('theme').insertAdjacentHTML('beforeend',themes.map(t=>'<option value="'+safe(t)+'">'+safe(t)+'</option>').join(''));
    for(const id of ['query','theme','sort'])$(id).addEventListener(id==='query'?'input':'change',draw);
    draw();
  }catch(error){
    $('count').textContent='读取精选目录失败：'+error.message;
    $('cards').innerHTML='<p class="empty">请打开基础作品库或稍后刷新页面。</p>';
  }
}
start();