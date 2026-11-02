#!/usr/bin/env python3
"""Resume IFDB 11618 and the prior PC-98 unresolved queue, two 500-work batches."""
import import_basic_r134_r135_20261103 as engine


def configure():
    engine.BASE = '1aff53081625d407b6e44f5b960cc55c8855ffd4'
    engine.START = 11618
    engine.ROUNDS = (136, 137)
    engine.SEED_AUDIT = engine.ROOT / 'data/ifdb-pc98-bulk-review-20261103-r135.json'
    engine.PC_RESUME_AUDIT = engine.ROOT / 'data/pc98-catalogue-audit-20261103.json'
    engine.REVIEW = engine.ROOT / 'data/pc98-admission-review-r136-r137-20261103.json'
    engine.PC_AUDIT = engine.ROOT / 'data/pc98-catalogue-audit-r136-r137-20261103.json'
    engine.REPORT = engine.ROOT / 'data/basic-r136-r137-audit-summary-20261103.md'
    assert engine.IFDB_CUTOFF.isoformat() == '2026-11-02'
    assert engine.ifdb.resume_position(engine.load(engine.SEED_AUDIT)['ifdbArchiveReview']) == engine.START


if __name__ == '__main__':
    configure()
    engine.main()
