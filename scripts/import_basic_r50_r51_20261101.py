#!/usr/bin/env python3
"""Rounds 50-51: drain rounds 48-49 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine

from import_basic_r48_r49_20261101 import reviewed_candidate


def configure():
    engine.source.candidate = reviewed_candidate
    engine.BASE='1cb36f80beab55b47e76d6a8093df665ed0efe86'
    engine.B24='vndb-kana-bulk-20261101-r50'
    engine.B25='nextmoe-galgame-bulk-20261101-r51'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r50.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r51.json'
    engine.REPORT=engine.ROOT/'data/basic-r50-r51-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r48.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r49.json'
    engine.EXPECTED_VNDB_START='v18709'


if __name__=='__main__':
    configure()
    engine.main()
