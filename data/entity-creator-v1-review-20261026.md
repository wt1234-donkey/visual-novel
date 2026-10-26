# A—Z 创作登记 V1：Virgin Games Ltd—VISUAL ARTS（2026-10-26）

承接U1，按既定英文排序连续核查V组两项并收尾。V累计2／2，当前A—V队列登记302／302，下一项WFS（WRIGHT FLYER STUDIOS）。登记包含证据缺口，不代表所有历史发行与制作分工已经查清。

## Virgin Games Ltd

1987年《The Growing Pains of Adrian Mole》的原说明书索引可读文字署“Published by Virgin Games Ltd”；同期《CRASH》38期广告由Virgin Games销售，支票抬头具名Virgin Games Ltd，另署“Produced by Mosaic Publishing Ltd”。据历史具名Ltd销售和出版主体，将其从`unknown`订正为`company`。保留ZX Spectrum原版一条`publisher`，不将其推为程序制作方；Level 9与Mosaic各自职责仍需按原版证据和地区分开。

来源：[原说明书扫描](https://www.mocagh.org/rainbird/adrianmole2-alt.pdf)、[1987同期广告](https://electronicsandbooks.com/edt/manual/Magazine/C/Crash%20Sinclair%20Spectrum%20Games%20UK/Crash38-Mar87%20c20111224%20%5B124%5D.pdf)、[Spectrum原版发行档案](https://worldofspectrum.org/archive/software/text-adventures/the-growing-pains-of-adrian-mole-virgin-games-ltd)。本次检索接口对两份PDF直读报错，仅使用可读搜索摘录，不冒称逐页查看扫描；先前[Mosaic审计](mosaic-audit.md)另列原手册实物的明确发行句。

限制：[MobyGames发行细目](https://www.mobygames.com/game/15160/the-growing-pains-of-adrian-mole/releases/)直读403，搜索摘要使用Mosaic发行、Virgin分销的不同细分口径。待原封套与地区版次核清前，不改原库Virgin署名，不把广告中其余机种及其同日标价变成新的内容或平台发行。Virgin Mastertronic及集团沿革也不合并。

## VISUAL ARTS

[官方公司概要](https://visual-arts.jp/)具名株式会社ビジュアルアーツ；[官方沿革](https://visual-arts.jp/history/)将1991年前身、1996更名、1998 Key开发室、1999 Key品牌分开。[2024官方博客](https://visual-arts.jp/blog_2024_1/)及[员工访谈](https://visual-arts.jp/recruitment/interview/crosstalk04/)继续将VISUAL ARTS公司和Key品牌区分。既有`company/sourceReviewed`身份保持；46条发行公司职责、Key既有制作品牌及运营关系均保持。

无法只从公司母体、引擎或发行推出25部关联作品的逐作公司原作制作；原资料尚需逐作核对。官方沿革年份也不填入现有空`dates`字段，避免把前身创立年当现公司名首用年。此项属于已核身份复查，没有人为制造新角色。

## 应用与保护

仅订正Virgin Games Ltd一项身份，复核VISUAL ARTS既有公司身份。326个实体及其ID、旧名、别名、日期、关系、80专题不增删；身份待核45降至44。5009条职责、2234条专题引用和601项`pendingRole`逐条保持；原作品、1487内容版本、2487平台发行与原publisher对象保持。

U1精确差异断言固定在已发布树`d4370f1cf0fc8984ff5dab3bd458fec81f93b0f8`；本批另核单项身份变化、既有VISUAL ARTS／Key分设、全部职责和原始对象不变、V完整排序及下一个WFS。

独立记录见[JSON核查](entity-creator-v1-review-20261026.json)。

## 验证

272项Python、222项Node测试通过；数据及实体校验、四项生成器`--check`与`git diff --check`通过。部署状态另以GitHub Actions确认。
