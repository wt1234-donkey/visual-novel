#!/usr/bin/env python3
"""Append a reviewed project batch without rebuilding or truncating earlier identities."""
import argparse
import hashlib
import json
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH = 'project-narrative-round3-20261031'
SEED = 'data/adv-rpg-round3-candidates-20261031.json'
REGISTRY = 'data/main-adv-rpg-works-20261031.json'
REVIEW = 'data/adv-rpg-round3-review-20261031.json'
REPORT = 'data/adv-rpg-round3-review-20261031.md'


def read(path):
    return json.loads((ROOT / path).read_text(encoding='utf-8'))


def norm(text):
    return ''.join(c for c in unicodedata.normalize('NFKC', str(text or '')).casefold() if c.isalnum())


def keys(work):
    titles = [work.get(k, '') for k in ('title', 'originalTitle', 'chineseTitle')]
    titles += work.get('aliases', []) + work.get('titleAliases', [])
    return {norm(part) for title in titles for part in [title, *re.split(r'\s+/\s+', title)] if norm(part)}


def resolve(row, index):
    """Exact documented aliases and year; ambiguity is held, never resolved by fuzzy similarity."""
    hits = {}
    for key in keys(row):
        for wid, year, location in index.get(key, []):
            hits.setdefault(wid, (year, location))
    if not hits:
        return None, None
    exact = [(wid, loc) for wid, (year, loc) in hits.items() if year == row['year']]
    primary = [(wid, loc) for wid, loc in exact if loc in ('complete-main', 'primary-identity')]
    if len(primary) == 1 and all(loc == 'supplement-complete' or wid == primary[0][0] for wid, loc in exact):
        exact = primary
    if len(exact) != 1:
        raise ValueError('同名身份或年份冲突：' + repr(hits))
    return exact[0]


