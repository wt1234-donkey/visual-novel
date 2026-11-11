# 基础身份库架构：第一至三阶段

在 GitHub + Pages 内完成渐进式分层。作品 ID、来源文件和网页入口继续使用。第二阶段建立从 r30 检查点开始的完整日志；第三阶段将其迁移为 schema 3 物理分片，通过一次 Git 引用更新原子提交快照和日志。全部当前值和三次快捷撤销保留。

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
| 基础设施 | `src/infrastructure/github/` | 通用 Contents 传输与基础库 Git 事务适配器 |
| 基础设施 | `src/infrastructure/storage/` | 浏览器及脚本共用分片规划、状态摘要和完整日志还原 |
| 基础设施 | `src/infrastructure/filesystem/` | 完整审计、分片持久化和构建输入读取 |
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
5. 写入检查最新文件 SHA，以最新主分支提交为父提交，同时写入快照与所需日志文件。仅对明确并发冲突自动重算并重试一次。
6. 无 HTTP 状态的传输错误通过读取远程内容核验；通过唯一操作 ID、原始意图和操作人核实是否已写入；即使已有后续修改，也不重复执行此前操作。无法核实时保留待重试命令和原操作 ID。
7. 保存与 Pages 发布分别表述。表单详情读取失败不会被外层成功提示覆盖。

严格快照构建和命令提交检查父作品存在、未删除且是主作品，并检查孤立修改身份。浏览器容错视图保留失效父关系的记录可见，发布构建则拒绝带错快照。

## 验证与后续边界

`tests/basic-catalogue-architecture.test.mjs` 覆盖身份映射、同名独立作品、快照与查询一致性、版本关系及领域依赖边界。`tests/basic-catalogue-commands.test.mjs` 使用内存仓储覆盖并发、SHA 竞争、响应中断、权限失败及批次原子性。原有完整数据、页面和 API 测试继续执行；Pages 和专项 CI 的路径触发范围已包含 `src/**`。

第三阶段已完成物理日志分片和事务仓储；正式库领域模型、独立标签分配记录及全站页面迁移仍是后续边界。

## 第二阶段：完整日志与应用服务

`createCatalogueService()` 统一持有快照、仓储、操作人、投影视图和待重试命令。连接读取失败时保留原会话；预览不修改快照或生成正式事件；保存失败后保留原操作 ID，成功后更新统一视图。只读快照被递归冻结，防止表单误改活动状态。界面仅收集输入、调用服务和绘制结果。

`basic-catalogue-edits.json` 的 schema 2 在当前状态旁增加独立的 `journal`：

- `baseline` 是迁移时完整的 schema 1 状态，当前检查点为 r30，保留26条更正及原有最近操作。其审阅散列由迁移前提交 `bc123909` 独立计算，回归测试固定验证。
- `events` 从检查点之后逐次追加：操作 ID、操作人、时间、原因、原始意图、前后修订、字段前后值、完整新增／移除身份、撤销目标。
- 快捷撤销仍只处理最近三次，但每次撤销会追加事件，完整日志不会随快捷列表截断而丢失。
- `replayJournal()` 按序检查前值、连续修订、身份唯一性和撤销目标，重建状态；`validateStore()` 对比重建状态与当前快照。不能只改 `records` 而遗漏事件。
- 迁移前更早的操作由 Git 历史追溯；本次不伪造缺失的逐次事件。`node scripts/migrate_basic_journal.mjs --write` 可幂等迁移，`--check` 只校验。

第二阶段曾将快照和日志放在同一个 JSON，利用一次 Contents API 写入保证一致性。第三阶段以多文件 Git 事务替代该存储方式，现行格式见下节。

已迁移的 schema 2 会被旧 schema 1 写入代码拒绝；新模型仍读取旧格式及测试夹具。构建和 CI 校验迁移状态。公开索引清单包含日志起始修订和事件数；编辑连接窗口可分页查看完整前后值。传给搜索线程的只是当前状态，不复制完整日志。

发布时 `version_browser_modules.py` 为 HTML 入口、嵌套导入和 Worker URL 统一添加提交号版本参数，避免新入口继续加载旧模型缓存。源文件不改写，登记数据字节不参与模块转换。

新增测试覆盖日志跨三次撤销窗口的保留、从检查点重放、操作 ID 重试、后续远程修改下的结果确认、连接失败、并发会话操作和完整模块图版本化。

## 第三阶段：快照与日志分片

| 文件或字段 | 内容与约束 |
|---|---|
| `data/basic-catalogue-edits.json` | schema 3 当前状态、三次快捷撤销、日志引用索引和当前状态 SHA-256；浏览时仅加载此文件 |
| `data/basic-catalogue-journal/checkpoints/r30.json` | 已审阅 schema 1 检查点，内容保持不变，以 Git blob SHA 固定引用 |
| `data/basic-catalogue-journal/events/rN-rM.json` | 连续事件分片；索引包含修订区间、操作 ID、字节数和 Git blob SHA |
| `transaction` | 仅存在于内存中，记录命令的基础状态及新增事件；禁止作为已保存快照读取 |

分片每份最多50个事件，以512 KiB为目标上限。单次大批量操作保持原子性，若单个事件已超上限则独占一片。未满的最后一片可以扩展：生成新的修订区间文件，再在同一提交内删除旧活动文件。已封存分片不再改写；旧快照仍可按不可变 blob SHA 获取历史对象。

`createBasicRepository()` 先读取主分支头，再在该提交上读取快照并核对 SHA。保存时依次创建日志与快照 blob、基于当前完整树创建新树、创建以所读头为父的提交，最后以 `force: false` 更新主分支引用。只有最后一步使结果对分支可见；此前任一步失败不改变有效文件。基树保留无关文件，竞争提交使引用更新失败，交给应用命令重读并按已有冲突规则重试一次。权限继续使用本仓库的 Contents: Read and write，不需要新增授权范围。协议依据 GitHub [Git Trees](https://docs.github.com/en/rest/git/trees) 与 [Git References](https://docs.github.com/en/rest/git/refs)。

正常读取验证当前快照的状态摘要，不下载全量历史。历史分页从最近分片倒序读取，按 blob SHA 缓存；提交响应中断时，通过索引定位原操作所在分片，核验唯一操作 ID 与原始意图。Git blob 读取失败可回退到已发布静态文件，仍须验证摘要；缺失、损坏或尚未发布时显示读取错误并允许重试，不显示成空历史。

构建和 CI 使用 `readBasicStoreSync()` 读取全部引用，校验文件摘要、长度、连续修订、操作 ID 与事件索引，再从检查点重放并对比当前状态。快照摘要用于检查内容一致性，不代替完整历史审计。`node scripts/migrate_basic_storage.mjs --write` 可幂等迁移 schema 1/2；`--check` 要求 schema 3 并执行完整审计。旧迁移命令仍可检查新格式，但不会降级。离线脚本使用同一分片规划，先暂存新日志再替换快照，异常时恢复；最终通过一次 Git 提交发布全部文件。

`tests/basic-catalogue-storage.test.mjs` 验证迁移、跨分片重放、封存文件不变、撤销与摘要错误。`tests/basic-catalogue-transaction.test.mjs` 使用实现真实 Git blob 摘要和父提交规则的内存服务，验证 blob／tree／commit／ref 各阶段故障、无关提交竞争、同字段冲突、响应中断后的幂等核验及历史按需读取。生产写入不使用测试记录验证。
