# 资料管理台使用说明

从首页右上角进入“资料管理”，或打开 `manage.html`。使用原有作品 ID，不另建重复档案。

1. 搜索中文名、原名、角色或作品 ID，选中作品；录入独立新作时点击“＋ 添加新作品”。

   新作品填写中文名、原名、首发年份、主／细分类、剧情简介、角色、玩法及各项来源，再填写一个原作内容与有确证的首批平台发行。同批平台逐行输入，共用一个内容 ID。系统建议尚未使用的作品 ID，并与主库、专题关联、仅专题书目和既有补录数据检查重名／ID 冲突。

   点击“将新作品加入修改清单”后，可继续补充四项叙事编目和创作者署名，随新作品一并提交。资料不足的编目可以暂缺，不能填占位词冒充已完成。普通移植或后发增补不能当独立原作录入；输入式书目的特殊准入仍走独立专题审查。

   同名独立作品需要额外身份核实，自动重复检查会阻止直接录入；存在并行补录导致的 ID 冲突时，保留草稿并重新核对，不能覆盖别人新加的作品。
2. 在“四项叙事编目”逐项填写结论、具体理由、资料摘记与来源。留空代表尚未核清，需要记录待核问题；最初八部历史基线只读。
3. 在“创作者署名”复用或新增个人身份，填写职责与版次范围。已有发行、库外产品与具名作品分工分别记录。勾选核实确认，再加入修改清单；既有署名订正通过补充说明单独审查。
4. “内容与版本”展示已存在的内容身份及历史发行。新发现的差异、角色补充和基础资料订正建议，在“补充说明”中附来源记录。这里不会自动新增正式内容版本或平台发行。
5. 表单输入自动存为本机草稿，但只有点击“加入修改清单”的记录才进入提交包。跨设备前点击“导出草稿”，在另一设备导入。草稿导入会检查记录冲突；与新数据库冲突的草稿必须重新核对，不强行覆盖。
6. 进入“审核与提交”，填写修改说明，检查每项修改前后的差异。点击“校验并准备 GitHub 提交”，复制更新包并打开 GitHub 提交页。
7. 登录有仓库写入权限的 GitHub 账号，选择 `main`，点击 **Run workflow**，将更新包粘贴到“资料管理更新包（JSON）”，运行。每批最多30项记录、60000字符；较大更新请分批。
8. 等待 Actions 运行完成，在运行摘要中打开 PR。如果仓库未启用机器人创建 PR，摘要会提供比较链接，手动点击 **Create pull request**。
9. 审核 PR 的 **Files changed** 后合并 `main`，等待 GitHub Pages 更新。失败步骤会显示原因，失败不会改写 `main`。

管理入口公开可访问；修改须经过 GitHub 登录与仓库写入权限。网页不索取、存储或嵌入 GitHub 令牌。更新包、修改历史和 PR 位于公开仓库，不要填写私密资料。

本机草稿不等于数据库已更新。PR 合并后请确认页面已更新，再清除本机草稿。后发增补版本、组织关系与历史身份订正仍需独立考据，不绕过现有保护规则。

## 本地使用更新包

在干净的独立分支运行：

```sh
python3 scripts/manage_catalogue.py path/to/update.json
python3 scripts/sync_versions_csv.py
python3 scripts/export_content_csv.py
python3 scripts/export_interaction_csv.py
python3 scripts/build_entity_model.py
python3 scripts/build_entity_pages.py
python3 scripts/build_company_pages.py
python3 scripts/audit_narrative_pending_20261030.py
python3 scripts/manage_catalogue.py --check
python3 scripts/validate_narrative_editorial.py
python3 scripts/validate_data.py
python3 scripts/validate_entity_model.py
python3 scripts/run_python_tests.py
node --test tests/*.test.mjs
python3 scripts/build_entity_model.py --check
python3 scripts/build_entity_pages.py --check
python3 scripts/build_company_pages.py --check
```

管理历史逐项保存修改前后的值与来源。历史回归依此还原原审阅范围，同时单独验证当前数据；不会用重新冻结基线的方式掩盖历史修改。
