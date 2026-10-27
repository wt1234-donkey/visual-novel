const TYPES={company:'公司',brand:'品牌',team:'团队',unknown:'身份待核',publication:'刊物',individual:'个人'};
const STATUS={sourceReviewed:'来源已核',existingDossier:'沿用档案',previewReviewed:'预览补充',pending:'关系待核',unresolved:'身份待核'};
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,'');
const GROUPS={creation:'创作作品',originalBrand:'原作发行品牌',pending:'专题职责待核',other:'其他参与／发行',verification:'核查结论'};
export function verificationRecords(data,node,{placement='main',query='',status='',category='',changedOnly=false}={}){
  const q=norm(query);
  const changed=new Set(data.verificationLedger?.changedRecordIds||[]);
  return (node.groups?.verification||[]).flatMap(row=>row.recordIds.map(id=>data.verificationLedger.records[id]))
    .filter(r=>data.works[r.workId].placement===placement&&(!status||r.status===status)&&(!category||r.category===category)&&(!changedOnly||changed.has(r.recordId))&&
      (!q||norm([r.game,r.topic,r.detail].join(' ')).includes(q)));
}
export function worksFor(data,node,group='creation',placement='main',query=''){
  const q=norm(query);
  return (node.groups?.[group]||[]).filter(r=>{const w=data.works[r.workId];return w.placement===placement&&(!q||norm([w.title,w.originalTitle].join(' ')).includes(q));});
}
export function creatorNodes(data,{kind='creators',placement='main',query=''}={}){
  const q=norm(query);return data.nodes.filter(n=>!n.previewOnly&&(kind==='all'?Object.keys(GROUPS).some(g=>worksFor(data,n,g,placement).length):(kind==='creators'?worksFor(data,n,'creation',placement).length>0:n.type===kind&&Object.keys(GROUPS).some(g=>worksFor(data,n,g,placement).length)))&&(!q||norm([n.name,...n.aliases,...data.nameHistory.filter(h=>h.fromId===n.id||h.toId===n.id).flatMap(h=>[h.oldName,h.newName])].join(' ')).includes(q))).sort((a,b)=>worksFor(data,b,'creation',placement).length-worksFor(data,a,'creation',placement).length||a.name.localeCompare(b.name,'zh-CN'));
}
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

const englishKey=value=>String(value).normalize('NFKD').replace(/[\u0300-\u036f]/g,'').trim().toLowerCase();
export function sortFamilies(families){
  return [...families].sort((a,b)=>{
    const ak=englishKey(a.title),bk=englishKey(b.title),ag=/^[a-z]/.test(ak)?0:1,bg=/^[a-z]/.test(bk)?0:1;
    return ag-bg||ak.localeCompare(bk,'en',{sensitivity:'base',numeric:true})||a.id.localeCompare(b.id,'en');
  });
}
export function searchFamilies(data,query){
  const q=norm(query),nodes=new Map(data.nodes.map(n=>[n.id,n]));
  return sortFamilies(data.families.filter(f=>!q||norm([f.title,f.subtitle,...[f.root,...f.entityIds].flatMap(id=>{const n=nodes.get(id);return n?[n.name,...n.aliases]:[];}),...historiesFor(data,f).flatMap(h=>[h.oldName,h.newName])].join(' ')).includes(q)));
}

