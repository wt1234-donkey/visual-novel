import { readWorkEditorContext } from "./src/application/work-editor/context.mjs";
import {
  collectCreatorNames,
  collectWorkValues,
} from "./src/application/work-editor/form-values.mjs";
import { createWorkEditorViews } from "./src/features/work-editor/views.mjs";
import { assertCurrentProjection } from "./src/infrastructure/storage/current-state-reader.mjs";
import { auditHistory } from "./src/features/audit-history.mjs";
import { readReleaseManifest } from "./src/infrastructure/storage/release-reader.mjs";
import { recordSavedOperation } from "./src/features/publication-status.mjs";
import { registerDraftEditor } from "./src/features/release-recovery.mjs";
import { readReleaseJson } from "./src/infrastructure/storage/release-reader.mjs";
import { createOnDemandReader } from "./src/infrastructure/storage/on-demand-reader.mjs";
import { requestScope } from "./src/infrastructure/storage/async-read.mjs";
const sourceReader = createOnDemandReader(),
  editorScope = requestScope();
import { same, lines, validURL } from "./management-model.mjs";
import {
  editableValues,
  projectWork,
  saveEdit,
  saveCreatorNames,
  undoEdit,
  changedFields,
  validateHistory,
  CREATOR_NAME_FIELDS,
} from "./work-edit-model.mjs?v=20261104-creators";
import {
  createEditClient,
  TOKEN_SETUP_URL,
} from "./work-edit-api.mjs?v=20261104-history-loading";
import { formalHistoryPage } from "./src/domain/catalogue/formal-journal.mjs";
import {
  createFormalCommandSession,
  commitFormalCommand,
} from "./src/application/catalogue/formal-commands.mjs";
const formalSession = createFormalCommandSession();
let historyBefore = Infinity;
import { makeProposal, offerEditorialProposal } from "./editorial-proposal.mjs";
const { escape, field, select, historyHTML, creatorFormHTML, editorHTML } =
  createWorkEditorViews(() => ({
    CREATOR_NAME_FIELDS,
    activeFieldEvidence,
    actor,
    base,
    creatorMode,
    historyBefore,
    historyReady,
    labels,
    loadedHistory,
    snapshot,
    taxonomy,
    TOKEN_SETUP_URL,
  }));
const labels = {
  ...CREATOR_NAME_FIELDS,
  title: "作品名称",
  originalTitle: "作品原名",
  chineseTitle: "中文检索名",
  chineseTitleType: "中文译名类型",
  titleAliases: "检索别名",
  category: "主分类",
  subcategory: "细分类",
  genre: "具体类型／题材",
  synopsis: "剧情简介",
  characters: "主要角色",
  charactersNote: "角色说明",
  charactersSource: "角色资料来源 URL",
  source: "作品资料来源 URL",
  interactionModes: "互动方式",
  interactionNote: "玩法说明与依据",
  interactionBasis: "玩法依据类型",
  interactionSources: "玩法来源 URL",
  notes: "作品备注",
};
let activeFieldEvidence = {},
  dialog,
  base,
  allWorks,
  reservedWorks,
  taxonomy,
  snapshot,
  client = createEditClient(),
  actor = "",
  busy = false,
  currentId = "",
  historyReady = false,
  creatorMode = false,
  editorSourceLease = null,
  editorCommandMode = "legacy";
const $ = (s) => dialog.querySelector(s);

function status(message, error = false) {
  $("#le-status").textContent = message;
  $("#le-status").className = "le-status" + (error ? " le-error" : "");
}
function ensureDialog() {
  if (dialog) return;
  const css = document.createElement("link");
  css.rel = "stylesheet";
  css.href = "./live-work-editor.css?v=20261101";
  document.head.append(css);
  dialog = document.createElement("dialog");
  dialog.id = "live-work-editor";
  dialog.setAttribute("aria-label", "编辑作品、完整历史与撤销");
  document.body.append(dialog);
  dialog.addEventListener("cancel", (e) => {
    e.preventDefault();
    close();
  });
  dialog.addEventListener("click", onClick);
  dialog.addEventListener("submit", (e) => {
    e.preventDefault();
    if (e.target.id === "le-form") save();
    else if (e.target.id === "le-creators-form") saveNames();
  });
  dialog.addEventListener("change", (e) => {
    if (e.target.name === "category") {
      $("[name=subcategory]").innerHTML = taxonomy.subcategories[e.target.value]
        .map((x) => `<option>${escape(x)}</option>`)
        .join("");
    }
  });
}
function dirty() {
  try {
    return !same(collect(), editableValues(projectWork(base, snapshot.store)));
  } catch {
    return false;
  }
}
function close() {
  if (busy) return;
  if (dirty() && !confirm("当前填写尚未保存，确定关闭编辑？")) return;
  editorScope.cancel();
  currentId = "";
  dialog.close();
}
let loadedHistory = null,
  historySerial = 0;
