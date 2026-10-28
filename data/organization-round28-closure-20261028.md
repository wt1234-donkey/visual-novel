# 第二十八轮四项已取得结论的落库核对

来源为第二十八轮筛选报告（Library `libfile_6590785c491c819192074e637a638987`）。上一批第29轮只接入了五条未结问题，这四条在当时仍停留于旧台账与旧正式索引。此次按稳定记录 ID 叠加差异，原第10／16／20／29轮文件保留。

| 记录 | 第28轮结论及正式范围 | 数据库处理 |
|---|---|---|
| `identity-37` | 2016 Mobage 应用 `game_id=12024891` 的[当期存档](https://web.archive.org/web/20160808151439/http://www.mbga.jp:80/_game_intro?game_id=12024891)署“サービス提供：株式会社NextNinja”。 | `g209-v2` 追加**服务提供方**的发行层限定职责；原作PC `g209-v1` 与GREE独立。 |
| `identity-36` | 2016 GREE 应用 `73010` 的[当期存档](https://web.archive.org/web/20160808133739/http://jp.apps.gree.net:80/ja/73010)署“提供：株式会社NextNinja”。 | `g209-v3` 追加同类限定职责；GREE保留为平台，不把平台经营者写成作品提供者。 |
| `duty-558` | [1985年《QL Classic Adventures》原版手册](https://www.mocagh.org/firstera/qladv-manual.pdf)第2—3页：内含《The Adventure》，Sinclair Research Ltd 为首次出版方与包装／文档版权方，程序署 Abersoft Ltd。 | 建立独立的 `g089-ql-classic-adventures-1985` **限定版次索引**及Sinclair出版职责，Sinclair专题由待核移到发行关系。不猜配原先四条PDP-10／TRS-80／Apple II版，也不把普通QL后发改版计为新增内容。 |
| `duty-120` | [SEGA 官方授权发行表](https://www.sega.jp/history/hard/segasaturn/software_l.html)列1997-03-28 Saturn版 `T-27801G` 厂商为メディアワークス。 | 撤销ASCII专题卡片中“1997版ASCII发行”的历史错署，改显示 Media Works；1995 PC Engine 原版Hudson保持。ASCII保留旧专题锚点供归属纠正对照，不再列为该作待核参与职责。 |

三条“限版确认”与一条“归属纠正”仅适用于上表范围。GREE/Mobage页面署的是**提供方**，不是从中推断的完整合同出版法人；旧 `publisher` 与 `publisherCompanies` 原文仍在历史发行层。QL补充是有手册支持的限定出版关系，不计入主库普通新增平台发行或内容版本。ASCII历史 `company-coverage.json` 原文保留为迁移快照；校正层在生成的专题页、组织台账与正式专题成员索引中覆盖该错署。详见[机器可读差异](organization-round28-closure-20261028.json)。
