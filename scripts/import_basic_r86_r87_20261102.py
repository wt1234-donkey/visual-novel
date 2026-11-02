#!/usr/bin/env python3
"""Rounds 86–87: recheck 44 saved VNDB + 242 saved NextMoe candidates, then resume all three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='505c425a26e302c508c0e4ed1a57de8014a71f16'
    mixed.B60='vndb-kana-bulk-20261102-r86'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r87'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r86.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r87.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r86-r87-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r84.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r85.json'

    vndb=mixed.e.load(mixed.SEED_VNDB)
    nextmoe=mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd']=='v38952'
    assert len(vndb['deferredEligible'])==44
    assert len(nextmoe['deferredEligible'])==242
    trace=nextmoe['summary']['paginationTrace']
    last=next(row for row in reversed(trace) if row['lane']=='era-keyset')
    assert last['nextCursor']=='cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNemN6T0ROOQ'
    assert last['releasedAfter']=='2010-01-01'
    assert last['releasedBefore']=='2026-11-02'
    review=nextmoe['ifdbArchiveReview']
    assert review['nextPosition']==3896
    mixed.EXPECTED_VNDB_START='v38952'
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    assert mixed.IFDB_START_POSITION==3896
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
