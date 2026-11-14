import { createResourceLoader } from "./src/application/catalogue/resource-loader.mjs";
import { createDiscoveryQueries } from "./src/application/discovery/queries.mjs";
import { createDiscoveryViews } from "./src/features/discovery/views.mjs";
import { createOnDemandReader } from "./src/infrastructure/storage/on-demand-reader.mjs";
import { requestScope } from "./src/infrastructure/storage/async-read.mjs";
import {
  registerPageRecovery,
  restoreReleaseState,
} from "./src/features/release-recovery.mjs";
import "./release-runtime.mjs";
import { readReleaseJson } from "./src/infrastructure/storage/release-reader.mjs";
import {
  buildEffectiveCatalogue,
  mergeFormalDatasets,
} from "./src/domain/catalogue/effective.mjs";
import {
  createBasicWebIndex,
  createHomeSearch,
  normalizeBasicQuery,
  slotPage,
} from "./basic-catalogue-index.mjs?v=20261110-flex-tags";
import { applyWorkEdits } from "./work-edit-model.mjs?v=20261104-creators";
import { showLiveWorkEditor } from "./live-work-editor.mjs?v=20261109-editorial";
import { createEntityIndex } from "./entities.mjs";
import { normalize } from "./filter.mjs";
import {
  createAtlas,
  filterAtlas,
  metadataValues,
  creatorCredits,
  manualCreatorNames,
  creatorWorkIds,
  productionCredits,
  creditScope,
  sourceStatus,
  titleOf,
  CREATOR_ROLES,
  PENDING,
  MAKER_ROLES,
  narrativeState,
  narrativeCounts,
} from "./discovery-model.mjs?v=20261104-creators";
const root = document.getElementById("story-atlas"),
  view = root.querySelector("#sa-view");
const $ = (selector) => root.querySelector(selector);
const basicIndex = createBasicWebIndex(),
  findBasicPage = createHomeSearch(basicIndex);
let basicRenderVersion = 0;
const basicScope = requestScope();
const {
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
} = createDiscoveryViews(() => ({
  PAGE_SIZE,
  atlas,
  creatorCredits,
  creatorRows,
  creatorWorkIds,
  creditScope,
  evidenceResults,
  fields,
  manualCreatorNames,
  metadataValues,
  narrativeState,
  normalize,
  productionCredits,
  resourceNotice,
  resources,
  sourceStatus,
  state,
  titleOf,
}));

const fields = [
  ["position", "叙事定位"],
  ["style", "剧情风格"],
  ["theme", "故事题材"],
  ["structure", "叙事结构"],
  ["gameplay", "玩法"],
];
const state = {
  page: "discover",
  q: "",
  facets: Object.fromEntries(fields.map(([k]) => [k, ""])),
  legacy: {},
  sort: "default",
  cataloguing: "",
  listPage: 1,
  basicPage: 1,
  detail: null,
  detailTab: "profile",
  creditWork: "g030",
  creditQuery: "",
  creatorType: "all",
  creatorQ: "",
  creatorPage: 1,
  selected: null,
  researchTab: "topics",
  topicQ: "",
  topicKind: "",
  evidenceStatus: "all",
  evidencePage: 1,
  evidenceQ: "",
  releaseQ: "",
  releasePage: 1,
  evidence: null,
};
const PAGE_SIZE = 12;
let atlas, entityIndex, editSourceData;
const reader = createOnDemandReader(),
  detailScope = requestScope(),
  resources = new Map();
let activeDetail = "",
  detailSignal;
