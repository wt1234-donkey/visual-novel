#!/usr/bin/env python3
"""Stage reviewed basic identities for future strict games.json promotion.

The basic registry is immediately searchable on the website. Strict games.json
requires an evidenced original content debut and a publisher/platform release.
Never invent those facts merely to inflate the complete-profile counter.
"""
import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/main-adv-rpg-works-20261031.json"
OUTPUT = ROOT / "data/basic-to-full-promotion-review-20261101.json"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def norm(value):
    return "".join(ch for ch in unicodedata.normalize("NFKC", str(value or "")).casefold() if ch.isalnum())

def names(work):
    labels = [work.get("title"), work.get("originalTitle"), work.get("chineseTitle"),
              *(work.get("titleAliases") or []), *(work.get("aliases") or [])]
    return sorted({norm(x) for x in labels if norm(x)})

def build_index():
    index = defaultdict(list)
    main = load(ROOT / "data/games.json")
    supplement = load(ROOT / "data/non-rpg-creator-supplement-20261030.json")
    coverage = load(ROOT / "data/company-coverage.json")
    for scope, items in (("complete", main["works"]), ("supplement", supplement["works"])):
        for item in items:
            for key in names(item):
                index[key].append({"id": item["id"], "year": item["firstYear"], "scope": scope})
    for company in coverage["companies"]:
        for field in ("relatedGames", "dossierOnlyWorks"):
            for item in company.get(field, []):
                for key in names(item):
                    index[key].append({"id": item["id"], "year": item["firstYear"], "scope": "dossier"})
    return index

def stage(offset, limit):
    registry = load(REGISTRY)
    index = build_index()
    seen_refs = set()
    eligible, linked, held = [], [], []
    for item in registry["works"]:
        if item.get("mainPlacement") != "promoted-basic":
            continue
        refs = [str(r) for r in item.get("sourceRefs", [])]
        if any(r in seen_refs for r in refs):
            held.append({"id": item["id"], "reason": "duplicate external identity within basic registry"})
            continue
        seen_refs.update(refs)
        matches = {(m["id"], m["year"], m["scope"]) for key in names(item) for m in index.get(key, [])}
        if matches:
            matches_list = [{"workId": x[0], "year": x[1], "scope": x[2]} for x in sorted(matches)]
            destination = linked if len({x[0] for x in matches}) == 1 and all(x[1] == item["firstYear"] for x in matches) else held
            destination.append({"id": item["id"], "title": item["title"], "firstYear": item["firstYear"],
                                "matched": matches_list, "reason": "existing identity" if destination is linked else "identity/year conflict"})
            continue
        if not re.match(r"^https://", item.get("source") or "") or not 1976 <= item.get("firstYear", 0) <= 2026:
            held.append({"id": item.get("id"), "reason": "invalid source or debut year"})
            continue
        eligible.append({
            "registryId": item["id"],
            "indexId": item["indexId"],
            "title": item["title"],
            "aliases": item.get("aliases", []),
            "firstYear": item["firstYear"],
            "source": item["source"],
            "sourceRefs": refs,
            "batch": item.get("batch", "historical"),
            "reviewRequired": ["independent work vs edition", "actual original debut and year",
                               "original release platform", "original publisher attribution",
                               "precise game category and interaction controls"],
            "readyForStrictGamesJson": False
        })
    # Stable ordering: explicit source registry order, no re-sorting on display titles.
    selection = eligible[offset:offset + limit]
    report = {
        "schema": 1,
        "sourceRegistry": str(REGISTRY.relative_to(ROOT)),
        "destination": "data/games.json after the specified original-release evidence is reviewed",
        "reason": "strict 3-layer model cannot legitimately turn a title/year into a fictitious release",
        "summary": {
            "registryAccepted": len(registry["works"]),
            "basicIdentities": sum(w.get("mainPlacement") == "promoted-basic" for w in registry["works"]),
            "stageableBasic": len(eligible),
            "alreadyInMainOrDossier": len(linked),
            "heldConflicts": len(held),
            "offset": offset, "limit": limit, "staged": len(selection)
        },
        "records": selection,
        "linkedExisting": linked,
        "heldForReview": held
    }
    assert len({x["registryId"] for x in selection}) == len(selection)
    assert all(not x["readyForStrictGamesJson"] for x in selection)
    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    assert args.offset >= 0 and 1 <= args.limit <= 500
    result = stage(args.offset, args.limit)
    if args.write:
        OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
