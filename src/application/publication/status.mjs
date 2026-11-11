export const PUBLICATION_LABELS={saved:'已保存',waiting:'等待发布',publishing:'发布中',published:'已生效',failed:'发布失败',unknown:'暂无法确认',rollback:'已保存，线上已回退'};
export function operationReceipt({operationId,kind,revision,commit,workId=null,at=new Date().toISOString()}){
 if(typeof operationId!=='string'||!operationId||operationId.length>500||!['basic','formal'].includes(kind)||!Number.isSafeInteger(revision)||revision<0||!Number.isFinite(Date.parse(at))||commit&&!/^[a-f0-9]{40}$/.test(commit))throw Error('保存回执格式无效');
 return {schemaVersion:1,operationId,kind,revision,commit:commit||null,workId,at};
}
export function publicationState(receipt,deployment,runs=[],{available=true}={}){
 if(deployment&&(deployment.revision===receipt.commit||deployment.ancestors?.includes(receipt.commit)||deployment.operationIds?.[receipt.kind]?.includes(receipt.operationId)))return {state:'published',revision:deployment.revision};
 if(deployment?.rollback&&Date.parse(receipt.at)<=Date.parse(deployment.rollback.at))return {state:'rollback',revision:deployment.revision,url:deployment.rollback.url};
 if(!available)return {state:'unknown'};
 const relevant=runs.filter(run=>run.containsOperation).sort((a,b)=>Date.parse(b.created_at)-Date.parse(a.created_at));
 const run=relevant[0];
 if(!run)return {state:'waiting'};
 if(['failure','timed_out','action_required','startup_failure'].includes(run.conclusion))return {state:'failed',url:run.html_url};
 if(run.status!=='completed')return {state:['in_progress','waiting'].includes(run.status)?'publishing':'waiting',url:run.html_url};
 return {state:'waiting',url:run.html_url};
}