function rebuild() {
  atlas = createAtlas(
    atlas.data,
    atlas.catalogue,
    atlas.editorial,
    atlas.creators,
    atlas.notes,
  );
  entityIndex = createEntityIndex(
    atlas.data,
    atlas.catalogue.model,
    atlas.catalogue,
  );
  evidenceCache = null;
}
function resourceNotice(key, label) {
  const row = resources.get(key);
  return row?.status === "ready"
    ? ""
    : `<section class="sa-panel" role="status">${safe(label)}${row?.status === "failed" ? "暂不可用：" + safe(row.error) : "正在读取"}；目录仍可使用。${row?.status === "failed" ? button("重试", `data-retry-resource="${safe(key)}"`) : ""}</section>`;
}
const ensureResource = createResourceLoader(resources, {
  ready: () => {
    rebuild();
    render();
  },
  failed: () => render(),
});
function ensureView() {
  const id = state.detail || (state.page === "credits" ? state.creditWork : "");
  if (activeDetail !== id) {
    detailScope.cancel();
    activeDetail = id;
    detailSignal = id ? detailScope.start().signal : undefined;
    for (const [key, value] of resources)
      if (value.status === "loading" && key.includes(":"))
        resources.delete(key);
  }
  const signal = detailSignal;
  if (id) {
    ensureResource(
      "formal:" + id,
      (o) => reader.formal(id, "formal", o),
      (full) => {
        atlas.data.works = atlas.data.works.map((w) =>
          w.id === id ? full.work : w,
        );
        for (const field of ["contentVersions", "platformReleases"])
          atlas.data[field] = [
            ...atlas.data[field].filter((r) => r.workId !== id),
            ...full[field],
          ];
        for (const name of ["main", "supplement"])
          editSourceData[name].works = editSourceData[name].works.map((w) =>
            w.id === id ? full.source : w,
          );
      },
      signal,
    );
    ensureResource(
      "editorial:" + id,
      (o) => reader.formal(id, "editorial", o),
      (value) => {
        if (value) atlas.editorial.works[id] = value;
        else delete atlas.editorial.works[id];
      },
      signal,
    );
    ensureResource(
      "notes:" + id,
      (o) => reader.formal(id, "notes", o),
      (value) => {
        atlas.notes.works[id] = value || [];
      },
      signal,
    );
  }
  if (
    id ||
    ["credits", "creators"].includes(state.page) ||
    (state.page === "research" && state.researchTab === "evidence")
  )
    ensureResource(
      "creators",
      (o) => reader.optional("creators", o),
      (value) => (atlas.creators = value),
    );
  if (
    (id && state.detailTab === "sources") ||
    (state.page === "research" && state.researchTab === "evidence")
  )
    ensureResource(
      "organizations",
      (o) => reader.optional("organizations", o),
      (value) => (atlas.catalogue = value),
    );
  if (state.page === "research" && state.researchTab === "evidence")
    ensureResource(
      "all-editorial",
      () => readReleaseJson("data/discovery-editorial.json"),
      (value) => (atlas.editorial = value),
    );
  if (state.page === "research" && state.researchTab === "releases")
    ensureResource(
      "releases",
      (o) => reader.optional("releases", o),
      (value) => {
        atlas.data.platformReleases = value.platformReleases;
        atlas.data.contentVersions = value.contentVersions;
      },
    );
  if (id && resources.get("formal:" + id)?.status !== "ready") {
    view.innerHTML =
      button("← 返回目录", "data-back") +
      resourceNotice("formal:" + id, "作品详情");
    view.setAttribute("aria-busy", "false");
    return false;
  }
  return true;
}
registerPageRecovery({
  capture: () => structuredClone(state),
  restore: async (saved) => {
    for (const key of Object.keys(state))
      if (Object.hasOwn(saved, key)) state[key] = saved[key];
    render();
  },
});

