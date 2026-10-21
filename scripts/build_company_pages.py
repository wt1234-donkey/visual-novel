"""Build static, source-linked company dossiers from the shared catalogue."""
import argparse
import html
import json
import re
from pathlib import Path
from source_urls import source_url_valid
from entity_model import MODEL, DOSSIERS, MEMBERSHIPS, GROUPS, POSITION, card_details, dossier_identity, membership_description
from entity_names import display_name

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / 'data/games.json').read_text(encoding='utf-8'))
coverage = json.loads((ROOT / 'data/company-coverage.json').read_text(encoding='utf-8'))
works = {work['id']: work for work in data['works']}
gameplay_catalogues = json.loads((ROOT / 'data/gameplay-catalogues.json').read_text(encoding='utf-8'))
escape = html.escape

NAV_START = '<!-- company-dossiers:start -->'
NAV_END = '<!-- company-dossiers:end -->'


def build_dossier_navigation(index):
    """Group homepage dossier links by their earliest main-catalogue work."""
    if NAV_START in index:
        before, rest = index.split(NAV_START, 1)
        previous, after = rest.split(NAV_END, 1)
    else:
        old = re.search(r'<div class="company-quick" aria-label="厂商专题">.*?</div></div>', index)
        assert old, '首页缺少厂商专题导航'
        before, previous, after = index[:old.start()], old.group(), index[old.end():]
    companies = {company['id']: company for company in coverage['companies']}
    grouped = {}
    for cid, company in companies.items():
        year = min((works[wid]['firstYear'] for wid in company['workIds']), default=None)
        period = year // 5 * 5 if year is not None else None
        kind = DOSSIERS[cid]['dossierType']
        name = {'legend_entertainment':'Legend Entertainment（美国）','te_soft':'T&E SOFT（日本）'}.get(cid,DOSSIERS[cid]['name'])
        anchor = f'<a class="secondary-link" href="{cid}.html">{escape(name)}</a>'
        grouped.setdefault(period, []).append((year, name.casefold(), cid, anchor, kind))
    sections = []
    for period in sorted(grouped, key=lambda year: year if year is not None else float('inf')):
        title = f'{period}—{period + 4}' if period is not None else '暂无主库作品'
        period_id = str(period) if period is not None else 'undated'
        items = []
        for year, _, cid, anchor, kind in sorted(grouped[period], key=lambda item: (item[0] or 9999, item[1], item[2])):
            year_label = str(year) if year is not None else '未归年'
            items.append(f'<div class="dossier-item" role="listitem" data-company="{cid}" data-first-year="{year or ""}" data-kind="{kind}">{anchor}<span class="entity-type">{escape(MODEL["typeLabels"][kind])}</span><span class="dossier-first-year">{year_label}</span></div>')
        sections.append(f'<section class="dossier-period" aria-labelledby="dossier-period-{period_id}"><h4 id="dossier-period-{period_id}">{title}<span>{len(items)}个专题</span></h4><div class="dossier-links" role="list">{"".join(items)}</div></section>')
    filters = '<div class="dossier-type-controls" role="group" aria-label="按专题类型筛选">' + ''.join(
        f'<button type="button" data-dossier-kind="{kind}" aria-pressed="{str(not kind).lower()}">{label}</button>'
        for kind, label in [('', '全部'), ('brand', '品牌'), ('company', '公司／组织'), ('team', '制作团队'), ('publication', '刊物'), ('history', '沿革专题')]) + '</div>'
    navigation = ('<section class="company-dossiers" id="company-dossiers" aria-label="公司与品牌专题">'
                  '<h3>公司与品牌专题</h3><p class="dossier-order-note">按专题关联的主库作品最早原作首发年排序，每5年一组；此年不代表公司成立、品牌启用或首次参与发行。未有主库作品的专题单列。</p>'
                  f'{filters}<p id="dossier-filter-count" aria-live="polite">{len(companies)}个专题</p>'
                  f'<div class="dossier-periods">{"".join(sections)}</div></section>')
    return before + NAV_START + '\n        ' + navigation + '\n        ' + NAV_END + after


def link(url, title):
    assert source_url_valid(url)
    return f'<a class="source-link" href="{escape(url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(title)} ↗</a>'


