# 发布产物与历史任务治理（A10、A11）

本批不修改作品事实、历史身份与版本关系，不改变可信个人保存及 main 的 build 保护要求。

## 发布目录

`config/release-policy.json` 是发布白名单：明确列出根目录浏览器入口、5个公开导入/标签模板、允许的数据下载格式，以及浏览器模块依赖目录。新页面或新下载格式必须登记；引用缺失时构建失败。

构建示例：

```bash
python3 scripts/validate_catalogue.py
python3 scripts/build_pages_artifact.py --workspace /tmp/catalogue-build --output /tmp/catalogue-site
```

两个目录都必须为空且相互独立。省略 workspace 时使用自动清理的临时目录。构建目录保留生成器、模板和所需源码，先生成有效作品、专题和CSV，再生成固定版本的索引。发布目录只接收白名单文件及浏览器模块依赖闭包，不复制 scripts、tests、editorial-service、archive、开发配置或文件系统适配器。

全部来源JSON、109个原始源片、历史审计资料、CSV与5个用户模板继续公开下载。新目录和运行产物清单仍与同一发布版本绑定；deployment.json记录策略摘要、公开文件数量和不含部署清单自身的正文总字节数。构建逐项核对HTML、CSS、模块和发布清单中的本地资源，部署前再次检查新格式产物。既有已验证旧产物的显式回退入口保持兼容。

## 派生数据的无损存储与具名事实配置

新增sources.html作为来源与历史资料总目录，并从发现页导航直达；原103个页面和882个原始data下载文件保留。原始data下载文件不压缩改写、不改变路径。仅对固定版本目录中的重复生成JSON采用gzip-base64封装，保留已存在的gzip快速读取文件；浏览器解码后仍按原始文本验证Git blob摘要，部署校验也先解码再核对。基础manifest和发布清单保持普通JSON。没有原生DecompressionStream时使用固定版本、带完整MIT声明的4KiB解码器，来源和摘要登记于config/runtime-vendors.json，构建不依赖在线CDN。

本地同等公开资料覆盖下，发布目录正文由702,717,555字节降为395,011,629字节，约减少43.8%；该数是解包目录正文，不冒称压缩上传包也减少同样比例。882个原始下载文件逐字节不变，原始资料下载体积另外列入验收报告。

原round28脚本中的具名专题显示纠正迁入config/dossier-corrections.json，具有schemaVersion、原证据文件及SHA256。通用执行器校验目标平台、年份、原署名和身份后应用配置；原模块只作兼容适配。原结论、来源与生成页面保持一致；新更正需要明确更新有来源的配置。

## 冻结的历史任务

106个历史工作流原样移到 `archive/workflows/`，不再位于 GitHub Actions 自动发现目录。原路径、内容SHA256、固定代码与数据快照、脚本摘要及只读核验命令登记于 `config/historical-tasks.json`。共享验证器另有维护，冻结任务不因新批次而复制或重写。

`config/workflow-policy.json` 登记11个活动工作流；`config/script-policy.json` 对186个脚本登记为53个活动依赖、121个冻结历史脚本和12个手动工具。历史脚本变更或未登记的新脚本会被拒绝。校验会拒绝未登记的 yml/yaml 工作流、重新放回活动目录的历史流程、改动的归档或未登记归档。历史文件保留其原始说明和原始写入步骤供查阅，但不会以原写入权限自动运行。

按固定快照隔离恢复与核验：

```bash
python3 scripts/workflow_governance.py --check
python3 scripts/workflow_governance.py --task ifdb-append-20261104 --output /tmp/ifdb-snapshot --execute-checks --report /tmp/ifdb-replay.json
```

输出目录必须是仓库之外的新目录。恢复使用 detached worktree，既有 main 和调用目录不变；移除运行环境中的GitHub写入凭证，只运行登记的Python核验命令，完成后检查快照没有变化。省略 execute-checks 时仅恢复和校验固定源码。该入口复现冻结时的资料和核验结果，不自动重访已停止的采集平台，也不执行归档里的提交或推送步骤。结构化报告与核验日志分开保存。

GitHub手动工作流 `Isolated frozen historical audit` 使用相同入口和只读权限，不设 push、PR或定时触发。自动检查已覆盖106项归档；本批实际运行了IFDB任务的独立复现，不把这一例说成106项都逐一执行过。

## 新增批次使用同一流程

新增一个不可变的规范化来源快照 `data/intake/<name>.json` 和计划 `config/intake-plans/<batch>.json`，不复制历史Python脚本和YAML。来源格式为 schemaVersion 1 与 records 数组，每条记录至少具有 id、indexId、title、firstYear、gameplay、group、source；aliases为字符串数组，identityStatus为经确认的 independent，否则隔离。

计划字段：

|字段|含义|
|---|---|
|schemaVersion|1|
|batchId|唯一批次ID，小写字母、数字及连字符|
|date|明确的ISO日期|
|batchSize|本批上限，默认500，最大500|
|sourceSnapshot|data/intake 下的来源JSON相对路径|
|sourceSha256|来源文件原始字节摘要|
|expectedRegistryLogicalSha256|准备计划时的逻辑源库摘要，源库变化后重新准备|

记录可携带显式外部稳定身份 `sourceIdentity`。已知相同外部身份和年份的候选计为重复；同名、别名重合、年份冲突或版本关系不明进入隔离清单。不能把共用的目录URL当作单部作品身份，也不据名称自动合并作品。内部ID或indexId碰撞直接拒绝，既有记录不被覆盖。

先预览：

```bash
python3 scripts/catalogue_intake.py --plan config/intake-plans/my-batch.json --report /tmp/intake-preview.json
```

预览只读；确认需要准备候选时加 apply。重复执行同一计划不会重复追加，批次ID与内容不一致会失败。来源摘要或源库基线变化同样拒绝。接受记录、隔离/重复明细、批次审计和源分片通过同一候选Git提交保存。

GitHub工作流 `Parameterized catalogue intake` 默认只预览。选择 prepare_candidate 后，从预览固定的提交产生候选，使用和发布相同的 `scripts/validate_catalogue.py` 检查，然后只推送 `catalog/intake-<run>-<attempt>` 新分支并给出比较链接。它不直接写 main；候选进入既有PR/build发布链路。个人网页修改继续走原有可信执行端，无需新增人工审核。

## 本批本地验收

- 原始源库108,173条，逻辑SHA256仍为2b419f6b412eda7898f4705d2aae137f21f8bdb516ef4421e28fdbe3932c29a2。
- 103个HTML页面（含93个专题）、882个原有data下载文件及5个用户模板保留；882个来源/派生数据文件与构建输入逐字节一致。
- 相比旧打包规则，438个跟踪文件不再进入运行产物，其中包含179个脚本、230个测试、6个审核服务文件、10个服务器/构建模块及开发说明配置。原始排除量约2.28MiB，源资料占产物主要体积，不能把治理改动称作大幅降低源数据体积。
- 保留按需目录、完整检索、源码下载与既有已验证发布恢复能力。最终CI、PR和线上版本记录另见本批验收报告。
