// Isolated disaster drill: no Git, source shards, credentials or write promotion.
import {
  readFileSync,
  writeFileSync,
  mkdirSync,
  existsSync,
  rmSync,
} from "node:fs";
import { resolve, join, dirname } from "node:path";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";
import {
  publishAuditLedger,
  restoreAuditKind,
  buildAuditLedger,
  verifyAuditGraph,
} from "../src/infrastructure/filesystem/audit-ledger.mjs";
import { AUDIT_PATH, AUDIT_SOURCES } from "../src/domain/audit/events.mjs";
import { journalKey } from "../src/domain/catalogue/journal.mjs";
export async function verifyArchiveRecovery(source, output) {
  source = resolve(source);
  output = resolve(output);
  if (
    output === source ||
    output.startsWith(source + "/") ||
    existsSync(output)
  )
    throw Error("恢复演练必须使用源码以外的全新隔离目录");
  mkdirSync(output, { recursive: true });
  const published = await publishAuditLedger(source, output);
  if (!published) throw Error("缺少独立审计归档");
  const manifest = JSON.parse(
      readFileSync(join(output, published.pointer.root.path)),
    ),
    kinds = {};
  for (const kind of Object.keys(manifest.kinds)) {
    const store = await restoreAuditKind(output, published.pointer.root, kind),
      logicalHash = createHash("sha256")
        .update(journalKey(store))
        .digest("hex");
    if (logicalHash !== manifest.kinds[kind].logicalHash)
      throw Error("隔离恢复摘要不一致");
    const path = join(output, AUDIT_SOURCES[kind]);
    mkdirSync(dirname(path), { recursive: true });
    writeFileSync(path, JSON.stringify(store) + "\n");
    kinds[kind] = {
      events: manifest.kinds[kind].eventCount,
      logicalHash,
      recovered: true,
    };
  }
  // Rebuild independently from restored logical aggregates, not old index files.
  rmSync(join(output, "data/audit-ledger"), { recursive: true });
  const rebuilt = await buildAuditLedger(output);
  await verifyAuditGraph(output, rebuilt.pointer.root);
  for (const kind of Object.keys(kinds)) {
    const store = await restoreAuditKind(output, rebuilt.pointer.root, kind);
    if (
      createHash("sha256").update(journalKey(store)).digest("hex") !==
      kinds[kind].logicalHash
    )
      throw Error("恢复后重建回放不一致");
    kinds[kind].rebuiltReplayEqual = true;
  }
  return {
    schemaVersion: 1,
    root: published.pointer.root.sha256,
    objects: published.objects,
    gitRequired: false,
    sourceShardsRequired: false,
    promotion: false,
    kinds,
  };
}
if (
  process.argv[1] &&
  import.meta.url === pathToFileURL(process.argv[1]).href
) {
  const [source, output, report = "test-results/archive-recovery.json"] =
    process.argv.slice(2);
  if (!source || !output)
    throw Error(
      "usage: node scripts/verify_archive_recovery.mjs artifact fresh-isolated-directory [report]",
    );
  const result = await verifyArchiveRecovery(source, output);
  mkdirSync(dirname(report), { recursive: true });
  writeFileSync(report, JSON.stringify(result, null, 2) + "\n");
  console.log(JSON.stringify(result));
}
