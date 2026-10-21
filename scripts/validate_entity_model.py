"""Validate the additive migration, scoped participation and preserved historical content."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from source_urls import source_url_valid
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text())

def validate():
 d=read('data/games.json');cov=read('data/company-coverage.json');m=read('data/entities.json');c=read('data/credits.json');p=read('data/work-classification.json');base=read('data/entity-migration-baseline.json');review=read('data/entity-migration-review.json')
 for field in ['works','contentVersions','platformReleases']:
  current={x['id']:hashlib.sha256(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest() for x in d[field]}
  assert all(current.get(wid)==value for wid,value in base['objects'][field].items()),f'既有记录变化需独立订正审核：{field}'
 allworks={w['id']:w for w in d['works']};releases={r['id']:r for r in d['platformReleases']};contents={v['id']:v for v in d['contentVersions']};expected_members=set()
 for company in cov['companies']:
  expected_members.update((company['id'],wid) for wid in company['workIds'])
  for field in ['relatedGames','dossierOnlyWorks']:
   for w in company.get(field,[]):
    expected_members.add((company['id'],w['id']));allworks[w['id']]=w
    for r in w.get('platformReleases',[]):releases[r['id']]=r
    for cv in w.get('contentVersions',[]):contents[cv['id']]=cv
 entities={e['id']:e for e in m['entities']};assert len(entities)==len(m['entities'])
 for entity in entities.values():
  assert entity['name'] and entity['type'] in m['typeLabels'] and entity['type']!='history'
  assert entity['verification'] in {'existingDossier','sourceReviewed','unresolved'}
  assert entity['sources'] and all(source_url_valid(s) for s in entity['sources'])
 for relation in m['relations']:
  assert relation['from'] in entities and relation['to'] in entities and relation['from']!=relation['to']
  assert relation['period']['precision'] in {'unknown','year','month','day'} and relation['note'] and source_url_valid(relation['source'])
 assert {x['id'] for x in m['dossiers']}=={x['id'] for x in cov['companies']}
 for dossier in m['dossiers']:
  assert dossier['dossierType'] in m['typeLabels'] and set(dossier['entityIds'])<=entities.keys()
 assert len(c['credits'])==len({x['id'] for x in c['credits']})
 assert len(c['credits'])==len({(x['entityId'],x['targetType'],x['targetId'],x['role']) for x in c['credits']})
 maps={'work':allworks,'release':releases,'content':contents}
 for cr in c['credits']:
  assert cr['entityId'] in entities and cr['role'] in m['roleLabels'] and source_url_valid(cr['source'])
  target=maps[cr['targetType']][cr['targetId']]
  assert cr['workId']==(target['id'] if cr['targetType']=='work' else target['workId'])
  if cr['role'] in {'publisher','publishingBrand','portDeveloper'}:assert cr['targetType']=='release'
  if cr['status']=='existingCredit' and cr['targetType']=='release':assert cr['rawCredit']==target['publisher']
 assert {(x['dossierId'],x['workId']) for x in c['dossierMemberships']}==expected_members
 assert len(c['dossierMemberships'])==len(expected_members)
 placements={x['workId']:x for x in p['placements']};assert set(placements)==set(allworks)
 assert {wid for wid,x in placements.items() if x['placement']=='main'}=={w['id'] for w in d['works']}
 assert all(x['decision']=='retainExistingPlacement' and x['narrativeAssessment']=='notReassessed' for x in placements.values())
 assert {x['workId'] for x in p['reviewQueue']}=={wid for wid,x in placements.items() if x['placement']!='main'}
 assert not review['identityConflicts'],'作品身份冲突不可由迁移自动合并'
 raw_credits=[x for x in c['credits'] if x['targetType']=='release' and x['rawCredit']=='Nitro+CHiRAL']
 assert raw_credits and {x['entityId'] for x in raw_credits}=={'entity-nitrochiral'}
 assert len(d['works'])>=base['counts']['works'] and len(d['platformReleases'])>=base['counts']['platformReleases']
 return {'entities':len(entities),'credits':len(c['credits']),'dossiers':len(m['dossiers']),'placements':len(placements),'unresolvedIdentities':len(review['pendingIdentities']),'pendingMemberships':review['pendingMembershipCount']}

if __name__=='__main__':print('实体与关系校验通过：',validate())
