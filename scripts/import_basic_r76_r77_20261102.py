#!/usr/bin/env python3
"""Rounds 76–77: saved 4+242 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='7bcf8b9d8de929ba765d1440b02aca0d7c478922'
    mixed.B60='vndb-kana-bulk-20261102-r76'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r77'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r76.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r77.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r76-r77-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r74.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r75.json'
    mixed.EXPECTED_VNDB_START='v31688'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
