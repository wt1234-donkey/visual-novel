# A—Z 创作登记 D1：D3 Publisher—dB-SOFT（2026-10-23）

D 字母依左侧英文排序已核 4／10，A—Z 累计 64／70；下一家 Digital Leisure。已核进度不表示历史发行或专题关联已核定为创作。

| 主体 | 分类及证据缺口 | 最小修正 |
| --- | --- | --- |
| D3 Publisher | [公司官网](https://www.d3p.co.jp/company/)明确株式会社ディースリー・パブリッシャー；[官方2007年产品目录](https://www.d3p.co.jp/cs/?pg=2&pl=2)列PS2《俺の下でAGAKE》并说明从PC作品改编。PS2版本开发团队及改编内容需原始片尾、手册和包装；PC原版的制作与此发行法人分开。 | 独立订正`entity-name-96d2374d7b76`公司身份；沿用该作品PS2版发行记录，不增加原作制作或开发。 |
| D4 Enterprise | [公司概要](https://d4e.co.jp/company)、[业务说明](https://d4e.co.jp/business)及[沿革](https://d4e.co.jp/history)支持既有公司身份，并说明Project EGG的授权复刻与配信。`g812`、`g813`及`jhv-desert`后发版的实际移植、原版制作和当时权利方仍须逐版确认。 | 沿用公司身份及三部作品既有发行；不把2004年后复刻业务倒填历史原作开发。 |
| Data East | 现有[国立国会图书馆主体记录](https://id.ndl.go.jp/auth/ndlna/033640244)、[任天堂再发行资料](https://www.nintendo.co.jp/wii/vc/vc_jsk/vc_jsk_01.html)及[《恸哭》后发权利方页面](https://el-dia.net/doukoku/)可分别支持身份、个别发行及后版权归属，但不能统一证明所有原版开发。23部既有发行/关联的版本与委托团队待逐作包装、片尾、同期广告；`g1159`专题职责继续待核。 | 保留既有公司、23部其他参与和1条待核；不批量增加开发，也不合并后发权利方。 |
| dB-SOFT（デービーソフト） | [Project EGG参与企业沿革](https://www.amusement-center.com/project/egg/participants/)记1980年Computer Land北海道、1984年更名；[既有专题来源](https://www.gamepres.org/pc88/library/dbsoft.html)列历史作品。`db-soft-south-pacific`、`db-soft-don-juan`、`g747`三条专题缺逐版原始制作署名；五部发行记录不能直接推开发。 | 保留公司身份、Macadamia品牌关系和五部发行；三条职责仍待核。 |

独立审核JSON只应用D3 Publisher一项既有身份订正，`creditAdditions`为空。`games.json`、`company-coverage.json`、原始署名、既有关系和迁移基线不改；下一轮从 Digital Leisure 开始。

发布前全量校验发现主分支`konami.html`含无效UTF-8及重复乱码段落。该页由现有`games.json`和专题配置重新生成，未修改作品事实或迁移基线；生成器`--check`及页面测试验证修复。
