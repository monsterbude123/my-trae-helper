---
name: screenshot
description: 通用 Playwright 截图工具 — 快速截取任意页面状态，用于 vision-audit 分析。每次只截一张，模拟人类操作节奏。
intent: 通用 Playwright 截图工具 — 快速截取任意页面状态，用于 vision-audit 分析
category: other
audience: [developer]
---
# screenshot

用 Playwright 快速截取页面截图。设计原则：**一次只做一件事** — 导航到页面、可选点击一个元素、截图、退出。

## 前置条件

- Playwright 已安装（项目已有依赖）
- 目标服务已启动

## 命令

```bash
# 基础截图
node screenshot/scripts/screenshot.mjs /workbench-unified debug/screenshots/manual/01.png

# 点击某元素后截图
node screenshot/scripts/screenshot.mjs /workbench-unified debug/screenshots/manual/02.png --click "button:has-text('智能体')"

# 等待某元素出现后截图
node screenshot/scripts/screenshot.mjs /workbench-unified debug/screenshots/manual/03.png --wait ".task-panel"

# 完整URL
node screenshot/scripts/screenshot.mjs http://localhost:5173/settings out/04.png

# 自定义延迟（ms）
node screenshot/scripts/screenshot.mjs /workbench-unified out/05.png --delay 1000
```

## 参数

| 参数 | 说明 | 默认 |
|------|------|------|
| `<url>` | 页面URL或相对路径 | (必填) |
| `<output>` | 输出PNG路径 | (必填) |
| `--base` | 基础URL | `http://127.0.0.1:5173` |
| `--click` | 截图前点击的CSS选择器 | — |
| `--wait` | 等待出现的CSS选择器 | — |
| `--delay` | 导航后等待(ms) | 800 |
| `--viewport` | 视口大小 WxH | `1440x900` |
| `--full` | 全页截图 | `false` |

## AI Agent 使用规范

> **关键铁律：一次只截一张图，截完用 vision-audit 看内容，再做下一步操作。**

```
循环:
  1. 用 screenshot 截一张图
  2. 用 vision-audit --single 分析这张图的内容
  3. 根据内容决定下一步操作
  4. 回到步骤1
```

禁止行为：
- ❌ 一次点击所有按钮再截图
- ❌ 不看截图就继续操作
- ❌ 用 take_snapshot 代替截图
