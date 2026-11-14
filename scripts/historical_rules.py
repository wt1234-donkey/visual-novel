"""Strict, checksummed historical facts shared by the active catalogue generators."""
import argparse
import hashlib
import json
from pathlib import Path
import re

REGISTRY='config/historical-entity-rules.json'
PAYLOAD_KEYS={'namespace','baseline','constants','references','sequences','dossiers','publisherAliases','supplementalEntities','supplementalRelations','subbrandRelations','operatedBy','entityDates','creditRules'}

def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def load_historical_rules(root):
    root=Path(root)
    registry=json.loads((root/REGISTRY).read_text())
    if set(registry)!={'schemaVersion','sha256','payload'} or registry['schemaVersion']!=1:
        raise ValueError('Historical rule registry schema is invalid')
    payload=registry['payload']
    if set(payload)!=PAYLOAD_KEYS or payload['namespace']!='narrative-entity-history' or hashlib.sha256(canonical(payload)).hexdigest()!=registry['sha256']:
        raise ValueError('Historical rule registry checksum or namespace differs')
    baseline=payload['baseline']
    if set(baseline)!={'commit','generators'} or not re.fullmatch('[0-9a-f]{40}',baseline['commit']) or any(not re.fullmatch('[0-9a-f]{64}',sha) for sha in baseline['generators'].values()):
        raise ValueError('Historical rule provenance is missing')
    constants=payload['constants']
    if set(constants)!={'BASE','DATE','TYPE_LABELS','ROLE_LABELS','BRANDS','HISTORIES','NAMES','EXTRAS','SUBBRANDS'}:
        raise ValueError('Historical rule constants differ from schema')
    for name,ref in payload['references'].items():
        if not name or set(ref)!={'path','sha256'} or not re.fullmatch(r'data/[A-Za-z0-9_-]+\.json',ref['path']) or not re.fullmatch('[0-9a-f]{64}',ref['sha256']):
            raise ValueError('Invalid historical source reference: '+name)
        path=root/ref['path']
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=ref['sha256']:
            raise ValueError('Historical source checksum differs: '+ref['path'])
    if set(payload['sequences'])!={'entityReviews','organizationReviews','organizationMilestones'}:
        raise ValueError('Historical sequence schema differs')
    for sequence in payload['sequences'].values():
        if not isinstance(sequence,list) or len(sequence)!=len(set(sequence)) or any(key not in payload['references'] for key in sequence):
            raise ValueError('Historical sequence is duplicated or references unknown evidence')
    if set(payload['dossiers'])!={'stableIdentities','entityKeys','types','names'}:
        raise ValueError('Dossier rule schema differs')
    for ref in payload['operatedBy']:
        if set(ref)!={'args','options'} or not 4<=len(ref['args'])<=6 or set(ref['options'])-{'status','start'}:
            raise ValueError('Invalid historical relationship rule')
    for rules in payload['creditRules'].values():
        if not isinstance(rules,list):raise ValueError('Historical credit rules must be ordered')
        for rule in rules:
            required={'entityId','scope','targets','role','source','note','status'}
            if not required<=set(rule) or set(rule)-required-{'raw','requiresDossier','requiresOriginalRelease','review'} or rule['scope'] not in {'work','release','content'} or rule['role'] not in constants['ROLE_LABELS'] or rule['status'] not in {'existingDossier','existingCredit','sourceReviewed'}:
                raise ValueError('Invalid scoped historical credit rule')
            target=rule['targets'];kind=target.get('kind')
            allowed={'ids':{'kind','ids'},'dossierWorks':{'kind','dossier','exclude'},'records':{'kind','workIds','firstYear','publisherEntity'}}
            if kind not in allowed or set(target)-allowed[kind] or kind=='dossierWorks' and rule['scope']!='work':
                raise ValueError('Invalid historical credit selector')
            if kind in {'ids','records'}:
                ids=target.get('ids' if kind=='ids' else 'workIds')
                if not isinstance(ids,list) or not ids or len(ids)!=len(set(ids)) or any(not isinstance(i,str) or not i for i in ids):
                    raise ValueError('Historical credit selector needs explicit unique IDs')
            source=rule['source']
            if isinstance(source,str):
                if not re.match('https?://',source):raise ValueError('Historical credit needs a source URL')
            elif not isinstance(source,dict) or len(source)!=1 or not set(source)<={'dossierSource','workSource','targetSources'}:
                raise ValueError('Invalid historical credit evidence selector')
    return payload

def reference_path(rules,key):
    return rules['references'][key]['path']

def resolve_evidence(value,companies):
    if isinstance(value,dict):
        if set(value)=={'dossierSource'}:
            return companies[value['dossierSource']]['source']
        return {key:resolve_evidence(item,companies) for key,item in value.items()}
    if isinstance(value,list):
        return [resolve_evidence(item,companies) for item in value]
    return value

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');parser.parse_args()
    rules=load_historical_rules(Path(__file__).resolve().parents[1])
    print(json.dumps({'references':len(rules['references']),'sequences':{key:len(value) for key,value in rules['sequences'].items()}},ensure_ascii=False))
