"""Python generators share the exact browser/domain projection via a Node adapter."""
import json
import subprocess
from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=4)
def load_effective(root):
    root = Path(root).resolve()
    script = Path(__file__).with_name('read_effective_catalogue.mjs')
    return json.loads(subprocess.check_output(['node', str(script), str(root)], text=True))


def effective_title(work):
    return work.get('displayTitle') or work.get('chineseTitle') or work['title']
