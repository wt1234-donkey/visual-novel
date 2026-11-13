import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {sealCatalogueWrite,verifyCatalogueWrite} from '../src/infrastructure/filesystem/write-boundary.mjs';
export {sealCatalogueWrite,verifyCatalogueWrite};
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
 const args=process.argv.slice(2),check=args.includes('--check'),root=resolve(args.find(a=>a!=='--check')||fileURLToPath(new URL('../',import.meta.url)));
 const result=check?await verifyCatalogueWrite(root):await sealCatalogueWrite(root,JSON.parse(readFileSync(0,'utf8')));
 console.log(JSON.stringify(check?{verified:true}: {operationId:result.receipt.operationId,receipt:result.path,archive:result.archive.root.sha256}));
}
