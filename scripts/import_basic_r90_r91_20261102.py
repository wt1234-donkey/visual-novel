#!/usr/bin/env python3
"""Rounds 90–91: recheck the 229 saved candidates, then resume all three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE = '43cf23ec8ccd1e1cccd06666fdf9db3a7eeaddd6'
    mixed.B60 = 'vndb-kana-bulk-20261102-r90'
    mixed.B61 = 'nextmoe-ifdb-bulk-20261102-r91'
    mixed.A60 = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r90.json'
    mixed.A61 = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r91.json'
    mixed.REPORT = mixed.e.ROOT / 'data/basic-r90-r91-diversity-20261102.json'
    mixed.SEED_VNDB = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r88.json'
    mixed.SEED_NEXTMOE = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r89.json'

    vndb = mixed.e.load(mixed.SEED_VNDB)
    nextmoe = mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd'] == 'v41596'
    assert len(vndb['deferredEligible']) == 2
    assert len(nextmoe['deferredEligible']) == 227
    assert len(vndb['deferredEligible']) + len(nextmoe['deferredEligible']) == 229
    assert nextmoe['summary']['after'] == 43785

    trace = nextmoe['summary']['paginationTrace']
    last = next(row for row in reversed(trace) if row['lane'] == 'era-keyset')
    assert last['nextCursor'] == 'cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNemsyTnpCOQ'
    assert last['releasedAfter'] == '2010-01-01'
    assert last['releasedBefore'] == '2026-11-02'

    review = nextmoe['ifdbArchiveReview']
    mixed.EXPECTED_VNDB_START = 'v41596'
    mixed.IFDB_START_POSITION = mixed.ifdb.resume_position(review)
    assert mixed.IFDB_START_POSITION == 4324
    mixed.configure()


if __name__ == '__main__':
    configure()
    mixed.main()
