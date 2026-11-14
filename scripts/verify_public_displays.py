"""Compare rendered title/year contracts with the current effective projection."""
import argparse,csv,json
from html.parser import HTMLParser
from pathlib import Path
from effective_catalogue import load_effective,effective_title
ROOT=Path(__file__).resolve().parents[1]
class Rows(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.active=None;self.depth=0;self.capture=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if self.active is None and ((tag=='article' and 'card' in a.get('class','').split() and a.get('id')) or (tag=='tr' and a.get('data-work-id'))):
   self.active={'id':a.get('data-work-id',a.get('id')),'title':'','year':''};self.depth=1;return
  if self.active is not None:
   if tag not in ['br','img','input','hr','meta','link','wbr']:self.depth+=1
   if tag=='h3' or (tag=='a' and self.active['title']==''):self.capture='title'
   if 'year' in a.get('class','').split() or tag=='small':self.capture='year'
 def handle_endtag(self,tag):
  if self.active is None:return
  if tag in ['h3','a','span','small']:self.capture=None
  self.depth-=1
  if self.depth==0:self.rows.append(self.active);self.active=None
 def handle_data(self,data):
  if self.active is not None and self.capture:self.active[self.capture]+=data

def verify(site,root=ROOT):
 effective=load_effective(root); main={w['id']:w for w in effective['main']['works']}; allworks=dict(main);counts={'dossierRows':0,'classificationRows':0,'organizationRows':0,'csvRows':0}
 for company in effective['coverage']['companies']:
  for field in ['relatedGames','dossierOnlyWorks']:
   for w in company.get(field,[]):allworks.setdefault(w['id'],w)
 for company in effective['coverage']['companies']:
  expected={**main,**{w['id']:w for field in ['relatedGames','dossierOnlyWorks'] for w in company.get(field,[])}}
  parser=Rows();parser.feed((site/(company['id']+'.html')).read_text())
  for row in parser.rows:
   w=expected[row['id']];assert row['title']==effective_title(w),(company['id'],row['id'],'title',row['title'],effective_title(w));assert row['year']==str(w['firstYear']),(company['id'],row['id'],'year',row['year'],w['firstYear']);counts['dossierRows']+=1
 parser=Rows();parser.feed((site/'classification.html').read_text())
 assert len(parser.rows)>1000,'classification work identities must remain addressable'
 for row in parser.rows:
  w=allworks[row['id']];assert row['title']==effective_title(w),(row['id'],'classification title');assert row['year'].split(' · ')[0]==str(w['firstYear']),(row['id'],'classification year');counts['classificationRows']+=1
 organizations=json.loads((site/'data/organizations.json').read_text())
 for id,row in organizations['works'].items():
  w=allworks[id];assert row['title']==effective_title(w) and row['year']==w['firstYear'],(id,'organization display');counts['organizationRows']+=1
 for name in ['versions.csv','platform-releases.csv','content-versions.csv']:
  for row in csv.DictReader((site/'data'/name).open(encoding='utf-8-sig')):
   assert row['作品名称']==effective_title(main[row['作品ID']]),(name,row['作品ID'],'CSV title');counts['csvRows']+=1
 assert min(counts.values())>0
 return counts
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--site',type=Path,default=ROOT);p.add_argument('--report',type=Path,default=ROOT/'test-results/public-displays.json');a=p.parse_args();counts=verify(a.site.resolve());a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps({'schemaVersion':1,'passed':True,**counts},indent=2)+'\n');print(counts)
