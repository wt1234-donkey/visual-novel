import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from historical_rules import canonical, load_historical_rules, resolve_evidence

class HistoricalRuleTests(unittest.TestCase):
    def fixture(self):
        temporary=tempfile.TemporaryDirectory();self.addCleanup(temporary.cleanup);root=Path(temporary.name)
        original=json.loads((ROOT/'config/historical-entity-rules.json').read_text());payload=original['payload']
        key=next(iter(payload['references']));ref=payload['references'][key];payload['references']={key:ref}
        payload['sequences']={name:[key] for name in payload['sequences']}
        target=root/ref['path'];target.parent.mkdir(parents=True);shutil.copyfile(ROOT/ref['path'],target)
        def save():
            original['sha256']=hashlib.sha256(canonical(payload)).hexdigest()
            path=root/'config/historical-entity-rules.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(original))
        save();return root,original,save,target
    def test_registered_facts_have_provenance_and_all_frozen_sources_verify(self):
        rules=load_historical_rules(ROOT)
        self.assertTrue(rules['baseline']['generators'])
        self.assertGreater(len(rules['references']),100)
        self.assertEqual(rules['dossiers']['stableIdentities']['kid'],'entity-name-3a59ff4a4f09')
    def test_changed_source_and_unsealed_registry_are_rejected(self):
        root,registry,save,target=self.fixture();target.write_text('{}')
        with self.assertRaisesRegex(ValueError,'source checksum'):load_historical_rules(root)
        root,registry,save,target=self.fixture();registry['payload']['constants']['DATE']='changed'
        (root/'config/historical-entity-rules.json').write_text(json.dumps(registry))
        with self.assertRaisesRegex(ValueError,'checksum'):load_historical_rules(root)
    def test_resealed_invalid_sequences_paths_and_unknown_schema_still_fail(self):
        for invalid in ['duplicate','path','duplicatePatch','patchField','schema']:
            root,registry,save,target=self.fixture();payload=registry['payload']
            if invalid=='duplicate':payload['sequences']['entityReviews']*=2
            elif invalid=='path':next(iter(payload['references'].values()))['path']='data/../outside.json'
            elif invalid=='duplicatePatch':payload['entityPatches']*=2
            elif invalid=='patchField':payload['entityPatches'][0]['set']['id']='different'
            else:payload['unexpected']=True
            save()
            with self.assertRaises(ValueError):load_historical_rules(root)
    def test_evidence_resolution_preserves_the_registered_facts(self):
        value={'dates':[['kind','1983',{'dossierSource':'studio'}]],'other':'literal'};before=copy.deepcopy(value)
        first=resolve_evidence(value,{'studio':{'source':'https://example.org/one'}})
        first['dates'].append('local')
        self.assertEqual(value,before)
        self.assertEqual(resolve_evidence(value,{'studio':{'source':'https://example.org/two'}})['dates'][0][-1],'https://example.org/two')
