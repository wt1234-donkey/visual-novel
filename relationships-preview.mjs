const TYPES={company:'公司',brand:'品牌',team:'团队',unknown:'身份待核',publication:'刊物',individual:'个人'};
const STATUS={sourceReviewed:'来源已核',existingDossier:'沿用档案',previewReviewed:'预览补充',pending:'关系待核',unresolved:'身份待核'};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v).normalize('NFKC').toLowerCase().replace(/\s+/g,'');
const safeUrl=v=>/^https?:\/\//.test(v)?esc(v):'#';

export function familyEdges(data,family,showPending=true){
  const ids=new Set([family.root,...family.entityIds]);
  const unique=new Map();
  for(const edge of data.edges){
    if(!ids.has(edge.parent)||!ids.has(edge.child)||(!showPending&&edge.status==='pending'))continue;
    const key=edge.parent+'|'+edge.child;
    if(!unique.has(key)||edge.kind==='brand')unique.set(key,edge);
  }
  return [...unique.values()];
}

export function layoutFamily(data,family,{showPending=true,collapsed=new Set()}={}){
  const edges=familyEdges(data,family,showPending),children=new Map();
  for(const edge of edges){if(!children.has(edge.parent))children.set(edge.parent,[]);children.get(edge.parent).push(edge.child);}
  const ids=[family.root,...family.entityIds],seen=new Set(),positions=[];let leaf=0,maxDepth=0;
  function visit(id,depth,path=new Set()){
    if(path.has(id)||seen.has(id))return null;
    seen.add(id);const next=new Set(path);next.add(id);
    const kids=collapsed.has(id)?[]:(children.get(id)||[]);
    const placed=kids.map(k=>visit(k,depth+1,next)).filter(Boolean);
    const x=placed.length?placed.reduce((s,n)=>s+n.slot,0)/placed.length:leaf++;
    const node={id,depth,slot:x};positions.push(node);maxDepth=Math.max(maxDepth,depth);return node;
  }
  visit(family.root,0);
  // Hidden candidate branches must not reappear as disconnected roots.
  const reachable=new Set();
  const walk=(id,path=new Set())=>{if(path.has(id))return;path.add(id);reachable.add(id);for(const child of children.get(id)||[])walk(child,new Set(path));};
  walk(family.root);
  const allIncoming=new Set(data.edges.filter(e=>ids.includes(e.parent)).map(e=>e.child));
  for(const id of family.entityIds)if(!seen.has(id)&&!reachable.has(id)&&!allIncoming.has(id))visit(id,0);
  const width=Math.max(650,leaf*238+50),offset=(width-leaf*238)/2;
  const nodes=positions.map(n=>({...n,x:offset+n.slot*238+14,y:40+n.depth*157}));
  const visible=new Set(nodes.map(n=>n.id));
  return {nodes,edges:edges.filter(e=>visible.has(e.parent)&&visible.has(e.child)),width,height:Math.max(355,168+maxDepth*157),children};
}

export function historiesFor(data,family){
  const ids=new Set(family.entityIds);
  return data.nameHistory.filter(h=>ids.has(h.fromId)||ids.has(h.toId));
}

export function searchFamilies(data,query){
  const q=norm(query),nodes=new Map(data.nodes.map(n=>[n.id,n]));
  return data.families.filter(f=>!q||norm([f.title,f.subtitle,...[f.root,...f.entityIds].flatMap(id=>{const n=nodes.get(id);return n?[n.name,...n.aliases]:[];}),...historiesFor(data,f).flatMap(h=>[h.oldName,h.newName])].join(' ')).includes(q));
}