const { matches, creatorRows, allEvidence } = createDiscoveryQueries(() => ({
  CREATOR_ROLES,
  atlas,
  creatorCredits,
  creatorWorkIds,
  creditScope,
  entityIndex,
  fields,
  filterAtlas,
  metadataValues,
  narrativeState,
  normalize,
  state,
  titleOf,
}));
function discoverResults() {
  const list = matches();
  state.listPage = Math.min(
    state.listPage,
    Math.max(1, Math.ceil(list.length / PAGE_SIZE)),
  );
  return `<div class="sa-toolbar"><p class="sa-count" aria-live="polite">${list.length} / ${atlas.data.works.length} 部作品</p><label class="sa-small sa-muted">排序 <select data-sort aria-label="作品排序">${[
    ["default", "档案顺序（示例在前）"],
    ["oldest", "首发：由早到晚"],
    ["newest", "首发：由近到远"],
    ["title", "名称排序"],
  ]
    .map(([v, l]) => option(v, l, state.sort))
    .join(
      "",
    )}</select></label></div>${cards(list.slice((state.listPage - 1) * PAGE_SIZE, state.listPage * PAGE_SIZE))}${pagination(list.length, state.listPage, "works")}`;
}
function mainBasicSection() {
  return '<section class="sa-panel" aria-label="统一基础作品检索"><h3>主库基础作品检索</h3><p role="status">正在读取基础作品索引…</p></section>';
}
async function updateBasicSection(scroll = false) {
  const host = $("#sa-basic-works"),
    version = ++basicRenderVersion,
    request = basicScope.start();
  if (!host) return;
  const query = normalizeBasicQuery(state.q),
    page = state.basicPage,
    size = 25;
  host.setAttribute("aria-busy", "true");
  try {
    const { home } = await basicIndex.meta();
    const result = query
      ? await findBasicPage(query, page, size, { signal: request.signal })
      : slotPage(home.total, page, size);
    if (version !== basicRenderVersion || host !== $("#sa-basic-works")) return;
    const details = await basicIndex.details("home", result.slots, {
      signal: request.signal,
    });
    if (version !== basicRenderVersion || host !== $("#sa-basic-works")) return;
    state.basicPage = result.page;
    const sample = result.slots.map((slot) => details.get(slot));
    host.innerHTML =
      '<section class="sa-panel" aria-label="统一基础作品检索"><div class="sa-heading"><h3>主库基础作品检索 · 已批量纳入网站</h3>' +
      status(home.total + " 部基础身份") +
      '</div><p class="sa-small sa-muted">本页直接检索基础身份库中尚未形成完整档案的条目。常规批次与完整档案同名同年的记录不重复展示，指定未去重导入的条目保留。</p>' +
      '<div class="sa-table-wrap"><table><thead><tr><th>作品及别名</th><th>首发年</th><th>玩法状态</th><th>关联线索</th><th>档案与来源</th></tr></thead><tbody>' +
      (sample
        .map(
          (w) =>
            "<tr><td>" +
            safe(w.title) +
            ((w.aliases || []).length
              ? '<div class="sa-small sa-muted">' +
                safe(w.aliases.slice(0, 3).join(" / ")) +
                "</div>"
              : "") +
            "</td><td>" +
            safe(w.firstYear ?? "年份待核") +
            "</td><td>" +
            safe(w.gameplay || "玩法待核") +
            "</td><td>" +
            safe(w.group || "来源待核") +
            "</td><td>" +
            status(
              w.mainPlacement === "promoted-dossier"
                ? "原专题关联"
                : "基础身份",
            ) +
            " " +
            textLink(w.source, "核对来源") +
            "</td></tr>",
        )
        .join("") ||
        '<tr><td colspan="5">没有符合当前关键词的基础记录</td></tr>') +
      "</tbody></table></div>" +
      pagination(result.total, result.page, "basic", size) +
      '<p class="sa-small sa-muted">当前搜索匹配 ' +
      result.total +
      " 部；与完整档案按身份或同名同年排除 " +
      home.excluded +
      ' 条。<a href="minimal-adv-rpg.html">完整基础索引及来源</a> · <a href="data/main-adv-rpg-works-20261031.json">原始基础数据 JSON</a></p></section>';
    if (scroll) host.scrollIntoView({ block: "start" });
  } catch (error) {
    if (version !== basicRenderVersion || host !== $("#sa-basic-works")) return;
    host.innerHTML =
      '<section class="sa-panel"><h3>基础作品索引暂不可用</h3><p role="alert">' +
      safe(error.message) +
      "</p>" +
      button("重试加载基础索引", "data-retry-basic") +
      ' <a href="minimal-adv-rpg.html">打开基础身份库</a></section>';
  } finally {
    if (version === basicRenderVersion) host.setAttribute("aria-busy", "false");
  }
}
function renderDiscover() {
  if (state.detail) {
    renderDetail();
    return;
  }
  const active = Object.entries(state.legacy).filter(([, v]) => v);
  view.innerHTML =
    heading(
      "DISCOVER / 作品发现",
      "下一段故事，从这里开始。",
      "按叙事体验寻找作品，查看主要角色、创作人员与版本差异。",
    ) +
    '<section class="sa-panel" aria-label="双层作品库入口"><div class="sa-heading"><h3>双层作品库：广泛收录与精选叙事</h3></div><p class="sa-small sa-muted">基础作品库优先保留独立作品名、原作年和来源；精选叙事库依据题材、结构与推荐理由逐步审核。完整档案不自动等于推荐，未精选也不表示作品质量不足。</p><div class="sa-legend"><a href="minimal-adv-rpg.html">浏览完整基础作品索引 →</a><a href="curated.html">查看精选叙事初选 →</a></div></section>' +
    search(state.q, "搜索作品、角色、题材或创作者…", "works") +
    (active.length
      ? `<div class="sa-active-filter">${status("已应用旧链接中的参与／发行筛选")}<button type="button" class="sa-link-button" data-reset>清除所有条件</button></div>`
      : "") +
    `<div class="sa-discover"><aside class="sa-filters"><div class="sa-filter-title"><strong>内容筛选</strong><button type="button" class="sa-link-button" data-reset>清除</button></div>${fields.map(([key, label]) => `<label class="sa-field">${label}<select data-filter="${key}" data-lazy-options>${option("", "全部", state.facets[key])}${state.facets[key] && state.facets[key] !== PENDING ? option(state.facets[key], state.facets[key], state.facets[key]) : ""}${key !== "gameplay" ? option(PENDING, "待编目", state.facets[key]) : ""}</select></label>`).join("")}<label class="sa-field">编目进度<select data-cataloguing>${[
      ["", "全部进度"],
      ["complete", "四项已编目"],
      ["partial", "已有部分编目"],
      ["missing", "尚未编目"],
    ]
      .map(([v, l]) => option(v, l, state.cataloguing))
      .join(
        "",
      )}</select></label><p class="sa-filter-note">按作品统计：四项已编目 ${narrativeCounts(atlas).complete} / ${atlas.data.works.length} 部，部分 ${narrativeCounts(atlas).partial} 部，尚未编目 ${narrativeCounts(atlas).missing} 部。标签为编辑归纳，具体依据与仍待补证的问题见作品档案。<br><a href="data/narrative-cataloguing-20261030.md" target="_blank" rel="noopener">本轮审核与缺口清单 ↗</a></p></aside><section id="sa-work-results">${discoverResults()}</section></div><div id="sa-basic-works">${mainBasicSection()}</div>`;
  updateBasicSection();
}

