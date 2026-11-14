import { restoreManagementDraft } from "./src/application/management/draft.mjs";
import { createManagementChanges } from "./src/application/management/changes.mjs";
import { createManagementForms } from "./src/features/management/forms.mjs";
import { createOnDemandReader } from "./src/infrastructure/storage/on-demand-reader.mjs";
import { requestScope } from "./src/infrastructure/storage/async-read.mjs";
import {
  registerPageRecovery,
  restoreReleaseState,
} from "./src/features/release-recovery.mjs";
import "./release-runtime.mjs";
import { readReleaseJson } from "./src/infrastructure/storage/release-reader.mjs";
import { buildManagementView } from "./src/application/management/view.mjs";
import { displayTitle } from "./src/domain/catalogue/effective.mjs";
import {
  managementProposal,
  offerEditorialProposal,
} from "./editorial-proposal.mjs";
import {
  FIELDS,
  ROLES,
  WORKFLOW,
  makeNewWork,
  validateNewBundle,
  duplicateWorks,
  nextWorkId,
  clone,
  same,
  lines,
  tags,
  validURL,
  searchWorks,
  resourceValue,
  setResource,
  packageChanges,
  validatePackage,
} from "./management-model.mjs?v=20261031-new-work";
const $ = (s) => document.querySelector(s),
  escape = (s) =>
    String(s ?? "").replace(
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
const KEY = "narrative-management-v1";
let projectionInputs, view;
const reader = createOnDemandReader(),
  ready = new Set(),
  scope = requestScope();
let waitingKey = "",
  loadError = "";
async function hydrateResource(id, family, options) {
  const key = family + ":" + id;
  if (ready.has(key)) return;
  if (family === "formal") {
    const full = await reader.formal(id, "formal", options);
    for (const target of [data, working])
      for (const name of ["games", "supplement"]) {
        const i = target[name].works.findIndex((w) => w.id === id);
        if (i < 0) continue;
        target[name].works[i] = structuredClone(full.source);
        for (const field of ["contentVersions", "platformReleases"])
          target[name][field] = [
            ...target[name][field].filter((r) => r.workId !== id),
            ...structuredClone(full[field]),
          ];
      }
  } else if (family === "creators" || family === "baseline") {
    const value = await reader.optional(family, options);
    data[family] = clone(value);
    working[family] = clone(value);
  } else {
    const value = await reader.formal(id, family, options);
    for (const target of [data, working]) {
      if (value === null) delete target[family].works[id];
      else target[family].works[id] = clone(value);
    }
  }
  ready.add(key);
}
async function hydrateDraft(draft) {
  const newIds = new Set(
    (draft.package?.operations || [])
      .filter((op) => op.resource === "newWork")
      .map((op) => op.key),
  );
  for (const op of draft.package?.operations || []) {
    if (["people", "credits"].includes(op.resource))
      await hydrateResource("*", "creators");
    else if (
      ["editorial", "notes"].includes(op.resource) &&
      !newIds.has(op.key)
    )
      await hydrateResource(op.key, op.resource);
  }
}
function selectionReady() {
  if (
    !selected ||
    selected === "__new__" ||
    !data.games.works.some((w) => w.id === selected)
  )
    return true;
  const families = [
    "formal",
    ...(tab === "editorial"
      ? ["editorial", "baseline"]
      : tab === "notes"
        ? ["notes"]
        : tab === "credits"
          ? ["creators"]
          : []),
  ];
  const missing = families.filter(
    (f) =>
      !ready.has(
        f + ":" + (["creators", "baseline"].includes(f) ? "*" : selected),
      ),
  );
  if (!missing.length) {
    waitingKey = "";
    return true;
  }
  const key = selected + ":" + tab;
  $("#panel").innerHTML =
    '<p role="status">' +
    (loadError && waitingKey === key
      ? "资料暂不可用：" +
        escape(loadError) +
        ' <button type="button" data-retry-detail>重试读取</button>'
      : '正在按需读取本部资料… <button type="button" data-cancel-detail>取消</button>') +
    "</p>";
  if (waitingKey !== key) {
    waitingKey = key;
    loadError = "";
    const id = selected,
      t = tab,
      request = scope.start();
    Promise.all(
      missing.map((f) =>
        hydrateResource(["creators", "baseline"].includes(f) ? "*" : id, f, {
          signal: request.signal,
        }),
      ),
    )
      .then(() => {
        if (request.current() && id === selected && t === tab) render();
      })
      .catch((error) => {
        if (request.current()) {
          loadError = error.message;
          render();
        }
      });
  }
  return false;
}
let data,
  working,
  selected = "",
  tab = "profile",
  limit = 50,
  formCache = {},
  reason = "",
  busy = false,
  storageOK = true;
const now = () =>
  new Date().toLocaleDateString("en-CA", { timeZone: "Asia/Shanghai" });
const title = (w) => displayTitle(view?.byId.get(w.id) || w);
registerPageRecovery({
  capture: () => {
    stashForm();
    saveDraft();
    return {
      draft: {
        schemaVersion: 1,
        package: getPackage(),
        formCache,
        selected,
        tab,
      },
      selected,
      tab,
      query: $("#search").value,
      missing: $("#missing-only").checked,
      limit,
    };
  },
  restore: async (saved) => {
    if (saved.draft) {
      await hydrateDraft(saved.draft);
      loadDraft(saved.draft);
      for (const values of Object.values(formCache))
        if (Object.hasOwn(values, "confirmed")) values.confirmed = false;
    }
    if (
      saved.selected === "__new__" ||
      working.games.works.some((work) => work.id === saved.selected)
    )
      selected = saved.selected;
    if (
      [
        "new",
        "profile",
        "editorial",
        "credits",
        "versions",
        "notes",
        "review",
      ].includes(saved.tab)
    )
      tab = saved.tab;
    $("#search").value = String(saved.query || "");
    $("#missing-only").checked = !!saved.missing;
    limit = Number.isSafeInteger(saved.limit) ? saved.limit : 50;
    render();
  },
});
const {
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
} = createManagementForms(() => ({
  $,
  FIELDS,
  ROLES,
  data,
  displayTitle,
  escape,
  getPackage,
  nextWorkId,
  reason,
  reservedWorks,
  validURL,
  validatePackage,
  working,
}));

function notice(message, error = false) {
  $("#notice").textContent = message;
  $("#notice").className = error ? "error" : "";
}
function getPackage() {
  return packageChanges(data, working, reason, now());
}
function updateCount() {
  $("#change-count").textContent = getPackage().operations.length;
}
function stashForm() {
  const form = $("#edit-form");
  if (!form) return;
  const values = {};
  for (const el of form.elements)
    if (el.name)
      values[el.name === "modes" ? "mode:" + el.value : el.name] =
        el.type === "checkbox" ? el.checked : el.value;
  formCache[selected + ":" + tab] = values;
}
function restoreForm() {
  const values = formCache[selected + ":" + tab],
    form = $("#edit-form");
  if (!values || !form) return;
  if (tab === "new" && values.category) {
    form.elements.namedItem("category").value = values.category;
    form.elements.namedItem("subcategory").innerHTML = options(
      data.taxonomy.subcategories[values.category]
        .filter((x) => !["纯文本指令", "图文指令"].includes(x))
        .map((x) => [x, x]),
      values.subcategory || "",
    );
  }
  for (const [key, value] of Object.entries(values)) {
    const el = key.startsWith("mode:")
      ? [...form.elements].find(
          (x) => x.name === "modes" && x.value === key.slice(5),
        )
      : form.elements.namedItem(key);
    if (el) {
      if (el.type === "checkbox") el.checked = value;
      else el.value = value;
    }
  }
}
function saveDraft() {
  if (!data) return;
  const p = getPackage();
  try {
    localStorage.setItem(
      KEY,
      JSON.stringify({
        schemaVersion: 1,
        package: p,
        formCache,
        selected,
        tab,
      }),
    );
    storageOK = true;
    $("#save-status").textContent =
      "草稿已保存在此浏览器 · " +
      new Date().toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
      });
  } catch {
    storageOK = false;
    $("#save-status").textContent = "浏览器存储不可用，请导出草稿";
    notice(
      "无法写入浏览器草稿。当前内容仍在本页内存中，请导出草稿备份。",
      true,
    );
  }
  updateCount();
  $("#export-draft").disabled = false;
}
function loadDraft(draft) {
  ({ working, formCache, reason, selected, tab } = restoreManagementDraft(
    data,
    draft,
  ));
}
function renderList() {
  const operations = getPackage().operations;
  view = buildManagementView(working, projectionInputs);
  const rows = searchWorks(
    view.main.works,
    $("#search").value,
    working.editorial,
    $("#missing-only").checked,
  );
  $("#result-count").textContent =
    `${rows.length} 部作品 · 显示 ${Math.min(rows.length, limit)} 部`;
  $("#work-list").innerHTML =
    rows
      .slice(0, limit)
      .map((w) => {
        const missing = FIELDS.filter(
          ([f]) => !working.editorial.works[w.id]?.[f]?.length,
        ).length;
        return `<button class="work-item" data-work="${escape(w.id)}" aria-current="${selected === w.id}"><strong>${escape(title(w))}</strong><small>${escape(w.originalTitle)} · ${escape(yearLabel(w))} · ${w.id}</small><small>${missing ? '<span class="dot"></span>待补 ' + missing + " 项" : "四项已有编目"}${operations.some((op) => op.key === w.id || op.after?.workId === w.id) ? " · 有草稿修改" : ""}</small></button>`;
      })
      .join("") ||
    '<p class="picker-foot">没有匹配作品，试试原名或较短的关键词。</p>';
  $("#more").hidden = rows.length <= limit;
}
function render() {
  renderList();
  $("#empty").hidden = !!selected;
  $("#editing").hidden = !selected;
  if (!selected) return;
  if (selected === "__new__") {
    $("#tabs").hidden = true;
    $("#work-heading").innerHTML =
      "<h2>添加新作品</h2><p>一个作品身份 · 一个原作内容 · 有依据的首批发行</p>";
    newWorkForm();
    restoreForm();
    return;
  }
  $("#tabs").hidden = false;
  const w = view.byId.get(selected);
  $("#work-heading").innerHTML =
    `<div class="heading-line"><div><p class="eyebrow">WORK RECORD / ${escape(w.id)}</p><h2>${escape(title(w))}</h2><p>${escape(w.originalTitle)} · ${escape(yearLabel(w))} · ${escape(w.category)}</p></div><a class="badge" href="index.html#work/${encodeURIComponent(w.id)}/profile" target="_blank" rel="noopener">查看作品 ↗</a></div>`;
  $("#tabs")
    .querySelectorAll("button")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.tab === tab)),
    );
  if (!selectionReady()) return;
  ({
    profile: profile,
    editorial: editorial,
    credits: credits,
    versions: versions,
    notes: notes,
    review: review,
  })[tab](view.byId.get(selected));
  restoreForm();
  updateCount();
}

