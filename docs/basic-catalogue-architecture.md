# 基础身份库架构：第一、二阶段

本次在 GitHub Contents API + Pages 内完成渐进式分层。作品 ID、来源文件和网页入口继续使用。第二阶段将人工修改文件迁移至 schema 2，保留全部当前值和三次快捷撤销，加入从明确检查点开始的完整变更日志。

## 模块职责

| 层 | 实现 | 职责 |
|---|---|---|
| 领域 | `src/domain/catalogue/identity.mjs` | 既有稳定 ID 的解析、来源记录到作品的显式映射；名称只生成待核候选 |
| 领域 | `src/domain/catalogue/model.mjs` | 编辑校验、版本关系、覆盖投影、原子变更、最近三次撤销 |
| 领域 | `src/domain/catalogue/order.mjs` | 浏览器、搜索线程与构建共用排序 |
| 领域 | `src/domain/taxonomy/style-tags.mjs` | 受控标签定义、维度和校验 |
| 应用 | `src/application/catalogue/snapshot.mjs` | 来源、注册表、基础修改层和正式档案的统一快照与首页视图 |
| 应用 | `src/application/catalogue/view.mjs` | 按作品 ID 去重、主作品列表、子版本、ID 查找表及关系诊断 |
| 领域 | `src/domain/catalogue/journal.mjs` | 检查点、变更事件、重放校验与历史分页 |
| 应用 | `src/application/catalogue/service.mjs` | 统一会话状态、连接同步、预览、保存、撤销与失败重试身份 |
| 应用 | `src/application/catalogue/commands.mjs` | 读取最新快照、重放无冲突命令、并发校验、提交与不确定响应核验 |
| 应用 | `src/application/catalogue/query.mjs` | 主线程和 Worker 共用的筛选入口与位置结果 |
| 应用 | `src/application/catalogue/filters.mjs`、`search.mjs` | 厂商、玩法、标签、组合条件和同发行条件语义 |
| 应用 | `src/application/catalogue/imports.mjs` | CSV / JSON 解析和导入边界校验 |
| 基础设施 | `src/infrastructure/github/` | 通用 Contents 文件适配器与基础库文件配置 |
| 基础设施 | `src/infrastructure/filesystem/catalogue-snapshot.mjs` | 构建时读取文件并调用纯快照函数 |
| 界面 | `basic-catalogue-editor.mjs`、`minimal-adv-rpg.mjs` | 表单、授权交互、选择、分页及状态显示 |
| 构建 | `scripts/build_basic_web_index.mjs` | 索引压缩、分片、清单和身份待核报告的序列化 |

根目录原模型、标签、查询和 API 模块保留为再导出入口。依赖旧路径的网页、脚本和测试继续访问相同实现；新业务逻辑应写入对应层，不复制回兼容入口。

领域模块只依赖领域模块，不访问 DOM、网络或文件系统。应用命令通过注入的 `repository.read()` / `write()` 持久化，可用内存适配器进行行为测试。正式档案目前复用 `work-edit-model.mjs` 的纯投影函数，这是保留的兼容边界，尚未迁移其独立编辑界面。

## 统一数据流

文件适配器读取原始资料后调用 `buildCatalogueSnapshot(inputs)`。快照包含：

- `sourceRows`：供公开压缩索引和实时编辑覆盖层使用的来源行；发布时不把人工更正永久写回来源。
- `entries` / `all` / `byId` / `childrenByMain`：同一修订下的主作品、全部有效身份、ID 查找表和版本关系。
- `identities.sourceToWork` / `sourcesByWork`：显式来源身份映射，不用同名同年自动认定同一作品。
- `formalById` / `formalIdByWorkId`：正式档案的已更正投影及显式链接；不把发行、开发和厂商角色相互推断。
- `home`：从同一作品视图筛选出的首页记录，并把关联版本名称纳入检索。
- `identityCandidates` / `issues`：同名同年待核候选与关系错误。

首页和高级索引共用这份快照中的正式档案投影。浏览器与 Worker 通过 `createCatalogueView()` 应用实时修改，借助 `queryCatalogueRows()` 使用同一查询语义。`slot` 只用于同一发布修订内的紧凑索引位置，业务命令始终使用作品 ID；不同发布修订不可混用分片。

