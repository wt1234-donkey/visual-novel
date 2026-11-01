#!/usr/bin/env python3
"""Rounds 56-57: drain rounds 54-55 queues and resume their exact source cursors."""
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
    engine.BASE='67a90f648ed2e4fc5dd73cbdfcfa095dc500a955'
    engine.B24='vndb-kana-bulk-20261102-r56'
    engine.B25='nextmoe-galgame-bulk-20261102-r57'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261102-r56.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261102-r57.json'
    engine.REPORT=engine.ROOT/'data/basic-r56-r57-diversity-20261102.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r54.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r55.json'
    engine.EXPECTED_VNDB_START='v21679'


if __name__=='__main__':
    configure()
    engine.main()
