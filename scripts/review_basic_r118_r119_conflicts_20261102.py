#!/usr/bin/env python3
"""Collect source evidence for the 67 isolated rows / 56 identities from rounds 118–119."""
import argparse
from collections import defaultdict
import datetime as dt
import hashlib
import json
import subprocess
import time
import urllib.error
import urllib.request

import import_basic_r22_cont_r23_20261101 as source
import ifdb_archive_identity as ifdb

ROOT = source.ROOT
BASE = "15de08a41d36d99fd0bd56dac86129360144e505"
A118 = ROOT / "data/vndb-kana-bulk-review-20261102-r118.json"
A119 = ROOT / "data/nextmoe-ifdb-bulk-review-20261102-r119.json"
OUT = ROOT / "data/basic-r118-r119-conflict-evidence-20261102.json"
MD = ROOT / "data/basic-r118-r119-conflict-evidence-20261102.md"
DATE = "2026-11-02"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def held_identities():
    audits = [(118, A118), (119, A119)]
    groups = {}
    locators = set()
    for batch, path in audits:
        audit = load(path)
        for index, row in enumerate(audit["heldForIdentityReview"]):
            key = "vndb:" + row["vndbId"] if row.get("vndbId") else "ifdb:" + row["sourceId"]
            locator = (str(path.relative_to(ROOT)), index)
            assert locator not in locators
            locators.add(locator)
            groups.setdefault(key, []).append({
                "batch": batch, "audit": str(path.relative_to(ROOT)),
                "index": index, "row": row
            })
    assert sum(len(v) for v in groups.values()) == 67
    assert len(groups) == 56
    return groups


def vndb_query(ids):
    ids = sorted(set(ids))
    if not ids:
        return {}
    payload = {
        "filters": ["id", "=", ids],
        "fields": (
            "title, alttitle, aliases, released, devstatus, "
            "developers{id,name,original,type}, "
            "relations{id,title,relation,relation_official}, extlinks{url}"
        ),
        "results": 100
    }
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        "https://api.vndb.org/kana/vn", data=body,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "NarrativeCatalogueResearch/1.0 (wt1234-donkey/visual-novel)"
        },
        method="POST"
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.loads(response.read().decode("utf-8"))
            rows = result.get("results", [])
            found = {row["id"]: row for row in rows}
            missing = set(ids) - set(found)
            if missing:
                raise RuntimeError("VNDB API omitted requested IDs: " + ", ".join(sorted(missing)))
            return found
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            if exc.code == 429 or 500 <= exc.code < 600:
                time.sleep(min(8 * (attempt + 1), 30))
                continue
            raise RuntimeError(f"VNDB API HTTP {exc.code}: {detail}") from exc
    raise RuntimeError("VNDB API request failed after retries")


def ifdb_maps(data):
    games = {str(row["id"]): row for row in data["games"]}
    forwards = {str(row["gameid"]): str(row["fwdgameid"]) for row in data["gamefwds"]}
    ifids = defaultdict(list)
    xrefs = defaultdict(list)
    links = defaultdict(list)
    for row in data["ifids"]:
        ifids[str(row["gameid"])].append(row["ifid"])
    for row in data["gamexrefs"]:
        xrefs[str(row["fromid"])].append({
            "target": str(row["toid"]), "relation": row["reftype"]
        })
    for row in data["gamelinks"]:
        links[str(row["gameid"])].append(row["url"])
    return games, forwards, ifids, xrefs, links


def ifdb_snapshot(tuid, maps):
    games, forwards, ifids, xrefs, links = maps
    canonical = ifdb.canonical_id(str(tuid), forwards)
    row = games.get(canonical)
    if not row:
        return None
    return {
        "tuid": canonical,
        "title": ifdb.clean_title(row.get("title") or ""),
        "author": row.get("author"),
        "published": row.get("published"),
        "system": row.get("system"),
        "language": row.get("language"),
        "flags": row.get("flags"),
        "tags": row.get("tags"),
        "ifids": sorted(ifids.get(canonical, [])),
        "redirectsTo": canonical if canonical != str(tuid) else None,
        "xrefs": xrefs.get(canonical, []),
        "links": sorted(set(links.get(canonical, []))),
        "website": row.get("website")
    }


def compact_work(work):
    if not work:
        return None
    return {
        "id": work.get("id"), "title": work.get("title"),
        "firstYear": work.get("firstYear"), "aliases": work.get("aliases", []),
        "sourceRefs": work.get("sourceRefs", []),
        "mainPlacement": work.get("mainPlacement"),
        "batch": work.get("batch")
    }


