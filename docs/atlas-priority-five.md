# 全站架构复审：五项优先问题实施说明

依据 `narrative_atlas_architecture_review_20261111.md` 的 A01—A05 实施。原始作品、内容版本、平台发行、主体职责与历史来源继续分别保存；本轮不执行作品去重或版本重新认定。

| 问题 | 实现与边界 |
|---|---|
| A01 当前有效数据分叉 | `src/domain/catalogue/effective.mjs` 为首页、正式检索、基础库、管理台显示、专题和 CSV 提供共同投影。原始资料不覆盖。基础更正中未变动的字段跟随当前来源；共同显示名称按明确更正与字段时间选择，撤销恢复对应视图。基础归组、删除不自动修改正式内容／发行身份。 |
| A02 单体源登记 | 原文件名改为清单，作品放入 `data/basic-registry/` 的内容寻址分片，每片最多1000条。清单保留原元数据、顺序、数量与正式身份链接，记录每片 SHA-256、Git SHA 与逻辑摘要。现有108173条记录与迁移前对象完整相等。 |
| A03 来源资料陈旧 | 发布清单绑定来源文件、全部源分片及编辑领域规则的 Git SHA。基础与正式保存都在最新 Git 头校验来源；文件 SHA 租约仍检查并发。来源变化要求刷新核对，最终引用更新不强推。正式修改文件自身由原有 SHA 租约处理，连续保存不会因自己的一次更正误报来源变化。 |
| A04 日期规则漂移 | `data/date-contract.json` 是共享规则；JS与Python有对照检查。登记年份允许1900—2200或未知，未来年份可保持待核／计划状态；正式原作准入须是已发行年份，不能据未来年生成已发行事实。基础界面提供年份状态。 |
| A05 全站验证范围不足 | `pages.yml` 对所有指向 main 的 PR 执行全量验证与产物构建，不再仅按基础库路径触发；检查源分片、日期契约、当前投影与历史回归。发布先再生当前专题和CSV，直接保存不需要人工审核。 |

## 来源与当前值

`sourceTitle`／`sourceFirstYear`保留来源值，`displayTitle`是共同显示值。正式原名、历史发行署名和内容ID不因显示名改变而重写。网页当前更正与来源分别保存在原有文件，生成内容可以从它们重建。

普通字段更正记录可能保存整组表单值；与身份原始快照相同的字段不被解释成新的人工断言。新普通更正保存字段级操作ID和时间，用于共用名称的优先级。旧更正不补造时间。

正式更正同样保存字段时间，独立于最近三次快捷回撤记录；连续修改其他字段不会丢失改名时间，回撤会恢复原字段时间。旧记录仅从仍可核对的历史事件取得时间，不推造已经移出的时间。

`catalogue-release.json`及其按提交号命名的输入快照供网页读取，带输入摘要与来源版本凭据。编辑器保留原始输入用于回撤；更新当前覆盖层后重新投影，不在已经覆盖的对象上叠加回撤。

专题和CSV属于派生视图。`generate_effective_views.py`统一再生；Pages在验证前和产物内再生，保证直接更正不会因仓库中的旧HTML／CSV而漏发布。仓库中的派生文件可能晚于最新直接更正，网站下载以实际发布产物为准；源JSON及其分片保留原始资料，不能用它们的字段值代替当前有效视图。

## 源登记读写

Python使用 `registry_store.read_json()`／`write_json()`，Node使用 `readJsonFileSync()`，浏览器使用 `readRegistry()`。历史小型完整JSON夹具仍可读写，生产CI要求实际源库必须为分片格式。

新分片先写入，清单最后替换；过期片在清单替换后清理。全部变更作为一次 Git 提交发布。仅追加记录时，已满且未变动的片保持字节不变。所有更新应一起暂存 `data/`，不能只提交清单。

导出外部工具需要的完整原始JSON：

```sh
python3 scripts/export_basic_registry.py --output /tmp/basic-registry.json
```

该导出不能覆盖源清单。历史精确批次脚本的旧总数和来源窗口仍只适用于各自基线，不作为当前补录入口。

## 校验与发布边界

```sh
python3 scripts/registry_store.py --check
python3 scripts/generate_effective_views.py
python3 scripts/validate_data.py
python3 scripts/validate_entity_model.py
python3 scripts/run_python_tests.py
node scripts/migrate_basic_storage.mjs --check
node --test tests/*.test.mjs
python3 scripts/build_company_pages.py --check
python3 scripts/build_entity_model.py --check
python3 scripts/build_entity_pages.py --check
python3 scripts/build_pages_artifact.py --output _site
```

代码修改使用PR与完整检查；个人数据编辑保留现有 Contents 写入凭证及直接保存方式，在应用与事务层执行领域校验、来源版本校验和并发校验。本轮不启用会阻断现有直接保存的主分支强制PR规则，也不为网页增加Actions权限或人工审核。全站PR检查的覆盖已补齐，仓库所有者主动绕过PR的权限不由网页应用撤销。

验证重点包括：跨入口名称一致、原始事实与内容ID不变、较新更正与撤销、来源修改竞争、正式连续保存、早期年份、未来年份与正式准入的区别、源分片损坏与追加、浏览器快照摘要、全站PR触发范围。
