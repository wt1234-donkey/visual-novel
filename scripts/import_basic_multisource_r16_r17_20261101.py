#!/usr/bin/env python3
"""Rounds 16/17: NextMoe alternate-source ranking + Bangumi game directory.

Append-only basic identity import. Does not write games.json or curated dossiers.
Round 16: NextMoe galgame records sorted by Bangumi-origin rating.
Round 17: Bangumi official v0 game catalogue, category=4001, filtered to
explicit ADV/VN/interactive-fiction or RPG genre tags.
"""
import argparse
import datetime as dt
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

import import_nextmoe_basic_20261101_r2 as common

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = common.REGISTRY
BATCH16 = "nextmoe-galgame-bulk-20261101-r16"
AUDIT16 = ROOT / "data/nextmoe-bulk-review-20261101-r16.json"
INDEX16 = "nextmoe-20261101-r16-"
BATCH17 = "bangumi-games-bulk-20261101-r17"
AUDIT17 = ROOT / "data/bangumi-game-bulk-review-20261101-r17.json"
INDEX17 = "bangumi-20261101-r17-"
BANGUMI_API = "https://api.bgm.tv/v0/subjects"
CUTOFF = dt.date(2026, 11, 1)

ADV_TAGS = {
    "adv", "avg", "vn", "galgame", "gal game", "visual novel",
    "interactive fiction", "interactive narrative", "narrative game",
    "文字冒险", "文字冒險", "文字冒险游戏", "文字游戏", "视觉小说", "視覺小說",
    "乙女", "乙女游戏", "恋爱冒险", "戀愛冒險", "互动小说", "互動小說",
    "互动叙事", "互動敘事", "アドベンチャー", "アドベンチャーゲーム",
    "ビジュアルノベル", "ノベルゲーム", "サウンドノベル",
    "ギャルゲーム", "ギャルゲー", "美少女ゲーム", "エロゲ",
    "恋愛adv", "推理adv",
}
RPG_TAGS = {
    "rpg", "jrpg", "crpg", "srpg", "drpg", "arpg",
    "角色扮演", "日式rpg", "策略rpg", "战棋", "戰棋",
    "ロールプレイング", "ロールプレイングゲーム",
}
RPG_SUBGENRES = {"jrpg", "crpg", "srpg", "drpg"}
EXPLICIT_NARRATIVE = {
    "剧情", "剧情向", "剧情丰富", "剧情驱动", "叙事", "叙事向", "网状叙事",
    "故事", "故事驱动", "推理", "悬疑", "galgame", "vn", "visual novel",
    "视觉小说", "视覺小說", "文字冒险", "文字冒險", "文字冒险游戏",
    "文字游戏", "互动小说", "互动叙事", "乙女", "乙女游戏",
    "恋爱adv", "恋爱冒险", "小说", "novel game", "sound novel",
    "サウンドノベル", "ノベルゲーム", "ビジュアルノベル",
}
ACTION_HEAVY = {
    "act", "aavg", "arpg", "fps", "tps", "rts", "mug", "spg", "rac",
    "stg", "ftg", "moba", "mmorpg", "platform", "平台跳跃", "动作",
    "射击", "竞速", "体育", "竞技", "音乐", "音游", "格斗", "即时战略",
}
HARD_NON_NARRATIVE = {
    "rts", "moba", "spg", "rac", "ftg", "mug", "sports", "体育",
    "竞技", "竞速", "即时战略",
}
STRONG_NARRATIVE = {
    "叙事", "叙事向", "网状叙事", "故事驱动", "剧情驱动", "剧情向",
    "剧情丰富", "推理", "悬疑", "galgame", "vn", "visual novel",
    "视觉小说", "视覺小說", "文字冒险", "文字冒險", "文字游戏",
    "互动小说", "互动叙事", "乙女", "乙女游戏", "恋爱adv",
    "小说", "novel game", "sound novel", "サウンドノベル",
    "ノベルゲーム", "ビジュアルノベル",
}
NON_WORK = re.compile(
    r"(?i)(?:\bdlc\b|\bdemo\b|\btrial\b|\bpatch\b|\bexpansion\b|"
    r"\bfan.?disc\b|\bfandisc\b|\bfd\b|体験版|体验版|試玩版|试玩版|"
    r"ファンディスク|修正パッチ|追加パック|追加コンテンツ|"
    r"サウンドトラック|soundtrack|合集|合輯|collection|bundle|"
    r"complete edition|remaster|リマスター|リメイク)"
)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def existing_batch(registry, batch_id, audit_path):
    matches = [b for b in registry.get("batches", []) if b.get("id") == batch_id]
    if not matches:
        return False
    if len(matches) != 1 or not audit_path.exists():
        raise RuntimeError(f"{batch_id}: batch exists but audit is missing or duplicated")
    audit = load_json(audit_path)
    count = matches[0]["summary"]["promoted-basic"]
    assert audit["summary"]["newDistinctWorks"] == count
    assert sum(w.get("batch") == batch_id for w in registry["works"]) == count
    print("SKIP_EXISTING", batch_id, count, flush=True)
    return True


