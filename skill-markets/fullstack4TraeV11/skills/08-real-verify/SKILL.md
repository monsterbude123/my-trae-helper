---
name: real-verify
description: "Stage 3.5 启动可见产物 — 唯一信任基础，不接受自评。环境依赖 + 真实验证 + 启动可见产物 + 阻塞处理。触发词：real verify / 启动验证 / 真实验证 / visible product。"
stage: 3.5
parent: fullstack4traev11
depends_on:
  skills: [visual-evidence-discipline, screenshot, playwright-best-practices]
  stages: [3/implement]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/dist-hash-check.py
    - ../../scripts/visual-content-check.py
---

# Stage 3.5 Real Verify — 启动可见产物

> 第一性原则：**启动可见产物是唯一信任基础，不接受自评**。V10 §0.10 NEW 防虚假交付。

## 边界

| Real Verify 处理 | Real Verify 不处理 |
|-----------------|-------------------|
| 环境依赖检查 + 真实验证 + 启动可见产物 | 实施编码 → Stage 3 Implement |
| 阻塞报告（V10 Article XV）| 验收 → Stage 4 Review |

## 铁律（6 条 — V10 §0.10）

```
1. 启动可见产物 — "启动 = 完成" 是软指标，必须有可见产物
2. 环境依赖检查 — DB / 缓存 / .env / 端口可达必走
3. 真实验证执行 — 迁移 / 测试 / 类型检查 / dev server 启动
4. 5 类项目启动验证 — Web / Tauri / CLI / Library / 后端
5. 阻塞诚实 — 任一 FAIL → 5 字段阻塞报告（Article XV）
6. 主上下文必查 — 亲自 Read 输出，不委派子代理
```

## 骨架流程（4 步）

```
Step 1: 环境依赖检查（DB / 缓存 / .env / 端口）
Step 2: 真实验证执行（迁移 / 测试 / 类型检查 / dev 启动）
Step 3: 启动可见产物（按项目类型 5 类之一）
Step 4: 阻塞处理（任一 FAIL → 5 字段报告 + 状态卡 blocked）
```

## 5 类项目启动验证（V10 §0.10 NEW）

| 项目类型 | 验证产物 | 强约束 |
|---------|---------|--------|
| **Web** | curl localhost 返回 200 + Playwright 截图 ≥1 张（≥5KB） | 必含 file:line 路径 |
| **Tauri** | `tauri dev` 进程存活 + 主窗口 screenshot ≥1 张 | 主上下文亲自 Read |
| **CLI** | 实际跑 1 次 end-to-end 命令 + 输出片段 ≥10 行 | 必含退出码 |
| **Library** | 集成测试真实调用 + 返回 200/正确字段 | 必含 API 调用证据 |
| **后端服务** | 健康检查端点返回 200 + 日志无 ERROR | 必含 health 路径 |

## 强约束（V10 §0.10）

- 可见产物必附 file:line 路径或 evidence_summary
- 不可用"看到进程即通过" / "vite 启动了应该没问题" / "截图不在本次范围"
- 与 §通过依据 [2] 区分: 本闸门是 Real Verify 实施者层（启动是否真跑通）

## 反例（3 条）

| # | 反例 | 详细 |
|:---:|------|------|
| 1 | "启动 = 完成" | anti-patterns/01-startup-equals-done.md |
| 2 | 容器未启声称迁移成功 | anti-patterns/02-container-not-started.md |
| 3 | 跳过 Playwright 截图 | anti-patterns/03-skip-screenshot.md |

## 参考索引

- [README.md](README.md)
- [startup-verification.md](references/startup-verification.md) — 5 类项目启动验证
- [visual-evidence.md](references/visual-evidence.md) — 视觉证据 3 层校验
- [blockage-report.md](references/blockage-report.md) — 5 字段阻塞报告
- V10 §0.10: `V10 来源` (已蒸馏到本文档)
- V10 实战蒸馏: [anti-patterns/V10-battle-tested.md](anti-patterns/V10-battle-tested.md)
