// Presentation only: mutable catalogue/session state stays with the controller.
export function createDiscoveryViews(read) {
  function safe(x) {
    return String(x ?? "").replace(
      /[&<>"']/g,
      (c) =>
        ({
          "&": "&amp;",
          "<": "&lt;",
          ">": "&gt;",
          '"': "&quot;",
          "'": "&#39;",
        })[c],
    );
  }

  function textLink(url, text) {
    try {
      const u = new URL(url, location.href);
      if (!["http:", "https:"].includes(u.protocol)) return safe(text);
      return `<a href="${safe(u.href)}" target="_blank" rel="noopener noreferrer">${safe(text)} ↗</a>`;
    } catch {
      return safe(text);
    }
  }

  function tags(values) {
    return (
      '<div class="sa-tags">' +
      values
        .map((v) => '<span class="sa-tag">' + safe(v) + "</span>")
        .join("") +
      "</div>"
    );
  }

  function status(text, kind = "") {
    return '<span class="sa-status ' + kind + '">' + safe(text) + "</span>";
  }

  function button(text, attrs = "", cls = "") {
    return (
      '<button type="button" class="sa-button ' +
      cls +
      '" ' +
      attrs +
      ">" +
      text +
      "</button>"
    );
  }

  function option(value, text, selected) {
    return (
      '<option value="' +
      safe(value) +
      '" ' +
      (selected === value ? "selected" : "") +
      ">" +
      safe(text) +
      "</option>"
    );
  }

  function heading(en, title, desc) {
    return `<div class="sa-eyebrow">${en}</div><h1>${title}</h1><p class="sa-lead">${desc}</p>`;
  }

  function search(value, placeholder, kind) {
    return `<div class="sa-search"><span class="sa-search-icon" aria-hidden="true">⌕</span><input type="search" data-search="${kind}" aria-label="${safe(placeholder)}" placeholder="${safe(placeholder)}" value="${safe(value)}"></div>`;
  }

  function book(w) {
    const { atlas } = read();
    const index = atlas.data.works.indexOf(w) % 4;
    return `<div class="sa-book b${index}"><span class="sa-book-word">${safe(atlas.editorial.works[w.id]?.cover || w.originalTitle)}</span><span class="sa-book-no">${w.firstYear}</span></div>`;
  }

  function brandLabel(w) {
    const { atlas, productionCredits } = read();
    const own = productionCredits(atlas, w.id);
    const names = [
      ...new Set(
        own.map((c) => atlas.entities.get(c.entityId)?.name).filter(Boolean),
      ),
    ];
    return names.length ? names.slice(0, 2).join(" / ") : "创作关系待核";
  }

  function cards(list) {
    const { atlas, titleOf } = read();
    return (
      '<div class="sa-work-grid">' +
      (list.length
        ? list
            .map(
              (w) =>
                `<button type="button" class="sa-work" data-work="${safe(w.id)}" aria-label="查看${safe(titleOf(w))}档案">${book(w)}<div class="sa-work-body"><h3>${safe(titleOf(w))}</h3><p class="sa-work-year">${safe(brandLabel(w))} · ${w.firstYear}</p>${tags([...(atlas.editorial.works[w.id]?.theme || []).slice(0, 1), ...(atlas.editorial.works[w.id]?.style || []).slice(0, 1), atlas.editorial.works[w.id]?.position || w.category])}<p class="sa-desc">${safe(w.synopsis)}</p></div><div class="sa-work-foot"><span>档案 · 创作 · 内容版本</span><span aria-hidden="true">↗</span></div></button>`,
            )
            .join("")
        : '<div class="sa-empty"><h3>没有符合条件的作品</h3><p>试试清除筛选或更换关键词。待编目不代表没有相关内容。</p></div>') +
      "</div>"
    );
  }

  function pagination(total, page, kind, size = read().PAGE_SIZE) {
    const max = Math.max(1, Math.ceil(total / size));
    return `<div class="sa-pagination">${button("← 上一页", `data-pager="${kind}" data-step="-1" ${page <= 1 ? "disabled" : ""}`)}<span class="sa-small sa-muted" aria-live="polite">第 ${page} / ${max} 页 · 共 ${total} 项</span>${button("下一页 →", `data-pager="${kind}" data-step="1" ${page >= max ? "disabled" : ""}`)}</div>`;
  }

  function detailTabs() {
    const { state } = read();
    return (
      '<nav class="sa-tabs" aria-label="作品档案栏目">' +
      [
        ["profile", "作品档案"],
        ["versions", "内容与版本"],
        ["sources", "证据与来源"],
      ]
        .map(
          ([id, title]) =>
            `<button type="button" data-detail-tab="${id}" aria-pressed="${state.detailTab === id}">${title}</button>`,
        )
        .join("") +
      "</nav>"
    );
  }

  function narrativeEvidence(w) {
    const { atlas, narrativeState } = read();

    const meta = atlas.editorial.works[w.id];
    if (!meta) return "";
    const labels = {
      position: "叙事定位",
      style: "剧情风格",
      theme: "故事题材",
      structure: "叙事结构",
    };
    const details = Object.entries(labels)
      .map(([field, label]) => {
        const ev = meta.fieldEvidence?.[field];
        if (!ev) return "";
        return `<details><summary>${label}的编目依据</summary><p class="sa-small">${safe(ev.basis || "")}</p>${ev.evidenceText ? `<p class="sa-small sa-muted">资料摘记（${ev.evidenceStatus === "primarySourceChecked" ? "本轮原始资料核对" : ev.evidenceStatus === "secondarySourceChecked" ? "本轮二手研究核对" : "继承档案及条目限定核对"}）：${safe(ev.evidenceText)}</p>` : ""}<div class="sa-legend">${(ev.sources || []).map((url) => textLink(url, "字段依据")).join(" · ")}</div></details>`;
      })
      .join("");
    const questions = (meta.openQuestions || [])
      .map(
        (q) =>
          `<li>${safe(typeof q === "string" ? q : q.question || q.reason || JSON.stringify(q))}</li>`,
      )
      .join("");
    return `<section class="sa-panel"><div class="sa-heading"><h3>叙事编目依据</h3>${status({ complete: "四项已编目", partial: "部分字段待补证", missing: "待编目" }[narrativeState(atlas, w)], narrativeState(atlas, w) === "complete" ? "" : "pending")}</div><p class="sa-small sa-muted">结构标签记录目前有据的组织方式，不表示全部路线、结局数量及所有版本均已考据完成。具体演出或玩法不自动等于故事拓扑。</p>${details}${questions ? `<details open><summary>仍需补充的资料</summary><ul class="sa-small">${questions}</ul></details>` : ""}</section>`;
  }

  function manualCreditHTML(w, role) {
    const { manualCreatorNames } = read();
    return manualCreatorNames(w, role)
      .map(
        (name) =>
          `<article class="sa-credit"><button type="button" class="sa-credit-name sa-link-button" data-creator-name="${safe(name)}">${safe(name)}</button><p class="sa-credit-role">${{ writer: "剧作", artist: "美术", musician: "音乐" }[role]}</p>${status("手动添加")}</article>`,
      )
      .join("");
  }

  function creatorSummary(w) {
    const {
      atlas,
      creatorCredits,
      manualCreatorNames,
      resourceNotice,
      resources,
    } = read();
    if (resources.get("creators")?.status !== "ready")
      return resourceNotice("creators", "个人署名");
    return `<dl class="sa-specs">${Object.entries({
      writer: "剧作",
      artist: "美术",
      musician: "音乐",
    })
      .map(
        ([role, label]) =>
          `<div><dt>${label}</dt><dd>${
            creatorCredits(atlas, w.id, role)
              .map(
                (c) =>
                  `<button type="button" class="sa-link-button" data-person="${safe(c.personId)}">${safe(atlas.people.get(c.personId).name)}</button>`,
              )
              .concat(
                manualCreatorNames(w, role).map(
                  (name) =>
                    `<button type="button" class="sa-link-button" data-creator-name="${safe(name)}">${safe(name)}</button> ${status("手动添加")}`,
                ),
              )
              .join(" / ") || "尚未添加"
          }</dd></div>`,
      )
      .join("")}</dl>`;
  }

  function profile(w) {
    const { atlas, fields, metadataValues, resourceNotice } = read();
    const meta = atlas.editorial.works[w.id];
    return `<section class="sa-panel"><h3>故事概览</h3><p class="sa-lead">${safe(w.synopsis)}</p><p class="sa-genres">原档案类型：${safe(w.category)} · ${safe(w.subcategory)}<br>题材原文：${safe(w.genre)}</p><dl class="sa-specs">${fields.map(([k, l]) => `<div><dt>${l}</dt><dd>${safe(metadataValues(atlas, w, k).join(" / ") || "待编目")}</dd></div>`).join("")}</dl><p class="sa-small sa-muted">${meta ? "叙事标签：编辑归纳 · " + safe(meta.basis) : "尚未统一编目，保留原档案题材；不能把未知解释为没有此类叙事内容。"}</p>${meta ? '<div class="sa-legend">' + (meta.sources || []).map((s) => textLink(s, "编目依据")).join(" · ") + "</div>" : ""}<details><summary>玩法依据 · ${safe(w.interactionBasis)}</summary><p class="sa-small sa-muted">${safe(w.interactionNote)}</p><div class="sa-legend">${(w.interactionSources || []).map((s) => textLink(s, "玩法来源")).join(" ")}</div></details></section>${resourceNotice("editorial:" + w.id, "编目依据")}${narrativeEvidence(w)}<section class="sa-panel"><div class="sa-heading"><h3>主要角色</h3>${w.charactersSource ? textLink(w.charactersSource, "角色依据") : status("沿用既有角色档案")}</div><div class="sa-lineup">${w.characters.map((n) => `<span class="sa-character"><span class="sa-dot">${safe(n.slice(0, 1))}</span>${safe(n)}</span>`).join("")}</div>${w.charactersNote ? `<p class="sa-lead sa-small">${safe(w.charactersNote)}</p>` : ""}</section><section class="sa-panel"><div class="sa-heading"><h3>剧作 · 美术 · 音乐</h3><div class="sa-lineup">${button("添加剧作／美术／音乐", `data-add-creators="${w.id}"`)}${button("查看创作关系", `data-open-credits="${w.id}"`)}</div></div>${creatorSummary(w)}</section>${resourceNotice("notes:" + w.id, "附注")}${(atlas.notes.works[w.id] || []).map((n) => `<section class="sa-panel"><h3>${safe(n.title)}</h3><p class="sa-lead">${safe(n.text)}</p><div class="sa-legend">${textLink(n.source, "补充依据")}${n.dossierId ? textLink(n.dossierId + ".html#" + n.anchor, "相关专题") : ""}</div></section>`).join("")}${w.notes ? `<p class="sa-lead sa-small">原档案备注：${safe(w.notes)}</p>` : ""}`;
  }

  function releaseRow(r) {
    const { atlas } = read();
    const name =
      atlas.catalogue.model.displayNames?.[r.publisher] || r.publisher;
    return `<div class="sa-release"><h4>${r.year} · ${safe(r.platform)} · ${safe(r.kind)}</h4><p>发行／出版：${safe(name)}${r.voice === "无" ? " · 无角色配音" : ""}</p>${name !== r.publisher ? `<p class="sa-muted">署名原文：${safe(r.publisher)}</p>` : ""}<p>${safe(r.differences)}</p><p class="sa-muted">${safe(r.contentNote)}</p>${textLink(r.source, "发行来源")}</div>`;
  }

  function versions(w) {
    const { atlas } = read();
    const contents = [...(atlas.contents.get(w.id) || [])].sort(
        (a, b) => a.firstYear - b.firstYear,
      ),
      releases = [...(atlas.releases.get(w.id) || [])].sort(
        (a, b) => a.year - b.year,
      ),
      pending = releases.filter((r) => !r.contentVersionId);
    const byContent = new Map(contents.map((c) => [c.id, c]));
    return `<div class="sa-heading"><h3>内容版本与平台发行</h3>${status(`${contents.length} 个内容版本 · ${releases.length} 条发行`)}</div><p class="sa-small sa-muted">内容版本按内容身份区分；平台发行单独保存。内容关系未核实，不等于没有新增内容或与原版相同。</p><div class="sa-table-wrap sa-versions"><table><thead><tr><th>发行</th><th>平台 / 版本</th><th>已关联内容</th><th>关系</th></tr></thead><tbody>${releases.map((r) => `<tr><td>${r.year}</td><td>${safe(r.platform)}<br><span class="sa-small sa-muted">${safe(r.kind)}</span></td><td>${safe(byContent.get(r.contentVersionId)?.label || "待核实")}</td><td>${status({ original: "原作", added: "新增内容", same: "同内容", unverified: "关系待核" }[r.contentRelation], r.contentVersionId ? "" : "pending")}</td></tr>`).join("")}</tbody></table></div><div class="sa-versions">${contents
      .map(
        (c) =>
          `<section class="sa-version"><h3>${c.firstYear} · ${safe(c.label)}</h3><p class="sa-small sa-muted">${c.basis === "original" ? "原作／首批内容" : "已明确新增内容"} · ${safe(c.id)}</p><p>${safe(c.evidence)}</p>${c.comparedTo ? `<p class="sa-muted">比较对象：${safe(byContent.get(c.comparedTo)?.label || c.comparedTo)}</p>` : ""}${c.addedContent.map((a) => `<p>新增：${safe(a.description)} ${textLink(a.source, "增量证据")}</p>`).join("")}<p>${textLink(c.source, "内容依据")}</p><details><summary>查看对应的 ${releases.filter((r) => r.contentVersionId === c.id).length} 条平台发行</summary>${releases
            .filter((r) => r.contentVersionId === c.id)
            .map(releaseRow)
            .join("")}</details></section>`,
      )
      .join(
        "",
      )}${pending.length ? `<details class="sa-panel"><summary>${pending.length} 条历史发行的内容关系待核实（不计新增内容版本）</summary>${pending.map(releaseRow).join("")}</details>` : ""}</div>${w.id === "g039" ? `<section class="sa-panel" style="margin-top:18px"><h3>关键剧情的逐版收录核对</h3><p class="sa-lead">《不倶戴天の君へ》及 Mini After Story 的具体产品收录与获取形态仍待逐项补证。暂不据合集名称判断“最完整版本”。</p><p class="sa-small">${textLink("https://aquaplus.jp/wa2/product.html", "PS3 官方追加说明")}</p></section>` : ""}${(w.editionCredits || []).map((c) => `<p class="sa-details">历史发行补充：${c.year} · ${safe(c.platform)} · ${safe(c.publisher)}。${safe(c.reason)} ${textLink(c.source, "依据")}</p>`).join("")}`;
  }

  function organizationCredits(w) {
    const { atlas, sourceStatus } = read();
    const rows = atlas.organization.get(w.id) || [];
    return rows.length
      ? rows
          .map((c) => {
            const e = atlas.entities.get(c.entityId);
            const target =
              c.targetType === "release"
                ? (atlas.releases.get(w.id) || []).find(
                    (r) => r.id === c.targetId,
                  )
                : null;
            return `<article class="sa-list-row"><div><h4>${safe(e?.name || c.entityId)} · ${safe(atlas.catalogue.model.roleLabels[c.role] || c.role)}</h4><p class="sa-small sa-muted">${c.targetType === "work" ? "原作／作品" : c.targetType === "content" ? "对应内容版本" : target ? `${target.year} · ${target.platform} · ${target.kind}` : "对应平台发行"} · ${sourceStatus(c.status)}</p>${c.note ? `<p class="sa-small sa-muted">${safe(c.note)}</p>` : ""}</div>${textLink(c.source, "依据")}</article>`;
          })
          .join("")
      : '<p class="sa-lead">参与职责尚待核实。</p>';
  }

  function sources(w) {
    const { atlas, resourceNotice, resources } = read();
    if (resources.get("organizations")?.status !== "ready")
      return resourceNotice("organizations", "机构署名");
    return `<section class="sa-panel"><h3>档案来源</h3><div class="sa-list-row"><div><h4>简介与历史资料</h4><p class="sa-small sa-muted">沿用既有作品档案与证据。</p></div>${textLink(w.source, "作品来源")}</div><div class="sa-list-row"><div><h4>叙事标签</h4><p class="sa-small sa-muted">${safe(atlas.editorial.works[w.id]?.basis || "待编目；未根据玩法或厂商自动推断。")}</p></div>${status(atlas.editorial.works[w.id] ? "编辑归纳" : "待编目", "pending")}</div></section><section class="sa-panel"><h3>制作、品牌与发行参与</h3>${organizationCredits(w)}</section><div class="sa-lineup" style="margin-top:18px">${button("查看个人创作署名", `data-open-credits="${w.id}"`)}${textLink("data/discovery-model.md", "编目与证据规则")}</div>`;
  }

  function creditWorkPicker() {
    const { state } = read();
    return (
      search(state.creditQuery, "输入作品名筛选署名档案…", "credit-work") +
      `<label class="sa-label">选择作品 <select data-credit-work aria-label="选择作品">${creditWorkOptions()}</select></label>`
    );
  }

  function creditWorkOptions() {
    const { atlas, normalize, state, titleOf } = read();
    const q = normalize(state.creditQuery);
    const selected = atlas.works.get(state.creditWork);
    let list = atlas.data.works.filter(
      (w) =>
        !q ||
        normalize(
          [titleOf(w), w.originalTitle, ...(w.titleAliases || [])].join(" "),
        ).includes(q),
    );
    if (selected && !list.includes(selected)) list.unshift(selected);
    return list
      .map((w) =>
        option(w.id, `${titleOf(w)} · ${w.firstYear}`, state.creditWork),
      )
      .join("");
  }

  function creditEvidence() {
    const { atlas, creditScope, state, titleOf } = read();
    const c = atlas.creators.credits.find((c) => c.id === state.evidence);
    if (!c) return "";
    return `<section class="sa-evidence" aria-live="polite"><div class="sa-heading"><h3>署名证据 · ${safe(atlas.people.get(c.personId).name)}</h3><button type="button" class="sa-link-button" data-close-evidence>收起</button></div><p>作品：${safe(titleOf(atlas.works.get(c.workId)))} / 职责：${safe(c.label)}</p><p>适用范围：${safe(creditScope(atlas, c))}</p><p>${safe(c.note)}</p><p>${textLink(c.source, "打开署名来源")}</p></section>`;
  }

  function creatorCards() {
    const { creatorRows, state } = read();
    const rows = creatorRows();
    state.creatorPage = Math.min(
      state.creatorPage,
      Math.max(1, Math.ceil(rows.length / 12)),
    );
    return `<div class="sa-count" aria-live="polite">${rows.length} 个主体 / 合作线索；作品数仅按直接制作或个人署名去重</div><div class="sa-entity-grid">${
      rows
        .slice((state.creatorPage - 1) * 12, state.creatorPage * 12)
        .map(
          (e) =>
            `<button type="button" class="sa-entity" data-select-creator="${e.kind}:${e.id}"><span class="sa-entity-avatar">${safe(e.mark || e.name.slice(0, 1))}</span><span><span class="sa-entity-name">${safe(e.name)}</span><span class="sa-entity-meta">${safe(e.label)}</span><span class="sa-entity-meta">${e.workIds.size} 部关联作品 →</span><span class="sa-entity-desc">${safe(e.desc)}</span></span></button>`,
        )
        .join("") || '<div class="sa-empty">没有匹配的创作者或品牌</div>'
    }</div>${pagination(rows.length, state.creatorPage, "creators")}`;
  }

  function selectedCreator() {
    const { atlas, creatorWorkIds, state } = read();
    if (!state.selected) return "";
    const [kind, id] = state.selected.split(":");
    const record =
      kind === "person"
        ? atlas.people.get(id)
        : kind === "entity"
          ? atlas.entities.get(id)
          : atlas.creators.collaborations.find((c) => c.id === id);
    if (!record) return "";
    const role =
      kind === "person" &&
      ["writer", "artist", "musician"].includes(state.creatorType)
        ? state.creatorType
        : "";
    const ids = creatorWorkIds(atlas, kind, id, role);
    const list = atlas.data.works
      .filter((w) => ids.has(w.id))
      .sort((a, b) => a.firstYear - b.firstYear);
    const max = Math.max(1, Math.ceil(list.length / 12));
    state.selectedPage = Math.min(state.selectedPage || 1, max);
    return `<section class="sa-entity-detail"><div class="sa-heading"><h2>${safe(record.name)}</h2><button type="button" class="sa-link-button" data-close-creator>收起作品</button></div><p>${safe(kind === "cooperation" ? record.note : kind === "person" ? "按已登记的个人署名关联；具体分工和适用版次见作品创作关系。" : "仅采用原作制作、制作品牌、开发与联合制作的作品／内容层直接记录；发行、版权与母公司关系不自动传递。")}</p>${!list.length ? "<p>暂无已核的直接制作关系。可以在历史专题查看发行与其他关联。</p>" : ""}${kind === "entity" ? `<p>${textLink("entities.html#" + record.id, "主体与证据档案")}</p>` : ""}${kind === "cooperation" ? `<p>${record.sources.map((s) => textLink(s, "共同署名来源")).join(" · ")}</p>` : ""}${cards(list.slice((state.selectedPage - 1) * 12, state.selectedPage * 12))}${list.length ? pagination(list.length, state.selectedPage, "selected") : ""}</section>`;
  }

  function researchTabs() {
    const { state } = read();
    return (
      '<nav class="sa-tabs" aria-label="历史考据栏目">' +
      [
        ["topics", "厂商专题"],
        ["organizations", "组织与沿革"],
        ["releases", "发行历史"],
        ["evidence", "考据与证据"],
      ]
        .map(
          ([id, title]) =>
            `<button type="button" data-research-tab="${id}" aria-pressed="${state.researchTab === id}">${title}</button>`,
        )
        .join("") +
      "</nav>"
    );
  }

  function releaseResults() {
    const { atlas, normalize, state, titleOf } = read();
    const q = normalize(state.releaseQ);
    const rows = atlas.data.platformReleases.filter(
      (r) =>
        !q ||
        normalize(
          [
            titleOf(atlas.works.get(r.workId)),
            atlas.works.get(r.workId).originalTitle,
            r.year,
            r.platform,
            r.publisher,
            r.kind,
            r.differences,
          ].join(" "),
        ).includes(q),
    );
    state.releasePage = Math.min(
      state.releasePage,
      Math.max(1, Math.ceil(rows.length / 15)),
    );
    return `<p class="sa-count" aria-live="polite">${rows.length} 条平台发行；保留原始署名与内容关系</p><div class="sa-table-wrap"><table><thead><tr><th>作品 / 年份</th><th>平台 / 发行署名</th><th>内容关系 / 依据</th></tr></thead><tbody>${
      rows
        .slice((state.releasePage - 1) * 15, state.releasePage * 15)
        .map(
          (r) =>
            `<tr><td><button type="button" class="sa-link-button" data-version-work="${r.workId}">${safe(titleOf(atlas.works.get(r.workId)))}</button><br>${r.year}</td><td>${safe(r.platform)}<br><span class="sa-muted">${safe(r.publisher)} · ${safe(r.kind)}</span></td><td>${status(r.contentVersionId ? "已关联内容" : "内容关系待核", r.contentVersionId ? "" : "pending")}<br>${textLink(r.source, "发行来源")}</td></tr>`,
        )
        .join("") || '<tr><td colspan="3">没有匹配的发行记录</td></tr>'
    }</tbody></table></div>${pagination(rows.length, state.releasePage, "releases", 15)}`;
  }

  function researchBody() {
    const { evidenceResults, resourceNotice, resources, state } = read();
    if (
      state.researchTab === "releases" &&
      resources.get("releases")?.status !== "ready"
    )
      return resourceNotice("releases", "发行历史");
    if (state.researchTab === "evidence") {
      const keys = ["all-editorial", "organizations", "creators"];
      if (keys.some((k) => resources.get(k)?.status !== "ready"))
        return keys.map((k) => resourceNotice(k, "证据资料")).join("");
    }
    if (state.researchTab === "topics")
      return (
        search(state.topicQ, "检索现有厂商专题…", "topics") +
        '<div id="sa-topics"></div>'
      );
    if (state.researchTab === "organizations")
      return `<section class="sa-panel"><div class="sa-heading"><h3>组织身份与历史关系</h3>${textLink("organizations.html", "进入组织与沿革")}</div><p class="sa-lead">公司、品牌、团队与个人各有独立身份。运营、名称变化、品牌家族及创作合作分别记录，起止未核的关系不推定为始终有效。</p><div class="sa-research-links">${textLink("organizations.html", "组织与沿革档案")}${textLink("entities.html", "主体身份与参与证据")}${textLink("relationships-preview.html", "关系图与历史线索")}${textLink("classification.html", "作品收录位置审核")}</div></section><section class="sa-panel"><h3>旧专题与历史记录继续保留</h3><p class="sa-lead">专题最早作品年份不等于组织成立时间；发行、授权与版权署名也不自动代表原作开发。</p><p style="margin-top:12px">${textLink("data/entity-model.md", "实体与参与模型")}${textLink("data/content-model.md", "内容版本规则")}</p></section>`;
    if (state.researchTab === "releases")
      return `<div class="sa-lineup">${button("进入高级发行检索", "data-open-advanced")}${textLink("data/platform-releases.csv", "平台发行 CSV")}${textLink("data/content-versions.csv", "内容版本 CSV")}</div>${search(state.releaseQ, "检索作品、年份、平台、发行方或版本差异…", "releases")}<div id="sa-release-results">${releaseResults()}</div>`;
    return `<div class="sa-lineup"><label class="sa-label">证据状态 <select data-status>${[
      ["all", "全部"],
      ["reviewed", "来源已核"],
      ["inherited", "沿用既有证据"],
      ["pending", "待核实"],
      ["editorial", "编辑归纳"],
    ]
      .map(([v, l]) => option(v, l, state.evidenceStatus))
      .join(
        "",
      )}</select></label>${textLink("data/discovery-model.md", "查看证据规则")}</div>${search(state.evidenceQ, "搜索作品、参与主体或待核问题…", "evidence")}<div id="sa-evidence-results">${evidenceResults()}</div>`;
  }
  return {
    safe,
    textLink,
    tags,
    status,
    button,
    option,
    heading,
    search,
    book,
    brandLabel,
    cards,
    pagination,
    detailTabs,
    narrativeEvidence,
    manualCreditHTML,
    creatorSummary,
    profile,
    releaseRow,
    versions,
    organizationCredits,
    sources,
    creditWorkPicker,
    creditWorkOptions,
    creditEvidence,
    creatorCards,
    selectedCreator,
    researchTabs,
    releaseResults,
    researchBody,
  };
}
