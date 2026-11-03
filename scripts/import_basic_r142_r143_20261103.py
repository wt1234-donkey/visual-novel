#!/usr/bin/env python3
"""Reproducible append-only intake from a pinned public-source snapshot."""
import argparse
import base64
import copy
import gzip
import hashlib
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path
import import_basic_r134_r135_20261103 as e

ROOT = Path(__file__).resolve().parents[1]
BASE = '94b24cb8e9678709a93d44eee22fb1cdc9ad2e09'
MANIFEST = ROOT / 'data/basic-r142-r143-source-manifest-20261103.json'
PREFIX = 'public-catalogues-20261103-r'
REPORT = ROOT / 'data/basic-r142-r143-audit-summary-20261103.md'
DERIVATIVE = re.compile(r'(?i)(\b(?:dlc|demo|trial|remake|remaster(?:ed)?|collection|bundle|expansion|fan.?disc|fandisk|FD|HD|definitive|ultimate|enhanced)\b|体験版|ファンディスク|リメイク|リマスター|復刻|完全版|新装版|移植版|追加シナリオ|アフター.{0,10}ストーリーズ|after.{0,15}stories|合辑|合集|重制|重製|高清|重置版|資料集|资料集|サウンドトラック)')
NARRATIVE = re.compile(r'故事|剧情|劇情|主角|主人公|物語|ストーリー|扮演|角色扮演|\bstory\b|\bprotagonist\b', re.I)
EXCLUDED = re.compile(r'MMORPG|MMO|网游|網遊|网络游戏|網絡遊戲|放置|卡牌对战|竞技|競技|麻雀|麻将|體育|体育|音游|音乐游戏', re.I)
CANCELLED = re.compile(r'発売中止|開発中止|开发中止|開發中止|取消发售|取消發售|未発売|尚未发售|尚未發售|release cancelled|unreleased', re.I)

def base_registry():
    return json.loads(subprocess.check_output(['git','show',BASE+':'+str(e.REG.relative_to(ROOT))],cwd=ROOT))

def read_snapshot(key, manifest):
    info = manifest['snapshots'][key]
    payload = (ROOT / info['file']).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == info['sha256']
    raw = gzip.decompress(base64.b64decode(payload))
    assert hashlib.sha256(raw).hexdigest() == info['uncompressedSha256']
    return json.loads(raw)

def values(value):
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [s for item in value for s in values(item)]
    if isinstance(value, dict):
        return values(value.get('v', ''))
    return []

