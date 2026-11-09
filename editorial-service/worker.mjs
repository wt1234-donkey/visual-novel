import {EDITORIAL_REPO,EDITORIAL_LIMIT,EDITORIAL_BATCH_LIMIT,editorialId,validateProposal} from '../editorial-proposal.mjs';

const github='https://api.github.com/repos/'+EDITORIAL_REPO;
const workflow='editorial-publish.yml';
const protectedHeaders={'Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer'};
const reply=(value,status=200)=>Response.json(value,{status,headers:protectedHeaders});
const deny=(message,status=403)=>reply({error:message},status);
const now=()=>new Date().toISOString();
const marks=ids=>ids.map(()=>'?').join(',');
const stmt=(db,sql,...args)=>db.prepare(sql).bind(...args);
const appRoles=new Set(['editor','reviewer','publisher']);

async function member(request,db){
 const id=request.headers.get('oai-authenticated-user-id');
 const email=request.headers.get('oai-authenticated-user-email')?.trim().toLowerCase();
 if(!id||!email)return null;
 // First visitor is the owner while the deployment is owner-private.
 await stmt(db,"INSERT OR IGNORE INTO members(email,user_id,role) SELECT ?,?,'owner' WHERE NOT EXISTS (SELECT 1 FROM members)",email,id).run();
 await stmt(db,'UPDATE members SET user_id=? WHERE email=? AND user_id IS NULL',id,email).run();
 const row=await stmt(db,'SELECT role FROM members WHERE user_id=?',id).first();
 return row?{id,email,role:row.role}:null;
}

async function readBody(request){
 if(!request.headers.get('content-type')?.startsWith('application/json'))throw Error('请求必须为 JSON');
 const stream=request.body?.getReader();
 if(!stream)throw Error('请求为空');
 const decoder=new TextDecoder();
 let size=0,body='';
 try{
  while(true){
   const {value,done}=await stream.read();
   if(done)break;
   size+=value.byteLength;
   if(size>EDITORIAL_LIMIT+1024){await stream.cancel();throw Error('请求超过大小限制');}
   body+=decoder.decode(value,{stream:true});
  }
 }finally{stream.releaseLock();}
 return JSON.parse(body+decoder.decode());
}

function selectedIds(value){
 if(!Array.isArray(value)||!value.length||value.length>EDITORIAL_BATCH_LIMIT||
    value.some(id=>!editorialId(id))||new Set(value).size!==value.length)throw Error('请选择 1 至 20 条不同提案');
 return value;
}

async function gitCall(env,path,options={}){
 if(!env.EDITORIAL_GITHUB_TOKEN)throw Error('发布服务尚未连接 GitHub');
 return fetch(github+path,{...options,headers:{Authorization:'Bearer '+env.EDITORIAL_GITHUB_TOKEN,
  Accept:'application/vnd.github+json','X-GitHub-Api-Version':'2026-03-10','User-Agent':'StoryAtlasEditorial',...options.headers}});
}

async function submit(db,user,body){
 const proposal=validateProposal(body);
 const saved=await stmt(db,'SELECT author,body FROM proposals WHERE id=?',proposal.id).first();
 const payload=JSON.stringify(proposal);
 if(saved)return saved.author===user.id&&saved.body===payload?reply({id:proposal.id}):deny('提案标识冲突，请重新生成',409);
 const result=await stmt(db,`INSERT OR IGNORE INTO proposals(id,author,body,state,submitted_at)
  SELECT ?,?,?,'pending',? WHERE (SELECT COUNT(*) FROM proposals WHERE author=? AND state='pending') < 50`,
  proposal.id,user.id,payload,now(),user.id).run();
 if(!result.meta.changes){
  const current=await stmt(db,'SELECT author,body FROM proposals WHERE id=?',proposal.id).first();
  if(current?.author===user.id&&current.body===payload)return reply({id:proposal.id});
  return deny('提案已存在或待审提案已达上限',409);
 }
 return reply({id:proposal.id},201);
}