def card(work, versions=None, anchors=(), version_label='个平台版本', context_label='', context_note='', catalogue_only=False):
    if versions is None:
        versions = [v for v in data['platformReleases'] if v['workId'] == work['id']]
    versions = sorted(versions, key=lambda v: v['year'])
    contents = work.get('contentVersions', [c for c in data['contentVersions'] if c['workId'] == work['id']])
    def release_row(v):
        voice_note = ' · 无角色配音' if v['voice'] == '无' else ''
        name = display_name(v['publisher'])
        raw_note = f'<p class="credit-scope">署名原文：{escape(v["publisher"])}</p>' if name != v['publisher'] else ''
        return f'''<div class="version release-row">
<div class="version-line"><strong>{v['year']}</strong><span class="platform-name">{escape(v['platform'])}</span><span class="version-kind">{escape(v['kind'])}</span></div>
<p class="publisher">发行／出版：{escape(name)}{voice_note}</p>{raw_note}
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
    interaction_tags = ''.join(f'<span class="interaction-tag{" pending-tag" if mode == "待核实" else ""}">{escape(mode)}</span>' for mode in work['interactionModes'])
    interaction_evidence = f'<details class="interaction-evidence"><summary>互动方式依据 · {escape(work["interactionBasis"])}</summary><p class="changes">{escape(work["interactionNote"])}</p>{" ".join(link(url, "玩法资料") for url in work["interactionSources"])}</details>'
    legacy_anchors = ''.join(f'<span id="{escape(anchor, quote=True)}" aria-hidden="true"></span>' for anchor in anchors)
    version_panel = ('<p class="scope-note">仅专题收录 · 含文字输入玩法，不新增至主数据库。</p>' if catalogue_only else
                     f'<details class="version-panel"><summary>查看 {len(contents)} 个内容版本 · {len(versions)} 条平台发行</summary><div class="version-list">{"".join(content_rows)}</div></details>')
    context = f'<p class="scope-note">{escape(context_note)}</p>' if context_note else ''
    return f'''<article class="card" id="{work['id']}">{legacy_anchors}