async function refreshHistory() {
  const version = ++historySerial,
    workId = base.id,
    before = historyBefore;
  try {
    const page = await auditHistory(
      "formal",
      snapshot.store,
      { workId, before },
      snapshot.head ? () => client.audit("formal", snapshot) : null,
    );
    if (
      version !== historySerial ||
      base.id !== workId ||
      before !== historyBefore
    )
      return;
    loadedHistory = page;
    $("#le-history").innerHTML = historyHTML();
  } catch (error) {
    if (version === historySerial)
      $("#le-history").textContent = "历史暂不可用：" + error.message;
  }
}

function render() {
  const w = editableValues(projectWork(base, snapshot.store));
  dialog.innerHTML = editorHTML(w);
  loadedHistory = null;
  return refreshHistory();
}
function collectNames() {
  return collectCreatorNames(
    new FormData($("#le-creators-form")),
    editableValues(projectWork(base, snapshot.store)),
    activeFieldEvidence,
  );
}
function collect() {
  return collectWorkValues(creatorMode ? null : new FormData($("#le-form")), {
    current: editableValues(projectWork(base, snapshot.store)),
    names: collectNames(),
    selectedFields: activeFieldEvidence,
    creatorsOnly: creatorMode,
  });
}
function offerWork(change, reason, before, after, sources = []) {
  const expectedRevision = snapshot.store.records[base.id]?.revision || 0;
  const preview = changedFields(before, after).map((field) => ({
    id: labels[field],
    before: before[field],
    after: after[field],
  }));
  const proposal = makeProposal(
    "work",
    reason,
    {
      workId: base.id,
      expectedRevision,
      sourceLease: editorSourceLease,
      ...change,
    },
    preview,
    sources,
  );
  status("");
  offerEditorialProposal($("#le-status"), proposal);
}
async function saveNames() {
  if (busy) return;
  try {
    if (!historyReady) throw Error("请先重新读取最新修改记录");
    const current = editableValues(projectWork(base, snapshot.store));
    if (
      changedFields(current, collect()).some((k) => !(k in CREATOR_NAME_FIELDS))
    )
      throw Error(
        "作品资料也有未保存修改，请使用下方作品表单一起提交，或先还原其他资料再单独保存创作者。",
      );
    const names = collectNames(),
      meta = {
        expectedRevision: snapshot.store.records[base.id]?.revision || 0,
        id: crypto.randomUUID(),
        at: new Date().toISOString(),
        actor: actor || "送审预览",
      };
    saveCreatorNames(
      snapshot.store,
      base,
      names,
      meta,
      taxonomy,
      reservedWorks.map((w) => projectWork(w, snapshot.store)),
    );
    if (!actor) {
      offerWork(
        { after: { ...current, ...names } },
        "添加或调整剧作、美术与音乐",
        current,
        { ...current, ...names },
      );
      return;
    }
    lock(true);
    status("正在保存剧作、美术与音乐…");
    const next = saveCreatorNames(
      snapshot.store,
      base,
      names,
      meta,
      taxonomy,
      reservedWorks.map((w) => projectWork(w, snapshot.store)),
    );
    await commit(next, snapshot.sha, "Update creator names for " + base.id, {
      operationId: meta.id,
      at: meta.at,
      expectedRevision: meta.expectedRevision,
      reason: "添加或调整剧作、美术与音乐",
      sources: [],
      action: { type: "creators", workId: base.id, names },
    });
  } catch (e) {
    if (e.code === "SOURCE_CHANGED")
      readReleaseManifest(fetch, { refresh: true }).catch(() => {});
    status(e.message, true);
  } finally {
    lock(false);
  }
}
let completeHistorySources = new Set();
async function validateLoadedHistory(live, { signal } = {}) {
  const workId = currentId,
    ids = Object.keys(live.store?.records || {}).filter(
      (id) => !completeHistorySources.has(id),
    );
  // Authenticated history can be ahead of the published snapshot. Hydrate only
  // those newly referenced originals before running the existing full validator.
  for (let i = 0; i < ids.length; i += 4) {
    const rows = await Promise.all(
      ids
        .slice(i, i + 4)
        .map((id) => sourceReader.formal(id, "formal", { signal })),
    );
    if (currentId !== workId || signal?.aborted)
      throw Object.assign(Error("读取已取消"), { name: "AbortError" });
    for (const { source } of rows) {
      allWorks = allWorks.map((w) => (w.id === source.id ? source : w));
      reservedWorks = reservedWorks.map((w) =>
        w.id === source.id ? source : w,
      );
      completeHistorySources.add(source.id);
    }
  }
  if (live.store.projectionVersion) {
    assertCurrentProjection(live.store, "formal");
    validateHistory(
      { schemaVersion: 1, records: live.store.records },
      reservedWorks,
      taxonomy,
    );
  } else validateHistory(live.store, reservedWorks, taxonomy);
}

