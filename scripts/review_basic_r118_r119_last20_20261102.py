#!/usr/bin/env python3
"""Final review of the 20 held identities from basic rounds 118-119.

Source snapshots come from the frozen preceding evidence report, never inferred
from title matching. The 1982 IFDB Earthquake catalogue record is an alias of the
1981 original; the 1987 Quill Shipwreck is independent of the 1986 BASIC game.
All other approvals have explicit story/creator/context evidence.
"""
import argparse
from collections import Counter
import hashlib
import json
import subprocess
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
import import_basic_r22_cont_r23_20261101 as src
import basic_identity_decisions as identity_decisions

ROOT=src.ROOT
REG=src.REG
PRIOR=ROOT/'data/basic-r118-r119-identity-review-20261102.json'
EVIDENCE=ROOT/'data/basic-r118-r119-conflict-evidence-20261102.json'
OUT=ROOT/'data/basic-r118-r119-last20-decisions-20261102.json'
BATCH='r118-r119-last20-identity-review-20261102'
BASE='9898e9fb800d03a192dfcdc9e249a1c680d25edb'
TODAY='2026-11-02'

# Distinct original works: specifically reviewed collision evidence; not a
# blanket "different year means different game" exception.
APPROVED={
'v60981':('Different standalone 2025 TOOLBOX STUDIOS point-and-click psychological-horror story; the 1995 g1127 is Sierra Phantasmagoria.',
 ['https://lobotomizedrick.itch.io/phantasmagoria','https://vndb.org/v60981']),
'v61154':('2025 toroyachi visual novel; 2022 Headlights is Jordan White and Eric Zinda parser interactive fiction.',
 ['https://toroyachi.itch.io/','https://ifdb.org/viewgame?id=5x7v9fiblus23eb6']),
'v61668':('2026 Karol_thegame choice-led visual novel; prior NextMoe source v32084 is Logo and a different story.',
 ['https://kaguya.io/vn/summer-story-2026','https://vndb.org/v32084']),
'v61848':('2011 VNDB visual novel; 1991 Apprentice by Bert Lee is an AGT fantasy parser game, not a port.',
 ['https://vndb.org/v61848','https://ifdb.org/viewgame?id=sc9qfq1k945o51ak']),
'v61970':('2011 Russian-titled VNDB work; 2001 Ruins is an Inform tutorial/demo by Graham Nelson with documented language/system differences.',
 ['https://vndb.org/v61970','https://ifdb.org/viewgame?id=rnsj9vbk0ewwip61']),
'v62070':('2023-08-04 original interactive branching BL story confirmed by the creator; later 1.01/1.02 are updates, not new titles.',
 ['https://booth.pm/ja/items/4979841','https://vndb.org/v62070']),
'v62101':('2021-02-04 stand-alone Buddy Collection spinoff contains newly written original scenario and character routes.',
 ['https://plicy.net/NewsRelease/2021.02.04','https://vndb.org/v62101']),
'v62145':('2026 VirtualDateGaming work; 1985 House of Secrets is George Gunn Eamon RPG episode 97.',
 ['https://vndb.org/v62145','https://ifdb.org/viewgame?id=0slrzbo45nb1mebi']),
'v62160':('2003 BRUN Yotsuba character installment is distinct from 2002 BLANC Karen; VNDB series relation is not an edition or port.',
 ['https://vndb.org/v62160','https://vndb.org/v62159']),
'v62240':('2020 original 満淫電射 by Naito Mea/Omatsupan vs BISHOP 2003 満淫電車, distinct Japanese titles and works.',
 ['https://vndb.org/v62240','https://vndb.org/v6095']),
'v62338':('2026 Elizabeth/sugarxxholic original Salvation with new story; 2025 Altila Salvation is O2A2 micro kinetic novel about Evan/Clarissa.',
 ['https://sugarxxholic.itch.io/salvation','https://altila.itch.io/salvation']),
'v62373':('2026 Aventy team Цветок/Cvetok original VN; 1998 The Plant is Michael J. Roberts TADS story.',
 ['https://vndb.org/v62373','https://ifdb.org/viewgame?id=77rsl9mezn5iogto']),
'v62396':('2024 lunariamv visual novel vs 2002 Mu original Love Letter, different creators/years and setting.',
 ['https://vndb.org/v62396','https://vndb.org/v4948']),
'v62422':('2021 koloquials VN vs 2020 Gareth Pitchford Mirror Mirror ZX Spectrum PAWS parser.',
 ['https://vndb.org/v62422','https://ifdb.org/viewgame?id=vke24gmd8usqywu4']),
'v62532':('2025 original fanmade side-story Hope Recreation+ explicitly resolves questions left by the 2024 Hope Recreation prologue.',
 ['https://cirnox12.itch.io/danganronpa-hr','https://www.castingcall.club/projects/danganronpa-hope-recreation-0095bbf1-8ea9-40e4-907d-5aa78556661a']),
'v62751':('2025 DroptineArt visual novel distinct from 2003 Quintin Stone TADS2 interactive fiction Scavenger.',
 ['https://vndb.org/v62751','https://ifdb.org/viewgame?id=ii7j0kliujc4k8wf']),
'v62845':('2026 complete self-contained short courtroom visual novel by AFancyQuestionMark; minor UI updates and Steam release not new works.',
 ['https://afancyquestionmark.itch.io/vampire-on-trial','https://store.steampowered.com/app/4532990/']),
'v62867':('2022 tokUUU Tower original visual novel; 2009 Vivienne Dunstan Tower is Inform 7 text adventure.',
 ['https://vndb.org/v62867','https://ifdb.org/viewgame?id=8u6m0cofv7m7pn5u'])
}
APPROVED_IFDB={
'ifdb:iq9wxtd9a7vpcy2g':(
 '1987 Tartan Software Quill story by Gladys and Gerry Officer is a distinct title from the 1986 Magnum Computing BASIC game by Paul Davies; separate makers, implementation, and work provenance.',
 ['https://ifdb.org/viewgame?id=iq9wxtd9a7vpcy2g',
  'https://worldofspectrum.org/archive/software/games/shipwreck-tartan-software',
  'https://worldofspectrum.org/archive/publishers/Magnum-Computing',
  'https://mug-uk.co.uk/zx-spectrum-bl-adventure-games/',
  'https://viva-games.ru/game/shipwreck'])
}
REUSE={
'ifdb:x7cvej7bm7ixiz0a':(
 'ai-earthquake',
 'IFDB 1982 catalogue date reflects later platform publication of the 1981 TRS-80 original; same game, Jyym Pearson/Norman Sailer.',
 ['https://ifdb.org/viewgame?id=x7cvej7bm7ixiz0a','https://www.mobygames.com/game/29354/earthquake-san-francisco-1906/'])
}

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def dump(path, data):
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def build(reg):
    prev=load(PRIOR)
    ev=load(EVIDENCE)
    assert prev['summary']=={'originalHeldRows':67,'reviewedIdentities':56,
          'registeredDistinct':36,'reusedExisting':0,'stillHeld':20}
    held={r['sourceIdentity']:r for r in prev['decisions'] if r['status']=='held'}
    assert len(held)==20
    targets={'vndb:'+v for v in APPROVED} | set(APPROVED_IFDB) | set(REUSE)
    assert targets==set(held),'All twenty held identities require disposition'
    registered={w['id']:w for w in src.all_works(reg)}
    refs=src.identity_map(reg)
    summary=Counter()
    decisions=[]
    additions=[]
    for key in sorted(held):
        item=ev['identities'][key]
        original=held[key]
        assert item['sourceIdentity']==key
        assert original['sourceIdentity']==key and item['title']==original['title']
        src_kind, sid=key.split(':',1)
        first=item['candidateSnapshot']
        if key in REUSE:
            target, reason, sources=REUSE[key]
            assert target in registered
            assert registered[target]['firstYear']==1981
            assert item['intakeYear']==1982 and src_kind=='ifdb'
            assert not any(key in w.get('sourceRefs',[]) for w in registered.values()),'Do not rewrite an existing physical source ref'
            assert not refs.get(key) or refs[key]=={'ai-earthquake'},'Reviewed alias may only map to original work'
            status='reuse-existing'
            target_id=target
            year=1981
        elif key in APPROVED_IFDB:
            reason,sources=APPROVED_IFDB[key]
            status='registered-distinct'
            assert src_kind=='ifdb'
            assert first['title']=='Shipwreck'
            assert first['author']=='Gladys Officer, Gerry Officer'
            assert first['published'].startswith('1987-')
            year=1987
            target_id='ifdb-'+sid
            assert target_id not in registered and not refs.get(key)
            assert len(item['matches'])==1
            match=item['matches'][0]
            assert match['id']=='ifdb-1j9p7lpcoj2sf05i' and match['year']==1986
            assert match.get('registryWork') and match['id'] in registered
            assert registered[match['id']]['firstYear']==1986
            additions.append({
                'id':target_id,'indexId':BATCH+'-'+sid,
                'title':'Shipwreck','aliases':[],'firstYear':1987,
                'gameplay':'ADV','group':'创作品牌待核',
                'source':'https://ifdb.org/viewgame?id='+sid,
                'sourceRefs':[key],'mainPlacement':'promoted-basic',
                'linkedRecordId':None,
                'creditScope':'IFDB及World of Spectrum署名Gladys/Gerry Officer；仍待核正式制作与发行职责。',
                'yearBasis':'IFDB和World of Spectrum均为1987；1986 Magnum Computing同名游戏由Paul Davies制作，并非该作更早版本。',
                'editorialScope':'按独立作者、发行方及The Quill与BASIC制作方式对照，确认区别于1986年同名作品。',
                'identityReview':str(OUT.relative_to(ROOT)),'batch':BATCH})
        else:
            reason,sources=APPROVED[sid]
            status='registered-distinct'
            target_id='vndb-'+sid
            assert src_kind=='vndb'
            assert first['id']==sid and first['title']==item['title']
            assert first['devstatus']==0
            year=int(str(first['released'])[:4])
            assert 1970<=year<=2026 and str(first['released'])[:10]<=TODAY
            assert item['intakeYear'] in (None,year)
            assert target_id not in registered
            assert not refs.get(key)
            # The earlier conflict stays evidence; compare matched target as a
            # distinct source identity, not an automatic duplicate assignment.
            for match in item['matches']:
                rid=match['id']
                if match.get('registryWork'):
                    assert rid in registered and registered[rid]['firstYear']==match['year']
            names=src.previous.vndb_names(first)
            assert names and src.norm(item['title']) in {src.norm(n) for n in names}
            clean_refs=[key]
            for r in clean_refs: assert not refs.get(r)
            notes=[]
            if sid=='v62101': notes.append('独立番外篇；新增原创剧情与多角色路线。')
            if sid=='v62532': notes.append('独立同人支线；剧情内容新增，非商业官方作品。')
            if sid=='v62160': notes.append('系列中不同人物独立篇目；同一团队不表示同一作品。')
            if sid in ('v62070','v62845'): notes.append('后续程序或UI更新不另外计作品身份。')
            work={
                'id':target_id,'indexId':BATCH+'-'+sid,
                'title':names[0],'aliases':names[1:],'firstYear':year,
                'gameplay':'视觉小说','group':'创作品牌待核',
                'source':'https://vndb.org/'+sid,'sourceRefs':clean_refs,
                'mainPlacement':'promoted-basic','linkedRecordId':None,
                'creditScope':'来源作者与开发者信号见逐项复核证据；不自动认定正式发行职责。',
                'yearBasis':'VNDB VN-level released年；复核时对照创作者或发行方原始页面。仅作作品首发年，不推断全部地区与版本史。',
                'editorialScope':'经人工对照作品身份、作者、类型和内容关系解除冲突；完整编目待完善。'+' '.join(notes),
                'identityReview':str(OUT.relative_to(ROOT)),'batch':BATCH}
            additions.append(work)
        summary[status]+=1
        decisions.append({
          'sourceIdentity':key,'title':item['title'],'firstYear':year,
          'status':status,'registryId':target_id,'reason':reason,
          'sourceUrls':sources,'previousStatus':'held',
          'priorReview':str(PRIOR.relative_to(ROOT)),
          'originalRows':original['originalRows'],
          'currentNameMatches':original['currentNameMatches'],
          'matchedRecords':[{'id':m['id'],'year':m['year'],
             'registeredTitle':(m.get('registryWork') or {}).get('title')}
             for m in item.get('matches',[])],
          'candidateSnapshot':first
        })
    assert (summary['registered-distinct'],summary['reuse-existing'],summary['held'])==(19,1,0)
    return additions,decisions,dict(summary)

