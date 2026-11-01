#!/usr/bin/env python3
"""Append-only VNDB round 22: source title, aliases, identity and debut-year metadata."""
import argparse
import copy
import hashlib
import json
import re
import time
from collections import Counter
from pathlib import Path

import import_basic_r20_r21_20261101 as previous
from import_basic_r20_r21_20261101 import (base_state, existing_batch, get_vndb_page,
    vndb_names, vndb_year, norm, load, save, VNDB_API, REG)
import import_nextmoe_basic_20261101_r2 as common

ROOT = Path(__file__).resolve().parents[1]
BATCH = "vndb-kana-bulk-20261101-r22"
AUDIT = ROOT / "data/vndb-kana-bulk-review-20261101-r22.json"
PROTECTED = ["data/games.json", "data/company-coverage.json", "data/entities.json",
             "data/credits.json", "data/non-rpg-creator-supplement-20261030.json"]

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()

def protected_hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in PROTECTED}

def append_batch(registry, additions, batch_id, source, audit_path, summary, *args):
    summary = {**summary, "priorWorksSha256": digest(registry["works"]),
               "protectedFileHashes": protected_hashes()}
    return previous.append_batch(registry, additions, batch_id, source, audit_path, summary, *args)

def round22(max_new=500, pages=250, delay=1.2):
    registry, index, ids, index_ids, refs = base_state()
    if existing_batch(registry, BATCH, AUDIT):
        return registry
    cursor = "v3968"
    scanned = 0
    counts = Counter()
    additions, records, held = [], [], []
    for page_number in range(1, pages + 1):
        payload = get_vndb_page(cursor)
        rows = payload["results"]
        if not rows:
            break
        for item in rows:
            scanned += 1
            vndb_id = str(item.get("id") or "")
            if not re.fullmatch(r"v\d+", vndb_id):
                counts["invalid-source-id"] += 1
                continue
            cursor = vndb_id
            source_ref = "vndb:" + vndb_id
            if source_ref in refs or "vndb-" + vndb_id in ids:
                counts["existing-source-id"] += 1
                continue
            names = vndb_names(item)
            if not names:
                counts["missing-title"] += 1
                continue
            year = vndb_year(item)
            if year is None:
                counts["missing-year-or-unreleased"] += 1
                continue
            if any(re.search(
                r"(?i)(?:\bdlc\b|\bdemo\b|\btrial\b|\bfan.?disc\b|\bfandisk\b|\bcollection\b|\bbundle\b|体験版|ファンディスク|合集)",
                name,
            ) for name in names):
                counts["derivative-held"] += 1
                held.append({"sourceId": vndb_id, "vndbId": vndb_id, "title": names[0],
                             "reason": "Possible derivative, fan disc, DLC, trial or compilation"})
                continue
            hits = set()
            for name in names:
                hits.update(index.get(norm(name), ()))
            if hits:
                if any(hit[1] == year for hit in hits):
                    counts["existing-work-matched"] += 1
                else:
                    counts["year-or-alias-conflict"] += 1
                    held.append({"sourceId": vndb_id, "vndbId": vndb_id, "title": names[0],
                                 "year": year, "matches": [list(hit) for hit in sorted(hits)[:8]]})
                continue
            work_id = "vndb-" + vndb_id
            index_id = "vndb-20261101-r22-" + vndb_id
            if work_id in ids or index_id in index_ids:
                counts["id-collision"] += 1
                continue
            source_url = "https://vndb.org/" + vndb_id
            work = {
                "id": work_id,
                "indexId": index_id,
                "title": names[0],
                "aliases": names[1:],
                "firstYear": year,
                "gameplay": "视觉小说",
                "group": "创作品牌待核",
                "source": source_url,
                "sourceRefs": [source_ref],
                "mainPlacement": "promoted-basic",
                "linkedRecordId": None,
                "creditScope": "VNDB Kana API 元数据；未断言开发、发行或创作职责。",
                "yearBasis": "VNDB VN-level released 日期；首次发行平台/地区/版次待核。",
                "editorialScope": "基本作品身份；剧情、创作者、玩法细节及版本差异待核。",
                "batch": BATCH,
            }
            additions.append(work)
            records.append({
                "sourceReleased": item["released"], "sourceDevstatus": item.get("devstatus"),
                "id": work_id, "sourceId": vndb_id, "vndbId": vndb_id,
                "title": names[0], "aliases": names[1:], "firstYear": year,
                "source": source_url, "sourceRefs": [source_ref],
            })
            ids.add(work_id)
            index_ids.add(index_id)
            refs.add(source_ref)
            for name in names:
                index[norm(name)].add((work_id, year, "r22"))
            if len(additions) >= max_new:
                break
        print("BATCH_PAGE", page_number, "SCANNED", scanned, "NEW", len(additions), "CURSOR", cursor, flush=True)
        if len(additions) >= max_new or not payload.get("more"):
            break
        time.sleep(delay)
    return append_batch(
        registry, additions, BATCH, VNDB_API, AUDIT,
        {"scanned": scanned, "cursorStart": "v3968", "cursorEnd": cursor, **dict(counts)},
        records, held, "https://api.vndb.org/kana", "https://vndb.org/d17",
    )


