#!/usr/bin/env python3
"""Rounds 40-41: drain rounds 38-39 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='843227fb28b311bb53b3d16f05e970d75650b312'
    engine.B24='vndb-kana-bulk-20261101-r40'
    engine.B25='nextmoe-galgame-bulk-20261101-r41'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r40.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r41.json'
    engine.REPORT=engine.ROOT/'data/basic-r40-r41-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r38.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r39.json'
    engine.EXPECTED_VNDB_START='v13465'


if __name__=='__main__':
    configure()
    engine.main()
