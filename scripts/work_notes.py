"""Source-linked annotations that do not create works, releases or credits."""
import re

from source_urls import source_url_valid


def validate_work_notes(data, work_ids, dossier_ids):
    assert data['updated'] and data['note']
    assert set(data['works']) <= set(work_ids), '补充说明引用了不存在的主库作品'
    for notes in data['works'].values():
        assert notes and len({n['title'] for n in notes}) == len(notes)
        for note in notes:
            assert set(note) == {'title', 'text', 'source', 'dossierId', 'anchor'}
            assert note['title'] and note['text'] and source_url_valid(note['source'])
            assert note['dossierId'] in dossier_ids
            assert re.fullmatch(r'[a-z0-9_-]+', note['dossierId'])
            assert re.fullmatch(r'[a-zA-Z0-9_-]+', note['anchor'])
