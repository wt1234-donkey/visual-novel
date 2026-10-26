# A—Z 创作登记 Y1：Yonago GAINAX—Yuzusoft（2026-10-26）

承接X1，按目录的英文排序核查Y组三项：Yonago GAINAX（米子ガイナックス）、Yuzusoft SOUR（ゆずソフトSOUR）、Yuzusoft（ゆずソフト）。Y累计3／3，A—Y累计312／312；下一项依排序为5pb.（数字组）。`reviewed`表示本轮审查、保留证据缺口，并非所有制作分工已确认。

## Yonago GAINAX

[米子ガイナックス株式会社官方公司概要](https://yonago-gainax.co.jp/conpany/company.html)记设立于**2014年5月**；公司负责人参与早期GAINAX不等于米子公司在1993年制作原版《プリンセスメーカー2》。因此为既有米子公司节点增加`established/2014-05/month`，不归并旧GAINAX。[Bliss Brain《Regeneration》说明](https://blissbrain.co.jp/pm2rg/)明确米子公司制作的是2024版新增片头动画，原有内容层一条`addedAnimation`保持，不据重绘或版权扩大为整部游戏开发。

## Yuzusoft SOUR

[EXNOA当事方新闻稿](https://prtimes.jp/main/html/rd/p/000002805.000032953.html)称SOUR是ゆずソフト的全年龄新品牌，《PARQUET》为出道作，于2021年7月31日在DMM GAMES发布，并明确株式会社ユノス制作；这是**已证的品牌活动月份**，不是法人成立日。为SOUR节点增加`brandActivityStarted/2021-07/month`。[Steam产品页](https://store.steampowered.com/app/1662840/PARQUET/)分别署名SOUR为开发者、NekoNyan与HIKARI FIELD为该平台发行者。既有SOUR的1条制作品牌、1条原作发行品牌、4条具体发行品牌职责保持；DMM浏览器和Steam版的未核内容关系不变。

## Yuzusoft

[官方产品目录](https://www.yuzu-soft.com/products.html)对应原有13部主品牌作品，包括2025年《ライムライト・レモネードジャム》；既有15条具体发行与13条原作发行品牌职责保持。SOUR的《PARQUET》另有自身品牌署名，父品牌在专题中针对该作的`pendingRole`保持。新闻稿提到ゆずソフト常规人员参与以及株式会社ユノス制作，不将其简化成父品牌对该作的单独开发署名，也不由主品牌产品目录批量推出各作品完整程序、美术或剧本职责。

## 应用与保护

本批只给两个既有主体添加有出处和精度的时间事实，无身份订正、无职责新增。326个实体及稳定ID、类别、名称与关系、80专题、40项身份待核、5011条职责、2234条专题引用及601项`pendingRole`保持。1274部主库作品、1487内容版本、2487平台发行、2175位置、原发行署名和内容关系保持。日期事实与缺口逐项记录于[JSON核查记录](entity-creator-y1-review-20261026.json)。

## 验证

本地校验通过：`validate_data.py`、`validate_entity_model.py`、282项Python测试、222项Node测试、四项生成器`--check`及`git diff --check`。公开部署状态以目标仓库合并与Pages运行记录为准。