def check():
    registry = load(REG)
    audit = load(AUDIT)
    summary = audit["summary"]
    rows = [w for w in registry["works"] if w.get("batch") == BATCH]
    before = summary["before"]
    assert 1 <= len(rows) <= 500
    assert len(rows) == summary["newDistinctWorks"] == len(audit["records"])
    assert len(registry["works"]) == summary["after"] == before + len(rows)
    assert registry["works"][before:] == rows, "Batch must be an appended suffix"
    assert digest(registry["works"][:before]) == summary["priorWorksSha256"]
    assert protected_hashes() == summary["protectedFileHashes"]
    prior = copy.deepcopy(registry)
    prior["works"] = prior["works"][:before]
    index = common.existing_index(prior)
    refs = {ref for w in prior["works"] for ref in w.get("sourceRefs", [])}
    ids = {w["id"] for w in prior["works"]}
    assert len({w["id"] for w in registry["works"]}) == len(registry["works"])
    assert len({w["indexId"] for w in registry["works"]}) == len(registry["works"])
    records = {row["id"]: row for row in audit["records"]}
    for w in rows:
        row = records[w["id"]]
        assert w["id"] not in ids
        assert w["firstYear"] == vndb_year({"released":row["sourceReleased"], "devstatus":row["sourceDevstatus"]})
        assert w["title"] == row["title"] and w["aliases"] == row["aliases"]
        assert w["sourceRefs"] == row["sourceRefs"] == ["vndb:" + row["vndbId"]]
        assert not (set(w["sourceRefs"]) & refs)
        assert w["id"] == "vndb-" + row["vndbId"]
        assert int(row["vndbId"][1:]) > 3968
        assert w["source"] == row["source"] == "https://vndb.org/" + row["vndbId"]
        assert w["mainPlacement"] == "promoted-basic" and w["linkedRecordId"] is None
        for name in [w["title"], *w["aliases"]]:
            key = norm(name)
            assert not index.get(key), "Existing title or alias collision: " + w["id"]
        for name in [w["title"], *w["aliases"]]:
            index[norm(name)].add((w["id"],w["firstYear"],"r22"))
        refs.update(w["sourceRefs"])
        ids.add(w["id"])
    batches = [b for b in registry["batches"] if b["id"] == BATCH]
    assert len(batches) == 1 and batches[0]["summary"]["promoted-basic"] == len(rows)
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert summary["scanned"] == len(rows) + sum(v for k,v in summary.items() if isinstance(v,int) and k not in {"before","after","newDistinctWorks","scanned"})
    print("R22_AUDIT_OK", json.dumps(summary, ensure_ascii=False), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if not args.check:
        assert load(ROOT / "data/vndb-kana-bulk-review-20261101-r20.json")["summary"]["cursorEnd"] == "v3968"
        round22(max_new=500, pages=100, delay=1.5)
    check()

if __name__ == "__main__":
    main()
