"""Find files that existed in both sides of a frozen historical comparison."""
from fnmatch import fnmatch
from functools import lru_cache
import subprocess


@lru_cache(maxsize=None)
def _files(root, ref):
    return set(subprocess.check_output(
        ['git', 'ls-tree', '-r', '--name-only', ref, 'data/'], cwd=root,
        text=True).splitlines())


def shared_paths(root, before, after, patterns):
    return sorted(path for path in _files(root, before) & _files(root, after)
                  if any(fnmatch(path, f'data/{pattern}') for pattern in patterns))
