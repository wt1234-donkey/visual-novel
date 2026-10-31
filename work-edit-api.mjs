const API='https://api.github.com',REPO='/repos/wt1234-donkey/visual-novel';
export const HISTORY_PATH='data/work-edit-history.json';
const decode=value=>JSON.parse(new TextDecoder().decode(Uint8Array.from(atob(value.replace(/\s/g,'')),c=>c.charCodeAt(0))));
const encode=value=>{const bytes=new TextEncoder().encode(JSON.stringify(value,null,2)+'\n');let s='';for(let i=0;i<bytes.length;i+=32766)s+=String.fromCharCode(...bytes.subarray(i,i+32766));return btoa(s);};
export function createEditClient(token='',fetcher=fetch){
 async function request(path,method='GET',body){const res=await fetcher(API+path,{method,cache:'no-store',headers:{Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28',...(token?{Authorization:'Bearer '+token}:{}),...(body?{'Content-Type':'application/json'}:{})},...(body?{body:JSON.stringify(body)}:{})});if(!res.ok){if(res.status===409||res.status===422)throw Error('数据库已变化或写入冲突，请重新读取后核对；没有覆盖其他修改');if(res.status===401)throw Error('连接凭证无效或已过期，请重新连接');if(res.status===403||res.status===404)throw Error('无法访问或写入该仓库，请检查仓库选择、Contents 读写权限与分支保护');throw Error('GitHub 请求失败（HTTP '+res.status+'），请保留当前编辑后重试');}return res.json();}
 return {
  async connect(){if(!token)throw Error('请填写仅授权本仓库的 GitHub 凭证');const [user,repo]=await Promise.all([request('/user'),request(REPO)]);if(repo.permissions?.push===false)throw Error('当前账号没有该仓库写入权限');return user.login;},
  async read(){const file=await request(REPO+'/contents/'+HISTORY_PATH+'?ref=main');const blob=file.content?file:await request(REPO+'/git/blobs/'+file.sha);const store=decode(blob.content);if(store.schemaVersion!==1||!store.records||Array.isArray(store.records))throw Error('修改历史格式不正确，请停止写入并核查');return {sha:file.sha,store};},
  async write(store,sha,message){if(!token)throw Error('请先连接 GitHub 写入权限');const result=await request(REPO+'/contents/'+HISTORY_PATH,'PUT',{message,branch:'main',sha,content:encode(store)});return {sha:result.content.sha,commit:result.commit.sha,url:result.commit.html_url};}
 };
}
