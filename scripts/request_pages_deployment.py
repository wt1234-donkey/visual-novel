"""Explicit handoff for token-dispatched builds; deployment remains a separate queue."""
import json
import os
from pathlib import Path
import re
import urllib.request

REPO = 'wt1234-donkey/visual-novel'


def request_deployment(env=os.environ):
    event = json.loads(Path(env['GITHUB_EVENT_PATH']).read_text())
    run_id = env.get('GITHUB_RUN_ID', '')
    if (env.get('GITHUB_REPOSITORY') != REPO or env.get('GITHUB_REF') != 'refs/heads/main'
            or env.get('GITHUB_EVENT_NAME') != 'repository_dispatch'
            or event.get('action') != 'catalogue-release-request'
            or not re.fullmatch(r'[1-9][0-9]*', run_id)):
        raise ValueError('Only this trusted main release build may request deployment')
    payload = {'event_type': 'catalogue-deploy-request', 'client_payload': {'run_id': int(run_id)}}
    request = urllib.request.Request('https://api.github.com/repos/'+REPO+'/dispatches',
        data=json.dumps(payload).encode(), method='POST', headers={
            'Authorization': 'Bearer '+env['GH_TOKEN'], 'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 204:
            raise ValueError('Deployment handoff was not accepted')
    print(json.dumps({'deploymentRequested': True, 'verifiedBuildRun': int(run_id)}))


if __name__ == '__main__':
    request_deployment()
