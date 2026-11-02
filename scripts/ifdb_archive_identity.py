#!/usr/bin/env python3
"""Read minimal identity facts from IFDB's official public SQL export; never execute SQL."""
import datetime as dt
import hashlib
import html
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict, deque
from pathlib import Path

ARCHIVE_URL='https://ifarchive.org/if-archive/info/ifdb/ifdb-archive-20260901.zip'
ARCHIVE_SHA256='0f7909470d03f4235e49637e492ca1c31ad7e0558a61bdd07fced1cb128a935b'
TOKEN=re.compile(r"'(?:\\.|[^'\\])*'|NULL|-?\d+(?:\.\d+)?", re.S)
ESCAPES={'0':'\0','b':'\b','n':'\n','r':'\r','t':'\t','Z':'\x1a'}
TABLES={'games','ifids','gamefwds','gamexrefs','gamelinks'}
KEEP={'id','title','author','published','system','language','flags','website','tags'}


def sql_rows(values):
    """Strict INSERT VALUES grammar, including MySQL quoted-string escapes."""
    i=0
    while i<len(values):
        if values[i] in ' \r\n\t,;':
            i+=1
            continue
        if values[i]!='(':
            raise ValueError('Expected row')
        i+=1
        row=[]
        while True:
            while values[i].isspace(): i+=1
            match=TOKEN.match(values,i)
            if not match: raise ValueError('Unsupported SQL literal')
            token=match[0]
            if token.startswith("'"):
                value=re.sub(r'\\(.)',lambda m:ESCAPES.get(m[1],m[1]),token[1:-1],flags=re.S)
            else:
                value=None if token=='NULL' else int(token) if '.' not in token else float(token)
            row.append(value)
            i=match.end()
            while values[i].isspace(): i+=1
            if values[i]==')':
                i+=1
                break
            if values[i]!=',': raise ValueError('Expected field separator')
            i+=1
        yield row


def archive_path(path):
    path=Path(path)
    if not path.exists():
        req=urllib.request.Request(ARCHIVE_URL,headers={'User-Agent':'NarrativeCatalogueResearch/1.1 (wt1234-donkey/visual-novel; minimal metadata)'})
        with urllib.request.urlopen(req,timeout=120) as response:
            path.write_bytes(response.read(50_000_001))
    if hashlib.sha256(path.read_bytes()).hexdigest()!=ARCHIVE_SHA256:
        raise ValueError('Unexpected IFDB archive checksum')
    return path


def read_archive(path):
    columns={}
    data={k:[] for k in TABLES}
    current=None
    with zipfile.ZipFile(archive_path(path)) as z:
        with z.open('ifdb-archive.sql') as stream:
            for raw in stream:
                line=raw.decode('utf-8',errors='replace')
                create=re.match(r'CREATE TABLE `(\w+)`',line)
                if create:
                    current=create[1]
                    if current in TABLES: columns[current]=[]
                elif current in TABLES and (column:=re.match(r'  `(\w+)`',line)):
                    columns[current].append(column[1])
                elif line.startswith(') ENGINE='): current=None
                insert=re.match(r'INSERT INTO `(\w+)` VALUES ',line)
                if not insert or insert[1] not in TABLES: continue
                table=insert[1]
                for row in sql_rows(line[insert.end():]):
                    if len(row)!=len(columns[table]):
                        raise ValueError('Archive schema changed: '+table)
                    record=dict(zip(columns[table],row))
                    if table=='games': record={k:v for k,v in record.items() if k in KEEP}
                    elif table=='gamelinks': record={k:record[k] for k in ('gameid','url')}
                    elif table=='gamefwds': record={k:record[k] for k in ('gameid','fwdgameid')}
                    data[table].append(record)
    return data


def clean_title(value):
    return ' '.join(html.unescape(re.sub(r'</?(?:i|b|em|strong|span)(?:\s[^>]*)?>','',value or '',flags=re.I)).split())


def canonical_id(tuid,forwards):
    seen=set()
    while tuid in forwards:
        if tuid in seen: raise ValueError('Cyclic IFDB redirect')
        seen.add(tuid)
        tuid=forwards[tuid]
    return tuid


