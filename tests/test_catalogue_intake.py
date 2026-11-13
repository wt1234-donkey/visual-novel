from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from catalogue_intake import prepare,REGISTRY
from registry_store import write_json,read_json,logical_digest


class ParameterizedIntakeTests(unittest.TestCase):
    def fixture(self,root):
        row={'id':'new','indexId':'basic-new','title':'New','firstYear':1981,'gameplay':'ADV','group':'Known','source':'https://ifdb.org/viewgame?id=new','aliases':[],'identityStatus':'independent'}
        base=deepcopy(row);base.update({'id':'old','indexId':'basic-old','title':'Old','firstYear':1980,'source':'https://ifdb.org/viewgame?id=old','sourceIdentity':'ifdb:old'})
        data={'works':[base],'summary':{'candidates':1,'accepted':1,'promotedBasic':1,'addedToMainIdentityLayer':1},'batches':[]}
        write_json(root/REGISTRY,data)
        duplicate=deepcopy(row);duplicate.update({'id':'duplicate','indexId':'basic-duplicate','title':'Old','firstYear':1980,'source':'https://ifdb.org/viewgame?id=other','sourceIdentity':'ifdb:old'})
        conflict=deepcopy(row);conflict.update({'id':'conflict','indexId':'basic-conflict','title':'Old','firstYear':1982,'source':'https://ifdb.org/viewgame?id=conflict'})
        source=root/'data/intake/test.json';source.parent.mkdir(parents=True)
        source.write_text(json.dumps({'schemaVersion':1,'records':[row,duplicate,conflict]}))
        plan={'schemaVersion':1,'batchId':'test-batch','date':'2026-11-12','batchSize':500,'sourceSnapshot':'data/intake/test.json','sourceSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'expectedRegistryLogicalSha256':logical_digest(data)}
        p=root/'config/intake-plans/test.json';p.parent.mkdir(parents=True);p.write_text(json.dumps(plan))
        return plan,p

    def test_preview_is_read_only_and_apply_is_idempotent_with_quarantine(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);_,p=self.fixture(root)
            before=(root/REGISTRY).read_bytes();report=prepare(p,root)
            self.assertEqual((root/REGISTRY).read_bytes(),before)
            self.assertEqual(report['summary'],{'candidates':3,'accepted':1,'duplicates':1,'quarantined':1,'before':1,'after':2})
            prepare(p,root,True)
            after=(root/REGISTRY).read_bytes()
            receipts=list((root/'data/command-receipts').glob('*.json'))
            self.assertEqual(len(receipts),1)
            receipt=json.loads(receipts[0].read_text())
            self.assertEqual(receipt['kind'],'intake');self.assertIn('auditRoot',receipt)
            self.assertEqual(json.loads(receipt['command'])['plan']['batchId'],'test-batch')
            receipt_bytes=receipts[0].read_bytes()
            self.assertEqual(len(read_json(root/REGISTRY)['works']),2)
            self.assertTrue(prepare(p,root,True)['alreadyApplied'])
            self.assertEqual((root/REGISTRY).read_bytes(),after)
            self.assertEqual(receipts[0].read_bytes(),receipt_bytes)

    def test_changed_source_and_moved_baseline_are_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);plan,p=self.fixture(root)
            source=root/plan['sourceSnapshot'];source.write_text(source.read_text()+' ')
            with self.assertRaisesRegex(ValueError,'Source snapshot changed'):prepare(p,root,True)
            plan['sourceSha256']=hashlib.sha256(source.read_bytes()).hexdigest();plan['expectedRegistryLogicalSha256']='0'*64;p.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError,'baseline moved'):prepare(p,root,True)
            self.assertEqual(len(read_json(root/REGISTRY)['works']),1)

    def test_shared_catalogue_url_is_not_a_work_identity_and_homonyms_are_held(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);plan,p=self.fixture(root)
            source=root/plan['sourceSnapshot'];payload=json.loads(source.read_text())
            other=deepcopy(payload['records'][0]);other.update({'id':'different','indexId':'basic-different','title':'Different work'})
            homonym=deepcopy(payload['records'][0]);homonym.update({'id':'homonym','indexId':'basic-homonym','title':'Old','firstYear':1980})
            payload['records']=[payload['records'][0],other,homonym]
            source.write_text(json.dumps(payload));plan['sourceSha256']=hashlib.sha256(source.read_bytes()).hexdigest();p.write_text(json.dumps(plan))
            result=prepare(p,root)
            self.assertEqual(result['summary']['accepted'],2)
            self.assertEqual(result['summary']['quarantined'],1)
            self.assertEqual(result['summary']['duplicates'],0)


if __name__=='__main__':unittest.main()
