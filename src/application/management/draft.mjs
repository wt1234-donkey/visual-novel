import {
  clone,
  same,
  resourceValue,
  setResource,
} from "../../../management-model.mjs";

// Validate against the current source before applying any local draft operation.
export function restoreManagementDraft(data, draft) {
  if (
    draft.schemaVersion !== 1 ||
    !draft.package ||
    !Array.isArray(draft.package.operations)
  )
    throw Error("不是有效的管理台草稿");
  const working = clone(data),
    conflicts = [];
  for (const op of draft.package.operations) {
    if (
      !["newWork", "editorial", "notes", "people", "credits"].includes(
        op.resource,
      ) ||
      typeof op.key !== "string" ||
      op.key === "__proto__" ||
      op.key === "constructor"
    )
      throw Error("草稿包含不支持的项目");
    if (op.resource === "newWork" && resourceValue(data, "newWork", op.key))
      conflicts.push(op.key);
    else if (!same(resourceValue(data, op.resource, op.key), op.before))
      conflicts.push(op.resource + "/" + op.key);
    else setResource(working, op.resource, op.key, op.after);
  }
  if (conflicts.length)
    throw Error(
      "数据库已变化，草稿未载入。冲突项目：" +
        conflicts.join("、") +
        "。请保留导出文件并重新核对，不要覆盖新资料。",
    );
  return {
    working,
    formCache: draft.formCache || {},
    reason: draft.package.reason || "",
    selected:
      draft.selected === "__new__"
        ? "__new__"
        : working.games.works.some((work) => work.id === draft.selected)
          ? draft.selected
          : "",
    tab: [
      "new",
      "profile",
      "editorial",
      "credits",
      "versions",
      "notes",
      "review",
    ].includes(draft.tab)
      ? draft.tab
      : "profile",
  };
}