async function init(){
  const $=id=>document.getElementById(id),workspace=$('workspace');
  let data;
  try{const response=await fetch('data/relationships-preview.json');if(!response.ok)throw new Error('HTTP '+response.status);data=await response.json();}
  catch{workspace.setAttribute('aria-busy','false');$('graph-stage').innerHTML='<p class="error-message">关系资料暂时无法读取。请刷新重试，或先查看<a href="entities.html">主体档案</a>。</p>';$('family-nav').innerHTML='<p class="no-results">暂时无法读取家族列表。</p>';return;}
  const nodes=new Map(data.nodes.map(n=>[n.id,n]));
  const params=new URLSearchParams(location.search);
  let family=data.families.find(f=>f.id===params.get('family'))||data.families[0];
  let selected=[family.root,...family.entityIds].includes(params.get('node'))?params.get('node'):family.focus;
  let view='tree',zoom=1,collapsed=new Set(),showPending=true;
  const linkSource=(url,label='来源 ↗')=>`<a href="${safeUrl(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  const nodeName=id=>nodes.get(id)?.name||id;
  const browseLink=id=>`index.html?participant=${encodeURIComponent(id)}#catalogue`;
  function setURL(){const p=new URLSearchParams({family:family.id,node:selected});history.replaceState(null,'','?'+p);}
  function toast(text){$('toast').textContent=text;$('toast').hidden=false;setTimeout(()=>{$('toast').hidden=true;},2400);}
  function renderNav(){
    const found=searchFamilies(data,$('family-search').value);
    $('family-total').textContent=found.length;
    $('family-nav').innerHTML=found.length?found.map((f,i)=>`<button class="family-button" data-family="${f.id}" aria-pressed="${f.id===family.id}"><span class="family-initial" aria-hidden="true">${esc(f.title.slice(0,1))}</span><span><strong>${esc(f.title)}</strong><small>${esc(f.subtitle)}</small></span></button>`).join(''):'<p class="no-results">暂无匹配家族。<br>试试 Key、NOVECT 或旧名。</p>';
  }
  function centerGraph(){const box=$('graph-scroll');box.scrollTo({left:Math.max(0,(parseFloat($('graph-stage').style.width)-box.clientWidth)/2),top:0});}
  function chooseFamily(id){const f=data.families.find(f=>f.id===id);if(!f)return;family=f;selected=f.focus;collapsed=new Set();zoom=1;render();centerGraph();}
  function renderGraph(){
    const layout=layoutFamily(data,family,{showPending,collapsed});
    const pos=new Map(layout.nodes.map(n=>[n.id,n]));
    const paths=layout.edges.map(edge=>{
      const a=pos.get(edge.parent),b=pos.get(edge.child),x1=a.x+105,y1=a.y+105,x2=b.x+105,y2=b.y;
      const mid=y1+(y2-y1)/2;
      return `<path class="edge-path ${edge.kind}" d="M${x1} ${y1} V${mid} H${x2} V${y2}"/><text class="edge-label" x="${x2+8}" y="${y2-15}">${esc(edge.label)}</text>`;
    }).join('');
    const cards=layout.nodes.map(p=>{
      const n=nodes.get(p.id);if(!n)return '';
      const incoming=layout.edges.find(e=>e.child===n.id),pending=incoming?.status==='pending';
      const old=historiesFor(data,family).some(h=>h.fromId===n.id&&h.fromId!==h.toId);
      return `<div class="graph-node kind-${n.type}${selected===n.id?' selected':''}${pending?' pending-node':''}" style="left:${p.x}px;top:${p.y}px"><button class="node-main" data-node="${n.id}" aria-pressed="${selected===n.id}" aria-label="查看${esc(n.name)}的关系和作品"><span class="node-meta"><span class="node-kind">${TYPES[n.type]||'主体'}</span><span>${pending?'衍生待核':old?'历史名称':selected===n.id?'正在查看':n.previewOnly?'预览补充':'主体档案'}</span></span><strong class="node-name">${esc(n.name)}</strong><span class="node-count"><i class="node-dot"></i>${n.previewOnly?'资料补充节点':`${n.stats.main} 部关联主库作品`}</span></button>${layout.children.has(n.id)?`<button class="fold-node" data-collapse="${n.id}" aria-expanded="${!collapsed.has(n.id)}" aria-label="${collapsed.has(n.id)?'展开':'折叠'}${esc(n.name)}的下级关系">${collapsed.has(n.id)?'+':'−'}</button>`:''}</div>`;
    }).join('');
    const stage=$('graph-stage');
    stage.style.width=layout.width*zoom+'px';stage.style.height=layout.height*zoom+'px';
    stage.innerHTML=`<div class="graph-inner" style="width:${layout.width}px;height:${layout.height}px;transform:scale(${zoom})"><svg width="${layout.width}" height="${layout.height}" aria-hidden="true">${paths}</svg>${cards}</div>`;
    $('zoom-value').textContent=Math.round(zoom*100)+'%';
    $('zoom-out').disabled=zoom<=.7;$('zoom-in').disabled=zoom>=1.4;
    $('graph-caption').textContent=`${layout.nodes.length} 个可见主体 · 点击节点查看详情；圆点展开／收起`;
    renderList(layout.edges);
  }
  function renderList(edges){
    $('relation-list').innerHTML=edges.length?edges.map(e=>`<article class="list-edge"><div><button data-node="${e.parent}">${esc(nodeName(e.parent))}</button><span class="edge-kind">${esc(e.label)} →</span><button data-node="${e.child}">${esc(nodeName(e.child))}</button></div><p>${esc(e.dateLabel)} · ${esc(STATUS[e.status]||e.status)}</p><p>${esc(e.note)}</p>${linkSource(e.source)}</article>`).join(''):'<p class="muted">该示例暂未登记组织归属关系。名称沿革见下方。</p>';
  }
  function renderHistory(){
    const histories=historiesFor(data,family);
    $('name-history').innerHTML=histories.length?histories.map(h=>`<div class="name-event"><strong>${esc(h.oldName)}</strong><span class="arrow">→</span><strong>${esc(h.newName)}</strong><div class="event-meta"><span>${esc(h.dateLabel)}</span>${linkSource(h.source)}</div></div>`).join(''):'<p class="empty-lane">此家族暂无已登记的更名记录。<br><button data-family="microsoft">查看 Xbox 更名示例 →</button></p>';
    const spins=familyEdges(data,family,showPending).filter(e=>e.kind==='spinOff');
    $('spin-history').innerHTML=spins.length?spins.map(e=>`<div class="spin-event"><button data-node="${e.parent}">${esc(nodeName(e.parent))}</button> <span>↗</span> <button data-node="${e.child}">${esc(nodeName(e.child))}</button><p>成员独立线索 · 待补原始公告<br>不表示母子公司或旧作继承</p><div class="event-meta"><span>${esc(e.dateLabel)}</span>${linkSource(e.source,'资料线索 ↗')}</div></div>`).join(''):`<p class="empty-lane">${!showPending&&family.id==='silkys'?'待核衍生线索已隐藏。':'此家族暂无已核的组织衍生记录。'}<br><button data-family="silkys">查看 Silky’s 待核示例 →</button></p>`;
  }
  function renderDetail(){
    const n=nodes.get(selected);if(!n)return;
    const edges=familyEdges(data,family,showPending).filter(e=>e.child===n.id||e.parent===n.id);
    const histories=historiesFor(data,family).filter(h=>h.fromId===n.id||h.toId===n.id);
    const alias=[...new Set(n.aliases)].filter(a=>a!==n.name).slice(0,3).join(' / ');
    const incoming=data.edges.find(e=>e.kind==='spinOff'&&e.child===n.id&&e.status==='pending');
    const status=incoming?'pending':n.verification;
    const description=n.historyNote||'主体身份、组织归属与作品参与分别记录。点击相连节点继续探索。';
    const relations=edges.map(e=>{const parent=e.child===n.id,other=parent?e.parent:e.child;const label=e.kind==='parent'?(parent?'母公司':'子公司'):e.kind==='spinOff'?(parent?'衍生来源（待核）':'衍生组织（待核）'):(parent?'上级／关联组织':'旗下／家族品牌');return `<div class="detail-relation"><div class="small-label">${label}</div><button data-node="${other}">${esc(nodeName(other))} ↗</button><p>${esc(e.dateLabel)} · ${esc(STATUS[e.status]||e.status)}</p><p>${esc(e.note)}</p>${linkSource(e.source)}</div>`;}).join('');
    $('detail-panel').innerHTML=`<div class="detail-kicker"><span class="node-kind">${TYPES[n.type]||'主体'}</span><span class="status-dot ${status==='pending'?'pending':''}">${STATUS[status]||'沿用档案'}</span></div><div class="detail-logo" aria-hidden="true">${esc(n.name.slice(0,1))}</div><h2>${esc(n.name)}</h2><p class="detail-alias">${esc(alias||'独立主体档案')}</p><p class="detail-description">${esc(description)}</p><div class="detail-stats"><div><strong>${n.stats.main}</strong><span>关联主库作品</span></div><div><strong>${n.productionCount}</strong><span>主库制作记录</span></div><div><strong>${n.stats.related}</strong><span>跨类型关联</span></div><div><strong>${n.stats.bibliography}</strong><span>仅专题书目</span></div></div><section class="detail-section"><h3>与此主体相连<span>${edges.length} 条</span></h3>${relations||'<p class="empty-lane">暂无已登记组织关系。</p>'}</section>${histories.length?`<section class="detail-section"><h3>名称沿革</h3>${histories.map(h=>`<div class="detail-relation"><button data-node="${h.toId}">${esc(h.oldName)} → ${esc(h.newName)}</button><p>${esc(h.note)}</p>${linkSource(h.source)}</div>`).join('')}</section>`:''}${n.works.length?`<section class="detail-section"><h3>直接关联作品<span>按原作年选列</span></h3>${n.works.map(w=>`<a class="detail-work" href="index.html?query=${encodeURIComponent(w.title)}#catalogue"><span>${esc(w.title)}</span><time>${w.year}</time></a>`).join('')}</section>`:''}<div class="detail-actions">${!n.previewOnly?`<a class="button-primary" href="${browseLink(n.id)}">浏览该主体关联作品 <span>↗</span></a><a class="button-secondary" href="entities.html#${n.id}">查看完整主体档案 <span>↗</span></a>`:`<a class="button-primary" href="${safeUrl(n.sources[0])}" target="_blank" rel="noopener noreferrer">查看母公司关系公告 <span>↗</span></a>`}${n.dossiers.map(d=>`<a class="button-secondary" href="${esc(d.id)}.html">${esc(d.name)}专题 <span>↗</span></a>`).join('')}</div><p class="detail-footnote">数量仅统计本主体的直接记录。组织关系不自动继承作品或创作风格；未核时间不等于当前归属。</p><details class="source-details"><summary>主体来源与记录依据</summary>${n.sources.map((s,i)=>linkSource(s,`${i+1}. ${esc(new URL(s).hostname)} ↗`)).join('')}</details>`;
  }
  function render(){
    $('family-title').textContent=family.title;
    renderNav();renderGraph();renderHistory();renderDetail();setURL();
    $('graph-scroll').hidden=view!=='tree';$('relation-list').hidden=view!=='list';
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
  }
  workspace.addEventListener('click',e=>{
    const familyButton=e.target.closest('[data-family]');if(familyButton){chooseFamily(familyButton.dataset.family);return;}
    const fold=e.target.closest('[data-collapse]');if(fold){const id=fold.dataset.collapse;if(collapsed.has(id))collapsed.delete(id);else collapsed.add(id);renderGraph();return;}
    const button=e.target.closest('[data-node]');if(button){selected=button.dataset.node;renderGraph();renderDetail();setURL();return;}
    const viewButton=e.target.closest('[data-view]');if(viewButton){view=viewButton.dataset.view;render();}
  });
  $('family-search').addEventListener('input',renderNav);
  $('show-pending').addEventListener('change',()=>{showPending=$('show-pending').checked;if(!showPending&&data.edges.some(e=>e.kind==='spinOff'&&e.child===selected))selected=family.root;render();});
  $('zoom-in').addEventListener('click',()=>{zoom=Math.min(1.4,Math.round((zoom+.1)*10)/10);renderGraph();});
  $('zoom-out').addEventListener('click',()=>{zoom=Math.max(.7,Math.round((zoom-.1)*10)/10);renderGraph();});
  $('reset-tree').addEventListener('click',()=>{collapsed=new Set();zoom=1;renderGraph();centerGraph();toast('关系树已展开并恢复缩放');});
  render();centerGraph();workspace.setAttribute('aria-busy','false');
}
if(typeof document!=='undefined')init();
