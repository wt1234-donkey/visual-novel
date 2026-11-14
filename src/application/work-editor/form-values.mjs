import { lines } from "../../../management-model.mjs";
import { CREATOR_NAME_FIELDS } from "../../../work-edit-model.mjs";

export function collectCreatorNames(values, current, selectedFields = {}) {
  return Object.fromEntries(
    Object.keys(CREATOR_NAME_FIELDS).map((key) => [
      key,
      selectedFields[key] ? current[key] : lines(String(values.get(key) || "")),
    ]),
  );
}
export function collectWorkValues(
  values,
  { current, names, selectedFields = {}, creatorsOnly = false },
) {
  if (creatorsOnly) return { ...current, ...names };
  const result = { ...names };
  for (const key of Object.keys(current)) {
    if (key in CREATOR_NAME_FIELDS) continue;
    if (selectedFields[key]) {
      result[key] = current[key];
      continue;
    }
    result[key] =
      key === "interactionModes"
        ? values.getAll(key)
        : ["titleAliases", "characters", "interactionSources"].includes(key)
          ? lines(String(values.get(key) || ""))
          : String(values.get(key) || "").trim();
  }
  for (const key of ["title", "originalTitle", "chineseTitle"])
    if (
      current[key] &&
      current[key] !== result[key] &&
      !result.titleAliases.includes(current[key])
    )
      result.titleAliases.push(current[key]);
  return result;
}
