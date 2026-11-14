// Loading an editor has no DOM side effects. The caller owns selection and cancellation.
export async function readWorkEditorContext(
  workId,
  { reader, client, actor, signal, readJson },
) {
  const [directory, full, tax, validation, release] = await Promise.all([
    reader.directory("formal", { signal }),
    reader.formal(workId, "formal", { signal }),
    readJson("data/taxonomy.json"),
    reader.optional("validation", { signal }),
    reader.release(),
  ]);
  client.setSourceLease(directory.sourceLease);
  client.setCommandMode?.(release.saveMode || "legacy");
  const history = await (
    actor
      ? client.read({ workIds: [workId] })
      : directory.currentStateVersion === 1
        ? reader
            .current("formal", { workIds: [workId], signal })
            .then((store) => ({ sha: null, store }))
        : Promise.resolve({ sha: null, store: directory.raw.history })
  ).catch((loadError) => ({
    sha: null,
    store: { schemaVersion: 1, records: {} },
    loadError,
  }));
  return { directory, full, tax, validation, release, history };
}