async function review(db,user,body){
 if(!['owner','reviewer'].includes(user.role))return deny('此账号没有证据审核权限');
 const ids=selectedIds(body.ids);
 if(!['approved','rejected'].includes(body.decision)||typeof body.note!=='string'||
    !body.note.trim()||body.note.length>2000)throw Error('请填写审核依据或退回原因');
 const where=`id IN (${marks(ids)}) AND state='pending'`;
 // A MATERIALIZED snapshot makes the batch guard independent of rows updated by this statement.
 const sql=`WITH eligible AS MATERIALIZED (SELECT id FROM proposals WHERE ${where})
  UPDATE proposals SET state=?,reviewer=?,reviewed_at=?,review_note=?
  WHERE id IN (SELECT id FROM eligible) AND (SELECT COUNT(*) FROM eligible)=? RETURNING id`;
 const result=await stmt(db,sql,...ids,body.decision,user.id,now(),body.note.trim(),ids.length).all();
 return result.results.length===ids.length?reply({ids}):deny('部分提案已变化，请刷新队列后重新审核',409);
}

async function publish(db,user,env,body){
 if(!['owner','publisher'].includes(user.role))return deny('此账号没有发布权限');
 if(!env.EDITORIAL_GITHUB_TOKEN)return deny('发布服务尚未连接 GitHub，已审核提案仍保留',503);
 const ids=selectedIds(body.ids),id=crypto.randomUUID();
 const rows=(await stmt(db,`SELECT id,body FROM proposals WHERE state='approved' AND id IN (${marks(ids)})`,...ids).all()).results;
 if(rows.length!==ids.length)return deny('只能发布已审核且尚未发布的提案',409);
 const payload=JSON.stringify({id,proposals:ids.map(key=>JSON.parse(rows.find(row=>row.id===key).body))});
 if(new TextEncoder().encode(payload).length>EDITORIAL_LIMIT)throw Error('本次发布超过 55 KB，请分批发布');
 const reserved=await db.batch([
  stmt(db,`INSERT INTO publication_batches(id,state,created_by,created_at)
    SELECT ?,'dispatching',?,? WHERE (SELECT COUNT(*) FROM proposals WHERE state='approved' AND id IN (${marks(ids)}))=?`,
   id,user.id,now(),...ids,ids.length),
  stmt(db,`UPDATE proposals SET batch_id=?,state='publishing' WHERE id IN (${marks(ids)}) AND EXISTS (SELECT 1 FROM publication_batches WHERE id=?)`,
   id,...ids,id)
 ]);
 if(!reserved[0].meta.changes)return deny('提案已被其他发布者处理，请刷新',409);
 let response;
 try{
  response=await gitCall(env,'/actions/workflows/'+workflow+'/dispatches',{
   method:'POST',headers:{'Content-Type':'application/json'},
   body:JSON.stringify({ref:'main',inputs:{batch:payload},return_run_details:true})
  });
 }catch{return deny('派发结果待确认，请在发布记录中同步状态',503);}
 if(!response.ok){
  // 5xx may happen after GitHub accepted the request. Keep the lease until reconciled.
  if(response.status<500)await db.batch([
   stmt(db,"UPDATE publication_batches SET state='dispatch_failed' WHERE id=?",id),
   stmt(db,"UPDATE proposals SET state='approved',batch_id=NULL WHERE batch_id=?",id)
  ]);
  return deny('GitHub 发布任务派发失败（HTTP '+response.status+'）',502);
 }
 const run=response.status===200?await response.json():{};
 await stmt(db,"UPDATE publication_batches SET state='running',run_id=? WHERE id=?",run.workflow_run_id||null,id).run();
 return reply({id,runId:run.workflow_run_id||null},202);
}