function renderDetail() {
  const w = atlas.works.get(state.detail);
  if (!w) {
    state.detail = null;
    renderDiscover();
    return;
  }
  view.innerHTML = `<button type="button" data-back class="sa-link-button">← 返回作品发现</button><div class="sa-detail-top"><div class="sa-detail-hero">${book(w)}<div><div class="sa-eyebrow">WORK DOSSIER / ${safe(w.id)}</div><h1>${safe(titleOf(w))}</h1><p class="sa-small sa-muted">${safe(w.originalTitle)}${w.chineseTitleType === "站内编辑译名" ? " · 中文名为站内编辑译名" : ""}</p><p class="sa-lead">${w.firstYear} · ${safe(brandLabel(w))}</p></div></div></div><div class="sa-lineup">${button("添加剧作／美术／音乐", `data-add-creators="${w.id}"`)}${button("编辑作品／回撤最近3次修改", `data-edit-work="${w.id}"`)}</div>${detailTabs()}${state.detailTab === "profile" ? profile(w) : state.detailTab === "versions" ? versions(w) : sources(w)}`;
}

function renderCredits() {
  if (resources.get("creators")?.status !== "ready") {
    view.innerHTML =
      creditWorkPicker() + resourceNotice("creators", "个人署名");
    return;
  }
  const w = atlas.works.get(state.creditWork) || atlas.data.works[0];
  state.creditWork = w.id;
  view.innerHTML =
    heading(
      "CREATION / 作品创作关系",
      "一部作品，三条创作线索。",
      "从作品出发，查看谁写下故事、谁塑造画面、谁创作音乐。",
    ) +
    creditWorkPicker() +
    `<div class="sa-detail-top"><h2>${safe(titleOf(w))}</h2><p class="sa-small sa-muted">${safe(w.originalTitle)}</p>${button("添加剧作／美术／音乐", `data-add-creators="${w.id}"`)}</div><div class="sa-role-grid">${Object.entries(
      CREATOR_ROLES,
    )
      .map(([role, label], i) => {
        const rows = creatorCredits(atlas, w.id, role);
        return `<section class="sa-panel"><div class="sa-role-head"><span>${["Words", "Art", "Music"][i]}</span><h3>${label}</h3></div>${rows.length || manualCreatorNames(w, role).length ? rows.map((c) => `<article class="sa-credit"><button type="button" class="sa-credit-name sa-link-button" data-person="${c.personId}">${safe(atlas.people.get(c.personId).name)}</button><p class="sa-credit-role">${safe(c.label)}</p>${status(creditScope(atlas, c), "good")}<button type="button" class="sa-link-button" data-evidence="${c.id}">查看署名证据 ↗</button></article>`).join("") + manualCreditHTML(w, role) : `<article class="sa-credit"><span class="sa-credit-name sa-muted">尚未添加</span><p class="sa-credit-role">可直接添加姓名</p>${button("添加姓名", `data-add-creators="${w.id}"`)}</article>`}</section>`;
      })
      .join(
        "",
      )}</div><div class="sa-soft">支持直接补充姓名，无需依据。手动添加的姓名可点击搜索相关作品；已登记署名可查看具体职责和适用版次。</div><div id="sa-evidence-slot">${creditEvidence()}</div><div class="sa-lineup" style="margin-top:18px">${button("查看作品档案", `data-work="${w.id}"`)}${button("按创作者寻找作品", "data-to-creators", "sa-primary")}</div>`;
}

