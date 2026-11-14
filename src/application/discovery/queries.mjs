// Presentation only: mutable catalogue/session state stays with the controller.
export function createDiscoveryQueries(read) {
  function matches() {
    const { atlas, entityIndex, filterAtlas, state } = read();
    return filterAtlas(
      atlas,
      {
        query: state.q,
        facets: state.facets,
        sort: state.sort,
        cataloguing: state.cataloguing,
        legacy: state.legacy,
      },
      entityIndex,
    );
  }

  function creatorRows() {
    const { CREATOR_ROLES, atlas, creatorWorkIds, normalize, state } = read();
    const result = [];
    const t = state.creatorType;
    for (const e of atlas.entities.values()) {
      const kind = e.type;
      const ids = creatorWorkIds(atlas, "entity", e.id);
      if (
        !["brand", "team"].includes(kind) &&
        !(kind === "company" && ids.size)
      )
        continue;
      if (t !== "all" && t !== kind) continue;
      result.push({
        ...e,
        kind: "entity",
        type: kind,
        workIds: ids,
        label: atlas.catalogue.model.typeLabels[kind],
        mark: e.name.slice(0, 1),
        desc: ids.size
          ? "有具名制作职责关联"
          : "制作职责待核，不由发行关系推导",
      });
    }
    for (const p of atlas.people.values()) {
      if (t !== "all" && !p.roles.includes(t)) continue;
      result.push({
        ...p,
        kind: "person",
        workIds: creatorWorkIds(
          atlas,
          "person",
          p.id,
          ["writer", "artist", "musician"].includes(t) ? t : "",
        ),
        label: p.roles.map((r) => CREATOR_ROLES[r]).join(" / "),
        aliases: [p.alias],
        desc: "署名按来源与适用版次记录",
      });
    }
    if (t === "all" || t === "cooperation")
      for (const c of atlas.creators.collaborations)
        result.push({
          ...c,
          kind: "cooperation",
          mark: "×",
          workIds: creatorWorkIds(atlas, "cooperation", c.id),
          label: "长期合作候选",
          desc: "跨作品共同署名线索，尚未认定正式团队",
        });
    const q = normalize(state.creatorQ);
    return result
      .filter(
        (e) =>
          !q ||
          normalize([e.name, ...(e.aliases || []), e.desc].join(" ")).includes(
            q,
          ),
      )
      .sort(
        (a, b) =>
          b.workIds.size - a.workIds.size || a.name.localeCompare(b.name, "zh"),
      );
  }

  function allEvidence() {
    const {
      CREATOR_ROLES,
      atlas,
      creatorCredits,
      creditScope,
      fields,
      metadataValues,
      narrativeState,
      titleOf,
    } = read();
    const rows = atlas.catalogue.credits.map((c) => ({
      kind:
        c.status === "sourceReviewed"
          ? "reviewed"
          : ["existingCredit", "existingDossier", "existingEvidence"].includes(
                c.status,
              )
            ? "inherited"
            : "pending",
      title:
        titleOf(atlas.works.get(c.workId)) +
        " · " +
        (atlas.entities.get(c.entityId)?.name || c.entityId),
      label: atlas.catalogue.model.roleLabels[c.role] || c.role,
      note:
        (c.targetType === "work"
          ? "原作／作品"
          : c.targetType === "content"
            ? "对应内容版本"
            : "对应平台发行") + (c.note ? " · " + c.note : ""),
      source: c.source,
      workId: c.workId,
    }));
    for (const c of atlas.creators.credits)
      rows.push({
        kind: "reviewed",
        title:
          titleOf(atlas.works.get(c.workId)) +
          " · " +
          atlas.people.get(c.personId).name,
        label: c.label,
        note: creditScope(atlas, c) + " · " + c.note,
        source: c.source,
        workId: c.workId,
      });
    for (const w of atlas.data.works) {
      const missing = Object.entries(CREATOR_ROLES)
        .filter(([role]) => !creatorCredits(atlas, w.id, role).length)
        .map(([, l]) => l);
      if (missing.length)
        rows.push({
          kind: "pending",
          title: titleOf(w),
          label: "个人创作署名待核",
          note: missing.join(" / ") + "：缺少已登记的游戏版署名证据。",
          source: null,
          workId: w.id,
        });
      const edit = atlas.editorial.works[w.id];
      if (narrativeState(atlas, w) !== "complete")
        rows.push({
          kind: "pending",
          title: titleOf(w),
          label: "叙事信息待补证",
          note: fields
            .filter(
              ([k]) => k !== "gameplay" && !metadataValues(atlas, w, k).length,
            )
            .map(([, l]) => l)
            .join(" / "),
          source: null,
          workId: w.id,
        });
      if (edit)
        rows.push({
          kind: "editorial",
          title: titleOf(w),
          label: "叙事标签 · 编辑归纳",
          note: edit.basis,
          source: edit.sources[0],
          workId: w.id,
        });
    }
    return rows;
  }
  return { matches, creatorRows, allEvidence };
}
