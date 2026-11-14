"""Validate fixed historical provenance and reproduce registered derived baselines."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from historical_baseline_recovery import load_plan,baseline_ref,baseline_json,recovery_report
for row in load_plan(ROOT)['entries']:
 ref=baseline_ref(ROOT,row['originalRef'])
 for path in row['files']:baseline_json(ROOT,ref,path)
report={'schemaVersion':1,'originalObjectsRewritten':False,'testPassClaim':False,'recoveries':recovery_report()};path=ROOT/'test-results/historical-baseline-provenance.json';path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'baselines':len(report['recoveries']),'testsAvailable':sum(r['tests'] for r in report['recoveries'])}))
