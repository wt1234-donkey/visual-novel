import test from "node:test";
import assert from "node:assert/strict";
import {
  mkdtempSync,
  mkdirSync,
  writeFileSync,
  readFileSync,
  rmSync,
} from "node:fs";
import { join } from "node:path";
import { tmpdir } from "node:os";
import {
  basicScale,
  formalScale,
  identityScale,
  fieldScale,
} from "./helpers/audit-scale-fixture.mjs";
import { AUDIT_PATH, AUDIT_SOURCES } from "../src/domain/audit/events.mjs";
import {
  buildAuditLedger,
  publishAuditLedger,
} from "../src/infrastructure/filesystem/audit-ledger.mjs";
import { verifyArchiveRecovery } from "../scripts/verify_archive_recovery.mjs";
test("all four audit kinds recover and rebuild from published objects after all authority sources are removed", async (t) => {
  const temp = mkdtempSync(join(tmpdir(), "atlas-recovery-"));
  t.after(() => rmSync(temp, { recursive: true, force: true }));
  const source = join(temp, "source"),
    publicDir = join(temp, "public"),
    recovered = join(temp, "recovered");
  mkdirSync(join(source, "data"), { recursive: true });
  for (const [kind, make] of [
    ["basic", basicScale],
    ["formal", formalScale],
    ["identity", identityScale],
    ["field", fieldScale],
  ])
    writeFileSync(
      join(source, AUDIT_SOURCES[kind]),
      JSON.stringify(make(100).store) + "\n",
    );
  await buildAuditLedger(source);
  await publishAuditLedger(source, publicDir);
  rmSync(source, { recursive: true });
  const result = await verifyArchiveRecovery(publicDir, recovered);
  assert.deepEqual(Object.keys(result.kinds).sort(), [
    "basic",
    "field",
    "formal",
    "identity",
  ]);
  assert.ok(
    Object.values(result.kinds).every(
      (v) => v.events === 100 && v.rebuiltReplayEqual,
    ),
  );
  assert.equal(result.promotion, false);
  await assert.rejects(verifyArchiveRecovery(publicDir, recovered), /隔离目录/);
  const pointer = JSON.parse(readFileSync(join(publicDir, AUDIT_PATH))),
    path = join(publicDir, pointer.root.path);
  writeFileSync(path, readFileSync(path, "utf8") + " ");
  await assert.rejects(
    verifyArchiveRecovery(publicDir, join(temp, "corrupt")),
    /摘要/,
  );
});
