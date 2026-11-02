#!/usr/bin/env python3
"""Rounds 72–73: saved 20+0 queues, exact source cursors, 500 identities each."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='589fccf3bacf4d52709af1fbd70c6d3758627fd1'
    mixed.B60='vndb-kana-bulk-20261102-r72'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r73'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r72.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r73.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r72-r73-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r70.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r71.json'
    mixed.EXPECTED_VNDB_START='v29551'
    review=mixed.e.load(mixed.SEED_NEXTMOE)['ifdbArchiveReview']
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
