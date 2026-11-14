import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve, extname } from "node:path";
const { chromium } = createRequire(import.meta.url)(
  process.env.PLAYWRIGHT_MODULE || "playwright",
);
const registry = JSON.parse(
  readFileSync(
    new URL("../../config/public-entrypoints.json", import.meta.url),
  ),
);
const site =
  process.env.ATLAS_SITE_DIRECTORY && resolve(process.env.ATLAS_SITE_DIRECTORY);
async function harness() {
  assert.ok(site, "actual release artifact required");
  const server = createServer(async (req, res) => {
    try {
      const path = resolve(
        site,
        "." + new URL(req.url, "http://localhost").pathname,
      );
      if (!path.startsWith(site + "/")) throw Error("invalid path");
      res.setHeader(
        "content-type",
        {
          ".mjs": "text/javascript",
          ".css": "text/css",
          ".html": "text/html",
          ".json": "application/json",
          ".gz": "application/gzip",
        }[extname(path)] || "application/octet-stream",
      );
      res.end(await readFile(path));
    } catch {
      res.writeHead(404);
      res.end();
    }
  });
  await new Promise((r) => server.listen(0, "127.0.0.1", r));
  let browser;
  try {
    browser = await chromium.launch({ headless: true });
  } catch (e) {
    await new Promise((r) => server.close(r));
    throw e;
  }
  return {
    browser,
    origin: "http://127.0.0.1:" + server.address().port,
    close: async () => {
      await browser.close();
      await new Promise((r) => server.close(r));
    },
  };
}
async function ready(page, entry) {
  const locator = page.locator(entry.ready.selector).first();
  await locator.waitFor({ state: "attached", timeout: 20000 });
  if (entry.ready.text)
    await locator
      .filter({ hasText: entry.ready.text })
      .waitFor({ state: "attached", timeout: 20000 });
  else
    await page.waitForFunction(
      (selector) =>
        Boolean(
          document.querySelector(selector)?.textContent?.trim() ||
            document.querySelector(selector)?.tagName === "INPUT",
        ),
      entry.ready.selector,
      { timeout: 20000 },
    );
}
test(
  "all 106 shipped HTML entries reach their registered startup signal using actual published resources",
  { timeout: 240000 },
  async () => {
    const f = await harness(),
      report = {
        schemaVersion: 1,
        revision: JSON.parse(
          readFileSync(resolve(site, "data/catalogue-release.json")),
        ).revision,
        entries: [],
      },
      queue = [...registry.entries];
    try {
      const release = JSON.parse(
        readFileSync(resolve(site, "data/catalogue-release.json")),
      );
      for (const entry of registry.entries) {
        for (const name of entry.resources)
          assert.ok(
            release.resources[name],
            entry.path + " missing frozen resource " + name,
          );
        for (const name of entry.catalogues)
          assert.ok(
            release.catalogues[name],
            entry.path + " missing catalogue " + name,
          );
        if (entry.basicManifest)
          assert.ok(release.basic, entry.path + " missing basic manifest");
      }
      await Promise.all(
        Array.from({ length: 3 }, async () => {
          for (let entry; (entry = queue.shift()); ) {
            const page = await f.browser.newPage({
                viewport: { width: 390, height: 844 },
              }),
              errors = [],
              failures = [],
              started = Date.now(),
              pending = new Set();
            page.on("request", (r) => {
              if (r.url().startsWith(f.origin)) pending.add(r);
            });
            page.on("requestfinished", (r) => pending.delete(r));
            page.on("requestfailed", (r) => {
              pending.delete(r);
              if (r.url().startsWith(f.origin))
                failures.push({ url: r.url(), error: r.failure()?.errorText });
            });
            page.on("pageerror", (e) => errors.push(e.message));
            page.on("response", (r) => {
              if (
                r.url().startsWith(f.origin) &&
                r.status() >= 400 &&
                !r.url().endsWith("/favicon.ico")
              )
                failures.push({ url: r.url(), status: r.status() });
            });
            try {
              assert.equal(
                (
                  await page.goto(f.origin + "/" + entry.path, {
                    waitUntil: "domcontentloaded",
                  })
                ).status(),
                200,
              );
              await ready(page, entry);
              // External image/analytics connections do not define application readiness.
              // All same-origin release reads must settle within the bounded window.
              const deadline = Date.now() + 10000;
              while (pending.size && Date.now() < deadline)
                await new Promise((r) => setTimeout(r, 50));
              assert.deepEqual(
                [...pending].map((r) => r.url()),
                [],
                entry.path + " unresolved release resources",
              );
              assert.deepEqual(errors, [], entry.path + " script errors");
              assert.deepEqual(
                failures,
                [],
                entry.path + " missing release resources",
              );
              report.entries.push({
                path: entry.path,
                ready: entry.ready,
                passed: true,
                ms: Date.now() - started,
              });
            } catch (error) {
              report.entries.push({
                path: entry.path,
                passed: false,
                error: error.message,
                errors,
                failures,
              });
            } finally {
              await page.close();
            }
          }
        }),
      );
      assert.equal(report.entries.length, registry.entries.length);
      assert.deepEqual(
        report.entries.filter((e) => !e.passed),
        [],
        "all published entries must initialize",
      );
    } finally {
      mkdirSync("test-results", { recursive: true });
      writeFileSync(
        "test-results/public-entrypoints.json",
        JSON.stringify(report, null, 2) + "\n",
      );
      await f.close();
    }
  },
);
test(
  "additional required-resource failures show bounded fallback and recover on reload",
  { timeout: 120000 },
  async () => {
    const f = await harness(),
      cases = [
        [
          "organizations.html",
          "organizations.json",
          "#graph-stage",
          "关系资料暂时无法读取",
        ],
        [
          "relationships-preview.html",
          "relationships-preview.json",
          "#graph-stage",
          "关系资料暂时无法读取",
        ],
        [
          "curated.html",
          "curated-narrative-works.json",
          "#cards",
          "请打开基础作品库",
        ],
      ];
    try {
      for (const [path, file, selector, message] of cases) {
        const page = await f.browser.newPage();
        let blocked = true,
          hits = 0;
        await page.route("**/*", async (route) => {
          const u = new URL(route.request().url());
          if (blocked && u.pathname.includes("/resources/" + file)) {
            hits++;
            await route.fulfill({ status: 503, body: "unavailable" });
          } else await route.continue();
        });
        await page.goto(f.origin + "/" + path);
        await page
          .locator(selector)
          .filter({ hasText: message })
          .waitFor({ timeout: 15000 });
        assert.ok(hits > 0, path + " failure actually injected");
        blocked = false;
        await page.reload();
        await ready(
          page,
          registry.entries.find((e) => e.path === path),
        );
        await page.close();
      }
    } finally {
      await f.close();
    }
  },
);
