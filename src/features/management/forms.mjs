// Presentation only: mutable catalogue/session state stays with the controller.
export function createManagementForms(read) {
  function yearLabel(w) {
    return w.firstYear === null
      ? "年份未知"
      : String(w.firstYear) +
          ({ unverified: "（待核）", planned: "（计划）" }[w.yearStatus] || "");
  }

  function input(name, label, value = "", hint = "", type = "text") {
    const { escape } = read();
    return `<label class="field"><span>${label}</span><input name="${name}" type="${type}" value="${escape(value)}">${hint ? `<small>${hint}</small>` : ""}</label>`;
  }

  function area(name, label, value = "", hint = "", rows = 3) {
    const { escape } = read();
    return `<label class="field"><span>${label}</span><textarea name="${name}" rows="${rows}">${escape(value)}</textarea>${hint ? `<small>${hint}</small>` : ""}</label>`;
  }

  function options(rows, value) {
    const { escape } = read();
    return rows
      .map(
        ([id, label]) =>
          `<option value="${escape(id)}" ${id === value ? "selected" : ""}>${escape(label)}</option>`,
      )
      .join("");
  }

  function select(name, label, rows, value = "") {
    return `<label class="field"><span>${label}</span><select name="${name}">${options(rows, value)}</select></label>`;
  }

  function link(url, label) {
    const { escape, validURL } = read();
    return validURL(url)
      ? `<a href="${escape(url)}" target="_blank" rel="noopener noreferrer">${escape(label)} ↗</a>`
      : escape(label);
  }

  function profileFields(w, { source = false } = {}) {
    const { displayTitle, escape } = read();

    const fields = [
      ["作品名称", source ? w.title : displayTitle(w)],
      ["中文检索名", w.chineseTitle || "同作品名称"],
      ["原名", w.originalTitle],
      ["首发年份", yearLabel(w)],
      ["分类", w.category + " / " + w.subcategory],
      ["具体类型／题材", w.genre],
      ["主要角色", (w.characters || []).join("、")],
      ["剧情简介", w.synopsis],
      ["互动方式", (w.interactionModes || []).join("、")],
      ["玩法依据", w.interactionNote],
      ["已有备注", w.notes || "暂无"],
    ];
    for (const [key, label] of [
      ["writerNames", "剧作（手动添加）"],
      ["artistNames", "美术（手动添加）"],
      ["musicianNames", "音乐（手动添加）"],
    ])
      if (w[key]?.length) fields.push([label, w[key].join("、")]);
    return `<dl>${fields.map(([label, value]) => `<dt>${label}</dt><dd>${escape(value)}</dd>`).join("")}<dt>作品资料</dt><dd>${link(w.source, source ? "打开原始来源" : "打开当前资料来源")}</dd></dl>`;
  }

  function profile(w) {
    const { $, data, escape } = read();

    const source = data.games.works.find((row) => row.id === w.id);
    $("#panel").innerHTML =
      `<h3>作品档案</h3><p><a href="index.html?edit=${encodeURIComponent(w.id)}#work/${encodeURIComponent(w.id)}/profile">直接编辑网站作品／回撤最近3次修改 ↗</a></p>${!source ? '<div class="info good">这是尚未提交的新作草稿。<button data-edit-new="' + escape(w.id) + '">修改新作资料</button></div>' : '<div class="info">当前档案显示已发布的有效资料，包含基础库和正式作品更正。原始资料可在下方展开核对。</div>'}<p><a href="field-evidence.html#${encodeURIComponent(w.id)}">管理本作品的字段证据、并存来源和选用理由 ↗</a></p>${
        w.fieldEvidence
          ? `<dl>${Object.entries(w.fieldEvidence)
              .map(
                ([key, a]) =>
                  `<dt>${escape({ title: "名称", firstYear: "年份", group: "厂商", writerNames: "剧作姓名", artistNames: "美术姓名", musicianNames: "音乐姓名" }[key] || key)} · 显式选用</dt><dd>${escape(Array.isArray(a.value) ? a.value.join("、") : a.value)} · ${escape(a.selection.reason)} · ${escape(a.selection.actor)}<br>断言 ${escape(a.id)} · ${escape({ unverified: "待核", supported: "已核对所列来源", disputed: "有争议", manual: "手动添加／未附证据" }[a.status] || a.status)}</dd>`,
              )
              .join("")}</dl>`
          : ""
      }${profileFields(w)}${source ? `<details><summary>查看原始资料</summary><p class="muted">以下为来源记录，保留原始名称、年份及资料依据；当前展示采用上方有效值。</p>${profileFields(source, { source: true })}</details>` : ""}<div class="actions"><button class="primary" data-go="editorial">开始叙事编目</button><button data-go="notes">添加资料订正说明</button></div>`;
  }

  function editorial(w) {
    const { $, FIELDS, data, working } = read();
    const r = working.editorial.works[w.id] || {},
      locked = w.id in data.baseline.works;
    $("#panel").innerHTML =
      `<h3>四项叙事编目</h3><div class="info">每项分别填写理由、摘记和来源。资料不足时留空并写明待核问题；不能由“有选项”推断多路线，也不要把后发版特征倒填原作。${locked ? "<br><b>此作品属于最初八部历史编目基线，当前只读。订正请使用补充说明进入独立审查。</b>" : ""}</div><form id="edit-form"><fieldset ${locked ? "disabled" : ""} style="border:0;padding:0;margin:0">${FIELDS.map(
        ([f, label]) => {
          const e = r.fieldEvidence?.[f] || {};
          return `<fieldset class="field-block"><legend>${label}</legend>${input(f, "编目结论", Array.isArray(r[f]) ? r[f].join("、") : r[f] || "", f === "position" ? "例如：叙事主导／叙事与解谜并重" : "多个标签用顿号或逗号分隔")}${area(f + "-basis", "为什么这样归纳", e.basis || "", "至少8字，明确解释资料与本项结论的关系。", 2)}${area(f + "-excerpt", "支持结论的资料摘记", e.evidenceText || "", "至少5字；简要概述资料明示的内容，注明适用版次。", 2)}${area(f + "-sources", "本项来源 URL", (e.sources || []).join("\n"), "每行一个链接；请填写 HTTPS 链接。", 2)}</fieldset>`;
        },
      ).join(
        "",
      )}${area("basis", "总体归纳依据", r.basis || "", "至少15字；说明资料范围及编辑归纳的边界。")}${area("sources", "总体资料来源", (r.sources || []).join("\n"), "每行一个来源；各字段已有来源会自动汇总。", 2)}${area("questions", "尚待核实的问题", (r.openQuestions || []).join("\n"), "未完成的字段需说明缺少什么证据；每行一项。", 2)}<label class="check"><input name="confirmed" type="checkbox">我已逐项核对本次修改的来源与适用版本</label><div class="actions"><button type="submit" class="primary">将编目加入修改清单</button><span class="muted">此时仅保存草稿，尚未提交数据库。</span></div></fieldset></form>`;
  }

  function creditRows(w) {
    const { ROLES, data, escape, working } = read();
    return (
      working.creators.credits
        .filter((c) => c.workId === w.id)
        .map(
          (c) =>
            `<article class="record"><strong>${escape(working.creators.people.find((p) => p.id === c.personId)?.name || c.personId)}</strong><span class="badge">${escape(ROLES[c.role])}</span><p>${escape(c.label)} · ${escape(c.scopeLabel)}</p><p>${escape(c.note)}</p>${link(c.source, "署名依据")}${!data.creators.credits.some((x) => x.id === c.id) ? ` <button class="remove" data-remove-credit="${escape(c.id)}">撤销本次新增</button>` : ""}</article>`,
        )
        .join("") ||
      '<p class="muted">尚无已登记的个人署名。缺项不等于没有该职责。</p>'
    );
  }

  function credits(w) {
    const { $, ROLES, working } = read();
    $("#panel").innerHTML =
      `<h3>已登记的个人创作关系</h3>${creditRows(w)}<h3 style="margin-top:24px">补充个人署名</h3><div class="info">优先复用已有个人身份。明确区分剧作、美术和音乐；演唱、配音不能直接写成作曲。这里只新增具名署名，已有署名订正请通过补充说明提出。</div><form id="edit-form">${select("person", "选择已有创作者", [["", "新增个人身份"], ...working.creators.people.map((p) => [p.id, p.name + " · " + p.id])])}<div class="form-row">${input("person-id", "新增个人 ID（仅新增时填写）", "", "英文小写、数字和连字符，例如 yamada-taro")}${input("person-name", "新增个人姓名")}</div>${input("person-alias", "其他姓名／检索别名（仅新增时填写）")}${select("role", "职责组", Object.entries(ROLES), "writer")}${input("label", "资料中实际署名", "", "例如：シナリオ／原画／作曲；保留具体职责")}${select(
        "scope",
        "证据适用范围",
        [
          ["documentedWork", "具名作品分工（官方栏目／访谈）"],
          ["release", "库中已有的具体平台发行"],
          ["externalEdition", "库外的后续产品版次"],
        ],
      )}${select("release", "库中发行（范围为具体发行时必选）", [["", "请选择"], ...working.games.platformReleases.filter((r) => r.workId === w.id).map((r) => [r.id, `${r.year} · ${r.platform} · ${r.id}`])])}<div class="form-row">${input("year", "库外版次年份", "", "仅范围为后续产品时填写", "number")}${input("platform", "库外版次平台", "", "仅范围为后续产品时填写")}</div>${input("scope-label", "范围说明", "", "例如：2014 PS Vita 官方产品页署名")}${input("source", "署名来源 URL", "", "官方产品页、片尾署名或当事人访谈", "url")}${area("note", "职责与版次的限定说明", "", "例如：未据此判断各路线分工；不外推其他历史版本。")}${input("credit-id", "本条署名 ID", "", "唯一英文 ID，例如 " + w.id + "-writer-yamada-original")}<label class="check"><input name="confirmed" type="checkbox">我已核实资料明确记载此人承担这项职责</label><div class="actions"><button type="submit" class="primary">将署名加入修改清单</button></div></form>`;
  }

  function versions(w) {
    const { $, escape, working } = read();
    const cs = working.games.contentVersions.filter((c) => c.workId === w.id),
      rs = working.games.platformReleases.filter((r) => r.workId === w.id);
    $("#panel").innerHTML =
      `<h3>内容身份与平台发行</h3><div class="info">${cs.length} 个内容版本，${rs.length} 条平台发行。普通移植、翻译或重发不新建内容版本；未知关系继续保持“待核”。本入口可补充有来源的差异说明，正式新增内容身份仍需单独考据。</div>${cs
        .map(
          (c) =>
            `<details open><summary>${c.firstYear} · ${escape(c.label)} <span class="badge">${c.basis === "original" ? "原作内容" : "已核新增内容"}</span></summary><p>${escape(c.id)}${c.comparedTo ? " · 比较对象 " + escape(c.comparedTo) : ""}</p><p>${escape(c.evidence)}</p>${link(c.source, "内容依据")}${rs
              .filter((r) => r.contentVersionId === c.id)
              .map(release)
              .join("")}</details>`,
        )
        .join("")}${
        rs.filter((r) => !r.contentVersionId).length
          ? "<h3>内容关系待核的历史发行</h3>" +
            rs
              .filter((r) => !r.contentVersionId)
              .map(release)
              .join("")
          : ""
      }<div class="actions"><button data-go="notes" class="primary">记录新发现的版本差异</button></div>`;
  }

  function release(r) {
    const { escape } = read();
    return `<article class="record"><strong>${r.year} · ${escape(r.platform)}</strong><p>${escape(r.publisher)} · ${escape(r.id)}</p><p>${escape(r.differences)}</p><p>${escape(r.contentNote)}</p>${link(r.source, "发行来源")}</article>`;
  }

  function notes(w) {
    const { $, data, escape, working } = read();
    const rows = working.notes.works[w.id] || [];
    $("#panel").innerHTML =
      `<h3>有来源的补充说明</h3><div class="info">适用于基础资料订正建议、历史背景、角色补充和未形成新增内容身份的版本差异。审核合并后显示在作品档案与相关专题；不会自动改变作品、版本或正式职责计数。</div>${rows.map((n, i) => `<article class="record"><strong>${escape(n.title)}</strong><p>${escape(n.text)}</p>${link(n.source, "补充依据")} · <a href="${escape(n.dossierId)}.html#${escape(n.anchor)}" target="_blank" rel="noopener">相关专题 ↗</a>${i >= (data.notes.works[w.id] || []).length ? ` <button class="remove" data-remove-note="${i}">撤销本次新增</button>` : ""}</article>`).join("") || '<p class="muted">暂无补充说明。</p>'}<form id="edit-form" style="margin-top:22px">${input("title", "说明标题", "", "例如：某版新增后日谈的核实记录／角色姓名订正建议")}${area("text", "具体结论、适用版次及仍有的疑问", "", "避免把未经证实的推断写成既定事实。", 5)}${input("source", "支持结论的来源 URL", "", "每条说明一项核心来源；其他链接可另建说明。", "url")}${select("dossier", "相关专题", [["", "选择与该作品相关的专题"], ...data.catalogue.model.dossiers.map((d) => [d.id, d.name])])}${input("anchor", "专题中的已有作品锚点", w.id, "通常为作品 ID；也可以填写真实的具名段落锚点。")}<label class="check"><input name="confirmed" type="checkbox">我已核对来源，确认它支持上述说明</label><div class="actions"><button type="submit" class="primary">将说明加入修改清单</button></div></form>`;
  }

  function review() {
    const { $, escape, getPackage, reason, validatePackage } = read();
    const p = getPackage(),
      errors = validatePackage(p);
    $("#panel").innerHTML =
      `<h3>核对本次修改</h3><p class="review-count">共 ${p.operations.length} 项记录 · ${
        new Set(
          p.operations
            .filter((x) =>
              ["newWork", "editorial", "notes"].includes(x.resource),
            )
            .map((x) => x.key)
            .concat(
              p.operations
                .filter((x) => x.resource === "credits")
                .map((x) => x.after.workId),
            ),
        ).size
      } 部相关作品</p><div class="info">草稿内容只在当前浏览器。点击提交后，前往 GitHub 登录并运行自动检查；通过后生成分支和 PR，审核合并才会更新主站。GitHub 更新包、分支及 PR 将保存在公开仓库，请勿录入私密资料。</div>${area("reason", "本次修改说明", reason, "说明查证了哪些资料、修改了什么；不需要重复整个记录。", 2)}<div id="review-errors">${errors.length ? '<p class="muted">提交前需处理：' + errors.map(escape).join("；") + "</p>" : '<div class="info good">更新包基础校验通过。服务端还会检查记录冲突、来源、身份关联及历史回归。</div>'}</div><div class="actions"><button id="prepare-submit" class="primary" ${!p.operations.length ? "disabled" : ""}>校验并准备 GitHub 提交</button><button id="download-package" ${!p.operations.length ? "disabled" : ""}>下载更新包</button><button id="clear-draft" class="danger">清除本机草稿</button></div>${p.operations.map((op) => `<details><summary>${escape({ newWork: "新增作品", editorial: "叙事编目", notes: "补充说明", people: "个人身份", credits: "个人署名" }[op.resource])} · ${escape(op.key)}</summary><p class="muted">左为提交前记录，右为本次草稿。空值代表新增。</p><div class="diff-grid"><pre>${escape(JSON.stringify(op.before, null, 2))}</pre><pre>${escape(JSON.stringify(op.after, null, 2))}</pre></div></details>`).join("")}`;
  }

  function newWorkForm(bundle = null) {
    const { $, data, escape, nextWorkId, reservedWorks } = read();
    const w = bundle?.work || {},
      c = bundle?.contentVersions[0] || {},
      r = bundle?.platformReleases[0] || {},
      category = w.category || "视觉小说";
    $("#panel").innerHTML =
      `<div class="info">只收录符合现有范围的独立叙事作品。后续移植或增补请复用原作身份；同批多平台共用一个内容版本。表单资料会保存为本机草稿。</div><form id="edit-form">${input("work-id", "作品 ID", w.id || nextWorkId(reservedWorks()), "自动建议；提交时会再次检查是否已被其他人使用。")}<div class="form-row">${input("title", "中文作品名称", w.title || "")}${input("originalTitle", "作品原名", w.originalTitle || "")}</div>${input("year", "原作首发年份", w.firstYear || "", "", "number")}<div id="duplicate-hint" class="muted" aria-live="polite"></div><div class="form-row">${select(
        "category",
        "主分类",
        Object.keys(data.taxonomy.subcategories).map((k) => [k, k]),
        category,
      )}${select(
        "subcategory",
        "细分类",
        data.taxonomy.subcategories[category]
          .filter((x) => !["纯文本指令", "图文指令"].includes(x))
          .map((k) => [k, k]),
        w.subcategory || "",
      )}</div>${input("genre", "具体类型", w.genre || "", "例如：校园恋爱／悬疑推理；填写资料支持的类型。")}${area("synopsis", "剧情简介", w.synopsis || "", "概述主人公、处境与叙事目标，避免剧透结局。")}${area("characters", "主要角色", w.characters?.join("\n") || "", "每行一位角色；第一人称作品可写有依据的主人公身份。")}${input("source", "作品资料来源 URL", w.source || "", "", "url")}${area("notes", "作品备注", w.notes || "")}<fieldset class="field-block"><legend>实际玩法与依据</legend><div class="form-row">${Object.keys(
        data.taxonomy.interactionModes,
      )
        .map(
          (mode) =>
            `<label class="check"><input type="checkbox" name="modes" value="${escape(mode)}" ${(w.interactionModes || []).includes(mode) ? "checked" : ""}>${escape(mode)}</label>`,
        )
        .join(
          "",
        )}</div>${area("interaction-note", "操作方式及分类理由", w.interactionNote || "", "不要根据战斗题材猜测操作方式；未知时只选“待核实”。")}${area("interaction-sources", "玩法来源 URL", w.interactionSources?.join("\n") || "", "每行一个链接。")}</fieldset><fieldset class="field-block"><legend>原作内容身份</legend>${area("content-evidence", "原作内容／首次版本依据", c.evidence || "", "至少10字，说明独立原作内容及首次发行依据。")}${input("content-source", "原作内容来源 URL", c.source || "", "", "url")}</fieldset><fieldset class="field-block"><legend>原作首批平台发行</legend>${area("platforms", "首批平台", bundle?.platformReleases.map((r) => r.platform).join("\n") || "", "每行一个平台，仅填有证据确认的同一首批；最多10项。不同发行署名的首批请拆开独立考据。")}${input("publisher", "该次发行署名", r.publisher || "", "按资料原文填写；不会据发行方推断开发方。")}${select(
        "voice",
        "角色配音状态",
        ["未核实", "有", "无", "有（部分）", "有（主角部分）"].map((x) => [
          x,
          x,
        ]),
        r.voice || "未核实",
      )}${area("release-evidence", "首批发行依据与范围", r.contentNote || "", "明确哪些平台属于首次发行批次，不能只凭同年份判断。")}${input("release-source", "首批发行来源 URL", r.source || "", "", "url")}</fieldset><label class="check"><input name="confirmed" type="checkbox">我已核对独立作品身份、收录范围及原作首批资料</label><div class="actions"><button type="submit" class="primary">将新作品加入修改清单</button><button type="button" data-cancel-new>返回作品列表</button></div></form>`;
  }
  return {
    yearLabel,
    input,
    area,
    options,
    select,
    link,
    profileFields,
    profile,
    editorial,
    creditRows,
    credits,
    versions,
    release,
    notes,
    review,
    newWorkForm,
  };
}
