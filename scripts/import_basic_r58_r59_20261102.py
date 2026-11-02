#!/usr/bin/env python3
"""Rounds 58-59: drain rounds 56-57 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine
from functools import partial
from basic_source_date_review import reviewed_add_fresh
from import_basic_r50_r51_20261101 import reviewed_candidate, original_add_fresh


def configure():
    engine.INTAKE_DATE='2026-11-02'
    engine.previous.CUTOFF=engine.previous.dt.date.fromisoformat(engine.INTAKE_DATE)
    engine.WINDOWS[-1]=('2010-01-01',engine.INTAKE_DATE)
    engine.source.candidate = reviewed_candidate
    engine.add_fresh = partial(reviewed_add_fresh, original_add_fresh,
                              engine.previous.vndb_year)
    engine.BASE='19ea503b2ea43eab6ba1a6ba5484639599006f01'
    engine.B24='vndb-kana-bulk-20261102-r58'
    engine.B25='nextmoe-galgame-bulk-20261102-r59'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261102-r58.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261102-r59.json'
    engine.REPORT=engine.ROOT/'data/basic-r58-r59-diversity-20261102.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261102-r56.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261102-r57.json'
    engine.EXPECTED_VNDB_START='v22758'


if __name__=='__main__':
    configure()
    engine.main()