<div class="card-top"><span class="year">{work['firstYear']}</span><span class="category">{escape(work['category'])}{' · ' + escape(context_label) if context_label else ''}</span></div>
<h3>{escape(display_title)}</h3>{original_line}{context}
<p class="intro">{escape(work['synopsis'])}</p>
{card_details(work, versions)}
<div class="interaction-tags" aria-label="互动方式">{interaction_tags}</div>{interaction_evidence}
<div class="card-meta"><span>{escape(work['subcategory'])} · {escape(work['genre'])}</span><span>主要角色 · {escape(' / '.join(work['characters']))}</span></div>
{f'<p class="character-evidence">{link(work["charactersSource"], "角色依据")}{(" · " + escape(work["charactersNote"])) if work.get("charactersNote") else ""}</p>' if work.get('charactersSource') else ''}
{edition_credits}{version_panel}
<div class="card-bottom">{link(work['source'], '作品来源')}<span class="card-note">{escape(work['notes'])}</span></div></article>'''


def gameplay_appendix(company):
    """Reference tables do not add catalogue works or change admission rules."""
    appendix = gameplay_catalogues['companies'].get(company['id'])
    if not appendix:
        return ''
    local = {**{wid: works[wid] for wid in company['workIds']},
             **{w['id']: w for w in company.get('relatedGames', [])},
             **{w['id']: w for w in company.get('dossierOnlyWorks', [])}}
    related_ids = {w['id'] for w in company.get('relatedGames', [])}
    dossier_ids = {w['id'] for w in company.get('dossierOnlyWorks', [])}
    groups = []
    for index, group in enumerate(appendix['groups'], 1):
        rows = []
        for item in group['rows']:
            if 'workId' in item:
                w = local[item['workId']]
                name = w.get('chineseTitle') or w['title']
                title = f'<a href="#{escape(w["id"], quote=True)}">{escape(name)}</a>'
                if name != w['originalTitle']:
                    title += f'<br><span class="original">{escape(w["originalTitle"])}</span>'
                kind = w['subcategory'] + ' · ' + w['genre'].replace('／角色与探索', '').replace('／探索与故事背景', '')
                relation = ('正文 · 仅专题书目' if w['id'] in dossier_ids else
                            '正文 · 跨类型／关联项目' if w['id'] in related_ids else '正文 · 主库引用')
                note = company.get('workContexts', {}).get(w['id'], '')
                if w['id'] in related_ids:
                    note = note or w['notes']
                controls = '、'.join(w['interactionModes'])
                note = f'互动方式：{controls}。' + note
                source = w['source']
                source_label = '作品资料'
            else:
                assert item['title'] and item['type'] and item['relation']
                title = escape(item['title'])
                if anchor := item.get('anchor'):
                    assert anchor in local, '附录作品锚点不在本专题'
                    title = f'<a href="#{escape(anchor, quote=True)}">{title}</a>'
                kind, relation, note = item['type'], item['relation'], item.get('note', '')
                source = item.get('source', group['source'])
                source_label = '资料' if 'source' in item else '分组资料'
            details = escape(relation) + (f'<p>{escape(note)}</p>' if note else '')
            rows.append(f'<tr><th scope="row">{title}</th><td>{escape(kind)}</td><td>{details}</td><td>{link(source, source_label)}</td></tr>')
        groups.append(f'<section id="gameplay-group-{index}"><h3>{escape(group["title"])}</h3>'
                      f'<p class="scope-note">{escape(group.get("note", ""))}</p>'
                      '<div class="audit-scroll"><table><thead><tr><th>作品／项目</th><th>玩法／游戏类型</th><th>专题关系与说明</th><th>资料</th></tr></thead>'
                      f'<tbody>\n{"\n".join(rows)}\n</tbody></table></div></section>')
    count = sum(len(g['rows']) for g in appendix['groups'])
    return (f'<section class="company-audit gameplay-appendix" id="gameplay-catalogue"><p class="eyebrow">GAMEPLAY REFERENCE · {escape(appendix.get("updated", gameplay_catalogues["updated"]))}</p>'
            f'<h2>{escape(appendix["title"])}</h2><p>{escape(appendix["scope"])}</p>'
            f'<p class="scope-note">{count}个清单项目 · {len(appendix["groups"])}组。{escape(gameplay_catalogues["note"])}</p>'
            '<p class="scope-note">类型为此前清单与现有资料的玩法概览，不宣称本次对每个平台逐项重新验证。分组资料用于目录与归属参考；具体操作依据见有正文记录的作品。未逐项核定的年份不补造。</p>'
            f'{"\n".join(groups)}</section>')


def build(company):
    company = {**company, 'name': DOSSIERS[company['id']]['name']}
    selected = sorted((works[wid] for wid in company['workIds']), key=lambda w: (w['firstYear'], w['id']))
    related = sorted(company.get('relatedGames', []), key=lambda w: (w['firstYear'], w['id']))
    dossier_only = company.get('dossierOnlyWorks', [])
    legacy_anchors = {}
    for anchor, wid in company.get('legacyAnchors', {}).items():
        legacy_anchors.setdefault(wid, []).append(anchor)
    count_versions = sum(v['workId'] in company['workIds'] for v in data['platformReleases']) + sum(len(g['platformReleases']) for g in related)
    count_contents = sum(c['workId'] in company['workIds'] for c in data['contentVersions']) + sum(len(g['contentVersions']) for g in related)
    toc = ''.join(f'<a href="#{w["id"]}"><span>{w["firstYear"]}</span>{escape(w.get("chineseTitle") or w["title"])}</a>'
                  for w in sorted(selected + related + dossier_only, key=lambda w: (w['firstYear'], w['id'])))
    related_by_id = {game['id']: game for game in related}
    dossier_by_id = {game['id']: game for game in dossier_only}
    audit_rows = []
    for item in company['entries']:
        references = ' / '.join([*(f'<a href="#{wid}">{escape(works[wid].get("chineseTitle") or works[wid]["title"])}</a>' for wid in item['workIds']),
                                *(f'<a href="#{rid}">{escape(related_by_id[rid]["title"])}</a>' for rid in item.get('relatedIds', [])),
                                *(f'<a href="#{did}">{escape(dossier_by_id[did]["title"])}</a>' for did in item.get('dossierIds', []))])
        audit_rows.append(f'<tr><th scope="row">{escape(item["title"])}</th><td>{escape(item["status"])}</td><td>{escape(item["reason"])}<div>{references}</div></td><td>{link(item["source"], "来源")}</td></tr>')
    related_section = ''
    if related:
        related_section = f'''<section class="related-games" id="related-games"><div class="section-heading"><div><p class="eyebrow">OTHER GAMES</p><h2>{escape(company.get('relatedSectionTitle', '跨类型合作游戏'))}</h2></div><p>{len(related)} 部 · {escape(company.get('relatedCountLabel', '按官方类型标注'))}</p></div>