def nextmoe_page_bangumi_rank(page, limit, retry=4):
    """Use documented NextMoe page mode and a different source-specific ranking."""
    params = urllib.parse.urlencode({
        "page": page, "limit": limit, "sort": "rating_bangumi",
        "nsfw": "true", "include": "titles,refs"
    })
    request = urllib.request.Request(
        common.API + "?" + params,
        headers={"User-Agent": "NarrativeCatalogueImport/1.0 (public metadata; wt1234-donkey/visual-novel)",
                 "Accept": "application/json"}
    )
    for attempt in range(retry):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if payload.get("object") != "list" or not isinstance(payload.get("items"), list):
                raise RuntimeError("unexpected NextMoe v2 response shape")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            wait = min(90, max(5, int(exc.headers.get("Retry-After") or 0), (attempt + 1) * 8))
            print("NextMoe retry", exc.code, wait, flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry - 1:
                raise
            time.sleep((attempt + 1) * 7)


def run_round16(args):
    registry = load_json(REGISTRY)
    if existing_batch(registry, BATCH16, AUDIT16):
        return registry
    common.BATCH = BATCH16
    common.AUDIT = AUDIT16
    common.INDEX_PREFIX = INDEX16
    common.get_page = nextmoe_page_bangumi_rank
    common.run(argparse.Namespace(
        pages=args.nextmoe_pages, limit=100, max_new=args.max_new, delay=args.delay,
        dry_run=False
    ))
    result = load_json(REGISTRY)
    batch = next(b for b in result["batches"] if b["id"] == BATCH16)
    print("ROUND16_NEW", batch["summary"]["promoted-basic"], "TOTAL", len(result["works"]), flush=True)
    return result


def bangumi_get_page(offset, limit, retry=5):
    params = urllib.parse.urlencode({
        "type": 4, "cat": 4001, "sort": "rank",
        "limit": limit, "offset": offset
    })
    request = urllib.request.Request(
        BANGUMI_API + "?" + params,
        headers={
            "User-Agent": "NarrativeCatalogueResearch/1.0 (https://github.com/wt1234-donkey/visual-novel)",
            "Accept": "application/json"
        }
    )
    for attempt in range(retry):
        try:
            with urllib.request.urlopen(request, timeout=35) as response:
                payload = json.load(response)
            if not isinstance(payload.get("data"), list):
                raise RuntimeError("Bangumi v0 response lacks a data array")
            if not isinstance(payload.get("total"), int):
                raise RuntimeError("Bangumi v0 response lacks a numeric total")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == retry - 1:
                raise
            wait = min(120, max(8, int(exc.headers.get("Retry-After") or 0), (attempt + 1) * 10))
            print("Bangumi retry", exc.code, wait, flush=True)
            time.sleep(wait)
        except (urllib.error.URLError, TimeoutError):
            if attempt == retry - 1:
                raise
            time.sleep((attempt + 1) * 8)


def bangumi_tags(item):
    values = []
    for tag in item.get("tags") or []:
        if isinstance(tag, str):
            value = tag.strip()
        elif isinstance(tag, dict):
            value = str(tag.get("name") or "").strip()
        else:
            value = ""
        if value and value not in values:
            values.append(value)
    return values


def tag_kind(tags):
    folded = {x.casefold().strip() for x in tags}
    adv = sorted(folded & {x.casefold() for x in ADV_TAGS})
    rpg = sorted(folded & {x.casefold() for x in RPG_TAGS})
    narrative = sorted(folded & {x.casefold() for x in EXPLICIT_NARRATIVE})
    action = sorted(folded & {x.casefold() for x in ACTION_HEAVY})
    explicit_vn = folded & {
        "vn", "visual novel", "galgame", "gal game", "视觉小说", "視覺小說",
        "文字冒险", "文字冒險", "文字冒险游戏", "文字游戏", "互动小说",
        "互動小說", "乙女", "乙女游戏", "恋爱adv", "ノベルゲーム",
        "サウンドノベル", "ビジュアルノベル", "エロゲ", "美少女ゲーム",
        "ギャルゲー"
    }
    strong_narrative = folded & {x.casefold() for x in STRONG_NARRATIVE}
    hard_non_narrative = folded & {x.casefold() for x in HARD_NON_NARRATIVE}
    if hard_non_narrative and not strong_narrative and not explicit_vn:
        return None, []
    rpg_subgenre = folded & RPG_SUBGENRES
    # RPG requires a story-leaning subgenre (JRPG/CRPG/SRPG/DRPG) or
    # explicit narrative evidence. Generic RPG tags alone are too noisy:
    # they also occur on RTS, sandbox, action and multiplayer titles.
    if rpg and (rpg_subgenre or narrative) and (not action or narrative):
        return "RPG", sorted(set(rpg) | rpg_subgenre | set(narrative))
    # VN/interactive-fiction/otome tags are strong evidence. Generic ADV/AVG
    # tags are accepted only when the record is not dominated by action genres,
    # or when the same entry has an explicit narrative/story tag.
    if explicit_vn:
        return "ADV", sorted(set(adv) | set(explicit_vn) | set(narrative))
    if adv and (not action or narrative):
        return "ADV", sorted(set(adv) | set(narrative))
    return None, []


def bangumi_year(item):
    raw = item.get("date")
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


def bangumi_names(item):
    raw = [item.get("name_cn"), item.get("name")]
    names, seen = [], set()
    for value in raw:
        if not isinstance(value, str):
            continue
        value = value.strip()
        key = common.norm(value)
        if len(key) < 3 or len(value) > 180 or key in seen:
            continue
        seen.add(key)
        names.append(value)
    return names


def import_round17(args):
    registry = load_json(REGISTRY)
    matches = [b for b in registry.get("batches", []) if b.get("id") == BATCH17]
    if matches:
        if len(matches) != 1 or not AUDIT17.exists():
            raise RuntimeError("Round 17 existing batch has missing audit or duplicate markers")
        previous_audit = load_json(AUDIT17)
        if previous_audit.get("filterVersion") == 3:
            if existing_batch(registry, BATCH17, AUDIT17):
                return registry
        else:
            # Replace the first, deliberately broad tag-only pass before merge.
            old_count = sum(w.get("batch") == BATCH17 for w in registry["works"])
            assert old_count == matches[0]["summary"]["promoted-basic"]
            registry["works"] = [w for w in registry["works"] if w.get("batch") != BATCH17]
            for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
                registry["summary"][key] -= old_count
            registry["batches"] = [b for b in registry["batches"] if b.get("id") != BATCH17]
            assert registry["summary"]["accepted"] == len(registry["works"])
            write_json(REGISTRY, registry)
            print("REPLACED_PREVIOUS_ROUND17", old_count, "WITH_FILTER_VERSION_3", flush=True)
    batch16 = next((b for b in registry.get("batches", []) if b.get("id") == BATCH16), None)
    if batch16 is None:
        raise RuntimeError("Round 16 must be imported and audited before round 17")
    before = len(registry["works"])
    indexed = common.existing_index(registry)
    existing_bangumi = {
        str(ref) for w in registry["works"] for ref in w.get("sourceRefs", [])
        if isinstance(ref, str) and ref.startswith("bangumi:")
    }
    used_ids = {str(w["id"]) for w in registry["works"]}
    used_index = {str(w["indexId"]) for w in registry["works"]}
    additions, held, counts = [], [], Counter()
    seen_subject_ids = set()
    page_count = 0
    for page in range(args.bangumi_pages):
        offset = page * args.bangumi_limit
        payload = bangumi_get_page(offset, args.bangumi_limit)
        page_count += 1
        rows = payload["data"]
        if not rows:
            break
        for item in rows:
            counts["scanned"] += 1
            subject_id = str(item.get("id") or "")
            if not subject_id.isdecimal() or subject_id in seen_subject_ids:
                counts["invalid-or-repeated-subject-id"] += 1
                continue
            seen_subject_ids.add(subject_id)
            ref = "bangumi:" + subject_id
            if ref in existing_bangumi:
                counts["existing-bangumi-id"] += 1
                continue
            if item.get("type") not in (None, 4):
                counts["unexpected-subject-type"] += 1
                continue
            names = bangumi_names(item)
            if not names:
                counts["missing-title"] += 1
                continue
            if any(NON_WORK.search(name) for name in names):
                counts["edition-dlc-or-pack-held"] += 1
                if len(held) < 1500:
                    held.append({"id": subject_id, "title": names[0],
                                 "reviewReason": "Possible DLC, demo, fan disc, remake, remaster or compilation"})
                continue
            year = bangumi_year(item)
            if year is None:
                counts["missing-or-invalid-year"] += 1
                continue
            tags = bangumi_tags(item)
            kind, matched_tags = tag_kind(tags)
            if kind is None:
                counts["not-story-oriented-under-filter-v2"] += 1
                continue
            collisions = set()
            for name in names:
                collisions.update(indexed.get(common.norm(name), ()))
            if collisions:
                if any(c[1] == year for c in collisions):
                    counts["existing-work-matched"] += 1
                else:
                    counts["year-or-alias-conflict"] += 1
                    if len(held) < 1500:
                        held.append({"id": subject_id, "title": names[0], "year": year,
                                     "matches": sorted(collisions)[:10]})
                continue
            work_id = "bangumi-" + subject_id
            index_id = INDEX17 + subject_id
            if work_id in used_ids or index_id in used_index:
                counts["generated-id-collision"] += 1
                continue
            work = {
                "id": work_id,
                "indexId": index_id,
                "title": names[0],
                "aliases": names[1:],
                "firstYear": year,
                "gameplay": kind,
                "group": "Bangumi作品目录（创作品牌待核）",
                "source": "https://bgm.tv/subject/" + subject_id,
                "sourceRefs": [ref],
                "sourceTags": tags[:60],
                "matchedSourceTags": matched_tags,
                "sourcePlatform": item.get("platform"),
                "mainPlacement": "promoted-basic",
                "linkedRecordId": None,
                "creditScope": "Bangumi 官方 v0 条目目录的社区维护元数据；未据此断言具体开发、发行或创作职责。",
                "yearBasis": "Bangumi subject date；只登记来源所列年份，首发平台、地区与原始发行版次尚未独立核实。",
                "editorialScope": "基础身份层候选；ADV/RPG 分类依据 Bangumi 标签，叙事主次、剧情、创作者、版本差异与品质评价待后续核实。",
                "batch": BATCH17
            }
            additions.append(work)
            existing_bangumi.add(ref)
            used_ids.add(work_id)
            used_index.add(index_id)
            for name in names:
                indexed[common.norm(name)].add((work_id, year, "current-import"))
            if len(additions) >= args.max_new:
                break
        print("BANGUMI_PAGE", page + 1, "SCANNED", counts["scanned"],
              "ELIGIBLE_NEW", len(additions), flush=True)
        if len(additions) >= args.max_new or offset + len(rows) >= payload["total"]:
            break
        time.sleep(args.bangumi_delay)
    if not additions:
        raise RuntimeError("Bangumi scan found zero eligible new ADV/RPG identities; no empty batch will be written")
    registry["works"].extend(additions)
    inc = len(additions)
    for key in ("candidates", "accepted", "promotedBasic", "addedToMainIdentityLayer"):
        registry["summary"][key] += inc
    registry["updated"] = "2026-11-01"
    registry["batches"].append({
        "id": BATCH17,
        "source": BANGUMI_API,
        "review": str(AUDIT17.relative_to(ROOT)),
        "summary": {
            "candidates": inc, "scanned": counts["scanned"],
            **dict(counts), "promoted-basic": inc,
            "year-or-alias-conflict-held": counts["year-or-alias-conflict"]
        }
    })
    assert registry["summary"]["accepted"] == len(registry["works"])
    assert registry["summary"]["addedToMainIdentityLayer"] == (
        registry["summary"]["promotedBasic"] + registry["summary"]["promotedDossier"])
    assert len({w["id"] for w in registry["works"]}) == len(registry["works"])
    assert len({w["indexId"] for w in registry["works"]}) == len(registry["works"])
    audit = {
        "schema": 1,
        "filterVersion": 3,
        "date": "2026-11-01",
        "source": BANGUMI_API,
        "sourceDocs": "https://github.com/bangumi/server/blob/master/openapi/v0.yaml",
        "scope": "Bangumi type=4 game subjects, cat=4001 ordinary games; include only explicit ADV/VN/interactive-fiction or RPG tags; names and source-reported year only",
        "request": {"type": 4, "cat": 4001, "sort": "rank",
                    "pageSize": args.bangumi_limit, "pageCountCap": args.bangumi_pages,
                    "pagesFetched": page_count, "limitNew": args.max_new},
        "summary": {"scanned": counts["scanned"], "newDistinctWorks": inc,
                    "before": before, "after": len(registry["works"]), **dict(counts)},
        "records": [{
            "id": w["id"], "title": w["title"], "aliases": w["aliases"],
            "firstYear": w["firstYear"], "gameplay": w["gameplay"],
            "source": w["source"], "sourceRefs": w["sourceRefs"],
            "sourceTags": w["sourceTags"],
            "matchedSourceTags": w["matchedSourceTags"]
        } for w in additions],
        "heldForIdentityReview": held,
        "caveats": [
            "Bangumi is a community-maintained directory; title/date/tag fields are source assertions, not independent proof.",
            "Only ordinary game category 4001 was scanned; DLC/software/tabletop categories were not imported.",
            "ADV/RPG is a tag-based inclusion screen, not a completed narrative-priority assessment.",
            "Remakes, remasters, fan discs, demos, add-ons and collections are held when indicated by title.",
            "Names and year collisions are matched against complete main works, supplements, dossiers and the existing basic registry.",
            "No publisher, developer or creator role is inferred from the directory entry."
        ]
    }
    write_json(REGISTRY, registry)
    write_json(AUDIT17, audit)
    print("ROUND17_NEW", inc, "FINAL", len(registry["works"]), flush=True)
    return registry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--nextmoe-pages", type=int, default=100)
    parser.add_argument("--bangumi-pages", type=int, default=160)
    parser.add_argument("--bangumi-limit", type=int, default=50)
    parser.add_argument("--max-new", type=int, default=500)
    parser.add_argument("--delay", type=float, default=2.2)
    parser.add_argument("--bangumi-delay", type=float, default=1.3)
    args = parser.parse_args()
    assert 1 <= args.nextmoe_pages <= 100
    assert 1 <= args.bangumi_pages <= 300
    assert 1 <= args.bangumi_limit <= 100
    assert 1 <= args.max_new <= 500
    assert args.delay >= 2.0 and args.bangumi_delay >= 1.0
    registry = run_round16(args)
    registry = import_round17(args)
    for number, batch_id in ((16, BATCH16), (17, BATCH17)):
        batch = next(b for b in registry["batches"] if b["id"] == batch_id)
        print("ROUND", number, "ADDED", batch["summary"]["promoted-basic"], flush=True)
    print("FINAL_BASIC_COUNT", len(registry["works"]), flush=True)


if __name__ == "__main__":
    main()
