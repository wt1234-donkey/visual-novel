#!/usr/bin/env python3
"""Rounds 44-45: drain rounds 42-43 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='479b579b2fcd6d7f09789b3956aa365d65282385'
    engine.B24='vndb-kana-bulk-20261101-r44'
    engine.B25='nextmoe-galgame-bulk-20261101-r45'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r44.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r45.json'
    engine.REPORT=engine.ROOT/'data/basic-r44-r45-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r42.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r43.json'
    engine.EXPECTED_VNDB_START='v15566'


if __name__=='__main__':
    configure()
    engine.main()