公开 `manifest.json` 增加快照格式版本、数据修订号及候选数。修订目录内的 `identity-review.json` 保存待核候选和关系诊断。候选仅用于核查，不自动合并或新增作品。

## 保存规则

1. 界面收集命令及操作 ID，应用服务读取最新远程状态。
2. 不同作品或同作品不同字段的普通编辑可以在最新状态上重算；同字段冲突、删除状态变化或版本关系变化拒绝提交。
3. 标签批次仅在目标作品均未变化时自动重放，任一目标变化则整批停止。
4. 合并、解除、删除和撤销遇到远程变化时要求重新核对，不自动重放。
5. 写入使用最新文件 SHA。仅对明确 SHA 冲突自动重算并重试一次。
6. 无 HTTP 状态的传输错误通过读取远程内容核验；通过唯一操作 ID、原始意图和操作人核实是否已写入；即使已有后续修改，也不重复执行此前操作。无法核实时保留待重试命令和原操作 ID。
7. 保存与 Pages 发布分别表述。表单详情读取失败不会被外层成功提示覆盖。

严格快照构建和命令提交检查父作品存在、未删除且是主作品，并检查孤立修改身份。浏览器容错视图保留失效父关系的记录可见，发布构建则拒绝带错快照。

## 验证与后续边界

`tests/basic-catalogue-architecture.test.mjs` 覆盖身份映射、同名独立作品、快照与查询一致性、版本关系及领域依赖边界。`tests/basic-catalogue-commands.test.mjs` 使用内存仓储覆盖并发、SHA 竞争、响应中断、权限失败及批次原子性。原有完整数据、页面和 API 测试继续执行；Pages 和专项 CI 的路径触发范围已包含 `src/**`。

第二阶段已建立统一会话服务和 schema 2 日志；正式库领域模型、独立标签分配记录、物理日志分片及全站页面迁移仍是后续边界。

## 第二阶段：完整日志与应用服务

`createCatalogueService()` 统一持有快照、仓储、操作人、投影视图和待重试命令。连接读取失败时保留原会话；预览不修改快照或生成正式事件；保存失败后保留原操作 ID，成功后更新统一视图。只读快照被递归冻结，防止表单误改活动状态。界面仅收集输入、调用服务和绘制结果。

`basic-catalogue-edits.json` 的 schema 2 在当前状态旁增加独立的 `journal`：

- `baseline` 是迁移时完整的 schema 1 状态，当前检查点为 r30，保留26条更正及原有最近操作。其审阅散列由迁移前提交 `bc123909` 独立计算，回归测试固定验证。
- `events` 从检查点之后逐次追加：操作 ID、操作人、时间、原因、原始意图、前后修订、字段前后值、完整新增／移除身份、撤销目标。
- 快捷撤销仍只处理最近三次，但每次撤销会追加事件，完整日志不会随快捷列表截断而丢失。
- `replayJournal()` 按序检查前值、连续修订、身份唯一性和撤销目标，重建状态；`validateStore()` 对比重建状态与当前快照。不能只改 `records` 而遗漏事件。
- 迁移前更早的操作由 Git 历史追溯；本次不伪造缺失的逐次事件。`node scripts/migrate_basic_journal.mjs --write` 可幂等迁移，`--check` 只校验。

逻辑上的快照和日志暂存于同一个 JSON，沿用一次 Contents API 写入和 SHA 校验，确保状态与日志共同成功或失败。没有引入“先保存快照、再写另一份日志”的部分成功窗口。物理分片需要事务仓储适配器，留给后续；当前31 KB状态迁移后约62 KB。

已迁移的 schema 2 会被旧 schema 1 写入代码拒绝；新模型仍读取旧格式及测试夹具。构建和 CI 校验迁移状态。公开索引清单包含日志起始修订和事件数；编辑连接窗口可分页查看完整前后值。传给搜索线程的只是当前状态，不复制完整日志。

发布时 `version_browser_modules.py` 为 HTML 入口、嵌套导入和 Worker URL 统一添加提交号版本参数，避免新入口继续加载旧模型缓存。源文件不改写，登记数据字节不参与模块转换。

新增测试覆盖日志跨三次撤销窗口的保留、从检查点重放、操作 ID 重试、后续远程修改下的结果确认、连接失败、并发会话操作和完整模块图版本化。
