#!/usr/bin/env python3
"""Rounds 34-35: drain rounds 32-33 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='ff6943de52d905bed06d2445f81bce30a94f0d15'
    engine.B24='vndb-kana-bulk-20261101-r34'
    engine.B25='nextmoe-galgame-bulk-20261101-r35'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r34.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r35.json'
    engine.REPORT=engine.ROOT/'data/basic-r34-r35-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r32.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r33.json'
    engine.EXPECTED_VNDB_START='v10355'


if __name__=='__main__':
    configure()
    engine.main()
