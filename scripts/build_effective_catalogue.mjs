import {mkdirSync,writeFileSync,existsSync,readFileSync,copyFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {loadEffectiveInputsSync,sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';
import {buildOnDemandCatalogues} from './build_on_demand_catalogues.mjs';
import {saveMode as policyMode} from '../src/application/commands/policy.mjs';
import {publishAuditLedger} from '../src/infrastructure/filesystem/audit-ledger.mjs';

export async function buildEffectiveRelease(root,output,revision){
 const {coverage,...inputs}=loadEffectiveInputsSync(root),sourceLease=sourceLeaseSync(root);
 const path='catalogue-web/'+revision+'/inputs.json',text=JSON.stringify({schemaVersion:1,...inputs,sourceLease})+'\n';
 mkdirSync(join(output,'data','catalogue-web',revision),{recursive:true});
 writeFileSync(join(output,'data',path),text);
 const resources={};
 const names=['taxonomy.json','date-contract.json','entity-catalogue.json','discovery-editorial.json','creator-credits.json','work-notes.json','company-coverage.json','narrative-editorial-baseline-20261029.json','basic-manufacturer-regions.json','curated-narrative-works.json','relationships-preview.json','games.json','non-rpg-creator-supplement-20261030.json','work-edit-history.json','basic-catalogue-edits.json','source-identity-decisions.json','field-evidence.json','main-adv-rpg-works-20261031.json'];
 const header=inputs.formalLinks&&existsSync(join(root,'data/main-adv-rpg-works-20261031.json'))?JSON.parse(readFileSync(join(root,'data/main-adv-rpg-works-20261031.json'),'utf8')):{};
 if(existsSync(join(root,'data/audit-ledger/manifest.json')))names.push('audit-ledger/manifest.json');
 names.push(...(header.storage?.shards||[]).map(ref=>ref.path));
 names.push(...[inputs.basicStore?.journal?.baseline,...(inputs.basicStore?.journal?.shards||[])].filter(Boolean).map(ref=>ref.path.replace(/^data\//,'')));
 const publishedAudit=await publishAuditLedger(root,output);
 for(const name of names){
  const source=join(publishedAudit&&name==='audit-ledger/manifest.json'?output:root,'data',name);if(!existsSync(source))continue;
  const target='catalogue-web/'+revision+'/resources/'+name;
  mkdirSync(join(output,'data',target,'..'),{recursive:true});copyFileSync(source,join(output,'data',target));
  resources['data/'+name]={path:target,sha:await blobDigest(readFileSync(source,'utf8'))};
 }
 const basicPath=join(output,'data/basic-web/manifest.json');let basic;
 if(existsSync(basicPath)){
  const content=readFileSync(basicPath,'utf8');basic={path:'catalogue-web/'+revision+'/basic-manifest.json',sha:await blobDigest(content)};
  writeFileSync(join(output,'data',basic.path),content);
 }
 const catalogues=await buildOnDemandCatalogues(root,output,revision);
 const policy=join(root,'data/trusted-save-policy.json'),saveMode=policyMode(existsSync(policy)?JSON.parse(readFileSync(policy,'utf8')):undefined);
 writeFileSync(join(output,'data/catalogue-release.json'),JSON.stringify({schemaVersion:1,revision,saveMode,inputs:{path,sha:await blobDigest(text)},resources,basic,catalogues,sourceLease})+'\n');
 return {sourceLease};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)await buildEffectiveRelease(...process.argv.slice(2));