def bangumi_candidate(row):
    """Return source facts and a disposition; tags alone do not prove scope."""
    fields = defaultdict(list)
    for item in row.get('infobox') or []:
        fields[item['key']].extend(values(item.get('value')))
    aliases = list(dict.fromkeys([row.get('name_cn') or '', *fields['别名']]))
    aliases = [s for s in aliases if s and s != row['name']]
    genre = ' / '.join(fields['游戏类型'])
    rowdate = row.get('date') or ''
    year = int(rowdate[:4]) if re.match(r'^\d{4}(?:-|$)', rowdate) else None
    result = {'sourceKind':'bangumi','sourceId':str(row['id']), 'title':row['name'],
              'aliases':aliases,'source':'https://bgm.tv/subject/'+str(row['id']),
              'sourceRefs':['bangumi:'+str(row['id']), 'bgm:'+str(row['id'])],
              'firstYear':year,'sourceDate':rowdate,'sourceGenre':genre,
              'sourceReleaseFields':fields['发行日期'],
              'group':' / '.join(fields['开发'] or fields['游戏开发商'] or fields['开发商']) or '创作主体待核'}
    is_adv = re.search(r'ADV|AVG|ノベル|ビジュアルノベル|视觉小说|視覺小說|文字冒险|文字冒險|Visual\s*Novel', genre, re.I)
    is_rpg = re.search(r'RPG|角色扮演', genre, re.I)
    if not is_adv and not is_rpg:
        return result, 'outside-or-unproven-narrative-scope'
    if EXCLUDED.search(genre):
        return result, 'outside-or-unproven-narrative-scope'
    if is_rpg and not NARRATIVE.search(row.get('summary') or ''):
        return result, 'narrative-rpg-evidence-held'
    if is_adv and not is_rpg and not NARRATIVE.search(row.get('summary') or '') and not re.search(r'ノベル|视觉小说|視覺小說|Visual\s*Novel',genre,re.I):
        return result, 'narrative-adv-evidence-held'
    result['gameplay'] = 'ADV' if is_adv and not is_rpg else 'RPG'
    if not year or not 1970 <= year <= 2026:
        return result, 'missing-or-invalid-year-held'
    if rowdate > '2026-11-03' and len(rowdate) >= 10:
        return result, 'unreleased-or-future-date-held'
    if CANCELLED.search(row.get('summary') or ''):
        return result, 'unreleased-or-cancelled-held'
    release_years = {int(y) for text in fields['发行日期'] for y in re.findall(r'(?<!\d)(?:19|20)\d{2}(?!\d)',text)}
    if release_years and release_years != {year}:
        return result, 'source-year-conflict-held'
    # A mention of a remake/port may refer to another release: keep it for review.
    edition_text = ' '.join([row['name'],*aliases,genre,row.get('summary') or '',*row.get('meta_tags',[])])
    if DERIVATIVE.search(edition_text):
        return result, 'possible-edition-or-dependent-content-held'
    result['gameplayNote'] = '来源游戏类型：'+genre+'；具体交互方式待专门核查。'
    result['yearBasis'] = 'Bangumi条目日期与发行日期字段年粒度一致（无字段时仅据条目日期）；基础身份暂记原作年，未独立核对每个平台首发。'
    return result, None

def work_from(candidate, round_number):
    sid = candidate['sourceId']
    wid = ('bangumi-'+sid) if candidate['sourceKind']=='bangumi' else 'pc98-igdb-'+sid
    return {'id':wid,'indexId':'basic-'+PREFIX+str(round_number)+'-'+wid,
            'title':candidate['title'],'aliases':candidate['aliases'],
            'firstYear':candidate['firstYear'],'gameplay':candidate['gameplay'],
            'gameplayNote':candidate['gameplayNote'],'group':candidate['group'],
            'source':candidate['source'],'sourceRefs':candidate['sourceRefs'],
            'mainPlacement':'promoted-basic','linkedRecordId':None,
            'creditScope':'来源开发关联仅供检索；未建立正式个人／机构职责。',
            'yearBasis':candidate['yearBasis'],
            'editorialScope':'仅补基础身份和来源；详细叙事、原始首发及内容版本仍待专门编目。',
            'batch':PREFIX+str(round_number)}

class NameIndex(defaultdict):
    def __init__(self, initial):
        super().__init__(set,initial)
        self.prefixes=defaultdict(set)

    def refresh_prefixes(self):
        for name in self:
            if len(name)>=8:self.prefixes[name[:8]].add(name)

def name_index(reg):
    index = NameIndex(e.full_index(reg))
    # Short names also collide, even if too ambiguous for automatic reuse.
    for work in e.catalogue.all_works(reg):
        for name in e.catalogue.common.names(work):
            if e.norm(name):
                index[e.norm(name)].add((work['id'],int(work.get('firstYear') or 0),'full-catalogue'))
    index.refresh_prefixes()
    return index

