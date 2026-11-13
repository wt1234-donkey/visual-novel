"""Seal a staged domain batch through the same receipt/archive protocol."""
import json
from pathlib import Path
import subprocess

def seal_write(root, descriptor):
    script = Path(__file__).with_name('seal_catalogue_write.mjs')
    subprocess.run(['node', str(script), str(Path(root).resolve())],
                   input=json.dumps(descriptor, ensure_ascii=False), text=True, check=True)
