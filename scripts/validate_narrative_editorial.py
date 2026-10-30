"""Validate work-level narrative annotations and their field-level editorial evidence."""
import hashlib
import json
from collections import Counter
from pathlib import Path
from source_urls import source_url_valid

ROOT=Path(__file__).resolve().parents[1]
FIELDS=('position','style','theme','structure')
BASELINE='data/narrative-editorial-baseline-20261029.json'

def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))

def has_value(record,field):
    value=record.get(field)
    return isinstance(value,str) and bool(value.strip()) if field=='position' else isinstance(value,list) and bool(value) and all(isinstance(x,str) and x.strip() for x in value)

def validate(data=None, catalogue=None):
    data=data or read('data/discovery-editorial.json')
    catalogue=catalogue or read('data/games.json')
    baseline=read(BASELINE)
    workmap={w['id']:w for w in catalogue['works']}
    counts=Counter({"complete":0,"partial":0,"missing":0})
    for wid,old in baseline['works'].items():
        assert data['works'].get(wid)==old, f'{wid}: historical editorial entry changed without separate review'
    for wid,record in data['works'].items():
        assert wid in workmap, f'{wid}: unknown work identity'
        assert isinstance(record.get('basis'),str) and len(record['basis'])>=15, f'{wid}: missing editorial rationale'
        assert record.get('sources') and all(source_url_valid(s) for s in record['sources']), f'{wid}: invalid source'
        present=[field for field in FIELDS if has_value(record,field)]
        state='complete' if len(present)==4 else 'partial' if present else 'missing'
        counts[state]+=1
        assert record['status'] in {'editorialObservation','partial'}, f'{wid}: invalid review status'
        if wid in baseline['works']:
            continue
        assert record.get('reviewedAt') in ('2026-10-30','2026-10-31'), f'{wid}: missing review date'
        assert record['status']==('editorialObservation' if state=='complete' else 'partial'), f'{wid}: false completion status'
        for field in present:
            labels=[record[field]] if field=='position' else record[field]
            assert len(labels)==len(set(labels)), f'{wid}/{field}: duplicate labels'
            assert not any(label.strip() in ('待编目','待核实','未知','资料不足') for label in labels), f'{wid}/{field}: placeholder is not completion'
            evidence=record.get('fieldEvidence',{}).get(field)
            assert isinstance(evidence,dict), f'{wid}/{field}: missing field evidence'
            assert isinstance(evidence.get('basis'),str) and len(evidence['basis'].strip())>=8, f'{wid}/{field}: weak basis'
            assert evidence.get('sources') and all(source_url_valid(s) for s in evidence['sources']), f'{wid}/{field}: invalid evidence source'
            assert isinstance(evidence.get('evidenceText'),str) and len(evidence['evidenceText'].strip())>=5, f'{wid}/{field}: empty evidence excerpt'
            assert evidence.get('sourceFields'), f'{wid}/{field}: source scope missing'
        if state!='complete':
            assert record.get('openQuestions'), f'{wid}: missing specific open question'
    counts['missing']+=len(workmap.keys()-data['works'].keys())
    assert not set(data.get('featuredWorkIds',[]))-workmap.keys(), 'Unknown featured work'
    report_path=ROOT/'data/narrative-cataloguing-20261030.json'
    if report_path.exists():
        report=read('data/narrative-cataloguing-20261030.json')
        old_ids=set(baseline['works'])
        target=set(report['targetWorkIds'])
        assert len(target)==1331 and not target.intersection(old_ids), 'Incorrect frozen review scope'
        assert target<=workmap.keys() and target<=data['works'].keys(), 'Reviewed work missing from catalogue'
        assert set(report['reviewedWorkIds'])==target, 'The requested 1331 work review scope is incomplete'
        assert len(report['reviewedWorkIds'])==len(target), 'Duplicate review identity'
        snapshot_counts=Counter({'complete':0,'partial':0,'missing':0})
        for wid in report['countedWorkIds']:
            present=sum(has_value(data['works'].get(wid,{}),f) for f in FIELDS)
            snapshot_counts['complete' if present==4 else 'partial' if present else 'missing']+=1
        assert report['counts']==dict(snapshot_counts), 'Progress report does not match actual four-field completion'
        for wid,expected in report['originalWorkHashes'].items():
            actual=hashlib.sha256(json.dumps(workmap[wid],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            assert actual==expected, f'{wid}: source work changed since editorial review'
    return dict(counts)

if __name__=='__main__':
    print('Narrative editorial validation passed:', validate())
