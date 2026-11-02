#!/usr/bin/env python3
"""Rounds 84–85: recheck 16 VNDB + 263 NextMoe saved candidates, then resume all three sources."""
import import_basic_r60_r61_20261102 as mixed


def configure():
    mixed.BASE='24dea848b3c7533fdce1374c1f27e775ce92b05b'
    mixed.B60='vndb-kana-bulk-20261102-r84'
    mixed.B61='nextmoe-ifdb-bulk-20261102-r85'
    mixed.A60=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r84.json'
    mixed.A61=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r85.json'
    mixed.REPORT=mixed.e.ROOT/'data/basic-r84-r85-diversity-20261102.json'
    mixed.SEED_VNDB=mixed.e.ROOT/'data/vndb-kana-bulk-review-20261102-r82.json'
    mixed.SEED_NEXTMOE=mixed.e.ROOT/'data/nextmoe-ifdb-bulk-review-20261102-r83.json'

    vndb=mixed.e.load(mixed.SEED_VNDB)
    nextmoe=mixed.e.load(mixed.SEED_NEXTMOE)
    assert vndb['summary']['cursorEnd']=='v37520'
    assert len(vndb['deferredEligible'])==16
    assert len(nextmoe['deferredEligible'])==263
    trace=nextmoe['summary']['paginationTrace']
    last=next(row for row in reversed(trace) if row['lane']=='era-keyset')
    assert last['nextCursor']=='cur_ZXlKeklqb2lhV1FpTENKcFpDSTZNell4TUROOQ'
    assert last['releasedAfter']=='2010-01-01'
    assert last['releasedBefore']=='2026-11-02'
    review=nextmoe['ifdbArchiveReview']
    assert review['nextPosition']==3672
    mixed.EXPECTED_VNDB_START='v37520'
    mixed.IFDB_START_POSITION=mixed.ifdb.resume_position(review)
    assert mixed.IFDB_START_POSITION==3672
    mixed.configure()


if __name__=='__main__':
    configure()
    mixed.main()
