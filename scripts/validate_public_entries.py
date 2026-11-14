"""Require an explicit startup contract for every shipped HTML entry."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(root=ROOT):
 root=Path(root); policy=json.loads((root/'config/release-policy.json').read_text()); registry=json.loads((root/'config/public-entrypoints.json').read_text())
 assert registry['schemaVersion']==1
 entries=registry['entries']; names=[e['path'] for e in entries]
 assert len(names)==len(set(names)) and set(names)=={p for p in policy['publicFiles'] if p.endswith('.html')},'public HTML entry inventory drift'
 for entry in entries:
  text=(root/entry['path']).read_text(); modules=[m.split('?')[0] for m in re.findall(r'<script[^>]+src="([^"]+)"',text)]
  assert modules==entry['modules'],entry['path']+' bootstrap modules changed'
  assert entry['ready']['selector'] and isinstance(entry['ready']['text'],str)
  for path in [*modules,*entry['resources']]:
   assert not '..' in Path(path).parts and (root/path).is_file(),path
 return len(entries)
if __name__=='__main__': print(f'Public entry startup contracts: {validate()}')
