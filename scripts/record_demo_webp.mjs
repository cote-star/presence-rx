#!/usr/bin/env node

import { spawn } from "node:child_process";
import { mkdtemp, mkdir, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const outputFile = resolve(
  repoRoot,
  process.env.DEMO_WEBP_OUTPUT ?? "docs/demo-assets/presence-rx-walkthrough.webp",
);
const chromePath =
  process.env.CHROME_PATH ??
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const img2webpPath = process.env.IMG2WEBP_PATH ?? "img2webp";
const baseUrl = process.env.PRESENCE_RX_URL ?? "http://localhost:3000";
const debugPort = Number(process.env.CHROME_DEBUG_PORT ?? 9334);
const frameDurationMs = Number(process.env.DEMO_FRAME_MS ?? 180);
const webpQuality = String(process.env.DEMO_WEBP_QUALITY ?? 60);
const viewport = {
  width: Number(process.env.DEMO_WIDTH ?? 1280),
  height: Number(process.env.DEMO_HEIGHT ?? 720),
  deviceScaleFactor: 1,
  mobile: false,
};

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

async function fetchJson(url, retries = 80) {
  let lastError;
  for (let i = 0; i < retries; i += 1) {
    try {
      const response = await fetch(url);
      if (response.ok) return response.json();
      lastError = new Error(`${response.status} ${response.statusText}`);
    } catch (error) {
      lastError = error;
    }
    await delay(100);
  }
  throw lastError ?? new Error(`Timed out fetching ${url}`);
}

class CdpClient {
  constructor(wsUrl) {
    this.wsUrl = wsUrl;
    this.nextId = 1;
    this.pending = new Map();
  }

  async connect() {
    this.socket = new WebSocket(this.wsUrl);
    this.socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (!message.id) return;
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      if (message.error) {
        pending.reject(new Error(message.error.message));
      } else {
        pending.resolve(message.result);
      }
    });
    await new Promise((resolveConnect, rejectConnect) => {
      this.socket.addEventListener("open", resolveConnect, { once: true });
      this.socket.addEventListener("error", rejectConnect, { once: true });
    });
  }

  send(method, params = {}) {
    const id = this.nextId;
    this.nextId += 1;
    this.socket.send(JSON.stringify({ id, method, params }));
    return new Promise((resolveSend, rejectSend) => {
      this.pending.set(id, { resolve: resolveSend, reject: rejectSend });
    });
  }

  close() {
    this.socket?.close();
  }
}

async function waitForText(cdp, text, timeoutMs = 10000) {
  const started = Date.now();
  const escaped = JSON.stringify(text);
  while (Date.now() - started < timeoutMs) {
    const result = await cdp.send("Runtime.evaluate", {
      expression: `document.body?.innerText?.includes(${escaped}) ?? false`,
      returnByValue: true,
    });
    if (result.result?.value) return;
    await delay(150);
  }
  throw new Error(`Timed out waiting for text: ${text}`);
}

async function navigate(cdp, url, text) {
  await cdp.send("Page.navigate", { url });
  await waitForText(cdp, text);
  await delay(500);
}

async function pageScrollY(cdp, expression) {
  const result = await cdp.send("Runtime.evaluate", {
    expression,
    returnByValue: true,
    awaitPromise: true,
  });
  return Number(result.result?.value ?? 0);
}

async function setScroll(cdp, y) {
  await cdp.send("Runtime.evaluate", {
    expression: `window.scrollTo(0, ${Math.max(0, Math.round(y))})`,
    awaitPromise: true,
  });
  await delay(40);
}

async function fillBlockedClaim(cdp) {
  await cdp.send("Runtime.evaluate", {
    expression: `
      (async () => {
        const simulator = [...document.querySelectorAll("h3")]
          .find((node) => node.textContent?.includes("Claim Simulator"));
        simulator?.scrollIntoView({ block: "center" });
        const input = document.querySelector("input[placeholder^='Type a marketing claim']");
        const claim = "Nothing Phone is the go-to minimalist tech brand";
        const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value").set;
        setter.call(input, claim);
        input.dispatchEvent(new InputEvent("input", { bubbles: true, data: claim, inputType: "insertText" }));
        await new Promise((resolve) => setTimeout(resolve, 100));
        const button = [...document.querySelectorAll("button")]
          .find((node) => node.textContent?.includes("Check claim"));
        button?.click();
      })();
    `,
    awaitPromise: true,
  });
  await waitForText(cdp, "Suggested safe rewrite", 5000);
  await cdp.send("Runtime.evaluate", {
    expression: `
      const result = [...document.querySelectorAll("*")]
        .find((node) => node.textContent?.trim() === "Suggested safe rewrite");
      result?.scrollIntoView({ block: "center" });
    `,
    awaitPromise: true,
  });
  await delay(300);
}

