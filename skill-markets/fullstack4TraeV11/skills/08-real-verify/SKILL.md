---
name: fullstack-08-real-verify
description: "Stage 3.5 启动可见产物 — 唯一信任基础，不接受自评。环境依赖 + 真实验证 + 启动可见产物 + 阻塞处理。触发词：real verify / 启动验证 / 真实验证 / visible product。"
stage: 3.5
parent: fullstack4traev11
depends_on:
  skills: [visual-evidence-discipline, screenshot, playwright-best-practices]
  stages: [3/implement]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/stage-08-real-verify-battle-report.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/gate-integrity-guard.py   # V11.7.0 NEW hash 锁校验
    - ../../scripts/dist-hash-check.py
    - ../../scripts/visual-content-check.py
---

> **V11.7.0+ 设计入口**:
> - **AC 核销门禁(Stage 4 Review)** → [skills/09-review/SKILL.md](../09-review/SKILL.md) + [acceptance-baseline-extract.md](../09-review/workflows/acceptance-baseline-extract.md)
> - **贾维斯门禁守护(防 agent 改标准)** → [skills/00-boot/SKILL.md](../00-boot/SKILL.md) + [agents/jarvis.md](../00-boot/agents/jarvis.md) + [gate-configuration-protocol.md](../../references/gate-configuration-protocol.md)
> - **变更**: 评分制废除 → 门禁制;4 维详情转附加检查;`registry/gates.yaml` v1.2.0 加 layer 分层字段(docs/module/app/system)

# Stage 3.5 Real Verify — 启动可见产物

> 第一性原则：**启动可见产物是唯一信任基础，不接受自评**。V10 §0.10 NEW 防虚假交付。

## 边界

| Real Verify 处理 | Real Verify 不处理 |
|-----------------|-------------------|
| 环境依赖检查 + 真实验证 + 启动可见产物 | 实施编码 → Stage 3 Implement |
| 阻塞报告（V10 Article XV）| 验收 → Stage 4 Review |

> **📎 qa-loop 提测闭环（V11.9 角色协议 NEW）**: 本阶段产出的"启动可见产物 + 运行中的应用进程"是 **qa-loop 提测闭环**（重启应用 → 步骤 1.5 自验证 → 委派测试专家 → 收报告修复 → 循环终止交接）的入口基础。真实验证确认"能启动、有可见产物"后，若无 L1/L2 bug 遗留，即可进入 [docs/specs/qa-loop.md](../../docs/specs/qa-loop.md) 走代码提测 ↔ 测试专家闭环；qa-loop 的修复内核（6 层排查 + e2e 先行 + GitNexus）见 Stage 6 [12-bug-fix/SKILL.md](../12-bug-fix/SKILL.md)。

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
| **Web** | curl localhost 返回 200 + **真实浏览器端到端 UI 截图（含本 change 实施 + 端到端可交互）** | 必含 file:line 路径 + 实施组件 ID/class/role 标注 |
| **Tauri** | `tauri dev` 进程存活 + 主窗口 screenshot ≥1 张 | 主上下文亲自 Read |
| **CLI** | 实际跑 1 次 end-to-end 命令 + 输出片段 ≥10 行 | 必含退出码 |
| **Library** | 集成测试真实调用 + 返回 200/正确字段 | 必含 API 调用证据 |
| **后端服务** | 健康检查端点返回 200 + 日志无 ERROR | 必含 health 路径 |

**真实浏览器端到端 UI 截图硬约束（V11.2 NEW — 蒸馏自 canvas-asset-folders）**：

- ✅ 必须用 Playwright MCP / Chrome DevTools MCP / 真实浏览器 驱动
- ✅ 截图必须包含本 change 实施的关键 UI 组件 ID/class/role
- ✅ 截图必须证明端到端可交互（点击 → API 调用 → 状态变化）
- ❌ 禁止 prototype 截图 / mock 截图 / 拼图截图
- ❌ 禁止"API 兜底全 PASS + 单元测试全 PASS" 等于 "UI 集成层 PASS" — 三层独立验证
- 失败处理：任何 1 项不满足 → 标记 FAIL + revert stage_status to in_progress + 清理虚假痕迹（截图 / 脚本 / 虚假 README）
- 反例：[anti-patterns/03-skip-screenshot.md](anti-patterns/03-skip-screenshot.md) §B 反例 2026-08-12-canvas-asset-folders

## 强约束（V10 §0.10）

- 可见产物必附 file:line 路径或 evidence_summary
- 不可用未验证断言充当通过依据(如"看到进程即通过"/"启动成功即认为运行正常"/"截图不在本次范围")
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