<p class="related-intro">{escape(company.get('relatedIntro', '涵盖官方年表收录的手机游戏、WFS 合作 RPG，以及 Index 制作、Key 官网宣传的授权作品。每款游戏按实际类型、发行公司与平台标注；顶部总数包含本节。'))}</p>
<div class="cards">{''.join(card(g, g['platformReleases'], version_label=company.get('versionPanelLabel', '个平台版本')) for g in related)}</div></section>'''
    section_title = company.get('sectionTitle') or (f"从 {selected[0]['title']} 到 {selected[-1]['title']}" if selected else '游戏作品核查')
    all_games = selected + related + dossier_only
    year_span = f"{min(w['firstYear'] for w in all_games)}—{max(w['firstYear'] for w in all_games)}" if all_games else '—'
    empty_note = f'<p class="scope-note">{escape(company.get("emptyWorksNote", "本次核查尚无可确认的游戏记录。"))}</p>' if not all_games else ''
    audit_label = company.get('auditLabel', f"官方作品清单 {company['catalogueEntryCount']} 项及范围说明。")
    audit_note = company.get('auditNote', '“核对完成”指上述清单中每项内容都有处理记录。未确认发售的项目和非游戏媒介不计入已发行游戏数。')
    audit_title = company.get('auditTitle', '官网目录核对清单')
    audit_source_label = company.get('auditSourceLabel', '官方产品目录')
    overview_label = company.get('overviewLabel', '已核实的相关游戏（含授权）' if related else '已核实的叙事作品')
    publisher_count = (f'<p class="scope-note"><strong>按实际发行署名：{len(company["publisherWorkIds"])} 部；'
                       f'专题主库引用：{len(selected)} 部。</strong></p>') if 'publisherWorkIds' in company else ''
    publisher_count = company.get('publisherWorkText', publisher_count)
    description = company.get('description', f"{company['name']} 叙事游戏作品专题：剧情、主要角色、首发年份、内容版本、平台发行与官方目录核对清单。")
    profile = company['creativeProfile']
    profile_rows = ''.join(f'''<article class="profile-phase"><span class="profile-period">{escape(phase['period'])}</span>
<h3>{escape(phase['heading'])}</h3><p>{escape(phase['analysis'])}</p>
<div class="profile-basis"><span>{escape(phase['basis'])}</span>{link(phase['source'], '阅读依据')}</div></article>''' for phase in profile['phases'])
    profile_section = f'''<section class="creative-profile" id="identity"><div class="section-heading"><div><p class="eyebrow">CREATIVE PROFILE</p><h2>作品怎样形成自己的风格</h2></div></div>
