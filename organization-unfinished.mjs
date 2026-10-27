const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=value=>String(value??'').normalize('NFKD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/\s+/g,'');
const safeUrl=value=>/^https?:\/\//.test(value)||/^(?:index|organizations|entities|[a-z0-9_]+)\.html(?:[?#].*)?$/.test(value)?esc(value):'#';

export function unfinishedRows(data){
  if(!data.unfinished)return [];
  const nodes=new Map(data.nodes.map(n=>[n.id,n])),edges=new Map(data.edges.map(e=>[e.id,e]));
  const history=new Map(data.nameHistory.map(h=>[h.id,h]));
  const records=data.verificationLedger.records;
  const priority={'仍待核':0,'证据冲突':1,'身份待核':2,'关系待核':3,'正式职责待核':4,'部分证据':5,'限版确认':6,'未登记直接创作依据':7,'起止时间待补':8,'更名时间待补':8};
  return data.unfinished.items.map(item=>{
    const kind=data.unfinished.kinds[item.kind],subjects=item.entityIds.map(id=>nodes.get(id));
    const work=data.works[item.workId],record=records[item.recordId],edge=edges.get(item.edgeId),event=history.get(item.historyId);
    const refs=(item.recordIds||[]).map(id=>records[id]);
    let title=work?work.title:subjects.map(n=>n.name).join(' → '),detail=kind.description;
    let sources=[];
    if(item.kind==='identity'){
      detail=subjects[0].historyNote;
      sources=subjects[0].sources.map(url=>({url,title:'主体原有依据'}));
    }else if(item.kind==='duty'){
      title+=' · '+item.dossierName+'专题';
      detail=kind.description+(refs.length?' 台账已有以下结论，仍需按职责及版次完成正式核定：'+refs.map(r=>r.status+'：'+r.detail).join('；'):' 当前暂无对应的独立台账结论。');
      sources=[{url:item.source,title:'原专题职责线索'},...refs.flatMap(r=>r.sources)];
    }else if(item.kind==='creation'){
      detail=kind.description+' 此项只说明当前索引的登记缺口，不表示没有创作者，也不表示参与主体未创作。';
      sources=[{url:work.href,title:'原作品档案'}];
    }else if(record){
      title+=' · '+record.topic;detail=record.detail+' 核查范围：'+record.placement;
      sources=record.sources.length?record.sources:[{url:record.oldUrl,title:'原清单线索'}];
    }else if(edge){
      title=nodes.get(edge.parent).name+' → '+nodes.get(edge.child).name;
      detail=edge.label+'；'+edge.dateLabel+'。'+edge.note;sources=[{url:edge.source,title:'关系原始依据'}];
    }else if(event){
      title=event.oldName+' → '+event.newName;detail=event.dateLabel+'。'+event.note;
      sources=[{url:event.source,title:'名称沿革依据'}];
    }
    const subjectText=subjects.map(n=>n.name).join(' / ');
    const href=work?.href||`organizations.html?node=${encodeURIComponent(item.entityIds[0])}#workspace`;
    const subjectHref=item.entityIds.length?`organizations.html?node=${encodeURIComponent(item.entityIds[0])}&group=${item.kind==='evidence'?'verification':'pending'}${work?'&placement='+work.placement:''}#creator-works`:null;
    const action=data.unfinished.statusActions[item.status]||kind.action;
    return {...item,title,detail,action,subjectText,href,subjectHref,kindLabel:kind.label,
      sources:sources.filter((s,i,all)=>s.url&&all.findIndex(other=>other.url===s.url)===i),
      searchText:norm([title,subjectText,detail,action,item.status,kind.label,work?.originalTitle,...subjects.flatMap(n=>n.aliases)].join(' '))};
  }).sort((a,b)=>(priority[a.status]??9)-(priority[b.status]??9)||a.title.localeCompare(b.title,'zh-CN')||a.id.localeCompare(b.id));
}

export function filterUnfinished(rows,{query='',kind='',status=''}={}){
  const q=norm(query);
  return rows.filter(row=>(!kind||row.kind===kind)&&(!status||row.status===status)&&(!q||row.searchText.includes(q)));
}

export function unfinishedPage(rows,page=1,size=20){
  const pages=Math.max(1,Math.ceil(rows.length/size)),current=Math.min(pages,Math.max(1,page));
  return {rows:rows.slice((current-1)*size,current*size),page:current,pages,total:rows.length};
}

export function initUnfinished(data){
  const $=id=>document.getElementById(id);
  if(!$('unfinished-rows')||!data.unfinished)return;
  const rows=unfinishedRows(data);let page=1;
  $('unfinished-kind').innerHTML='<option value="">全部事项</option>'+Object.entries(data.unfinished.kinds).map(([id,k])=>`<option value="${id}">${esc(k.label)}</option>`).join('');
  $('unfinished-status').innerHTML='<option value="">全部状态</option>'+[...new Set(rows.map(r=>r.status))].map(s=>`<option>${esc(s)}</option>`).join('');
  $('unfinished-note').textContent=data.unfinished.note;
  function render(){
    const kind=$('unfinished-kind').value;
    $('unfinished-metrics').innerHTML=Object.entries(data.unfinished.kinds).map(([id,k])=>`<button data-unfinished-kind="${id}" aria-pressed="${id===kind}"><strong>${data.unfinished.counts[id]||0}</strong><span>${esc(k.label)}</span></button>`).join('');
    const found=filterUnfinished(rows,{kind,query:$('unfinished-search').value,status:$('unfinished-status').value});
    const result=unfinishedPage(found,page);page=result.page;
    $('unfinished-count').textContent=`匹配 ${result.total} 条事项 · 第 ${page} / ${result.pages} 页`;
    $('unfinished-rows').innerHTML=result.rows.map(row=>`<tr><td><span class="unfinished-kind">${esc(row.kindLabel)}</span><a href="${safeUrl(row.href)}">${esc(row.title)}</a><small>${esc(row.subjectText||'尚未登记直接创作主体')}</small></td><td><span class="unfinished-status">${esc(row.status)}</span></td><td><details><summary>${esc(row.detail.slice(0,100))}${row.detail.length>100?'…':''}</summary><p>${esc(row.detail)}</p></details></td><td><p>${esc(row.action)}</p>${row.subjectHref?`<a href="${safeUrl(row.subjectHref)}">查看对应主体与职责 ↗</a>`:''}<details><summary>查看现有依据（${row.sources.length}）</summary>${row.sources.map(s=>`<p><a href="${safeUrl(s.url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)} ↗</a></p>`).join('')||'<p>暂无已登记来源。</p>'}</details></td></tr>`).join('')||'<tr><td colspan="4">当前筛选没有未完成事项。</td></tr>';
    $('unfinished-prev').disabled=page<=1;$('unfinished-next').disabled=page>=result.pages;
  }
  for(const id of ['unfinished-search','unfinished-kind','unfinished-status'])$(id).addEventListener(id==='unfinished-search'?'input':'change',()=>{page=1;render();});
  $('unfinished-reset').addEventListener('click',()=>{$('unfinished-search').value='';$('unfinished-kind').value='';$('unfinished-status').value='';page=1;render();});
  $('unfinished-metrics').addEventListener('click',event=>{const button=event.target.closest('[data-unfinished-kind]');if(button){$('unfinished-kind').value=button.dataset.unfinishedKind;$('unfinished-status').value='';page=1;render();}});
  $('unfinished-prev').addEventListener('click',()=>{page--;render();});
  $('unfinished-next').addEventListener('click',()=>{page++;render();});
  render();
}
