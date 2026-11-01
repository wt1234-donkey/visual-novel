# 公开游戏目录补充来源评估（2026-11-01）

本文件用于扩大基础身份库的来源覆盖，同时保持“来源记录”与“作品身份”分离。外部目录的条目不直接等于新作品；导入前仍需用来源ID、VNDB ID、名称、别名、年份和版本关系进行交叉核验。

## 已有来源（第20、21批延续）

- **VNDB Kana API**：第20批从 VN ID `v3178` 之后续采。保留 VNDB ID、标题、别名与 VNDB 的 release 日期年份；不推断开发者、发行者或具体版本。
  - API 文档：https://api.vndb.org/kana
  - 数据许可：https://vndb.org/d17
- **NextMoe Galgame API**：第21批从第93页开始。仅纳入 medium=galgame 且存在 VNDB ID 的记录；保留 NextMoe source ID 与 VNDB ID 两个独立标识，任一已存在即复用旧身份，不另建作品。
  - API：https://api.nextmoe.dev/v2/catalog/works

## 下一步优先接入：IFDB（Interactive Fiction Database）

IFDB 对早期互动小说、独立作者、文字冒险和小型叙事作品有补充价值，尤其适合覆盖 VNDB / NextMoe 之外的独立创作。

- 官方 API 文档：https://ifdb.org/api/
- 搜索 API：https://ifdb.org/api/search
- IF Archive 定期 SQL 导出目录：https://ifarchive.org/indexes/if-archive/info/ifdb/
- 官方文档明确说明 API 面向低频、用户驱动应用，不适合高频批量爬取；如需批量处理，应优先使用 IF Archive 提供的季度 SQL 导出，并控制下载/解析频率。
- IFDB 条目 TUID 是稳定的目录身份；API 可提供标题、作品作者、开发系统和 publication date。
- IFDB Terms of Service 说明，用户上传到 IFDB 的原创信息采用 CC BY 3.0 US；游戏本身、游戏文件及封面图不因此获得该许可。后续只考虑最小化的目录事实字段（TUID、标题、作者字段、年份、条目链接），保留 IFDB 链接与必要署名，不复制评论、长描述、封面图或游戏文件。
- 下一轮正式导入前，先验证最新导出 SQL 的表结构、字段来源、贡献者署名字段、删除/修订记录及重复条目处理；未经核验不把 IFDB 候选直接写入基础身份库。

## 可作为跨目录身份交叉表：Wikidata

Wikidata 结构化数据采用 CC0，适合作为目录 ID 的连接层，而不是唯一的年份权威来源。优先检查以下外部标识属性：

| 属性 | 对应目录 | 用途 |
|---|---|---|
| P3180 | VNDB | 连接现有 VNDB ID |
| P6748 | IFDB | 连接互动小说条目 |
| P6717 | Indie DB | 发现独立游戏 |
| P6299 | PC-9801 DB | 补充日本 PC-98 历史游戏 |
| P6337 | PCGamingWiki | 连接 PC 游戏条目 |
| P7005 | Adventure Gamers | 补充冒险游戏目录 |

Wikidata 项目 Q ID 可作为独立 source ID；外部目录 ID 必须原样保留。对发布日期存在多值、只有移植年份或与现有年份冲突的条目，放入待核队列，不直接覆盖已有年份。

- SPARQL 服务：https://query.wikidata.org/
- 数据许可：https://www.wikidata.org/wiki/Wikidata:Licensing
- 视频游戏标识符清单：https://www.wikidata.org/wiki/Wikidata:WikiProject_Video_games/Properties/identifiers

## 其他候选来源与使用边界

- **SteamSpy**：公开 API 无需密钥，`all` 接口按每页约1,000条分页，但该接口约每60秒才应请求一次；数据来自有限 Steam 用户样本，拥有量估计并非权威数据，近期作品尤其不稳定。可作独立游戏发现入口，年份与作品类型必须回查 Steam 商店或开发者官网。
  - API 说明：https://steamspy.com/api.php
  - 数据局限：https://steamspy.com/about
- **RAWG**：需要 API key；免费计划有个人项目限制，官方条款明确禁止数据再分发，因此不作为基础库批量镜像来源。
  - 文档与条款：https://rawg.io/apidocs
- **MobyGames**：API 需要申请 API key，存在请求额度；在没有相应授权和许可确认前，不自动批量复制其目录。
  - API 文档：https://www.mobygames.com/info/api/
- **IGDB**：API 需要 Twitch Client ID 与 OAuth token；完整数据转储仅向数据合作伙伴提供。未取得凭证/合作授权前不作为自动导入源。
  - API 文档：https://api-docs.igdb.com/

## 统一导入规则