function formValues() {
  return Object.fromEntries(new FormData($("#edit-form")));
}
const { saveEditorial, saveCredit, saveNote } = createManagementChanges(() => ({
  FIELDS,
  clone,
  data,
  lines,
  now,
  same,
  selected,
  setResource,
  tags,
  validURL,
  validatePackage,
  working,
}));

function download(value, name) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(value, null, 2) + "\n"], {
      type: "application/json",
    }),
  );
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$("#panel").addEventListener("submit", (event) => {
  event.preventDefault();
  try {
    const v = formValues();
    if (tab === "new") {
      v.modes = [
        ...$("#edit-form").querySelectorAll("[name=modes]:checked"),
      ].map((el) => el.value);
      saveNewWork(v);
    } else
      ({ editorial: saveEditorial, credits: saveCredit, notes: saveNote })[tab](
        v,
      );
    delete formCache[selected + ":" + tab];
    saveDraft();
    render();
    notice(
      "已加入修改清单并保存本机草稿。你可以继续编辑，或前往“审核与提交”。",
    );
  } catch (e) {
    notice(e.message, true);
  }
});
$("#panel").addEventListener("input", (event) => {
  if (event.target.name === "reason") {
    reason = event.target.value;
    saveDraft();
  } else {
    stashForm();
    saveDraft();
  }
});
$("#panel").addEventListener("change", () => {
  stashForm();
  saveDraft();
});
function navigate(next) {
  stashForm();
  tab = next;
  saveDraft();
  render();
  notice("");
}
$("#tabs").addEventListener("click", (e) => {
  const b = e.target.closest("[data-tab]");
  if (b) navigate(b.dataset.tab);
});
$("#work-list").addEventListener("click", (e) => {
  const b = e.target.closest("[data-work]");
  if (!b) return;
  stashForm();
  selected = b.dataset.work;
  saveDraft();
  render();
  notice("");
  history.replaceState({}, "", "#" + selected);
});
$("#search").addEventListener("input", () => {
  limit = 50;
  renderList();
});
$("#missing-only").addEventListener("change", () => {
  limit = 50;
  renderList();
});
$("#more").addEventListener("click", () => {
  limit += 50;
  renderList();
});
$("#export-draft").addEventListener("click", () => {
  stashForm();
  download(
    { schemaVersion: 1, package: getPackage(), formCache, selected, tab },
    "narrative-draft-" + now() + ".json",
  );
});
$("#import-draft").addEventListener("change", async (e) => {
  try {
    const f = e.target.files[0];
    if (!f) return;
    if (f.size > 2e6) throw Error("草稿超过2MB，请检查文件。");
    const imported = JSON.parse(await f.text());
    if (
      !confirm(
        "导入会替换当前浏览器中的管理台草稿。请确认已经导出需要保留的内容。",
      )
    )
      return;
    await hydrateDraft(imported);
    loadDraft(imported);
    saveDraft();
    render();
    notice("草稿已导入，数据库记录冲突检查通过。");
  } catch (err) {
    notice(err.message, true);
  } finally {
    e.target.value = "";
  }
});
$("#panel").addEventListener("click", (e) => {
  const b = e.target.closest("button");
  if (!b) return;
  try {
    if (b.dataset.editNew) {
      const bundle = resourceValue(working, "newWork", b.dataset.editNew);
      selected = "__new__";
      tab = "new";
      newWorkForm(bundle);
      $("#tabs").hidden = true;
      $("#work-heading").innerHTML = "<h2>修改新作草稿</h2>";
      return;
    }
    if (b.dataset.go) navigate(b.dataset.go);
    else if (b.dataset.removeCredit) {
      working.creators.credits = working.creators.credits.filter(
        (c) => c.id !== b.dataset.removeCredit,
      );
      for (const p of [...working.creators.people]) {
        const old = data.creators.people.find((x) => x.id === p.id);
        if (!working.creators.credits.some((c) => c.personId === p.id)) {
          working.creators.people = working.creators.people.filter(
            (x) => x.id !== p.id,
          );
          if (old) working.creators.people.push(clone(old));
        } else if (old)
          p.roles = [
            ...new Set([
              ...old.roles,
              ...working.creators.credits
                .filter((c) => c.personId === p.id)
                .map((c) => c.role),
            ]),
          ];
      }
      saveDraft();
      render();
    } else if (b.dataset.removeNote) {
      working.notes.works[selected].splice(Number(b.dataset.removeNote), 1);
      if (!working.notes.works[selected].length)
        delete working.notes.works[selected];
      saveDraft();
      render();
    } else if (b.id === "download-package") {
      download(getPackage(), "narrative-update-" + now() + ".json");
    } else if (b.id === "prepare-submit") {
      const p = getPackage(),
        errors = validatePackage(p);
      if (errors.length) throw Error(errors.join("；"));
      offerEditorialProposal($("#editorial-submit"), managementProposal(p));
      $("#submission-json").value = JSON.stringify(p);
      $("#workflow-link").href = WORKFLOW;
      $("#submit-dialog").showModal();
    } else if (
      b.id === "clear-draft" &&
      confirm(
        "清除当前浏览器的所有管理台草稿？已提交到 GitHub 的记录不会被删除。",
      )
    ) {
      working = clone(data);
      formCache = {};
      reason = "";
      saveDraft();
      render();
      notice("本机草稿已清除。");
    }
  } catch (err) {
    notice(err.message, true);
  }
});
$("#backup-draft").addEventListener("click", () =>
  download(
    JSON.parse(localStorage.getItem(KEY + "-conflict-backup")),
    "narrative-conflicted-draft-" + now() + ".json",
  ),
);
$("#copy-package").addEventListener("click", async () => {
  const box = $("#submission-json");
  try {
    await navigator.clipboard.writeText(box.value);
    $("#copy-package").textContent = "已复制更新包";
  } catch {
    box.focus();
    box.select();
    $("#copy-package").textContent = "请长按或 Ctrl+C 复制选中文字";
  }
});
window.addEventListener("beforeunload", (e) => {
  if (!storageOK) {
    e.preventDefault();
    e.returnValue = "";
  }
});
async function load() {
  try {
    const [directory, taxonomy] = await Promise.all([
      reader.directory("formal"),
      readReleaseJson("data/taxonomy.json"),
    ]);
    projectionInputs = directory.raw;
    data = {
      editorial: clone(directory.editorial),
      notes: { works: {} },
      creators: { people: [], credits: [], collaborations: [] },
      catalogue: directory.catalogue,
      baseline: { works: [] },
      games: clone(directory.raw.main),
      supplement: clone(directory.raw.supplement),
      taxonomy,
      coverage: directory.coverage,
    };
    working = clone(data);
    try {
      $("#backup-draft").hidden = !localStorage.getItem(
        KEY + "-conflict-backup",
      );
      const saved = localStorage.getItem(KEY);
      if (saved) {
        const draft = JSON.parse(saved);
        await hydrateDraft(draft);
        loadDraft(draft);
      }
    } catch (e) {
      notice(
        e.message + "。原草稿仍保留；可点击导出草稿备份后再重新编辑。",
        true,
      );
      $("#export-draft").disabled = false;
      try {
        const raw = localStorage.getItem(KEY);
        if (raw) {
          localStorage.setItem(KEY + "-conflict-backup", raw);
          $("#backup-draft").hidden = false;
        }
      } catch {
        storageOK = false;
      }
    }
    const hash = decodeURIComponent(location.hash.slice(1));
    if (data.games.works.some((w) => w.id === hash)) selected = hash;
    $("#new-work").disabled = false;
    $("#search").disabled = false;
    $("#export-draft").disabled = false;
    $("#save-status").textContent = "数据库已读取 · 草稿仅保存在当前浏览器";
    render();
    await restoreReleaseState();
  } catch (e) {
    notice("加载数据库失败：" + e.message + "。请刷新页面重试。", true);
    $("#save-status").textContent = "读取失败";
  }
}
load();

