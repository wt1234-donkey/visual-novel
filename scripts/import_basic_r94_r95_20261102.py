#!/usr/bin/env python3
"""Rounds 94–95: recheck 38 VNDB + 254 NextMoe candidates, then resume three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE = '0a92b1efed84c6415b944cc48cd47f6095c4ac42'
    mixed.B60 = 'vndb-kana-bulk-20261102-r94'
    mixed.B61 = 'nextmoe-ifdb-bulk-20261102-r95'
    mixed.A60 = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r94.json'
    mixed.A61 = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r95.json'
    mixed.REPORT = mixed.e.ROOT / 'data/basic-r94-r95-diversity-20261102.json'
    mixed.SEED_VNDB = mixed.e.ROOT / 'data/vndb-kana-bulk-review-20261102-r92.json'
    mixed.SEED_NEXTMOE = mixed.e.ROOT / 'data/nextmoe-ifdb-bulk-review-20261102-r93.json'
    vndb = mixed.e.load(mixed.SEED_VNDB)
    nextmoe = mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd'] == 'v44030'
    assert len(vndb['deferredEligible']) == 38
    assert len(nextmoe['deferredEligible']) == 254
    assert len(vndb['deferredEligible']) + len(nextmoe['deferredEligible']) == 292
    last = next(row for row in reversed(nextmoe['summary']['paginationTrace']) if row['lane'] == 'era-keyset')
    assert last['nextCursor'] == 'cur_ZXlKeklqb2lhV1FpTENKcFpDSTZOREl3T0RSOQ'
    assert (last['releasedAfter'], last['releasedBefore']) == ('2010-01-01', '2026-11-02')
    mixed.EXPECTED_VNDB_START = 'v44030'
    mixed.IFDB_START_POSITION = mixed.ifdb.resume_position(nextmoe['ifdbArchiveReview'])
    assert mixed.IFDB_START_POSITION == 4762
    assert mixed.NEXT_LIMIT == 300
    mixed.configure()


if __name__ == '__main__':
    configure()
    mixed.main()
