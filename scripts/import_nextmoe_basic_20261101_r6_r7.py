#!/usr/bin/env python3
"""Import NextMoe rounds 6 and 7 into the established basic identity registry.

Preserves original IDs, titles, aliases and year collision holds. Only main
title/year/source identities are appended; strict three-layer work data untouched.
"""
import argparse
import json
from pathlib import Path
import import_nextmoe_basic_20261101_r2 as importer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=85)
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--max-new", type=int, default=500)
    parser.add_argument("--delay", type=float, default=2.2)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    assert 1 <= args.pages <= 100
    assert 1 <= args.limit <= 100
    assert 1 <= args.max_new <= 1000
    for round_number in (6, 7):
        importer.BATCH = f"nextmoe-galgame-bulk-20261101-r{round_number}"
        importer.AUDIT = importer.ROOT / f"data/nextmoe-bulk-review-20261101-r{round_number}.json"
        importer.INDEX_PREFIX = f"nextmoe-20261101-r{round_number}-"
        registry = json.loads(importer.REGISTRY.read_text(encoding="utf-8"))
        existing_batches = [b for b in registry["batches"] if b["id"] == importer.BATCH]
        # This is an additive importer: when CI reruns after writing data, do not
        # alter a successful batch by rescanning a live and changing API.
        if existing_batches:
            if not importer.AUDIT.is_file():
                raise RuntimeError("batch marker present but audit absent; manual reconciliation required")
            audit = json.loads(importer.AUDIT.read_text(encoding="utf-8"))
            if audit["summary"]["newDistinctWorks"] != existing_batches[0]["summary"]["promoted-basic"]:
                raise RuntimeError("batch count/audit mismatch")
            print(f"SKIPPED_EXISTING_{round_number}={audit['summary']['newDistinctWorks']}", flush=True)
            continue
        print(f"IMPORT_ROUND={round_number}", flush=True)
        importer.run(args)
    final = json.loads(importer.REGISTRY.read_text(encoding="utf-8"))
    for round_number in (6, 7):
        batch = next(b for b in final["batches"] if b["id"].endswith(f"-r{round_number}"))
        print(f"ROUND_{round_number}_NEW={batch['summary']['promoted-basic']}", flush=True)
    print(f"FINAL_BASIC_IDENTITY_COUNT={len(final['works'])}", flush=True)

if __name__ == "__main__":
    main()
