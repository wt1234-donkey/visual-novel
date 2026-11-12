# 第2批：可信保存与强制校验边界

## 当前状态

PR #329、#330 已合并并上线。隔离规则 `Catalogue save gate rehearsal`（ID 27081428）已启用，仅匹配 `validation/trusted-save-gate-*`，要求 GitHub Actions 的 build 检查，禁止强推和删除，绕过清单为空。

真实 GitHub 派发验证 [43131680398](https://github.com/wt1234-donkey/visual-novel/actions/runs/43131680398) 已通过：认证事件、不可变命令、来源/修订校验和日志回放均通过；隔离提交 `8efa2b4a7b5366773afafff6d95ccea7d54bd0e3` 在缺少或失败 build 检查时均被 GitHub 拒绝，在成功检查后获准写入，main 未改变。

`data/trusted-save-policy.json` 现切换为 `mode: trusted`。本次发布后完成真实回执、自动 Pages 请求及主分支规则验收。规则管理通过管理员界面完成，无需扩大浏览器保存凭据的权限；最终状态以实际启用的 main 规则和线上发布版本为准。

旧写入入口已核对：历史导入的 Git push 都指向 PR 分支，管理台也生成 PR，合并后统一受 main 的必需检查约束。唯一旧直接 main 发布入口为 `editorial-publish.yml`，现补上经过全量验证的数据提交证明和非强制更新；不允许它携带代码变更。该入口对基础修改复用共同动作验证器，可信模式下基础/正式旧提案必须携带来源凭据，批次 ID 重试核对完整命令摘要。发布任务必须核对实际线上部署祖先才报告完成。

## 执行方案与权限决策

沿用 GitHub Actions 作为执行端，不增加外部服务、不在站点存放用户凭据。浏览器仍使用本仓库的 Contents 写入凭据：先上传不可变的命令 blob，再通过 `repository_dispatch` 派发其 SHA；无需把用户 token 交给执行端，也不要求浏览器凭据增加 Actions 或 Administration 权限。

新工作流仅使用作业期 `GITHUB_TOKEN` 的 Contents 写入和 Statuses 写入权限。它从 main 检出规则、从 GitHub 事件取得操作人、核对 blob 摘要、来源及规则凭据、目标修订、字段和业务限制。用户不能指定执行代码、仓库、分支或文件路径。命令只允许基础更正/标签/合并/撤销及正式更正/创作者/撤销；不接受浏览器提供的最终数据库快照。创作者姓名仍可无证据保存。

执行通过后，在隔离工作区形成数据修改；数据和日志回放检查通过后，只将允许的更正快照、追加事件及命令回执组成同一 Git 提交。执行端先为该提交发布 `build` 成功状态，再以非强制引用更新写入 main。main 已变化则拒绝更新，保留原操作 ID 重试。脚本型编辑可复用 `executeCommand(root, command, authenticatedActor)`，不能直接修改覆盖快照来绕过领域验证。

操作 ID 按 SHA-256 定位回执。重复操作在核对实际认证人和完整原始命令后返回已有结果，即使其后已有新修订也不会再次应用；同一 ID 搭配不同命令拒绝。前端只有读取并验证 main 中的回执才提示已保存，派发成功本身不算保存成功。派发响应丢失时核对同一操作；超时保留输入并显示结果待确认。

GITHUB_TOKEN 写 main 不会自动触发 push 构建，因此显式发送独立的 `catalogue-release-request`，随后复用第1批累计构建及串行部署。重复派发只核对回执并补发构建请求，不重复改数据。

## 强制规则草案及待完成验收

建议 main 要求 GitHub Actions（App ID 15368）提供 `build` 成功检查，禁止删除和强推，不配置常规绕过者。这样代码 PR 继续经过现有全套检查，数据命令由受信执行端在落库前校验。所有者仍能主动修改仓库规则；此权限属于仓库所有权，不由网页撤销。规则草案不把 main 设为只能走人工审核 PR，以保留个人保存能力。

**切换前必须一起完成，不能只打开规则：**

1. 获得仓库管理规则的操作能力，核对实际规则及状态来源；在隔离分支确认失败检查被拒、合法数据提交可通过。
2. 对管理台 PR 通道、旧审核发布及仍需使用的脚本/导入流程逐项登记和迁移。旧直接发布已接入提交证明；历史 PR 写入边界由自动检查固定，任何通道都不加入绕过清单。
3. 联调实际 GitHub 派发、回执和自动 Pages 请求。测试使用隔离库，不能向生产目录写测试作品。
4. 先切换 `mode: trusted` 并核对单作品、批量标签、CSV、AI候选确认和正式姓名保存，再启用必需检查规则；顺序不能倒置。通道验证失败则在启用规则前保持原通道并保留输入；不得让前端静默退回直接写入以绕过已启用门禁。

只有这些验收全部通过，才可宣告第2批完成。当前自动化覆盖命令与领域校验、旧来源/旧修订/伪造身份、重复操作与冲突、失去响应、数据提交白名单及非强制更新顺序；真实浏览器通过隔离 Git 服务联调新保存路径，不等于实际仓库规则已启用。

## 官方接口依据

- [repository_dispatch：Contents 写入权限](https://docs.github.com/en/rest/repos/repos#create-a-repository-dispatch-event)
- [GITHUB_TOKEN 的触发例外](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)
- [必需检查与预期来源](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets)
- [检查与同名状态的行为](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)

## 隔离验证入口

在 Actions 运行 **Catalogue command gate rehearsal**（main）。第一轮只上传标准命令 blob 并派发专用 repository_dispatch；第二轮用相同业务执行器验证，原子提交到唯一的 `validation/trusted-save-gate-<run_id>` 分支。它依次断言缺少检查和明确失败检查均被拒绝，再由 GitHub Actions 给出成功证明并验证更新获准，最后确认 main 未改变。该验证与生产命令使用相同对象摘要、认证事件、来源/修订及回执规则；专用事件和命令行标记共同限制隔离路径，不能通过生产 payload 切换目标分支。

随后通过网页的同一 `submitCommand` 回执验证器读取真实隔离分支，核对 Git blob 摘要、完整原始命令、身份和修订；该步骤只允许 GET。最后发送与生产相同的 `catalogue-release-request`，由 Pages 工作流构建 main，因此测试作品不会被发布。首次验收遇到未完成的基线 build 时，GitHub 拒绝了隔离分支创建；基线检查通过后重跑成功，没有放宽规则。

仓库所有者仍可主动修改规则，这是所有权边界；常规网页保存、脚本和 PR 不配置绕过者。测试数据仅出现在隔离验证分支，不进入生产目录。
