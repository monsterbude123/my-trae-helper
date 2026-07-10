# babylon-capture.md

> 来源：godogen babylon/capture.md（Playwright 浏览器录制模板，2026-06 提取）
> 关联：babylon-engine-build/SKILL.md §Playwright 录制 (Capture)
> 目的：capture.ts 完整模板 — headless chromium + recordVideo + 序列时序 + 视频编码。

## §1 安装依赖

```bash
npm install -D playwright @playwright/test
npx playwright install chromium
```

> ffmpeg 需系统级安装（见 §5）。

## §2 capture.ts 完整模板

```ts
// capture.ts
import { chromium, type Browser, type Page } from "playwright";
import { mkdir } from "node:fs/promises";
import { join } from "node:path";
import { exec } from "node:child_process";
import { promisify } from "node:util";

const execAsync = promisify(exec);

const BUILD_TAG = process.env.BUILD_TAG ?? "v0.1.0";
const URL = process.env.PREVIEW_URL ?? "http://localhost:4173";
const OUT_DIR = join("screenshots", "result", BUILD_TAG);
const STEPS = ["title", "gameplay_01", "gameplay_02", "gameplay_03"];
const STEP_DELAY = 1500;

async function waitReady(page: Page) {
  await page.waitForLoadState("networkidle");
  // 关键：等待 WebGL 渲染稳定（场景就绪）
  await page.waitForFunction(() => {
    const c = document.querySelector("canvas");
    return c && c.width > 0 && c.height > 0;
  });
  await page.waitForTimeout(STEP_DELAY);
}

async function captureSequence(browser: Browser) {
  await mkdir(OUT_DIR, { recursive: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 720 },
    recordVideo: { dir: OUT_DIR, size: { width: 1280, height: 720 } },
  });
  const page = await context.newPage();
  try {
    await page.goto(URL, { waitUntil: "domcontentloaded" });
    await waitReady(page);
    for (const step of STEPS) {
      await page.screenshot({ path: join(OUT_DIR, `${step}.png`) });
      console.log(`[capture] ${step} done`);
      await page.keyboard.press("Space");
      await page.waitForTimeout(STEP_DELAY);
    }
  } finally {
    await context.close(); // 触发 video 落盘
  }
}

async function encodeVideo() {
  const webm = join(OUT_DIR, "video.webm");
  const mp4 = join(OUT_DIR, "video.mp4");
  await execAsync(`ffmpeg -y -i "${webm}" -c:v libx264 -pix_fmt yuv420p "${mp4}"`);
}

async function main() {
  const browser = await chromium.launch({ headless: true });
  try {
    await captureSequence(browser);
    await encodeVideo();
  } finally {
    await browser.close();
  }
}

main().catch((err) => { console.error(err); process.exit(1); });
```

## §3 序列时序

```
0ms       goto(URL)
~2000ms   canvas 渲染首帧
~3500ms   title.png（STEP_DELAY 后）
+1500ms   gameplay_01.png（按 Space）
+1500ms   gameplay_02.png
+1500ms   gameplay_03.png
~9000ms   context.close() → 视频落盘
~12000ms  ffmpeg 转码完成
```

> 关键：`recordVideo` 必须在 `context.close()` 后才能拿到 `video.webm`。

## §4 运行命令

```bash
# 终端 A：vite preview
npm run build && npx vite preview --port 4173

# 终端 B：录制
npx tsx capture.ts

# 自定义 BUILD_TAG
BUILD_TAG=v0.2.0 npx tsx capture.ts
```

## §5 视频编码

| 参数 | 作用 |
|------|------|
| `-y` | 覆盖输出 |
| `-c:v libx264` | H.264 编码（浏览器友好） |
| `-pix_fmt yuv420p` | 兼容 QuickTime / iOS |
| `-crf 23` | 视觉质量（18~28） |

> ffmpeg 系统级：Windows `winget install ffmpeg` / macOS `brew install ffmpeg` / Linux `apt install ffmpeg`。

## §6 错误处理

| 症状 | 根因 | 修复 |
|------|------|------|
| 截图白屏 | WebGL 未渲染 | 增大 STEP_DELAY 或 `await scene.isReady()` |
| 视频 0 字节 | recordVideo dir 不存在 | mkdir -p 父目录 |
| ffmpeg 失败 | 旧版不支持 VP9 | 升级 ffmpeg ≥4.3 |

## §7 输出结构

```
screenshots/result/{build_tag}/
├── title.png / gameplay_01.png / gameplay_02.png / gameplay_03.png
├── video.webm      # Playwright 原始录屏
├── video.mp4       # ffmpeg 转码后
└── proof.md        # 人工 review 验收记录
```
