#!/usr/bin/env python3
"""Rounds 28-29: drain rounds 26-27 queues, then resume their saved cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='71c05d563d9d592066ec6962a4376ff7911c0329'
    engine.B24='vndb-kana-bulk-20261101-r28'
    engine.B25='nextmoe-galgame-bulk-20261101-r29'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r28.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r29.json'
    engine.REPORT=engine.ROOT/'data/basic-r28-r29-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r26.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r27.json'
    engine.EXPECTED_VNDB_START='v7199'


if __name__=='__main__':
    configure()
    engine.main()
