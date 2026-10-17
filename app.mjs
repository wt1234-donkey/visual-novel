import {filterCatalogue,publisherWorkCounts,visibleVoiceNote} from './filter.mjs?v=20261018-te-soft-v1';

const $=id=>document.getElementById(id);
const fields={query:$('search'),category:$('category'),subcategory:$('subcategory'),company:$('company-select'),platform:$('platform'),from:$('from'),to:$('to'),voice:$('voice'),sort:$('sort'),contentStatus:$('content-status'),interaction:$('interaction')};
const label=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;el.textContent=text;return el};
const safeLink=(url,title)=>{const a=label('a','source-link',title);try{const u=new URL(url);if(['https:','http:'].includes(u.protocol)){a.href=u.href;a.target='_blank';a.rel='noopener noreferrer'}}catch{}return a};

function renderCard({work,platformReleases:versions,contentVersions}){
  const card=label('article','card','');
  const top=label('div','card-top','');
  top.append(label('span','year',String(work.firstYear)),label('span','category category-'+work.category,work.category));
  const displayTitle=work.chineseTitle||work.title;
  const title=label('h3','',displayTitle);
  const original=label('p','original',displayTitle===work.originalTitle?'':`原名 · ${work.originalTitle}`);
  if(work.chineseTitleType==='站内编辑译名') original.append(label('span','editorial-translation',' · 中文名为站内编辑译名'));
  const intro=label('p','intro',work.synopsis);
  const meta=label('div','card-meta','');
  const companies=[...new Set(versions.flatMap(v=>v.publisherCompanies||[]))];
  const publisherLabel=companies.length ? companies.slice(0,2).join(' / ')+(companies.length>2?` 等 ${companies.length} 家`:'') : '非商业／未署商业厂商';
  meta.append(label('span','',`细分类 · ${work.subcategory}`),label('span','',work.genre),label('span','','主要角色 · '+work.characters.join(' / ')),label('span','','发行厂商 · '+publisherLabel));
  card.append(top,title,original,intro,meta);
  const tags=label('div','interaction-tags','');tags.setAttribute('aria-label','互动方式');
  for(const mode of work.interactionModes||[])tags.append(label('span','interaction-tag'+(mode==='待核实'?' pending-tag':''),mode));
  card.append(tags);
  const interactionEvidence=document.createElement('details');interactionEvidence.className='interaction-evidence';
  interactionEvidence.append(label('summary','','互动方式依据 · '+work.interactionBasis),label('p','changes',work.interactionNote));
  for(const source of work.interactionSources||[])interactionEvidence.append(safeLink(source,'玩法资料 ↗'));
  card.append(interactionEvidence);
  const detail=document.createElement('details');detail.className='version-panel';
  detail.append(label('summary','',`查看 ${contentVersions.length} 个内容版本 · ${versions.length} 条平台发行`));
  const container=label('div','version-list','');
  const releaseRow=(release)=>{
    const row=label('div','version release-row','');
    const line=label('div','version-line','');
    line.append(label('strong','',String(release.year)),label('span','platform-name',release.platform),label('span','version-kind',release.kind));
    row.append(line,label('p','publisher','发行／出版：'+release.publisher+(visibleVoiceNote(release)?' · '+visibleVoiceNote(release):'')),label('p','changes',release.differences),safeLink(release.source,'发行来源 ↗'));
    return row;
  };
  for(const content of contentVersions.sort((a,b)=>a.firstYear-b.firstYear)){
    const group=label('section','content-group','');
    group.append(label('h4','content-heading',`${content.firstYear} · ${content.label}`),label('p','content-basis',content.basis==='original'?'原作／首批内容':'有新增内容 · '+content.id),label('p','changes',content.evidence),safeLink(content.source,'内容依据 ↗'));
    const releases=document.createElement('details');releases.className='release-panel';
    const rows=versions.filter(v=>v.contentVersionId===content.id);
    releases.append(label('summary','',`关联平台发行 ${rows.length} 条`),...rows.map(releaseRow));
    group.append(releases);container.append(group);
  }
  const pending=versions.filter(v=>!v.contentVersionId);
  if(pending.length){
    const group=document.createElement('details');group.className='release-panel pending-releases';
    group.append(label('summary','',`内容关系待核实：${pending.length} 条历史发行（不计内容版本）`),label('p','changes','保留旧发行资料。尚未确认新增内容，也未证明与已有内容完全相同。'),...pending.map(releaseRow));
    container.append(group);
  }
  for(const credit of work.editionCredits||[])container.append(label('p','changes',`历史发行补充：${credit.year} · ${credit.platform} · ${credit.publisher}。${credit.reason}`),safeLink(credit.source,'发行补充依据 ↗'));
  detail.append(container);card.append(detail);
  const bottom=label('div','card-bottom','');bottom.append(safeLink(work.source,'作品来源 ↗'));
  if(work.charactersSource)bottom.append(safeLink(work.charactersSource,'角色依据 ↗'));
  if(work.notes)bottom.append(label('span','card-note',work.notes));
  card.append(bottom);
  return card;
}

function readFilters(){return Object.fromEntries(Object.entries(fields).map(([key,node])=>[key,node.value]))}

