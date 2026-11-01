#!/usr/bin/env python3
"""Rounds 54-55: drain rounds 52-53 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine
from functools import partial
from basic_source_date_review import reviewed_add_fresh
from import_basic_r50_r51_20261101 import reviewed_candidate, original_add_fresh


def configure():
    engine.source.candidate = reviewed_candidate
    engine.add_fresh = partial(reviewed_add_fresh, original_add_fresh,
                              engine.previous.vndb_year)
    engine.BASE='1e79ba46daf2c21adcbb11ddfe98471c61a3e87a'
    engine.B24='vndb-kana-bulk-20261101-r54'
    engine.B25='nextmoe-galgame-bulk-20261101-r55'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r54.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r55.json'
    engine.REPORT=engine.ROOT/'data/basic-r54-r55-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r52.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r53.json'
    engine.EXPECTED_VNDB_START='v20623'


if __name__=='__main__':
    configure()
    engine.main()
