# 基础作品库 → 主库网站批量补录（2026-11-01）

## 两种「进入主库」必须分清

- **网站统一检索（可以立即批量实现）**：`data/main-adv-rpg-works-20261031.json` 与 `data/games.json` 在首页「作品发现」同时查询。基础身份在页面直接展示、按名称与别名检索、分页及核对来源，无需伪造原作发行记录。与完整档案同名同年的作品不会双重展示。基础库的详情仍以基础档案标识，不冒充已编目完整档案。
- **升级为严格完整主库记录（必须有证据）**：`data/games.json` 的 `works/contentVersions/platformReleases` 三层数据要求实际首发版次、平台、发行署名与证据，不能仅用名称+年份自动写入。版本差异与创作者也不能凭来源联想补齐。

网站入口：`index.html`「作品发现」输入作品名或别名，查看「基础作品检索」；`minimal-adv-rpg.html` 可浏览全部基础身份。

## 下一批：仍沿用原有去重口径

从仓库根目录运行：

```bash
python3 scripts/import_nextmoe_basic_20261101_r3.py --pages 50 --limit 100 --max-new 500 --dry-run
# 审核通过后（在独立工作分支）再执行：
python3 scripts/import_nextmoe_basic_20261101_r3.py --pages 50 --limit 100 --max-new 500
```

第三批使用原第二批导入函数，沿用 NSFW/galgame + VNDB ID、NextMoe source ID、作品题名/别名 NFKC 比较和年份冲突暂缓规则。过滤试玩、DLC、部分合集和版本歧义。批次标识 `nextmoe-galgame-bulk-20261101-r3`，审计数据 `data/nextmoe-bulk-review-20261101-r3.json`。不采集游戏下载资源、账户数据或版权受保护内容。

建议先在测试分支运行 GitHub Action `nextmoe-basic-main-bridge-20261101.yml`，该流程读取真实 NextMoe 目录 → 去重 → 生成基础身份 → 生成100条待核验主库升级清单 → 全套数据/前端检查 → 提交到功能分支。只有确认 Action 通过及 PR 差异无误后才合并部署。

## 每100部准备一次严格主库升级

```bash
python3 scripts/stage_basic_registry_for_main.py --offset 0 --limit 100 --write
python3 scripts/stage_basic_registry_for_main.py --offset 100 --limit 100 --write
```

输出 `data/basic-to-full-promotion-review-20261101.json`，后一次执行覆盖前一次批次文件（需要归档时先改名保存）。报告严格分出：

1. `records`：基础作品身份中没有与 `games.json` / 补充库 / 专题直接碰撞的待核条目。
2. `linkedExisting`：标题/别名且首发年份一致，已有作品身份，不再建新作品。
3. `heldForReview`：同名跨身份、年份冲突、重复外部身份或来源异常，不能自动合并。

`readyForStrictGamesJson: false` 是刻意设计：仍需确认新旧版本是否独立作品、首发平台及发行方、可核验的原作内容和互动方式。已经存在完整主库 ID 的作品应以原 ID 补充缺项，而不是再次建作品。

## 完整主库升级时如何执行

在核实后，将选中的独立作品添加到 `data/games.json` 的 `works`，同时建立**一个** `basis: original` 的 `contentVersions`，以及有来源的 `releaseRole: contentDebut` 平台发行记录。普通移植和同内容再次发行不另建内容版本；新增剧情/路线/角色/游戏内素材须有独立证据才能新增 `basis: added` 记录。不要用「待核实平台」或「待核实发行方」假装已有首次发行。

通过现有资料管理系统或带审核的批量脚本写入，并在每100条后执行：

```bash
python3 scripts/sync_versions_csv.py
python3 scripts/export_content_csv.py
python3 scripts/export_interaction_csv.py
python3 scripts/build_entity_model.py
python3 scripts/build_entity_pages.py
python3 scripts/build_company_pages.py
python3 scripts/validate_data.py
python3 scripts/validate_entity_model.py
python3 scripts/run_python_tests.py
node --test tests/*.test.mjs
python3 scripts/build_company_pages.py --check
```

任何未通过的批次都不能合并到 `main`。升级进度按三个数分别统计：基础身份独立数、完整档案升级成功数、因冲突待核数；**不把基础身份数直接加到正式 `games.json` 作品数上**。

## 审计与源数据

- 基础身份：`data/main-adv-rpg-works-20261031.json`
- 第二批审核：`data/nextmoe-bulk-review-20261101-r2.json`
- 第三批审核：`data/nextmoe-bulk-review-20261101-r3.json`
- 可升级清单：`data/basic-to-full-promotion-review-20261101.json`
- 严格模型：`data/content-model.md` 和 `AGENTS.md`
