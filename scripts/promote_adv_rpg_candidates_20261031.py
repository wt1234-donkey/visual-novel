#!/usr/bin/env python3
"""Promote source-screened ADV/RPG works into the main lightweight work identity layer.

The historical games.json is a strict *fully documented* record store; do not manufacture
characters, publisher/platform releases, variant records or creator credits to satisfy it.
The main registry is an additive primary work identity layer consumed by Works Discovery.
"""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))
index=load("data/adv-rpg-minimal-index-20261031.json")
summary=index["summary"]
assert summary["candidates"]==208
rows=index["records"][:summary["candidates"]]
assert len(rows)==208 and len({r["id"] for r in rows})==208
assert sorted(r["status"] for r in rows).count("new-basic")==48
assert sorted(r["status"] for r in rows).count("main-linked")==57
assert sorted(r["status"] for r in rows).count("dossier-linked")==103
main_ids={w["id"] for w in load("data/games.json")["works"]}
dossier_ids={
    w["id"] for c in load("data/company-coverage.json")["companies"]
    for field in ("relatedGames","dossierOnlyWorks")
    for w in c.get(field,[])
}
HOLD={"Dragon Knight & Graffiti"}
assert len(HOLD & {r["title"] for r in rows})==1
accepted=[]
review=[]
for row in rows:
    assert row["title"] and 1976<=row["year"]<=2026
    assert row["gameplay"] in {"ADV","视觉小说","RPG","SRPG","ARPG","互动电影ADV"}
    assert row["source"].startswith("https://")
    assert row["status"] in {"main-linked","dossier-linked","new-basic"}
    if row["status"]=="main-linked":
        assert row["matchedWorkId"] in main_ids
        layer="existing-complete"
    elif row["status"]=="dossier-linked":
        assert row["matchedWorkId"] in dossier_ids
        layer="promoted-dossier"
    else:
        assert row["matchedWorkId"] is None
        layer="promoted-basic"
    entry={
        "id":row["matchedWorkId"] or row["id"],
        "indexId":row["id"],
        "title":row["title"],
        "aliases":row.get("aliases",[]),
        "firstYear":row["year"],
        "gameplay":row["gameplay"],
        "group":row["group"],
        "source":row["source"],
        "mainPlacement":layer,
        "linkedRecordId":row["matchedWorkId"],
        "creditScope":"Brand/series/source-list association only; never assert developer or publisher without direct evidence.",
        "yearBasis":row.get("yearBasis","Project company list; exact platform/day may require review."),
        "editorialScope":"Title, first release year and dominant ADV/RPG gameplay only. Narrative and production credentials are not yet catalogued.",
    }
    if row["title"] in HOLD:
        review.append({
            **entry,"reason":"PC Engine 1995 Dragon Knight & Graffiti includes an original-game mode; confirm independently added narrative content before treating it as a separate work from Dragon Knight.","reviewType":"edition-versus-work",
            "additionalSource":"https://www.tg-16.com/contributors/dshadoff/Daigirin/Daigirin_1997_06_NEC_Extract.pdf"
        })
        continue
    accepted.append(entry)
assert len(accepted)==207 and len(review)==1
from collections import Counter
counts=Counter(a["mainPlacement"] for a in accepted)
assert counts=={"existing-complete":57,"promoted-dossier":103,"promoted-basic":47}
out={
    "schema":1,
    "updated":"2026-10-31",
    "role":"Primary main catalogue work-identity registry, separate from the complete dossier-only games.json schema.",
    "reviewPolicy":"Record title / first year / dominant gameplay and directly link existing identity; do not fabricate characters, releases, original creators or narrative editorials.",
    "summary":{"candidates":208,"accepted":207,"existingComplete":57,"promotedDossier":103,"promotedBasic":47,"identityReview":1,"addedToMainIdentityLayer":150},
    "works":accepted,
    "identityReview":review
}
dest=ROOT/"data/main-adv-rpg-works-20261031.json"
if dest.exists():
    current=json.loads(dest.read_text(encoding='utf-8'))
    if current.get('nextBatch') or current.get('batches'):
        assert current['works'][:207]==accepted, 'First-batch identities changed; review before rebuilding later batches.'
        assert current['identityReview'][:1]==review
        print('First 208 candidates verified; later reviewed batches preserved.')
        raise SystemExit(0)
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps(out["summary"],ensure_ascii=False))
