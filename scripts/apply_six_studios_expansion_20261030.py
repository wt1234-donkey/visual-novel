#!/usr/bin/env python3
"""Apply non-RPG narrative catalogue expansion for six studios.

Idempotent: original work identity is reused if an exact normalized title exists.
Never edits historical works; never fabricates a new-content later edition.
"""
import json
import re
import unicodedata
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"data/non-rpg-six-studios-expansion-20261030.json"
DB=ROOT/"data/games.json"
TAX=ROOT/"data/taxonomy.json"
data=json.loads(DB.read_text(encoding="utf-8"))
intake=json.loads(SOURCE.read_text(encoding="utf-8"))
taxonomy=json.loads(TAX.read_text(encoding="utf-8"))
def norm(s):
    s=unicodedata.normalize("NFKC",s or "").casefold()
    return "".join(c for c in s if c.isalnum())
identities={}
for w in data["works"]:
    for v in [w["title"],w["originalTitle"],w.get("chineseTitle",""),*w.get("titleAliases",[])]:
        if v:
            identities.setdefault(norm(v),w["id"])
existing_ids={w["id"] for w in data["works"]}
counter=max(int(w["id"][1:]) for w in data["works"])+1
types={"Galgame":"恋爱剧情冒险","视觉小说":"剧情分支／冒险","文字冒险":"图文选项／调查","互动动画":"全动画·剧情分支"}
added=[]
reused=[]
for row in intake["items"]:
    original=row["originalTitle"]
    keys=[norm(original),norm(row["title"])]
    found={identities[k] for k in keys if k in identities}
    if len(found)>1:
        raise ValueError(f"Ambiguous identity: {row['title']} {sorted(found)}")
    if found:
        reused.append({"workId":next(iter(found)),"group":row["group"],"title":row["title"]})
        continue
    wid=f"g{counter}";counter+=1
    cid=f"{wid}-c-original";rid=f"{wid}-v-original"
    source=row["source"]
    if not source.startswith("https://"):
        raise ValueError("Missing scoped source: "+row["group"])
    genre={
        "Galgame":"角色关系／剧情分支冒险",
        "视觉小说":"故事阅读／角色抉择",
        "文字冒险":"场景调查／对话推理冒险",
        "互动动画":"多路线／互动电影"
    }[row["category"]]
    modes={
        "Galgame":["阅读推进","选项分支"],
        "视觉小说":["阅读推进","选项分支"],
        "文字冒险":["菜单指令","点击调查"],
        "互动动画":["选项分支","限时反应","直接移动"]
    }[row["category"]]
    if row["group"]=="free":
        modes=["阅读推进","直接移动"]
    if row["group"]=="inkle":
        modes=["阅读推进","选项分支","菜单指令"]
    if row["group"]=="red":
        modes=["直接移动","点击调查","谜题操作"]
    if row["group"]=="grass":
        modes=["阅读推进","菜单指令","谜题操作"]
    modes=row.get("interactionModes", ["待核实"])
    note=f"{row['year']}年首批内容暂存记录；首发署名与具体内容仍需进一步核实。"
    characters=row.get("characters") or ["原作叙事主体（姓名待编）"]
    w=dict(id=wid,title=row["title"],chineseTitle=row["title"],chineseTitleType="通行译名",
       originalTitle=original,titleAliases=[original],firstYear=row["year"],
       category=row["category"],subcategory=types[row["category"]],genre="叙事型ADV／视觉小说（题材待编）",
       characters=characters,charactersNote="主要人物姓名与角色关系尚未采编；所示主体为数据占位，不代表具名角色。",
       synopsis=row["synopsis"],
       notes=f"2026-10-30六组品牌非RPG补录；候选创作品牌：{row['group']}。年份取自具名品牌或第三方作品目录，制作、发行及个人职责仍待终核。中文名以原名暂代，并非确定的通行译名。",
       source=source,interactionModes=modes,
       interactionNote="作品为叙事类候选；交互方式暂未依原说明书或实机逐条核实。",
       interactionBasis="待核实",interactionSources=[source])
    publisher=row["publisher"]
    companies=taxonomy["publisherAliases"].get(publisher,publisher)
    v=dict(id=rid,workId=wid,year=row["year"],platform=row["platform"],publisher=publisher,
       publisherCompanies=[companies],kind="原作／首次内容发行",voice="未核实",
       differences=note,source=source,contentVersionId=cid,contentRelation="original",
       contentNote="原作内容首批发行；后续增强及移植均不在本次凭推测增加。",releaseRole="contentDebut")
    c=dict(id=cid,workId=wid,label="原作／首批内容",firstYear=row["year"],
        basis="original",evidence=note,source=source,evidenceReleaseIds=[rid],addedContent=[])
    data["works"].append(w)
    data["platformReleases"].append(v)
    data["contentVersions"].append(c)
    identities[norm(original)]=wid
    identities[norm(row["title"])]=wid
    added.append({"workId":wid,"group":row["group"],"title":row["title"]})
data["meta"]["updated"]="2026-10-30"
DB.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
out={"date":"2026-10-30","added":added,"reused":reused,"excluded":intake["reviewQueue"],
     "reviewNote":"Studio/developer and individual creative credits are not fabricated from publisher fields; pending evidence-scoped verification."}
(ROOT/"data/non-rpg-six-studios-expansion-result-20261030.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Six-brand expansion: {len(added)} new, {len(reused)} reused")
