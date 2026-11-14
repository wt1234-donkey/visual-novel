import {createEditClient} from './contents-repository.mjs';
import {submitCommand} from './command-transport.mjs';
import {validateIdentityStore} from '../../domain/catalogue/source-identities.mjs';
export const IDENTITY_PATH='data/source-identity-decisions.json';
export function createIdentityRepository(token='',fetcher=fetch,{sourceLease=null}={}){
 const client=createEditClient(token,fetcher,{historyPath:IDENTITY_PATH,sourceLease,validate:validateIdentityStore});
 let selection={};
 const read=options=>{selection=options||{};return client.readCurrent('identity',selection);};
 return {
  connect:()=>client.connect(),read,current:(snapshot,options)=>{selection=options||{};return client.current('identity',snapshot,selection);},readPublished:()=>client.readPublished(),audit:snapshot=>client.audit('identity',snapshot),
  async executeCommand(command){
   if(command.kind!=='identity')throw Error('身份核对命令类型无效');
   const receipt=await submitCommand(client.gitRequest,{...command,sourceLease:command.sourceLease||sourceLease});
   return {...receipt,...await client.readCurrent('identity',{...selection,verifySource:false})};
  }
 };
}
