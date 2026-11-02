#!/usr/bin/env python3
"""Rounds 64–65: saved 43+208 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='ca624747435cf7bee89de3efbd525ad4e772eb7b'
    mixed.B60='vndb-kana-bulk-20261102-r64'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r65'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r64.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r65.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r64-r65-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r62.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r63.json'
    mixed.EXPECTED_VNDB_START='v25384'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
