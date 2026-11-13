"""Validate current formal corrections, compatibility undo and checkpoint-forward audit."""
import copy
import hashlib
import json
import unicodedata
from pathlib import Path
from source_urls import source_url_valid
ROOT=Path(__file__).resolve().parents[1]
CREATOR_NAMES={'writerNames','artistNames','musicianNames'}
FIELDS={'title','originalTitle','chineseTitle','chineseTitleType','titleAliases','category','subcategory','genre','synopsis','characters','charactersNote','charactersSource','source','interactionModes','interactionNote','interactionBasis','interactionSources','notes'}|CREATOR_NAMES
ARRAYS={'titleAliases','characters','interactionModes','interactionSources'}|CREATOR_NAMES

def field_meta(row):
    result=copy.deepcopy(row.get('fieldMeta',{}))
    for event in row.get('recent',[]):
        for key in FIELDS:
            if event['before'].get(key)!=event['after'].get(key) and key not in row.get('fieldMeta',{}):
                result[key]={'id':event['id'],'at':event['at']}
    return {key:value for key,value in result.items() if key in row.get('overrides',{})}

def replay_formal(store, validate_state=lambda state:None):
    from datetime import datetime
    journal=store['journal']
    assert set(store)=={'schemaVersion','records','journal'} and journal['schemaVersion']==1
    assert journal['checkpoint']['coverage']=='checkpoint-forward'
    datetime.fromisoformat(journal['checkpoint']['at'].replace('Z','+00:00'))
    assert journal['baseline']['schemaVersion']==1 and isinstance(journal['events'],list)
    state=copy.deepcopy(journal['baseline']);seen={e['id'] for row in state['records'].values() for e in row['recent']}
    validate_state(state)
    for sequence,event in enumerate(journal['events'],1):
        assert event['schemaVersion']==1 and event['sequence']==sequence
        assert isinstance(event['id'],str) and event['id'] and event['id'] not in seen
        seen.add(event['id']);datetime.fromisoformat(event['at'].replace('Z','+00:00'))
        assert isinstance(event['actor'],str) and event['actor'].strip() and 5<=len(event['reason'].strip())<=1000
        assert isinstance(event['sources'],list) and all(source_url_valid(s) for s in event['sources'])
        wid=event['workId'];before=state['records'].get(wid)
        assert before==event['before'], '正式事件修改前值不匹配'
        previous=before or {'revision':0,'overrides':{},'recent':[]}
        assert event['previousRevision']==previous['revision'] and event['revision']==previous['revision']+1
        after=event['after'];assert after['revision']==event['revision']
        kind=event['commandType'];assert kind in ('edit','creators','undo') and event['intent']['type']==kind
        for side,patch in [('before',previous['overrides']),('after',after['overrides'])]:
            assert set(event['values'][side])==FIELDS
            assert all(event['values'][side][k]==v for k,v in patch.items())
        if kind=='undo':
            assert event['undoOf']==event['intent']['targetId']
            index=next((i for i,e in enumerate(previous['recent']) if e['id']==event['undoOf']),None)
            assert index is not None, '正式撤销目标不存在'
            target=previous['recent'][index];recent=previous['recent'][:index]
            expected=dict(revision=event['revision'],overrides=target['before'],recent=recent,
                          fieldMeta=target.get('beforeFieldMeta',field_meta(dict(overrides=target['before'],recent=recent))))
            assert after==expected, '正式撤销结果不匹配'
        else:
            entry={key:event[key] for key in ('id','revision','at','actor','reason','sources')}
            entry.update(before=previous['overrides'],after=after['overrides'],beforeFieldMeta=field_meta(previous))
            assert after['recent']==[*previous['recent'],entry][-3:], '正式快照与事件不一致'
            metadata=field_meta(previous);changed=set()
            for key in FIELDS:
                if key not in after['overrides']:metadata.pop(key,None)
                elif event['values']['before'][key]!=event['values']['after'][key]:metadata[key]={'id':event['id'],'at':event['at']}
                if event['values']['before'][key]!=event['values']['after'][key]:changed.add(key)
            assert changed and after['fieldMeta']==metadata, '正式字段更正身份或时间不匹配'
            if kind=='edit':assert event['intent']['values']==event['values']['after']
            else:
                assert event['intent']['names']=={key:event['values']['after'][key] for key in CREATOR_NAMES}
                assert changed<=CREATOR_NAMES
        state['records'][wid]=copy.deepcopy(after)
        validate_state(state)
    assert state=={'schemaVersion':1,'records':store['records']}, '正式日志回放与当前状态不一致'
    return state

