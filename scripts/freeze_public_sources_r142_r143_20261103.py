#!/usr/bin/env python3
"""Freeze collected metadata and resumable source boundaries, without credentials."""
import base64
import gzip
import hashlib
import json
from pathlib import Path
import import_basic_r142_r143_20261103 as intake

ROOT=Path(__file__).resolve().parents[1]
FILES={'bangumi':'data/bangumi-source-r142-r143-20261103.json',
       'wikidata':'data/wikidata-source-r142-r143-20261103.json',
       'bangumiRelations':'data/bangumi-relations-r142-r143-20261103.json'}

def main():
    entries={}
    for key,name in FILES.items():
        data=(ROOT/name).read_bytes()
        target=f'data/public-source-r142-r143-{key}.b64'
        content=base64.b64encode(gzip.compress(data,mtime=0))+b'\n'
        (ROOT/target).write_bytes(content)
        entries[key]={'file':target,'encoding':'base64+gzip+json',
                      'sha256':hashlib.sha256(content).hexdigest(),
                      'uncompressedSha256':hashlib.sha256(data).hexdigest()}
    bgm=json.loads((ROOT/FILES['bangumi']).read_bytes())
    wd=json.loads((ROOT/FILES['wikidata']).read_bytes())
    manifest={'schema':1,'date':'2026-11-03','baseCommit':intake.BASE,'snapshots':entries,
      'sourceAvailability':{
        'igdb':{'status':'blocked-no-configured-api-credentials','observedHttpStatus':401,'apiRecordsCollected':0,'nextCursor':None},
        'mobygames':{'status':'blocked-no-configured-api-credentials','observedHttpStatus':401,'apiRecordsCollected':0,'nextCursor':None},
        'bangumi':{'status':'public-game-metadata-captured','rawRecords':len(bgm['records']),'startOffset':0,'limit':50,
                   'scope':'Public API results only; not a complete site mirror.'},
        'wikidata':{'status':'historical-adventure-discovery-captured','rawRows':len(wd['records']),'distinctItems':len(wd['entityIds'])}},
      'nextCursors':{'bangumi':bgm['nextCursor'],
        'wikidata':{'query':wd['query'],'excludeAlreadyCapturedEntityIds':wd['entityIds'],
                    'continuationPolicy':'Exclude captured IDs in the next query, then freeze the response; there is no fabricated global offset.'},
        'igdb':None,'mobygames':None,
        'historicalPc98':{'pendingAudit':'data/pc98-catalogue-audit-r142-r143-20261103.json','remainingUnresolvedRawRecords':543}},
      'attribution':[
        {'source':'Bangumi contributors','url':'https://bgm.tv/','apiDocumentation':'https://bangumi.github.io/api/',
         'scope':'Titles, explicit aliases, dates, genre/developer fields, game relations, and short evidence excerpts. User reviews/statistics/images omitted.'},
        {'source':'Wikidata contributors','url':'https://www.wikidata.org/','scope':'Labels, aliases, publication dates and external identifiers; discovery evidence, not independent year certification.'},
        {'source':'ゲーム保存協会 / Project EGG','url':'https://www.gamepres.org/pc88/library/1988/arcus.htm','scope':'Explicit historical source review; no wholesale historical catalogue mirror.'}]}
    intake.e.save(intake.MANIFEST,manifest)
    print('FROZEN',len(bgm['records']),len(wd['entityIds']))

if __name__=='__main__':main()
