# 第2批：可信保存与强制校验边界

## 当前状态

第2批已完成可信保存、发布联调和主分支强制校验的切换。实现由 PR #329、#330、#332、#333 合并上线；实现与真实发布验收基准为 `3328761a00f9be71a4158aa0a461e055a8719885`。

经仓库所有者于2026-11-12明确授权，`Verified main updates`（ID 27095396）已创建并启用。GitHub 返回 `main.protected: true`；规则匹配默认分支 main 的全部文件更新，要求 GitHub Actions（App ID 15368）的 `build` 成功，严格检查最新基线，禁止删除和强推，绕过清单为空。没有要求每次数据保存先提交人工审核 PR。

隔离规则 `Catalogue save gate rehearsal`（ID 27081428）继续仅匹配 `validation/trusted-save-gate-*`。已逐字段核对：两条规则的三项执行规则完全相同，仅名称、目标分支及 GitHub 元数据不同。实际主分支配置导出为 `config/main-ruleset.active.json`；`config/main-ruleset.proposed.json` 保留为默认禁用的准备模板，不代表线上状态。

真实 GitHub 派发验证 [43131680398](https://github.com/wt1234-donkey/visual-novel/actions/runs/43131680398) 已通过：认证事件、不可变命令、来源/修订校验和日志回放均通过；隔离提交 `8efa2b4a7b5366773afafff6d95ccea7d54bd0e3` 在缺少或失败 build 检查时均被 GitHub 拒绝，在成功检查后获准写入，main 未改变。

`data/trusted-save-policy.json` 已切换为 `mode: trusted`。真实回执、自动 Pages 请求及独立部署均已验收通过，随后才启用 main 规则。规则管理通过管理员界面完成，浏览器保存凭据继续只需本仓库 Contents 读写；个人仍点击保存即可提交，未增加人工发布审核。

旧写入入口已核对：历史导入的 Git push 都指向 PR 分支，管理台也生成 PR，合并后统一受 main 的必需检查约束。唯一旧直接 main 发布入口为 `editorial-publish.yml`，现补上经过全量验证的数据提交证明和非强制更新；不允许它携带代码变更。该入口对基础修改复用共同动作验证器，可信模式下基础/正式旧提案必须携带来源凭据，批次 ID 重试核对完整命令摘要。发布任务必须核对实际线上部署祖先才报告完成。

## 执行方案与权限决策

沿用 GitHub Actions 作为执行端，不增加外部服务、不在站点存放用户凭据。浏览器仍使用本仓库的 Contents 写入凭据：先上传不可变的命令 blob，再通过 `repository_dispatch` 派发其 SHA；无需把用户 token 交给执行端，也不要求浏览器凭据增加 Actions 或 Administration 权限。

新工作流仅使用作业期 `GITHUB_TOKEN` 的 Contents 写入和 Statuses 写入权限。它从 main 检出规则、从 GitHub 事件取得操作人、核对 blob 摘要、来源及规则凭据、目标修订、字段和业务限制。用户不能指定执行代码、仓库、分支或文件路径。命令只允许基础更正/标签/合并/撤销及正式更正/创作者/撤销；不接受浏览器提供的最终数据库快照。创作者姓名仍可无证据保存。

执行通过后，在隔离工作区形成数据修改；数据和日志回放检查通过后，只将允许的更正快照、追加事件及命令回执组成同一 Git 提交。执行端先为该提交发布 `build` 成功状态，再以非强制引用更新写入 main。main 已变化则拒绝更新，保留原操作 ID 重试。脚本型编辑可复用 `executeCommand(root, command, authenticatedActor)`，不能直接修改覆盖快照来绕过领域验证。

操作 ID 按 SHA-256 定位回执。重复操作在核对实际认证人和完整原始命令后返回已有结果，即使其后已有新修订也不会再次应用；同一 ID 搭配不同命令拒绝。前端只有读取并验证 main 中的回执才提示已保存，派发成功本身不算保存成功。派发响应丢失时核对同一操作；超时保留输入并显示结果待确认。

GITHUB_TOKEN 写 main 不会自动触发 push 构建，因此显式发送独立的 `catalogue-release-request`，随后复用第1批累计构建及串行部署。重复派发只核对回执并补发构建请求，不重复改数据。

真实运行 43158549064 暴露了构建完成后的 `workflow_run` 未触发部署这一尾项。现在，自动派发的构建上传已校验产物后，显式发送 `catalogue-deploy-request`，仅携带它自己的 GitHub run ID；独立部署队列重新核验仓库、工作流路径、main、成功状态、最新提交、产物来源及摘要。构建作业仍只读；单独的派发作业只在 main 的指定事件成功后使用作业期 Contents 写入权限，不改变浏览器凭据。部署继续独立串行运行，新构建取消不会中断正在部署的作业。push/手动构建沿用原 `workflow_run` 通道，自动派发构建不重复走该通道；回退仍保留单独的手动参数和验证。

## 已启用的强制边界及验收证据

main 已要求 GitHub Actions（App ID 15368）提供 `build` 成功检查，禁止删除和强推，不配置常规绕过者。代码 PR 继续经过现有全套检查，数据命令由受信执行端在落库前校验。所有者仍能主动修改仓库规则；此权限属于仓库所有权，不由网页撤销。规则没有将 main 设为只能走人工审核 PR，以保留个人保存能力。

**已按先验证、后切换的顺序完成：**

1. 获得仓库管理规则的操作能力，核对实际规则及状态来源；隔离分支确认缺失、失败检查被拒，合法数据提交可通过。
2. 核对管理台 PR、旧审核发布及历史脚本/导入入口。旧直接发布接入提交证明，历史导入写 PR 分支；没有为任何通道添加绕过者。
3. 通过真实 GitHub 派发、网页同一回执验证器、自动 Pages 请求和独立部署联调。测试作品只出现在隔离分支，生产目录未写入测试事件。
4. 单作品、批量标签、CSV、AI候选确认、正式姓名保存和故障恢复回归通过，`mode: trusted` 上线后，再启用 main 必需检查规则。前端不会静默退回直接写入来绕过规则。

| 验收项 | 已取得的证据 |
|---|---|
| 业务验证、来源/修订、身份与幂等 | 414项 Node 回归通过，覆盖非法字段、旧来源/修订、伪造操作人、完整命令重试及响应丢失；单作品、批量标签、实际CSV解析、AI确认行及无证据姓名保持可用 |
| 数据、生成器、发布及权限回归 | Python 553项中511通过、42按既有条件跳过；数据/实体、源分片、日志回放、生成器和完整静态构建检查通过 |
| 页面交互 | 4项 Chromium 回归通过，包含真实表单在隔离 Git 服务下走可信保存和跨发布草稿恢复；未将其冒充为生产作品写入测试 |
| 实际 GitHub 规则拒绝与放行 | 运行 [43160375424](https://github.com/wt1234-donkey/visual-novel/actions/runs/43160375424)：缺少/失败 build 均被拒，成功证明后写入隔离提交 `35dd4fa0aff2440e838e7c798cff1953e0913669`，main 不变；同一网页回执验证器核验身份、完整命令、修订及 blob 摘要通过 |
| 未检查代码的常规合并 | 隔离代码 PR #331 缺少 build 时合并 API 返回405及必需检查错误，已关闭；main 当前启用与该隔离验证相同的执行规则 |
| 自动构建到实际上线 | 上述命令触发构建 [43160477401](https://github.com/wt1234-donkey/visual-novel/actions/runs/43160477401)，交接到部署 [43160978733](https://github.com/wt1234-donkey/visual-novel/actions/runs/43160978733)；构建、派发与独立部署均成功，部署日志确认使用该构建ID，线上清单/目录/可信保存策略一致 |
| 数据保真 | 108173条源记录逻辑SHA256仍为 `2b419f6b412eda7898f4705d2aae137f21f8bdb516ef4421e28fdbe3932c29a2`；生产更正保持r30、检查点和已有事件不变，未通过迁移重编号或自动合并身份 |

正式作品的完整追加审计仍属于第4批；不补造迁移前已经缺失的历史。仓库所有者主动修改规则的能力仍属于所有权边界。后续批次必须继续保留当前业务、来源、幂等和发布检查。

## 官方接口依据

- [repository_dispatch：Contents 写入权限](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)
- [GITHUB_TOKEN 的触发例外](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [必需检查与预期来源](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [检查与同名状态的行为](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)

## 隔离验证入口

在 Actions 运行 **Catalogue command gate rehearsal**（main）。第一轮只上传标准命令 blob 并派发专用 repository_dispatch；第二轮用相同业务执行器验证，原子提交到唯一的 `validation/trusted-save-gate-<run_id>` 分支。它依次断言缺少检查和明确失败检查均被拒绝，再由 GitHub Actions 给出成功证明并验证更新获准，最后确认 main 未改变。该验证与生产命令使用相同对象摘要、认证事件、来源/修订及回执规则；专用事件和命令行标记共同限制隔离路径，不能通过生产 payload 切换目标分支。

随后通过网页的同一 `submitCommand` 回执验证器读取真实隔离分支，核对 Git blob 摘要、完整原始命令、身份和修订；该步骤只允许 GET。最后发送与生产相同的 `catalogue-release-request`，由 Pages 工作流构建 main，因此测试作品不会被发布。首次验收遇到未完成的基线 build 时，GitHub 拒绝了隔离分支创建；基线检查通过后重跑成功，没有放宽规则。

仓库所有者仍可主动修改规则，这是所有权边界；常规网页保存、脚本和 PR 不配置绕过者。测试数据仅出现在隔离验证分支，不进入生产目录。
