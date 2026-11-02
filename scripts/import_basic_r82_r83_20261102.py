#!/usr/bin/env python3
"""Rounds 82–83: drain 56 VNDB + 242 NextMoe saved candidates, then resume all three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='6accb8d6203122a1dbea679e7243139ff5a672c8'
    mixed.B60='vndb-kana-bulk-20261102-r82'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r83'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r82.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r83.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r82-r83-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r80.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r81.json'
    mixed.EXPECTED_VNDB_START='v36278'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
