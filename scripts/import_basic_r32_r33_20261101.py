#!/usr/bin/env python3
"""Rounds 32-33: drain rounds 30-31 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='e36330bc16e882f59a7de551496314b91577d690'
    engine.B24='vndb-kana-bulk-20261101-r32'
    engine.B25='nextmoe-galgame-bulk-20261101-r33'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r32.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r33.json'
    engine.REPORT=engine.ROOT/'data/basic-r32-r33-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r30.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r31.json'
    engine.EXPECTED_VNDB_START='v9413'


if __name__=='__main__':
    configure()
    engine.main()
