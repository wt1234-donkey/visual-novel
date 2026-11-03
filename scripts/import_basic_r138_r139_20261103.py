#!/usr/bin/env python3
"""Resume IFDB 12711 and the prior PC-98 review queue, up to 500 per batch."""
import import_basic_r134_r135_20261103 as engine


def configure():
    engine.BASE = 'fc0fff6dd5b5c236f7eb648d78a0a550c4de8cc4'
    engine.START = 12711
    engine.ROUNDS = (138, 139)
    engine.SEED_AUDIT = engine.ROOT / 'data/ifdb-pc98-bulk-review-20261103-r137.json'
    engine.PC_RESUME_AUDIT = engine.ROOT / 'data/pc98-catalogue-audit-r136-r137-20261103.json'
    engine.REVIEW = engine.ROOT / 'data/pc98-admission-review-r138-r139-20261103.json'
    engine.HISTORICAL_REVIEWS = (engine.ROOT / 'data/pc98-admission-review-20261103.json',
        engine.ROOT / 'data/pc98-admission-review-r136-r137-20261103.json')
    engine.ALLOW_PARTIAL_BATCHES = True
    engine.PC_AUDIT = engine.ROOT / 'data/pc98-catalogue-audit-r138-r139-20261103.json'
    engine.REPORT = engine.ROOT / 'data/basic-r138-r139-audit-summary-20261103.md'
    assert engine.IFDB_CUTOFF.isoformat() == '2026-11-02'
    assert engine.ifdb.resume_position(engine.load(engine.SEED_AUDIT)['ifdbArchiveReview']) == engine.START


if __name__ == '__main__':
    configure()
    engine.main()
