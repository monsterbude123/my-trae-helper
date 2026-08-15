---
name: fullstack-12-bug-fix
description: "Stage 6 统一工序 — Phase A 批量 bug 发现（14 模块 × 4 维度） + Phase B 单点 bug 修复（6 层排查 + TDD）+ 6 工具脚本 + 13 铁律 + 6 反例。触发词：bug / 修复 / e2e 先行 / 6 层排查 / debugger / bug-hunt / 受 auth 保护路由 / 真登录 7 步 / HMR / 截图归档 / 可见证据抽检。"
stage: 6
parent: fullstack4traev11
depends_on:
  skills: [gitnexus4Trae]
  stages: [-1/intake, 3.5/real-verify, 4/review]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/gitnexus-tools.md
    - ./references/gitnexus-6-layer.md
    - ./references/five-step-flow.md
    - ./references/six-layer-diagnosis.md
    - ./references/cross-layer-fix.md
    - ./references/bug-state-machine.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
    - ./references/bug-hunt-phase-a.md
    - ./references/bug-hunt-4d-observation.md
    - ./references/bug-hunt-5-check.md
    - ./references/bug-hunt-battle-report.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/gate-integrity-guard.py
    - ../../scripts/code-hygiene.py
    - ../../scripts/state-card-validator.py
    - ./scripts/bug-hunt/new-bug.sh
    - ./scripts/bug-hunt/close-bug.sh
    - ./scripts/bug-hunt/dev-hmr-recovery.sh
    - ./scripts/bug-hunt/dev-hmr-recovery.ps1
    - ./scripts/bug-hunt/archive-screenshot.sh
    - ./scripts/bug-hunt/archive-screenshot.ps1
---

> **V11.7.0+ 设计入口**:
> - **AC 核销门禁(Stage 4 Review)** → [skills/09-review/SKILL.md](../09-review/SKILL.md) + [acceptance-baseline-extract.md](../09-review/workflows/acceptance-baseline-extract.md)
> - **贾维斯门禁守护(防 agent 改标准)** → [skills/00-boot/SKILL.md](../00-boot/SKILL.md) + [agents/jarvis.md](../00-boot/agents/jarvis.md) + [gate-configuration-protocol.md](../../references/gate-configuration-protocol.md)

# Stage 6 Bug Fix & Hunt — 统一工序

> 第一性原则：**根因不明不修复 + e2e 先行证明 bug 真实存在 + 批量发现走 Phase A + 单点修复走 Phase B**。
>
> **V11.8.2 升级（2026-08-15 NEW）**：从原「5 步单点修复」扩为 **Phase A（3 步批量发现）+ Phase B（5 步单点修复）= 7 步统一工序**。同时把 bug-hunt-tooling skill 的工具脚本折叠进 Stage 6 子包（`scripts/bug-hunt/`），下次项目用 V11 自动带出 bug-hunt 能力，无需独立 install bug-hunt-tooling skill。

---

## 铁律（13 条 — V10 debugger.md + V11.8.2 bug-hunt 实战段蒸馏）

```
═══════ 共享铁律（bug 发现 + 修复通用）═══════
 1. 根因不明不修复     — 必 6 层排查 + GitNexus impact（Phase B）
 2. e2e 先行           — 必初始 FAIL（证明 bug 真实存在）（Phase B）
 3. INITIAL PASS = 不是 bug — e2e 初始 PASS → 回退 OPEN（Phase B）
 4. 障碍诚实           — 5 字段阻塞报告（V10 Article XV）
 5. SKEPTICAL VALIDATION — P0/P1 bug 修复按 skeptical-validation-protocol.md 质疑性校验

═══════ Phase A 专属铁律（批量发现）═══════
 6. 真登录取证必走       — 受 supabase auth 保护路由必走 7 步（详见 references/bug-hunt-phase-a.md §A.1）
 7. 4 维度观察法        — visual + behavior + data + console（详见 references/bug-hunt-4d-observation.md）
 8. 14 模块 ≥ 7 必委派   — V11 §1.6：模块数 ≤ 6 主代理亲自；> 6 必拆 sub-agent 并行
 9. bug 单生成必走脚本   — `scripts/bug-hunt/new-bug.sh` 替代手填 6 字段（V11 §8）
10. HMR 反复重 navigate — failure budget = 3；连续 3 次空文本 → `dev-hmr-recovery.{sh,ps1}`
11. 截图归档必走脚本    — `archive-screenshot.{sh,ps1}` 替代 Copy-Item
12. 5 项证据独立抽检    — Phase B 完成后主代理必跑（详见 references/bug-hunt-5-check.md）

═══════ Phase B 专属铁律（单点修复）═══════
13. 跨层修复最小化       — Ponytail bug 修复决策阶梯
14. 修复回写 bug 单     — bug 单 .md + index.md + .state-card.md 三文件同步（close-bug.sh）
```