function reservedWorks() {
  return [
    ...working.games.works,
    ...data.coverage.companies.flatMap((c) => [
      ...(c.relatedGames || []),
      ...(c.dossierOnlyWorks || []),
    ]),
    ...data.supplement.works,
  ];
}

function saveNewWork(v) {
  if (!v.confirmed)
    throw Error("请核对新作品身份、收录范围和原作首批资料并勾选确认。");
  const bundle = makeNewWork(v, data.taxonomy);
  validateNewBundle(bundle);
  if (data.games.works.some((w) => w.id === bundle.work.id))
    throw Error("作品 ID 已存在于主库，请复用已有身份。");
  const duplicated = duplicateWorks(reservedWorks(), bundle.work);
  if (duplicated.length)
    throw Error(
      "名称与已有作品重复：" +
        duplicated
          .slice(0, 5)
          .map((w) => title(w) + "（" + w.id + "）")
          .join("、") +
        "。请先核实身份。",
    );
  if (
    reservedWorks().some((w) => w.id === bundle.work.id) &&
    !working.games.works.some((w) => w.id === bundle.work.id)
  )
    throw Error("该 ID 已用于专题或关联作品，请重新生成。");
  setResource(working, "newWork", bundle.work.id, bundle);
  delete formCache["__new__:new"];
  selected = bundle.work.id;
  tab = "profile";
}
$("#new-work").addEventListener("click", () => {
  stashForm();
  selected = "__new__";
  tab = "new";
  saveDraft();
  render();
  notice("");
});
$("#panel").addEventListener("input", (e) => {
  if (tab !== "new" || !["title", "originalTitle"].includes(e.target.name))
    return;
  const v = formValues(),
    matches = duplicateWorks(reservedWorks(), {
      id: v["work-id"],
      title: v.title,
      originalTitle: v.originalTitle,
    });
  $("#duplicate-hint").textContent = matches.length
    ? "可能已收录：" +
      matches
        .slice(0, 5)
        .map((w) => title(w) + " · " + w.id)
        .join("；")
    : "尚未发现同名作品；请同时检查别名和历史版本。";
});
$("#panel").addEventListener("change", (e) => {
  if (tab === "new" && e.target.name === "category") {
    $("[name=subcategory]").innerHTML = options(
      data.taxonomy.subcategories[e.target.value]
        .filter((x) => !["纯文本指令", "图文指令"].includes(x))
        .map((x) => [x, x]),
      "",
    );
    stashForm();
    saveDraft();
  }
});
$("#panel").addEventListener("click", (e) => {
  if (e.target.closest("[data-cancel-new]")) {
    stashForm();
    selected = "";
    tab = "profile";
    saveDraft();
    render();
  }
});

$("#panel").addEventListener("click", (e) => {
  if (e.target.closest("[data-retry-detail]")) {
    waitingKey = "";
    loadError = "";
    render();
  }
  if (e.target.closest("[data-cancel-detail]")) {
    scope.cancel();
    loadError = "读取已取消；草稿保留";
    render();
  }
});
