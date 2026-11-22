#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Download ALL VNDB visual novels from official Kana API and export CSV/JSONL.

Python 3.10+, stdlib only. Read-only: this script never changes the Git repository.
Run: python3 export_all_vndb.py --out vndb-full-export --repo .

Source: https://api.vndb.org/kana
"""
from __future__ import annotations
import argparse, csv, datetime as dt, hashlib, json, re, sqlite3, sys, time, unicodedata, urllib.error, urllib.request, zipfile
from collections import defaultdict, Counter
from pathlib import Path

API = "https://api.vndb.org/kana/vn"
STATS = "https://api.vndb.org/kana/stats"
SOURCE_FILE = "data/main-adv-rpg-works-20261031.json"
FIELDS = "title,alttitle,aliases,titles{lang,title,latin,official,main},released,olang,devstatus,languages,platforms,developers{id,name},length_minutes,rating,votecount"
HEADERS = ["vID", "VNDB主标题", "原文标题", "多语言标题", "别名", "首发日期", "首发年份", "原始语言", "可用语言", "平台", "开发者（VNDB关联）", "开发状态", "平均游玩分钟", "评分（10-100）", "投票数", "VNDB链接", "基础身份库关联", "基础身份库ID"]
RE_ID = re.compile(r"^v([1-9][0-9]*)$", re.I)
RE_REF = re.compile(r"^vndb[:\-]v([1-9][0-9]*)$", re.I)
RE_URL = re.compile(r"^https?://(?:www\.)?vndb\.org/v([1-9][0-9]*)(?:[/?#].*)?$", re.I)
USER_AGENT = "VNDB-complete-catalogue-export/1.0 (academic inventory research; contact via VNDB forum)"


def normalized_id(value):
    if not isinstance(value, str):
        return None
    val = value.strip()
    for pattern in (RE_ID, RE_REF, RE_URL):
        matched = pattern.fullmatch(val)
        if matched:
            return "v" + str(int(matched.group(1)))
    return None


def local_ids(source_path=None, source_archive=None):
    if source_archive:
        with zipfile.ZipFile(source_archive) as z:
            content = z.read(SOURCE_FILE)
    elif source_path and source_path.exists():
        content = source_path.read_bytes()
    else:
        return None, {}
    raw = json.loads(content)
    works = raw.get("works")
    if not isinstance(works, list):
        raise ValueError("本地快照中缺少 works 列表")
    mapping = defaultdict(set)
    for w in works:
        if not isinstance(w, dict):
            raise ValueError("works 存在非对象条目")
        possible = [w.get(k) for k in ("id", "indexId", "vndbId", "vndbID", "vndb_id", "vndb", "source")]
        possible += w.get("sourceRefs") or []
        for x in possible:
            vid = normalized_id(x)
            if vid:
                mapping[vid].add(str(w.get("id", "")))
    meta = {"works": len(works), "unique_vIDs": len(mapping), "local_sha256": hashlib.sha256(content).hexdigest()}
    return meta, mapping


def request_json(url, body=None, retries=6):
    payload = None if body is None else json.dumps(body, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    for n in range(retries):
        req = urllib.request.Request(url, data=payload, headers={
            "Content-Type": "application/json", "Accept": "application/json", "User-Agent": USER_AGENT},
            method="POST" if payload else "GET")
        try:
            with urllib.request.urlopen(req, timeout=75) as response:
                return json.load(response)
        except urllib.error.HTTPError as e:
            message = e.read().decode("utf-8", errors="replace")
            if e.code in (429, 500, 502, 503, 504) and n < retries - 1:
                retry_after = e.headers.get("Retry-After", "")
                delay = int(retry_after) if retry_after.isdigit() else min(60, (n+1)*8)
                print(f"服务端暂时不可用 HTTP {e.code}，退避后重试", file=sys.stderr, flush=True)
                time.sleep(delay)
                continue
            raise RuntimeError(f"VNDB HTTP {e.code}: {message[:1500]}\n请求参数: {body}") from e
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if n == retries - 1:
                raise RuntimeError(f"访问 VNDB 失败: {e}") from e
            time.sleep(min(60, (n+1)*8))


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE IF NOT EXISTS vn (id_num INTEGER PRIMARY KEY, json TEXT NOT NULL)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    conn.commit()
    return conn


def setting(conn, key, default=None):
    rec = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    return json.loads(rec[0]) if rec else default


def persist_page(conn, entries, more):
    # Insert results and checkpoint together in one atomic transaction.
    prev = setting(conn, "last_id_num", 0)
    last = prev
    data = []
    for e in entries:
        value = normalized_id(e.get("id"))
        if not value:
            raise RuntimeError("官方记录缺少有效 vID: " + repr(e.get("id")))
        num = int(value[1:])
        if num <= last:
            raise RuntimeError("官方分页排序异常：vID 未严格升序")
        last = num
        data.append((num, json.dumps(e, ensure_ascii=False, separators=(",", ":"))))
    if not data and more:
        raise RuntimeError("官方返回空结果但 more=true；停止以避免漏采")
    with conn:
        conn.executemany("INSERT INTO vn(id_num,json) VALUES(?,?)", data)
        conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", ("last_id_num", json.dumps(last)))
        if not more:
            conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", ("complete", "true"))
            conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", ("finished_utc", json.dumps(dt.datetime.now(dt.timezone.utc).isoformat())))
    return last


def collect(conn, interval):
    if setting(conn, "complete", False):
        print("已存在完整官方目录检查点，跳过网络采集。", flush=True)
        return
    last = setting(conn, "last_id_num", 0)
    while True:
        query = {"fields": FIELDS, "sort": "id", "results": 100}
        if last:
            query["filters"] = ["id", ">", "v" + str(last)]
        page = request_json(API, query)
        rows = page.get("results")
        more = page.get("more")
        if not isinstance(rows, list) or not isinstance(more, bool):
            raise RuntimeError("VNDB 响应缺少有效的 results/more 字段")
        if not more:
            expected = (setting(conn, "initial_stats", {}) or {}).get("vn")
            actual = conn.execute("SELECT COUNT(*) FROM vn").fetchone()[0] + len(rows)
            if actual == 0:
                raise RuntimeError("官方 API 返回零条记录，拒绝标记为完整")
            if isinstance(expected, int) and abs(actual - expected) > max(100, int(expected * 0.01)):
                raise RuntimeError(f"官方扫描结果 {actual} 条，与统计接口 {expected} 差异过大；拒绝标记完整")
        last = persist_page(conn, rows, more)
        current = conn.execute("SELECT COUNT(*) FROM vn").fetchone()[0]
        if current % 1000 == 0 or not more:
            print(f"VNDB 已读取 {current:,} 条；最后 vID v{last}", flush=True)
        if not more:
            return
        time.sleep(interval)


def safe_spreadsheet_text(v):
    # Prevent spreadsheet formula injection while leaving the original JSON untouched.
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        return v
    s = str(v)
    if s.startswith(("=", "+", "-", "@", "\t", "\r", "\n")):
        return "'" + s
    return s


def join(items):
    if isinstance(items, list):
        return " | ".join(str(x) for x in items if x is not None)
    return ""


def flatten_titles(titles):
    rows = []
    for t in titles or []:
        if not isinstance(t, dict):
            continue
        title = t.get("title") or ""
        latin = t.get("latin") or ""
        lang = t.get("lang") or "?"
        status = "主标题" if t.get("main") else ""
        rows.append(f"[{lang}] {title}" + (f" ({latin})" if latin else "") + (f" {status}" if status else ""))
    return " | ".join(rows)


def to_row(v, local):
    vid = normalized_id(v.get("id"))
    rel = v.get("released") or ""
    year = rel[:4] if isinstance(rel, str) and re.match(r"^\d{4}", rel) else ""
    devers = v.get("developers") or []
    names = []
    for d in devers:
        if isinstance(d, dict):
            name = d.get("name")
            if name:
                names.append(str(name))
    status = {0: "已完成", 1: "开发中", 2: "已取消"}.get(v.get("devstatus"), "未知")
    ids = sorted(local.get(vid, [])) if local is not None else []
    answer = [vid or "", v.get("title") or "", v.get("alttitle") or "",
              flatten_titles(v.get("titles")), join(v.get("aliases")), rel, year,
              v.get("olang") or "", join(v.get("languages")), join(v.get("platforms")),
              join(names), status, v.get("length_minutes"), v.get("rating"),
              v.get("votecount"), f"https://vndb.org/{vid}",
              "已关联" if ids else ("未关联" if local is not None else "未比对"), join(ids)]
    return [safe_spreadsheet_text(x) for x in answer]


def write_csv(path, header, rows):
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)


def export(conn, out, local_meta, local):
    if not setting(conn, "complete", False):
        raise RuntimeError("官方 VNDB 全量采集尚未完成，因此不生成伪装成完整目录的文件")
    totals = conn.execute("SELECT COUNT(*) FROM vn").fetchone()[0]
    official = out / "VNDB_全作品.csv"
    missing = out / "VNDB_未关联基础身份库_vID.csv"
    raw = out / "VNDB_原始记录.jsonl"
    stats = Counter()
    with official.open("w", newline="", encoding="utf-8-sig") as fo, \
         missing.open("w", newline="", encoding="utf-8-sig") as fm, \
         raw.open("w", encoding="utf-8") as fj:
        all_writer = csv.writer(fo)
        missing_writer = csv.writer(fm)
        all_writer.writerow(HEADERS)
        missing_writer.writerow(HEADERS)
        for (source,) in conn.execute("SELECT json FROM vn ORDER BY id_num"):
            item = json.loads(source)
            flattened = to_row(item, local)
            all_writer.writerow(flattened)
            fj.write(json.dumps(item, ensure_ascii=False) + "\n")
            stats["all"] += 1
            if local is not None and flattened[-2] == "未关联":
                missing_writer.writerow(flattened)
                stats["missing"] += 1
            elif local is not None:
                stats["linked"] += 1
    if stats["all"] != totals:
        raise RuntimeError("导出后的数量与缓存不一致")
    summary = {
        "official_source": API,
        "stats_source": STATS,
        "official_record_count": totals,
        "scan_finished_utc": setting(conn, "finished_utc"),
        "local_meta": local_meta,
        "official_linked_in_local": stats.get("linked", 0) if local is not None else None,
        "official_unlinked_in_local": stats.get("missing", 0) if local is not None else None,
        "important_note": "未关联 vID 不等于该游戏确实不存在于本地库；需审查别名和版本。",
        "fields": FIELDS,
        "csv_encoding": "UTF-8 with BOM",
    }
    (out / "导出说明.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print("全量目录：", official, f"({totals:,} 条)")
    if local is not None:
        print("基础库无显式 vID 关联：", missing, f"({stats['missing']:,} 条)")
    print("原始 JSONL：", raw)
    return summary


def selftest():
    import tempfile
    sample = [
        {"id": "v1", "title": "Example", "alttitle": "例", "aliases": ["Alias"], "released": "2000", "titles": [], "devstatus": 0},
        {"id": "v8", "title": "=formula", "released": "2001-03", "titles": [], "devstatus": 1},
    ]
    with tempfile.TemporaryDirectory() as t:
        path = Path(t)
        db = connect(path / "tmp.sqlite3")
        persist_page(db, sample[:1], True)
        assert setting(db, "last_id_num") == 1 and not setting(db, "complete", False)
        persist_page(db, sample[1:], False)
        assert setting(db, "complete", False)
        meta = export(db, path, {"works": 1}, {"v1": {"local-1"}})
        assert meta["official_record_count"] == 2
        assert meta["official_linked_in_local"] == 1
        assert meta["official_unlinked_in_local"] == 1
        with (path / "VNDB_全作品.csv").open(encoding="utf-8-sig", newline="") as f:
            rows = list(csv.reader(f))
            assert len(rows) == 3 and rows[2][1] == "'=formula"
        db.close()
    print("SELFTEST PASSED: checkpoint, export, vID difference, CSV formula safety")


def main():
    parser = argparse.ArgumentParser(description="VNDB 官方全作品导出和可选的本地基础库 vID 对比")
    parser.add_argument("--repo", type=Path, default=Path("."), help="本地 Git 仓库，默认当前目录")
    parser.add_argument("--archive", type=Path, help="上传过的基础库 ZIP 快照；优先于仓库文件")
    parser.add_argument("--out", type=Path, default=Path("vndb-full-export"))
    parser.add_argument("--interval", type=float, default=2.0, help="请求之间的间隔（秒），至少1.6秒")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--fresh", action="store_true", help="删除旧缓存重新扫描官方 API")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return
    if args.interval < 1.6:
        parser.error("--interval 至少为 1.6 秒，以避免请求过快")
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    db_path = out / "vndb_official_cache.sqlite3"
    if args.fresh and db_path.exists():
        db_path.unlink()
    conn = connect(db_path)
    try:
        local_path = args.repo / SOURCE_FILE
        meta, local = local_ids(local_path, args.archive)
        print("本地库：", meta if meta is not None else "没有提供；只生成 VNDB 全量目录")
        if not setting(conn, "started_utc"):
            with conn:
                conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", ("started_utc", json.dumps(dt.datetime.now(dt.timezone.utc).isoformat())))
        if not setting(conn, "complete", False):
            try:
                stats = request_json(STATS)
                with conn:
                    conn.execute("INSERT OR REPLACE INTO settings VALUES(?,?)", ("initial_stats", json.dumps(stats)))
                print("扫描前 VNDB 官方 VN 总量：", stats.get("vn"))
            except Exception as e:
                print("统计端点暂不可用，仍尝试正文目录：", e, file=sys.stderr)
        collect(conn, args.interval)
        export(conn, out, meta, local if meta else None)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
