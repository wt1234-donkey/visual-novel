#!/usr/bin/env python3
"""Rounds 36-37: drain rounds 34-35 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='eb0f4eb2739e6170cc1c29002aff8a71473abc51'
    engine.B24='vndb-kana-bulk-20261101-r36'
    engine.B25='nextmoe-galgame-bulk-20261101-r37'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r36.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r37.json'
    engine.REPORT=engine.ROOT/'data/basic-r36-r37-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r34.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r35.json'
    engine.EXPECTED_VNDB_START='v11318'


if __name__=='__main__':
    configure()
    engine.main()
