#!/usr/bin/env python3
"""Current contracts need no historical download; exact-delta audits are explicit."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--historical', action='store_true', help='also run frozen exact-delta modules')
    parser.add_argument('--fetch-history', action='store_true', help='explicitly allow fetching missing historical objects')
    parser.add_argument('--report', default='test-results/python-capabilities.json')
    args = parser.parse_args(argv)
    if args.fetch_history and not args.historical:
        parser.error('--fetch-history requires --historical')
    if args.historical and not available():
        if not args.fetch_history:
            raise SystemExit('Historical objects unavailable; use a full checkout or --historical --fetch-history')
        shallow = git('rev-parse', '--is-shallow-repository', capture_output=True, text=True).stdout.strip() == 'true'
        git('fetch', '--unshallow' if shallow else '--refetch', '--no-filter', 'origin', 'main')
        if not available():
            raise SystemExit('Historical objects remain unavailable')
    os.environ['GIT_NO_LAZY_FETCH'] = '1'
    policy = json.loads((ROOT/'config/test-capabilities.json').read_text())
    historical = {row['module']: row for row in policy['historicalModules']}
    paths = sorted((ROOT/'tests').glob('test_*.py'))
    modules = [p.stem for p in paths if args.historical or p.stem not in historical]
    if not set(historical) <= {p.stem for p in paths}:
        raise SystemExit('Historical capability registry contains a missing module')
    sys.path.insert(0, str(ROOT/'tests'))
    historical_cases = {row['testId'] for row in policy.get('historicalTests', [])}
    def selected(suite):
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                yield from selected(test)
            elif args.historical or test.id() not in historical_cases:
                yield test
    suite = unittest.TestSuite(selected(unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in modules)))
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    skipped = []
    for test, reason in result.skipped:
        capability = next((row for row in policy['conditionalSkips']
            if test.id().startswith(row['module']+'.') and row['ref'] in reason), None)
        skipped.append({'test': test.id(), 'reason': reason, 'registered': capability is not None,
                        'alternative': capability['alternative'] if capability else [],
                        'limitation': capability.get('limitation') if capability else 'Unregistered skip is a failure'})
    report = {'schemaVersion': 1, 'mode': 'historical-inclusive' if args.historical else 'current',
        'testsRun': result.testsRun, 'failures': len(result.failures), 'errors': len(result.errors),
        'skipped': skipped, 'modulesRun': modules,
        'separateHistoricalModules': [] if args.historical else list(historical),
        'separateHistoricalCases': [] if args.historical else sorted(historical_cases),
        'separateHistoricalTests': 0 if args.historical else sum(row['tests'] for row in historical.values())+len(historical_cases),
        'capabilities': policy['capabilities']}
    if args.historical:
        from historical_baseline_recovery import recovery_report
        report['baselineRecoveries'] = recovery_report()
    target = ROOT/args.report;target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({key: report[key] for key in ['mode', 'testsRun', 'failures', 'errors', 'separateHistoricalTests']}, ensure_ascii=False))
    return 0 if result.wasSuccessful() and all(row['registered'] for row in skipped) else 1


if __name__ == '__main__':
    raise SystemExit(main())
