"""Validate a successful main build before promotion or rollback; never checkout its code."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tarfile
import urllib.request
from release_policy import verify_public
from wire_format import decode_wire

REPO = 'wt1234-donkey/visual-novel'


def validate_run(run, repository_id):
    if (run.get('repository', {}).get('full_name') != REPO or
            run.get('repository', {}).get('id') != repository_id or
            run.get('head_repository', {}).get('full_name') != REPO or
            run.get('path') != '.github/workflows/pages.yml' or
            run.get('event') not in ('push', 'workflow_dispatch', 'repository_dispatch') or
            run.get('head_branch') != 'main' or run.get('conclusion') != 'success' or
            not re.fullmatch(r'[a-f0-9]{40}', run.get('head_sha', ''))):
        raise ValueError('Only a successful trusted main Pages build may be published')
    return run['head_sha']


def select_release(run, repository_id, latest, rollback=False):
    revision = validate_run(run, repository_id)
    return {'revision': revision, 'publish': rollback or revision == latest, 'rollback': rollback}


def unpack_verified(archive, output, revision):
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError('Release output must be empty')
    with tarfile.open(archive) as source:
        members = source.getmembers()
        for member in members:
            path = Path(member.name)
            if path.is_absolute() or '..' in path.parts or member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise ValueError('Unsafe Pages archive member')
        output.mkdir(parents=True, exist_ok=True)
        source.extractall(output, members=members, filter='data')
    deployment = json.loads((output/'deployment.json').read_text())
    release = json.loads((output/'data/catalogue-release.json').read_text())
    if deployment.get('revision') != revision or release.get('revision') != revision:
        raise ValueError('Artifact provenance does not match the verified build')
    for ref in [release['inputs'], *release.get('resources', {}).values(), *([release['basic']] if release.get('basic') else [])]:
        path = ref['path']
        if not path.startswith('catalogue-web/'+revision+'/') or '..' in Path(path).parts:
            raise ValueError('Invalid published resource path')
        raw = decode_wire((output/'data'/path).read_bytes())
        digest = hashlib.sha1(('blob '+str(len(raw))+'\0').encode()+raw).hexdigest()
        if digest != ref['sha']:
            raise ValueError('Published resource checksum mismatch')
    if (output/'.git').exists() or (output/'.github').exists():
        raise ValueError('Repository metadata must not be published')
    if deployment.get('releasePolicySha256'):
        verify_public(output)
    return deployment



def rollback_metadata(deployment, run, latest, at):
    return {**deployment, 'rollback': {'at': at, 'verifiedRunId': run['id'],
        'repositoryHead': latest, 'url': run['html_url']}}


def api(path):
    request = urllib.request.Request('https://api.github.com/repos/'+REPO+path,
        headers={'Authorization': 'Bearer '+os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', type=int, required=True)
    parser.add_argument('--rollback', action='store_true')
    parser.add_argument('--archive')
    parser.add_argument('--output', default='_site')
    args = parser.parse_args()
    run = api('/actions/runs/'+str(args.run_id))
    latest = api('/git/ref/heads/main')['object']['sha']
    result = select_release(run, int(os.environ['GITHUB_REPOSITORY_ID']), latest, args.rollback)
    if args.archive:
        deployment = unpack_verified(args.archive, args.output, result['revision'])
        if args.rollback:
            from datetime import datetime, timezone
            deployment = rollback_metadata(deployment, run, latest, datetime.now(timezone.utc).isoformat())
            (Path(args.output)/'deployment.json').write_text(json.dumps(deployment, ensure_ascii=False, indent=2)+'\n')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as stream:
            stream.write('publish='+str(result['publish']).lower()+'\nrevision='+result['revision']+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
