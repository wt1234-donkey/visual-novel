"""Build human-readable entity directory and classification review without new work identities."""
import argparse
import csv
import io
import json
from collections import Counter,defaultdict
from pathlib import Path
from entity_model import MODEL,CREDITS,CLASSIFICATION,ENTITIES,DOSSIERS,POSITION,entity_link
from html import escape as e
ROOT=Path(__file__).resolve().parents[1]

def shell(title,body):
 return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} · 叙事游戏年鉴</title><link rel="stylesheet" href="styles.css?v=20261021-entities"><link rel="stylesheet" href="company.css?v=20261021-entities"><script type="module" src="entity-directory.mjs?v=20261021-entities"></script></head><body><div class="app-shell"><header class="masthead"><a class="brand" href="index.html">叙事游戏年鉴</a><nav><a href="index.html#catalogue">主库</a><a href="index.html#company-dossiers">公司与品牌专题</a><a href="entities.html">主体档案</a><a href="classification.html">作品分类审核</a></nav></header><main>{body}</main><footer>资料按已知证据整理；身份与具体参与职责分别核对。</footer></div></body></html>'''

def build():
 data=json.loads((ROOT/'data/games.json').read_text());coverage=json.loads((ROOT/'data/company-coverage.json').read_text())
 allworks={w['id']:w for w in data['works']}
 for c in coverage['companies']:
  for field in ['relatedGames','dossierOnlyWorks']:
   for w in c.get(field,[]):allworks.setdefault(w['id'],w)
 counts=Counter(x['type'] for x in MODEL['entities']);roles=defaultdict(lambda:defaultdict(set));member=defaultdict(list)
 for c in CREDITS['credits']:roles[c['entityId']][c['role']].add(c['workId'])
 for m in CREDITS['dossierMemberships']:member[m['workId']].append(m['dossierId'])
 summaries=' · '.join(f'{MODEL["typeLabels"][kind]} {n}' for kind,n in counts.items())
 body=f'<section class="company-hero"><h1>公司、品牌与制作主体档案</h1><p class="lead">同一作品可以关联多个主体；原作制作、品牌、发行、移植与授权分别记录。</p><p>{summaries}</p><p class="scope-note">身份待核的名称来自已保存的历史署名，尚不推定其为法人或品牌。统计为实体档案数，专题和角色作品数不相加。</p></section>'
 body+='<div class="directory-controls"><label>检索主体<input type="search" id="directory-search" placeholder="名称、别名、公司或品牌"></label><label>主体类型<select id="directory-kind"><option value="">全部类型</option>'+''.join(f'<option value="{k}">{v}</option>' for k,v in MODEL['typeLabels'].items() if k!='history')+'</select></label></div><p id="directory-count" aria-live="polite"></p><div class="entity-directory">'
 for entity in sorted(MODEL['entities'],key=lambda x:(x['type']=='unknown',x['name'].casefold())):
  eid=entity['id'];ds=[d for d in MODEL['dossiers'] if eid in d['entityIds']]
  sources=' '.join(f'<a class="source-link" href="{e(src,quote=True)}" target="_blank" rel="noopener noreferrer">资料 ↗</a>' for src in entity['sources'])
  related=[]
  for r in MODEL['relations']:
   if eid not in [r['from'],r['to']]:continue
   period=r['period'];period_text=(f'起点 {period["from"]}' if period.get('from') else '起点未核')+'；终点未核（不表示持续至今）'
   related.append(f'<li>{entity_link(r["from"])} → {entity_link(r["to"])}：{e(r["note"])}<span class="credit-scope">{period_text}</span><a class="source-link" href="{e(r["source"],quote=True)}" target="_blank" rel="noopener noreferrer">来源 ↗</a></li>')
  date_names={'established':'公司成立','brandStarted':'品牌启用','brandActivityStarted':'品牌活动起点','renamedBentenFilm':'更名BENTEN Film','renamedSierraOnLine':'更名Sierra On-Line'}
  precision_names={'year':'年级资料','month':'月级资料','day':'日级资料'}
  date_text=' · '.join(f'{date_names[x["kind"]]}：{x["value"]}（{precision_names[x["precision"]]}）' for x in entity['dates'])
  role_text=' · '.join(f'{e(MODEL["roleLabels"][role])} {len(ids)}部' for role,ids in roles[eid].items()) or '暂无已登记的具体作品职责'
  search=' '.join([entity['name'],*entity['aliases'],entity['historyNote']])
  body+=f'<article class="entity-record" id="{eid}" data-directory-kind="{entity["type"]}" data-search="{e(search,quote=True)}"><h2>{e(entity["name"])}<span class="entity-type">{MODEL["typeLabels"][entity["type"]]}</span></h2><p>检索名：{e(" / ".join(entity["aliases"]))}</p><p>{e(entity["historyNote"])}</p><p>{e(date_text)}</p><p>{role_text}</p><p class="scope-note">角色数按档案作品身份去重，含主库与专题关联；同作可有多个角色。</p><p><a href="index.html?participant={eid}#catalogue">在主库查询此主体</a>'+''.join(f' · <a href="{d["id"]}.html">{e(d["name"])}专题</a>' for d in ds)+f'</p>{sources}'+(f'<details><summary>所属与历史关系</summary><ul>{"".join(related)}</ul></details>' if related else '')+'</article>'
 body+='</div>';out={'entities.html':shell('主体档案',body)}
 main_count=len(data['works']);related_count=sum(len(c.get('relatedGames',[])) for c in coverage['companies']);bibliography_count=sum(len(c.get('dossierOnlyWorks',[])) for c in coverage['companies'])
 body=f'<section class="company-hero"><h1>作品位置与分类审核</h1><p class="lead">作品位置、叙事主次、互动方式与厂商关系分开记录。本轮保留既有主库、关联和书目位置；未因ADV、RPG、问答或文字输入标签自动增删作品。</p><p>主库{main_count:,}部 · 关联记录{related_count}条 · 仅专题书目{bibliography_count}条。后两项为原有专题记录数，未经身份核对不能相加作为独立作品总数。</p><p><a href="data/work-classification.json">下载逐作审核记录</a> · <a href="data/entity-model.md">查看分类规则</a></p></section>'
 body+='<div class="directory-controls"><label>查找作品<input type="search" id="directory-search" placeholder="作品名称或互动方式"></label><label>当前收录位置<select id="directory-kind"><option value="">全部位置</option>'+''.join(f'<option value="{k}">{v}</option>' for k,v in POSITION.items())+'</select></label></div><p id="directory-count" aria-live="polite"></p><div class="audit-scroll"><table><thead><tr><th>作品</th><th>当前位置</th><th>互动方式</th><th>本轮处理与依据</th></tr></thead><tbody>'
 for p in sorted(CLASSIFICATION['placements'],key=lambda p:(allworks[p['workId']]['firstYear'],p['workId'])):
  w=allworks[p['workId']];name=w.get('chineseTitle') or w['title'];dossiers=member[w['id']];url=f'{dossiers[0]}.html#{w["id"]}' if dossiers else 'index.html#catalogue'
  text=f'{name} {w["originalTitle"]} '+ ' '.join(w['interactionModes'])
  body+=f'<tr class="classification-row" data-directory-kind="{p["placement"]}" data-search="{e(text,quote=True)}"><th scope="row"><a href="{url}">{e(name)}</a><small>{w["firstYear"]} · {e(w["originalTitle"])}</small></th><td>{POSITION[p["placement"]]}</td><td>{e("、".join(w["interactionModes"]))}</td><td>{e(p["reason"])}<a class="source-link" href="{e(p["source"],quote=True)}" target="_blank" rel="noopener noreferrer">现有作品依据 ↗</a></td></tr>'
 body+='</tbody></table></div>';out['classification.html']=shell('作品分类审核',body)
 rows=io.StringIO();writer=csv.writer(rows,lineterminator='\n');writer.writerow(['参与记录ID','实体ID','名称','实体类型','作品ID','目标层级','目标ID','参与角色','署名原文','核查依据','来源'])
 for c in CREDITS['credits']:
  entity=ENTITIES[c['entityId']];writer.writerow([c['id'],entity['id'],entity['name'],MODEL['typeLabels'][entity['type']],c['workId'],c['targetType'],c['targetId'],MODEL['roleLabels'][c['role']],c['rawCredit'],c['status'],c['source']])
 out['data/entity-credits.csv']='\ufeff'+rows.getvalue()
 main_ids={w['id'] for w in data['works']}
 public_model={k:MODEL[k] for k in ['typeLabels','roleLabels','relations','dossiers']}
 public_model['entities']=[{k:v for k,v in item.items() if k in ['id','name','type','aliases']} for item in MODEL['entities']]
 compact_credits=[{k:v for k,v in c.items() if k not in ['note','territory','id']} for c in CREDITS['credits'] if c['workId'] in main_ids]
 out['data/entity-catalogue.json']=json.dumps({'model':public_model,'credits':compact_credits,'dossierMemberships':[m for m in CREDITS['dossierMemberships'] if m['workId'] in main_ids]},ensure_ascii=False,separators=(',',':'))+'\n'
 return out

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
 for path,value in build().items():
  target=ROOT/path
  if args.check:assert target.read_text(encoding='utf-8')==value,f'{path} 未同步'
  else:target.write_text(value,encoding='utf-8')
  print(path)