def decide(candidate, index, refs):
    names = [candidate['title'],*candidate['aliases']]
    hits = set().union(*(index.get(e.norm(n),set()) for n in names))
    refhits = set().union(*(refs.get(r.casefold(),set()) for r in [*candidate['sourceRefs'],'source-url:'+candidate['source']]))
    if hits or refhits:
        ids = {h[0] for h in hits} | refhits
        years = {h[1] for h in hits if h[1]}
        candidate['matches'] = [list(h) for h in sorted(hits)]
        candidate['matchedWorkIds'] = sorted(ids)
        if len(ids)==1 and (not years or years=={candidate['firstYear']}):
            return 'existing-identity'
        return 'name-year-or-multiple-identity-held'
    variants=set()
    for name in names:
        key=e.norm(name)
        if len(key)<8:continue
        for oldname in getattr(index,'prefixes',{}).get(key[:8],set()):
            if key.startswith(oldname) or oldname.startswith(key):
                variants.update(index[oldname])
    if variants:
        candidate['matches']=[list(h) for h in sorted(variants)]
        candidate['matchedWorkIds']=sorted({h[0] for h in variants})
        candidate['basis']='较长标题与已有名称存在完整前缀关系；可能为省略副标题或版本名，须人工核查，不能自动新建。'
        return 'possible-title-variant-held'
    return None

