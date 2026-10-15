"""Export one row per work, including company-only related games."""
import csv
import io
import json
from pathlib import Path
from interaction_model import iter_interaction_works, validate_interactions

ROOT = Path(__file__).resolve().parents[1]


def interaction_csv(data, coverage):
    output = io.StringIO(newline='')
    fields = ['范围', '作品ID', '中文检索名', '原名', '首发年份', '互动方式', '分类依据', '操作说明', '资料来源']
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for scope, w in iter_interaction_works(data, coverage):
        writer.writerow(dict(zip(fields, [scope, w['id'], w.get('chineseTitle') or w['title'],
            w['originalTitle'], w['firstYear'], '、'.join(w['interactionModes']), w['interactionBasis'],
            w['interactionNote'], ' | '.join(w['interactionSources'])])))
    return output.getvalue()


if __name__ == '__main__':
    data = json.loads((ROOT/'data/games.json').read_text())
    coverage = json.loads((ROOT/'data/company-coverage.json').read_text())
    validate_interactions(data, coverage, json.loads((ROOT/'data/taxonomy.json').read_text()))
    (ROOT/'data/interaction-modes.csv').write_text(interaction_csv(data, coverage), encoding='utf-8-sig')
    print('已导出主目录及专题附录的全部互动方式标签')