async function captureFrame(cdp, framesDir, index) {
  const screenshot = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
  });
  const file = resolve(framesDir, `frame-${String(index).padStart(4, "0")}.png`);
  await writeFile(file, Buffer.from(screenshot.data, "base64"));
  return file;
}

async function captureHold(cdp, framesDir, state, count) {
  for (let i = 0; i < count; i += 1) {
    state.frames.push(await captureFrame(cdp, framesDir, state.frames.length));
  }
}

async function captureScroll(cdp, framesDir, state, startY, endY, steps) {
  for (let i = 0; i < steps; i += 1) {
    const t = steps === 1 ? 1 : i / (steps - 1);
    const eased = 0.5 - Math.cos(Math.PI * t) / 2;
    await setScroll(cdp, startY + (endY - startY) * eased);
    state.frames.push(await captureFrame(cdp, framesDir, state.frames.length));
  }
}

async function encodeWebp(frames, output) {
  await mkdir(dirname(output), { recursive: true });
  const args = ["-loop", "0", "-min_size"];
  for (const frame of frames) {
    args.push("-d", String(frameDurationMs), "-lossy", "-q", webpQuality, "-m", "5", frame);
  }
  args.push("-o", output);

  await new Promise((resolveEncode, rejectEncode) => {
    const child = spawn(img2webpPath, args, { stdio: ["ignore", "pipe", "pipe"] });
    let stderr = "";
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("error", rejectEncode);
    child.on("close", (code) => {
      if (code === 0) resolveEncode();
      else rejectEncode(new Error(stderr || `img2webp exited with ${code}`));
    });
  });
}

async function main() {
  const tempRoot = await mkdtemp(resolve(tmpdir(), "presence-rx-webp-"));
  const framesDir = resolve(tempRoot, "frames");
  const userDataDir = resolve(tempRoot, "chrome");
  await mkdir(framesDir, { recursive: true });

  const chrome = spawn(chromePath, [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--no-first-run",
    "--no-default-browser-check",
    `--remote-debugging-port=${debugPort}`,
    `--user-data-dir=${userDataDir}`,
    `--window-size=${viewport.width},${viewport.height}`,
    "about:blank",
  ]);

  chrome.stderr.on("data", (chunk) => {
    const line = chunk.toString();
    if (line.includes("DevTools listening")) return;
    if (process.env.VERBOSE_CHROME) process.stderr.write(line);
  });

  try {
    const pages = await fetchJson(`http://127.0.0.1:${debugPort}/json`);
    const page = pages.find((entry) => entry.type === "page") ?? pages[0];
    const cdp = new CdpClient(page.webSocketDebuggerUrl);
    await cdp.connect();
    await cdp.send("Page.enable");
    await cdp.send("Runtime.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", viewport);

    const state = { frames: [] };

    await navigate(cdp, `${baseUrl}/diagnosis`, "Conversation Blocks");
    await captureHold(cdp, framesDir, state, 8);
    await captureScroll(cdp, framesDir, state, 0, 760, 28);

    await navigate(cdp, `${baseUrl}/`, "Discovery Gaps");
    const actionStart = await pageScrollY(
      cdp,
      `(() => {
        const heading = [...document.querySelectorAll("h2")]
          .find((node) => node.textContent?.includes("Discovery Gaps"));
        return Math.max(0, (heading?.getBoundingClientRect().top ?? 0) + window.scrollY - 66);
      })()`,
    );
    await captureScroll(cdp, framesDir, state, actionStart, actionStart + 980, 32);

    await navigate(cdp, `${baseUrl}/evidence`, "Claim Simulator");
    await fillBlockedClaim(cdp);
    await captureHold(cdp, framesDir, state, 20);

    await navigate(cdp, `${baseUrl}/future`, "Illustrative preview");
    await captureHold(cdp, framesDir, state, 6);
    await captureScroll(cdp, framesDir, state, 0, 520, 16);

    cdp.close();
    await encodeWebp(state.frames, outputFile);
    console.log(`Wrote ${outputFile} (${state.frames.length} frames)`);
  } finally {
    chrome.kill("SIGTERM");
    await new Promise((resolveExit) => {
      chrome.once("exit", resolveExit);
      setTimeout(resolveExit, 1000);
    });
    await rm(tempRoot, { recursive: true, force: true }).catch(() => {});
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
