"""Compatibility adapter for the frozen, sourced round-28 dossier display rules."""
import json
from pathlib import Path
from coverage_corrections import apply_configured

ROOT=Path(__file__).resolve().parents[1]

def review():
    return json.loads((ROOT/'data/organization-round28-closure-20261028.json').read_text())

def corrected_coverage(coverage):
    return apply_configured(coverage,ROOT)
