import {fieldKey} from '../../domain/catalogue/field-evidence.mjs';

export async function readAuditCurrent(reader,descriptor,{kind,workIds=[],sourceIds=[],caseIds=[],scope=null,field=null,page=0,exportAll=false,...options}={}){
 if(!descriptor.current)throw Object.assign(Error('此版本尚无按需当前状态，请重新发布后重试'),{code:'CURRENT_REQUIRED'});
 const meta=await reader.read(descriptor.current,options);
 if(meta.type!=='current-state'||meta.kind!==kind||meta.source.sha!==descriptor.source.sha||meta.eventCount!==descriptor.eventCount||meta.revision!==descriptor.currentRevision)throw Error('当前状态投影版本不一致');
 const state={schemaVersion:1,projectionVersion:1,kind,revision:meta.revision,eventCount:meta.eventCount,sourceSha:meta.source.sha,checkpoint:meta.checkpoint,stats:meta.stats,
  ...(kind==='formal'?{records:{},baselineRecords:{}}:kind==='identity'?{links:{},cases:{}}:{assertions:{},choices:{},candidateTotal:0,nextPage:null})};
 async function row(table,id){const ref=meta.tables[table]?await reader.lookup(meta.tables[table],id,options):null;if(!ref)return null;
  const value=await reader.read(ref,options);if(value.type!=='current-row'||value.kind!==kind||value.table!==table||value.id!==id)throw Error('当前状态投影身份不一致');return value.value;}
 if(kind==='formal')for(const id of new Set(workIds)){const value=await row('records',id);if(value){state.records[id]=value.record;if(value.baseline)state.baselineRecords[id]=value.baseline;}}
 else if(kind==='identity')for(const [table,ids] of [['links',sourceIds],['cases',caseIds]])for(const id of new Set(ids)){const value=await row(table,id);if(value)state[table][id]=value;}
 else if(exportAll&&kind==='field'){
  async function keys(ref){if(!ref)return [];const node=await reader.read(ref,options);if(node.type==='map')return Object.entries(node.entries).filter(([,v])=>v).map(([key])=>key);if(node.type!=='branch')throw Error('当前字段导出索引格式无效');const result=[];for(const child of Object.values(node.children))result.push(...await keys(child));return result;}
  for(const key of await keys(meta.tables.groups)){const group=await row('groups',key);if(group.choice)state.choices[key]=group.choice;for(const ref of group.pages){const values=await reader.read(ref,options);if(values.type!=='current-field-page'||values.assertions.some(a=>fieldKey(a.scope,a.field)!==key))throw Error('字段导出分页身份不一致');for(const a of values.assertions)state.assertions[a.id]=a;}}
 }
 else if(scope&&field){
  if(!Number.isSafeInteger(page)||page<0)throw Error('当前字段分页范围无效');
  const key=fieldKey(scope,field),group=await row('groups',key);
  if(group){state.candidateTotal=group.count;if(group.choice)state.choices[key]=group.choice;if(group.selected)state.assertions[group.selected.id]=group.selected;
   if(group.pages[page]){const values=await reader.read(group.pages[page],options);if(values.type!=='current-field-page'||values.assertions.length>50||values.assertions.some(a=>fieldKey(a.scope,a.field)!==key))throw Error('字段候选分页身份不一致');for(const a of values.assertions)state.assertions[a.id]=a;}
   state.nextPage=page+1<group.pages.length?page+1:null;
  }
 }
 return state;
}

export function assertCurrentProjection(state,kind){
 if(state?.projectionVersion!==1||state.kind!==kind||!Number.isSafeInteger(state.revision)||state.revision<0||!Number.isSafeInteger(state.eventCount)||state.eventCount<0||!/^[a-f0-9]{40}$/.test(state.sourceSha))throw Error('当前状态只读投影无效');
 return state;
}
