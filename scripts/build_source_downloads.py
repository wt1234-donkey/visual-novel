"""Public download directory; leaves every original file and URL unchanged."""
from html import escape
from pathlib import Path
from urllib.parse import quote
import argparse

ROOT=Path(__file__).resolve().parents[1]


def render(root):
    root=Path(root)
    groups={'.csv':('CSV索引',[]),'.json':('数据与索引',[]),'.md':('历史核验与来源说明',[]),'.b64':('来源快照',[])}
    for path in sorted((root/'data').rglob('*')):
        if not path.is_file() or path.suffix not in groups or {'basic-web','catalogue-web'}&set(path.relative_to(root).parts):
            continue
        name=path.relative_to(root).as_posix()
        if name.startswith('data/audit-ledger/objects/'):
            continue  # Internal immutable index objects are reached through the archive manifest.
        groups[path.suffix][1].append(f'<li><a href="{quote(name,safe="/")}" download>{escape(name)}</a><span>{path.stat().st_size:,} B</span></li>')
    count=sum(len(rows) for _,rows in groups.values())
    body=''.join(f'<details{(" open" if suffix==".csv" else "")}><summary>{label} · {len(rows)}项</summary><ul>{"".join(rows)}</ul></details>' for suffix,(label,rows) in groups.items())
    return ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>来源与历史资料下载 · 叙事游戏年鉴</title><style>body{font:16px/1.6 system-ui,sans-serif;color:#203344;background:#f7f5ee;margin:0}main{max-width:1100px;margin:auto;padding:28px}a{color:#215b78;overflow-wrap:anywhere}nav{display:flex;gap:20px;flex-wrap:wrap}details{border-top:1px solid #ccd4d8;padding:16px 0}summary{cursor:pointer;font-weight:650}ul{padding-left:20px}li{margin:10px 0}li span{display:block;color:#586875;font-size:13px}</style></head><body><main><nav><a href="index.html">作品发现</a><a href="minimal-adv-rpg.html">基础作品库</a><a href="catalogue.html">高级检索</a></nav>'
            f'<h1>来源与历史资料下载</h1><p>共{count}项公开资料。原始来源、历史核验记录与CSV索引保留原格式和下载路径；来源记录不等同于当前有效显示值。基础源库清单与其分片需配套使用。</p>{body}</main></body></html>\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    content=render(ROOT);target=ROOT/'sources.html'
    if args.check:
        if not target.exists() or target.read_text()!=content:raise SystemExit('Source download directory is stale')
    else:target.write_text(content)
