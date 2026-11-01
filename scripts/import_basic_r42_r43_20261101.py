#!/usr/bin/env python3
"""Rounds 42-43: drain rounds 40-41 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='d85671cb22a02312968f7a9bf1dea0a1eb9bbcaf'
    engine.B24='vndb-kana-bulk-20261101-r42'
    engine.B25='nextmoe-galgame-bulk-20261101-r43'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r42.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r43.json'
    engine.REPORT=engine.ROOT/'data/basic-r42-r43-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r40.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r41.json'
    engine.EXPECTED_VNDB_START='v14410'


if __name__=='__main__':
    configure()
    engine.main()
