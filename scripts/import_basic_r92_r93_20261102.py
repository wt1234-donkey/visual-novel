#!/usr/bin/env python3
"""Rounds 92–93: recheck 36 VNDB + 229 NextMoe candidates, then resume all three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE = 'b784bc9b3f30ae5849485c7b59c95a4a4aff2f09'
    mixed.B60 = 'vndb-kana-bulk-20261102-r92'
    mixed.B61 = 'nextmoe-ifdb-bulk-20261102-r93'
    mixed.A60 = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r92.json'
    mixed.A61 = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r93.json'
    mixed.REPORT = mixed.e.ROOT / 'data/basic-r92-r93-diversity-20261102.json'
    mixed.SEED_VNDB = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r90.json'
    mixed.SEED_NEXTMOE = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r91.json'

    vndb = mixed.e.load(mixed.SEED_VNDB)
    nextmoe = mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd'] == 'v42716'
    assert len(vndb['deferredEligible']) == 36
    assert len(nextmoe['deferredEligible']) == 229
    assert len(vndb['deferredEligible']) + len(nextmoe['deferredEligible']) == 265

    trace = nextmoe['summary']['paginationTrace']
    last = next(row for row in reversed(trace) if row['lane'] == 'era-keyset')
    # Use the exact valid cursor saved by round 91; the user-supplied variant has a malformed payload.
    assert last['nextCursor'] == 'cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOREE0TmpoOQ'
    assert last['releasedAfter'] == '2010-01-01'
    assert last['releasedBefore'] == '2026-11-02'

    review = nextmoe['ifdbArchiveReview']
    mixed.EXPECTED_VNDB_START = 'v42716'
    mixed.IFDB_START_POSITION = mixed.ifdb.resume_position(review)
    assert mixed.IFDB_START_POSITION == 4550
    assert mixed.NEXT_LIMIT == 300
    mixed.configure()


if __name__ == '__main__':
    configure()
    mixed.main()
