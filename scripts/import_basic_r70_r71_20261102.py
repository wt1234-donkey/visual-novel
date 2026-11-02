#!/usr/bin/env python3
"""Rounds 70–71: empty saved queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='5bf8b2bf37a4411aa8abbaa261273836873638a2'
    mixed.B60='vndb-kana-bulk-20261102-r70'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r71'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r70.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r71.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r70-r71-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r68.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r69.json'
    mixed.EXPECTED_VNDB_START='v28503'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
