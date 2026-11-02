#!/usr/bin/env python3
"""Rounds 62–63: saved 29+126 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='fcad342d4611736d0b7d34ddd44eeb2ba21f95c9'
    mixed.B60='vndb-kana-bulk-20261102-r62'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r63'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r62.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r63.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r62-r63-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r60.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r61.json'
    mixed.EXPECTED_VNDB_START='v24452'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
