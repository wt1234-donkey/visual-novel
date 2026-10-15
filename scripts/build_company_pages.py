"""Build static, source-linked company dossiers from the shared catalogue."""
import argparse
import html
import json
from pathlib import Path
from source_urls import source_url_valid

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'data/games.json').read_text(encoding='utf-8'))
coverage = json.loads((ROOT / 'data/company-coverage.json').read_text(encoding='utf-8'))
works = {work['id']: work for work in data['works']}
escape = html.escape


def link(url, title):
    assert source_url_valid(url)
    return f'<a class="source-link" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(title)} ↗</a>'


def card(work, versions=None, anchors=(), version_label='个平台版本'):
    if versions is None:
        versions = [v for v in data['platformReleases'] if v['workId'] == work['id']]
    versions = sorted(versions, key=lambda v: v['year'])
    contents = work.get('contentVersions', [c for c in data['contentVersions'] if c['workId'] == work['id']])
    def release_row(v):
        voice_note = ' · 无角色配音' if v['voice'] == '无' else ''
        return f'''<div class="version release-row">
<div class="version-line"><strong>{v['year']}</strong><span class="platform-name">{escape(v['platform'])}</span><span class="version-kind">{escape(v['kind'])}</span></div>
<p class="publisher">发行／出版：{escape(v['publisher'])}{voice_note}</p>
<p class="changes">{escape(v['differences'])}</p>{link(v['source'], '发行来源')}</div>'''
    content_rows = []
    for c in sorted(contents, key=lambda c: c['firstYear']):
        associated = [v for v in versions if v['contentVersionId'] == c['id']]
        basis = '原作／首批内容' if c['basis'] == 'original' else '有新增内容'
        content_rows.append(f'''<section class="content-group"><h4 class="content-heading">{c['firstYear']} · {escape(c['label'])}</h4>
<p class="content-basis">{basis} · {escape(c['id'])}</p><p class="changes">{escape(c['evidence'])}</p>{link(c['source'], '内容依据')}
<details class="release-panel"><summary>关联平台发行 {len(associated)} 条</summary>{''.join(release_row(v) for v in associated)}</details></section>''')
    pending = [v for v in versions if not v['contentVersionId']]
    if pending:
        content_rows.append(f'''<details class="release-panel pending-releases"><summary>内容关系待核实：{len(pending)} 条历史发行（不计内容版本）</summary>
<p class="changes">保留旧发行证据；未确认新增内容，也不推定与原作完全相同。</p>{''.join(release_row(v) for v in pending)}</details>''')
    display_title = work.get('chineseTitle') or work['title']
    original_line = f'<p class="original">原名 · {escape(work["originalTitle"])}</p>' if display_title != work['originalTitle'] else ''
    if work.get('chineseTitleType') == '站内编辑译名':
        original_line = original_line.replace('</p>', ' · 中文名为站内编辑译名</p>')
    edition_credits = ''.join(
        f'<p class="character-evidence">相关发行（不重复计内容版本）：{credit["year"]} · '
        f'{escape(credit["platform"])} · {escape(credit["publisher"])}。'
        f'{escape(credit["reason"])}。{link(credit["source"], "发行依据")}</p>\n'
        for credit in work.get('editionCredits', []))
    legacy_anchors = ''.join(f'<span id="{escape(anchor, quote=True)}" aria-hidden="true"></span>' for anchor in anchors)
    return f'''<article class="card" id="{work['id']}">{legacy_anchors}
<div class="card-top"><span class="year">{work['firstYear']}</span><span class="category">{escape(work['category'])}</span></div>
<h3>{escape(display_title)}</h3>{original_line}
<p class="intro">{escape(work['synopsis'])}</p>
<div class="card-meta"><span>{escape(work['subcategory'])} · {escape(work['genre'])}</span><span>主要角色 · {escape(' / '.join(work['characters']))}</span></div>
{f'<p class="character-evidence">{link(work["charactersSource"], "角色依据")}{(" · " + escape(work["charactersNote"])) if work.get("charactersNote") else ""}</p>' if work.get('charactersSource') else ''}
{edition_credits}<details class="version-panel"><summary>查看 {len(contents)} 个内容版本 · {len(versions)} 条平台发行</summary><div class="version-list">{''.join(content_rows)}</div></details>
<div class="card-bottom">{link(work['source'], '作品来源')}<span class="card-note">{escape(work['notes'])}</span></div></article>'''


