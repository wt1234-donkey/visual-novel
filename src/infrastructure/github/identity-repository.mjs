import {createEditClient} from './contents-repository.mjs';
import {submitCommand} from './command-transport.mjs';
import {validateIdentityStore} from '../../domain/catalogue/source-identities.mjs';
export const IDENTITY_PATH='data/source-identity-decisions.json';
export function createIdentityRepository(token='',fetcher=fetch,{sourceLease=null}={}){
 const client=createEditClient(token,fetcher,{historyPath:IDENTITY_PATH,sourceLease,validate:validateIdentityStore});
 return {
  connect:()=>client.connect(),read:()=>client.read(),readPublished:()=>client.readPublished(),
  async executeCommand(command){
   if(command.kind!=='identity')throw Error('身份核对命令类型无效');
   const receipt=await submitCommand(client.gitRequest,{...command,sourceLease:command.sourceLease||sourceLease});
   const head=(await client.gitRequest('/repos/wt1234-donkey/visual-novel/git/ref/heads/main')).object.sha;
   const file=await client.readFile(IDENTITY_PATH,head);
   return {...receipt,sha:file.sha,head,store:validateIdentityStore(JSON.parse(file.text))};
  }
 };
}
