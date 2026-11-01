#!/usr/bin/env python3
"""Append-only rounds 20-21. R20 resumes VNDB after v3178; R21 resumes NextMoe at page 93."""
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
REG = common.REGISTRY
CUTOFF = dt.date(2026, 11, 1)
R20 = "vndb-kana-bulk-20261101-r20"
A20 = ROOT / "data/vndb-kana-bulk-review-20261101-r20.json"
R21 = "nextmoe-galgame-bulk-20261101-r21"
A21 = ROOT / "data/nextmoe-bulk-review-20261101-r21.json"
VNDB_API = "https://api.vndb.org/kana/vn"
NEXTMOE_API = "https://api.nextmoe.dev/v2/catalog/works"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm(value):
    return common.norm(value)


def vndb_names(item):
    values = [item.get("title"), item.get("alttitle"), *(item.get("aliases") or [])]
    result, seen = [], set()
    for value in values:
        if not isinstance(value, str):
            continue
        value = value.strip()
        key = norm(value)
        if len(key) < 3 or len(value) > 160 or key in seen:
            continue
        seen.add(key)
        result.append(value)
    return result


def vndb_year(item):
    raw = item.get("released")
    if item.get("devstatus") not in (None, 0):
        return None
    if not isinstance(raw, str) or not re.fullmatch(r"\d{4}(?:-\d{2}){0,2}", raw):
        return None
    year = int(raw[:4])
    if year < 1976 or year > CUTOFF.year:
        return None
    try:
        if len(raw) == 10 and dt.date.fromisoformat(raw) > CUTOFF:
            return None
        if len(raw) == 7 and year == CUTOFF.year and int(raw[5:7]) > CUTOFF.month:
            return None
    except ValueError:
        return None
    return year


