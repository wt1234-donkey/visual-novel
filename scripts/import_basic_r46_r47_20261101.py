#!/usr/bin/env python3
"""Rounds 46-47: drain rounds 44-45 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='fb2659fbdaeee7b0747e68b070a0e03cd2bc270a'
    engine.B24='vndb-kana-bulk-20261101-r46'
    engine.B25='nextmoe-galgame-bulk-20261101-r47'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r46.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r47.json'
    engine.REPORT=engine.ROOT/'data/basic-r46-r47-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r44.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r45.json'
    engine.EXPECTED_VNDB_START='v16615'


if __name__=='__main__':
    configure()
    engine.main()
