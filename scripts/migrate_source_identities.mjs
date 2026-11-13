import {readFileSync,writeFileSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {resolve,join} from 'node:path';
import {journalKey} from '../src/domain/catalogue/journal.mjs';
import {buildCatalogueSnapshot} from '../src/application/catalogue/snapshot.mjs';
import {loadCatalogueSnapshot} from '../src/infrastructure/filesystem/catalogue-snapshot.mjs';
import {projectRegistry} from '../src/domain/catalogue/model.mjs';
import {identityFormalLinks} from '../src/domain/catalogue/source-identities.mjs';
const hashRows=rows=>{const h=createHash('sha256');for(const row of rows)h.update(journalKey(row)+'\n');return h.digest('hex');};
const projected=s=>({sourceRows:hashRows(s.sourceRows),entries:hashRows(s.entries),home:hashRows(s.home.rows),homeExcluded:s.home.excluded,formalIds:hashRows([...s.formalById.keys()])});
export function checkSourceIdentities(root){
 const {inputs,snapshot}=loadCatalogueSnapshot(root),model=snapshot.sourceIdentity;
 const baseline=JSON.parse(readFileSync(join(root,'config/source-identity-baseline.json'),'utf8'));
 if(inputs.registry.works.length<baseline.sourceRecordCount||hashRows(inputs.registry.works.slice(0,baseline.sourceRecordCount))!==baseline.sourceRecordsSha256)throw Error('原始来源、ID、顺序或证据发生变化');
 const legacy=buildCatalogueSnapshot({...inputs,identityLinks:{}});
 const migrated=buildCatalogueSnapshot({...inputs,identityLinks:inputs.identityStore.revision===0?identityFormalLinks(model):{}});
 if(inputs.identityStore.revision===0&&!([...inputs.main.works,...inputs.supplement.works].some(w=>w.basicRegistryId))&&journalKey(projected(legacy))!==journalKey(projected(migrated)))throw Error('格式迁移改变可见作品或有效投影');
 const bulk=projectRegistry(inputs.registry,inputs.store).works.length;
 model.stats.bulkVisibleGroups=bulk;model.stats.legacySourceRowCount=legacy.sourceRows.length;
 if(inputs.identityStore.revision===0&&inputs.store.revision===baseline.basicRevision&&inputs.registry.works.length===baseline.sourceRecordCount&&model.stats.formalProfiles===baseline.visible.formalProfiles&&!([...inputs.main.works,...inputs.supplement.works].some(w=>w.basicRegistryId))){
  for(const [key,n] of Object.entries(baseline.visible))if(model.stats[key]!==n)throw Error('迁移可见数量变化：'+key);
 }
 return {sourceRecords:model.sources.size,stats:model.stats,sourceRecordsSha256:baseline.sourceRecordsSha256,identityRevision:inputs.identityStore.revision,events:inputs.identityStore.events.length};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 const root=fileURLToPath(new URL('../',import.meta.url));
 if(process.argv.includes('--apply')){
  const file=join(root,'config/source-identity-baseline.json');if(existsSync(file))throw Error('身份迁移检查点已存在；禁止重置');
  const {inputs,snapshot}=loadCatalogueSnapshot(root);
  writeFileSync(file,JSON.stringify({schemaVersion:1,at:new Date().toISOString(),sourceCommit:execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim(),
   sourceRecordCount:inputs.registry.works.length,sourceRecordsSha256:hashRows(inputs.registry.works),sourceLogicalSha256:JSON.parse(readFileSync(join(root,'data/main-adv-rpg-works-20261031.json'),'utf8')).storage?.logicalSha256,
   basicRevision:inputs.store.revision,visible:{basicVisibleGroups:snapshot.entries.length,discoveryBasicGroups:snapshot.home.rows.length,bulkVisibleGroups:projectRegistry(inputs.registry,inputs.store).works.length,formalProfiles:snapshot.formalById.size}},null,2)+'\n');
 }
 console.log(JSON.stringify(checkSourceIdentities(root)));
}
