#!/usr/bin/env python3
"""Append a source-audited 1970s interactive-fiction batch to the basic identity registry."""
import argparse
import copy
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import import_nextmoe_basic_20261101_r2 as common

REGISTRY = ROOT / "data/main-adv-rpg-works-20261031.json"
INTAKE = ROOT / "data/historical-interactive-fiction-a-intake-20261101.json"
AUDIT = ROOT / "data/historical-interactive-fiction-1970s-audit-20261101.json"
REPORT = ROOT / "docs/historical-interactive-fiction-1970s-20261101.md"
BATCH = "historical-interactive-fiction-1970s-20261101"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")

def digest(obj):
    raw = json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def validate_candidate(row):
    assert row["evidenceLevel"] == "A-identity-year", row["title"]
    assert 1970 <= int(row["firstYear"]) <= 1979, row["title"]
    assert row["historicalScope"] in ("precursor", "proto-adventure", "core-interactive-fiction")
    assert row["title"] and row["gameplay"] and row["group"]
    assert row["evidenceNote"] and row["sourceRefs"] and row["platforms"]
    urls = [row["source"], *row.get("supportingSources", [])]
    assert len(urls) >= 1, row["title"]
    for value in urls:
        parsed = urlsplit(value)
        assert parsed.scheme == "https" and parsed.netloc, (row["title"], value)
    assert len(set(row["sourceRefs"])) == len(row["sourceRefs"]), row["title"]

def make_report(audit, intake):
    s = audit["summary"]
    lines = [
        "# 1970年代早期互动小说与文字冒险补录（2026-11-01）",
        "",
        f"基础身份库：{s['before']:,} → {s['after']:,}；输入候选 {s['inputCandidates']} 部，新建身份 {s['newDistinctWorks']} 部，关联已有身份 {s['linkedExisting']} 部，待核 {s['held']} 部。",
        "",
        "## 年份口径",
        "",
        "firstYear按最早可核的创作/首个实质版本年份记录。开发起始、首次可玩、公开传播、同期杂志刊载、商业销售和后续移植分别写入证据说明；不将不同阶段混成一个首发日期。",
        "",
        "## 已审阅作品",
        "",
        "| 作品 | 年份 | 历史范围 | 类型 | 平台线索 | 来源 |",
        "|---|---:|---|---|---|---|",
    ]
    for r in audit["records"]:
        p = "、".join(r["platforms"])
        lines.append(f"| {r['title']} | {r['firstYear']} | {r['historicalScope']} | {r['gameplay']} | {p} | [档案/资料]({r['source']}) |")
    lines += ["", "## 年份与版本核验说明", ""]
    for r in audit["records"]:
        lines.append(f"- **{r['title']}（{r['firstYear']}）**：{r['yearBasis']}")
    lines += ["", "## 已有身份关联（未重复新增）", ""]
    for r in audit["linkedExisting"]:
        lines.append(f"- {r['title']}：匹配已有身份 " + ", ".join(f"{m['workId']}（{m['year']}）" for m in r["matches"]))
    if not audit["linkedExisting"]:
        lines.append("- 无")
    lines += ["", "## 自动去重或年份冲突待核", ""]
    for r in audit["heldForReview"]:
        lines.append(f"- **{r['title']}**：{r['reason']}")
    if not audit["heldForReview"]:
        lines.append("- 无")
    lines += ["", "## 人工范围排除", ""]
    for r in intake.get("excludedByScope", []):
        lines.append(f"- **{r['title']}**：{r['reason']}")
    lines += [
        "",
        "## 分类原则",
        "",
        "- Hunt the Wumpus标记为文字迷宫探索前驱，不宣称其具有Adventure式自然语言解析器。",
        "- Wander标记为文字世界模拟/互动小说原型，兼具创作系统性质，不与成熟商业文字冒险混为一类。",
        "- Colossal Cave Adventure的Crowther原始作品与Woods扩展属于同一作品的版本演进，不重复建身份。",
        "- Zork指MIT大型机原始作品；1980—1982年商业三部曲是后续拆分发行，不把Zork I年份倒填给原始作品。",
        "- Stuga、Acheton和Haunt的开发跨越多个年份，firstYear只取最早可核的创作/首个实质版本年份。",
        "- Adventureland的1978年首个实质版本、1979年广告和馆藏平台记录分别保留。",
        "",
        "## 自动验证与上线",
        "",
        "导入脚本保留导入前全部作品对象哈希，并逐条复核新增记录；重复执行不会重复追加。GitHub Actions运行数据/实体校验、Python和Node回归测试后，将审计文件、报告和基础身份库生成结果提交到本PR分支。只有检查通过且合并到main后，才视为正式上线。",
        "",
        "## 本批暂缓",
        "",
    ]
    for r in intake.get("heldForReview", []):
        lines.append(f"- **{r['title']}**：{r['reason']}")
    lines.append("")
    REPORT.write_text("\\n".join(lines), encoding="utf-8")

