import {mkdirSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {loadEffectiveInputsSync,sourceLeaseSync} from '../src/infrastructure/filesystem/effective-catalogue.mjs';
import {blobDigest} from '../src/infrastructure/storage/digests.mjs';

export async function buildEffectiveRelease(root,output,revision){
 const {coverage,...inputs}=loadEffectiveInputsSync(root),sourceLease=sourceLeaseSync(root);
 const path='catalogue-web/'+revision+'/inputs.json',text=JSON.stringify({schemaVersion:1,...inputs,sourceLease})+'\n';
 mkdirSync(join(output,'data','catalogue-web',revision),{recursive:true});
 writeFileSync(join(output,'data',path),text);
 writeFileSync(join(output,'data/catalogue-release.json'),JSON.stringify({schemaVersion:1,revision,inputs:{path,sha:await blobDigest(text)},sourceLease})+'\n');
 return {sourceLease};
}
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)await buildEffectiveRelease(...process.argv.slice(2));
