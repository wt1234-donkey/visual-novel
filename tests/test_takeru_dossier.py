"""Current TAKERU additions are exact and do not inherit channel game creation."""
import json
import subprocess
import unittest
from pathlib import Path
from historical_paths import shared_paths
ROOT=Path(__file__).resolve().parents[1]
BASE='a1c4959cd7a2ef52460eebfa16388fea815c4642'
T='entity-name-08cbddd5e450'
def read(path):return json.loads(subprocess.check_output(['git','show',f'329447b4c8ee6c7656301a4a0ab5f1fe9edd51cf:{path}'],cwd=ROOT))
def old(path):return json.loads(subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=ROOT))
class TakeruDossierTests(unittest.TestCase):
    def test_only_one_new_work_content_and_first_release_and_no_old_object_changes(self):
        before,after=old('data/games.json'),read('data/games.json')
        for key,newid in [('works','g1278'),('contentVersions','g1278-c-original'),('platformReleases','g1278-v1')]:
            b={x['id']:x for x in before[key]};a={x['id']:x for x in after[key]}
            self.assertEqual(set(a)-set(b),{newid});self.assertEqual({k:a[k] for k in b},b)
        self.assertEqual(after['meta'],before['meta'])
        w=next(w for w in after['works'] if w['id']=='g1278')
        self.assertEqual(w['interactionModes'],['菜单指令']);self.assertIn('8BITS',w['interactionNote'])
        r=next(r for r in after['platformReleases'] if r['id']=='g812-v2')
        self.assertEqual((r['contentRelation'],r['contentVersionId']),('unverified',None))
    def test_existing_dossiers_and_frozen_audits_remain_identical(self):
        prior,current=old('data/company-coverage.json'),read('data/company-coverage.json')
        current['companies']=[c for c in current['companies'] if c['id']!='takeru'];self.assertEqual(current,prior)
        paths=['data/taxonomy.json','data/entity-migration-baseline.json','data/content-migration-baseline.json','data/gameplay-catalogues.json']
        paths += shared_paths(ROOT, BASE, '329447b4c8ee6c7656301a4a0ab5f1fe9edd51cf', ['organization-context*.json','organization-verification*.json'])
        for p in paths:self.assertEqual(read(p),old(p),p)
    def test_service_identity_is_reused_and_only_initial_operator_added(self):
        prior,current=old('data/entities.json'),read('data/entities.json')
        b={e['id']:e for e in prior['entities']};a={e['id']:e for e in current['entities']}
        self.assertEqual(set(a)-set(b),{'entity-brother'})
        self.assertEqual({k for k in b if a[k]!=b[k]},{T})
        self.assertEqual((a[T]['type'],a[T]['verification']),('brand','sourceReviewed'))
        self.assertEqual([(d['kind'],d['value']) for d in a[T]['dates']],[('serviceStarted','1986'),('serviceEnded','1997')])
        self.assertEqual(current['relations'][:-1],prior['relations'])
        edge=current['relations'][-1];self.assertEqual((edge['from'],edge['to'],edge['period']['from']),(T,'entity-brother',1986));self.assertIsNone(edge['period']['to'])
        self.assertEqual(next(d for d in current['dossiers'] if d['id']=='takeru')['entityIds'],[T])
    def test_credits_are_release_only_and_input_work_has_no_fabricated_release(self):
        b,a=old('data/credits.json'),read('data/credits.json')
        bc={c['id']:c for c in b['credits']};ac={c['id']:c for c in a['credits']}
        self.assertEqual({k:ac[k] for k in bc},bc)
        added=[ac[k] for k in set(ac)-set(bc)];self.assertEqual(len(added),1)
        self.assertEqual((added[0]['entityId'],added[0]['targetId'],added[0]['role']),(T,'g1278-v1','publisher'))
        self.assertEqual([m for m in a['dossierMemberships'] if m['dossierId']!='takeru'],b['dossierMemberships'])
        self.assertFalse(any(c['entityId']=='entity-brother' for c in a['credits']))
        self.assertFalse(any(c['workId']=='takeru-madeline' for c in a['credits']))
        dossier=next(c for c in read('data/company-coverage.json')['companies'] if c['id']=='takeru')
        self.assertEqual(dossier['workIds'],['g743','g812','g1278']);self.assertEqual(dossier['dossierOnlyWorks'][0]['interactionModes'],['文字输入'])
        page=(ROOT/'takeru.html').read_text();self.assertEqual(page.count('<article class="card"'),4);self.assertIn('销售渠道与服务沿革',page);self.assertIn('未完成：1994年业务移交',page)
    def test_timeline_and_unfinished_are_current_but_old_ledger_is_preserved(self):
        b,a=old('data/organizations.json'),read('data/organizations.json')
        self.assertEqual(a['verificationLedger'],b['verificationLedger'])
        self.assertEqual(a['organizationEvents'][:-3],b['organizationEvents'])
        self.assertEqual([e['year'] for e in a['organizationEvents'][-3:]],[1986,1992,1997])
        self.assertTrue(all(e['sources'] and not e['recordIds'] for e in a['organizationEvents'][-3:]))
        self.assertEqual(a['unfinished']['counts'],{'identity':32,'duty':590,'creation':800,'evidence':481,'chronology':43,'relation':1})
        node=next(n for n in a['nodes'] if n['id']==T);self.assertEqual(node['productionCount'],0)
        self.assertIn('data-company="takeru" data-first-year="1988"',(ROOT/'index.html').read_text())