async function syncPublication(db,user,env,body){
 if(!['owner','publisher','reviewer'].includes(user.role))return deny('此账号没有核对发布状态的权限');
 if(!editorialId(body.id))throw Error('发布批次标识无效');
 const batch=await stmt(db,'SELECT * FROM publication_batches WHERE id=?',body.id).first();
 if(!batch)return deny('发布批次不存在',404);
 if(!['running','dispatching'].includes(batch.state))return reply({state:batch.state});
 let runId=batch.run_id;
 if(!runId){
  const response=await gitCall(env,'/actions/workflows/'+workflow+'/runs?event=workflow_dispatch&per_page=50');
  if(!response.ok)return deny('暂时无法核对 GitHub 发布状态',502);
  runId=(await response.json()).workflow_runs.find(row=>row.display_title==='编目发布 '+batch.id)?.id;
 }
 if(!runId)return reply({state:'dispatching'});
 const response=await gitCall(env,'/actions/runs/'+runId);
 if(!response.ok)return deny('暂时无法核对 GitHub 发布状态',502);
 const run=await response.json();
 if(run.status!=='completed'){
  await stmt(db,"UPDATE publication_batches SET state='running',run_id=? WHERE id=?",runId,batch.id).run();
  return reply({state:'running',runId});
 }
 const state=run.conclusion==='success'?'published':'failed';
 await db.batch([
  stmt(db,'UPDATE publication_batches SET state=?,run_id=? WHERE id=?',state,runId,batch.id),
  stmt(db,'UPDATE proposals SET state=? WHERE batch_id=?',state,batch.id)
 ]);
 return reply({state,runId});
}

export default {async fetch(request,env){
 const url=new URL(request.url);
 if(request.method==='GET'&&url.pathname==='/')return new Response(editorialPage,{headers:{...protectedHeaders,'Content-Type':'text/html; charset=utf-8','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"}});
 if(!url.pathname.startsWith('/api/'))return deny('找不到页面',404);
 if(request.method==='POST'&&request.headers.get('origin')!==url.origin)return deny('请从审核台发送请求');
 if(!env.DB)return deny('审核数据库未连接',503);
 try{
  const user=await member(request,env.DB);
  if(!user)return deny('请登录已获授权的账号',401);
  const db=env.DB;
  if(request.method==='GET'&&url.pathname==='/api/queue'){
   const own=user.role==='editor',condition=own?'WHERE p.author=?':'';
   const status=url.searchParams.get('state')||'pending';
   if(!['pending','approved','publishing','published','rejected','failed'].includes(status))return deny('队列状态无效',400);
   const page=Number(url.searchParams.get('page')||0);
   if(!Number.isSafeInteger(page)||page<0||page>1000)return deny('页码无效',400);
   const rows=(await stmt(db,`SELECT p.*,b.run_id FROM proposals p LEFT JOIN publication_batches b ON p.batch_id=b.id
    ${condition} ${own?'AND':'WHERE'} p.state=? ORDER BY p.submitted_at DESC LIMIT 26 OFFSET ?`,...(own?[user.id]:[]),status,page*25).all()).results;
   return reply({role:user.role,ready:!!env.EDITORIAL_GITHUB_TOKEN,more:rows.length>25,rows:rows.slice(0,25).map(row=>({
    id:row.id,own:row.author===user.id,state:row.state,submittedAt:row.submitted_at,reviewedAt:row.reviewed_at,
    note:row.review_note,batchId:row.batch_id,runId:row.run_id,proposal:JSON.parse(row.body)
   }))});
  }
  if(request.method!=='POST')return deny('找不到操作',404);
  let body;
  try{body=await readBody(request);}catch(error){return deny(error.message,400);}
  try{
   if(url.pathname==='/api/submit')return await submit(db,user,body);
   if(url.pathname==='/api/review')return await review(db,user,body);
   if(url.pathname==='/api/publish')return await publish(db,user,env,body);
   if(url.pathname==='/api/sync')return await syncPublication(db,user,env,body);
   if(url.pathname==='/api/member'&&user.role==='owner'){
    const email=String(body.email||'').trim().toLowerCase();
    if(email.length>254||!/^\S+@\S+\.\S+$/.test(email)||!appRoles.has(body.role))throw Error('邮箱或角色无效');
    await stmt(db,"INSERT INTO members(email,role) VALUES(?,?) ON CONFLICT(email) DO UPDATE SET role=excluded.role WHERE members.role!='owner'",email,body.role).run();
    return reply({ok:true});
   }
  }catch(error){return deny(error.message,400);}
  return deny('此账号没有该操作权限');
 }catch{return deny('审核服务暂时不可用，请稍后重试',503);}
}};
