#!/usr/bin/env python3
"""Rounds 66–67: saved 31+0 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='14bd85c98a0fc79044d2d8a61286e7eacb580e46'
    mixed.B60='vndb-kana-bulk-20261102-r66'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r67'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r66.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r67.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r66-r67-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r64.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r65.json'
    mixed.EXPECTED_VNDB_START='v26318'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
