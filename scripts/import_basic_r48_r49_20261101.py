#!/usr/bin/env python3
"""Rounds 48-49: drain rounds 46-47 queues and resume their exact source cursors."""
import import_basic_r24_r25_20261101 as engine

original_candidate = engine.source.candidate


def reviewed_candidate(item, source_kind, source_id, names, index, refs,
                       counts, reused, held, batch):
    """Quarantine a reviewed cross-source date conflict without merging identities."""
    if source_kind == 'nextmoe' and str(source_id) == '43993':
        counts['source-date-conflict-held'] += 1
        held.append({'sourceId': str(source_id), 'vndbId': item['id'],
                     'title': names[0] if names else '',
                     'sourceReleased': item.get('released'),
                     'nextmoeSourceReleased': '2006-03-23',
                     'reason': 'NextMoe 43993 reports 2006-03-23 but its VNDB reference v46627 reports 2023-07-31; association requires review.'})
        return None
    return original_candidate(item, source_kind, source_id, names, index, refs,
                              counts, reused, held, batch)


def configure():
    engine.source.candidate = reviewed_candidate
    engine.BASE='804264aa60121d0410b1340cab64b3caf9b30ead'
    engine.B24='vndb-kana-bulk-20261101-r48'
    engine.B25='nextmoe-galgame-bulk-20261101-r49'
    engine.A24=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r48.json'
    engine.A25=engine.ROOT/'data/nextmoe-bulk-review-20261101-r49.json'
    engine.REPORT=engine.ROOT/'data/basic-r48-r49-diversity-20261101.json'
    engine.SEED_VNDB=engine.ROOT/'data/vndb-kana-bulk-review-20261101-r46.json'
    engine.SEED_NEXTMOE=engine.ROOT/'data/nextmoe-bulk-review-20261101-r47.json'
    engine.EXPECTED_VNDB_START='v17546'


if __name__=='__main__':
    configure()
    engine.main()
