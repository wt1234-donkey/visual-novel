import {validateValues} from '../../domain/catalogue/model.mjs';
import {validateStyleTags,validateStyleEvidence} from '../../domain/taxonomy/style-tags.mjs';
import {journalKey} from '../../domain/catalogue/journal.mjs';
export const COMMAND_LIMIT=1024*1024;
export const commandText=command=>journalKey(command);
const fail=message=>{throw Object.assign(Error(message),{code:'INVALID_COMMAND'});};
const object=value=>value&&typeof value==='object'&&!Array.isArray(value);
const exact=(value,keys)=>{if(!object(value)||Object.keys(value).some(key=>!keys.includes(key)))fail('命令包含未允许字段');};
const id=value=>typeof value==='string'&&value.length>0&&value.length<=500&&!['__proto__','constructor','prototype'].includes(value);
function clean(value,depth=0){
 if(depth>30)fail('命令层级过深');
 if(value&&typeof value==='object')for(const [key,item]of Object.entries(value)){if(['__proto__','constructor','prototype'].includes(key))fail('命令含保留字段');clean(item,depth+1);}
}
export function validateBasicAction(action){
 const fields={edit:['type','id','values'],add:['type','works'],'style-update':['type','rows'],merge:['type','mainId','ids','relation'],delete:['type','id'],detach:['type','id'],undo:['type','targetId']};
 if(!fields[action?.type])fail('基础命令类型无效');exact(action,fields[action.type]);
 if(['edit','delete','detach'].includes(action.type)&&!id(action.id))fail('目标身份无效');
 if(action.type==='edit')validateValues(action.values);
 if(action.type==='add'){
  if(!Array.isArray(action.works)||!action.works.length||action.works.length>500)fail('每批新增1至500部');
  for(const work of action.works){exact(work,['id','title','firstYear','yearStatus','group','gameplay','plotStyles','plotTags','plotTagEvidence','source']);const {id:identity,...values}=work;if(!id(identity))fail('新增身份无效');validateValues({...values,plotStyles:values.plotStyles||[]});}
 }
 if(action.type==='style-update'){
  if(!Array.isArray(action.rows)||!action.rows.length||action.rows.length>500||new Set(action.rows.map(row=>row.id)).size!==action.rows.length)fail('每批标签更新1至500部不同作品');
  for(const row of action.rows){exact(row,['id','title','mode','tags','evidence']);if(!id(row.id)||!['fill','append','set','remove'].includes(row.mode))fail('标签目标或模式无效');validateStyleTags(row.tags,{allowClear:row.mode==='set'});if(row.evidence)validateStyleEvidence(row.evidence,row.tags);}
 }
 if(action.type==='merge'){
  if(!id(action.mainId)||!Array.isArray(action.ids)||!action.ids.length||action.ids.length>500||action.ids.some(value=>!id(value))||new Set(action.ids).size!==action.ids.length)fail('合并身份无效');
  exact(action.relation,['type','label','note','source']);
 }
 if(action.type==='undo'&&!id(action.targetId))fail('回撤目标无效');
 return action;
}
export function validateCommand(command){
 clean(command);exact(command,['schemaVersion','operationId','kind','actor','at','reason','sources','expectedRevision','sourceLease','action']);
 if(command.schemaVersion!==1||!id(command.operationId)||!['basic','formal'].includes(command.kind)||!id(command.actor)||!Number.isFinite(Date.parse(command.at))||!Number.isSafeInteger(command.expectedRevision)||command.expectedRevision<0||typeof command.reason!=='string'||command.reason.length>1000||!Array.isArray(command.sources)||command.sources.length>100||command.sources.some(url=>typeof url!=='string'||!/^https?:\/\//.test(url)))fail('命令身份、修订或依据无效');
 const lease=command.sourceLease;exact(lease,['schemaVersion','files']);if(lease.schemaVersion!==1||!object(lease.files)||Object.entries(lease.files).some(([key,value])=>!key||!/^([a-f0-9]{40})$/.test(value)))fail('来源凭据无效');
 if(command.kind==='basic')validateBasicAction(command.action);
 else{
  const fields={edit:['type','workId','values'],creators:['type','workId','names'],undo:['type','workId','targetId']};
  if(!fields[command.action?.type])fail('正式命令类型无效');exact(command.action,fields[command.action.type]);if(!id(command.action.workId))fail('正式作品身份无效');
  if(command.action.type==='undo'&&!id(command.action.targetId))fail('正式回撤目标无效');
 }
 if(new TextEncoder().encode(commandText(command)).length>COMMAND_LIMIT)fail('命令超过1MiB，请拆批');
 return command;
}