def check():
    a=load(OUT)
    reg=load(REG)
    assert a['baseCommit']==BASE
    for path,digest in a['sourceInputSha256'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
    additions,decisions,stats=build_for_check(reg,a)
    assert a['summary']=={'reviewed':20,'registeredDistinct':19,'reusedExisting':1,'remainingHeld':0}
    assert a['decisions']==decisions
    assert [w for w in reg['works'] if w.get('batch')==BATCH]==additions
    assert reg['summary']['accepted']==len(reg['works'])
    prior=json.loads(subprocess.check_output(
        ['git','show',BASE+':'+str(REG.relative_to(ROOT))],cwd=ROOT))
    assert len(reg['works'])==len(prior['works'])+19
    assert reg['works'][:len(prior['works'])]==prior['works']
    assert reg['batches'][:len(prior['batches'])]==prior['batches']
    assert reg['batches'][-1]['id']==BATCH
    for key,val in prior['summary'].items():
        assert reg['summary'][key]==val+(19 if key in
          ('candidates','accepted','promotedBasic','addedToMainIdentityLayer') else 0),(key,val)
    assert len(reg['works'])==len({w['id'] for w in reg['works']})
    assert len(reg['works'])==len({w['indexId'] for w in reg['works']})
    for path in src.PROTECTED:
        assert (ROOT/path).read_bytes()==subprocess.check_output(
           ['git','show',BASE+':'+path],cwd=ROOT),path
    refs=src.identity_map(reg)
    assert refs.get('ifdb:x7cvej7bm7ixiz0a')=={'ai-earthquake'}
    ids={w['id'] for w in src.all_works(reg)}
    assert len(ids)>=len(reg['works'])
    assert all(d['registryId'] not in ids for d in a['decisions'] if d['status']=='held' and d['registryId'])
    print('LAST20_CHECK_OK +19 reuse 1 held 0',flush=True)

def build_for_check(reg,a):
    # Check exact added-work objects without consulting mutable live APIs.
    recorded=a['worksToAppend']
    seen={w['id'] for w in recorded}
    assert len(seen)==len(recorded)==19
    assert all(w['batch']==BATCH and w['identityReview']==str(OUT.relative_to(ROOT)) for w in recorded)
    assert all(w['sourceRefs']==[('ifdb:' if w['id'].startswith('ifdb-') else 'vndb:')+w['id'].split('-',1)[1]] for w in recorded)
    assert len(a['decisions'])==20
    assert {d['sourceIdentity'] for d in a['decisions']}==(
        {'vndb:'+k for k in APPROVED}|set(APPROVED_IFDB)|set(REUSE))
    for d in a['decisions']:
        assert d['reason'] and d['sourceUrls']
    return recorded,a['decisions'],a['summary']

def apply():
    reg=load(REG)
    if any(b['id']==BATCH for b in reg['batches']):
        existing=load(OUT)
        if existing['summary']['registeredDistinct']==19:
            check()
            return
        # GitHub Actions earlier committed the 18-item conservative version to
        # this PR before the distinct 1987 Shipwreck evidence was recovered.
        # Upgrade only that exact reviewed append, never rewrite base objects.
        assert existing['summary']=={'reviewed':20,'registeredDistinct':18,
                                      'reusedExisting':1,'remainingHeld':1}
        baseline=json.loads(subprocess.check_output([
            'git','show',BASE+':'+str(REG.relative_to(ROOT))],cwd=ROOT))
        assert len(reg['works'])==len(baseline['works'])+18
        assert reg['works'][:len(baseline['works'])]==baseline['works']
        prior_additions=[w for w in reg['works'] if w.get('batch')==BATCH]
        assert prior_additions==existing['worksToAppend']
        additions, decisions, stats=build(baseline)
        assert len(additions)==19
        new_by_id={w['id']:w for w in additions}
        assert all(new_by_id.get(w['id'])==w for w in prior_additions)
        assert {w['id'] for w in additions}-{w['id'] for w in prior_additions}=={
            'ifdb-iq9wxtd9a7vpcy2g'}
        reg['works']=baseline['works']+additions
        for field in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
            reg['summary'][field]+=1
        reg['batches'][-1]['summary'].update({
            'candidates':19,'promoted-basic':19,'remainingHeld':0})
        existing['summary']={'reviewed':20,'registeredDistinct':19,
                             'reusedExisting':1,'remainingHeld':0}
        existing['policy']='1987 Tartan Shipwreck distinct from 1986 Magnum by creators and engine; 1982 IFDB Earthquake alias of original 1981 work; no older identities or cursors changed.'
        existing['decisions']=decisions
        existing['worksToAppend']=additions
        dump(OUT,existing)
        dump(REG,reg)
        identity_decisions.decisions.cache_clear()
        check()
        print('LAST20_AUDIT_UPGRADED 18 to 19 distinct, 1 alias, 0 held',flush=True)
        return
    additions, decisions, stats=build(reg)
    assert len(additions)==19
    audit={'schema':1,'date':TODAY,'baseCommit':BASE,'batchId':BATCH,
        'sourceInputSha256':{str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in (PRIOR,EVIDENCE)},
        'summary':{'reviewed':20,'registeredDistinct':19,'reusedExisting':1,'remainingHeld':0},
        'policy':'Exact source-identity comparisons only; 2026-11-02 evidence snapshot pinned. 1987 Tartan Shipwreck differs from 1986 Magnum Computing Shipwreck by author, publisher and engine. Earthquake source becomes a cross-source alias; preserve old year/object. No cursor or historical audit mutated.',
        'decisions':decisions,'worksToAppend':additions}
    # Never rewrite historical entries. No extra source-refs added to old objects:
    # reviewed alias is resolved by basic_identity_decisions.py
    oldworks=len(reg['works'])
    reg['works'].extend(additions)
    for key in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
        reg['summary'][key]+=19
    reg['updated']=TODAY
    reg['batches'].append({'id':BATCH,
        'source':['https://api.vndb.org/kana/vn','https://ifdb.org/'],
        'review':str(OUT.relative_to(ROOT)),
        'summary':{'candidates':19,'promoted-basic':19,'reviewedIdentities':20,
                   'reusedExisting':1,'remainingHeld':0}})
    assert len(reg['works'])==oldworks+19
    dump(OUT,audit)
    dump(REG,reg)
    # The first catalogue read memoized decisions before this audit existed.
    identity_decisions.decisions.cache_clear()
    check()
    print('LAST20_REVIEW_IMPORTED 19 new, 1 alias, 0 held',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    check() if args.check else apply()