def build():
    manifest = e.load(MANIFEST)
    assert manifest['baseCommit']==BASE
    bgm = read_snapshot('bangumi',manifest)
    wd = read_snapshot('wikidata',manifest)
    relations = read_snapshot('bangumiRelations',manifest)
    original = base_registry()
    reg = copy.deepcopy(original)
    index = name_index(reg)
    refs = defaultdict(set)
    for key, ids in e.full_refs(reg).items():
        refs[key.casefold()].update(ids)
    e.reserve_reviewed_pc98_reuse(index,refs,[ROOT/'data/pc98-admission-review-20261103.json',
        ROOT/'data/pc98-admission-review-r136-r137-20261103.json',
        ROOT/'data/pc98-admission-review-r138-r139-20261103.json'])
    index.refresh_prefixes()
    audits = {}
    added_ids = set()
    # Preserve earlier unmerged PC-98 work as an independently sourced historical candidate.
    historical = {'sourceKind':'historical','sourceId':'80836','title':'アークス','aliases':['ARCUS','アーカス'],
                  'firstYear':1988,'gameplay':'RPG','gameplayNote':'保存协会资料记剧情驱动角色扮演游戏。',
                  'group':'Wolf Team','source':'https://www.gamepres.org/pc88/library/1988/arcus.htm',
                  'sourceRefs':['igdb:80836','source-url:https://www.amusement-center.com/project/egg/pdf/launcher_key.pdf'],
                  'yearBasis':'游戏保存协会及Project EGG授权发行资料均记1988年；目录PC-98行复用原作身份，不按移植重复。'}
    historical_existing = {'sourceKind':'historical','sourceId':'84171','title':'38万キロの虚空 File1 A Day in the Life of 2049',
                  'aliases':['38万キロの虚空','38-man Kilo no Kokuu'],'firstYear':1989,'gameplay':'ADV',
                  'gameplayNote':'科幻小说式冒险作品。','group':'System Sacom',
                  'source':'https://www.d4e.co.jp/info/media/20240312_d4e_newsrelease.pdf','sourceRefs':['igdb:84171'],
                  'yearBasis':'D4授权发行资料记1989年原作；目录长标题与既有作品相同。'}
    wd_items = defaultdict(list)
    for r in wd['records']:
        wd_items[r['item']['value'].rsplit('/',1)[-1]].append(r)
    rows = bgm['records']
    midpoint = (len(rows)+1)//2
    for n, block in ((142,rows[:midpoint]),(143,rows[midpoint:])):
        records = []
        before = len(reg['works'])
        candidates = []
        if n==142:
            candidates.append((historical,None))
            candidates.append((historical_existing,None))
        candidates.extend(bangumi_candidate(row) for row in block)
        for c, reason in candidates:
            # Even a held candidate retains its source facts and exact reason.
            c = copy.deepcopy(c)
            if c['sourceKind']=='bangumi' and reason is None:
                related = relations['records'].get(c['sourceId'])
                c['relatedGameEvidence'] = related
                if related is None:
                    reason = 'version-relations-unavailable-held'
                elif any(x['relation'] in {'主版本','不同版本','不同演绎','扩展包','扩展','番外篇','总集篇','总集','合集','原作'} for x in related):
                    reason = 'possible-edition-or-dependent-content-held'
            duplicate = decide(c,index,refs) if c.get('firstYear') else None
            if reason:c['sourceReviewReason']=reason
            status = duplicate or reason
            if status is None:
                if len(reg['works'])-before >= 500:
                    status = 'verified-basic-candidate-staged-cap'
                else:
                    work = work_from(c,n)
                    assert work['id'] not in added_ids
                    reg['works'].append(work)
                    added_ids.add(work['id'])
                    e.reserve(work,index,refs)
                    for name in e.split_names(work):
                        key=e.norm(name)
                        if len(key)>=8:index.prefixes[key[:8]].add(key)
                    status = 'promoted-basic'
                    c['workId'] = work['id']
            c['status'] = status
            records.append(c)
        for ordinal,(qid, group) in enumerate(sorted(wd_items.items())):
            if ordinal % 2 != n-142:
                continue
            first = group[0]
            years = sorted({int(r['date']['value'][:4]) for r in group})
            aliases = list(dict.fromkeys(x.strip() for r in group for x in r.get('itemAltLabel',{}).get('value','').split(',') if x.strip()))
            source_refs = ['wikidata:'+qid]
            for r in group:
                for field,prefix in (('moby','mobygames:'),('igdb','igdb:'),('vndb','vndb:')):
                    if field in r:
                        source_refs.append(prefix+r[field]['value'])
            c = {'sourceKind':'wikidata','sourceId':qid,'title':first['itemLabel']['value'],
                 'aliases':aliases,'firstYear':min(years),'reportedYears':years,
                 'source':'https://www.wikidata.org/wiki/'+qid,'sourceRefs':list(dict.fromkeys(source_refs))}
            status = decide(c,index,refs)
            c['status'] = status or 'original-year-and-work-identity-review-staged'
            c['basis'] = 'Wikidata用于发现及跨目录ID关联；未取得独立原作年份证据的候选不直接入库。'
            records.append(c)
        count = len(reg['works'])-before
        assert 0 <= count <= 500
        for key in ('candidates','accepted','promotedBasic','addedToMainIdentityLayer'):
            reg['summary'][key] += count
        batchid = PREFIX+str(n)
        summary = {'candidates':count,'promoted-basic':count,'newDistinctWorks':count,'before':before,'after':len(reg['works']),
                   'scannedRecords':len(records),'dispositions':dict(Counter(r['status'] for r in records)),
                   'sourceCounts':dict(Counter(r['sourceKind'] for r in records)),
                   'newSourceCounts':dict(Counter(r['sourceKind'] for r in records if r['status']=='promoted-basic'))}
        path = ROOT/f'data/public-catalogues-review-20261103-r{n}.json'
        reg['batches'].append({'id':batchid,'source':['https://api.bgm.tv/v0/subjects','https://query.wikidata.org/','https://www.gamepres.org/'],
                              'review':str(path.relative_to(ROOT)),'summary':summary})
        audits[path] = {'schema':1,'date':'2026-11-03','baseCommit':BASE,'summary':summary,
                        'snapshotManifest':str(MANIFEST.relative_to(ROOT)),'records':records}
    assert len({w['id'] for w in reg['works']})==len(reg['works'])
    assert len({w['indexId'] for w in reg['works']})==len(reg['works'])
    assert reg['summary']['accepted']==len(reg['works'])
    assert reg['works'][:len(original['works'])]==original['works']
    pending = [dict(r,round=n) for n in (142,143) for r in audits[ROOT/f'data/public-catalogues-review-20261103-r{n}.json']['records']
               if r['status'].endswith('-held') or r['status'].endswith('-staged') or r['status'].endswith('-cap')]
    audits[ROOT/'data/public-catalogues-pending-20261103-r143.json'] = {'schema':1,'date':'2026-11-03','records':pending,
        'summary':dict(Counter(r['status'] for r in pending)), 'nextCursors':manifest['nextCursors']}
    prior_path='data/pc98-catalogue-audit-r140-r141-20261103.json'
    pc=copy.deepcopy(e.load(ROOT/prior_path))
    for row in pc['records']:
        if row['catalogue']=='ikachi-igdb' and row['sourceId'] in ('80836','84171'):
            row.update(status='reviewed-new-work' if row['sourceId']=='80836' else 'reviewed-existing-work',
                       candidateWorkId='pc98-igdb-80836' if row['sourceId']=='80836' else 'historical-71aee6cc5b98d400',
                       basis='详见第142批历史目录复核记录。')
    counts=Counter(r['status'] for r in pc['records'])
    pc.update(inputPendingAudit=prior_path,baseCommit=BASE)
    pc['summary'].update(dispositions=dict(counts),reviewedNewWorks=1,reviewedExistingWorks=1,
                         remainingUnresolvedRecords=sum(v for k,v in counts.items() if k.endswith('-held') or k=='needs-primary-year-and-alias-review'))
    assert pc['summary']['remainingUnresolvedRecords']==543
    audits[ROOT/'data/pc98-catalogue-audit-r142-r143-20261103.json']=pc
    lines=['# 基础身份库第142、143批来源审计','','每批最多新增500部。原有对象及精选主库不变；基础身份的数据库年份不等于逐平台首发已完成独立考据。','',
           '|批次|审计身份记录|新增独立作品|复用|隔离|暂存|范围外或缺准入依据|','|---|---:|---:|---:|---:|---:|---:|']
    for n in (142,143):
        s=audits[ROOT/f'data/public-catalogues-review-20261103-r{n}.json']['summary'];d=s['dispositions']
        lines.append(f"|{n}|{s['scannedRecords']}|{s['newDistinctWorks']}|{d.get('existing-identity',0)}|{sum(v for k,v in d.items() if k.endswith('-held'))}|{sum(v for k,v in d.items() if k.endswith('-staged') or k.endswith('-cap'))}|{d.get('outside-or-unproven-narrative-scope',0)}|")
    lines += ['',f"基础身份新增层 {original['summary']['promotedBasic']:,} → {reg['summary']['promotedBasic']:,}；含完整主库和专题关联的身份总清单 {len(original['works']):,} → {len(reg['works']):,}。",'',
              'IGDB及MobyGames API均实际返回401，环境中未配置专用凭据；本轮没有取得这两站的API游戏记录。历史目录新增来自保存协会及授权发行资料；含IGDB/MobyGames外部ID的Wikidata行不冒充直接采集。','',
              'Bangumi按已保存API页扫描，不按热门榜续采；继续前须重读上一页核对边界ID。Wikidata候选缺独立年份证据时进入暂存。','',
              '逐条隔离、暂存、来源ID、别名、年份和匹配身份见两批审计JSON；续采参数见来源清单。','']
    return original,reg,audits,'\n'.join(lines)

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');args=p.parse_args()
    original,expected,audits,report=build()
    if args.check:
        assert e.load(e.REG)==expected
        for path,value in audits.items(): assert e.load(path)==value
        assert REPORT.read_text()==report
        for name in e.catalogue.PROTECTED:
            assert subprocess.check_output(['git','show',BASE+':'+name],cwd=ROOT)==(ROOT/name).read_bytes()
        print('BASIC_R142_R143_CHECK_OK',len(original['works']),len(expected['works']))
    else:
        assert e.load(e.REG) in (original,expected), 'Registry changed; refusing overwrite'
        e.save(e.REG,expected)
        for path,value in audits.items():e.save(path,value)
        REPORT.write_text(report,encoding='utf-8')
        print('BASIC_R142_R143_WRITTEN',len(original['works']),len(expected['works']))

if __name__=='__main__':main()
