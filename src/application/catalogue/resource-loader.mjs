// An optional failure belongs to one resource; stale/aborted reads cannot publish state.
export function createResourceLoader(resources, { ready, failed }) {
  return function ensureResource(key, loader, apply, signal) {
    if (resources.has(key)) return;
    const entry = { status: "loading" };
    resources.set(key, entry);
    const stale = () => signal?.aborted || resources.get(key) !== entry;
    const discard = () => {
      if (resources.get(key) === entry) resources.delete(key);
    };
    Promise.resolve()
      .then(() => loader({ signal }))
      .then((value) => {
        if (stale()) {
          discard();
          return;
        }
        apply(value);
        resources.set(key, { status: "ready" });
        ready();
      })
      .catch((error) => {
        if (stale()) {
          discard();
          return;
        }
        resources.set(key, { status: "failed", error: error.message });
        failed();
      });
  };
}
