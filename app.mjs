import {registerPageRecovery,restoreReleaseState} from './src/features/release-recovery.mjs';
import './release-runtime.mjs';
import {readReleaseJson} from './src/infrastructure/storage/release-reader.mjs';
import {createOnDemandReader} from './src/infrastructure/storage/on-demand-reader.mjs';
import {mergeFormalDatasets,displayTitle as effectiveTitle} from './src/domain/catalogue/effective.mjs';
import {applyWorkEdits} from './work-edit-model.mjs?v=20261104-creators';
import {createEntityIndex,entityWorkCounts,summarizeCredits,displayPublisherName,BRAND_ROLES,DEVELOPER_ROLES,PUBLISHER_ROLES} from './entities.mjs?v=20261021-names';
import {filterCatalogue,publisherWorkCounts,visibleVoiceNote} from './filter.mjs?v=20261021-entities';

const $=id=>document.getElementById(id);
const fields={query:$('search'),category:$('category'),subcategory:$('subcategory'),company:$('legacy-company-select'),publisher:$('company-select'),brand:$('brand-select'),developer:$('developer-select'),participant:$('participant-select'),participantRole:$('participant-role'),dossier:$('dossier-select'),dossierRelation:$('dossier-relation'),platform:$('platform'),from:$('from'),to:$('to'),voice:$('voice'),sort:$('sort'),contentStatus:$('content-status'),interaction:$('interaction')};
let entityIndex;
let workNotes={};
const label=(tag,className,text)=>{const el=document.createElement(tag);if(className)el.className=className;el.textContent=text;return el};
const safeLink=(url,title)=>{const a=label('a','source-link',title);try{const u=new URL(url);if(['https:','http:'].includes(u.protocol)){a.href=u.href;a.target='_blank';a.rel='noopener noreferrer'}}catch{}return a};

function renderCard({work,platformReleases:versions,contentVersions}){
  const compact=label('article','card','');compact.id=work.id;compact.append(label('h3','',effectiveTitle(work)),label('p','original',work.originalTitle),label('p','',`${work.firstYear} · ${work.category} · ${work.subcategory}`),label('p','intro',work.synopsis));const link=label('a','source-link','打开完整作品、版本、附注与署名 →');link.href='index.html#work/'+encodeURIComponent(work.id)+'/profile';compact.append(link);return compact;
}

function readFilters(){return {...Object.fromEntries(Object.entries(fields).map(([key,node])=>[key,node.value])),includeAffiliates:$('include-affiliates').checked}}

