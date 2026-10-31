# 项目厂商清单：作品名称与首发年份补录核查（2026-10-31）

按用户要求，本批**仅补作品原名与首发年**，不要求主角、剧情、交互细节、脚本、原画或音乐创作者编目。各记录仅建立可用于页面显示的最小身份、原始内容和首批发行关联，历史移植、重制、合集没有另建。

## 去重结果

候选78条；主库**新增18部**，复用原ID 60部；身份歧义0项，首发年异文0项。
当前主库新增后约1605部作品，另已有年份不更改。

| 新ID | 关联厂商/制作品牌 | 原作标题 | 首发年 | 来源 |
|---|---|---|---:|---|
| g1591 | ぱれっと | はちみつ荘 de ほっぺにチュウ | 2002 | [来源](https://www.clearrave.co.jp/brand/brand_palette.html) |
| g1592 | Spinnaker | Snooper Troops: Case No. 1 - The Granite Point Ghost | 1982 | [来源](https://www.atarimania.com/games/atari-400-800-xl-xe-games-snooper-troops-case-1-the-granite-point-ghost-4769/print?print=1) |
| g1593 | Spinnaker | Snooper Troops: Case No. 2 - The Disappearing Dolphin | 1982 | [来源](https://www.mobygames.com/company/9633/idealogic-sa/) |
| g1594 | Telarium | Amazon | 1984 | [来源](https://pixelatedarcade.com/companies/telarium-corp) |
| g1595 | Telarium | Dragonworld | 1984 | [来源](https://www.lemon64.com/games/list.php?list_company=telarium) |
| g1596 | Telarium | Fahrenheit 451 | 1984 | [来源](https://pixelatedarcade.com/companies/telarium-corp) |
| g1597 | Telarium | Rendezvous with Rama | 1984 | [来源](https://pixelatedarcade.com/companies/telarium-corp) |
| g1598 | Telarium | Nine Princes in Amber | 1985 | [来源](https://www.lemon64.com/games/list.php?list_company=telarium) |
| g1599 | Telarium | Perry Mason: The Case of the Mandarin Murder | 1985 | [来源](https://www.lemon64.com/games/list.php?list_company=telarium) |
| g1600 | Windham Classics | Below the Root | 1984 | [来源](https://www.mobygames.com/company/678/windham-classics-corp/) |
| g1601 | Windham Classics | Swiss Family Robinson | 1984 | [来源](https://www.mobygames.com/company/678/windham-classics-corp/) |
| g1602 | Windham Classics | Alice in Wonderland | 1985 | [来源](https://www.mobygames.com/company/678/windham-classics-corp/) |
| g1603 | Windham Classics | Treasure Island | 1985 | [来源](https://www.mobygames.com/company/678/windham-classics-corp/) |
| g1604 | Windham Classics | The Wizard of Oz | 1985 | [来源](https://www.mobygames.com/company/678/windham-classics-corp/) |
| g1605 | Double Fine Productions | Stacking | 2011 | [来源](https://www.doublefine.com/games/stacking) |
| g1606 | Double Fine Productions | The Cave | 2013 | [来源](https://www.doublefine.com/games) |
| g1607 | Double Fine Productions | Psychonauts in the Rhombus of Ruin | 2017 | [来源](https://www.doublefine.com/games) |
| g1608 | Double Fine Productions | Keeper | 2025 | [来源](https://www.doublefine.com/games) |

## 已存在的候选作品与厂商范围

| 来源组 | 候选数 | 本次新增 | 复用旧作品 |
|---|---:|---:|---:|
| FAVORITE | 14 | 0 | 14 |
| AUGUST | 13 | 0 | 13 |
| ぱれっと | 17 | 1 | 16 |
| まどそふと | 9 | 0 | 9 |
| tone work’s | 5 | 0 | 5 |
| Spinnaker | 2 | 2 | 0 |
| Telarium | 6 | 6 | 0 |
| Windham Classics | 5 | 5 | 0 |
| Double Fine Productions | 5 | 4 | 1 |
| GigasDrop. | 1 | 0 | 1 |
| RIGHTWAY | 1 | 0 | 1 |

## 准确性及后续待核事项

1. 新作品标记 `catalogueDepth=titleYearOnly`；人物只填写明确的“人物尚未编目”占位，**不能据此理解为已经查明故事中的人物或完成四字段叙事编目**。`name_year_only`独立统计，不与之前已完成叙事考据的旧作品混算。
2. Telarium系 **Spinnaker旧品牌/出版子品牌**；Windham Classics为另一子品牌。仅将已有来源的首次发行年份和候选发行署名登记，实际软件开发者、移植商和公司沿革仍需独立核验。文本输入机制暂未按单机种分解。
3. Double Fine的叙事冒险如《Stacking》《The Cave》等可独立收入；纯重制《Grim Fandango Remastered》《Day of the Tentacle Remastered》等不作为新作品。`Keeper` 2025首次发售，不收录2026后发布的未发行游戏。
4. `STEINS;GATE 変移空間のオクテット`和`everlasting flowers`既有作品匹配成功，因此只保留原有身份，避免把GigasDrop或RIGHTWAY的开发/实体发行商角色错误写成另一部。
5. 发行平台、确切首发日、原作内容与增强版本的差异尚未系统核对；首次发行记录仅是现有仓库工作关联所需的候选值，不应被理解为所有地区和机种首发年的终审证明。
6. 原数据库作品的身份、版本、发行、创作者、剧情四字段均未覆盖。后续可从`data/gameplay-catalogues.json`其他尚无独立主库身份的叙事候选继续筛选，不直接把赛车/棋盘/麻将/RPG合集全量导入。

## 复现与完整性验证

`python3 scripts/backfill_project_title_years_20261031.py` → `sync_versions_csv.py`/`export_content_csv.py`/`export_interaction_csv.py` → 构建实体、厂商和页面 → `validate_data.py`, `validate_entity_model.py`, 全部Python/Node回归检查。