async function init(){
  const $=id=>document.getElementById(id),workspace=$('workspace');
  let data;
  try{const response=await fetch(document.body.dataset.source||'data/relationships-preview.json');if(!response.ok)throw new Error('HTTP '+response.status);data=await response.json();}
  catch(error){console.error('组织目录读取失败',error);workspace.setAttribute('aria-busy','false');$('graph-stage').innerHTML='<p class="error-message">关系资料暂时无法读取。请刷新重试，或先查看<a href="entities.html">主体档案</a>。</p>';$('family-nav').innerHTML='<p class="no-results">暂时无法读取家族列表。</p>';if($('creator-grid')){$('creator-grid').innerHTML='<p class="error-message">作品目录读取失败，请刷新重试或查看主体档案。</p>';$('creator-work-list').textContent='作品职责暂时无法读取。';}return;}
  const nodes=new Map(data.nodes.map(n=>[n.id,n]));
  const params=new URLSearchParams(location.search);
  let family=data.families.find(f=>f.id===params.get('family'))||data.families.find(f=>[f.root,...f.entityIds].includes(params.get('node')))||data.families.find(f=>f.id===document.body.dataset.defaultFamily)||data.families[0];
  let selected=[family.root,...family.entityIds].includes(params.get('node'))?params.get('node'):family.focus;
  let view='tree',zoom=1,collapsed=new Set(),showPending=true;
  const catalogue=!!$('creator-grid');let verificationStatus='',verificationCategory='',verificationChangedOnly=false;let workGroup=Object.hasOwn(GROUPS,params.get('group'))?params.get('group'):'creation';
  if(catalogue&&['main','related','bibliography'].includes(params.get('placement')))$('work-placement').value=params.get('placement');
  const linkSource=(url,label='来源 ↗')=>`<a href="${safeUrl(url)}" target="_blank" rel="noopener noreferrer">${label}</a>`;
  const nodeName=id=>nodes.get(id)?.name||id;
  const browseLink=id=>`index.html?participant=${encodeURIComponent(id)}#catalogue`;
  function setURL(){const p=new URLSearchParams({family:family.id,node:selected});if(catalogue){p.set('group',workGroup);p.set('placement',$('work-placement').value);}history.replaceState(null,'','?'+p);}
  function toast(text){$('toast').textContent=text;$('toast').hidden=false;setTimeout(()=>{$('toast').hidden=true;},2400);}
  function renderNav(){
    const found=searchFamilies(data,$('family-search').value);
    $('family-total').textContent=found.length;
    $('family-nav').innerHTML=found.length?found.map((f,i)=>`<button class="family-button" data-family="${f.id}" aria-pressed="${f.id===family.id}"><span class="family-initial" aria-hidden="true">${esc(f.title.slice(0,1))}</span><span><strong>${esc(f.title)}</strong><small>${esc(f.subtitle)}</small></span></button>`).join(''):'<p class="no-results">暂无匹配主体。<br>试试 Key、NOVECT 或旧名。</p>';
  }
  function centerGraph(){const box=$('graph-scroll');box.scrollTo({left:Math.max(0,(parseFloat($('graph-stage').style.width)-box.clientWidth)/2),top:0});}
  function chooseFamily(id){const f=data.families.find(f=>f.id===id);if(!f)return;family=f;selected=f.focus;collapsed=new Set();zoom=1;if(catalogue)$('work-search').value='';render();centerGraph();}
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
      return `<div class="graph-node kind-${n.type}${selected===n.id?' selected':''}${pending?' pending-node':''}" style="left:${p.x}px;top:${p.y}px"><button class="node-main" data-node="${n.id}" aria-pressed="${selected===n.id}" aria-label="查看${esc(n.name)}的关系和作品"><span class="node-meta"><span class="node-kind">${TYPES[n.type]||'主体'}</span><span>${pending?'衍生待核':old?'历史名称':selected===n.id?'正在查看':n.previewOnly?'预览补充':'主体档案'}</span></span><strong class="node-name">${esc(n.name)}</strong><span class="node-count"><i class="node-dot"></i>${n.previewOnly?'资料补充节点':`${catalogue?(n.productionCount?`${n.productionCount} 部创作作品`:'暂无已登记创作记录'):`${n.stats.main} 部关联主库作品`}`}</span></button>${layout.children.has(n.id)?`<button class="fold-node" data-collapse="${n.id}" aria-expanded="${!collapsed.has(n.id)}" aria-label="${collapsed.has(n.id)?'展开':'折叠'}${esc(n.name)}的下级关系">${collapsed.has(n.id)?'+':'−'}</button>`:''}</div>`;
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
    const ids=new Set(family.entityIds);
    const events=(data.organizationEvents||[]).filter(event=>event.entityIds.some(id=>ids.has(id))).sort((a,b)=>a.year-b.year);
    if(events.length)$('name-history').innerHTML+=(histories.length?'':'<h4>已核版次中的历史节点</h4>')+events.map(event=>`<div class="name-event"><strong>${event.year} · ${esc(event.title)}</strong><p>${esc(event.note)}</p><div class="event-meta">${event.recordIds.flatMap(id=>data.verificationLedger.records[id].sources).filter((src,i,all)=>all.findIndex(s=>s.url===src.url)===i).map(src=>linkSource(src.url,esc(src.title)+' ↗')).join(' · ')}</div></div>`).join('');
    const spins=familyEdges(data,family,showPending).filter(e=>['spinOff','succession'].includes(e.kind));
    $('spin-history').innerHTML=spins.length?spins.map(e=>`<div class="spin-event"><button data-node="${e.parent}">${esc(nodeName(e.parent))}</button> <span>↗</span> <button data-node="${e.child}">${esc(nodeName(e.child))}</button><p>${esc(e.kind==='succession'?e.note:'成员独立线索 · 待补原始公告；不表示母子公司或旧作继承')}</p><div class="event-meta"><span>${esc(e.dateLabel)}</span>${linkSource(e.source,e.kind==='succession'?'同期报道 ↗':'资料线索 ↗')}</div></div>`).join(''):`<p class="empty-lane">${!showPending&&family.id==='silkys'?'待核衍生线索已隐藏。':'此家族暂无已核的组织衍生记录。'}<br><button data-family="silkys">查看 Silky’s 待核示例 →</button></p>`;
  }
  function renderDetail(){
    const n=nodes.get(selected);if(!n)return;
    const edges=familyEdges(data,family,showPending).filter(e=>e.child===n.id||e.parent===n.id);
    const histories=historiesFor(data,family).filter(h=>h.fromId===n.id||h.toId===n.id);
    const alias=[...new Set(n.aliases)].filter(a=>a!==n.name).slice(0,3).join(' / ');
    const incoming=data.edges.find(e=>e.kind==='spinOff'&&e.child===n.id&&e.status==='pending');
    const status=incoming?'pending':n.verification;
    const description=n.historyNote||'主体身份、组织归属与作品参与分别记录。点击相连节点继续探索。';
    const verificationNotes=(n.verificationNotes||[]).map(note=>`<div class="verification-note"><p>${esc(note.note)}</p>${note.recordIds.flatMap(id=>data.verificationLedger.records[id].sources).filter((src,i,all)=>all.findIndex(s=>s.url===src.url)===i).map(src=>linkSource(src.url,esc(src.title)+' ↗')).join(' · ')}</div>`).join('');
    const collaborations=(data.cooperations||[]).filter(c=>c.entityIds.includes(n.id)).map(c=>`<div class="verification-note"><strong>${esc(c.label)}</strong><p>${esc(c.note)}</p>${c.entityIds.filter(id=>id!==n.id).map(id=>`<a href="organizations.html?node=${encodeURIComponent(id)}&group=verification">${esc(nodeName(id))} ↗</a>`).join(' · ')}</div>`).join('');
    const relations=edges.map(e=>{const parent=e.child===n.id,other=parent?e.parent:e.child;const label=e.kind==='parent'?(parent?'母公司':'子公司'):e.kind==='spinOff'?(parent?'衍生来源（待核）':'衍生组织（待核）'):e.kind==='succession'?(parent?'业务与资产来源':'后继业务组织'):(parent?'上级／关联组织':'旗下／家族品牌');return `<div class="detail-relation"><div class="small-label">${label}</div><button data-node="${other}">${esc(nodeName(other))} ↗</button><p>${esc(e.dateLabel)} · ${esc(STATUS[e.status]||e.status)}</p><p>${esc(e.note)}</p>${linkSource(e.source)}</div>`;}).join('');
    $('detail-panel').innerHTML=`<div class="detail-kicker"><span class="node-kind">${TYPES[n.type]||'主体'}</span><span class="status-dot ${status==='pending'?'pending':''}">${STATUS[status]||'沿用档案'}</span></div><div class="detail-logo" aria-hidden="true">${esc(n.name.slice(0,1))}</div><h2>${esc(n.name)}</h2><p class="detail-alias">${esc(alias||'独立主体档案')}</p><p class="detail-description">${esc(description)}</p><div class="detail-stats"><div><strong>${n.stats.main}</strong><span>关联主库作品</span></div><div><strong>${n.productionCount}</strong><span>主库制作记录</span></div><div><strong>${n.stats.related}</strong><span>跨类型关联</span></div><div><strong>${n.stats.bibliography}</strong><span>仅专题书目</span></div></div>${verificationNotes?`<section class="detail-section"><h3>本轮组织核查</h3>${verificationNotes}</section>`:''}${collaborations?`<section class="detail-section"><h3>项目合作</h3>${collaborations}</section>`:''}<section class="detail-section"><h3>与此主体相连<span>${edges.length} 条</span></h3>${relations||'<p class="empty-lane">暂无已登记组织关系。</p>'}</section>${histories.length?`<section class="detail-section"><h3>名称沿革</h3>${histories.map(h=>`<div class="detail-relation"><button data-node="${h.toId}">${esc(h.oldName)} → ${esc(h.newName)}</button><p>${esc(h.note)}</p>${linkSource(h.source)}</div>`).join('')}</section>`:''}${n.works.length?`<section class="detail-section"><h3>直接关联作品<span>按原作年选列</span></h3>${n.works.map(w=>`<a class="detail-work" href="index.html?query=${encodeURIComponent(w.title)}#catalogue"><span>${esc(w.title)}</span><time>${w.year}</time></a>`).join('')}</section>`:''}<div class="detail-actions">${catalogue?`<a class="button-primary" href="#creator-works">按职责浏览本主体作品 <span>↓</span></a>`:''}${!n.previewOnly?`<a class="button-primary" href="${browseLink(n.id)}">浏览该主体关联作品 <span>↗</span></a><a class="button-secondary" href="entities.html#${n.id}">查看完整主体档案 <span>↗</span></a>`:`<a class="button-primary" href="${safeUrl(n.sources[0])}" target="_blank" rel="noopener noreferrer">查看母公司关系公告 <span>↗</span></a>`}${n.dossiers.map(d=>`<a class="button-secondary" href="${esc(d.id)}.html">${esc(d.name)}专题 <span>↗</span></a>`).join('')}</div><p class="detail-footnote">数量仅统计本主体的直接记录。组织关系不自动继承作品或创作风格；未核时间不等于当前归属。</p><details class="source-details"><summary>主体来源与记录依据</summary>${n.sources.map((s,i)=>linkSource(s,`${i+1}. ${esc(new URL(s).hostname)} ↗`)).join('')}</details>`;
  }
  function render(){
    $('family-title').textContent=family.title;
    renderNav();renderGraph();renderHistory();renderDetail();if(catalogue)renderCatalogue();setURL();
    $('graph-scroll').hidden=view!=='tree';$('relation-list').hidden=view!=='list';
    document.querySelectorAll('[data-view]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.view===view)));
  }
  workspace.addEventListener('click',e=>{
    const familyButton=e.target.closest('[data-family]');if(familyButton){chooseFamily(familyButton.dataset.family);return;}
    const fold=e.target.closest('[data-collapse]');if(fold){const id=fold.dataset.collapse;if(collapsed.has(id))collapsed.delete(id);else collapsed.add(id);renderGraph();return;}
    const button=e.target.closest('[data-node]');if(button){selected=button.dataset.node;if(catalogue)$('work-search').value='';renderGraph();renderDetail();if(catalogue)renderCatalogue();setURL();return;}
    const viewButton=e.target.closest('[data-view]');if(viewButton){view=viewButton.dataset.view;render();}
  });
  $('family-search').addEventListener('input',renderNav);
  $('show-pending').addEventListener('change',()=>{showPending=$('show-pending').checked;if(!showPending&&data.edges.some(e=>e.kind==='spinOff'&&e.child===selected))selected=family.root;render();});
  $('zoom-in').addEventListener('click',()=>{zoom=Math.min(1.4,Math.round((zoom+.1)*10)/10);renderGraph();});
  $('zoom-out').addEventListener('click',()=>{zoom=Math.max(.7,Math.round((zoom-.1)*10)/10);renderGraph();});
  $('reset-tree').addEventListener('click',()=>{collapsed=new Set();zoom=1;renderGraph();centerGraph();toast('关系树已展开并恢复缩放');});
  function renderCatalogue(){
    const placement=$('work-placement').value;
    const found=creatorNodes(data,{kind:$('creator-kind').value,placement,query:$('creator-search').value});
    $('creator-count').textContent=`${found.length} 个主体`;
    if($('registration-progress')&&data.registrationProgress){const p=data.registrationProgress;const complete=!p.nextEntityId;const group=p.letter==='数字及其他'?'数字及其他':`${esc(p.letter)} 字母`;const tail=complete?`全队列累计 ${p.processedEntityIds.length} 个 · 当前队列已完成`:`A—Z 累计 ${p.processedEntityIds.length} 个 · 下一家：${esc(p.nextName)}`;const second=data.recheckProgress;const recheck=second?`<br>二轮身份复核 ${second.processedEntityIds.length} / ${second.total} 个 · 仍待核 ${data.nodes.filter(n=>n.verification==='unresolved').length} 个 · 下一家：${esc(second.nextName)} <a href="${esc(second.audit)}">查看二轮依据 ↗</a>`:'';$('registration-progress').innerHTML=`${group}已核查 ${p.letterProcessed??p.processedEntityIds.length} / ${p.letterTotal??p.total} 个主体 · ${tail} <a href="${esc(p.audit)}">查看证据与待核清单 ↗</a>${recheck}`;}
    if($('verification-summary')&&data.verificationLedger){const v=data.verificationLedger;$('verification-summary').innerHTML=`第${v.source.round}轮已整理台账：${v.total}条 · ${v.entityCount}个主体／专题。${v.changedCount?`本次更新${v.changedCount}条。`:""}`+Object.entries(v.counts).map(([status,count])=>`${esc(status)} ${count}`).join(' · ')+`。<a href="${esc(v.audit)}">查看本轮整理说明 ↗</a>`;}
    $('creator-grid').innerHTML=found.length?found.map(n=>`<button class="creator-card" data-creator="${n.id}" aria-pressed="${n.id===selected}"><span class="node-kind">${TYPES[n.type]||'主体'}</span><strong>${esc(n.name)}</strong><span>${worksFor(data,n,'creation',placement).length} 部创作 · ${worksFor(data,n,'pending',placement).length} 部专题待核</span></button>`).join(''):'<p class="muted">暂无符合条件的创作厂商。可选择“全部主体（含发行与待核）”继续查找。</p>';
    renderWorks();
  }
  function renderWorks(){
    const n=nodes.get(selected),placement=$('work-placement').value;
    $('creator-works-title').textContent=n.name+' · 作品分类';
    $('creator-works-note').textContent='按本主体的直接职责归类；创作作品包括原作制作、开发、联合制作和制作品牌，具体适用版本见依据。仅有原作发行署名或进入专题，均不自动认定为创作。';
    $('work-groups').innerHTML=Object.entries(GROUPS).map(([key,label])=>`<button data-work-group="${key}" aria-pressed="${workGroup===key}">${label}<span>${worksFor(data,n,key,placement).length}</span></button>`).join('');
    if($('verification-controls'))$('verification-controls').hidden=workGroup!=='verification';
    if(workGroup==='verification'){
      const rows=verificationRecords(data,n,{placement,query:$('work-search').value,status:verificationStatus,category:verificationCategory,changedOnly:verificationChangedOnly});
      $('creator-works-note').textContent=`第${data.verificationLedger.source.round}轮台账按所指作品与版次展示。证据充分、限版确认、部分证据、证据冲突与仍待核分别保留；正式创作职责以已登记的具名审核为准。`;
      $('creator-work-list').innerHTML=`<p class="work-result-count">当前主体 · ${rows.length}条核查结论</p>`+rows.map(r=>{
        const w=data.works[r.workId],previous=data.verificationLedger.recordHistory?.[r.recordId],isChanged=data.verificationLedger.changedRecordIds?.includes(r.recordId),revisions=data.verificationLedger.recordHistories?.[r.recordId]||(previous?[previous]:[]);return `<article class="creator-work verification-record" data-record-id="${esc(r.recordId)}"><div class="work-card-heading"><time>${w.year}</time><div><h3><a href="${esc(w.href)}">${esc(w.title)} ↗</a></h3><p>${esc(r.category)} · 原序号${r.id} · ${esc(r.topic)}${r.newRound?` · 原台账第${r.newRound}轮`:""}${isChanged?` · 第${data.verificationLedger.source.round}轮快照修订（原为${esc(previous.status)}）`:""}</p></div><span class="verification-status ${r.status==='证据冲突'?'conflict':r.status==='仍待核'?'pending':r.status==='证据充分'?'confirmed':'limited'}">${esc(r.status)}</span></div><p>${esc(r.detail)}</p><details class="work-evidence"><summary>查看版次范围与原始依据</summary><p>冻结清单范围：${esc(r.placement)}</p><p>原核查问题：${esc(r.need)}</p><p>资料性质：${esc(r.strength)}；具体来源以每个链接标示为准。</p>${r.sources.map(src=>`<p>${linkSource(src.url,esc(src.title)+' ↗')}</p>`).join('')||'<p>尚无独立查证来源。</p>'}<p>原清单线索：${linkSource(r.oldUrl)}</p>${revisions.map(entry=>`<details class="verification-history"><summary>对照第${entry.round}轮记录：${esc(entry.status)}</summary><p>${esc(entry.detail)}</p>${entry.sources.map(src=>`<p>${linkSource(src.url,esc(src.title)+" ↗")}</p>`).join("")||"<p>当时尚无独立查证来源。</p>"}</details>`).join("")}</details></article>`;
      }).join('')+(rows.length?'':'<p class="work-empty">当前范围暂无匹配核查记录，可切换作品位置或筛选条件。</p>');
      return;
    }
    const rows=worksFor(data,n,workGroup,placement,$('work-search').value);
    const positionLabel={main:'主库作品',related:'叙事／跨类型关联',bibliography:'仅专题书目'}[placement];
    $('creator-work-list').innerHTML=rows.length?`<p class="work-result-count">${positionLabel} · ${GROUPS[workGroup]} · ${rows.length} 部，按原作首发年排序</p>`+rows.map(r=>{
      const w=data.works[r.workId],cs=r.creditIds.map(id=>data.credits[id]);
      const roles=[...new Set(cs.map(c=>data.roleLabels[c.role]||c.role))];
      const evidence=cs.filter(c=>workGroup!=='creation'||data.creationRoles.includes(c.role));
      return `<article class="creator-work"><div class="work-card-heading"><time>${w.year}</time><div><h3><a href="${esc(w.href)}">${esc(w.title)} ↗</a></h3><p>${esc(w.originalTitle)} · ${esc(w.category)}</p></div><span class="work-role ${workGroup==='pending'?'pending-role':''}">${GROUPS[workGroup]}</span></div><p class="work-credit-summary">${esc(roles.join(' · ')||'专题引用，具体职责未核')}${workGroup==='pending'?' · 专题职责待核':''}</p><details class="work-evidence"><summary>查看署名、适用范围与来源</summary>${evidence.map(c=>`<div><strong>${esc(data.roleLabels[c.role]||c.role)}</strong> · ${{work:'作品层',content:'内容版本层',release:'平台发行层'}[c.targetType]||esc(c.targetType)} ${esc(c.targetId)}<p>署名原文：${esc(c.rawCredit)}</p><p>${esc(c.note)}</p><p>${esc(STATUS[c.status]||({existingCredit:'沿用发行记录',existingEvidence:'沿用档案依据'}[c.status])||c.status)} · ${linkSource(c.source)}</p></div>`).join('')}${r.pendingRefs.map(ref=>`<div><strong>专题职责待核</strong><p>来自 <a href="${esc(ref.dossierId)}.html">${esc(ref.dossierId)} 专题</a>，保留原待核状态。</p>${linkSource(ref.source)}</div>`).join('')}</details></article>`;
    }).join(''):`<p class="work-empty">当前${positionLabel}范围内，暂无“${GROUPS[workGroup]}”记录。${workGroup==='creation'?'可查看其他职责组；暂无记录不代表该主体未参与创作。':''}</p>`;
  }
  if(catalogue){
    const mainWorks=Object.values(data.works).filter(w=>w.placement==='main').length,withCreation=new Set(data.nodes.flatMap(n=>worksFor(data,n,'creation','main').map(r=>r.workId))).size;
    $('creation-coverage').textContent=`主库 ${mainWorks} 部作品中，${withCreation} 部已有直接创作记录，${mainWorks-withCreation} 部仍待补充创作依据。选择主体后，下方按职责列出作品；发行署名与专题待核不计入创作数量。`;
    $('organization-total').textContent=`${data.nodes.filter(n=>!n.previewOnly).length} 个主体 · ${data.families.length} 组组织档案。点击节点，再按职责浏览作品。`;
    if($('verification-status'))$('verification-status').addEventListener('change',()=>{verificationStatus=$('verification-status').value;renderWorks();});
    if($('verification-changed'))$('verification-changed').addEventListener('change',()=>{verificationChangedOnly=$('verification-changed').checked;renderWorks();});
    if($('verification-category'))$('verification-category').addEventListener('change',()=>{verificationCategory=$('verification-category').value;renderWorks();});
    $('creator-search').addEventListener('input',renderCatalogue);$('creator-kind').addEventListener('change',renderCatalogue);
    $('work-placement').addEventListener('change',()=>{renderCatalogue();setURL();});$('work-search').addEventListener('input',renderWorks);
    $('work-groups').addEventListener('click',e=>{const button=e.target.closest('[data-work-group]');if(button){workGroup=button.dataset.workGroup;renderWorks();setURL();}});
    $('creator-grid').addEventListener('click',e=>{const button=e.target.closest('[data-creator]');if(!button)return;const f=data.families.find(f=>[f.root,...f.entityIds].includes(button.dataset.creator));if(!f)return;family=f;selected=button.dataset.creator;collapsed=new Set();zoom=1;workGroup='creation';$('work-search').value='';render();centerGraph();$('creator-works').scrollIntoView({block:'start'});});
  }
  render();centerGraph();workspace.setAttribute('aria-busy','false');
}
if(typeof document!=='undefined')init();