<p class="profile-lead">{escape(profile['thesis'])}</p><div class="profile-phases">{profile_rows}</div>
<p class="profile-caveat">时期划分是依据作品目录与厂商资料所做的编辑归纳；“厂商说明”引用其公开文字。“编辑观察”仅说明作品中可见的变化，不推断未经证实的经营或创作动机。</p></section>'''
    work_cards = '<div class="cards">' + ''.join(card(w, anchors=legacy_anchors.get(w['id'], ()), version_label=company.get('versionPanelLabel', '个平台版本')) for w in selected) + '</div>'
    if company.get('workGroups'):
        grouped_ids = [wid for group in company['workGroups'] for wid in group['workIds']]
        assert len(grouped_ids) == len(set(grouped_ids)) and set(grouped_ids) == set(company['workIds']), '专题分期必须完整且不重复覆盖作品'
        work_cards = ''.join(
            f'<section class="dossier-period" id="{escape(group["id"], quote=True)}"><h3>{escape(group["title"])}</h3><p class="scope-note">{escape(group["description"])}</p><div class="cards">'
            + ''.join(card(w, anchors=legacy_anchors.get(w['id'], ()), context_label=group.get('cardLabel', ''))
                      for w in sorted((works[wid] for wid in group['workIds']), key=lambda w: (w['firstYear'], w['id'])))
            + '</div></section>' for group in company['workGroups'])
    if company.get('dossierGroups'):
        all_by_id = {w['id']: w for w in all_games}
        grouped_ids = [wid for group in company['dossierGroups'] for wid in group['workIds']]
        assert len(grouped_ids) == len(set(grouped_ids)) and set(grouped_ids) == set(all_by_id), '专题分组必须完整且不重复覆盖全部作品'
        contexts = company.get('workContexts', {})
        def dossier_card(wid, label):
            w = all_by_id[wid]
            return card(w, w.get('platformReleases') if wid in related_by_id else None,
                        context_label=label, context_note=contexts.get(wid, ''), catalogue_only=wid in dossier_by_id)
        work_cards = ''.join(
            f'<section class="dossier-period" id="{escape(group["id"], quote=True)}"><h3>{escape(group["title"])}</h3><p class="scope-note">{escape(group["description"])}</p><div class="cards">'
            + ''.join(dossier_card(wid, group.get('cardLabel', '')) for wid in group['workIds'])
            + '</div></section>' for group in company['dossierGroups'])
        related_section = ''
    # Group once by scoped participation; keep every historical card and URL anchor.
    by_id = {w['id']: w for w in all_games}
    legacy_groups = [*company.get('workGroups', []), *company.get('dossierGroups', [])]
    legacy_navigation = ''
    if legacy_groups:
        legacy_navigation = '<details class="legacy-groups"><summary>原目录分期与范围说明</summary>' + ''.join(
            f'<div id="{escape(group["id"])}"><h4>{escape(group["title"])}</h4><p>{escape(group["description"])}</p>'
            + ' / '.join(f'<a href="#{escape(wid)}">{escape(by_id[wid].get("chineseTitle") or by_id[wid]["title"])}</a>' for wid in group['workIds']) + '</div>'
            for group in legacy_groups) + '</details>'
    old_card_labels = {wid:g.get('cardLabel','') for g in legacy_groups for wid in g['workIds']}
    legacy_navigation += ''.join(f'<p class="scope-note">{escape(company.get(key, ""))}</p>' for key in ['relatedSectionTitle','relatedIntro'])
    grouped_cards = []
    for group_id, group_title in GROUPS.items():
        group_works = sorted((w for w in all_games if MEMBERSHIPS[(company['id'], w['id'])]['group'] == group_id), key=lambda w: (w['firstYear'], w['id']))
        if not group_works: continue
        cards = []
        for w in group_works:
            member = MEMBERSHIPS[(company['id'], w['id'])]
            note = membership_description(company['id'], w['id']) + ' ' + company.get('workContexts', {}).get(w['id'], '')
            rendered = card(w, w.get('platformReleases') if w['id'] in related_by_id else ([] if w['id'] in dossier_by_id else None),
                            anchors=legacy_anchors.get(w['id'], ()), context_label=POSITION[member['placement']] + (' · ' + old_card_labels[w['id']] if old_card_labels.get(w['id']) else ''), context_note=note,
                            catalogue_only=w['id'] in dossier_by_id, version_label=company.get('versionPanelLabel', '个平台版本'))
            modes = '|'.join(w['interactionModes'])
            cards.append(f'<div class="dossier-card-wrapper" data-placement="{member["placement"]}" data-relation="{group_id}" data-modes="{escape(modes, quote=True)}">{rendered}</div>')
        grouped_cards.append(f'<section class="participation-group" id="participation-{group_id}" data-participation-group="{group_id}"><h3>{group_title}<span class="group-count">{len(group_works)}部</span></h3><div class="cards">{"".join(cards)}</div></section>')
    modes = sorted({mode for w in all_games for mode in w['interactionModes']})
    dossier_filters = '<div class="dossier-filters"><label>作品位置<select data-dossier-filter="placement"><option value="">全部位置</option>' + ''.join(f'<option value="{key}">{value}</option>' for key,value in POSITION.items()) + '</select></label>'
    dossier_filters += '<label>参与关系<select data-dossier-filter="relation"><option value="">全部关系</option>' + ''.join(f'<option value="{key}">{value}</option>' for key,value in GROUPS.items()) + '</select></label>'
    dossier_filters += '<label>互动方式<select data-dossier-filter="mode"><option value="">全部互动</option>' + ''.join(f'<option>{escape(mode)}</option>' for mode in modes) + '</select></label></div><p id="dossier-result-count" aria-live="polite"></p>'
    work_cards = dossier_filters + legacy_navigation + ''.join(grouped_cards)
    related_section = '<span id="related-games" aria-hidden="true"></span>' if related else ''
    historical_section = ''
    if archive := company.get('historicalArchive'):
        path = Path(archive['path'])
        assert path.parts[0] == 'data' and '..' not in path.parts and (ROOT / path).is_file(), '历史存档路径不正确'
        archived_links = ''.join(f'<li id="{escape(w["id"], quote=True)}">{escape(w["title"])}</li>' for w in archive['works'])
        historical_section = f'<details class="scope-note" id="historical-archive"><summary>{escape(archive["title"])}</summary><p>{escape(archive["note"])}</p><a href="{escape(archive["path"], quote=True)}">查看完整历史记录（JSON）</a><ul>{archived_links}</ul></details>'
    appendix = gameplay_appendix(company)
    appendix_nav = '<a href="#gameplay-catalogue">玩法总表</a>' if appendix else ''
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{escape(description)}">
<title>{escape(company['name'])} 作品专题 · 叙事游戏年鉴</title>
<link rel="stylesheet" href="styles.css?v=20261021-entities"><link rel="stylesheet" href="company.css?v=20261021-entities"><script type="module" src="dossiers.mjs?v=20261021-entities"></script></head>
<body><div class="app-shell"><header class="masthead"><a class="brand" href="index.html"><span class="brand-mark">N.</span><span>叙事游戏年鉴</span></a><nav aria-label="专题导航"><a href="#identity">创作风格</a><a href="#works">全部作品</a><a href="#coverage">核对清单</a>{appendix_nav}<a href="index.html#catalogue">返回数据库</a></nav></header>
<main><section class="company-hero"><p class="eyebrow">COMPANY DOSSIER · {escape(company['checkedAt'])}</p><h1>{escape(company['name'])} 作品专题</h1>
<p class="lead">{escape(company['publisherNote'])}</p>{publisher_count}
<div class="overview"><div><strong>{len(all_games)}</strong><span>{overview_label}</span></div><div><strong>{count_contents} / {count_versions}</strong><span>{escape(company.get('contentCountLabel', '内容版本 / 平台发行'))}</span></div><div><strong>{escape(company.get('yearSpanLabel', year_span))}</strong><span>{escape(company.get('yearSpanCaption', '作品首发跨度'))}</span></div></div>
<p class="scope-note">{escape(company['scope'])}</p><p class="scope-note">{escape(company['versionScope'])}</p>
<div class="hero-links"><a class="primary-link" href="#identity">阅读创作风格</a><a class="secondary-link" href="#works">按年份阅读作品</a></div></section>
<p class="scope-note">互动方式为可多选的作品层玩法概览，各平台操作可能不同；依据现有资料归纳，操作不明时标待核实。<a href="index.html#interaction-guide">查看互动方式定义</a> · <a href="data/interaction-modes.csv">下载互动清单</a>。</p>
<p class="scope-note">当前采用作品 → 内容版本 → 平台发行三层记录。同内容跨平台不增加内容版本；仅确认首次新增剧情、人物、路线、可玩内容、美术或音频时新增。内容关系待核的历史发行另列，不计为新增内容。下方旧核对说明中的版本数保留其当时口径。</p>
{dossier_identity(company)}
{profile_section}
<section id="works"><div class="section-heading"><div><p class="eyebrow">GAME CATALOGUE</p><h2>{escape(section_title)}</h2></div><p>{len(selected)} 部主库引用 · {len(related)} 部关联 · {len(dossier_only)} 部书目</p></div>
<nav class="work-index" aria-label="按年份跳转作品">{toc}</nav>{empty_note}{work_cards}</section>
{related_section}{historical_section}
<section class="company-audit" id="coverage"><p class="eyebrow">CATALOGUE AUDIT</p><h2>{escape(audit_title)}</h2>
<p>核对日期：{escape(company['checkedAt'])} · {escape(audit_label)} {link(company['source'], audit_source_label)}</p>
<p class="scope-note">{escape(audit_note)}</p>
<div class="audit-scroll"><table><thead><tr><th>官网项目／补充项目</th><th>处理</th><th>说明与对应作品</th><th>证据</th></tr></thead><tbody>{''.join(audit_rows)}</tbody></table></div></section>{appendix}
</main><footer><span>{escape(company.get('footerNote', company['name'] + ' 专题 · 与主数据库共用作品、内容版本和平台发行记录'))}</span><a href="index.html#catalogue">返回数据库 ↑</a></footer></div></body></html>
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
        print(f'{target.name}: {len(company["workIds"]) + len(company.get("relatedGames", [])) + len(company.get("dossierOnlyWorks", []))} 部相关游戏，已同步')
    index_path = ROOT / 'index.html'
    index = index_path.read_text(encoding='utf-8')
    ordered_index = build_dossier_navigation(index)
    if args.check:
        assert index == ordered_index, '首页专题链接未按主库最早作品年份分组'
    else:
        index_path.write_text(ordered_index, encoding='utf-8')
    print('index.html: 专题链接按主库最早作品年份分组，已同步')
