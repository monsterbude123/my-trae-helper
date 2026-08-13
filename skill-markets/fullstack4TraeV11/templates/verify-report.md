# Verify Report: {change-id}

> 位置: `docs/specs/changes/{id}/verify-report.md`
> 编制依据: Stage 3 实施产物 + Stage 3.5 启动验证 + 视觉证据（V11.2 NEW）
> V11.2 NEW: 必须含 `## 视觉证据 (visual-evidence-Layer-1)` 子节，含真实浏览器截图

---

## 启动验证（5 项必跑）

| # | 项目 | 验证产物 | 状态 |
|---|------|---------|------|
| 1 | 环境依赖（DB / 缓存 / .env / 端口）| {evidence} | {PASS/FAIL} |
| 2 | 真实验证执行（迁移 / 测试 / 类型检查 / dev 启动）| {evidence} | {PASS/FAIL} |
| 3 | 启动可见产物（按项目类型 5 类之一）| {evidence} | {PASS/FAIL} |
| 4 | 阻塞诚实（如有 FAIL → 5 字段阻塞报告）| {evidence} | {PASS/FAIL/N/A} |
| 5 | 主上下文必查（亲自 Read 截图 / 不委派子代理）| {evidence} | {PASS/FAIL} |

---

## 视觉证据（visual-evidence-Layer-1）（V11.2 NEW — 蒸馏自 canvas-asset-folders）

> **Web 类必跑第 6 项**：API 兜底 PASS + 单元测试 PASS ≠ UI 集成层 PASS — 三层独立验证。

### 必含清单

- [ ] **真实浏览器截图 ≥1 张**（Playwright MCP / Chrome DevTools MCP / 真实浏览器驱动，禁止 prototype/mock/拼图）
- [ ] **截图内容含本 change 实施的 UI 组件**（必填：组件 ID/class/role 列表）
- [ ] **截图证明端到端可交互**（click → API 调用 → 状态变化）
- [ ] **截图落盘路径**：`docs/verifications/web/{change-id}/{screenshot-name}.png`
- [ ] **主上下文亲自 Read PNG 验证**（不委派子代理，禁止 AI 描述代替像素）

### 截图登记表

| 截图名 | 路径 | 含本 change 组件 | 端到端可交互证明 | 主上下文已 Read PNG |
|--------|------|----------------|---------------|-------------------|
| {name} | {path} | {component-id/class/role} | {click→API→state} | {true/false + file:line} |

### 视觉证据失真检测

```bash
# V11.2 NEW: 主上下文亲自验证截图（必跑）
# 检查项：截图 PNG 大小 ≥5KB + 7 天内 + 含本 change 组件 + 非 generic 页面
python ~/.trae-cn/skills/fullstack4TraeV11/scripts/visual-content-check.py \
  --project-root . --change-id {change-id}
```

### 三层独立验证声明（V11.2 NEW）

| 验证层 | 方法 | 状态 | evidence |
|-------|------|------|----------|
| 单元测试层 | vitest run | {PASS/FAIL} | {test 输出} |
| API 真实链路层 | curl + service token | {PASS/FAIL} | {6/6 链路} |
| **UI 集成层** | **真实浏览器截图 + 交互证据** | **{PASS/FAIL}** | **{本节视觉证据}** |

> 警告：API PASS + Unit PASS ≠ UI 集成层 PASS。任何 1 层 FAIL → 整体 FAIL。

---

## 5 字段阻塞报告（如有）

```yaml
type: "{env_dependency|test_fail|type_error|startup_fail|ui_integration_fail|visual_evidence_fail}"
description: "{具体错误信息}"
attempted_solution: "{已尝试方案}"
time_consumed_minutes: {N}
attempt_count: {N}
```

---

## 验收签字

- 主上下文 Read PNG 验证：{timestamp} + {file:line}
- state-card visual_evidence.status：{verified | unverified}
- Stage 3.5 → Stage 4 推进门禁：{PASS/FAIL}

---

## 关联引用

- [Stage 3.5 SKILL.md §3.5 5 类项目启动验证](d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\skills\08-real-verify\SKILL.md)
- [anti-patterns/03-skip-screenshot.md §B 截图无实施](d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\skills\08-real-verify\anti-patterns\03-skip-screenshot.md)
- [references/visual-evidence.md](d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\skills\08-real-verify\references\visual-evidence.md) — 视觉证据 3 层校验
- [state-card-protocol.md §2.1 visual_evidence_verified 字段](d:\workspace\my-trae-helper\skill-markets\fullstack4TraeV11\references\state-card-protocol.md)
- 蒸馏来源：2026-08-12-canvas-asset-folders 会话 + session-distiller V2.1