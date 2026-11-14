# 当前契约、精简历史夹具与条件覆盖（A13尾项）

当前功能门禁与精确历史差量分开。`config/test-capabilities.json` 登记历史模块、混合模块中的单独历史用例、条件跳过、替代覆盖和未验证能力；没有删除旧审计用例，也没有把移至独立运行的测试算作本次通过。

|能力|执行与条件|覆盖边界|
|---|---|---|
|当前Python／Node契约|`python3 scripts/verify_current_contracts.py` 强制复制当前来源到不含Git对象的独立目录，再运行两套用例|来源保全、身份与范围、日期、编辑、并发、回放、归档、生成器及发布边界必须通过；不下载历史。|
|精简历史契约|`tests/fixtures/history-contracts.json`；固定SHA256在能力登记中核对|80个旧专题锚点、旧检索页、Banpresto归档边界、Enix七部作品及发行、601项待核职责。每项保留原提交及原完整文件摘要。|
|精确历史差量|`python3 scripts/run_python_tests.py --historical`；另有只读、仅手动的historical-validation工作流|验证冻结旧批次的精确变化；需要相应历史对象。当前工作流不因此恢复旧采集、写入或发布触发器。|
|缺失／损坏的精确快照|仅登记的模块和匹配ref可有说明地跳过|输出每个测试名、原因、替代文件和限制；未登记的跳过使检查失败。当前存续断言不等价于原快照的逐字节证明。|
|万条日志容量|Node强制用例，输出读数与回放结果|合成数据，不向生产库添加测试记录。查询预算与离线完整审计分别计量。|
|真实Chromium关键流程|发布CI必须安装浏览器并执行，缺少依赖不能称作通过|包括保存、撤销、响应中断、后续修改、重载、跨发布恢复、手机视口和已索引历史。|
|Android真机|尚无实际设备测量|既有390×844、限速及CPU减速的性能和故障模拟作为替代，明确不等同真机结果。|

默认 `python3 scripts/run_python_tests.py` 只运行登记之外的当前用例，不自动获取Git历史。缺少历史对象时，附加审计必须由调用者显式指定 `--historical --fetch-history` 才允许下载。

精简夹具由 `python3 scripts/build_history_fixtures.py` 从明确的已提交对象重新提取，属于维护工具，当前门禁不执行它。夹具是相关断言的最小投影，不提供整个旧树，也没有补造未提交或损坏的历史。冻结完整历史的106个旧流程、脚本摘要和隔离重放登记继续原样保留。

`scripts/validate_catalogue.py` 将当前功能放入无历史目录验证。正式Pages打包仍保留Git祖先信息用于发布与保存状态追溯；这是发布溯源用途，不能误写成“整个发布流程完全不需要Git”。

CI保留 `python-capabilities.json`、`current-checkout-proof.json` 和 `audit-capacity.json`。报告区分执行、失败、条件跳过、另行运行的历史用例及替代覆盖；历史能力未执行、原始快照不可恢复或真机未测，均不计为已验证。

浏览器回归先构建实际发布目录，再设置 `ATLAS_SITE_DIRECTORY` 指向该目录，执行 `node --test tests/browser/*.test.mjs`。CI同时提供隔离的 `PLAYWRIGHT_MODULE`。公开页面初始化与编辑恢复都使用同一个测试入口；缺少实际产物时公开页面回归明确失败，不以跳过替代。

## 复评增长与启动门禁

`audit-growth-and-startup` 为必测能力：万条基线后的100次连续追加与批次追加；正式、身份、字段三类非空万条日志的当前值和20项历史；真实页面／编辑器的手机条件启动与撤销证据。产物为 `audit-incremental.json`、`audit-current.json`、`audit-startup-mobile.json`。浏览器每类一次预算回归不宣称真机、中位数或端到端发布耗时。
