"""Verify published ancestry or replay frozen generators; never rewrite raw Git objects."""
import copy,hashlib,io,json,os,subprocess,sys,tarfile,tempfile
from functools import lru_cache
from pathlib import Path,PurePosixPath
_USED={}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root,env={**os.environ,'GIT_NO_LAZY_FETCH':'1'},stderr=subprocess.DEVNULL)
def load_plan(root):
 value=json.loads((Path(root)/'config/historical-baseline-recovery.json').read_text());payload=value['payload']
 if value.get('schemaVersion')!=1 or payload.get('schemaVersion')!=1 or sha(canonical(payload))!=value.get('sha256'):raise ValueError('Historical recovery registry checksum differs')
 entries=payload['entries']
 if len({r['module'] for r in entries})!=len(entries) or len({r['originalRef'] for r in entries})!=len(entries):raise ValueError('Historical recovery registry duplicates a baseline')
 for r in entries:
  if r['mode'] not in {'published-parent','frozen-generator-replay'} or any(len(r[k])!=40 or any(c not in '0123456789abcdef' for c in r[k]) for k in ['baselineRef','reviewCommit','tree']):raise ValueError('Invalid historical recovery provenance')
 return payload
@lru_cache(maxsize=None)
def _plan(root):return load_plan(root)
def descriptor(root,ref):return next((r for r in _plan(str(root))['entries'] if ref in {r['originalRef'],r['baselineRef']}),None)
@lru_cache(maxsize=None)
def _verify(root,ref):
 r=descriptor(root,ref)
 if not r:return None
 baseline=r['baselineRef'];parent=git(root,'rev-parse',r['reviewCommit']+'^').decode().strip()
 if parent!=baseline or git(root,'rev-parse',baseline+'^{tree}').decode().strip()!=r['tree']:raise ValueError('Historical recovery ancestry differs')
 if sha(git(root,'show',r['reviewCommit']+':'+r['reviewRecord']))!=r['reviewSha256']:raise ValueError('Historical review record differs')
 for path,record in r['files'].items():
  raw=git(root,'show',baseline+':'+path)
  if sha(raw)!=record['rawSha256'] or git(root,'rev-parse',baseline+':'+path).decode().strip()!=record['gitBlob']:raise ValueError('Original historical blob differs')
  if r['mode']=='published-parent':json.loads(raw)
 _USED[r['module']]={'originalRef':r['originalRef'],'baselineRef':baseline,'reviewCommit':r['reviewCommit'],'tree':r['tree'],'mode':r['mode'],'tests':r['tests'],'originalObjectsRewritten':False}
 return r

def extract_source(raw,target):
 with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
  for member in archive.getmembers():
   path=PurePosixPath(member.name)
   if path.is_absolute() or '..' in path.parts or not(member.isfile() or member.isdir()):raise ValueError('Historical source archive contains an unsafe entry')
  archive.extractall(target,filter='data')
@lru_cache(maxsize=None)
def _replay(root,ref):
 r=_verify(root,ref)
 if not r or r['mode']!='frozen-generator-replay':raise ValueError('Historical generator replay is not registered')
 with tempfile.TemporaryDirectory(prefix='atlas-frozen-generator-') as directory:
  target=Path(directory);extract_source(git(root,'archive',r['baselineRef'],'data','scripts'),target)
  for name,digest in r['generators'].items():
   if sha((target/name).read_bytes())!=digest:raise ValueError('Frozen historical generator differs')
  environment={**os.environ,'PYTHONHASHSEED':'0'};environment.pop('PYTHONPATH',None)
  for name in ['scripts/build_entity_model.py','scripts/build_organizations.py']:
   subprocess.run([sys.executable,name],cwd=target,env=environment,check=True,stdout=subprocess.DEVNULL,timeout=60)
  for path,digest in r['validGeneratedFiles'].items():
   if sha((target/path).read_bytes())!=digest:raise ValueError('Replay changes an intact historical generated file')
  result={}
  for path,record in r['files'].items():
   raw=(target/path).read_bytes()
   if sha(raw)!=record['replayedSha256']:raise ValueError('Replayed historical baseline differs from registered output')
   result[path]=json.loads(raw)
 _USED[r['module']]['intactFilesByteEqual']=True;_USED[r['module']]['replayedOutputHashes']={p:v['replayedSha256'] for p,v in r['files'].items()}
 return result

def baseline_ref(root,ref):
 r=_verify(str(root),ref);return r['baselineRef'] if r else ref

def baseline_json(root,ref,path):
 root=str(root);r=_verify(root,ref)
 if r and r['mode']=='frozen-generator-replay' and path in r['files']:return copy.deepcopy(_replay(root,ref)[path])
 return json.loads(git(root,'show',(r['baselineRef'] if r else ref)+':'+path))
def recovery_report():return [copy.deepcopy(_USED[key]) for key in sorted(_USED)]