def prepare(data,cutoff):
    games={r['id']:r for r in data['games']}
    forwards={r['gameid']:r['fwdgameid'] for r in data['gamefwds']}
    identifiers=defaultdict(set)
    aliases=defaultdict(set)
    links=defaultdict(set)
    blocked=defaultdict(list)
    for old in forwards:
        target=canonical_id(old,forwards)
        identifiers[target].add('ifdb:'+old)
        if old in games: aliases[target].add(clean_title(games[old]['title']))
    for r in data['ifids']:
        identifiers[canonical_id(r['gameid'],forwards)].add('ifid:'+r['ifid'].casefold())
    for r in data['gamexrefs']:
        # Ports/translations/remakes require a separate content-identity review.
        if r['reftype'] in {2,4,7}:
            blocked[canonical_id(r['fromid'],forwards)].append({'target':'ifdb:'+canonical_id(r['toid'],forwards),'relation':r['reftype']})
    for r in data['gamelinks']:
        if isinstance(r['url'],str): links[canonical_id(r['gameid'],forwards)].add(r['url'])
    rows=[]
    rejected=Counter()
    for tuid,g in sorted(games.items()):
        if tuid in forwards:
            rejected['redirected-identity']+=1
            continue
        title=clean_title(g['title'])
        published=g['published'] or ''
        try: date=dt.date.fromisoformat(published[:10])
        except ValueError:
            rejected['missing-or-invalid-published-date']+=1
            continue
        if not 1976<=date.year or date>cutoff:
            rejected['outside-original-year-window']+=1
            continue
        if g.get('flags')!=0 or not re.fullmatch('[a-z0-9]{16}',tuid) or not title or '\ufffd' in title:
            rejected['flagged-or-invalid-identity']+=1
            continue
        if blocked[tuid]:
            rejected['translation-port-remake-held']+=1
            continue
        tags=str(g.get('tags') or '').casefold()
        if any(t in tags for t in ['noninteractive','non-interactive','game doesn\'t exist']):
            rejected['noninteractive-or-nonexistent-held']+=1
            continue
        if re.search(r'(?i)\b(demo|trial|collection|bundle|remaster|walkthrough|source code|game engine|tutorial)\b',title):
            rejected['edition-or-non-work-held']+=1
            continue
        refs={'ifdb:'+tuid,*identifiers[tuid]}
        urls=links[tuid]|{g.get('website') or ''}
        vndb={m[1] for u in urls for m in re.finditer(r'https?://(?:www\.)?vndb\.org/(v\d+)(?=[/?#\s]|$)',u)}
        rows.append({'tuid':tuid,'title':title,'aliases':sorted(a for a in aliases[tuid] if a and a!=title),
            'firstYear':date.year,'published':published,'author':g['author'],'system':g['system'],'language':g['language'],
            'sourceRefs':sorted(refs),'linkedVndbIds':sorted(vndb),
            'archiveLinks':sorted(u for u in urls if re.match(r'https?://(?:www\.)?ifarchive\.org/',u))})
    # Shared IFIDs between different canonical TUIDs are ambiguous, even if the titles differ.
    owners=defaultdict(set)
    for tuid,identities in identifiers.items():
        for ref in identities: owners[ref.casefold()].add(tuid)
    safe=[]
    for row in rows:
        if any(len(owners[ref.casefold()])>1 for ref in row['sourceRefs']):
            rejected['shared-ifid-held']+=1
        elif row['linkedVndbIds']:
            # Explicit cross-catalogue links are retained for reuse review, never assigned a new identity here.
            rejected['cross-vndb-link-held']+=1
        else: safe.append(row)
    return safe,dict(rejected)


