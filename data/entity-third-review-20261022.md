# 第三批主体与制作职责核查

核查日期：2026-10-22。基准：[b9a5a7e7f10568e005c58bdc346e04b7e8cec399](https://github.com/wt1234-donkey/visual-novel/commit/b9a5a7e7f10568e005c58bdc346e04b7e8cec399)，即PR #51后的main。

读取既有主体、参与索引、专题正文和卡片、原始发行及其链接后，优先选择高频发行主体和有具名开发证据的作品。分类为可直接确认8项、需要补充来源3项、暂不宜判断1项；同名品牌与公司仍是不同身份。人工输入为同名JSON，生成器只消费identityCorrections和creditAdditions，deferredReviews不触发修改。

## 可直接确认并实施

### T1：HIKARI FIELD

- 定位：`entity-name-5c51b719b1bb`。
- 原值：unknown／unresolved；改为company／sourceReviewed。
- 证据、缺口和范围：官网公司概要明确株式会社HIKARI FIELD。只确认该署名的公司类型，不将成员早期活动并为法人历史，不给全部作品批量追加翻译、移植或开发职责。
- 本轮读取来源：[1](https://www.hikarifield.com/jp/)；[2](https://www.hikarifield.com/)。
- 应改文件：独立JSON本项、生成器批次入口；派生entities.json、entity-migration-review.json、entity-catalogue.json、entities.html及引用主体的既有专题页。不改发行职责。

### T2：Sekai Project

- 定位：`entity-name-06aeb9d01fbe`。
- 原值：unknown／unresolved；改为company／sourceReviewed。
- 证据、缺口和范围：官方联络页列Sekai Project Inc.，公司十周年回顾亦明确公司身份；仅改类型，不把全部发行作品视为其开发或本地化，也不新增其他发行品牌关系。
- 本轮读取来源：[1](https://sekaiproject.com/contact/)；[2](https://sekaiproject.com/reflections-on-10-years-at-sekai-project/)。
- 应改文件：独立JSON本项、生成器批次入口；派生entities.json、entity-migration-review.json、entity-catalogue.json、entities.html及引用主体的既有专题页。不改发行职责。

### T3：CAPCOM

- 定位：`entity-name-7554e19bb041`。
- 原值：unknown／unresolved；改为company／sourceReviewed。
- 证据、缺口和范围：官方概要列CAPCOM CO., LTD.。只确认公司类型；不因一般开发业务介绍给各平台发行增加制作，不追加海外主体合并、日期或集团关系。
- 本轮读取来源：[1](https://www.capcom.co.jp/ir/english/company/info.html)。
- 应改文件：独立JSON本项、生成器批次入口；派生entities.json、entity-migration-review.json、entity-catalogue.json、entities.html及引用主体的既有专题页。不改发行职责。

### T4：Square Enix

- 定位：`entity-name-8a3d38d0d11f`。
- 原值：unknown／unresolved；改为company／sourceReviewed。
- 证据、缺口和范围：官方公司概要与既有2012原始发行公告明确株式会社スクウェア・エニックス。仅确认公司类型；不合并另存的日文署名、Square、Enix或控股公司，不补写2008以前法人连续性。
- 本轮读取来源：[1](https://www.jp.square-enix.com/company/en/outline/)；[2](https://www.jp.square-enix.com/company/ja/news/2012/html/b72327bc03e5a1056508e9bfb870ea96688e6b25.html)。
- 应改文件：独立JSON本项、生成器批次入口；派生entities.json、entity-migration-review.json、entity-catalogue.json、entities.html及引用主体的既有专题页。不改发行职责。

### T5：Serenity Forge

- 定位：`entity-name-22015689e48e`。
- 原值：unknown／unresolved；改为company／sourceReviewed。
- 证据、缺口和范围：官方About明确其为游戏开发与发行公司，页脚列Serenity Forge LLC。只确认类型，不由公司综合业务或联合版权给DDLC原作追加开发，不合并Team Salvato或Dan Salvato LLC。
- 本轮读取来源：[1](https://serenityforge.com/about)；[2](https://serenityforge.com/games/doki-doki-literature-club-plus)。
- 应改文件：独立JSON本项、生成器批次入口；派生entities.json、entity-migration-review.json、entity-catalogue.json、entities.html及引用主体的既有专题页。不改发行职责。

### T6：g647

- 定位：`entity-overdrive`／`g647`。
- 原作品角色：无；仅追加`originalProduction`。
- 证据、缺口和范围：2011年8月30日MangaGamer官方发行公告明确OVERDRIVE开发，Steam开发者字段一致。只确认2011原作制作；2015／2016扩充逐内容职责另核，MangaGamer全部历史publisher署名及既有内容身份保留。
- 本轮读取来源：[1](https://mangagamer.wordpress.com/2011/08/30/announcing-go-go-nippon/)；[2](https://store.steampowered.com/app/251870/)。
- 应改文件：独立JSON本项、credits.json、entity-migration-review.json、目录／CSV、overdrive.html；仅g647专题从待核改为原作制作，原位置main不变。

### T7：g163

- 定位：`entity-nitroplus_brand`／`g163`。
- 原作品角色：originalPublishingBrand；仅追加`productionBrand`。
- 证据、缺口和范围：官方英文站明确Nitroplus制作室出品，日文原作页列脚本、原画、音乐，授权商店亦将Creator与JAST USA发行分别列出。只给同名品牌增加制作品牌；不由品牌或个人职员署名上推Nitroplus公司，不推定BD／Android移植开发，也不新增STOVE发行。
- 本轮读取来源：[1](https://songofsaya.com/)；[2](https://www.nitroplus.co.jp/game/06-song-of-saya/saya.php)；[3](https://store.onstove.com/en/games/1248/)。
- 应改文件：独立JSON本项、credits.json、目录／CSV、entities.html和nitroplus.html；公司专题分组仍为职责待核，卡片列出已确认的品牌制作与范围。

### T8：g614

- 定位：`entity-nitroplus_brand`／`g614`。
- 原作品角色：originalPublishingBrand；仅追加`productionBrand`。
- 证据、缺口和范围：Steam开发者字段明确Nitroplus、发行另列JAST，原作官方2013访谈讨论企划、开发与美术过程。仅追加同名品牌制作职责；公司专题仍待核，不用2024现行Nitro Origin名称倒替2013原作，也不追加JAST开发或本地化职责。
- 本轮读取来源：[1](https://store.steampowered.com/app/1293820/)；[2](https://www.nitroplus.co.jp/game/totono/interview/01.php)；[3](https://www.nitroplus.co.jp/game/totono/)。
- 应改文件：独立JSON本项、credits.json、目录／CSV、entities.html和nitroplus.html；公司专题分组仍为职责待核，卡片列出已确认的品牌制作与范围。

T1只确认公司类型，官网列出的2015中国公司、2016日本起业与成员2002年活动不合并成一个创立日期。T4的现行公司概要和2012发行公告相互对应，但不将Square、Enix、Square Enix Holdings或另存的日文署名合并。T5的综合业务介绍不支持把Team Salvato开发作品都登记为Serenity Forge开发。

T6的2011年8月30日官方公告明确由OVERDRIVE开发，Steam另列MangaGamer为发行；只审核原作职责，不给2015／2016扩充新增内容层职员。T7日文官方原作页有2003年首发日期和脚本／原画／音乐名单，英文官方站明确制作室出品；STOVE具名Creator作补充，页面自带自动翻译提示，正文涉及引擎和Steam版的通用描述不用于订正任何内容版本。Steam《沙耶之歌》本轮地区不可用，未将其声称为已读取证据，也未新增STOVE发行。T8通过Steam明确的developer字段与2013官方原作访谈交叉核对；不以现行Nitro Origin页脚替换历史制作主体。

T7、T8只确认Nitroplus品牌制作，不把同名制作署名扩展成公司层断言。没有给JAST追加开发或重写发行，也未从个人脚本、美术推断整个公司独立完成所有工种。

## 需要补充来源与暂不宜判断

| 项目 | 分类 | 缺口与最小方案 |
| --- | --- | --- |
| D1 `entity-name-b01843ba1268` | 需要补充来源 | Team Salvato开发署名与Dan Salvato LLC版权并列不能直接证明两者为同一法人；about页面本轮未成功读取，保留身份待核。 |
| D2 `entity-name-2ddaddfb96a5` | 需要补充来源 | DMM GAMES既有文字兼有平台、品牌和发行名义。未在本批取得各时期具名发行与运营范围的完整证据，不把EXNOA直接作别名替换。 |
| D3 `entity-name-77c5d6e9dcc8` | 暂不宜判断 | TYPE-MOON历史同人社团、商业品牌和Notes法人层次需分时期证据。官网名称与一般次级介绍不足以给现有跨期署名选定单一身份，本批不改。 |
| D4 `entity-nitroplus` | 需要补充来源 | 本批T7、T8确认品牌制作，不把公司与品牌并成同一对象。公司专题具体职责需继续核对公司层证据。 |

D1的[官方商品版权页](https://ddlc.plus/merch)检索可见Dan Salvato LLC及Serenity Forge LLC，并非Team Salvato法人名的充分证明；Team Salvato about请求未成功，未据此修改。D2的[官方合作方2022公告](https://www.koeitecmo.co.jp/news/news_20221101.pdf)可检索文本说明EXNOA运营DMM GAMES平台，但本轮未用它核定发行名义的全时期身份。D3仅浏览[TYPE-MOON官网](https://typemoon.com/)及相关检索线索，未取得足以覆盖旧同人／商业时期的独立证据。D4继续保留公司专题待核，不以品牌订正代替。

## 最小变更与保护范围

- 新输入：`data/entity-third-review-20261022.json`及本文件。生成器仅增加第三批读取入口，沿用旧值检查与品牌／公司分离规则。
- 仅5个既有实体的类型、核对状态、来源、说明变化。稳定ID、名称、别名、日期、relations、dossiers均不变。
- 旧4750条credit逐项不变，追加3条work层记录；2234条专题引用只改变OVERDRIVE／g647的一条，Nitroplus公司g163、g614继续pendingRole。
- 四份核心JSON、作品／内容／发行ID、原位置、两个迁移基线、前两批证据逐字保留。不增加新作品、新版本、普通移植或平台记录。
- 前两批测试仍精确比较各自应用前后快照；本批回归精确比较当前数据与PR #51快照，验证前批事实没有被覆盖。

| 指标 | 本批前 | 本批后 |
| --- | ---: | ---: |
| 实体 | 326 | 326 |
| 参与记录 | 4750 | 4753 |
| 专题引用 | 2234 | 2234 |
| 待核身份 | 192 | 187 |
| 职责待核专题引用 | 614 | 613 |
| 主库作品／内容／平台发行 | 1274／1487／2487 | 1274／1487／2487 |

实体与数据库校验通过；Python回归30项、Node回归206项全部通过。三个生成器的 `--check` 与 `git diff --check` 均通过；两个CSV已重新生成。没有进行真实浏览器画面验收，使用数据库、HTML卡片、过滤行为及生成器一致性检查。
