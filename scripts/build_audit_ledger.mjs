import {fileURLToPath,pathToFileURL} from 'node:url';
import {buildAuditLedger} from '../src/infrastructure/filesystem/audit-ledger.mjs';
const root=fileURLToPath(new URL('../',import.meta.url));
if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href)console.log(JSON.stringify(await buildAuditLedger(root,{check:process.argv.includes('--check')})));