function renderCreators() {
  if (resources.get("creators")?.status !== "ready") {
    view.innerHTML = resourceNotice("creators", "创作者");
    return;
  }
  view.innerHTML =
    heading(
      "PEOPLE & COLLECTIVES / 创作者与品牌",
      "沿着喜欢的创作，继续寻找。",
      "按制作品牌、创作团队、编剧、原画师、音乐创作者及合作关系检索。",
    ) +
    search(
      state.creatorQ,
      "搜索品牌、团队、编剧、画师或音乐创作者…",
      "creators",
    ) +
    `<nav class="sa-chips" aria-label="创作者类型">${[
      ["all", "全部"],
      ["brand", "制作品牌"],
      ["team", "创作团队"],
      ["company", "制作公司"],
      ["writer", "个人编剧"],
      ["artist", "原画师"],
      ["musician", "音乐创作者"],
      ["cooperation", "长期合作关系"],
    ]
      .map(
        ([id, label]) =>
          `<button type="button" class="sa-chip" aria-pressed="${state.creatorType === id}" data-creator-type="${id}">${label}</button>`,
      )
      .join(
        "",
      )}</nav><div id="sa-creator-results">${creatorCards()}</div><div id="sa-selected-creator">${selectedCreator()}</div><p class="sa-lead sa-small">合作次数不自动证明正式团队或隶属关系；缺少跨年资料时只标为合作线索。</p>`;
}

let evidenceCache;
function evidenceResults() {
  const q = normalize(state.evidenceQ);
  const rows = (evidenceCache ??= allEvidence()).filter(
    (r) =>
      (state.evidenceStatus === "all" || r.kind === state.evidenceStatus) &&
      (!q || normalize([r.title, r.label, r.note].join(" ")).includes(q)),
  );
  state.evidencePage = Math.min(
    state.evidencePage,
    Math.max(1, Math.ceil(rows.length / 12)),
  );
  return `<p class="sa-count" aria-live="polite">${rows.length} 条署名、证据与待核事项；不等于作品总数</p><section class="sa-panel" style="margin-top:12px">${
    rows
      .slice((state.evidencePage - 1) * 12, state.evidencePage * 12)
      .map(
        (r) =>
          `<article class="sa-list-row"><div><h3>${safe(r.title)}</h3><p class="sa-small">${safe(r.label)}</p><p class="sa-small sa-muted">${safe(r.note)}</p><div style="margin-top:5px">${status({ reviewed: "来源已核", inherited: "沿用既有证据", pending: "待核实", editorial: "编辑归纳" }[r.kind], r.kind === "reviewed" ? "good" : r.kind === "pending" ? "pending" : "")}</div></div><div>${r.source ? textLink(r.source, "依据") : button("查看档案", `data-work="${r.workId}"`)}</div></article>`,
      )
      .join("") || '<p class="sa-muted">没有匹配记录</p>'
  }</section>${pagination(rows.length, state.evidencePage, "evidence")}`;
}

