// Official transport: https://developer.chrome.com/docs/devtools/remote-debugging
// Browser API: https://playwright.dev/docs/api/class-browsertype#browser-type-connect-over-cdp
import { execFileSync } from "node:child_process";
import { createRequire } from "node:module";
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
const args = process.argv.slice(2),
  value = (flag) => args[args.indexOf(flag) + 1],
  serial = args.includes("--serial") ? value("--serial") : null;
const reportPath = args.includes("--report")
  ? value("--report")
  : "test-results/android-real-device.json";
const report = {
  schemaVersion: 1,
  capability: "android-real-device",
  status: "unavailable",
  passed: false,
  emulation: false,
  reason: "未指定已授权连接的实体 Android 设备；未执行真机测量。",
};
let browser, page, port;
const adb = (...command) =>
  execFileSync("adb", ["-s", serial, ...command], {
    encoding: "utf8",
    timeout: 15000,
  }).trim();
try {
  if (serial) {
    if (!args.includes("--physical-device"))
      throw Error(
        "实体设备测量必须显式 --physical-device；模拟器结果不能冒充真机",
      );
    if (
      adb("get-state") !== "device" ||
      serial.startsWith("emulator-") ||
      adb("shell", "getprop", "ro.kernel.qemu") === "1"
    )
      throw Error("设备不可用或是模拟器");
    report.device = {
      model: adb("shell", "getprop", "ro.product.model"),
      manufacturer: adb("shell", "getprop", "ro.product.manufacturer"),
      android: adb("shell", "getprop", "ro.build.version.release"),
      sdk: adb("shell", "getprop", "ro.build.version.sdk"),
    };
    const base = new URL(
      args.includes("--url")
        ? value("--url")
        : "https://wt1234-donkey.github.io/visual-novel/",
    );
    if (base.protocol !== "https:") throw Error("真机联网测量需要 HTTPS 站点");
    const { chromium } = createRequire(import.meta.url)(
      process.env.PLAYWRIGHT_MODULE || "playwright",
    );
    port = adb("forward", "tcp:0", "localabstract:chrome_devtools_remote");
    if (!/^\d+$/.test(port)) throw Error("Chrome 调试端口不可用");
    browser = await chromium.connectOverCDP("http://127.0.0.1:" + port);
    page = await browser.contexts()[0].newPage();
    const entries = JSON.parse(
      readFileSync(
        new URL("../config/public-entrypoints.json", import.meta.url),
      ),
    ).entries;
    report.pages = [];
    report.startedAt = new Date().toISOString();
    report.browser = browser.version();
    report.cachePolicy =
      "existing device Chrome cache; three fresh navigations; no CPU, network or viewport emulation";
    for (const path of ["index.html", "manage.html", "bulk-import.html"]) {
      const contract = entries.find((e) => e.path === path),
        runs = [];
      for (let i = 0; i < 3; i++) {
        const start = Date.now();
        await page.goto(new URL(path, base).href, { timeout: 45000 });
        await page
          .locator(contract.ready.selector)
          .first()
          .waitFor({ timeout: 45000 });
        const readyMs = Date.now() - start;
        await page.waitForLoadState("networkidle", { timeout: 45000 });
        runs.push({
          readyMs,
          ...(await page.evaluate(() => ({
            viewport: {
              width: innerWidth,
              height: innerHeight,
              dpr: devicePixelRatio,
            },
            connection: navigator.connection
              ? {
                  effectiveType: navigator.connection.effectiveType,
                  rtt: navigator.connection.rtt,
                  downlink: navigator.connection.downlink,
                }
              : null,
            requests: performance.getEntriesByType("resource").length,
            transferBytes: performance
              .getEntriesByType("resource")
              .reduce((n, r) => n + r.transferSize, 0),
          }))),
        });
      }
      report.pages.push({
        path,
        runs,
        medianReadyMs: runs.map((r) => r.readyMs).sort((a, b) => a - b)[1],
      });
    }
    report.status = "measured";
    report.passed = true;
    delete report.reason;
  }
} catch (error) {
  report.status = "failed";
  report.reason = error.message;
  process.exitCode = 1;
} finally {
  await page?.close();
  await browser?.close();
  if (port)
    try {
      adb("forward", "--remove", "tcp:" + port);
    } catch {}
  mkdirSync(dirname(reportPath), { recursive: true });
  writeFileSync(reportPath, JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report));
}
