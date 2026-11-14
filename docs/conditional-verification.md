# 历史验证恢复与Android真机采样

## 42项历史断言恢复

`config/historical-baseline-recovery.json`固定19个基线的原引用、实际审核提交与父提交、完整树SHA、原始文件摘要、生成器摘要和原42个测试方法的AST摘要。测试方法未删改。

14个无效短引用重新锚定实际审核文件首次加入的已发布提交之父，29项原断言直接读取其原Git对象。另5个已发布基线含损坏派生JSON；在隔离目录提取同一原提交的data与scripts，校验原生成器摘要后重建，13项原断言读取该重建结果。所有尚完好的原生成文件必须逐字节相等，重建输出也必须匹配固定摘要；不使用当前生成器、当前资料或反向猜测旧值。

原始坏Git对象原样保留，原失效引用保留在恢复登记及测试中的ORIGINAL_BASE。恢复的是可复现的历史差量验证，不宣称把坏字节修复成某个从未提交的有效原文件。来源、树、生成器或结果摘要不符均失败，不能静默跳过。当前功能仍在无Git副本执行，历史专项独立、显式运行。

```sh
python3 scripts/verify_historical_baselines.py
python3 scripts/run_python_tests.py --historical --report test-results/historical-complete.json
```

报告逐项区分published-parent与frozen-generator-replay，并记录未改写原对象。历史手动工作流保留来源验证与完整用例结果。

## 手机上完成真机采样

在真实Android设备浏览器打开[真机测量入口](https://wt1234-donkey.github.io/visual-novel/device-check.html)，确认设备后点击开始，保持前台。发现页、管理台、批量页各采样三次，完成后下载或复制报告发回核验。页面只打开目录，不提交数据库编辑。

采样使用可见同源iframe，记录实际视口、网络估计与资源时间；缓存保持自然状态，首次与后续分开保留。ResourceTiming可能因缓存或接口限制记录零字节，不能当作完整线路流量；可选JS堆可能由同进程共享。单页45秒、发布清单15秒、可选设备提示3秒。超时、停止、切到后台、脚本错误或版本切换会结束等待并保留部分结果。

网页不能独立认证物理硬件，报告保留hardwareAttested=false和reviewed=false；CI模拟结果只验证采样流程，不能登记成真机实测。需要用户在自己的真实设备上执行，并回传报告核验后才能关闭真机条件。已有ADB设备级测量命令继续可用。
