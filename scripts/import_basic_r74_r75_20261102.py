#!/usr/bin/env python3
"""Rounds 74–75: saved 11+0 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='7614d0b6954149cc9c4e799466204b67bb8b8fc0'
    mixed.B60='vndb-kana-bulk-20261102-r74'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r75'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r74.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r75.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r74-r75-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r72.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r73.json'
    mixed.EXPECTED_VNDB_START='v30526'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
