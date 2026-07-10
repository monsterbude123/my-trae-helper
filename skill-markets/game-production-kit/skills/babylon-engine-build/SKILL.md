---
name: babylon-engine-build
description: Babylon.js 引擎构建与验证 — Vite 构建 + Playwright 浏览器截图 proof bundle。包含 npm run build + Playwright 录制 + ffmpeg 视频编码。触发词：Babylon构建、babylon build、babylonjs deploy。
user-invocable: true
---

# Babylon.js 引擎构建与验证

> 吸收自 godogen babylon/ 模块（capture.md Playwright 录制 + quirks.md + task-execution.md Vite dev server 循环）。

将 Babylon.js TypeScript 项目构建为静态站点，并进行视觉验证。

> 前置条件：`game-quality-gate` 门禁已通过，`babylon-scripting` 场景已完成。
>
> 协作关系：在当前 kit 编排器路由下执行。

## 核心铁律

```
1. Babylon.js 是浏览器引擎 — 所有验证通过浏览器截图完成
2. 构建后必须生成 proof bundle（Playwright 截图 + 视频）
3. Vite 生产构建：npm run build → dist/
4. 热重载是标准开发流程，不支持交互式构建
5. WebGL context 必须可用（CI 用 xvfb 或 headless Chrome）
```

## 构建流程

```
1. npm run build → Vite 生产构建 → dist/
2. 本地预览: npx vite preview
3. Playwright 录制: 导航 → 截图 → 视频
4. 人工确认 proof bundle
5. 部署 static site
```

## 构建命令

```bash
# 安装依赖
npm install

# 开发模式 (HMR)
npm run dev

# 生产构建
npm run build          # → dist/

# 本地预览
npx vite preview
```

## Playwright 录制 (Capture)

> 来自 godogen babylon capture.md。浏览器引擎专用截图方案。

**关键 wiring**:
- `chromium.launch({ headless: true })`
- `context.recordVideo` → 录屏
- `page.goto("http://localhost:4173")` → vite preview 端口
- `page.waitForTimeout(5000)` → 等待游戏启动/WebGL 渲染帧
- `page.screenshot()` → 截图序列

> 完整 capture.ts 模板、序列时序、错误处理 → `references/babylon-capture.md`

```bash
npx tsx capture.ts

# ffmpeg 视频转换
ffmpeg -y -i screenshots/result/video.webm \
  -c:v libx264 -pix_fmt yuv420p screenshots/result/{tag}/video.mp4
```

## Proof Bundle 输出

```
screenshots/result/{build_tag}/
├── title.png          # 标题画面
├── gameplay_01.png    # 游戏场景 1
├── gameplay_02.png    # 游戏场景 2
├── gameplay_03.png    # 关键剧情节点
├── video.mp4          # Playwright 录制视频 (webm→mp4)
└── proof.md
```

## 部署

Babylon.js 产物为标准静态站点（`dist/`）：

```
Netlify / Vercel / GitHub Pages / Cloudflare Pages
→ 上传 dist/ 目录
```

或自有服务器：

```bash
scp -r dist/ user@server:/var/www/{game}/
```

## 已知坑

> 来自 godogen babylon quirks.md。

| 错误 | 原因 | 解决 |
|------|------|------|
| WebGL context lost | 浏览器标签切换 | `engine.onContextLostObservable` 处理恢复 |
| AudioContext blocked (移动端) | 自动播放策略 | 首次用户交互后激活 |
| Playwright 截图白屏 | WebGL 渲染帧未完成 | 等待 `scene.isReady()` |
| Vite build 报 module not found | @babylonjs 子包未安装 | 检查 `@babylonjs/core` 在 dependencies |
| 素材 404 | 路径不在 public/ | 素材放 public/ 下或用 import.meta.url |

> 新发现的坑写入 `quirks-babylon.md`。
