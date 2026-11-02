#!/usr/bin/env python3
"""Rounds 88–89: recheck 46 saved VNDB + 295 saved NextMoe candidates, then resume all three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE = '1715c90e1641cfaaa51e5103a50c8dd8ad53072a'
    mixed.B60 = 'vndb-kana-bulk-20261102-r88'
    mixed.B61 = 'nextmoe-ifdb-bulk-20261102-r89'
    mixed.A60 = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r88.json'
    mixed.A61 = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r89.json'
    mixed.REPORT = mixed.e.ROOT / 'data/basic-r88-r89-diversity-20261102.json'
    mixed.SEED_VNDB = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r86.json'
    mixed.SEED_NEXTMOE = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r87.json'

    vndb = mixed.e.load(mixed.SEED_VNDB)
    nextmoe = mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd'] == 'v40387'
    assert len(vndb['deferredEligible']) == 46
    assert len(nextmoe['deferredEligible']) == 295
    assert len(vndb['deferredEligible']) + len(nextmoe['deferredEligible']) == 341

    trace = nextmoe['summary']['paginationTrace']
    last = next(row for row in reversed(trace) if row['lane'] == 'era-keyset')
    assert last['nextCursor'] == 'cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNemczT0RkOQ'
    assert last['releasedAfter'] == '2010-01-01'
    assert last['releasedBefore'] == '2026-11-02'

    review = nextmoe['ifdbArchiveReview']
    mixed.EXPECTED_VNDB_START = 'v40387'
    mixed.IFDB_START_POSITION = mixed.ifdb.resume_position(review)
    assert mixed.IFDB_START_POSITION > 3896
    mixed.configure()


if __name__ == '__main__':
    configure()
    mixed.main()
