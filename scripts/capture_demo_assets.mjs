#!/usr/bin/env node

import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..");
const outputDir = resolve(repoRoot, "docs/demo-assets");
const chromePath =
  process.env.CHROME_PATH ??
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const baseUrl = process.env.PRESENCE_RX_URL ?? "http://localhost:3000";
const debugPort = Number(process.env.CHROME_DEBUG_PORT ?? 9333);
const viewport = {
  width: Number(process.env.DEMO_WIDTH ?? 1440),
  height: Number(process.env.DEMO_HEIGHT ?? 1100),
  deviceScaleFactor: 1,
  mobile: false,
};

const shots = [
  {
    id: "gap-analysis",
    title: "Gap Analysis",
    url: `${baseUrl}/diagnosis`,
    waitForText: "Conversation Blocks",
    beforeCapture: async (cdp) => {
      await cdp.send("Runtime.evaluate", {
        expression: "window.scrollTo(0, 0)",
        awaitPromise: true,
      });
    },
  },
  {
    id: "strategic-action",
    title: "Strategic Action",
    url: `${baseUrl}/`,
    waitForText: "Discovery Gaps",
    beforeCapture: async (cdp) => {
      await cdp.send("Runtime.evaluate", {
        expression: `
          const heading = [...document.querySelectorAll("h2")]
            .find((node) => node.textContent?.includes("Discovery Gaps"));
          heading?.scrollIntoView({ block: "start" });
          window.scrollBy(0, -66);
        `,
        awaitPromise: true,
      });
    },
    clip: { x: 220, y: 56, width: 1220, height: 980 },
  },
  {
    id: "channel-activation",
    title: "Channel Activation",
    url: `${baseUrl}/`,
    waitForText: "Where to Engage",
    beforeCapture: async (cdp) => {
      await cdp.send("Runtime.evaluate", {
        expression: `
          const heading = [...document.querySelectorAll("h2")]
            .find((node) => node.textContent?.includes("Where to Engage"));
          heading?.scrollIntoView({ block: "start" });
          window.scrollBy(0, 36);
        `,
        awaitPromise: true,
      });
    },
    clip: { x: 220, y: 480, width: 1220, height: 620 },
  },
  {
    id: "claim-simulation",
    title: "Claim Simulation",
    url: `${baseUrl}/evidence`,
    waitForText: "Claim Simulator",
    beforeCapture: async (cdp) => {
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
    },
    clip: { x: 220, y: 610, width: 1220, height: 490 },
  },
  {
    id: "future-preview",
    title: "Future Direction Preview",
    url: `${baseUrl}/future`,
    waitForText: "Illustrative preview",
    beforeCapture: async (cdp) => {
      await cdp.send("Runtime.evaluate", {
        expression: "window.scrollTo(0, 0)",
        awaitPromise: true,
      });
    },
  },
];

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

async function captureShot(cdp, shot) {
  await cdp.send("Page.navigate", { url: shot.url });
  await waitForText(cdp, shot.waitForText);
  await shot.beforeCapture?.(cdp);
  await delay(500);
  let clip;
  if (shot.clip) {
    const scroll = await cdp.send("Runtime.evaluate", {
      expression: "({ x: window.scrollX, y: window.scrollY })",
      returnByValue: true,
    });
    clip = {
      ...shot.clip,
      x: shot.clip.x + Number(scroll.result?.value?.x ?? 0),
      y: shot.clip.y + Number(scroll.result?.value?.y ?? 0),
      scale: 1,
    };
  }
  const screenshot = await cdp.send("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport: false,
    ...(clip ? { clip } : {}),
  });
  const file = resolve(outputDir, `${shot.id}.png`);
  await writeFile(file, Buffer.from(screenshot.data, "base64"));
  console.log(`${shot.title}: ${file}`);
}

async function main() {
  await mkdir(outputDir, { recursive: true });
  const userDataDir = resolve("/tmp", `presence-rx-chrome-${process.pid}`);
  await rm(userDataDir, { recursive: true, force: true });

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

    for (const shot of shots) {
      await captureShot(cdp, shot);
    }

    cdp.close();
  } finally {
    chrome.kill("SIGTERM");
    await new Promise((resolveExit) => {
      chrome.once("exit", resolveExit);
      setTimeout(resolveExit, 1000);
    });
    await rm(userDataDir, { recursive: true, force: true }).catch(() => {});
  }
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