async function main(){
  try {
    const reader=createOnDemandReader();let queryDetails,renderSerial=0;
    const [directory,taxonomy]=await Promise.all([reader.directory('formal'),readReleaseJson('data/taxonomy.json')]);
    const data=directory.data,catalogue=directory.catalogue;workNotes={};
    entityIndex=createEntityIndex(data,catalogue.model,catalogue);
    const typeCounts=new Map();for(const e of catalogue.model.entities)typeCounts.set(e.type,(typeCounts.get(e.type)||0)+1);
    $('entity-stat-status').textContent=`${typeCounts.get('company')||0}个公司／组织 · ${typeCounts.get('brand')||0}个品牌 · ${catalogue.model.dossiers.length}个专题；其他团队、刊物和待核身份见主体档案。`;
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
    function fillEntities(node,counts){
      for(const [id,count] of [...counts].sort((a,b)=>b[1]-a[1]||entityIndex.entities.get(a[0]).name.localeCompare(entityIndex.entities.get(b[0]).name,'zh'))){
        const entity=entityIndex.entities.get(id),option=label('option','',`${entity.name}〔${entityIndex.model.typeLabels[entity.type]}〕 · ${count?count+'部':'需展开品牌关系'}`);option.value=id;node.append(option);
      }
    }
    const publisherCounts=entityWorkCounts(entityIndex,PUBLISHER_ROLES,{releaseOnly:true});
    for(const [name,count] of [...publisherWorkCounts(data)].sort((a,b)=>b[1]-a[1])){const option=label('option','',`${name==='__unattributed__'?'非商业／未署商业厂商':displayPublisherName(entityIndex,name)} · ${count}部`);option.value=name;fields.company.append(option);}
    const unattributedCount=filterCatalogue(data,{publisher:'__unattributed__'},entityIndex).length;if(unattributedCount){const option=label('option','',`非商业／未署发行方 · ${unattributedCount}部`);option.value='__unattributed__';fields.publisher.append(option);}
    fillEntities(fields.publisher,publisherCounts);fillEntities(fields.brand,entityWorkCounts(entityIndex,BRAND_ROLES));
    const developerCounts=entityWorkCounts(entityIndex,DEVELOPER_ROLES);
    // Registered parent organizations are selectable only with the explicit family-expansion switch.
    for(const relation of entityIndex.model.relations)if(developerCounts.has(relation.from)&&!developerCounts.has(relation.to))developerCounts.set(relation.to,0);
    fillEntities(fields.developer,developerCounts);fillEntities(fields.participant,entityWorkCounts(entityIndex));
    for(const [id,name] of Object.entries(entityIndex.model.roleLabels)){
      const option=label('option','',name);option.value=id;fields.participantRole.append(option);
    }
    for(const dossier of entityIndex.model.dossiers){const option=label('option','',dossier.name);option.value=dossier.id;fields.dossier.append(option);}
    const params=new URLSearchParams(location.search);
    for(const key of ['brand','developer','publisher','participant','participantRole','dossier','dossierRelation','query'])if(params.has(key))fields[key].value=params.get(key);
    $('include-affiliates').checked=params.get('includeAffiliates')==='true';
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
    let visible=25;const more=label('button','','显示更多作品');more.type='button';$('cards').after(more);more.addEventListener('click',()=>{visible+=25;render();});
    const render=async()=>{
      const ticket=++renderSerial,filters=readFilters(),byId=new Map(data.works.map(w=>[w.id,w]));let searchable=data;
      if(filters.query){try{queryDetails??=reader.optional('advancedSearch').catch(error=>{queryDetails=null;throw error;});const details=await queryDetails;if(ticket!==renderSerial)return;searchable={...data,works:data.works.map(w=>({...w,synopsis:data.searchById[w.id]||w.synopsis})),contentVersions:data.contentVersions.map(c=>({...c,evidence:details.contents[c.id]})),platformReleases:data.platformReleases.map(r=>({...r,differences:details.releases[r.id]}))};}catch(error){if(ticket===renderSerial)$('result-count').textContent='检索详情暂不可用：'+error.message+'；已显示的目录保留，请重试。';return;}}
      const matches=filterCatalogue(searchable,filters,entityIndex).map(row=>({...row,work:byId.get(row.work.id)}));
      const count=matches.reduce((n,item)=>n+item.platformReleases.length,0);
      $('result-count').textContent=`显示 ${matches.length} 部作品 · ${matches.reduce((n,item)=>n+item.contentVersions.length,0)} 个内容版本 · ${count} 条平台发行`;
      $('empty').hidden=matches.length>0;
      $('cards').replaceChildren(...matches.slice(0,visible).map(renderCard));
      more.hidden=visible>=matches.length;
      for(const button of $('company-quick-list').querySelectorAll('button')){
        button.setAttribute('aria-pressed',String(button.value===fields.brand.value));
      }
    };
    const brands=[...entityWorkCounts(entityIndex,BRAND_ROLES)].sort((a,b)=>b[1]-a[1]);
    for(const [id,count] of [['',data.works.length],...brands.slice(0,8)]){
      const button=label('button','',id?`${entityIndex.entities.get(id).name} · ${count}部`:`全部品牌 · ${count}部`);
      button.type='button';button.value=id;
      button.addEventListener('click',()=>{fields.brand.value=id;render()});$('company-quick-list').append(button);
    }
    $('include-affiliates').addEventListener('change',render);
    for(const [key,node] of Object.entries(fields)){
      node.addEventListener(key==='query'||key==='from'||key==='to'?'input':'change',()=>{
        if(key==='category')fillSubcategories();
        if(key==='subcategory' && !fields.category.value && fields.subcategory.value){
          fields.category.value=Object.keys(taxonomy.subcategories).find(category=>taxonomy.subcategories[category].includes(fields.subcategory.value))||'';
          fillSubcategories();
        }
        visible=25;render();
      });
    }
    $('clear').addEventListener('click',()=>{for(const [key,node] of Object.entries(fields))node.value=key==='sort'?'oldest':'';$('include-affiliates').checked=false;fillSubcategories();render();fields.query.focus()});
    registerPageRecovery({capture:readFilters,restore:async saved=>{for(const [key,node] of Object.entries(fields))if(typeof saved[key]==='string')node.value=saved[key];$('include-affiliates').checked=!!saved.includeAffiliates;fillSubcategories();render();}});
    render();await restoreReleaseState();
    if(/^#g\d+$/.test(location.hash))location.replace('index.html#work/'+location.hash.slice(1)+'/profile');
  }catch(error){$('result-count').textContent='数据加载失败';$('empty').hidden=false;$('empty').querySelector('span').textContent='请从 GitHub Pages 或本地 HTTP 服务访问；'+error.message}
}
main();
