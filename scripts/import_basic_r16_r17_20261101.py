#!/usr/bin/env python3
"""Append-only rounds 16-17. R16 resumes VNDB after v1296; R17 resumes NextMoe after page 79."""
import json,re,time,argparse,datetime as dt
from collections import Counter
from pathlib import Path
import import_nextmoe_basic_20261101_r2 as common

ROOT=Path(__file__).resolve().parents[1]
REG=common.REGISTRY
CUTOFF=dt.date(2026,11,1)
R16="vndb-kana-bulk-20261101-r16"; A16=ROOT/"data/vndb-kana-bulk-review-20261101-r16.json"
R17="nextmoe-galgame-bulk-20261101-r17"; A17=ROOT/"data/nextmoe-bulk-review-20261101-r17.json"

def load(p): return json.loads(Path(p).read_text(encoding="utf-8"))
def save(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
def norm(s): return common.norm(s)
def vndb_names(x):
    out=[]
    for s in [x.get("title"),x.get("alttitle"),*(x.get("aliases") or [])]:
        if isinstance(s,str) and len(norm(s))>=3 and s.strip() not in out: out.append(s.strip())
    return out
def vndb_year(x):
    d=x.get("released")
    if x.get("devstatus") not in (None,0) or not isinstance(d,str) or not re.fullmatch(r"\d{4}(?:-\d{2}){0,2}",d): return None
    y=int(d[:4])
    if y<1976 or y>2026:return None
    try:
        if len(d)==10 and dt.date.fromisoformat(d)>CUTOFF:return None
        if len(d)==7 and y==2026 and int(d[5:7])>11:return None
    except ValueError:return None
    return y

def base_state():
    reg=load(REG); idx=common.existing_index(reg)
    ids={w["id"] for w in reg["works"]}; iids={w["indexId"] for w in reg["works"]}
    refs={r for w in reg["works"] for r in w.get("sourceRefs",[])}
    return reg,idx,ids,iids,refs

def append(reg, additions, batch, source, audit_path, summary, records, held):
    if not additions: raise RuntimeError(batch+" produced zero new identities; refusing empty batch")
    reg["works"].extend(additions)
    n=len(additions)
    for k in ("candidates","accepted","promotedBasic","addedToMainIdentityLayer"):reg["summary"][k]+=n
    reg["updated"]="2026-11-01"
    reg["batches"].append({"id":batch,"source":source,"review":str(audit_path.relative_to(ROOT)),
                           "summary":{"candidates":n,"promoted-basic":n,**summary}})
    assert reg["summary"]["accepted"]==len(reg["works"])
    audit={"schema":1,"date":"2026-11-01","source":source,"summary":{"newDistinctWorks":n,"before":len(reg["works"])-n,"after":len(reg["works"]),**summary},
           "records":records,"heldForIdentityReview":held,
           "caveats":["Basic identity only: title, aliases, source ID and source year; not a quality recommendation.",
                      "No platform edition, content-version or creator attribution asserted.",
                      "Conflicts and dependent editions are held, not forced into the registry."]}
    save(REG,reg);save(audit_path,audit)
    print(batch,"NEW",n,"TOTAL",len(reg["works"]),flush=True)

def round16(max_new=500,pages=250,delay=1.2):
    reg,idx,ids,iids,refs=base_state()
    if any(b["id"]==R16 for b in reg["batches"]):
        assert A16.exists() and len([w for w in reg["works"] if w.get("batch")==R16])==load(A16)["summary"]["newDistinctWorks"]
        print("SKIP",R16,flush=True);return reg
    cursor="v1296"; scanned=0; counts=Counter(); additions=[]; held=[]; records=[]
    for pg in range(pages):
        req={"fields":"title,alttitle,aliases,released,devstatus","results":100,"sort":"id","reverse":False,
             "filters":["id",">",cursor]}
        payload=common.post_vndb(req) if hasattr(common,"post_vndb") else None
        if payload is None:
            import urllib.request
            raw=json.dumps(req).encode()
            q=urllib.request.Request("https://api.vndb.org/kana/vn",data=raw,headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"NarrativeCatalogueResearch/1.0"})
            with urllib.request.urlopen(q,timeout=35) as z: payload=json.load(z)
        rows=payload.get("results",[])
        if not rows:break
        for x in rows:
            scanned+=1; vid=x.get("id","")
            if not re.fullmatch(r"v\d+",vid):counts["invalid-id"]+=1;continue
            cursor=vid; ref="vndb:"+vid
            if ref in refs:counts["existing-external-id"]+=1;continue
            year=vndb_year(x); names=vndb_names(x)
            if not names:counts["missing-title"]+=1;continue
            if year is None:counts["missing-year-or-unreleased"]+=1;continue
            if any(re.search(r"(?i)(\bdlc\b|\bdemo\b|\btrial\b|\bfan.?disc\b|\bfandisk\b|\bcollection\b|\bbundle\b|体験版|ファンディスク|合集)",n) for n in names):
                counts["derivative-held"]+=1;held.append({"id":vid,"title":names[0],"reason":"Possible derivative/edition"});continue
            hits=set()
            for n in names:hits.update(idx.get(norm(n),()))
            if hits:
                if any(h[1]==year for h in hits):counts["existing-work-matched"]+=1
                else:counts["year-or-alias-conflict"]+=1;held.append({"id":vid,"title":names[0],"year":year,"matches":[list(h) for h in list(hits)[:8]]})
                continue
            wid="vndb-"+vid;iid="vndb-20261101-r16-"+vid
            if wid in ids or iid in iids:counts["id-collision"]+=1;continue
            w={"id":wid,"indexId":iid,"title":names[0],"aliases":names[1:18],"firstYear":year,
               "gameplay":"视觉小说","group":"创作品牌待核","source":"https://vndb.org/"+vid,
               "sourceRefs":[ref],"mainPlacement":"promoted-basic","linkedRecordId":None,
               "creditScope":"VNDB Kana API 元数据；未断言开发、发行或创作职责。",
               "yearBasis":"VNDB VN-level released 日期；首次发行平台/版次待核。",
               "editorialScope":"基本作品身份；剧情、创作者、玩法细节及版本差异待核。","batch":R16}
            additions.append(w);records.append({"id":wid,"title":names[0],"aliases":names[1:18],"firstYear":year,"source":w["source"],"sourceRefs":[ref]})
            ids.add(wid);iids.add(iid);refs.add(ref)
            for n in names:idx[norm(n)].add((wid,year,"r16"))
            if len(additions)>=max_new:break
        print("R16_PAGE",pg+1,"SCANNED",scanned,"NEW",len(additions),"CURSOR",cursor,flush=True)
        if len(additions)>=max_new or not payload.get("more"):break
        time.sleep(delay)
    append(reg,additions,R16,"https://api.vndb.org/kana/vn",A16,{"scanned":scanned,"cursorStart":"v1296","cursorEnd":cursor,**dict(counts)},records,held)
    return load(REG)

