#!/usr/bin/env python3
"""Import only distinct story-game names and original debut years from NextMoe.

Uses the publicly documented anonymous list API, not resource/download counts.
Does not touch games.json, content versions, editions or creator credits.
The script is intentionally conservative: uncertain aliases and years go to audit.
"""
import argparse
import datetime as dt
import json
import os
import re
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/main-adv-rpg-works-20261031.json"
AUDIT = ROOT / "data/nextmoe-bulk-review-20261031.json"
API = "https://api.nextmoe.dev/v2/catalog/works"
BATCH = "nextmoe-galgame-bulk-20261031"
CUTOFF = dt.date(2026, 10, 31)

def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))

def norm(value):
    return "".join(c for c in unicodedata.normalize("NFKC", str(value or "")).casefold() if c.isalnum())

def text_value(value):
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("name", "title", "text", "value", "display_name"):
            if isinstance(value.get(key), str) and value[key].strip():
                return value[key].strip()
    return ""

def names(record):
    result = [record.get("title"), record.get("originalTitle"), record.get("chineseTitle")]
    result += record.get("titleAliases") or []
    result += record.get("aliases") or []
    return [v for v in result if isinstance(v, str) and len(norm(v)) >= 3]

def source_names(work):
    candidates = [work.get("display_name"), work.get("latin")]
    local = work.get("localized") or {}
    if isinstance(local, dict):
        candidates += [text_value(v) for v in local.values()]
    for title in work.get("titles") or []:
        candidates.append(text_value(title))
    out, seen = [], set()
    for value in candidates:
        value = text_value(value)
        key = norm(value)
        if len(key) < 3 or len(value) > 160 or key in seen:
            continue
        seen.add(key)
        out.append(value)
    return out

def has_vndb_identity(record):
    # VNDB is a stronger independent visual-novel identity signal than the
    # broad galgame medium (which also covers DLC, clickers, and action games).
    for ref in record.get("refs") or []:
        if not isinstance(ref, dict):
            continue
        source = str(ref.get("source") or "").strip().lower()
        rid = str(ref.get("external_id") or ref.get("ref_id") or ref.get("value") or "")
        if source == "vndb" and re.fullmatch(r"v\d+", rid):
            return rid
    return None

def is_non_work_pack(title):
    return bool(re.search(r"(?i)(?:DLC\d*|体験版|体验版|試玩版|试玩版|\bdemo\b|\btrial\b|\bappend\b|無料版|免费版|\bpatch\b|追加パック|追加コンテンツ|修正パッチ|サントラ|soundtrack)", title))

