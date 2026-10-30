#!/usr/bin/env python3
"""Preserve existing entity evidence when append-only releases regenerate indexes."""
import json
import sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
old=json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
path=root/"data/entities.json"
new=json.loads(path.read_text(encoding="utf-8"))
by_id={e["id"]:e for e in old["entities"]}
count=0
for entity in new["entities"]:
    prior=by_id.get(entity["id"])
    if prior is not None:
        entity["sources"]=prior.get("sources",[])
        count+=1
path.write_text(json.dumps(new,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(f"Preserved evidence source lists for {count} historical entity identities")