async function main(){
  try {
    const [response,taxonomyResponse]=await Promise.all([fetch('./data/games.json?v=20261018-te-soft-v1'),fetch('./data/taxonomy.json?v=20261018-te-soft-v1')]);
    if(!response.ok||!taxonomyResponse.ok)throw Error('HTTP '+(response.ok?taxonomyResponse.status:response.status));
    const [data,taxonomy]=await Promise.all([response.json(),taxonomyResponse.json()]);
    $('stat-works').textContent=data.works.length;
    $('stat-versions').textContent=data.contentVersions.length;
    $('stat-releases').textContent=data.platformReleases.length;
    $('content-policy-status').textContent=`${data.platformReleases.filter(v=>!v.contentVersionId).length} 条历史发行的内容关系尚待核实，不计为新增内容版本。`;
    const years=data.platformReleases.map(v=>v.year);$('stat-years').textContent=Math.min(...years)+'—'+Math.max(...years);
    const modeCounts=new Map();for(const work of data.works)for(const mode of work.interactionModes||[])modeCounts.set(mode,(modeCounts.get(mode)||0)+1);
    for(const [mode,description] of Object.entries(taxonomy.interactionModes)){
      if(modeCounts.has(mode)){const option=label('option','',`${mode} · ${modeCounts.get(mode)} 部`);option.value=mode;fields.interaction.append(option)}
      const row=label('div','interaction-definition','');row.append(label('dt','',mode),label('dd','',description));$('interaction-definitions').append(row);
    }
    $('interaction-policy-status').textContent=`互动方式可多选，按作品统计；${modeCounts.get('待核实')||0} 部主目录作品的具体操作待核实。标签为已记录玩法概览，不代表每个机种都有这些操作。`;
    const platforms=[...new Set(data.platformReleases.map(v=>v.platform.trim()))].sort((a,b)=>a.localeCompare(b,'zh'));
    for(const p of platforms){const option=label('option','',p);option.value=p;fields.platform.append(option)}
    const companyCounts=publisherWorkCounts(data);
    const unattributed=companyCounts.get('__unattributed__')||0;
    companyCounts.delete('__unattributed__');
    const orderedCompanies=[...companyCounts].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0],'zh'));
    for(const [company,count] of orderedCompanies){
      const option=label('option','',`${company} · ${count} 部游戏`);option.value=company;fields.company.append(option);
    }
    if(unattributed){const option=label('option','',`非商业／未署商业厂商 · ${unattributed} 部游戏`);option.value='__unattributed__';fields.company.append(option)}
    const fillSubcategories=()=>{
      const previous=fields.subcategory.value;
      const allOption=label('option','','全部细分类');allOption.value='';
      fields.subcategory.replaceChildren(allOption);
      const categories=fields.category.value?[fields.category.value]:Object.keys(taxonomy.subcategories);
      for(const category of categories){
        const parent=fields.category.value?fields.subcategory:document.createElement('optgroup');
        if(parent!==fields.subcategory)parent.label=category;
        for(const name of taxonomy.subcategories[category]){const option=label('option','',name);option.value=name;parent.append(option)}
        if(parent!==fields.subcategory)fields.subcategory.append(parent);
      }
      fields.subcategory.value=categories.some(category=>taxonomy.subcategories[category].includes(previous))?previous:'';
    };
    fillSubcategories();
    const render=()=>{
      const matches=filterCatalogue(data,readFilters());
      const count=matches.reduce((n,item)=>n+item.platformReleases.length,0);
      $('result-count').textContent=`显示 ${matches.length} 部作品 · ${matches.reduce((n,item)=>n+item.contentVersions.length,0)} 个内容版本 · ${count} 条平台发行`;
      $('empty').hidden=matches.length>0;
      $('cards').replaceChildren(...matches.map(renderCard));
      for(const button of $('company-quick-list').querySelectorAll('button')){
        button.setAttribute('aria-pressed',String(button.value===fields.company.value));
      }
    };
    for(const [name,count] of [['',data.works.length],...orderedCompanies.slice(0,8)]){
      const button=label('button','',name?`${name} · ${count} 部游戏`:`全部厂商 · ${count} 部游戏`);
      button.type='button';button.value=name;
      button.addEventListener('click',()=>{fields.company.value=name;render()});
      $('company-quick-list').append(button);
    }
    for(const [key,node] of Object.entries(fields)){
      node.addEventListener(key==='query'||key==='from'||key==='to'?'input':'change',()=>{
        if(key==='category')fillSubcategories();
        if(key==='subcategory' && !fields.category.value && fields.subcategory.value){
          fields.category.value=Object.keys(taxonomy.subcategories).find(category=>taxonomy.subcategories[category].includes(fields.subcategory.value))||'';
          fillSubcategories();
        }
        render();
      });
    }
    $('clear').addEventListener('click',()=>{for(const [key,node] of Object.entries(fields))node.value=key==='sort'?'oldest':'';fillSubcategories();render();fields.query.focus()});
    render();
  }catch(error){$('result-count').textContent='数据加载失败';$('empty').hidden=false;$('empty').querySelector('span').textContent='请从 GitHub Pages 或本地 HTTP 服务访问；'+error.message}
}
main();