1. 每条来源记录保留 `sourceId`、可用的 `vndbId`、标题、别名、年份、原始条目 URL 与 sourceRefs。
2. 先按 source ID / VNDB ID 精确复用，再按规范化标题、别名与年份交叉去重。
3. 名称相同但年份冲突、疑似重制/合集/Fan Disc/DLC、来源年份不清楚的记录进入独立审计，不强行合并。
4. 每批最多新增500个身份；扫描数、跳过原因、冲突数、待核数均写入独立审计文件。
5. 基础身份层不等于精选叙事作品主库；不自动生成剧情编目、创作者署名、内容版本或发行关系。

## 第20、21批的多样性核验

本轮 VNDB 采用 ID 断点连续采集，NextMoe 采用目录分页连续采集，优先保证断点可复现和不漏掉来源序列中的候选。为避免把“跨年代/跨厂商/独立制作”当作未经验证的结论，配套生成 `data/basic-r20-r21-diversity-audit-20261101.json`：通过 VNDB ID 回查开发者 producer ID、名称和类型（公司 `co`、个人 `in`、业余团体 `ng`），并按年代统计。个人/业余团体仅作为独立创作信号，不直接推定独立工作室；无开发者字段也不代表没有开发者。下一批将结合该审计与 IFDB/IndieDB 等来源，优先补足年代和创作者类型分布不足的区间。


## 第22批续批与第23批（2026-11-01）

- 已上线的第22批 `v3968 → v4819` 保持不变。本次 VNDB 从 `v4819` 之后开始，独立标记为 `vndb-kana-bulk-20261101-r22-cont1`；NextMoe 第23批按用户要求从第93页重扫，旧条目按精确VNDB/来源ID复用，不改旧ID或重复建档。
- 每个来源在限定页数内先建立约900条合格候选池，再按“年代×开发主体类型”轮流选择，每组内轮流取不同开发者，最多新增500部。以当前基础库稀缺年代优先开始；若候选池不足则如实报告。VNDB的 `in` / `ng` 只是个人/业余团体信号，不等于已证实独立制作。
- NextMoe新候选回查VNDB，使用同一VNDB ID的作品级 `released` 年份；保留NextMoe原日期供比对，不用译版/目录日期覆盖原始年份。地区、版次和最初内容发行仍待逐项核实。
- 同源或跨源已有身份只写入审计 `reusedExisting`，包含匹配到的旧作品ID，不追加新作品。新增NextMoe候选使用 `vndb-vNNN` 作为作品ID，另保留 `nextmoe:NNN` 来源引用。
- 合格但未选中的候选完整保存在各审计 `deferredEligible` 中。下一批必须先读取该队列并对当前全库重新去重，再从 `cursorEnd` 或 `endPage` 之后续采；**不能只移动断点而丢弃队列**。不同来源的暂存候选可能在另一批已被选中，重读队列时需再按VNDB ID复用。
- IFDB接入为补充候选适配器：按1976—1989、1990—2009、2010—2026三个时间范围各做一次低频搜索，每组最多保留20条最小事实字段。本轮不直接导入IFDB作品，只记录标题、TUID、源日期、作者字段、开发系统、链接及与现有库的名称匹配。后续大规模分析应读取IF Archive SQL导出，不分页爬取API。
- IFDB官方接口：https://ifdb.org/api/ ，搜索JSON根地址为 `https://ifdb.org/search?json&game&searchfor=...`；不是将文档地址 `/api/search` 当作数据接口。可选补充源暂时无法访问时独立报告，不影响两个已授权来源的采集与验收。
- `data/basic-r22-cont-r23-diversity-20261101.json` 保存实际年代、开发者类型和厂商分布。所有开发者信息只在审计层记录，不增补正式署名。

### NextMoe分页上限与续采方式

实际采集确认 `page=101&limit=100` 返回400 `INVALID_PARAMETER`：官方页码模式要求 `page × limit ≤ 10000`。因此第23批先如实完成第93—100页，然后改用官方支持的 `sort=id` 与 `released_after` / `released_before` 年代区间筛选，原样回传服务器的 `next_cursor`，不自行拼造游标或提高页码绕过上限。区间依次1976—1999、2000—2009、2010—2026-11-01，先补足早期覆盖。最多60次额外游标请求，仍遵守每批最多500部的新增上限。

每次请求的车道、区间、实际使用游标及返回游标保存到第23批审计 `summary.paginationTrace`。下一批先消化 `deferredEligible`，再从最后未耗尽区间的返回游标继续，并保留尚未遍历的后续区间；不能将 `endPage=100` 误当成整个目录已经取完。

官方契约：https://developer.nextmoe.dev/docs/pagination 、https://developer.nextmoe.dev/docs/v2/listCatalogWorks 。
