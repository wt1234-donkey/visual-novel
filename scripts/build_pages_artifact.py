#!/usr/bin/env python3
"""Package tracked static content and attach verifiable catalogue provenance."""
from registry_store import read_json as read_registry_json, write_json as write_registry_json, write_text as write_registry_text
import argparse
import hashlib
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from version_browser_modules import version_modules

ROOT=Path(__file__).resolve().parents[1]
REGISTRY='data/main-adv-rpg-works-20261031.json'


def build(root,output,revision=None):
    root,output=Path(root).resolve(),Path(output).resolve()
    if output==root or (output.exists() and any(output.iterdir())):
        raise ValueError('Use a separate empty output directory; existing files are never removed')
    registry_bytes=(root/REGISTRY).read_bytes()
    registry=read_registry_json(root/REGISTRY)
    works=registry['works']
    if len({w['id'] for w in works})!=len(works) or registry['summary']['accepted']!=len(works):
        raise ValueError('Basic registry has duplicate identities or incorrect accounting')
    paths=subprocess.check_output(['git','ls-files','-z'],cwd=root).decode().split('\0')
    paths=[p for p in paths if p and Path(p).parts[0]!='.github' and p not in {'.gitignore','AGENTS.md'}]
    for name in paths:
        src=root/name
        if src.is_symlink() or not src.is_file():
            raise ValueError('Artifact requires regular tracked files: '+name)
    output.mkdir(parents=True,exist_ok=True)
    for name in paths:
        target=output/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(root/name,target)
    (output/'.nojekyll').touch()
    revision=revision or subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    # Published HTML and CSV always include current corrections. Never require a
    # browser data edit to commit regenerated derived views back to source Git.
    if 'scripts/generate_effective_views.py' in paths:
        subprocess.run(['python3',str(output/'scripts/generate_effective_views.py')],check=True)
    if 'scripts/build_basic_web_index.mjs' in paths:
        subprocess.run(['node',str(root/'scripts/build_basic_web_index.mjs'),str(root),str(output),revision],check=True)
    if 'scripts/build_effective_catalogue.mjs' in paths:
        subprocess.run(['node', str(root/'scripts/build_effective_catalogue.mjs'), str(root), str(output), revision], check=True)
    if (output/'release-runtime.mjs').is_file():
        for page in output.glob('*.html'):
            text=page.read_text(encoding='utf-8')
            script='<script type="module" src="./release-runtime.mjs"></script>'
            if '</body>' in text:
                page.write_text(text.replace('</body>',script+'</body>'),encoding='utf-8')
    ancestors=[]
    if len(revision)==40:
        ancestors=subprocess.check_output(['git','rev-list',revision],cwd=root,text=True).splitlines()
    versioned_modules=version_modules(output,revision)
    manifest={
        'schema':1,
        'ancestors':ancestors,
        'revision':revision,
        'registry':REGISTRY,
        'registrySha256':hashlib.sha256(registry_bytes).hexdigest(),
        'basicWorkCount':len(works),
        'batchCounts':dict(sorted(Counter(w.get('batch','historical') for w in works).items())),
        'trackedFileCount':len(paths),
        'versionedBrowserFiles':versioned_modules,
    }
    write_registry_text(output/'deployment.json', json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    if (output/REGISTRY).read_bytes()!=registry_bytes or not (output/'index.html').is_file():
        raise ValueError('Published entry point or registry differs from the checkout')
    if (output/'.git').exists() or (output/'.github').exists():
        raise ValueError('Repository authentication or workflow files must not enter the artifact')
    return manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='_site')
    args=parser.parse_args()
    print(json.dumps(build(ROOT,args.output),ensure_ascii=False,indent=2))
