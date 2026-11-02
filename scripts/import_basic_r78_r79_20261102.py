#!/usr/bin/env python3
"""Rounds 78–79: saved 57+201 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='01d862e2ce7cad9291ee465326934dbe976b5c02'
    mixed.B60='vndb-kana-bulk-20261102-r78'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r79'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r78.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r79.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r78-r79-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r76.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r77.json'
    mixed.EXPECTED_VNDB_START='v33562'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