def collect():
    groups = held_identities()
    registry = source.load(source.REG)
    work_map = {w["id"]: w for w in source.all_works(registry)}
    vndb_ids = set()
    for key, entries in groups.items():
        if key.startswith("vndb:"):
            vndb_ids.add(key.split(":", 1)[1])
        for entry in entries:
            for match in entry["row"].get("matches", []):
                match_id = str(match[0])
                if match_id.startswith("vndb-v"):
                    vndb_ids.add(match_id[len("vndb-"):])
    vndb = vndb_query(vndb_ids)

    archive_path = ROOT / "tmp-ifdb-archive-20260901.zip"
    archive = ifdb.read_archive(archive_path)
    safe_rows, rejected = ifdb.prepare(archive, dt.date.fromisoformat(DATE))
    safe_ifdb = {row["tuid"]: row for row in safe_rows}
    ifdb_data = ifdb_maps(archive)

    evidence = {}
    for key, entries in groups.items():
        first = entries[0]["row"]
        if key.startswith("vndb:"):
            sid = key.split(":", 1)[1]
            candidate = vndb.get(sid)
            candidate_kind = "vndb"
        else:
            sid = key.split(":", 1)[1]
            candidate = ifdb_snapshot(sid, ifdb_data)
            candidate_kind = "ifdb"
        matches = []
        for entry in entries:
            for match in entry["row"].get("matches", []):
                match_id, match_year = str(match[0]), match[1]
                match_source = match[2] if len(match) > 2 else None
                match_item = {
                    "id": match_id, "year": match_year, "matchSource": match_source,
                    "registryWork": compact_work(work_map.get(match_id))
                }
                if match_id.startswith("vndb-v"):
                    match_item["sourceSnapshot"] = vndb.get(match_id[len("vndb-"):])
                elif match_id.startswith("ifdb-"):
                    match_item["sourceSnapshot"] = ifdb_snapshot(match_id[len("ifdb-"):], ifdb_data)
                matches.append(match_item)
        evidence[key] = {
            "sourceIdentity": key,
            "candidateKind": candidate_kind,
            "candidateSourceId": sid,
            "title": first.get("title"),
            "intakeYear": first.get("firstYear") or (
                int(first["published"][:4]) if first.get("published") else None
            ),
            "reason": first.get("reason") or first.get("basis"),
            "sourceRows": entries,
            "candidateSnapshot": candidate,
            "candidateSafeInPinnedIfdbArchive": (
                sid in safe_ifdb if candidate_kind == "ifdb" else None
            ),
            "matches": matches
        }

    counts = {
        "rawRows": sum(len(v) for v in groups.values()),
        "uniqueSourceIdentities": len(groups),
        "vndbIdentities": sum(k.startswith("vndb:") for k in groups),
        "ifdbIdentities": sum(k.startswith("ifdb:") for k in groups),
        "nameYearIdentityConflicts": sum(
            not any("edition" in str(e["row"].get("reason") or e["row"].get("basis"))
                    or "dependent" in str(e["row"].get("reason") or e["row"].get("basis"))
                    for e in entries)
            for entries in groups.values()
        ),
        "suspectedEditionOrDependentContent": sum(
            any("edition" in str(e["row"].get("reason") or e["row"].get("basis"))
                or "dependent" in str(e["row"].get("reason") or e["row"].get("basis"))
                for e in entries)
            for entries in groups.values()
        ),
        "repeatedRowsCollapsed": sum(len(v) - 1 for v in groups.values())
    }
    assert counts == {
        "rawRows": 67, "uniqueSourceIdentities": 56,
        "vndbIdentities": 39, "ifdbIdentities": 17,
        "nameYearIdentityConflicts": 53,
        "suspectedEditionOrDependentContent": 3,
        "repeatedRowsCollapsed": 11
    }
    assert len(vndb) == len(vndb_ids)
    return {
        "schema": 1, "date": DATE, "baseCommit": BASE,
        "batchId": "r118-r119-conflict-evidence-20261102",
        "summary": counts,
        "provenance": {
            "vndbApi": "https://api.vndb.org/kana/vn",
            "vndbRetrievedOn": DATE,
            "ifdbArchiveUrl": ifdb.ARCHIVE_URL,
            "ifdbArchiveSha256": ifdb.ARCHIVE_SHA256,
            "ifdbArchivePreparationDispositions": rejected,
            "registryWorkCount": len(registry["works"]),
            "inputAudits": {
                str(A118.relative_to(ROOT)): hashlib.sha256(A118.read_bytes()).hexdigest(),
                str(A119.relative_to(ROOT)): hashlib.sha256(A119.read_bytes()).hexdigest()
            }
        },
        "identities": evidence
    }