def date_year(record):
    if record.get("release_status") != "released":
        return None
    raw = record.get("release_date")
    if not isinstance(raw, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return None
    try:
        release = dt.date.fromisoformat(raw)
    except ValueError:
        return None
    if release > CUTOFF or release.year < 1976:
        return None
    return release.year

def get_page(page, limit, retry=4):
    params = urllib.parse.urlencode({
        "page": page, "limit": limit, "sort": "rating_vndb",
        "nsfw": "true", "include": "titles,refs"
    })
    request = urllib.request.Request(
        API + "?" + params,
        headers={"User-Agent": "NarrativeCatalogueImport/1.0 (public metadata; wt1234-donkey/visual-novel)",
                 "Accept": "application/json"}
    )
    for attempt in range(retry):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("object") != "list" or not isinstance(payload.get("items"), list):
                raise RuntimeError("unexpected NextMoe API response shape")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            wait = min(90, max(3, int(exc.headers.get("Retry-After") or 0), (attempt + 1) * 8))
            print(f"API HTTP {exc.code}, retry after {wait}s", flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry - 1:
                raise
            time.sleep((attempt + 1) * 6)

def existing_index(registry):
    indexed = defaultdict(set)
    main = load("data/games.json")
    extra = load("data/non-rpg-creator-supplement-20261030.json")
    coverage = load("data/company-coverage.json")
    def add(work, scope):
        year = int(work.get("firstYear") or work.get("year") or 0)
        for name in names(work):
            indexed[norm(name)].add((str(work.get("id")), year, scope))
    for work in main["works"]:
        add(work, "complete")
    for work in extra.get("works", []):
        add(work, "supplement")
    for group in coverage.get("companies", []):
        for collection in ("relatedGames", "dossierOnlyWorks"):
            for work in group.get(collection, []):
                add(work, "historical-dossier")
    for work in registry["works"]:
        add(work, "identity-registry")
    return indexed

def run(args):
    registry = load("data/main-adv-rpg-works-20261031.json")
    # Replace this tentative source batch instead of compounding old imports.
    previous = [w for w in registry["works"] if w.get("batch") == BATCH]
    if previous:
        registry["works"] = [w for w in registry["works"] if w.get("batch") != BATCH]
        for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
            registry["summary"][key] -= len(previous)
        registry["batches"] = [b for b in registry["batches"] if b.get("id") != BATCH]
    before = len(registry["works"])
    existing = existing_index(registry)
    taken_ids = {str(w["id"]) for w in registry["works"]}
    taken_index_ids = {str(w["indexId"]) for w in registry["works"]}
    scanned, counts, additions, held = 0, Counter(), [], []
    seen_upstream = set()
    for page in range(1, args.pages + 1):
        payload = get_page(page, args.limit)
        rows = payload["items"]
        if not rows:
            break
        for item in rows:
            scanned += 1
            if item.get("medium") != "galgame":
                counts["other-medium"] += 1
                continue
            counts["galgame"] += 1
            vndb_id = has_vndb_identity(item)
            if not vndb_id:
                counts["no-vndb-identity-held"] += 1
                continue
            upstream_id = str(item.get("id") or "")
            if not upstream_id.isdecimal() or upstream_id in seen_upstream:
                counts["missing-or-repeat-source-id"] += 1
                continue
            seen_upstream.add(upstream_id)
            year = date_year(item)
            if year is None:
                counts["missing-unreleased-or-future-year"] += 1
                continue
            aliases = source_names(item)
            if not aliases:
                counts["missing-title"] += 1
                continue
            if is_non_work_pack(aliases[0]):
                counts["non-independent-pack-held"] += 1
                continue
            collisions = set()
            for alias in aliases:
                collisions.update(existing.get(norm(alias), ()))
            if collisions:
                if any(c[1] == year for c in collisions):
                    counts["existing-work-matched"] += 1
                else:
                    counts["year-or-alias-conflict"] += 1
                    held.append({"sourceId": upstream_id, "names": aliases[:8],
                                 "year": year, "matches": sorted(collisions)[:10]})
                continue
            work_id = "nextmoe-" + upstream_id
            index_id = "nextmoe-20261031-" + upstream_id
            if work_id in taken_ids or index_id in taken_index_ids:
                counts["duplicate-id"] += 1
                continue
            title = aliases[0]
            # The source medium is verified; ADV versus RPG mechanics are not inferred.
            item_out = {
                "id": work_id,
                "indexId": index_id,
                "title": title,
                "aliases": aliases[1:18],
                "firstYear": year,
                "gameplay": "Galgame（玩法待核）",
                "group": "创作品牌待核",
                "source": API.replace("/works", "/works/" + upstream_id),
                "sourceRefs": ["vndb:" + vndb_id],
                "mainPlacement": "promoted-basic",
                "linkedRecordId": None,
                "creditScope": "NextMoe/鲲 Galgame 论坛汇聚元数据，仅来源关联，未断言具体创作/发行职责。",
                "yearBasis": "NextMoe v2 catalog release_date 首发记录；只登记年份，跨源和区域版次尚未独立核定。",
                "editorialScope": "名称与原作年份基础身份；剧情、角色、创作者、版本和详细玩法均待核。",
                "batch": BATCH,
            }
            additions.append(item_out)
            taken_ids.add(work_id)
            taken_index_ids.add(index_id)
            for alias in aliases:
                existing[norm(alias)].add((work_id, year, "current-import"))
            if len(additions) >= args.max_new:
                break
        print(f"page {page}, scanned {scanned}, galgame {counts['galgame']}, new {len(additions)}", flush=True)
        if len(additions) >= args.max_new or not rows or scanned >= payload.get("total", 10**9):
            break
        if page < args.pages:
            time.sleep(args.delay)
    if scanned == 0:
        raise RuntimeError("no source rows fetched - refusing to write")
    if not additions:
        raise RuntimeError("zero usable new distinct works - refusing to write")
    registry["works"].extend(additions)
    inc = len(additions)
    for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
        registry["summary"][key] += inc
    registry["updated"] = "2026-10-31"
    registry["batches"] = [b for b in registry.get("batches", []) if b.get("id") != BATCH]
    # Earlier KUN batch introduced an append-only metadata source before the
    # common per-batch 'candidates' accounting field was standardized.
    for earlier in registry["batches"]:
        summary = earlier.get("summary", {})
        if "candidates" not in summary and earlier.get("id") == "kungal-firstyear-20261031":
            summary["candidates"] = int(summary.get("newToRegistry", 0))
    registry["batches"].append({
        "id": BATCH, "source": API,
        "review": "data/nextmoe-bulk-review-20261031.json",
        "summary": {"candidates": inc, "scanned": scanned, **dict(counts), "promoted-basic": inc,
                    "year-or-alias-conflict-held": len(held)}
    })
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert registry["summary"]["addedToMainIdentityLayer"] == (
        registry["summary"]["promotedBasic"] + registry["summary"]["promotedDossier"])
    assert len(taken_ids) == len(registry["works"])
    assert len(taken_index_ids) == len(registry["works"])
    audit = {
        "schema": 1, "date": "2026-10-31", "source": API,
        "scope": "NextMoe medium=galgame with VNDB identity, released by 2026-10-31, exclude DLC/trials, names/aliases and original year only",
        "request": {"sort": "rating_vndb", "pageCountCap": args.pages, "pageSize": args.limit,
                    "limitNew": args.max_new},
        "summary": {"scanned": scanned, "newDistinctWorks": inc, "before": before,
                    "after": len(registry["works"]), **dict(counts)},
        "records": [{"id": r["id"], "title": r["title"], "aliases": r["aliases"],
                     "firstYear": r["firstYear"], "source": r["source"], "sourceRefs": r["sourceRefs"]} for r in additions],
        "heldForIdentityReview": held[:1000],
        "caveats": [
            "This is an API-sorted partial batch, not complete KUN resource-site harvesting.",
            "Medium galgame plus VNDB identity is an inclusion screen, not proof of story quality or specific ADV/RPG gameplay.",
            "No claims on ratings, quality, creator roles, content versions or translated edition chronology.",
            "Name/alias and matching-year collisions are skipped; differing-year conflicts are held, not merged or auto-added."
        ]
    }
    if args.dry_run:
        print(json.dumps(audit["summary"], ensure_ascii=False, indent=2))
        return
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"ADDED={inc} FROM={before} TO={len(registry['works'])} AUDIT={AUDIT}", flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=50)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-new", type=int, default=500)
    parser.add_argument("--delay", type=float, default=2.2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    assert 1 <= args.pages <= 100 and 1 <= args.limit <= 100 and 1 <= args.max_new <= 1500
    run(args)

if __name__ == "__main__":
    main()
