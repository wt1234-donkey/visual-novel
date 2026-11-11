export function createSourceGuard(request,repo){
 const cache=new Map();
 return async(head,lease)=>{
  if(!lease)return null;
  if(lease.schemaVersion!==1||!lease.files||!Object.keys(lease.files).length||Object.entries(lease.files).some(([path,sha])=>!(path.startsWith('data/')||path.startsWith('src/')||['work-edit-model.mjs','management-model.mjs'].includes(path))||path.includes('..')||!/^[a-f0-9]{40}$/.test(sha)))throw Error('来源版本凭据无效，请刷新页面');
  if(!cache.has(head))cache.set(head,(async()=>{
   const commit=await request(repo+'/git/commits/'+head);
   const tree=await request(repo+'/git/trees/'+commit.tree.sha+'?recursive=1');
   if(tree.truncated||!Array.isArray(tree.tree))throw Error('无法完整校验来源版本，请稍后重试');
   return {commit,files:new Map(tree.tree.filter(entry=>entry.type==='blob').map(entry=>[entry.path,entry.sha]))};
  })().catch(error=>{cache.delete(head);throw error;}));
  const result=await cache.get(head);
  if(cache.size>4)cache.delete(cache.keys().next().value);
  for(const [path,sha] of Object.entries(lease.files))if(result.files.get(path)!==sha)throw Object.assign(Error('来源资料或编辑规则已更新，请刷新页面后核对；当前填写保留，本次未覆盖新来源。'),{code:'SOURCE_CHANGED',status:409});
  return result.commit;
 };
}
