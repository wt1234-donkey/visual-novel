"""Controlled, sourced, multi-value interaction labels at work level."""
from source_urls import source_url_valid

INTERACTION_FIELDS = {'interactionModes', 'interactionNote', 'interactionBasis', 'interactionSources'}


def iter_interaction_works(data, coverage):
    yield from (('主目录', w) for w in data['works'])
    for company in coverage['companies']:
        yield from ((company['id'], w) for w in company.get('relatedGames', []))


def validate_interactions(data, coverage, taxonomy):
    allowed = taxonomy['interactionModes']
    assert all(name in allowed for name in ['文字输入', '选项分支', '菜单指令', '点击调查'])
    assert all(isinstance(value, str) and value for value in allowed.values())
    for scope, w in iter_interaction_works(data, coverage):
        modes = w['interactionModes']
        assert isinstance(modes, list) and modes, f'{scope}/{w["id"]} 缺少互动方式'
        assert all(isinstance(mode, str) and mode in allowed for mode in modes), f'{w["id"]} 有未定义标签'
        assert len(modes) == len(set(modes)), f'{w["id"]} 标签重复'
        assert '待核实' not in modes or modes == ['待核实'], '未知不能同时宣称具体操作'
        assert isinstance(w['interactionNote'], str) and w['interactionNote'].strip()
        assert w['interactionBasis'] in {'既有资料归纳', '来源核对'}
        sources = w['interactionSources']
        assert isinstance(sources, list) and sources and len(sources) == len(set(sources))
        assert all(source_url_valid(url) for url in sources), f'{w["id"]} 缺少有效玩法资料'