def validate(store=None, root=ROOT):
    read=lambda n:json.loads((root/'data'/n).read_text(encoding='utf-8'))
    actual_file=store is None
    store=read('work-edit-history.json') if store is None else store
    if store.get('schemaVersion')==2:
        replay_formal(store,lambda state:validate(state,root))
        if actual_file:
            expected=json.loads((root/'config/formal-audit-checkpoint.json').read_text())
            canonical=json.dumps(store['journal']['baseline'],ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
            assert hashlib.sha256(canonical).hexdigest()==expected['baselineSha256'], '正式迁移检查点已变化'
            assert all(expected[k]==store['journal']['checkpoint'][k] for k in ('at','sourceCommit'))
        store={'schemaVersion':1,'records':store['records']}
    works={w['id']:w for w in [*read('non-rpg-creator-supplement-20261030.json')['works'],*read('games.json')['works']]}
    taxonomy=read('taxonomy.json')
    assert set(store)=={'schemaVersion','records'} and store['schemaVersion']==1 and isinstance(store['records'],dict)
    def patch(p):
        assert isinstance(p,dict) and set(p)<=FIELDS, '不可编辑作品身份、年份或历史发行字段'
        for k,v in p.items():
            if k in ARRAYS:
                assert isinstance(v,list) and len(v)<=100 and all(isinstance(x,str) and x.strip() and len(x)<=500 for x in v) and len(v)==len(set(v))
            else:assert isinstance(v,str) and len(v)<=20000
    for wid,row in store['records'].items():
        assert wid in works and {'revision','overrides','recent'}<=set(row)<={'revision','overrides','fieldMeta','recent'}
        assert type(row['revision']) is int and row['revision']>=1 and isinstance(row['recent'],list) and len(row['recent'])<=3
        patch(row['overrides']);last=None;seen=set();revision=0
        for entry in row['recent']:
            assert {'id','revision','at','actor','reason','sources','before','after'}<=set(entry)<={'id','revision','at','actor','reason','sources','before','after','beforeFieldMeta'}
            assert isinstance(entry['id'],str) and entry['id'] and entry['id'] not in seen
            assert type(entry['revision']) is int and revision<entry['revision']<=row['revision']
            assert isinstance(entry['actor'],str) and entry['actor'] and isinstance(entry['reason'],str) and 5<=len(entry['reason'].strip())<=1000
            from datetime import datetime
            datetime.fromisoformat(entry['at'].replace('Z','+00:00'))
            patch(entry['before']);patch(entry['after'])
            changed={k for k in FIELDS if entry['before'].get(k,[] if k in CREATOR_NAMES else None)!=entry['after'].get(k,[] if k in CREATOR_NAMES else None)}
            assert isinstance(entry['sources'],list) and all(source_url_valid(s) for s in entry['sources'])
            assert entry['sources'] or (changed and changed<=CREATOR_NAMES), '只有剧作、美术与音乐姓名的修改可不填来源'
            assert last is None or last==entry['before'], '修订快照不连续'
            seen.add(entry['id']);revision=entry['revision'];last=entry['after']
        assert last is None or last==row['overrides'], '当前记录与历史不一致'
        def metadata(value,patch):
            from datetime import datetime
            assert isinstance(value,dict) and set(value)<=set(patch)
            for item in value.values():
                assert isinstance(item.get('id'),str) and item['id']
                datetime.fromisoformat(item['at'].replace('Z','+00:00'))
        metadata(row.get('fieldMeta',{}),row['overrides'])
        for entry in row['recent']:metadata(entry.get('beforeFieldMeta',{}),entry['before'])
        w=works[wid]|row['overrides']
        assert all(isinstance(w.get(k),str) and w[k].strip() for k in ('title','originalTitle','genre','synopsis','interactionNote','interactionBasis'))
        assert w['category'] in taxonomy['subcategories'] and w['subcategory'] in taxonomy['subcategories'][w['category']]
        assert isinstance(w['characters'],list) and w['characters'] and all(isinstance(x,str) and x.strip() and '待核实' not in x for x in w['characters'])
        assert source_url_valid(w['source']) and all(source_url_valid(s) for s in w['interactionSources']) and w['interactionSources']
        assert not w.get('charactersSource') or source_url_valid(w['charactersSource'])
        assert w.get('chineseTitleType','通行译名') in {'通行译名','站内编辑译名'} and (w.get('chineseTitleType')!='站内编辑译名' or w.get('chineseTitle'))
        assert w['interactionModes'] and set(w['interactionModes'])<=set(taxonomy['interactionModes'])
        assert '待核实' not in w['interactionModes'] or w['interactionModes']==['待核实']
    coverage=read('company-coverage.json')
    others=[*works.values(),*[w for c in coverage['companies'] for f in ('relatedGames','dossierOnlyWorks') for w in c.get(f,[])]]
    norm=lambda x: ''.join(c for c in unicodedata.normalize('NFKC',x).casefold() if c.isalnum())
    names=lambda w:{norm(n) for n in [w.get('title',''),w.get('originalTitle',''),w.get('chineseTitle',''),*w.get('titleAliases',[])] if n}
    projected=[w|store['records'].get(w['id'],{}).get('overrides',{}) for w in others]
    for wid,row in store['records'].items():
        introduced=names(works[wid]|row['overrides'])-names(works[wid])
        assert not any(w['id']!=wid and introduced & names(w) for w in projected), '网页更正名称与其他身份冲突'
    return len(store['records'])
if __name__=='__main__':print(f'正式作品更正、快捷回撤及完整审计校验通过：{validate()}部')
