#!/usr/bin/env python3
"""Rounds 48-49: drain rounds 46-47 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='804264aa60121d0410b1340cab64b3caf9b30ead'
    engine.B24='vndb-kana-bulk-20261101-r48'
    engine.B25='nextmoe-galgame-bulk-20261101-r49'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r48.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r49.json'
    engine.REPORT=engine.ROOT/'data/basic-r48-r49-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r46.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r47.json'
    engine.EXPECTED_VNDB_START='v17546'


if __name__=='__main__':
    configure()
    engine.main()
