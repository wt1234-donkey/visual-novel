#!/usr/bin/env python3
"""Rounds 14/15: extend basic narrative-game identities from NextMoe + VNDB Kana.

Only name/aliases/first year/source; never fabricate games.json provenance or
content versions. Every round is append-only and has its own reproducible audit.
"""
import argparse
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

import import_nextmoe_basic_20261101_r2 as common

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = common.REGISTRY
API = "https://api.vndb.org/kana/vn"
BATCH15 = "vndb-kana-bulk-20261101-r15"
AUDIT15 = ROOT / "data/vndb-kana-bulk-review-20261101-r15.json"
CUTOFF = dt.date(2026, 11, 1)
NON_INDEPENDENT = re.compile(
    r"(?i)(?:\bdlc\b|\bdemo\b|\btrial\b|\bpatch\b|\bfan.?disc\b|"
    r"\bfandisk\b|\bremaster(?:ed)?\b|\bcollection\b|\bbundle\b|"
    r"体験版|体验版|試玩版|试玩版|ファンディスク|修正パッチ|追加パック|合集|"
    r"サウンドトラック|soundtrack)"
)


def get_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def existing_batch(registry, batch_id, audit_path):
    matches = [b for b in registry.get("batches", []) if b["id"] == batch_id]
    if not matches:
        return False
    if len(matches) != 1 or not audit_path.exists():
        raise RuntimeError("Existing batch has missing audit or duplicate batch marker")
    audit = get_json(audit_path)
    expected = matches[0]["summary"]["promoted-basic"]
    assert audit["summary"]["newDistinctWorks"] == expected
    assert sum(w.get("batch") == batch_id for w in registry["works"]) == expected
    print("SKIP_EXISTING", batch_id, expected, flush=True)
    return True


def get_vndb_page(cursor, retry=4):
    # Keyset pagination: no 100-page ceiling and no offset drift.
    query = {"fields": "title,alttitle,aliases,released,devstatus",
             "results": 100, "sort": "id", "reverse": False}
    if cursor is not None:
        query["filters"] = ["id", ">", cursor]
    raw = json.dumps(query).encode("utf-8")
    request = urllib.request.Request(
        API, data=raw, method="POST",
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "User-Agent": "NarrativeCatalogueResearch/1.0 (wt1234-donkey/visual-novel; metadata only)"})
    for attempt in range(retry):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.load(response)
            if not isinstance(payload.get("results"), list) or not isinstance(payload.get("more"), bool):
                raise RuntimeError("VNDB API response shape changed")
            return payload
        except urllib.error.HTTPError as e:
            if e.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            wait = max(5, int(e.headers.get("Retry-After") or 0), (attempt + 1) * 6)
            print("VNDB retry", e.code, wait, flush=True)
            time.sleep(min(wait, 90))
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry - 1:
                raise
            time.sleep((attempt + 1) * 7)


def all_names(item):
    raw = [item.get("title"), item.get("alttitle")]
    raw.extend(item.get("aliases") or [])
    out, seen = [], set()
    for s in raw:
        if not isinstance(s, str):
            continue
        s = s.strip()
        k = common.norm(s)
        if len(k) < 3 or len(s) > 160 or k in seen:
            continue
        seen.add(k)
        out.append(s)
    return out


def original_year(item):
    if item.get("devstatus") not in (None, 0):
        return None
    date = item.get("released")
    if not isinstance(date, str) or not re.match(r"^\d{4}(?:-\d{2}){0,2}$", date):
        return None
    year = int(date[:4])
    if year < 1976 or year > CUTOFF.year:
        return None
    try:
        if len(date) == 10 and dt.date.fromisoformat(date) > CUTOFF:
            return None
        if len(date) == 7 and year == CUTOFF.year and int(date[5:7]) > CUTOFF.month:
            return None
    except ValueError:
        return None
    return year


def import_round_14(args):
    common.BATCH = "nextmoe-galgame-bulk-20261101-r14"
    common.AUDIT = ROOT / "data/nextmoe-bulk-review-20261101-r14.json"
    common.INDEX_PREFIX = "nextmoe-20261101-r14-"
    registry = get_json(REGISTRY)
    if not existing_batch(registry, common.BATCH, common.AUDIT):
        common.run(argparse.Namespace(pages=args.nextmoe_pages, limit=100,
                                      max_new=args.max_new, delay=args.delay, dry_run=False))
    return get_json(REGISTRY)


