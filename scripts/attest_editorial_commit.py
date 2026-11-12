"""Attest the trusted reviewed-data workflow before it updates protected main."""
import os
from pathlib import Path
import re
from promote_catalogue_command import api,git

def allowed_path(path):
    value=Path(path)
    return '..' not in value.parts and ((path.startswith('data/') and value.suffix in ('.json','.csv','.md')) or (len(value.parts)==1 and value.suffix=='.html'))

def main():
    expected='wt1234-donkey/visual-novel/.github/workflows/editorial-publish.yml@refs/heads/main'
    if os.environ.get('GITHUB_WORKFLOW_REF')!=expected or os.environ.get('GITHUB_REF')!='refs/heads/main':
        raise ValueError('Attestation is restricted to the trusted main editorial workflow')
    sha=git('rev-parse','HEAD');parent=git('rev-parse','HEAD^')
    if api('/git/ref/heads/main')['object']['sha']!=parent:raise ValueError('main changed; the same batch must be verified again')
    paths=git('diff','--name-only',parent,sha).splitlines()
    if not paths or any(not allowed_path(path) for path in paths):raise ValueError('Reviewed data publish cannot include code or arbitrary paths')
    run_id=os.environ.get('GITHUB_RUN_ID','')
    if not re.fullmatch(r'[0-9]+',run_id):raise ValueError('Missing GitHub run identity')
    branch='editorial-verified/'+run_id+'-'+os.environ.get('GITHUB_RUN_ATTEMPT','1')
    git('push','origin','HEAD:refs/heads/'+branch)
    api('/statuses/'+sha,'POST',{'state':'success','context':'build','description':'Trusted reviewed-data workflow passed all data and regression checks'})
    api('/git/refs/heads/main','PATCH',{'sha':sha,'force':False})
    print('Verified editorial commit saved: '+sha)
if __name__=='__main__':main()