---

## 7 步统一工序（V11.8.2 NEW）

```
════════════════════════════════════════════════════════════
Phase A 批量 bug 发现（前置工序，14 模块扫一次）
════════════════════════════════════════════════════════════
Step 1: 启动 dev + 真登录（受 auth 路由必走 7 步）
        → 详见 references/bug-hunt-phase-a.md §A.1
Step 2: 14 模块 × 4 维度观察（visible_text + behavior + data + console）
        → 详见 references/bug-hunt-4d-observation.md
        → ≥ 7 模块拆 sub-agent 并行（V11 §1.6）
Step 3: 批量落 bug 单（new-bug.sh 一键 6 字段）
        → 主代理补 Description + Fix；归档 screenshots
        → 详见 references/bug-hunt-phase-a.md §A.3

════════════════════════════════════════════════════════════
Phase B 单点 bug 修复（每个 bug 单走一次，可循环 N 次）
════════════════════════════════════════════════════════════
Step 4: 理解期望（读 bug 单 + spec.md INV + AC）
        → 沿用 references/five-step-flow.md Step 1
Step 5: e2e 先行（必初始 FAIL → 证明 bug 真实存在）
        → INITIAL PASS = 回退 OPEN
Step 6: 数据分析 + TDD 修复（GitNexus impact + 6 层排查 + RED → GREEN → REFACTOR）
        → 6 层排查：网络 / 接入 / 应用 / 数据 / 集成 / 客户端
        → 跨层修复最小化（Ponytail）
Step 7: 验收（5 项证据独立抽检 + bug 单 3 文件同步）
        → 详见 references/bug-hunt-5-check.md
        → close-bug.sh BUG-NNN <agent-id>（bug 单 .md + index.md + .state-card.md）
```

---

## 6 层排查（V10 debugger-methodology.md，Phase B Step 6 用）

| 层 | 检查 |
|----|------|
| **网络层** | curl / DNS / TLS / proxy |
| **接入层** | API gateway / 路由 / 限流 |
| **应用层** | 业务逻辑 / 中间件 / 状态 |
| **数据层** | DB schema / 索引 / 事务 |
| **集成层** | 第三方服务 / SDK |
| **客户端层** | UI / 缓存 / localStorage |

---

## 关键产物

| 产物 | 路径 | 阶段 |
|------|------|------|
| Bug 单 | `docs/bugs/{change-id}/BUG-NNN-{slug}.md` | Phase A Step 3 |
| 截图证据 | `docs/evidence/{date}/bug-hunt/{slug}.png` | Phase A Step 2 + 3 |
| e2e 测试 | `tests/e2e/test_{bug-id}.{py,ts}` | Phase B Step 5 |
| 修复代码 | `src/{module}/{file}.{ts,py,rs}` | Phase B Step 6 |
| 根因报告 | `docs/bugs/{change-id}/{bug-id}-root-cause.md`（可选）| Phase B Step 6 |
| 3 文件状态同步 | bug 单 .md + index.md + .state-card.md | Phase B Step 7 |

---

## 6 工具脚本（Stage 6 子包内 `scripts/bug-hunt/`）

> **不外挂独立 skill**——下次项目用 V11 自动带出，无需 `trae-cli add bug-hunt-tooling`。