def markdown(report):
    lines = [
        "# 第118、119批隔离身份来源核实证据",
        "",
        "本文件先收集来源元数据和匹配身份信息，不自动作出新增、合并或版本决定。",
        "",
        f"原始记录 {report['summary']['rawRows']} 条；独立来源身份 "
        f"{report['summary']['uniqueSourceIdentities']} 个；名称/年份/身份冲突 "
        f"{report['summary']['nameYearIdentityConflicts']} 个；疑似版本/依赖内容 "
        f"{report['summary']['suspectedEditionOrDependentContent']} 个。",
        "",
        "| 来源身份 | 候选作品 | 年份 | 来源作者/开发主体 | 匹配身份 | 匹配年份 | 匹配作者/开发主体 | 来源行数 |",
        "|---|---|---:|---|---|---:|---|---:|"
    ]
    for key, item in report["identities"].items():
        candidate = item.get("candidateSnapshot") or {}
        creator = ", ".join(
            d.get("name", "") for d in candidate.get("developers", [])
            if isinstance(d, dict)
        ) if item["candidateKind"] == "vndb" else candidate.get("author", "")
        if not creator:
            creator = "原始来源未提供"
        matches = item.get("matches", [])
        if not matches:
            lines.append(
                f"| {key} | {item.get('title','')} | {item.get('intakeYear') or ''} | "
                f"{creator} | — | — | — | {len(item['sourceRows'])} |"
            )
        else:
            for index, match in enumerate(matches):
                snap = match.get("sourceSnapshot") or {}
                matched_creator = ", ".join(
                    d.get("name", "") for d in snap.get("developers", [])
                    if isinstance(d, dict)
                ) if "developers" in snap else snap.get("author", "")
                if not matched_creator:
                    matched_creator = "仅有主库/历史身份摘要"
                lines.append(
                    f"| {key if index == 0 else ''} | {item.get('title','') if index == 0 else ''} | "
                    f"{item.get('intakeYear') or '' if index == 0 else ''} | "
                    f"{creator if index == 0 else ''} | {match['id']} | {match.get('year') or ''} | "
                    f"{matched_creator} | {len(item['sourceRows']) if index == 0 else ''} |"
                )
    lines += [
        "", "## 处理边界", "",
        "- VNDB的released字段是VN级日期；需结合开发主体、原文标题、关系和发行资料判断同名异作。",
        "- IFDB候选使用固定归档的作者、published、系统、IFID、重定向和交叉引用；归档日期不等于作品年份。",
        "- 发现同一作者或同一故事的移植、翻译、重制、合集、FD或依赖内容时，不自动新建身份。",
        "- 证据不足的身份继续隔离；来源日期不覆盖主库原有年份。",
        "", "## 来源与文件", "",
        f"- VNDB API：{report['provenance']['vndbApi']}",
        f"- IFDB固定归档：{report['provenance']['ifdbArchiveUrl']}",
        f"- IFDB SHA-256：{report['provenance']['ifdbArchiveSha256']}",
        "- 原始审计：data/vndb-kana-bulk-review-20261102-r118.json、data/nextmoe-ifdb-bulk-review-20261102-r119.json",
        ""
    ]
    return "\n".join(lines)


def write():
    report = collect()
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD.write_text(markdown(report), encoding="utf-8")
    print("CONFLICT_EVIDENCE_OK", json.dumps(report["summary"], ensure_ascii=False), flush=True)


def check():
    report = load(OUT)
    assert report["baseCommit"] == BASE
    assert report["summary"]["rawRows"] == 67
    assert report["summary"]["uniqueSourceIdentities"] == 56
    assert report["summary"]["nameYearIdentityConflicts"] == 53
    assert report["summary"]["suspectedEditionOrDependentContent"] == 3
    assert len(report["identities"]) == 56
    assert all(row.get("candidateSnapshot") for row in report["identities"].values())
    assert MD.read_text(encoding="utf-8") == markdown(report)
    for path, digest in report["provenance"]["inputAudits"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    print("CONFLICT_EVIDENCE_CHECK_OK 67 rows / 56 identities")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    check() if args.check else write()
