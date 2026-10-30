#!/usr/bin/env python3
"""Import prior-message recommended non-RPG narratives without rewriting legacy works.

Existing titles are retained; collision and uncertainty queues stay explicit.
Original content/version records are created only for genuinely new identities.
This script is idempotent and does not introduce unsourced remaster or port versions.
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/non-rpg-recommended-intake-20261030.json"
DB = ROOT / "data/games.json"
TAX = ROOT / "data/taxonomy.json"
RESULT = ROOT / "data/non-rpg-recommended-intake-result-20261030.json"

def norm(value):
    return "".join(ch for ch in unicodedata.normalize("NFKC", value or "").casefold() if ch.isalnum())

data = json.loads(DB.read_text(encoding="utf-8"))
intake = json.loads(SOURCE.read_text(encoding="utf-8"))
taxonomy = json.loads(TAX.read_text(encoding="utf-8"))
identities = {}
for work in data["works"]:
    candidates = [work.get("title"), work.get("originalTitle"), work.get("chineseTitle"), *(work.get("titleAliases") or [])]
    for name in candidates:
        if name:
            identities.setdefault(norm(name), set()).add(work["id"])

counter = max(int(w["id"][1:]) for w in data["works"]) + 1
types = {"Galgame": "恋爱剧情冒险", "视觉小说": "剧情分支／冒险",
         "文字冒险": "图文选项／调查", "互动动画": "全动画·剧情分支"}
added, reused, ambiguous = [], [], []
for item in intake["items"]:
    names = [item.get("originalTitle"), item.get("title"), item.get("chineseTitle"), *(item.get("aliases") or [])]
    keys = {norm(name) for name in names if name}
    matches = set()
    for k in keys:
        matches.update(identities.get(k, set()))
    if len(matches) > 1:
        ambiguous.append({"group": item["group"], "title": item["title"], "matchIds": sorted(matches)})
        continue
    if matches:
        reused.append({"group": item["group"], "title": item["title"], "workId": next(iter(matches))})
        continue
    wid = f"g{counter}"
    counter += 1
    cid, rid = f"{wid}-c-original", f"{wid}-v-original"
    source = item["source"]
    if not source.startswith("https://"):
        raise ValueError(f"Invalid source for {item['title']}")
    category = item["category"]
    if category not in types:
        raise ValueError(f"Invalid category {category}")
    year = item["year"]
    publisher = item["publisher"]
    alias = list(dict.fromkeys(x for x in [item.get("originalTitle"), item.get("title"), *(item.get("aliases") or [])] if x))
    role_note = ("创作关联组：" + item["group"] + "；发行署名：" + publisher
                 + "。不能据发行署名推定开发或个人编剧、原画、音乐职责。"
                 + " 本条为2026-10-30作品身份首批补录，独立叙事来源、确切首发平台和内容差异待复核。")
    note = f"{year}年原作首批内容；具体首发署名与内容版本尚未逐平台终核。"
    work = dict(
        id=wid, title=item["title"], chineseTitle=item.get("chineseTitle", ""),
        chineseTitleType=("通行译名" if item.get("chineseTitle") else ""),
        originalTitle=item["originalTitle"], titleAliases=alias, firstYear=year,
        category=category, subcategory=types[category],
        genre=("非RPG叙事游戏／" + category + "（独立题材待编）"),
        characters=["叙事主体（角色姓名未编目）"],
        charactersNote="未把角色身份占位视作已核实姓名；完整角色名单需要作品专属出处。",
        synopsis=item["synopsis"], notes=role_note, source=source,
        interactionModes=item.get("interactionModes") or ["待核实"],
        interactionNote="具体交互操作需逐作品查说明书或实机；不从题材和ADV分类推定互动方式。",
        interactionBasis="既有资料归纳", interactionSources=[source]
    )
    company = taxonomy["publisherAliases"].get(publisher, publisher)
    rel = dict(id=rid, workId=wid, year=year, platform=item["platform"], publisher=publisher,
               publisherCompanies=[company], kind="原作／首次内容发行", voice="未核实",
               differences=note, source=source, contentVersionId=cid,
               contentRelation="original", contentNote="仅建原作内容身份；内容增强与纯移植待分别核查。",
               releaseRole="contentDebut")
    content = dict(id=cid, workId=wid, label="原作／首批内容", firstYear=year,
                   basis="original", evidence=note, source=source,
                   evidenceReleaseIds=[rid], addedContent=[])
    data["works"].append(work)
    data["platformReleases"].append(rel)
    data["contentVersions"].append(content)
    for key in keys:
        identities.setdefault(key, set()).add(wid)
    added.append({"group": item["group"], "title": item["title"], "workId": wid})
data["meta"]["updated"] = "2026-10-30"
DB.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
result = {
    "batch": intake["batch"], "candidateCount": len(intake["items"]),
    "added": added, "reused": reused, "ambiguous": ambiguous,
    "reviewQueue": intake["reviewQueue"],
    "disclaimer": "Unverified creator credits, first-publication publishers, interaction labels and narrative metadata remain pending; no post-original content versions invented."
}
RESULT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Recommended non-RPG narrative intake: {len(added)} new, {len(reused)} reused, {len(ambiguous)} ambiguous")
