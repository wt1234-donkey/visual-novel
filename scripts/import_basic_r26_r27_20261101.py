#!/usr/bin/env python3
"""Rounds 26-27: drain rounds 24-25 queues, then use their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='75e450fa88ac3023f87c5eb5b7f778b022092c8e'
    engine.B24='vndb-kana-bulk-20261101-r26'
    engine.B25='nextmoe-galgame-bulk-20261101-r27'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r26.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r27.json'
    engine.REPORT=engine.ROOT/'data/basic-r26-r27-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r24.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r25.json'
    engine.EXPECTED_VNDB_START='v6382'


if __name__=='__main__':
    configure()
    engine.main()