def build(company):
    selected = sorted((works[wid] for wid in company['workIds']), key=lambda w: (w['firstYear'], w['id']))
    related = sorted(company.get('relatedGames', []), key=lambda w: (w['firstYear'], w['id']))
    legacy_anchors = {}
    for anchor, wid in company.get('legacyAnchors', {}).items():
        legacy_anchors.setdefault(wid, []).append(anchor)
    count_versions = sum(v['workId'] in company['workIds'] for v in data['platformReleases']) + sum(len(g['platformReleases']) for g in related)
    count_contents = sum(c['workId'] in company['workIds'] for c in data['contentVersions']) + sum(len(g['contentVersions']) for g in related)
    toc = ''.join(f'<a href="#{w["id"]}"><span>{w["firstYear"]}</span>{escape(w.get("chineseTitle") or w["title"])}</a>'
                  for w in sorted(selected + related, key=lambda w: (w['firstYear'], w['id'])))
    related_by_id = {game['id']: game for game in related}
    audit_rows = []
    for item in company['entries']:
        references = ' / '.join([*(f'<a href="#{wid}">{escape(works[wid].get("chineseTitle") or works[wid]["title"])}</a>' for wid in item['workIds']),
                                *(f'<a href="#{rid}">{escape(related_by_id[rid]["title"])}</a>' for rid in item.get('relatedIds', []))])
        audit_rows.append(f'<tr><th scope="row">{escape(item["title"])}</th><td>{escape(item["status"])}</td><td>{escape(item["reason"])}<div>{references}</div></td><td>{link(item["source"], "来源")}</td></tr>')
    related_section = ''
    if related:
        related_section = f'''<section class="related-games" id="related-games"><div class="section-heading"><div><p class="eyebrow">OTHER GAMES</p><h2>{escape(company.get('relatedSectionTitle', '跨类型合作游戏'))}</h2></div><p>{len(related)} 部 · {escape(company.get('relatedCountLabel', '按官方类型标注'))}</p></div>
<p class="related-intro">{escape(company.get('relatedIntro', '涵盖官方年表收录的手机游戏、WFS 合作 RPG，以及 Index 制作、Key 官网宣传的授权作品。每款游戏按实际类型、发行公司与平台标注；顶部总数包含本节。'))}</p>
<div class="cards">{''.join(card(g, g['platformReleases'], version_label=company.get('versionPanelLabel', '个平台版本')) for g in related)}</div></section>'''
    section_title = company.get('sectionTitle') or (f"从 {selected[0]['title']} 到 {selected[-1]['title']}" if selected else '游戏作品核查')
    all_games = selected + related
    year_span = f"{min(w['firstYear'] for w in all_games)}—{max(w['firstYear'] for w in all_games)}" if all_games else '—'
    empty_note = f'<p class="scope-note">{escape(company.get("emptyWorksNote", "本次核查尚无可确认的游戏记录。"))}</p>' if not all_games else ''
    audit_label = company.get('auditLabel', f"官方作品清单 {company['catalogueEntryCount']} 项及范围说明。")
    audit_note = company.get('auditNote', '“核对完成”指上述清单中每项内容都有处理记录。未确认发售的项目和非游戏媒介不计入已发行游戏数。')
    audit_title = company.get('auditTitle', '官网目录核对清单')
    audit_source_label = company.get('auditSourceLabel', '官方产品目录')
    overview_label = company.get('overviewLabel', '已核实的相关游戏（含授权）' if related else '已核实的叙事作品')
    publisher_count = (f'<p class="scope-note"><strong>按实际发行署名：{len(company["publisherWorkIds"])} 部；'
                       f'按作品品牌：{len(selected)} 部。</strong></p>') if 'publisherWorkIds' in company else ''
    publisher_count = company.get('publisherWorkText', publisher_count)
    description = company.get('description', f"{company['name']} 叙事游戏作品专题：剧情、主要角色、首发年份、内容版本、平台发行与官方目录核对清单。")
    profile = company['creativeProfile']
    profile_rows = ''.join(f'''<article class="profile-phase"><span class="profile-period">{escape(phase['period'])}</span>
<h3>{escape(phase['heading'])}</h3><p>{escape(phase['analysis'])}</p>
<div class="profile-basis"><span>{escape(phase['basis'])}</span>{link(phase['source'], '阅读依据')}</div></article>''' for phase in profile['phases'])
    profile_section = f'''<section class="creative-profile" id="identity"><div class="section-heading"><div><p class="eyebrow">CREATIVE PROFILE</p><h2>作品怎样形成自己的风格</h2></div></div>
<p class="profile-lead">{escape(profile['thesis'])}</p><div class="profile-phases">{profile_rows}</div>
<p class="profile-caveat">时期划分是依据作品目录与厂商资料所做的编辑归纳；“厂商说明”引用其公开文字。“编辑观察”仅说明作品中可见的变化，不推断未经证实的经营或创作动机。</p></section>'''
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description)}">
<title>{escape(company['name'])} 作品专题 · 叙事游戏年鉴</title>
<link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="company.css"></head>
<body><div class="app-shell"><header class="masthead"><a class="brand" href="index.html"><span class="brand-mark">N.</span><span>叙事游戏年鉴</span></a><nav aria-label="专题导航"><a href="#identity">创作风格</a><a href="#works">全部作品</a><a href="#coverage">核对清单</a><a href="index.html#catalogue">返回数据库</a></nav></header>
<main><section class="company-hero"><p class="eyebrow">COMPANY DOSSIER · {escape(company['checkedAt'])}</p><h1>{escape(company['name'])} 作品专题</h1>
<p class="lead">{escape(company['publisherNote'])}</p>{publisher_count}
<div class="overview"><div><strong>{len(selected) + len(related)}</strong><span>{overview_label}</span></div><div><strong>{count_contents} / {count_versions}</strong><span>内容版本 / 平台发行</span></div><div><strong>{year_span}</strong><span>作品首发跨度</span></div></div>
<p class="scope-note">{escape(company['scope'])}</p><p class="scope-note">{escape(company['versionScope'])}</p>
<div class="hero-links"><a class="primary-link" href="#identity">阅读创作风格</a><a class="secondary-link" href="#works">按年份阅读作品</a></div></section>
<p class="scope-note">当前采用作品 → 内容版本 → 平台发行三层记录。同内容跨平台不增加内容版本；仅确认首次新增剧情、人物、路线、可玩内容、美术或音频时新增。内容关系待核的历史发行另列，不计为新增内容。下方旧核对说明中的版本数保留其当时口径。</p>
{profile_section}
<section id="works"><div class="section-heading"><div><p class="eyebrow">GAME CATALOGUE</p><h2>{escape(section_title)}</h2></div><p>{len(selected)} 部四类作品 · 增强版合并计数</p></div>
<nav class="work-index" aria-label="按年份跳转作品">{toc}</nav>{empty_note}<div class="cards">{''.join(card(w, anchors=legacy_anchors.get(w['id'], ()), version_label=company.get('versionPanelLabel', '个平台版本')) for w in selected)}</div></section>
{related_section}
<section class="company-audit" id="coverage"><p class="eyebrow">CATALOGUE AUDIT</p><h2>{escape(audit_title)}</h2>
<p>核对日期：{escape(company['checkedAt'])} · {escape(audit_label)} {link(company['source'], audit_source_label)}</p>
<p class="scope-note">{escape(audit_note)}</p>
<div class="audit-scroll"><table><thead><tr><th>官网项目／补充项目</th><th>处理</th><th>说明与对应作品</th><th>证据</th></tr></thead><tbody>{''.join(audit_rows)}</tbody></table></div></section>
</main><footer><span>{escape(company['name'])} 专题 · 与主数据库共用作品、内容版本和平台发行记录</span><a href="index.html#catalogue">返回数据库 ↑</a></footer></div></body></html>
'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Fail if generated pages are outdated')
    args = parser.parse_args()
    for company in coverage['companies']:
        target = ROOT / f'{company["id"]}.html'
        output = build(company)
        if args.check:
            assert target.read_text(encoding='utf-8') == output, f'{target.name} 未与 JSON 同步'
        else:
            target.write_text(output, encoding='utf-8')
        print(f'{target.name}: {len(company["workIds"]) + len(company.get("relatedGames", []))} 部相关游戏，已同步')
