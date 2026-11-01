#!/usr/bin/env python3
"""Audit decade and developer-type diversity for basic registry rounds 20 and 21.

Only reads the two batch audit files and VNDB's public producer/developer metadata.
It does not write creator credits into the basic registry or assert independent status.
"""
import json
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VNDB_API = "https://api.vndb.org/kana/vn"
AUDITS = [
    ("r20", ROOT / "data/vndb-kana-bulk-review-20261101-r20.json"),
    ("r21", ROOT / "data/nextmoe-bulk-review-20261101-r21.json"),
]
OUT = ROOT / "data/basic-r20-r21-diversity-audit-20261101.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def fetch_developers(vndb_ids, retry=4):
    query = {
        "fields": "id,developers.id,developers.name,developers.original,developers.type",
        "filters": ["or", *[["id", "=", value] for value in vndb_ids]],
        "results": 100,
    }
    request = urllib.request.Request(
        VNDB_API,
        data=json.dumps(query).encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "NarrativeCatalogueResearch/1.0 (wt1234-donkey/visual-novel; developer-diversity-audit)",
        },
    )
    for attempt in range(retry):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.load(response)
            if not isinstance(payload.get("results"), list):
                raise RuntimeError("VNDB developer audit response schema changed")
            return payload["results"]
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            wait = min(90, max(10, int(exc.headers.get("Retry-After") or 0), (attempt + 1) * 10))
            print("VNDB_DEVELOPER_RETRY", exc.code, wait, flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry - 1:
                raise
            time.sleep((attempt + 1) * 10)
    raise RuntimeError("VNDB developer audit retry loop exhausted")


def main():
    works = []
    for batch, path in AUDITS:
        audit = load(path)
        for row in audit["records"]:
            works.append({
                "batch": batch,
                "sourceId": row["sourceId"],
                "vndbId": row["vndbId"],
                "title": row["title"],
                "firstYear": row["firstYear"],
                "source": row["source"],
            })
    ids = [row["vndbId"] for row in works]
    if len(works) != 1000 or len(ids) != len(set(ids)):
        raise RuntimeError("Expected exactly 1,000 unique VNDB IDs across rounds 20 and 21")
    developers_by_vn = {}
    for offset in range(0, len(ids), 100):
        chunk = ids[offset:offset + 100]
        rows = fetch_developers(chunk)
        for row in rows:
            developers_by_vn[row["id"]] = row.get("developers") or []
        print("DEVELOPER_AUDIT", min(offset + 100, len(ids)), "OF", len(ids),
              "RETURNED", len(rows), flush=True)
        if offset + 100 < len(ids):
            # Deliberately throttle this supplementary metadata read.
            time.sleep(15)

    records = []
    decade_counts = Counter()
    batch_counts = Counter()
    producer_type_counts = Counter()
    producer_work_counts = Counter()
    producer_names = {}
    coverage_by_decade = defaultdict(Counter)
    with_developer = 0
    individual_or_amateur = 0
    company_only = 0
    no_developer = 0
    for work in works:
        developers = []
        seen = set()
        for producer in developers_by_vn.get(work["vndbId"], []):
            producer_id = str(producer.get("id") or "")
            if not producer_id or producer_id in seen:
                continue
            seen.add(producer_id)
            kind = str(producer.get("type") or "unknown")
            producer_type_counts[kind] += 1
            producer_work_counts[producer_id] += 1
            producer_names[producer_id] = {
                "id": producer_id,
                "name": producer.get("name"),
                "original": producer.get("original"),
                "type": kind,
            }
            developers.append({
                "id": producer_id,
                "name": producer.get("name"),
                "original": producer.get("original"),
                "type": kind,
            })
        year = int(work["firstYear"])
        decade = f"{(year // 10) * 10}s"
        decade_counts[decade] += 1
        batch_counts[work["batch"]] += 1
        coverage_by_decade[decade]["total"] += 1
        kinds = {developer["type"] for developer in developers}
        if developers:
            with_developer += 1
            coverage_by_decade[decade]["withDeveloper"] += 1
        else:
            no_developer += 1
            coverage_by_decade[decade]["noDeveloperListed"] += 1
        if kinds & {"in", "ng"}:
            individual_or_amateur += 1
            coverage_by_decade[decade]["individualOrAmateurSignal"] += 1
        elif "co" in kinds:
            company_only += 1
            coverage_by_decade[decade]["companyOnly"] += 1
        records.append({
            **work,
            "decade": decade,
            "developers": developers,
            "developerClassification": (
                "individual-or-amateur-group signal" if kinds & {"in", "ng"}
                else "company-only metadata" if "co" in kinds
                else "no developer listed"
            ),
        })

    top_developers = sorted(
        ({"workCount": count, **producer_names[producer_id]}
         for producer_id, count in producer_work_counts.items()),
        key=lambda item: (-item["workCount"], item["name"] or ""),
    )[:30]
    summary = {
        "records": len(records),
        "uniqueVndbIds": len(set(ids)),
        "developerLinkedWorks": with_developer,
        "noDeveloperListed": no_developer,
        "individualOrAmateurGroupSignalWorks": individual_or_amateur,
        "companyOnlyWorks": company_only,
        "uniqueDeveloperProducerIds": len(producer_names),
        "producerEntryCountsByType": dict(producer_type_counts),
        "decades": dict(sorted(decade_counts.items())),
        "byBatch": dict(batch_counts),
        "developerCoverageByDecade": {
            decade: dict(counts) for decade, counts in sorted(coverage_by_decade.items())
        },
        "classificationCaveat": (
            "VNDB producer type 'in' means individual and 'ng' means amateur group. "
            "Their presence is only a source-metadata signal, not proof that a work or studio is independent. "
            "Missing developer entries do not mean the work has no developer."
        ),
    }
    output = {
        "schema": 1,
        "date": "2026-11-01",
        "source": VNDB_API,
        "sourceLicense": "https://vndb.org/d17",
        "method": "Batch lookup of up to 100 VNDB IDs per request; fields limited to producer IDs, names, original names and producer type.",
        "summary": summary,
        "topDevelopersByLinkedWorkCount": top_developers,
        "records": records,
    }
    OUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("DIVERSITY_AUDIT_COMPLETE", json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