def import_round_15(args):
    registry = get_json(REGISTRY)
    if existing_batch(registry, BATCH15, AUDIT15):
        return registry
    before = len(registry["works"])
    if not any(b["id"] == common.BATCH for b in registry["batches"]):
        raise RuntimeError("Round 14 missing: refusing out-of-order import")
    indexed = common.existing_index(registry)
    existing_vndb = {x for w in registry["works"] for x in w.get("sourceRefs", [])
                     if isinstance(x, str) and x.startswith("vndb:v")}
    used_ids = {w["id"] for w in registry["works"]}
    used_index = {w["indexId"] for w in registry["works"]}
    additions, held, counts = [], [], Counter()
    cursor, seen_cursors = None, set()
    for page in range(1, args.vndb_pages + 1):
        payload = get_vndb_page(cursor)
        items = payload["results"]
        if not items:
            break
        last_id = items[-1].get("id")
        if not isinstance(last_id, str) or not re.fullmatch(r"v\d+", last_id):
            raise RuntimeError("VNDB returned invalid cursor")
        if last_id in seen_cursors or last_id == cursor:
            raise RuntimeError("VNDB cursor stopped advancing")
        seen_cursors.add(last_id)
        cursor = last_id
        for item in items:
            counts["scanned"] += 1
            vid = str(item.get("id") or "")
            if not re.fullmatch(r"v\d+", vid):
                counts["invalid-id"] += 1
                continue
            ref = "vndb:" + vid
            if ref in existing_vndb:
                counts["existing-external-id"] += 1
                continue
            year = original_year(item)
            if year is None:
                counts["missing-unreleased-or-future-year"] += 1
                continue
            names = all_names(item)
            if not names:
                counts["missing-title"] += 1
                continue
            if any(NON_INDEPENDENT.search(n) for n in names):
                counts["edition-or-pack-held"] += 1
                if len(held) < 1000:
                    held.append({"id": vid, "title": names[0], "reviewReason": "Possible derivative, DLC, demo or collection"})
                continue
            collisions = set()
            for name in names:
                collisions.update(indexed.get(common.norm(name), ()))
            if collisions:
                if any(c[1] == year for c in collisions):
                    counts["existing-work-matched"] += 1
                else:
                    counts["year-or-alias-conflict"] += 1
                    if len(held) < 1000:
                        held.append({"id": vid, "title": names[0], "year": year,
                                     "matches": sorted(collisions)[:8]})
                continue
            wid, iid = "vndb-" + vid, "vndb-20261101-r15-" + vid
            if wid in used_ids or iid in used_index:
                raise RuntimeError("Generated identity collision")
            work = {
                "id": wid, "indexId": iid, "title": names[0],
                "aliases": names[1:18], "firstYear": year,
                "gameplay": "视觉小说", "group": "创作品牌待核",
                "source": "https://vndb.org/" + vid, "sourceRefs": [ref],
                "mainPlacement": "promoted-basic", "linkedRecordId": None,
                "creditScope": "VNDB 官方 Kana API 原作元数据；未断言开发、发行、创作职责。",
                "yearBasis": "VNDB VN-level released 日期；可能仅精确到年份/月，具体首次发行待独立核实。",
                "editorialScope": "基本作品身份，不等于品质推荐；发行平台、剧情、创作者、内容版本待核。",
                "batch": BATCH15}
            additions.append(work)
            existing_vndb.add(ref)
            used_ids.add(wid)
            used_index.add(iid)
            for n in names:
                indexed[common.norm(n)].add((wid, year, "current-import"))
            if len(additions) >= args.max_new:
                break
        print("VNDB_PAGE", page, "SCAN", counts["scanned"], "ADDED", len(additions), flush=True)
        if len(additions) >= args.max_new or not payload["more"]:
            break
        time.sleep(args.delay)
    if not additions:
        raise RuntimeError("No new eligible VNDB independent work identities; no silent empty batch")
    registry["works"].extend(additions)
    inc = len(additions)
    for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
        registry["summary"][key] += inc
    registry["updated"] = "2026-11-01"
    registry["batches"].append({
        "id": BATCH15, "source": API,
        "review": str(AUDIT15.relative_to(ROOT)),
        "summary": {"candidates": inc, "scanned": counts["scanned"],
                    **dict(counts), "promoted-basic": inc,
                    "year-or-alias-conflict-held": len(held)}})
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert registry["summary"]["addedToMainIdentityLayer"] == registry["summary"]["promotedBasic"] + registry["summary"]["promotedDossier"]
    audit = {
        "schema": 1, "date": "2026-11-01", "source": API,
        "sourceDocs": "https://api.vndb.org/kana",
        "sourceLicense": "https://vndb.org/d17",
        "scope": "VNDB visual novels, original name/alias/year and vndb id only; no claims about creators or versions",
        "request": {"sort": "id", "pageSize": 100,
                    "pageCountCap": args.vndb_pages, "limitNew": args.max_new},
        "summary": {"scanned": counts["scanned"], "newDistinctWorks": inc,
                    "before": before, "after": len(registry["works"]), **dict(counts)},
        "records": [{"id": w["id"], "title": w["title"], "aliases": w["aliases"],
                     "firstYear": w["firstYear"], "source": w["source"], "sourceRefs": w["sourceRefs"]} for w in additions],
        "heldForIdentityReview": held,
        "caveats": ["Source is VNDB Kana API, not NextMoe: source identity preserved.",
                    "Source license and attribution must be respected (VNDB Data License).",
                    "VN-level released can be less precise than first platform launch.",
                    "Editions, fan discs, same-title conflicts and source-year discrepancies are not forced in.",
                    "This is a lightweight foundation, not a curated story quality assessment."]}
    write_json(REGISTRY, registry)
    write_json(AUDIT15, audit)
    print("ROUND15_NEW", inc, "FINAL", len(registry["works"]), flush=True)
    return registry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nextmoe-pages", type=int, default=100)
    parser.add_argument("--vndb-pages", type=int, default=250)
    parser.add_argument("--max-new", type=int, default=500)
    parser.add_argument("--delay", type=float, default=1.2)
    args = parser.parse_args()
    assert 1 <= args.nextmoe_pages <= 100
    assert 1 <= args.vndb_pages <= 400
    assert 1 <= args.max_new <= 500
    assert args.delay >= 1
    first = import_round_14(args)
    print("ROUND14_TOTAL", len(first["works"]), flush=True)
    final = import_round_15(args)
    for number, batchid in ((14, common.BATCH), (15, BATCH15)):
        b = next(b for b in final["batches"] if b["id"] == batchid)
        print("ROUND", number, "ADDED", b["summary"]["promoted-basic"], flush=True)
    print("FINAL_BASIC_COUNT", len(final["works"]), flush=True)


if __name__ == "__main__":
    main()
