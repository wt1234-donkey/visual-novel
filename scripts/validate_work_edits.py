"""Validate additive website corrections and the last three per-work undo snapshots.

Original works/content/releases remain source records; this file is the current
website correction layer. Full older edits remain in Git history.
"""
import json
import unicodedata
from pathlib import Path
from source_urls import source_url_valid
ROOT=Path(__file__).resolve().parents[1]
FIELDS={'title','originalTitle','chineseTitle','chineseTitleType','titleAliases','category','subcategory','genre','synopsis','characters','charactersNote','charactersSource','source','interactionModes','interactionNote','interactionBasis','interactionSources','notes'}
ARRAYS={'titleAliases','characters','interactionModes','interactionSources'}

def validate(store=None, root=ROOT):
    read=lambda n:json.loads((root/'data'/n).read_text(encoding='utf-8'))
    store=read('work-edit-history.json') if store is None else store
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
        assert wid in works and set(row)=={'revision','overrides','recent'}
        assert type(row['revision']) is int and row['revision']>=1 and isinstance(row['recent'],list) and len(row['recent'])<=3
        patch(row['overrides']);last=None;seen=set();revision=0
        for entry in row['recent']:
            assert set(entry)=={'id','revision','at','actor','reason','sources','before','after'}
            assert isinstance(entry['id'],str) and entry['id'] and entry['id'] not in seen
            assert type(entry['revision']) is int and revision<entry['revision']<=row['revision']
            assert isinstance(entry['actor'],str) and entry['actor'] and isinstance(entry['reason'],str) and 5<=len(entry['reason'].strip())<=1000
            from datetime import datetime
            datetime.fromisoformat(entry['at'].replace('Z','+00:00'))
            assert entry['sources'] and all(source_url_valid(s) for s in entry['sources'])
            patch(entry['before']);patch(entry['after'])
            assert last is None or last==entry['before'], '修订快照不连续'
            seen.add(entry['id']);revision=entry['revision'];last=entry['after']
        assert last is None or last==row['overrides'], '当前记录与历史不一致'
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
if __name__=='__main__':print(f'网站作品更正与最近3次回撤记录校验通过：{validate()}部')
