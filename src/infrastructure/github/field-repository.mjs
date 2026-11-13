import {createEditClient} from './contents-repository.mjs';
import {submitCommand} from './command-transport.mjs';
import {validateFieldStore} from '../../domain/catalogue/field-evidence.mjs';
const PATH='data/field-evidence.json';
export function createFieldRepository(token='',fetcher=fetch,{sourceLease=null}={}){
 const client=createEditClient(token,fetcher,{historyPath:PATH,sourceLease,validate:validateFieldStore});
 return {connect:()=>client.connect(),read:()=>client.read(),audit:snapshot=>client.audit('field',snapshot),async executeCommand(command){
  if(command.kind!=='field')throw Error('字段证据命令类型无效');const receipt=await submitCommand(client.gitRequest,{...command,sourceLease:command.sourceLease||sourceLease});
  const head=(await client.gitRequest('/repos/wt1234-donkey/visual-novel/git/ref/heads/main')).object.sha,file=await client.readFile(PATH,head);
  return {...receipt,sha:file.sha,head,store:validateFieldStore(JSON.parse(file.text))};
 }};
}