| 脚本 | 用途 | 触发条件 | V11 §3.7 反例 |
|------|------|---------|---------------|
| `scripts/bug-hunt/new-bug.sh` | 6 字段 bug 单生成 | Phase A Step 3 落单 | §3.7 #2（脚本化） |
| `scripts/bug-hunt/close-bug.sh` | bug 单 3 文件同步回写 | Phase B Step 7 验收 | §3.7 #7（status 回写） |
| `scripts/bug-hunt/dev-hmr-recovery.sh` | HMR stale 4 步恢复（bash）| Phase A Step 1 启动 | §3.7 #5（脚本化） |
| `scripts/bug-hunt/dev-hmr-recovery.ps1` | HMR stale 4 步恢复（PowerShell）| 同上 Windows | §3.7 #5 |
| `scripts/bug-hunt/archive-screenshot.sh` | 截图归档（替代 Copy-Item）| Phase A Step 2 截图后 | §3.7 #2（脚本化） |
| `scripts/bug-hunt/archive-screenshot.ps1` | 截图归档（PowerShell）| 同上 Windows | §3.7 #2 |
| `tests/e2e/fixtures/auth-fixture.ts` | signedInPage fixture | Phase A Step 1 真登录（长期 e2e） | §3.7 #6（fixture 复用） |

**自验收命令**（铁律 6/9/10/11 必跑）：

```bash
# 铁律 6：真登录 fixture 复用
grep -rE "playwright_(navigate|fill).*signin" tests/e2e/

# 铁律 9：bug 单脚本生成
head -20 BUG-*.md | grep "generated by new-bug.sh"

# 铁律 10：HMR 恢复脚本可用
pwsh scripts/bug-hunt/dev-hmr-recovery.ps1 -DryRun  # Windows
bash scripts/bug-hunt/dev-hmr-recovery.sh -DryRun   # bash

# 铁律 11：截图归档脚本可用
pwsh scripts/bug-hunt/archive-screenshot.ps1 -DryRun
```

---

## 反模式（6 条 — V11.8.2 升级）

| # | 反例 | 阶段 | 详细 |
|:---:|------|:----:|------|
| 1 | 跳过 e2e 先行直接修 | Phase B | anti-patterns/01-skip-e2e-first.md |
| 2 | 跨层过度修复（违反 Ponytail）| Phase B | anti-patterns/02-cross-layer-overkill.md |
| 3 | 修复未回写 bug 单 | Phase B | anti-patterns/03-not-update-bug.md |
| 4 | 大小写不敏感比较违规 | Phase B | anti-patterns/04-case-insensitive-bug.md |
| 5 | 跳过真登录取证 7 步 | Phase A | anti-patterns/05-skip-real-login.md |
| 6 | 14 模块串行未委派 | Phase A | anti-patterns/06-serial-no-delegate.md |

---

## 参考索引

### V11 公共 references
- [state-card-protocol.md](../../references/state-card-protocol.md)
- [gitnexus-tools.md](../../references/gitnexus-tools.md)
- [stage-interaction-protocol.md](../../references/stage-interaction-protocol.md)
- [common-iron-rules.md](../../references/common-iron-rules.md)

### Stage 6 内部 references（5 步精简流程）
- [five-step-flow.md](references/five-step-flow.md) — Phase B Step 4-7
- [six-layer-diagnosis.md](references/six-layer-diagnosis.md) — Phase B Step 6
- [cross-layer-fix.md](references/cross-layer-fix.md) — Phase B Step 6
- [bug-state-machine.md](references/bug-state-machine.md) — OPEN/IN-FIX/FIXED/VERIFIED/CLOSED
- [gitnexus-6-layer.md](references/gitnexus-6-layer.md) — Phase B Step 6

### Stage 6 内部 references（V11.8.2 NEW Phase A 专属）
- [bug-hunt-phase-a.md](references/bug-hunt-phase-a.md) — Phase A 3 步流程（启动 / 观察 / 落单）
- [bug-hunt-4d-observation.md](references/bug-hunt-4d-observation.md) — 4 维度观察法
- [bug-hunt-5-check.md](references/bug-hunt-5-check.md) — 5 项证据独立抽检
- [bug-hunt-battle-report.md](references/bug-hunt-battle-report.md) — V11.8.2 实战报告（蒸馏自 2026-08-15 90 min / 14 模块 / 16 bug 全流程 + V11.5 5 缺漏）

### V10 来源
- V10 debugger.md
- V10 debugger-methodology.md
- V10 bug-workflow.md

---

## 变更日志（V11.8.2）

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-08-15 | V11.8.2 | Stage 6 扩为 7 步统一工序（Phase A 批量发现 + Phase B 单点修复）+ 13 铁律 + 6 反例 + 6 工具脚本折叠进 `scripts/bug-hunt/` 子包 + 实战报告迁入 Stage 6 references/ 子段。下次项目用 V11 自动带 bug-hunt 能力，无需独立 install bug-hunt-tooling skill。 |