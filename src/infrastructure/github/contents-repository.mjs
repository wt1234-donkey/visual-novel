import {readReleaseJson} from '../storage/release-reader.mjs';
import {submitCommand} from './command-transport.mjs';
import {createSourceGuard} from './source-lease.mjs';
import {blobDigest} from '../storage/digests.mjs';
export const EDIT_REPOSITORY='/repos/wt1234-donkey/visual-novel';
const API='https://api.github.com',REPO=EDIT_REPOSITORY;
export const HISTORY_PATH='data/work-edit-history.json';
export const TOKEN_SETUP_URL='https://github.com/settings/personal-access-tokens/new?name=visual-novel-editor&target_name=wt1234-donkey&contents=write';
const permissionHelp='请用有权限的 GitHub 账号，确认 Resource owner 为 wt1234-donkey，Repository access 选择 Only select repositories → visual-novel，Repository permissions → Contents 为 Read and write。Public repositories 仅包含公开仓库读取权限。';
export const decodeContentText=value=>new TextDecoder().decode(Uint8Array.from(atob(value.replace(/\s/g,'')),c=>c.charCodeAt(0)));
const decode=value=>JSON.parse(decodeContentText(value));
const encode=value=>{const bytes=new TextEncoder().encode(JSON.stringify(value,null,2)+'\n');let s='';for(let i=0;i<bytes.length;i+=32766)s+=String.fromCharCode(...bytes.subarray(i,i+32766));return btoa(s);};
export function createEditClient(token='',fetcher=fetch,{historyPath=HISTORY_PATH,validate=null,sourceLease=null,commandMode='legacy'}={}){
 let oauthScopes=null;
 const validateRead=store=>{if(validate)validate(store);else if(!store||![1,2].includes(store.schemaVersion)||!store.records||Array.isArray(store.records))throw Error('修改历史格式不正确，请停止写入并核查');return store;};
 async function request(path,method='GET',body){
  const operation=method!=='GET'?'保存网站修改':path==='/user'?'校验 GitHub 账号':path===REPO?'读取目标仓库':'读取网站修改记录';
  let res;
  try{res=await fetcher(API+path,{method,cache:'no-store',headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',...(token?{Authorization:'Bearer '+token}:{}),...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});}
  catch{throw Error(operation+'失败：无法连接 GitHub API，请检查网络后重试；当前填写保留。');}
  if(!res.ok){
   let payload={};try{payload=(await res.json())||{};}catch{}
   const redact=value=>String(value||'').replaceAll(token||'\u0000','[凭证已隐藏]').replace(/(?:github_pat_|gh[pousr]_)[A-Za-z0-9_]+/g,'[凭证已隐藏]');
   const raw=redact(payload.message),details=raw?'\nGitHub 返回：'+raw.slice(0,500):'';
   let message,code;
   if(res.status===429||res.headers?.get('x-ratelimit-remaining')==='0'||/rate limit|abuse detection/i.test(raw)){
    code='RATE_LIMIT';message='GitHub 请求频率受限，请稍后重试；当前填写保留。';
   }else if(/protected branch|GH006|GH013|repository rule|must be made through a pull request/i.test(raw)){
    code='BRANCH_RULE';message='GitHub 主分支规则拒绝直接提交，需要按仓库要求通过 Pull Request 合并；当前填写保留。';
   }else if(res.status===401){
    code='INVALID_TOKEN';message='连接凭证无效、已过期或已撤销，请重新连接。';
   }else if(res.status===403){
    code='PERMISSION_DENIED';message='GitHub 拒绝'+(method!=='GET'?'写入':'读取')+' wt1234-donkey/visual-novel。'+permissionHelp+' 读取成功不代表已获得写入权限；当前填写保留。';
   }else if(res.status===404){
    code='NOT_FOUND';message=(path===REPO?'目标仓库不可访问。':method!=='GET'?'GitHub 无法访问本次写入的目标文件。':'无法读取修改记录 '+historyPath+'。')+permissionHelp+' 如果权限正确，请核对目标文件是否存在；当前填写保留。';
   }else if(res.status===409||res.status===422&&/sha|already exists|does not match|not a fast forward|non.fast.forward|reference update failed/i.test(raw)){
    code='CONFLICT';message='数据库已变化或写入冲突，请重新读取后核对；没有覆盖其他修改。';
   }else if(res.status===422){
    code='VALIDATION';message='GitHub 拒绝本次提交的内容，请核对下方具体原因；当前填写保留。';
   }else{code='GITHUB_ERROR';message='GitHub 请求失败，请稍后重试；当前填写保留。';}
   const error=Error(operation+'失败（HTTP '+res.status+'）：'+message+details);error.status=res.status;error.code=code;throw error;
  }
  const scopes=res.headers?.get('x-oauth-scopes');
  if(scopes!==undefined&&scopes!==null)oauthScopes=scopes.split(',').map(x=>x.trim()).filter(Boolean);
  return res.status===204?{}:res.json();
 }
 async function readFile(path=historyPath,ref='main'){const file=await request(REPO+'/contents/'+path+'?ref='+encodeURIComponent(ref));const blob=file.content?file:await request(REPO+'/git/blobs/'+file.sha);return {sha:file.sha,text:decodeContentText(blob.content)};}
 const guard=createSourceGuard(request,REPO);
 const dependencies=()=>sourceLease?{...sourceLease,files:Object.fromEntries(Object.entries(sourceLease.files).filter(([path])=>path!==historyPath))}:null;
 return {
  gitRequest:request,readFile,setSourceLease:lease=>{sourceLease=lease;},
  get commandMode(){return commandMode;},setCommandMode:mode=>{commandMode=mode;},
  async executeCommand(command){
   if(commandMode!=='trusted'||!sourceLease||historyPath!==HISTORY_PATH)throw Error('可信正式保存尚未启用');
   const result=await submitCommand(request,{...command,sourceLease:command.sourceLease||sourceLease});
   const head=(await request(REPO+'/git/ref/heads/main')).object.sha,file=await readFile(historyPath,head);
   return {...result,sha:file.sha,store:validateRead(JSON.parse(file.text))};
  },
  async connect(){
   if(!token)throw Error('请填写仅授权本仓库的 GitHub 凭证');
   const [user,repo]=await Promise.all([request('/user'),request(REPO)]);
   if(repo.permissions?.push!==true)throw Error('当前账号 '+(user.login||'未知')+' 未获得 wt1234-donkey/visual-novel 的写入权限。'+permissionHelp);
   if(/^gh[po]_/.test(token)&&oauthScopes!==null&&!oauthScopes.some(s=>s==='repo'||s==='public_repo'))throw Error('当前凭证缺少公开仓库内容写入权限。'+permissionHelp);
   return user.login;
  },
  async readPublished(){
   if(sourceLease)return {sha:null,store:validateRead(await readReleaseJson(historyPath,fetcher))};
   const response=await fetcher('./'+historyPath,{cache:'no-store'});
   if(!response.ok)throw Error('读取已发布修改记录失败（HTTP '+response.status+'）');
   return {sha:null,store:validateRead(await response.json())};
  },
  async read({verifySource=true}={}){
   const head=sourceLease?(await request(REPO+'/git/ref/heads/main')).object.sha:'main';
   if(verifySource)await guard(head,dependencies());const file=await readFile(historyPath,head);
   return {head,sha:file.sha,store:validateRead(JSON.parse(file.text))};
  },
  async write(store,sha,message){
   if(!token)throw Error('请先连接 GitHub 写入权限');if(!sha)throw Error('请先读取 GitHub 最新修改记录后保存；已发布副本不能直接写入');
   validateRead(store);
   if(!sourceLease){const result=await request(REPO+'/contents/'+historyPath,'PUT',{message,branch:'main',sha,content:encode(store)});return {sha:result.content.sha,commit:result.commit.sha,url:result.commit.html_url};}
   const head=(await request(REPO+'/git/ref/heads/main')).object.sha,parent=await guard(head,dependencies());
   const current=await readFile(historyPath,head);
   if(current.sha!==sha)throw Object.assign(Error('作品修改记录已变化，请重新读取后核对'),{code:'CONFLICT',status:409});
   const content=JSON.stringify(store,null,2)+'\n',blob=await request(REPO+'/git/blobs','POST',{content,encoding:'utf-8'});
   if(blob.sha!==await blobDigest(content))throw Error('保存对象摘要不一致');
   const tree=await request(REPO+'/git/trees','POST',{base_tree:parent.tree.sha,tree:[{path:historyPath,mode:'100644',type:'blob',sha:blob.sha}]});
   const commit=await request(REPO+'/git/commits','POST',{message,tree:tree.sha,parents:[head]});
   await request(REPO+'/git/refs/heads/main','PATCH',{sha:commit.sha,force:false});
   return {sha:blob.sha,commit:commit.sha,url:'https://github.com/wt1234-donkey/visual-novel/commit/'+commit.sha};
  }
 };
}
