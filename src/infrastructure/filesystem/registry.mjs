import {readFileSync} from 'node:fs';
import {dirname,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {journalKey} from '../../domain/catalogue/journal.mjs';

export const REGISTRY_PATH='data/main-adv-rpg-works-20261031.json';
export function readJsonFileSync(input){
 const path=input instanceof URL?fileURLToPath(input):input;
 const value=JSON.parse(readFileSync(path,'utf8')),storage=value?.storage;
 if(storage?.format!=='registry-shards-v1')return value;
 if(storage.schemaVersion!==1)throw Error('基础源库格式无效');
 const works=[],ids=new Set();
 for(const [i,ref] of storage.shards.entries()){
  if(ref.path!=='basic-registry/works-'+String(i).padStart(5,'0')+'-'+ref.sha256.slice(0,12)+'.json')throw Error('基础源库分片路径无效');
  const raw=readFileSync(join(dirname(path),ref.path));
  if(raw.length!==ref.bytes||createHash('sha256').update(raw).digest('hex')!==ref.sha256||createHash('sha1').update('blob '+raw.length+'\0').update(raw).digest('hex')!==ref.gitSha)throw Error('基础源库分片摘要不一致');
  const rows=JSON.parse(raw);if(!Array.isArray(rows)||rows.length!==ref.count)throw Error('基础源库分片计数不一致');
  for(const row of rows){if(ids.has(row.id))throw Error('基础源库身份重复');ids.add(row.id);works.push(row);}
 }
 const {storage:ignored,...result}=value;result.works=works;
 if(works.length!==storage.count||works.length!==result.summary.accepted)throw Error('基础源库总数不一致');
 if(createHash('sha256').update(journalKey(result)+'\n').digest('hex')!==storage.logicalSha256)throw Error('基础源库逻辑摘要不一致');
 return result;
}
