import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
import {createServer} from 'node:http';
import {readFile} from 'node:fs/promises';
import {readFileSync,readdirSync} from 'node:fs';
import {resolve,extname} from 'node:path';
import {loadEffectiveCatalogueSync} from '../../src/infrastructure/filesystem/effective-catalogue.mjs';
import {mergeFormalDatasets,displayTitle} from '../../src/domain/catalogue/effective.mjs';
import {decodePublishedText} from '../../src/infrastructure/storage/wire-format.mjs';
const {chromium}=createRequire(import.meta.url)(process.env.PLAYWRIGHT_MODULE||'playwright');
const site=process.env.ATLAS_SITE_DIRECTORY&&resolve(process.env.ATLAS_SITE_DIRECTORY);
test('published organization and classification pages initialize against their actual frozen release', {timeout:60000},async()=>{
 assert.ok(site,'Build the static artifact and set ATLAS_SITE_DIRECTORY before browser regressions');
 const release=JSON.parse(readFileSync(resolve(site,'data/catalogue-release.json'))),expected=loadEffectiveCatalogueSync(resolve(import.meta.dirname,'../..'));
 const directory=JSON.parse(await decodePublishedText(readFileSync(resolve(site,'data',release.catalogues.formal.path),'utf8')));
 const expectedFormal=new Map(mergeFormalDatasets(expected).works.map(w=>[w.id,w]));assert.equal(directory.data.works.length,expectedFormal.size);for(const row of directory.data.works){const w=expectedFormal.get(row.id);assert.ok(w,row.id);assert.equal(displayTitle(row),displayTitle(w),row.id+' formal directory title');assert.equal(row.firstYear,w.firstYear,row.id+' formal directory year');}
 assert.equal(directory.currentStateVersion,1);assert.equal(directory.raw.history.journal,undefined);
 assert.ok(Object.values(directory.raw.history.records).every(row=>row.recent.length===0),'directory contains current values, not undo snapshots or full event journals');
 // This checks entry declarations, not merely the raw download returning 200.
 for(const file of readdirSync(site).filter(n=>n.endsWith('.html'))){const body=readFileSync(resolve(site,file),'utf8').match(/<body\b[^>]*>/)?.[0],source=body?.match(/data-source="([^"]+)"/)?.[1];if(source?.startsWith('data/'))assert.ok(release.resources[source.split('?')[0]],file+' runtime resource is frozen');}
 const server=createServer(async(req,res)=>{try{const path=resolve(site,'.'+new URL(req.url,'http://localhost').pathname);if(!path.startsWith(site+'/'))throw Error('invalid path');res.setHeader('content-type',({'.mjs':'text/javascript','.css':'text/css','.html':'text/html','.json':'application/json'})[extname(path)]||'application/octet-stream');res.end(await readFile(path));}catch{res.writeHead(404);res.end();}});
 await new Promise(r=>server.listen(0,'127.0.0.1',r));let browser;
 try{browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:390,height:844}}),errors=[],resources=[];page.on('pageerror',e=>errors.push(e.message));page.on('request',r=>resources.push(r.url()));
  const origin='http://127.0.0.1:'+server.address().port;await page.goto(origin+'/organizations.html');await page.locator('#family-nav .family-button').first().waitFor();await page.locator('#unfinished-count').filter({hasText:/匹配/}).waitFor();assert.ok(resources.some(u=>u.includes('/catalogue-web/'+release.revision+'/resources/organizations.json')));
  await page.locator('#family-nav .family-button').nth(1).click();const selected=new URL(page.url()).searchParams.get('family');assert.ok(selected);await page.reload();await page.locator('#family-nav .family-button[aria-pressed=true]').waitFor();assert.equal(new URL(page.url()).searchParams.get('family'),selected);
  await page.goto(origin+'/classification.html');const works=new Map(expected.coverage.companies.flatMap(c=>[...(c.relatedGames||[]),...(c.dossierOnlyWorks||[])]) .map(w=>[w.id,w]));
  for(const id of ['ai-secret-mission','ai-strange-odyssey','ai-pyramid-doom']){const row=page.locator('tr').filter({has:page.locator('a[href$="#'+id+'"]')}),work=works.get(id);assert.equal((await row.locator('small').textContent()).split(' · ')[0],String(work.firstYear));}
  assert.deepEqual(errors,[]);
 }finally{await browser?.close();await new Promise(r=>server.close(r));}
});