def check_existing(registry, intake):
    audit = load(AUDIT)
    batch_rows = [b for b in registry.get("batches", []) if b.get("id") == BATCH]
    assert len(batch_rows) == 1, "batch metadata missing or duplicated"
    assert audit["batch"] == BATCH
    assert audit["intakeSha256"] == digest(intake), "intake changed after review"
    old_count = audit["summary"]["before"]
    assert digest(registry["works"][:old_count]) == audit["existingWorksSha256"], "pre-existing work objects changed"
    added = [w for w in registry["works"] if w.get("batch") == BATCH]
    assert len(added) == audit["summary"]["newDistinctWorks"] == batch_rows[0]["summary"]["promoted-basic"]
    expected = {r["id"]: r["registryRecord"] for r in audit["records"]}
    assert {w["id"] for w in added} == set(expected)
    for w in added:
        assert w == expected[w["id"]], "imported identity changed: " + w["id"]
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert len({w["id"] for w in registry["works"]}) == len(registry["works"])
    assert len({w["indexId"] for w in registry["works"]}) == len(registry["works"])
    print(f"Verified {len(added)} historical identities; preserved {old_count} pre-existing work objects.")

def run(args):
    intake = load(INTAKE)
    registry = load(REGISTRY)
    existing_batch = any(b.get("id") == BATCH for b in registry.get("batches", []))
    if existing_batch:
        check_existing(registry, intake)
        if args.check:
            return
        raise SystemExit("Batch already imported; refusing to append twice.")
    if args.check:
        raise SystemExit("Batch has not yet been imported.")
    before_registry = copy.deepcopy(registry)
    index = common.existing_index(registry)
    existing_ids = {str(w["id"]) for w in registry["works"]}
    existing_index_ids = {str(w["indexId"]) for w in registry["works"]}
    existing_refs = {ref for w in registry["works"] for ref in w.get("sourceRefs", [])}
    additions, linked, held = [], [], copy.deepcopy(intake.get("heldForReview", []))
    in_batch = {}
    added_rows = []
    for row in intake["records"]:
        validate_candidate(row)
        names = [row["title"], *row.get("aliases", [])]
        keys = {common.norm(n) for n in names if common.norm(n)}
        collisions_in_batch = {in_batch[k]["id"]: in_batch[k] for k in keys if k in in_batch}
        if collisions_in_batch:
            if all(item["year"] == row["firstYear"] for item in collisions_in_batch.values()):
                linked.append({"title": row["title"], "year": row["firstYear"], "matches": [
                    {"workId": item["id"], "year": item["year"], "scope": "same-batch"}
                    for item in sorted(collisions_in_batch.values(), key=lambda x: x["id"])
                ]})
            else:
                held.append({"title": row["title"], "reason": "same-batch title/alias year conflict"})
            continue
        matches = set()
        for key in keys:
            matches.update(index.get(key, set()))
        if matches:
            same_year = {m for m in matches if int(m[1]) == int(row["firstYear"])}
            if same_year:
                linked.append({"title": row["title"], "year": row["firstYear"], "matches": [
                    {"workId": m[0], "year": m[1], "scope": m[2]} for m in sorted(same_year)
                ]})
                if any(int(m[1]) != int(row["firstYear"]) for m in matches):
                    held.append({"title": row["title"], "reason": "additional alias matches a different year; same-year identity linked but conflict retained",
                                 "matches": [{"workId": m[0], "year": m[1], "scope": m[2]} for m in sorted(matches)]})
            else:
                held.append({"title": row["title"], "reason": "title/alias exists with a different firstYear",
                             "matches": [{"workId": m[0], "year": m[1], "scope": m[2]} for m in sorted(matches)]})
            continue
        repeated_refs = existing_refs.intersection(row["sourceRefs"])
        if repeated_refs:
            held.append({"title": row["title"], "reason": "source reference already used", "sourceRefs": sorted(repeated_refs)})
            continue
        key = hashlib.sha256(row["sourceRefs"][0].encode("utf-8")).hexdigest()[:16]
        work_id = "historical-" + key
        index_id = "basic-historical-1970s-20261101-" + key
        if work_id in existing_ids or index_id in existing_index_ids:
            held.append({"title": row["title"], "reason": "generated identity ID collision"})
            continue
        work = {
            "id": work_id,
            "indexId": index_id,
            "title": row["title"],
            "aliases": row.get("aliases", []),
            "firstYear": row["firstYear"],
            "gameplay": row["gameplay"],
            "group": row["group"],
            "source": row["source"],
            "sourceRefs": row["sourceRefs"],
            "mainPlacement": "promoted-basic",
            "linkedRecordId": None,
            "creditScope": "历史资料中的作者/组织仅作为来源线索；本批未建立正式开发、发行或个人署名职责关系。",
            "yearBasis": row["evidenceNote"],
            "editorialScope": "基础作品身份、年粒度创作/首个实质版本年份及粗粒度玩法；剧情、角色、正式创作者职责和具体平台发行版本仍待独立核验。",
            "batch": BATCH,
            "historicalScope": row["historicalScope"],
            "platformCandidates": row["platforms"],
            "sourceNote": row["evidenceNote"],
            "evidenceLevel": row["evidenceLevel"]
        }
        additions.append(work)
        added_rows.append(row)
        for name in names:
            k = common.norm(name)
            if k:
                in_batch[k] = {"id": work_id, "year": row["firstYear"]}
                index[k].add((work_id, row["firstYear"], "current-import"))
        existing_ids.add(work_id)
        existing_index_ids.add(index_id)
        existing_refs.update(row["sourceRefs"])
    if not additions:
        raise SystemExit("No new identities survived deduplication; refusing an empty import.")
    old_count = len(before_registry["works"])
    registry["works"].extend(additions)
    n = len(additions)
    for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
        registry["summary"][key] += n
    registry["updated"] = "2026-11-01"
    registry["batches"].append({
        "id": BATCH,
        "source": "IF Archive, MIT/Strong archival records, author historical accounts and museum catalogue; see intake/audit",
        "review": str(AUDIT.relative_to(ROOT)),
        "summary": {
            "candidates": len(intake["records"]),
            "promoted-basic": n,
            "linked-existing": len(linked),
            "held": len(held),
            "before": old_count,
            "after": len(registry["works"])
        }
    })
    assert registry["works"][:old_count] == before_registry["works"], "pre-existing objects changed"
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert len({w["id"] for w in registry["works"]}) == len(registry["works"])
    assert len({w["indexId"] for w in registry["works"]}) == len(registry["works"])
    audit = {
        "schema": 1,
        "date": "2026-11-01",
        "batch": BATCH,
        "intakeSha256": digest(intake),
        "existingWorksSha256": digest(before_registry["works"]),
        "summary": {
            "inputCandidates": len(intake["records"]),
            "before": old_count,
            "after": len(registry["works"]),
            "newDistinctWorks": n,
            "linkedExisting": len(linked),
            "held": len(held),
            "byYear": dict(Counter(str(r["firstYear"]) for r in added_rows)),
            "byScope": dict(Counter(r["historicalScope"] for r in added_rows))
        },
        "records": [{**row, "id": work["id"], "registryRecord": work}
                    for row, work in zip(added_rows, additions)],
        "linkedExisting": linked,
        "heldForReview": held
    }
    save(REGISTRY, registry)
    save(AUDIT, audit)
    make_report(audit, intake)
    check_existing(registry, intake)
    print(json.dumps(audit["summary"], ensure_ascii=False, indent=2))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    run(parser.parse_args())

if __name__ == "__main__":
    main()
