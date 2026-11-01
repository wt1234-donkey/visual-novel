#!/usr/bin/env python3
"""Rounds 38-39: drain rounds 36-37 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine


def configure():
    engine.BASE='7b26b533b77d6ca85ccdc6cf551eacea29f2798a'
    engine.B24='vndb-kana-bulk-20261101-r38'
    engine.B25='nextmoe-galgame-bulk-20261101-r39'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r38.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r39.json'
    engine.REPORT=engine.ROOT/'data/basic-r38-r39-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r36.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r37.json'
    engine.EXPECTED_VNDB_START='v12493'


if __name__=='__main__':
    configure()
    engine.main()