def round17(max_new=500,start_page=80,pages=100,delay=1.2):
    reg,idx,ids,iids,refs=base_state()
    if any(b["id"]==R17 for b in reg["batches"]):
        assert A17.exists() and len([w for w in reg["works"] if w.get("batch")==R17])==load(A17)["summary"]["newDistinctWorks"]
        print("SKIP",R17,flush=True);return reg
    additions=[];records=[];held=[];counts=Counter();scanned=0
    for page in range(start_page,start_page+pages):
        payload=common.get_page(page,100)
        rows=payload["items"]
        if not rows:break
        for item in rows:
            scanned+=1
            if item.get("medium")!="galgame":counts["other-medium"]+=1;continue
            vid=common.has_vndb_identity(item)
            if not vid:counts["no-vndb-identity-held"]+=1;continue
            sid=str(item.get("id") or "")
            if not sid.isdecimal():counts["invalid-source-id"]+=1;continue
            if "nextmoe:"+sid in refs or "vndb:"+vid in refs:counts["existing-external-id"]+=1;continue
            year=common.date_year(item);names=common.source_names(item)
            if year is None:counts["missing-year"]+=1;continue
            if not names:counts["missing-title"]+=1;continue
            if sid in common.HELD_EDITION_IDS or common.is_non_work_pack(names[0]) or any(re.search(r"(?i)(fan.?disc|\bFD\b|\bbundle\b|\bcollection\b|remaster|リマスター|合集)",n) for n in names):
                counts["edition-held"]+=1;held.append({"id":sid,"title":names[0],"reason":"Possible edition, DLC or collection"});continue
            hits=set()
            for n in names:hits.update(idx.get(norm(n),()))
            if hits:
                if any(h[1]==year for h in hits):counts["existing-work-matched"]+=1
                else:counts["year-or-alias-conflict"]+=1;held.append({"id":sid,"title":names[0],"year":year,"matches":[list(h) for h in list(hits)[:8]]})
                continue
            wid="nextmoe-"+sid;iid="nextmoe-20261101-r17-"+sid
            if wid in ids or iid in iids:counts["id-collision"]+=1;continue
            w={"id":wid,"indexId":iid,"title":names[0],"aliases":names[1:18],"firstYear":year,
               "gameplay":"Galgame（玩法待核）","group":"创作品牌待核",
               "source":"https://api.nextmoe.dev/v2/catalog/works/"+sid,"sourceRefs":["vndb:"+vid],
               "mainPlacement":"promoted-basic","linkedRecordId":None,
               "creditScope":"NextMoe v2 Galgame 目录来源；未断言创作或发行职责。",
               "yearBasis":"NextMoe release_date 年份；首次发行地区/版次待核。",
               "editorialScope":"基础作品身份；剧情、创作者、详细玩法及内容版本待核。","batch":R17}
            additions.append(w);records.append({"id":wid,"title":names[0],"aliases":names[1:18],"firstYear":year,"source":w["source"],"sourceRefs":w["sourceRefs"]})
            ids.add(wid);iids.add(iid);refs.add("vndb:"+vid)
            for n in names:idx[norm(n)].add((wid,year,"r17"))
            if len(additions)>=max_new:break
        print("R17_PAGE",page,"SCANNED",scanned,"NEW",len(additions),flush=True)
        if len(additions)>=max_new or scanned>=payload.get("total",10**9):break
        time.sleep(delay)
    append(reg,additions,R17,"https://api.nextmoe.dev/v2/catalog/works",A17,{"scanned":scanned,"startPage":start_page,"endPage":page,**dict(counts)},records,held)
    return load(REG)

def main():
    p=argparse.ArgumentParser();p.add_argument("--max-new",type=int,default=500);p.add_argument("--vndb-pages",type=int,default=250);p.add_argument("--nextmoe-start-page",type=int,default=80);p.add_argument("--nextmoe-pages",type=int,default=100);p.add_argument("--delay",type=float,default=1.2);a=p.parse_args()
    assert 1<=a.max_new<=500 and a.nextmoe_start_page>=1 and a.delay>=1
    x=round16(a.max_new,a.vndb_pages,a.delay);print("AFTER_R16",len(x["works"]),flush=True)
    x=round17(a.max_new,a.nextmoe_start_page,a.nextmoe_pages,a.delay);print("AFTER_R17",len(x["works"]),flush=True)
if __name__=="__main__":main()