function applyTopicFilters() {
  const holder = $("#sa-topics");
  if (!holder) return;
  let count = 0;
  const q = normalize(state.topicQ);
  for (const item of holder.querySelectorAll(".dossier-item")) {
    const ok =
      (!q || normalize(item.textContent).includes(q)) &&
      (!state.topicKind || item.dataset.kind === state.topicKind);
    item.hidden = !ok;
    if (ok) count++;
  }
  for (const period of holder.querySelectorAll(".dossier-period"))
    period.hidden = ![...period.querySelectorAll(".dossier-item")].some(
      (el) => !el.hidden,
    );
  holder.querySelector("#dossier-filter-count").textContent =
    `${count} / ${atlas.catalogue.model.dossiers.length} 个专题`;
  for (const b of holder.querySelectorAll("[data-dossier-kind]"))
    b.setAttribute(
      "aria-pressed",
      String(b.dataset.dossierKind === state.topicKind),
    );
}
function renderResearch() {
  view.innerHTML =
    heading(
      "ARCHIVE / 历史与考据",
      "让每条记录，都有来处。",
      "现有厂商专题、组织变迁、发行历史及证据状态，作为深入研究入口。",
    ) +
    researchTabs() +
    '<div id="sa-research-body">' +
    researchBody() +
    "</div>";
  if (state.researchTab === "topics") {
    $("#sa-topics").append($("#sa-dossier-template").content.cloneNode(true));
    applyTopicFilters();
  }
}
function render() {
  if (!atlas || !ensureView()) return;
  root
    .querySelectorAll("[data-page]")
    .forEach((b) =>
      b.setAttribute("aria-pressed", String(b.dataset.page === state.page)),
    );
  ({
    discover: renderDiscover,
    credits: renderCredits,
    creators: renderCreators,
    research: renderResearch,
  })[state.page]();
  view.setAttribute("aria-busy", "false");
}
function currentHash() {
  if (state.page === "discover")
    return state.detail
      ? `work/${encodeURIComponent(state.detail)}/${state.detailTab}`
      : "discover";
  if (state.page === "credits")
    return `credits/${encodeURIComponent(state.creditWork)}`;
  if (state.page === "creators")
    return state.selected ? "creator/" + state.selected : "creators";
  return "research/" + state.researchTab;
}
function saveURL(push = false) {
  const url = new URL(location.href);
  url.hash = currentHash();
  if (state.q) url.searchParams.set("query", state.q);
  else url.searchParams.delete("query");
  if (state.cataloguing) url.searchParams.set("cataloguing", state.cataloguing);
  else url.searchParams.delete("cataloguing");
  for (const [k, v] of Object.entries(state.facets)) {
    if (v) url.searchParams.set(k, v);
    else url.searchParams.delete(k);
  }
  if (state.sort !== "default") url.searchParams.set("sort", state.sort);
  else url.searchParams.delete("sort");
  for (const k of [
    "brand",
    "developer",
    "publisher",
    "participant",
    "participantRole",
    "dossier",
    "dossierRelation",
    "includeAffiliates",
  ]) {
    if (state.legacy[k]) url.searchParams.set(k, String(state.legacy[k]));
    else url.searchParams.delete(k);
  }
  history[push ? "pushState" : "replaceState"]({}, "", url);
}
function navigate() {
  saveURL(true);
  render();
  $("#catalogue").scrollIntoView({ block: "start" });
}
function showWork(id, tab = "profile") {
  state.page = "discover";
  state.detail = id;
  state.detailTab = tab;
  state.evidence = null;
  navigate();
}
function route() {
  const params = new URLSearchParams(location.search);
  state.q = params.get("query") || "";
  for (const [k] of fields) state.facets[k] = params.get(k) || "";
  state.sort = params.get("sort") || "default";
  state.cataloguing = ["complete", "partial", "missing"].includes(
    params.get("cataloguing"),
  )
    ? params.get("cataloguing")
    : "";
  state.legacy = Object.fromEntries(
    [
      "brand",
      "developer",
      "publisher",
      "participant",
      "participantRole",
      "dossier",
      "dossierRelation",
    ].map((k) => [k, params.get(k) || ""]),
  );
  state.legacy.includeAffiliates = params.get("includeAffiliates") === "true";
  state.detail = null;
  const raw = decodeURIComponent(location.hash.slice(1));
  const [name, id, tab] = raw.split("/");
  if (["interaction-guide", "method"].includes(name)) {
    location.replace("catalogue.html#" + name);
    return;
  }
  if (name === "work" && atlas.works.has(id)) {
    state.page = "discover";
    state.detail = id;
    state.detailTab = ["profile", "versions", "sources"].includes(tab)
      ? tab
      : "profile";
  } else if (atlas.works.has(raw)) {
    state.page = "discover";
    state.detail = raw;
    state.detailTab = "profile";
  } else if (name === "credits") {
    state.page = "credits";
    if (atlas.works.has(id)) state.creditWork = id;
  } else if (name === "creators" || name === "creator") {
    state.page = "creators";
    state.selected = name === "creator" ? id : null;
  } else if (name === "research") {
    state.page = "research";
    state.researchTab = [
      "topics",
      "organizations",
      "releases",
      "evidence",
    ].includes(id)
      ? id
      : "topics";
  } else if (name === "company-dossiers") {
    state.page = "research";
    state.researchTab = "topics";
  } else {
    state.page = "discover";
  }
  render();
}
root.addEventListener("click", (event) => {
  const b = event.target.closest("button");
  if (!b || !root.contains(b)) return;
  if (b.dataset.retryResource) {
    resources.delete(b.dataset.retryResource);
    render();
    return;
  }
  if (b.hasAttribute("data-retry")) {
    load();
    return;
  }
  if (b.hasAttribute("data-retry-basic")) {
    updateBasicSection();
    return;
  }
  if (!atlas) return;
  if (b.dataset.editWork) {
    showLiveWorkEditor(b.dataset.editWork);
    return;
  }
  if (b.dataset.addCreators) {
    showLiveWorkEditor(b.dataset.addCreators, { creatorsOnly: true });
    return;
  }
  if (b.dataset.creatorName) {
    state.page = "discover";
    state.detail = null;
    state.q = b.dataset.creatorName;
    state.facets = Object.fromEntries(fields.map(([k]) => [k, ""]));
    state.legacy = {};
    state.cataloguing = "";
    state.listPage = 1;
    navigate();
    return;
  }
  if (b.dataset.page) {
    state.page = b.dataset.page;
    state.detail = null;
    state.evidence = null;
    state.selected = null;
    navigate();
  } else if (b.dataset.work) showWork(b.dataset.work);
  else if (b.dataset.versionWork) showWork(b.dataset.versionWork, "versions");
  else if (b.hasAttribute("data-back")) {
    state.detail = null;
    navigate();
  } else if (b.dataset.detailTab) {
    state.detailTab = b.dataset.detailTab;
    navigate();
  } else if (b.dataset.openCredits) {
    state.page = "credits";
    state.creditWork = b.dataset.openCredits;
    state.evidence = null;
    navigate();
  } else if (b.hasAttribute("data-to-creators")) {
    state.page = "creators";
    navigate();
  } else if (b.dataset.evidence) {
    state.evidence =
      state.evidence === b.dataset.evidence ? null : b.dataset.evidence;
    $("#sa-evidence-slot").innerHTML = creditEvidence();
  } else if (b.hasAttribute("data-close-evidence")) {
    state.evidence = null;
    $("#sa-evidence-slot").innerHTML = "";
  } else if (b.dataset.person) {
    state.page = "creators";
    state.creatorType = "all";
    state.creatorQ = "";
    state.selected = "person:" + b.dataset.person;
    state.selectedPage = 1;
    navigate();
    $("#sa-selected-creator").scrollIntoView({ block: "start" });
  } else if (b.dataset.creatorType) {
    state.creatorType = b.dataset.creatorType;
    state.creatorPage = 1;
    state.selected = null;
    render();
  } else if (b.dataset.selectCreator) {
    state.selected = b.dataset.selectCreator;
    state.selectedPage = 1;
    saveURL(true);
    $("#sa-selected-creator").innerHTML = selectedCreator();
    $("#sa-selected-creator").scrollIntoView({ block: "start" });
  } else if (b.hasAttribute("data-close-creator")) {
    state.selected = null;
    saveURL();
    $("#sa-selected-creator").innerHTML = "";
  } else if (b.dataset.researchTab) {
    state.researchTab = b.dataset.researchTab;
    navigate();
  } else if (b.hasAttribute("data-dossier-kind")) {
    state.topicKind = b.dataset.dossierKind;
    applyTopicFilters();
  } else if (b.hasAttribute("data-reset")) {
    state.q = "";
    Object.keys(state.facets).forEach((k) => (state.facets[k] = ""));
    state.legacy = {};
    state.sort = "default";
    state.cataloguing = "";
    state.listPage = 1;
    state.basicPage = 1;
    saveURL();
    render();
  } else if (b.hasAttribute("data-open-advanced")) {
    location.href = "catalogue.html" + location.search;
  } else if (b.dataset.pager) {
    const map = {
      works: "listPage",
      creators: "creatorPage",
      selected: "selectedPage",
      basic: "basicPage",
      releases: "releasePage",
      evidence: "evidencePage",
    };
    state[map[b.dataset.pager]] += Number(b.dataset.step);
    if (b.dataset.pager === "basic") {
      updateBasicSection(true);
    } else if (b.dataset.pager === "works") {
      $("#sa-work-results").innerHTML = discoverResults();
      $("#sa-work-results").scrollIntoView({ block: "start" });
    } else if (b.dataset.pager === "creators") {
      $("#sa-creator-results").innerHTML = creatorCards();
      $("#sa-creator-results").scrollIntoView({ block: "start" });
    } else if (b.dataset.pager === "selected") {
      $("#sa-selected-creator").innerHTML = selectedCreator();
      $("#sa-selected-creator").scrollIntoView({ block: "start" });
    } else if (b.dataset.pager === "releases") {
      $("#sa-release-results").innerHTML = releaseResults();
      $("#sa-release-results").scrollIntoView({ block: "start" });
    } else {
      $("#sa-evidence-results").innerHTML = evidenceResults();
      $("#sa-evidence-results").scrollIntoView({ block: "start" });
    }
  }
});
function populateFacet(event) {
  const select = event.target.closest?.("select[data-lazy-options]");
  if (!select || !atlas) return;
  const key = select.dataset.filter,
    current = select.value,
    values = [
      ...new Set(
        atlas.data.works.flatMap((w) => metadataValues(atlas, w, key)),
      ),
    ].sort((a, b) => a.localeCompare(b, "zh"));
  select.innerHTML =
    option("", "全部", current) +
    values.map((v) => option(v, v, current)).join("") +
    (key !== "gameplay" ? option(PENDING, "待编目", current) : "");
  select.removeAttribute("data-lazy-options");
}
// Populate before the native picker opens; keyboard and assistive focus use
// the same full value set, without constructing thousands of idle DOM nodes.
root.addEventListener("pointerdown", populateFacet);
root.addEventListener("focusin", populateFacet);
root.addEventListener("input", (event) => {
  const t = event.target,
    type = t.dataset.search;
  if (!atlas) return;
  if (type === "works") {
    state.q = t.value;
    state.listPage = 1;
    state.basicPage = 1;
    saveURL();
    $("#sa-work-results").innerHTML = discoverResults();
    updateBasicSection();
  } else if (type === "credit-work") {
    state.creditQuery = t.value;
    $("[data-credit-work]").innerHTML = creditWorkOptions();
  } else if (type === "creators") {
    state.creatorQ = t.value;
    state.creatorPage = 1;
    state.selected = null;
    $("#sa-creator-results").innerHTML = creatorCards();
    $("#sa-selected-creator").innerHTML = "";
  } else if (type === "topics") {
    state.topicQ = t.value;
    applyTopicFilters();
  } else if (type === "releases") {
    state.releaseQ = t.value;
    state.releasePage = 1;
    $("#sa-release-results").innerHTML = releaseResults();
  } else if (type === "evidence") {
    state.evidenceQ = t.value;
    state.evidencePage = 1;
    $("#sa-evidence-results").innerHTML = evidenceResults();
  }
});
root.addEventListener("change", (event) => {
  const t = event.target;
  if (!atlas) return;
  if (t.hasAttribute("data-cataloguing")) {
    state.cataloguing = t.value;
    state.listPage = 1;
    saveURL();
    $("#sa-work-results").innerHTML = discoverResults();
  } else if (t.dataset.filter) {
    state.facets[t.dataset.filter] = t.value;
    state.listPage = 1;
    saveURL();
    $("#sa-work-results").innerHTML = discoverResults();
  } else if (t.hasAttribute("data-sort")) {
    state.sort = t.value;
    state.listPage = 1;
    saveURL();
    $("#sa-work-results").innerHTML = discoverResults();
  } else if (t.hasAttribute("data-credit-work")) {
    state.creditWork = t.value;
    state.evidence = null;
    saveURL();
    render();
  } else if (t.hasAttribute("data-status")) {
    state.evidenceStatus = t.value;
    state.evidencePage = 1;
    $("#sa-evidence-results").innerHTML = evidenceResults();
  }
});
window.addEventListener("popstate", () => atlas && route());
window.addEventListener("hashchange", () => atlas && route());
async function load() {
  view.setAttribute("aria-busy", "true");
  try {
    const directory = await reader.directory("formal");
    editSourceData = structuredClone(directory.raw);
    const edited = directory.data,
      catalogue = directory.catalogue;
    atlas = createAtlas(
      edited,
      catalogue,
      directory.editorial,
      { people: [], credits: [], collaborations: [] },
      { works: {} },
    );
    entityIndex = createEntityIndex(edited, catalogue.model, catalogue);
    $("#sa-total-note").textContent =
      `${edited.works.length} 部作品 · ${edited.contentVersions.length} 个内容版本 · ${catalogue.model.dossiers.length} 个历史专题`;
    route();
    await restoreReleaseState();
    const editId = new URLSearchParams(location.search).get("edit");
    if (editId && atlas.works.has(editId)) showLiveWorkEditor(editId);
  } catch (error) {
    view.setAttribute("aria-busy", "false");
    view.innerHTML =
      '<div class="sa-empty" role="alert"><h2>作品档案加载失败</h2><p>请刷新重试，或使用高级检索与历史专题。</p><p class="sa-small">' +
      safe(error.message) +
      "</p>" +
      button("重试加载", "data-retry") +
      ' <a href="catalogue.html">高级检索</a></div>';
    console.error(error);
  }
}
load();

window.addEventListener("catalogue-work-edit", (event) => {
  if (!atlas || !editSourceData) return;
  const data = mergeFormalDatasets(
    buildEffectiveCatalogue({
      ...editSourceData,
      history: {
        schemaVersion: 1,
        records: { ...editSourceData.history.records, ...event.detail.records },
      },
    }),
  );
  atlas = createAtlas(
    data,
    atlas.catalogue,
    atlas.editorial,
    atlas.creators,
    atlas.notes,
  );
  entityIndex = createEntityIndex(data, atlas.catalogue.model, atlas.catalogue);
  evidenceCache = null;
  render();
});