def get_vndb_page(cursor, retry=4):
    query = {
        "fields": "title,alttitle,aliases,released,devstatus",
        "results": 100,
        "sort": "id",
        "reverse": False,
        "filters": ["id", ">", cursor],
    }
    request = urllib.request.Request(
        VNDB_API,
        data=json.dumps(query).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NarrativeCatalogueResearch/1.0 (wt1234-donkey/visual-novel; metadata only)",
        },
    )
    for attempt in range(retry):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.load(response)
            if not isinstance(payload.get("results"), list) or not isinstance(payload.get("more"), bool):
                raise RuntimeError("VNDB Kana response schema changed")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            wait = min(90, max(5, int(exc.headers.get("Retry-After") or 0), (attempt + 1) * 7))
            print("VNDB_RETRY", exc.code, wait, flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry - 1:
                raise
            time.sleep((attempt + 1) * 7)
    raise RuntimeError("VNDB retry loop exhausted")


def base_state():
    registry = load(REG)
    index = common.existing_index(registry)
    ids = {str(work["id"]) for work in registry["works"]}
    index_ids = {str(work["indexId"]) for work in registry["works"]}
    refs = {ref for work in registry["works"] for ref in work.get("sourceRefs", [])}
    return registry, index, ids, index_ids, refs


def append_batch(registry, additions, batch_id, source, audit_path, summary, records, held, source_docs, source_license, intake_date="2026-11-01"):
    if not additions:
        raise RuntimeError(batch_id + " produced zero eligible new identities; refusing empty batch")
    before = len(registry["works"])
    registry["works"].extend(additions)
    count = len(additions)
    for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
        registry["summary"][key] += count
    registry["updated"] = intake_date
    registry["batches"].append({
        "id": batch_id,
        "source": source,
        "review": str(audit_path.relative_to(ROOT)),
        "summary": {"candidates": count, "promoted-basic": count, **summary},
    })
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert registry["summary"]["addedToMainIdentityLayer"] == (
        registry["summary"]["promotedBasic"] + registry["summary"]["promotedDossier"]
    )
    audit = {
        "schema": 1,
        "date": intake_date,
        "source": source,
        "sourceDocs": source_docs,
        "sourceLicense": source_license,
        "summary": {
            "newDistinctWorks": count,
            "before": before,
            "after": len(registry["works"]),
            **summary,
        },
        "records": records,
        "heldForIdentityReview": held,
        "caveats": [
            "Basic identity only: source ID, VNDB ID where available, title, aliases and source year.",
            "No platform edition, content-version, creator credit, publisher role or narrative-quality claim is asserted.",
            "Name/year conflicts, derivative works and uncertain identities are held or skipped, not force-merged.",
        ],
    }
    save(REG, registry)
    save(audit_path, audit)
    print("BATCH_DONE", batch_id, "NEW", count, "BEFORE", before, "AFTER", len(registry["works"]), flush=True)
    return registry


def existing_batch(registry, batch_id, audit_path):
    matches = [batch for batch in registry.get("batches", []) if batch.get("id") == batch_id]
    if not matches:
        return False
    if len(matches) != 1 or not audit_path.exists():
        raise RuntimeError("Existing batch has missing audit or duplicate batch marker: " + batch_id)
    audit = load(audit_path)
    expected = matches[0]["summary"]["promoted-basic"]
    actual = sum(work.get("batch") == batch_id for work in registry["works"])
    assert audit["summary"]["newDistinctWorks"] == expected == actual
    print("SKIP_EXISTING", batch_id, expected, flush=True)
    return True


def round20(max_new=500, pages=250, delay=1.2):
    registry, index, ids, index_ids, refs = base_state()
    if existing_batch(registry, R20, A20):
        return registry
    cursor = "v3178"
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
            index_id = "vndb-20261101-r20-" + vndb_id
            if work_id in ids or index_id in index_ids:
                counts["id-collision"] += 1
                continue
            source_url = "https://vndb.org/" + vndb_id
            work = {
                "id": work_id,
                "indexId": index_id,
                "title": names[0],
                "aliases": names[1:18],
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
                "batch": R20,
            }
            additions.append(work)
            records.append({
                "id": work_id, "sourceId": vndb_id, "vndbId": vndb_id,
                "title": names[0], "aliases": names[1:18], "firstYear": year,
                "source": source_url, "sourceRefs": [source_ref],
            })
            ids.add(work_id)
            index_ids.add(index_id)
            refs.add(source_ref)
            for name in names:
                index[norm(name)].add((work_id, year, "r20"))
            if len(additions) >= max_new:
                break
        print("R20_PAGE", page_number, "SCANNED", scanned, "NEW", len(additions), "CURSOR", cursor, flush=True)
        if len(additions) >= max_new or not payload.get("more"):
            break
        time.sleep(delay)
    return append_batch(
        registry, additions, R20, VNDB_API, A20,
        {"scanned": scanned, "cursorStart": "v3178", "cursorEnd": cursor, **dict(counts)},
        records, held, "https://api.vndb.org/kana", "https://vndb.org/d17",
    )


def round21(max_new=500, start_page=93, pages=100, delay=1.2):
    registry, index, ids, index_ids, refs = base_state()
    if existing_batch(registry, R21, A21):
        return registry
    additions, records, held = [], [], []
    counts = Counter()
    scanned = 0
    end_page = start_page - 1
    for page in range(start_page, start_page + pages):
        payload = common.get_page(page, 100)
        rows = payload["items"]
        if not rows:
            break
        end_page = page
        for item in rows:
            scanned += 1
            if item.get("medium") != "galgame":
                counts["other-medium"] += 1
                continue
            vndb_id = common.has_vndb_identity(item)
            if not vndb_id:
                counts["no-vndb-identity-held"] += 1
                continue
            source_id = str(item.get("id") or "")
            if not source_id.isdecimal():
                counts["invalid-source-id"] += 1
                continue
            source_ref = "nextmoe:" + source_id
            vndb_ref = "vndb:" + vndb_id
            if source_ref in refs or "nextmoe-" + source_id in ids or vndb_ref in refs:
                counts["existing-source-or-vndb-id"] += 1
                continue
            names = common.source_names(item)
            year = common.date_year(item)
            if year is None:
                counts["missing-year-or-unreleased"] += 1
                continue
            if not names:
                counts["missing-title"] += 1
                continue
            if (source_id in common.HELD_EDITION_IDS or common.is_non_work_pack(names[0]) or
                any(re.search(r"(?i)(?:fan.?disc|\bFD\b|\bbundle\b|\bcollection\b|remaster|リマスター|合集)", name)
                    for name in names)):
                counts["edition-held"] += 1
                held.append({"sourceId": source_id, "vndbId": vndb_id, "title": names[0],
                             "reason": "Possible edition, DLC, fan disc or collection"})
                continue
            hits = set()
            for name in names:
                hits.update(index.get(norm(name), ()))
            if hits:
                if any(hit[1] == year for hit in hits):
                    counts["existing-work-matched"] += 1
                else:
                    counts["year-or-alias-conflict"] += 1
                    held.append({"sourceId": source_id, "vndbId": vndb_id, "title": names[0],
                                 "year": year, "matches": [list(hit) for hit in sorted(hits)[:8]]})
                continue
            work_id = "nextmoe-" + source_id
            index_id = "nextmoe-20261101-r21-" + source_id
            if work_id in ids or index_id in index_ids:
                counts["id-collision"] += 1
                continue
            source_url = NEXTMOE_API + "/" + source_id
            source_refs = [source_ref, vndb_ref]
            work = {
                "id": work_id,
                "indexId": index_id,
                "title": names[0],
                "aliases": names[1:18],
                "firstYear": year,
                "gameplay": "Galgame（玩法待核）",
                "group": "创作品牌待核",
                "source": source_url,
                "sourceRefs": source_refs,
                "mainPlacement": "promoted-basic",
                "linkedRecordId": None,
                "creditScope": "NextMoe v2 Galgame 目录来源；仅来源关联，未断言创作或发行职责。",
                "yearBasis": "NextMoe release_date 年份；首次发行地区/版次待核。",
                "editorialScope": "基本作品身份；剧情、创作者、详细玩法及内容版本待核。",
                "batch": R21,
            }
            additions.append(work)
            records.append({
                "id": work_id, "sourceId": source_id, "vndbId": vndb_id,
                "title": names[0], "aliases": names[1:18], "firstYear": year,
                "source": source_url, "sourceRefs": source_refs,
            })
            ids.add(work_id)
            index_ids.add(index_id)
            refs.add(source_ref)
            refs.add(vndb_ref)
            for name in names:
                index[norm(name)].add((work_id, year, "r21"))
            if len(additions) >= max_new:
                break
        print("R21_PAGE", page, "SCANNED", scanned, "NEW", len(additions), flush=True)
        if len(additions) >= max_new or scanned >= payload.get("total", 10**9):
            break
        time.sleep(delay)
    return append_batch(
        registry, additions, R21, NEXTMOE_API, A21,
        {"scanned": scanned, "startPage": start_page, "endPage": end_page, **dict(counts)},
        records, held, "https://api.nextmoe.dev/v2/catalog/works",
        "NextMoe public API metadata; no separate redistribution license asserted. Retain only minimal identity facts and source links.",
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-new", type=int, default=500)
    parser.add_argument("--vndb-pages", type=int, default=250)
    parser.add_argument("--nextmoe-start-page", type=int, default=93)
    parser.add_argument("--nextmoe-pages", type=int, default=100)
    parser.add_argument("--delay", type=float, default=1.2)
    args = parser.parse_args()
    assert 1 <= args.max_new <= 500
    assert 1 <= args.vndb_pages <= 400
    assert args.nextmoe_start_page >= 93
    assert 1 <= args.nextmoe_pages <= 150
    assert args.delay >= 1
    registry = round20(args.max_new, args.vndb_pages, args.delay)
    print("AFTER_R20", len(registry["works"]), flush=True)
    registry = round21(args.max_new, args.nextmoe_start_page, args.nextmoe_pages, args.delay)
    print("AFTER_R21", len(registry["works"]), flush=True)


if __name__ == "__main__":
    main()