def diverse_order(rows):
    groups=defaultdict(lambda:defaultdict(deque))
    for row in sorted(rows,key=lambda r:(r['firstYear'],r['tuid'])):
        groups[row['firstYear']//10*10][(row['author'] or 'unknown').casefold()].append(row)
    decade_queues={}
    for decade,authors in groups.items():
        q=deque()
        while any(authors.values()):
            for author in sorted(authors):
                if authors[author]: q.append(authors[author].popleft())
        decade_queues[decade]=q
    while any(decade_queues.values()):
        for decade in sorted(decade_queues):
            if decade_queues[decade]: yield decade_queues[decade].popleft()


def resume_position(review):
    """An archive offset is valid only for the exact pinned export."""
    if review.get('url')!=ARCHIVE_URL or review.get('sha256')!=ARCHIVE_SHA256:
        raise ValueError('IFDB resume archive does not match the pinned export')
    position=review.get('nextPosition')
    if type(position) is not int or position<1:
        raise ValueError('Invalid IFDB resume position')
    return position


def choose(rows,needed,index,refs,norm,batch,*,start_position=1):
    if type(start_position) is not int or not 1<=start_position<=len(rows)+1:
        raise ValueError('IFDB resume position is outside the candidate sequence')
    selected=[]
    reused=[]
    held=[]
    counts=Counter()
    # IFIDs are case insensitive; source refs from older importers may use upper case.
    folded=defaultdict(set)
    for ref,ids in refs.items(): folded[ref.casefold()].update(ids)
    scanned=0
    last_position=start_position-1
    for position,row in enumerate(diverse_order(rows),1):
        if position<start_position: continue
        if len(selected)==needed: break
        scanned+=1
        last_position=position
        names=[row['title'],*row['aliases']]
        hits=set().union(*(folded.get(ref.casefold(),set()) for ref in row['sourceRefs']))
        if hits:
            counts['reused-external-identity']+=1
            reused.append({'sourceId':row['tuid'],'matchedWorkIds':sorted(hits),'basis':'ifdb-tuid-or-case-insensitive-ifid'})
            continue
        matches=set().union(*(index.get(norm(n),set()) for n in names))
        if matches:
            # Ambiguous same-name different-year records are held, not merged or added.
            if len({str(m[0]) for m in matches})==1 and {m[1] for m in matches}=={row['firstYear']}:
                counts['reused-title-alias']+=1
                reused.append({'sourceId':row['tuid'],'matchedWorkIds':sorted({str(m[0]) for m in matches}),'basis':'normalized-title-alias-and-year'})
            else:
                counts['name-year-conflict-held']+=1
                held.append({'sourceId':row['tuid'],'title':row['title'],'published':row['published'],'reason':'name-year-conflict','matches':sorted(matches)})
            continue
        if not all(norm(n) and '\ufffd' not in n for n in names):
            counts['invalid-name-held']+=1
            continue
        work={'id':'ifdb-'+row['tuid'],'indexId':batch+'-ifdb-'+row['tuid'],'title':row['title'],
            'aliases':list(dict.fromkeys(row['aliases'])),'firstYear':row['firstYear'],
            'gameplay':'互动小说（玩法待核）','group':'创作品牌待核',
            'source':'https://ifdb.org/viewgame?id='+row['tuid'],'sourceRefs':row['sourceRefs'],
            'mainPlacement':'promoted-basic','linkedRecordId':None,
            'creditScope':'IFDB作者和开发系统仅保留于来源审计，未建立正式职责。',
            'yearBasis':'IFDB published字段所列作品年；不是档案上传年或条目创建年，原版区域及内容仍待完整编目核对。',
            'editorialScope':'基础身份层，仅作品名、别名与来源原始年份；不生成内容或平台发行记录。','batch':batch}
        for name in names: index[norm(name)].add((work['id'],work['firstYear'],'ifdb-new'))
        for ref in work['sourceRefs']:
            refs[ref].add(work['id'])
            folded[ref.casefold()].add(work['id'])
        selected.append({'work':work,'sourceKind':'ifdb','sourceId':row['tuid'],'intakeOrigin':'live',
            'ifdbPublished':row['published'],'ifdbAuthor':row['author'],'ifdbSystem':row['system'],
            'ifdbLanguage':row['language'],'ifArchiveLinks':row['archiveLinks'],
            'archiveUrl':ARCHIVE_URL,'archiveSha256':ARCHIVE_SHA256,'archivePosition':position,
            'developers':[],'developerClassification':'unknown'})
    if len(selected)!=needed: raise RuntimeError(f'Only {len(selected)} safe IFDB identities for {needed} slots')
    return selected,{'eligibleArchiveCandidates':len(rows),'scanned':scanned,'selected':len(selected),
        'dispositions':dict(counts),'startPosition':start_position,'nextPosition':last_position+1,
        'reusedExisting':reused,'heldForIdentityReview':held}
