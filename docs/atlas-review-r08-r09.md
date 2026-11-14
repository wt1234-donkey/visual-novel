# R08 / R09：职责拆分与长期验证

本轮不处理身份、日期或署名案件，不新增事实裁决。来源108,173条、原ID、109个源分片及现有证据保持不变。

## R08

保留 discovery.mjs、manage.mjs、live-work-editor.mjs 兼容入口。表单与历史呈现放入 src/features；检索、草稿恢复、表单值和编辑上下文读取放入 src/application。根入口管理页面生命周期与取消信号；领域规则与可信执行协议沿用现有模块。资源加载器独立处理失败与取消，旧请求不得覆盖新选择。

历史生成规则由 config/historical-entity-rules.json 登记。外层摘要、冻结基线、105份证据文件摘要、具名身份／关系／署名适用范围及执行序列统一校验。脚本保留异构旧资料格式适配与限制性断言；不在本轮重新判定历史事实。两个生成器的六份实体与组织产物与拆分前逐字节一致。

## R09

config/public-entrypoints.json 覆盖发布白名单全部106个HTML入口，登记脚本、必需资源和数据完成后的启动信号。新入口未登记或入口脚本漂移使验证失败。Chromium以实际静态发布包逐页启动，并记录异常、缺失资源与耗时。组织关系、组织目录和精选页另有必需资源503后的提示与刷新恢复演练。

verify_public_displays.py 对实际HTML正文和CSV逐条验证当前名称／年份，避免只有源数据正确而可见页面仍旧。正式目录的全部摘要另由浏览器套件与有效投影比较。发行年份属于发行层级，不强制等于作品首次年份。

verify_archive_recovery.mjs 仅向全新隔离目录恢复：验证发布对象图、恢复四类逻辑存储、移除索引、重新构建，再次回放并比较逻辑摘要。无需Git和源分片；不自动将恢复结果作为正式写入输入。已有摘要篡改、缺失对象及语义伪造检查继续执行。

容量覆盖保留万条查询、三类万条启动和100次连续追加；另以340项并存断言、多个字段与适用范围验证分页、末页选用值固定展示、完整CSV及零事件正文读取。

## 条件能力

所有条件跳过必须与 config/test-capabilities.json 中的模块和历史ref对应，逐项记录原因、替代覆盖与局限。当前功能回归在无Git副本执行；历史精确增量单独显式运行。

实体Android设备尚未连接，不能将模拟结果计为真机通过。已提供脚本：

```sh
PLAYWRIGHT_MODULE=/path/to/playwright node scripts/measure_android_device.mjs --serial DEVICE --physical-device --report test-results/android-real-device.json
```

设备需已授权ADB调试、Chrome已运行。脚本拒绝已知模拟器，记录型号、系统、网络与浏览器，三次真实导航取中位数；不模拟CPU、视口或网络。无设备调用只报告unavailable。传输方式依据Chrome远程调试文档与Playwright的connectOverCDP接口；该能力需在真实设备首次执行后才能关闭“真机测量未完成”条件。

CI必需验证包含全部入口、当前显示、隔离恢复和现有浏览器编辑回归；test-results中各项报告作为构建附件保留。配置和脚本不进入运行产物。
