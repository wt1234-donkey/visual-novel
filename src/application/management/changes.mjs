// Presentation only: mutable catalogue/session state stays with the controller.
export function createManagementChanges(read) {
  function saveEditorial(v) {
    const {
      FIELDS,
      clone,
      data,
      lines,
      now,
      same,
      selected,
      tags,
      validatePackage,
      working,
    } = read();
    if (selected in data.baseline.works)
      throw Error("历史八部编目只读，请提交补充说明。");
    if (!v.confirmed) throw Error("请核对来源并勾选确认。");
    const before = working.editorial.works[selected] || {},
      r = clone(before);
    r.fieldEvidence ??= {};
    for (const [f] of FIELDS) {
      const value = f === "position" ? v[f].trim() : tags(v[f]);
      const evidence = {
        basis: v[f + "-basis"].trim(),
        evidenceText: v[f + "-excerpt"].trim(),
        sources: lines(v[f + "-sources"]),
        sourceFields: ["manualSourceReview"],
        verification: "manualSourceReview",
      };
      if (
        !same(value, before[f] ?? (f === "position" ? "" : [])) ||
        !same(
          [evidence.basis, evidence.evidenceText, evidence.sources],
          [
            before.fieldEvidence?.[f]?.basis || "",
            before.fieldEvidence?.[f]?.evidenceText || "",
            before.fieldEvidence?.[f]?.sources || [],
          ],
        )
      ) {
        if (value.length) {
          r[f] = value;
          r.fieldEvidence[f] = evidence;
        } else {
          delete r[f];
          delete r.fieldEvidence[f];
        }
      }
    }
    r.basis = v.basis.trim();
    r.sources = [
      ...new Set([
        ...lines(v.sources),
        ...FIELDS.flatMap(([f]) =>
          r[f]?.length ? r.fieldEvidence?.[f]?.sources || [] : [],
        ),
      ]),
    ];
    r.openQuestions = lines(v.questions);
    r.status = FIELDS.every(([f]) => r[f]?.length)
      ? "editorialObservation"
      : "partial";
    r.reviewedAt = now();
    r.evidenceStatus = "manualSourceReview";
    const p = {
      schemaVersion: 1,
      reason: "人工资料核对",
      operations: [{ resource: "editorial", key: selected, before, after: r }],
    };
    const errors = validatePackage(p);
    if (errors.length) throw Error(errors.join("；"));
    working.editorial.works[selected] = r;
  }

  function saveCredit(v) {
    const { clone, selected, setResource, validURL, working } = read();
    if (!v.confirmed) throw Error("请先核实职责并勾选确认。");
    const id = v.person || v["person-id"].trim();
    if (!/^[a-z0-9][a-z0-9_-]{1,79}$/.test(id))
      throw Error("请填写有效的个人 ID（2–80位英文小写、数字、连字符）。");
    let person = working.creators.people.find((p) => p.id === id);
    if (!person && (!v["person-name"].trim() || !v["person-id"].trim()))
      throw Error("新增个人须填写姓名和唯一 ID。");
    if (
      !person &&
      working.creators.people.some(
        (p) =>
          p.name.normalize("NFKC") ===
          v["person-name"].trim().normalize("NFKC"),
      )
    )
      throw Error("已有同名个人，请先复用现有身份或核对是否重名。");
    if (
      !/^[a-z0-9][a-z0-9_-]{1,119}$/.test(v["credit-id"]) ||
      working.creators.credits.some((c) => c.id === v["credit-id"])
    )
      throw Error("署名 ID 格式无效或已经存在。");
    if (
      !v.label.trim() ||
      !v["scope-label"].trim() ||
      !v.note.trim() ||
      !validURL(v.source)
    )
      throw Error("请填写实际署名、有效来源、适用范围及限定说明。");
    let scope = { type: v.scope };
    if (v.scope === "release") {
      if (
        !working.games.platformReleases.some(
          (r) => r.id === v.release && r.workId === selected,
        )
      )
        throw Error("请选择本作品的已有发行。");
      scope.releaseId = v.release;
    } else if (v.scope === "externalEdition") {
      if (
        !v.year ||
        !Number.isInteger(Number(v.year)) ||
        Number(v.year) <
          working.games.works.find((w) => w.id === selected).firstYear ||
        Number(v.year) > new Date().getFullYear() ||
        !v.platform.trim()
      )
        throw Error("请填写有效的后续产品年份与平台。");
      scope = {
        ...scope,
        year: Number(v.year),
        platform: v.platform.trim(),
        label: v["scope-label"].trim(),
      };
    } else scope.label = v["scope-label"].trim();
    person = person
      ? clone(person)
      : {
          id,
          name: v["person-name"].trim(),
          mark: { writer: "文", artist: "画", musician: "音" }[v.role],
          alias: v["person-alias"].trim(),
          roles: [],
        };
    person.roles = [...new Set([...person.roles, v.role])];
    setResource(working, "people", id, person);
    working.creators.credits.push({
      id: v["credit-id"],
      workId: selected,
      personId: id,
      role: v.role,
      label: v.label.trim(),
      source: v.source.trim(),
      note: v.note.trim(),
      status: "sourceReviewed",
      scopeLabel: v["scope-label"].trim(),
      scope,
    });
  }

  function saveNote(v) {
    const { selected, validURL, working } = read();
    if (!v.confirmed) throw Error("请核对来源并勾选确认。");
    if (
      !v.title.trim() ||
      v.text.trim().length < 10 ||
      !validURL(v.source) ||
      !v.dossier ||
      !/^[a-zA-Z0-9_-]+$/.test(v.anchor)
    )
      throw Error("请填写标题、至少10字正文、有效来源、相关专题和锚点。");
    const rows = working.notes.works[selected] || [];
    if (rows.some((n) => n.title === v.title.trim()))
      throw Error("已有同标题说明，请使用能区分具体结论的标题。");
    working.notes.works[selected] = [
      ...rows,
      {
        title: v.title.trim(),
        text: v.text.trim(),
        source: v.source.trim(),
        dossierId: v.dossier,
        anchor: v.anchor.trim(),
      },
    ];
  }
  return { saveEditorial, saveCredit, saveNote };
}
