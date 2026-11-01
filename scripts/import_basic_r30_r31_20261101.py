#!/usr/bin/env python3
"""Rounds 30-31: drain rounds 28-29 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='fc5acc33873712a60493ca1af3fbae55c507a630'
    engine.B24='vndb-kana-bulk-20261101-r30'
    engine.B25='nextmoe-galgame-bulk-20261101-r31'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r30.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r31.json'
    engine.REPORT=engine.ROOT/'data/basic-r30-r31-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r28.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r29.json'
    engine.EXPECTED_VNDB_START='v8147'


if __name__=='__main__':
    configure()
    engine.main()
