"""Commit only command data; status attestation precedes a non-force main update."""
import base64
import json
import os
import re
import sys
import urllib.error
from pathlib import Path
import subprocess
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
REPO='wt1234-donkey/visual-novel'
def allowed_path(path):
    return path in ('data/basic-catalogue-edits.json','data/work-edit-history.json') or (
        path.startswith(('data/basic-catalogue-journal/events/','data/command-receipts/')) and
        path.endswith('.json') and '..' not in Path(path).parts)
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT,text=True).strip()
def api(path,method='GET',value=None):
    raw=json.dumps(value).encode() if value is not None else None
    request=urllib.request.Request('https://api.github.com/repos/'+REPO+path,data=raw,method=method,
        headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'],'Accept':'application/vnd.github+json','Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=30) as response:
        return json.load(response) if response.status!=204 else None
def rejected_update(path,sha):
    try:api(path,'PATCH',{'sha':sha,'force':False})
    except urllib.error.HTTPError as error:
        message=error.read().decode()
        if error.code in (403,422) and 'build' in message and 'status check' in message.lower():return True
        raise
    raise ValueError('Unverified update unexpectedly succeeded; isolated rule is not enforcing the check')
def main(rehearsal=False):
    head=git('rev-parse','HEAD')
    if api('/git/ref/heads/main')['object']['sha']!=head:raise ValueError('main changed; retry the same operation from current main')
    target='heads/main'
    if rehearsal:
        run_id=os.environ.get('GITHUB_RUN_ID','')
        if not re.fullmatch(r'[0-9]+',run_id):raise ValueError('Rehearsal requires a GitHub run ID')
        target='heads/validation/trusted-save-gate-'+run_id
        api('/git/refs','POST',{'ref':'refs/'+target,'sha':head})
    changed=git('ls-files','--modified','--deleted','--others','--exclude-standard').splitlines()
    paths=sorted(set(path for path in changed if allowed_path(path)))
    if not paths or not any(path.startswith('data/command-receipts/') for path in paths):raise ValueError('No validated command receipt to promote')
    tree=[]
    for path in paths:
        file=ROOT/path
        if not file.exists():tree.append({'path':path,'mode':'100644','type':'blob','sha':None});continue
        blob=api('/git/blobs','POST',{'content':base64.b64encode(file.read_bytes()).decode(),'encoding':'base64'})
        tree.append({'path':path,'mode':'100644','type':'blob','sha':blob['sha']})
    parent=api('/git/commits/'+head)
    built=api('/git/trees','POST',{'base_tree':parent['tree']['sha'],'tree':tree})
    commit=api('/git/commits','POST',{'message':'Apply verified catalogue command','tree':built['sha'],'parents':[head]})
    blocked={}
    if rehearsal:
        blocked['missing']=rejected_update('/git/refs/'+target,commit['sha'])
        if api('/git/ref/'+target)['object']['sha']!=head:raise ValueError('Rejected update changed the isolated branch')
        api('/statuses/'+commit['sha'],'POST',{'state':'failure','context':'build','description':'Isolated negative check; main is untouched'})
        blocked['failed']=rejected_update('/git/refs/'+target,commit['sha'])
    api('/statuses/'+commit['sha'],'POST',{'state':'success','context':'build','description':'Trusted data-only command validated before main update'})
    api('/git/refs/'+target,'PATCH',{'sha':commit['sha'],'force':False})
    if rehearsal and api('/git/ref/heads/main')['object']['sha']!=head:raise ValueError('main changed during the isolated rehearsal')
    print(json.dumps({'commit':commit['sha'],'paths':len(paths),'target':target,'blocked':blocked,'mainUnchanged':rehearsal}))
if __name__=='__main__':main(rehearsal='--rehearsal' in sys.argv)
