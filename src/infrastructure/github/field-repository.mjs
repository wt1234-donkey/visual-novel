import {createEditClient} from './contents-repository.mjs';
import {submitCommand} from './command-transport.mjs';
import {validateFieldStore} from '../../domain/catalogue/field-evidence.mjs';
const PATH='data/field-evidence.json';
export function createFieldRepository(token='',fetcher=fetch,{sourceLease=null}={}){
 const client=createEditClient(token,fetcher,{historyPath:PATH,sourceLease,validate:validateFieldStore});
 let selection={};
 const read=options=>{selection=options||{};return client.readCurrent('field',selection);};
 return {connect:()=>client.connect(),read,current:(snapshot,options)=>{selection=options||{};return client.current('field',snapshot,selection);},exportState:snapshot=>client.current('field',snapshot,{exportAll:true}),audit:snapshot=>client.audit('field',snapshot),async executeCommand(command){
  if(command.kind!=='field')throw Error('字段证据命令类型无效');const receipt=await submitCommand(client.gitRequest,{...command,sourceLease:command.sourceLease||sourceLease});
  return {...receipt,...await client.readCurrent('field',{...selection,verifySource:false})};
 }};
}