function lock(value) {
  busy = value;
  dialog
    .querySelectorAll("button,input,textarea,select")
    .forEach((el) => (el.disabled = value));
  if (!value) {
    $("#le-disconnect").disabled = !actor;
    $("#le-retry-pending").disabled =
      !actor ||
      !formalSession
        .pending(base?.id)
        .some((command) => command.actor === actor);
  }
}
async function commit(store, sha, message, details) {
  const command = {
    schemaVersion: 1,
    kind: "formal",
    actor,
    sourceLease: editorSourceLease,
    ...details,
  };
  const result = await formalSession.execute(command, (operation) =>
    commitFormalCommand({
      repository: client,
      opened: snapshot,
      command: operation,
      base,
      taxonomy,
      works: reservedWorks.map((w) => projectWork(w, snapshot.store)),
      validate: validateLoadedHistory,
    }),
  );
  recordSavedOperation({
    operationId: result.operationId || details.operationId,
    kind: "formal",
    revision: result.revision,
    commit: result.commit,
    workId: base.id,
    at: result.at || details.at,
  });
  try {
    await validateLoadedHistory(result);
  } catch (error) {
    status(
      "本次操作已确认保存，当前资料读取暂不可用；输入保留，请重新读取。" +
        error.message,
      true,
    );
    return;
  }
  snapshot = {
    sha: result.sha,
    head: result.head || result.commit,
    store: result.store,
  };
  historyBefore = Infinity;
  window.dispatchEvent(
    new CustomEvent("catalogue-work-edit", { detail: snapshot.store }),
  );
  await render();
  status(
    result.alreadyApplied
      ? "已确认原操作保存成功，当前显示最新记录，后续修改已保留。"
      : "已保存到主库，当前页面已更新。完整修改和撤销事件可在下方查询；生效进度见“保存与发布状态”。",
  );
}
async function save() {
  if (busy) return;
  try {
    if (!historyReady) throw Error("请先重新读取最新修改记录");
    const values = new FormData($("#le-form"));
    if (!values.has("confirmed")) throw Error("请核对来源并勾选确认");
    const after = collect(),
      meta = {
        expectedRevision: snapshot.store.records[base.id]?.revision || 0,
        id: crypto.randomUUID(),
        at: new Date().toISOString(),
        actor: actor || "送审预览",
        reason: String(values.get("reason") || ""),
        sources: lines(String(values.get("evidenceSources") || "")),
      };
    const projected = reservedWorks.map((w) => projectWork(w, snapshot.store));
    saveEdit(snapshot.store, base, after, meta, taxonomy, projected);
    if (!actor) {
      offerWork(
        { after },
        meta.reason,
        editableValues(projectWork(base, snapshot.store)),
        after,
        meta.sources,
      );
      return;
    }
    lock(true);
    status("正在校验最新记录并保存…");
    const next = saveEdit(
      snapshot.store,
      base,
      after,
      meta,
      taxonomy,
      reservedWorks.map((w) => projectWork(w, snapshot.store)),
    );
    await commit(
      next,
      snapshot.sha,
      "Edit " + base.id + ": " + meta.reason.replace(/\s+/g, " ").slice(0, 80),
      {
        operationId: meta.id,
        at: meta.at,
        expectedRevision: meta.expectedRevision,
        reason: meta.reason,
        sources: meta.sources,
        action: { type: "edit", workId: base.id, values: after },
      },
    );
  } catch (e) {
    if (e.code === "SOURCE_CHANGED")
      readReleaseManifest(fetch, { refresh: true }).catch(() => {});
    status(e.message, true);
  } finally {
    lock(false);
  }
}
async function undo(target) {
  if (busy) return;
  if (!actor) {
    $("#le-auth").open = true;
    status("请先连接 GitHub 写入权限后回撤", true);
    return;
  }
  const entries = snapshot.store.records[base.id]?.recent || [],
    i = entries.findIndex((e) => e.id === target);
  if (i < 0) return;
  if (dirty() && !confirm("当前填写尚未保存，回撤会替换这些输入。继续？"))
    return;
  if (
    !confirm(
      `恢复到“${entries[i].reason}”之前？将撤回该次及之后的 ${entries.length - i} 次修改，并留下独立撤销事件。`,
    )
  )
    return;
  try {
    lock(true);
    status("正在核对并回撤…");
    const details = {
      operationId: crypto.randomUUID(),
      at: new Date().toISOString(),
      expectedRevision: snapshot.store.records[base.id].revision,
      reason: "回撤最近正式作品修改",
      sources: [],
      action: { type: "undo", workId: base.id, targetId: target },
    };
    const next = undoEdit(
      snapshot.store,
      base,
      target,
      details.expectedRevision,
      taxonomy,
      reservedWorks.map((w) => projectWork(w, snapshot.store)),
      {
        id: details.operationId,
        at: details.at,
        actor,
        reason: details.reason,
        sources: [],
      },
    );
    await commit(
      next,
      snapshot.sha,
      "Undo recent work edits for " + base.id,
      details,
    );
  } catch (e) {
    if (e.code === "SOURCE_CHANGED")
      readReleaseManifest(fetch, { refresh: true }).catch(() => {});
    status(e.message, true);
  } finally {
    lock(false);
  }
}
async function onClick(e) {
  const b = e.target.closest("button");
  if (!b) return;
  if (b.id === "le-history-older") {
    historyBefore = Number(b.dataset.before);
    refreshHistory();
  } else if (b.id === "le-history-newest") {
    historyBefore = Infinity;
    refreshHistory();
  } else if (b.id === "le-retry-pending") {
    const pending = formalSession
      .pending(base.id)
      .filter((command) => command.actor === actor)
      .at(-1);
    if (!pending) return;
    if (
      dirty() &&
      !confirm("核对成功后将显示最新记录，请先保留需要的未保存输入。继续？")
    )
      return;
    try {
      lock(true);
      status("正在核对原操作…");
      await commit(null, null, "", pending);
    } catch (error) {
      status(error.message, true);
    } finally {
      lock(false);
    }
  } else if (b.id === "le-jump-history")
    $("#le-history").scrollIntoView({ behavior: "smooth", block: "start" });
  else if (b.hasAttribute("data-le-close")) close();
  else if (b.id === "le-connect") {
    const token = $("#le-token").value.trim();
    $("#le-token").value = "";
    try {
      lock(true);
      const connection = createEditClient(token, fetch, {
        sourceLease: editorSourceLease,
        commandMode: editorCommandMode,
      });
      const login = await connection.connect();
      const live = await connection.read({ workIds: [base.id] });
      await validateLoadedHistory(live);
      const changed =
          !historyReady ||
          !same(
            live.store.records[base.id] || null,
            snapshot.store.records[base.id] || null,
          ),
        hasDraft = historyReady && dirty();
      client = connection;
      actor = login;
      if (changed && hasDraft) {
        $("#le-auth").querySelector("summary").textContent =
          "写入权限 · " + actor + "（仅本次会话）";
        status(
          "已连接，但此作品在网站发布后已有新修改。当前输入保留；请先保留需要的内容，再点“重新读取最新记录”核对。",
          true,
        );
      } else {
        snapshot = live;
        historyReady = true;
        if (changed) await render();
        else refreshHistory();
        $("#le-auth").querySelector("summary").textContent =
          "写入权限 · " + actor + "（仅本次会话）";
        $("#le-auth").open = false;
        status(
          "已连接账号 " +
            actor +
            "，并读取最新修改记录；保存时会再次检查并发修改和写入权限。",
        );
      }
    } catch (err) {
      status(err.message, true);
    } finally {
      lock(false);
    }
  } else if (b.id === "le-refresh") {
    if (!actor) {
      $("#le-auth").open = true;
      status("请先连接 GitHub，再读取最新修改记录。", true);
      return;
    }
    if (dirty() && !confirm("重新读取将替换当前尚未保存的输入，继续？")) return;
    try {
      lock(true);
      const live = await client.read({ workIds: [currentId] });
      await validateLoadedHistory(live);
      snapshot = live;
      historyReady = true;
      await render();
      status("已读取最新修改记录，可以继续编辑。");
    } catch (err) {
      status(err.message, true);
    } finally {
      lock(false);
    }
  } else if (b.id === "le-disconnect") {
    client = createEditClient();
    actor = "";
    $("#le-auth").open = true;
    $("#le-auth").querySelector("summary").textContent =
      "写入权限 · 连接 GitHub";
    $("#le-disconnect").disabled = true;
    status("已断开连接，凭证已从当前会话移除。");
  } else if (b.id === "le-creators-preview") {
    const names = collectNames();
    $("#le-creators-preview-box").innerHTML = Object.entries(
      CREATOR_NAME_FIELDS,
    )
      .map(
        ([k, label]) =>
          `<p><strong>${label}</strong>：${escape(names[k].join("、") || "尚未添加")}</p>`,
      )
      .join("");
  } else if (b.id === "le-preview") {
    try {
      const before = editableValues(projectWork(base, snapshot.store)),
        after = collect(),
        fields = changedFields(before, after);
      $("#le-preview-box").innerHTML = fields.length
        ? `<details open><summary>本次修改 ${fields.length} 项</summary>${fields.map((k) => `<p><strong>${labels[k]}</strong></p><pre class="le-diff">${escape(JSON.stringify({ 修改前: before[k], 修改后: after[k] }, null, 2))}</pre>`).join("")}</details>`
        : '<p class="le-small">没有实际修改。</p>';
    } catch (err) {
      status(err.message, true);
    }
  } else if (b.dataset.leUndo) undo(b.dataset.leUndo);
}
export async function showLiveWorkEditor(
  workId,
  { creatorsOnly = false } = {},
) {
  ensureDialog();
  if (busy) return;
  if (dialog.open && dirty() && !confirm("切换作品会丢弃未保存输入，继续？"))
    return;
  currentId = workId;
  historyBefore = Infinity;
  creatorMode = creatorsOnly;
  dialog.dataset.recoveryWorkId = workId;
  dialog.dataset.recoveryMode = creatorsOnly ? "creators" : "edit";
  dialog.innerHTML = "<h2>正在读取作品与修改历史…</h2>";
  if (!dialog.open) dialog.showModal();
  try {
    const request = editorScope.start();
    const { directory, full, tax, validation, release, history } =
      await readWorkEditorContext(workId, {
        reader: sourceReader,
        client,
        actor,
        signal: request.signal,
        readJson: readReleaseJson,
      });
    editorSourceLease = directory.sourceLease;
    editorCommandMode = release.saveMode || "legacy";
    if (!request.current() || currentId !== workId) return;
    const originals = new Map(
      [
        ...directory.raw.main.works,
        ...directory.raw.supplement.works,
        ...validation,
        full.source,
      ].map((w) => [w.id, w]),
    );
    allWorks = [...originals.values()];
    completeHistorySources = new Set(
      [...validation, full.source].map((w) => w.id),
    );
    reservedWorks = [
      ...allWorks,
      ...directory.coverage.companies.flatMap((c) => [
        ...(c.relatedGames || []),
        ...(c.dossierOnlyWorks || []),
      ]),
    ];
    activeFieldEvidence = full.work?.fieldEvidence || {};
    base = full.source;
    if (!base) throw Error("此作品尚未进入正式主库，请先完成基础库补录");
    taxonomy = tax;
    snapshot = history;
    historyReady = !history.loadError;
    if (historyReady)
      try {
        await validateLoadedHistory(snapshot, { signal: request.signal });
      } catch (error) {
        if (!request.current() || currentId !== workId) return;
        snapshot = {
          sha: null,
          store: { schemaVersion: 1, records: {} },
          loadError: error,
        };
        historyReady = false;
      }
    await render();
    if (!historyReady) {
      $("#le-auth").open = true;
      status(
        "修改记录暂时不可用，已保留账号连接入口。请连接 GitHub 后重新读取，或稍后重新打开；当前资料暂不能保存。\n" +
          snapshot.loadError.message,
        true,
      );
    }
  } catch (e) {
    if (currentId !== workId || e.name === "AbortError") return;
    dialog.innerHTML = `<h2>暂时无法编辑</h2><p>${escape(e.message)}</p><button data-le-close>关闭</button>`;
  }
}

registerDraftEditor("live-work-editor", {
  canRestore: (mode) => ["edit", "creators"].includes(mode),
  open: (id, mode) =>
    showLiveWorkEditor(id, { creatorsOnly: mode === "creators" }),
});
