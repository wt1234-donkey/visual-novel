// Presentation only: mutable catalogue/session state stays with the controller.
export function createWorkEditorViews(read) {
  function escape(s) {
    return String(s ?? "").replace(
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

  function field(name, value, multiline = false) {
    const { activeFieldEvidence, labels } = read();
    const picked = activeFieldEvidence[name];
    if (picked) value = picked.value;
    return `<label class="le-field"><span>${labels[name]}</span>${multiline ? `<textarea name="${name}" rows="3" ${picked ? "readonly" : ""}>${escape(Array.isArray(value) ? value.join("\n") : value)}</textarea>` : `<input name="${name}" value="${escape(value)}" ${picked ? "readonly" : ""}>`}</label>`;
  }

  function select(name, values, value) {
    const { labels } = read();
    return `<label class="le-field"><span>${labels[name]}</span><select name="${name}">${values.map((x) => `<option ${x === value ? "selected" : ""}>${escape(x)}</option>`).join("")}</select></label>`;
  }

  function historyHTML() {
    const { base, historyBefore, historyReady, loadedHistory, snapshot } =
      read();

    if (!historyReady)
      return '<p class="le-small">修改记录暂不可用，连接 GitHub 后可重新读取。</p>';
    if (!loadedHistory)
      return '<p class="le-small">正在按作品索引读取历史…</p>';
    const row = snapshot.store.records[base.id],
      entries = row?.recent || [],
      page = loadedHistory;
    const diff = (entry) =>
      `<details><summary>查看更正层前后内容</summary><pre class="le-diff">${escape(JSON.stringify(entry.values ? { 修改前: entry.values.before, 修改后: entry.values.after } : { 修改前: entry.before?.overrides ?? entry.before ?? {}, 修改后: entry.after?.overrides ?? entry.after ?? {} }, null, 2))}</pre></details>`;
    return `<h3>最近3次快捷回撤 · 当前修订 ${row?.revision || 0}</h3><p class="le-small">恢复到某次修改前会撤回该次及之后的快捷修改；撤销本身会追加独立事件，完整历史不会删除。</p>${
      [...entries]
        .reverse()
        .map(
          (entry) =>
            `<article class="le-record"><strong>${escape(entry.reason)}</strong><p class="le-small">${escape(entry.at)} · ${escape(entry.actor)}</p>${diff(entry)}<button type="button" data-le-undo="${escape(entry.id)}">恢复到此次修改前</button></article>`,
        )
        .join("") || '<p class="le-small">本作品尚无可快捷回撤的修改。</p>'
    }
 <h3>完整审计历史 · ${page.total}个迁移后事件</h3><p class="le-small">${page.checkpoint ? `完整日志起点：${escape(page.checkpoint.at)}；本作品起点修订 ${page.baselineRevision}。` : "旧格式记录尚无完整追加日志。"}迁移前已保留的最近记录仅作兼容证据，更早历史可在 GitHub 仓库追溯。</p>
 ${page.events.map((event) => `<article class="le-record" data-audit-id="${escape(event.id)}"><strong>${event.commandType === "undo" ? "撤销事件" : "修改事件"} · ${escape(event.reason)}</strong><p class="le-small">修订 ${event.previousRevision} → ${event.revision} · ${escape(event.at)} · ${escape(event.actor)}</p><p class="le-small">操作ID：${escape(event.id)}${event.undoOf ? `；撤销目标：${escape(event.undoOf)}` : ""}</p>${diff(event)}<p class="le-small">来源：${event.sources.length ? event.sources.map(escape).join("、") : "姓名手动添加或撤销事件，无新增来源"}</p></article>`).join("") || '<p class="le-small">此页没有迁移后的修改事件。</p>'}
 <div class="le-actions">${page.nextBefore !== null ? `<button type="button" id="le-history-older" data-before="${page.nextBefore}">更早的20条</button>` : ""}${historyBefore !== Infinity ? '<button type="button" id="le-history-newest">返回最新历史</button>' : ""}</div>
 ${page.legacyRecent.length ? `<details><summary>迁移起点保留的旧记录（${page.legacyRecent.length}条，非补建事件）</summary>${page.legacyRecent.map((entry) => `<article class="le-record"><strong>${escape(entry.reason)}</strong><p>${escape(entry.at)} · ${escape(entry.actor)} · 修订 ${entry.revision}</p>${diff(entry)}</article>`).join("")}</details>` : ""}`;
  }

  function creatorFormHTML(w) {
    const { CREATOR_NAME_FIELDS, actor, historyReady } = read();
    return `<form id="le-creators-form" ${historyReady ? "" : "inert"}><h3>添加剧作／美术／音乐</h3><p class="le-small">每行一人，可填写多人；无需依据、来源链接或修改说明。保存后显示为“手动添加”。</p>${Object.keys(
      CREATOR_NAME_FIELDS,
    )
      .map((k) => field(k, w[k], true))
      .join(
        "",
      )}<div class="le-actions"><button type="button" id="le-creators-preview">预览创作者</button><button type="submit" class="le-primary">${actor ? "保存剧作／美术／音乐" : "预览并送审创作者"}</button></div><div id="le-creators-preview-box"></div></form>`;
  }
  function editorHTML(w) {
    const {
      activeFieldEvidence,
      actor,
      base,
      creatorMode,
      historyReady,
      taxonomy,
      TOKEN_SETUP_URL,
    } = read();
    return `<div class="le-head"><div><h2>${creatorMode ? "添加剧作／美术／音乐" : "编辑作品"} · ${escape(w.chineseTitle || w.title)}</h2><p class="le-small">${escape(base.id)} · 原作年份 ${base.firstYear} · 最近3次修改可回撤</p></div><button class="le-close" type="button" data-le-close aria-label="关闭编辑">×</button></div><div class="le-info">连接账号后可直接保存，经可信执行端校验后发布。作品身份、首发年份、发行与内容版本保持关联；这些资料请在资料管理台单独核查。剧作、美术、音乐可直接填写姓名；其他作品资料的说明与来源将随修改记录公开。</div><div class="le-actions"><button type="button" id="le-jump-history">查看完整历史与回撤</button><button type="button" id="le-retry-pending">核对上次保存结果</button></div><details id="le-auth"><summary>管理员直连 · ${actor ? escape(actor) + "（仅本次会话）" : "GitHub 备用入口"}</summary><p class="le-small">使用本仓库的 Fine-grained personal access token，Resource owner 选择 <b>wt1234-donkey</b>；Repository access 选择 <b>Only select repositories → visual-novel</b>（Public repositories 只有读取权限），Repository permissions → <b>Contents: Read and write</b>。凭证只保留在当前页面内存，刷新后需重新连接；不要把凭证发到聊天。</p><div class="le-actions"><a class="le-link" href="${TOKEN_SETUP_URL}" target="_blank" rel="noopener noreferrer">创建本仓库专用凭证 ↗</a><button type="button" id="le-disconnect" ${actor ? "" : "disabled"}>断开连接</button></div><label class="le-field"><span>GitHub 写入凭证</span><input id="le-token" type="password" autocomplete="off" spellcheck="false" aria-label="GitHub 写入凭证"></label><div class="le-actions"><button type="button" id="le-connect">连接写入权限</button><button type="button" id="le-refresh">重新读取最新记录</button></div></details><div id="le-status" class="le-status" role="status" aria-live="polite"></div>${creatorFormHTML(w)}<form id="le-form" ${creatorMode ? "hidden " : ""}${historyReady ? "" : "inert"}><p><a href="field-evidence.html#${encodeURIComponent(base.id)}">字段证据、不同来源与选用理由 ↗</a></p>${Object.keys(activeFieldEvidence).length ? '<p class="le-info">以下只读字段采用显式证据结论。请到字段证据页更换或清除选用；其他资料和无来源姓名仍可直接修改。</p>' : ""}<h3>作品资料</h3><div class="le-grid">${field("title", w.title)}${field("originalTitle", w.originalTitle)}${field("chineseTitle", w.chineseTitle)}${select("chineseTitleType", ["通行译名", "站内编辑译名"], w.chineseTitleType)}</div>${field("titleAliases", w.titleAliases, true)}<div class="le-grid">${select("category", Object.keys(taxonomy.subcategories), w.category)}${select("subcategory", taxonomy.subcategories[w.category], w.subcategory)}</div>${field("genre", w.genre)}${field("synopsis", w.synopsis, true)}${field("characters", w.characters, true)}<p class="le-small">别名、主要角色、来源列表均每行一项。未核实的角色不要用占位词填充。</p>${field("charactersNote", w.charactersNote, true)}${field("charactersSource", w.charactersSource)}${field("source", w.source)}<h3>实际玩法与依据</h3><div class="le-modes">${Object.keys(
      taxonomy.interactionModes,
    )
      .map(
        (m) =>
          `<label class="le-check"><input type="checkbox" name="interactionModes" value="${escape(m)}" ${w.interactionModes.includes(m) ? "checked" : ""}>${escape(m)}</label>`,
      )
      .join(
        "",
      )}</div>${field("interactionNote", w.interactionNote, true)}${select("interactionBasis", [...new Set([w.interactionBasis, "既有资料归纳", "来源核对"])], w.interactionBasis)}${field("interactionSources", w.interactionSources, true)}${field("notes", w.notes, true)}<h3>本次修改依据</h3><label class="le-field"><span>修改说明（至少5字）</span><textarea name="reason" rows="2"></textarea></label><label class="le-field"><span>支持本次修改的来源 URL（每行一项）</span><textarea name="evidenceSources" rows="2">${escape(w.source)}</textarea></label><label class="le-check"><input type="checkbox" name="confirmed">我已核对本次修改的事实与来源</label><div class="le-actions"><button type="button" id="le-preview">预览修改</button><button type="submit" class="le-primary">${actor ? "保存到主库网站" : "预览并送审"}</button><a class="le-link" href="manage.html#${encodeURIComponent(base.id)}">叙事编目、署名与版本资料 ↗</a></div><div id="le-preview-box"></div></form><section id="le-history">正在读取历史…</section>`;
  }
  return { escape, field, select, historyHTML, creatorFormHTML, editorHTML };
}
