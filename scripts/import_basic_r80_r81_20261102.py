#!/usr/bin/env python3
"""Rounds 80–81: drain 0+207 saved queues, then resume VNDB, NextMoe and IFDB."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='07df044e832690574df11a5b2fb9b305cffd9f00'
    mixed.B60='vndb-kana-bulk-20261102-r80'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r81'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r80.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r81.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r80-r81-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r78.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r79.json'
    mixed.EXPECTED_VNDB_START='v34594'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
