#!/usr/bin/env python3
"""Rounds 52-53: drain rounds 50-51 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine
from functools import partial
from basic_source_date_review import reviewed_add_fresh
from import_basic_r50_r51_20261101 import reviewed_candidate, original_add_fresh


def configure():
    engine.source.candidate = reviewed_candidate
    engine.add_fresh = partial(reviewed_add_fresh, original_add_fresh,
                              engine.previous.vndb_year)
    engine.BASE='5860808746392cd18975ee0ee92751ea160cab21'
    engine.B24='vndb-kana-bulk-20261101-r52'
    engine.B25='nextmoe-galgame-bulk-20261101-r53'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r52.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r53.json'
    engine.REPORT=engine.ROOT/'data/basic-r52-r53-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r50.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r51.json'
    engine.EXPECTED_VNDB_START='v19655'


if __name__=='__main__':
    configure()
    engine.main()
