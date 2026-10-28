"""Rendering helpers for typed entities, scoped credits and dossier membership."""
import html
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MODEL=json.loads((ROOT/'data/entities.json').read_text())
CREDITS=json.loads((ROOT/'data/credits.json').read_text())
CLASSIFICATION=json.loads((ROOT/'data/work-classification.json').read_text())
ENTITIES={e['id']:e for e in MODEL['entities']}
DOSSIERS={d['id']:d for d in MODEL['dossiers']}
PLACEMENTS={p['workId']:p for p in CLASSIFICATION['placements']}
MEMBERSHIPS={(m['dossierId'],m['workId']):m for m in CREDITS['dossierMemberships']}
WORK_CREDITS=defaultdict(list)
for c in CREDITS['credits']:WORK_CREDITS[c['workId']].append(c)
ESC=html.escape
GROUPS={'original':'本品牌／原作制作','cooperation':'联合制作与创作合作','release':'发行、代理与移植','licensed':'授权、监修与版权关联','unresolved':'其他专题关联／职责待核','reference':'归属纠正／历史对照'}
POSITION={'main':'主库引用','related':'叙事／跨类型关联','bibliography':'仅专题书目'}

def entity_link(eid):
 e=ENTITIES[eid]
 return f'<a href="entities.html#{ESC(eid)}">{ESC(e["name"])}<span class="entity-type">{ESC(MODEL["typeLabels"][e["type"]])}</span></a>'

def card_details(work,versions):
 wid=work['id'];releases={v['id'] for v in versions};contents={v['contentVersionId'] for v in versions if v['contentVersionId']}
 rows=[];seen=set()
 for c in WORK_CREDITS[wid]:
  if c['targetType']=='release' and c['targetId'] not in releases:continue
  if c['targetType']=='content' and c['targetId'] not in contents:continue
  key=(c['entityId'],c['role'],c['targetType'])
  if key in seen:continue
  seen.add(key)
  scope={'work':'原作／作品','content':'对应新增内容','release':'对应平台发行','edition':'独立核对的限定版次'}[c['targetType']]
  evidence='本轮来源核对' if c['status']=='sourceReviewed' else '沿用既有资料'
  review_note=(f'<p class="scope-note">{ESC(c["note"])} <a href="{ESC(c["reviewRecord"],quote=True)}">核查记录 {ESC(c["reviewId"])}</a></p>' if c.get('reviewRecord') else '')
  rows.append(f'<li>{entity_link(c["entityId"])} · {ESC(MODEL["roleLabels"][c["role"]])}<span class="credit-scope">{scope} · {evidence}</span> <a class="source-link" href="{ESC(c["source"],quote=True)}" target="_blank" rel="noopener noreferrer">依据 ↗</a>{review_note}</li>')
 placement=PLACEMENTS[wid]
 intro=f'<p class="catalogue-placement">{POSITION[placement["placement"]]} · 沿用既有收录，叙事主次未在本轮重新评定。</p>'
 if not rows:return intro+'<p class="credit-pending">参与职责尚待核实，详见作品原始资料。</p>'
 return intro+f'<details class="entity-credits"><summary>制作、品牌与发行关系 · {len(rows)}项</summary><ul>{"".join(rows)}</ul><p class="scope-note">角色分别作用于原作、增补内容或具体发行；品牌归属不等于开发或历史发行归属。</p></details>'

def dossier_identity(company):
 d=DOSSIERS[company['id']];subjects=set(d['entityIds']);rels=[]
 for r in MODEL['relations']:
  if r['from'] not in subjects and r['to'] not in subjects:continue
  label={'operatedBy':'运营关系','brandFamily':'品牌家族关系'}[r['type']]
  rels.append(f'<li>{entity_link(r["from"])} → {entity_link(r["to"])} · {label}。{ESC(r["note"])} <a class="source-link" href="{ESC(r["source"],quote=True)}" target="_blank" rel="noopener noreferrer">来源 ↗</a></li>')
 return (f'<section class="dossier-identity"><p class="entity-badge">{ESC(MODEL["typeLabels"][d["dossierType"]])}</p><p>{" / ".join(entity_link(eid) for eid in d["entityIds"])}</p>'
 '<p class="scope-note">公司、品牌与参与角色分别记录。下方按作品与本专题的关系分组；旧发行原文保留。</p>'
 + (f'<details><summary>所属品牌与历史关系</summary><ul>{"".join(rels)}</ul><p class="scope-note">起止未核的关系不表示历年持续有效；详见主体档案。</p></details>' if rels else '')+'</section>')

def membership_description(cid,wid):
 m=MEMBERSHIPS[(cid,wid)]
 if m['group']=='reference':return '专题归属纠正：本作保留历史对照锚点，未登记该主体的具体参与职责。'
 return '专题关系：'+'、'.join(MODEL['roleLabels'][role] for role in m['roles'])+'。'
