#!/usr/bin/env python3
"""Run historical tests with the committed Git history available locally.

The exact-delta tests use committed trees from earlier catalogue audits. A
shallow or blob-filtered checkout must be hydrated before unittest discovery;
unpublished transient trees are handled explicitly in audit_baselines.py.
"""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PROBES = (
    '0f2d278e17d631b85ed7e34e7dd378a361ff4695:data/games.json',
    '37a7d92010796ef272b69985bb7c514fdfdd0769:data/credits.json',
)


def git(*args, check=True, **kwargs):
    return subprocess.run(['git', *args], cwd=ROOT, check=check, **kwargs)


def available():
    env = {**os.environ, 'GIT_NO_LAZY_FETCH': '1'}
    return all(git('cat-file', '-e', ref, env=env, check=False,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
               for ref in PROBES)


def main():
    shallow = git('rev-parse', '--is-shallow-repository', capture_output=True,
                  text=True).stdout.strip() == 'true'
    if shallow:
        git('fetch', '--unshallow', 'origin', 'main')
    if not available():
        git('fetch', '--refetch', '--no-filter', 'origin', 'main')
    if not available():
        raise SystemExit('Historical test objects remain unavailable after fetching origin/main')
    return subprocess.run(
        [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'],
        cwd=ROOT, env={**os.environ, 'GIT_NO_LAZY_FETCH': '1'}).returncode


if __name__ == '__main__':
    raise SystemExit(main())