def build():
    registry = read(REGISTRY)
    # Rebuild only this batch. Previous identities and decisions remain byte-equivalent objects.
    registry['works'] = [w for w in registry['works'] if w.get('batch') != BATCH]
    registry['identityReview'] = [w for w in registry['identityReview'] if w.get('batch') != BATCH]
    registry['batches'] = [b for b in registry.get('batches', []) if b['id'] != BATCH]
    seed = read(SEED)
    index = defaultdict(list)
    for location, works in [
        ('complete-main', read('data/games.json')['works']),
        ('primary-identity', registry['works']),
        ('supplement-complete', read('data/non-rpg-creator-supplement-20261030.json')['works']),
        ('company-dossier', [w for c in read('data/company-coverage.json')['companies']
                             for field in ('relatedGames', 'dossierOnlyWorks') for w in c.get(field, [])]),
    ]:
        for work in works:
            for key in keys(work):
                index[key].append((work['id'], work['firstYear'], location))
    base_ids = {w['id'] for w in registry['works']}
    before = len(base_ids)
    decisions = []
    seen = set()
    for row in seed['records']:
        marker = (norm(row['title']), row['year'])
        assert marker not in seen
        seen.add(marker)
        assert row['source'].startswith('https://') and row['gameplayNote']
        iid = 'round3-' + hashlib.sha256(f'{marker[0]}|{marker[1]}'.encode()).hexdigest()[:16]
        decision = {**row, 'indexId': iid, 'registryId': None, 'batch': BATCH}
        if row['selection'] == 'defer':
            decision['status'] = 'identity-review' if row['reviewType'] == 'edition-versus-work' else 'eligibility-review'
            registry['identityReview'].append({**decision, 'firstYear': row['year']})
        else:
            assert row['gameplay'] in {'ADV', '视觉小说', '互动电影ADV', 'RPG', 'SRPG', 'ARPG'}
            try:
                wid, location = resolve(row, index)
                if row.get('expectedWorkId') and wid != row['expectedWorkId']:
                    raise ValueError('Explicit reviewed identity does not match aliases')
            except ValueError as error:
                decision.update(status='identity-review', reason=str(error), reviewType='identity-or-year')
                registry['identityReview'].append({**decision, 'firstYear': row['year']})
                decisions.append(decision)
                continue
            if wid in base_ids:
                decision.update(status='linked-existing-registry', registryId=wid)
            else:
                placement = ('existing-complete' if location in ('complete-main', 'supplement-complete')
                             else 'promoted-dossier' if wid else 'promoted-basic')
                wid = wid or 'basic-narr-' + hashlib.sha256(f'{marker[0]}|{marker[1]}'.encode()).hexdigest()[:16]
                entry = {
                    'id': wid, 'indexId': iid, 'title': row['title'], 'aliases': row.get('aliases', []),
                    'firstYear': row['year'], 'gameplay': row['gameplay'], 'gameplayNote': row['gameplayNote'],
                    'group': row['group'], 'source': row['source'], 'mainPlacement': placement,
                    'linkedRecordId': wid if location else None, 'batch': BATCH,
                    'creditScope': 'Project list association only; no developer or publisher role is inferred.',
                    'editorialScope': 'Title, original year, dominant gameplay and sources only; detailed narrative and content editions await separate review.',
                }
                for field in ('additionalSources', 'evidenceLevel', 'associationNote'):
                    if field in row:
                        entry[field] = row[field]
                registry['works'].append(entry)
                base_ids.add(wid)
                for key in keys(entry):
                    index[key].append((wid, row['year'], 'primary-identity'))
                decision.update(status=placement, registryId=wid)
        decisions.append(decision)
    counts = Counter(d['status'] for d in decisions)
    assert len(base_ids) == len(registry['works'])
    summary = {'candidates': len(decisions), 'newToRegistry': len(base_ids) - before, **dict(counts)}
    registry['batches'].append({'id': BATCH, 'source': SEED, 'review': REVIEW, 'summary': summary})
    placements = Counter(w['mainPlacement'] for w in registry['works'])
    registry['summary'].update(
        candidates=267 + sum(b['summary']['candidates'] for b in registry['batches']),
        accepted=len(registry['works']), existingComplete=placements['existing-complete'],
        promotedDossier=placements['promoted-dossier'], promotedBasic=placements['promoted-basic'],
        identityReview=len(registry['identityReview']),
        addedToMainIdentityLayer=placements['promoted-dossier'] + placements['promoted-basic'],
    )
    review = {'schema': 1, 'batch': BATCH, 'reviewedAt': '2026-10-31',
              'policy': seed['policy'], 'summary': summary, 'records': decisions}
    lines = ['# 第三批项目厂商叙事作品筛选（2026-10-31）', '',
             '按既有厂商清单逐作筛选，仅补名称、原作首年、主要玩法与来源。复用已有ID，厂商清单关联不等于制作或发行署名。', '',
             '## 本批结果', '', '| 处理结果 | 数量 |', '|---|---:|']
    labels = {'promoted-basic': '全新基础作品身份', 'promoted-dossier': '专题身份纳入主库发现',
              'existing-complete': '已有完整主库，追加清单关联', 'linked-existing-registry': '此前主库身份已存在',
              'identity-review': '版本或身份待核', 'eligibility-review': '叙事与玩法主次待核'}
    lines += [f'| {labels[k]} | {v} |' for k, v in counts.items()]
    lines += [f'| 合计 | {len(decisions)} |', '', '## 逐作清单', '',
              '| 厂商清单组 | 作品 | 原作年 | 主要玩法 | 结果 | 来源 |', '|---|---|---:|---|---|---|']
    for d in decisions:
        lines.append(f"| {d['group']} | {d['title']} | {d['year']} | {d['gameplay']}：{d['gameplayNote']} | {labels[d['status']]} | [资料]({d['source']}) |")
    lines += ['', '## 待核及范围说明', '']
    lines += [f"- **{d['title']}**：{d['reason']}" for d in decisions if d.get('reason')]
    lines += ['', '- 名侦探皮卡丘按2016首次内容建立一个作品身份；2018剧情扩充不另建新作品，具体增补版次留待后续考据。',
              '- Nintendo清单中的Metal Slader Glory原作归属HAL；本批不将Nintendo清单关联误写为原作发行或开发。',
              '- BS探侦俱乐部按1997首次广播登记，三篇合一；未声称现存ROM包含完整广播声音。',
              '- Endonesia保留冒险RPG类型，以无常规战斗、无经验值、人物交流与情感谜题为本批叙事优先依据。',
              '- 其他以战斗、养成、策略或随机地牢循环为主要体验的RPG不因有剧情而自动准入。',
              '- 本批基础身份已进入首页作品发现与基础作品表，不等于完整剧情、创作者和内容版本档案已完成。', '']
    return {REGISTRY: registry, REVIEW: review, REPORT: '\n'.join(lines)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    for path, content in build().items():
        rendered = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2) + '\n'
        if args.check:
            assert (ROOT / path).read_text(encoding='utf-8') == rendered, f'Stale generated file: {path}'
        else:
            (ROOT / path).write_text(rendered, encoding='utf-8')
    print('Third narrative batch verified' if args.check else 'Third narrative batch appended')


if __name__ == '__main__':
    main()
