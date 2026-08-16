---
name: fullstack-12-bug-fix
description: "Stage 6 Bug 处理分层决策框架 — 4 层通用模型：发现(4D观察+覆盖策略) → 严重性分波(L1/L2/L3优先级+Wave回归) → 修复(6层排查+e2e先行+最小化) → 收敛(预算驱动停止+产物落盘)。不规定具体模块数/步骤数，适用于任何项目规模。触发词：bug / 修复 / e2e 先行 / 严重性分波 / 波次修复 / 预算驱动 / 6 层排查 / bug-hunt。"
stage: 6
parent: fullstack4traev11
depends_on:
  skills: [gitnexus4Trae]
  stages: [-1/intake, 3.5/real-verify, 4/review]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/gitnexus-tools.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
    - ./references/bug-layer-1-discovery.md
    - ./references/bug-layer-2-severity.md
    - ./references/bug-layer-3-repair.md
    - ./references/bug-layer-4-convergence.md
    - ./references/gitnexus-6-layer.md
    - ./references/five-step-flow.md
    - ./references/six-layer-diagnosis.md
    - ./references/cross-layer-fix.md
    - ./references/bug-state-machine.md
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

# Stage 6 Bug Fix — 分层决策框架

> **第一性原则**：**根因不明不修复 + e2e 先行证明 bug 真实存在 + 严重性分波处理 + 预算驱动停止**。
>
> **V11.8.3 升级（2026-08-15）**：从"7步统一工序"升级为"**4 层分层决策框架**"——不规定具体模块数/步骤数，而是提供通用决策模型，适用于任何项目规模。

---

## 4 层分层决策框架

```
┌─────────────────────────────────────────────────────────────┐
│           Layer 1 发现分层 — 怎么发现 bug                    │
│  决策：维度选择(4D) + 覆盖策略 + 委派决策                     │
│              ↓ 产出：Bug 候选清单                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           Layer 2 严重性分层 — 按什么优先级修                │
│  决策：L1/L2/L3 分类 + Wave 分波 + 时间预算分配              │
│              ↓ 产出：波次修复计划                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           Layer 3 修复分层 — 如何修单个 bug                  │
│  决策：根因定位(6层) + 修复范围(Ponytail) + 验证策略(e2e)    │
│              ↓ 产出：修复代码 + e2e 测试                     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│           Layer 4 收敛分层 — 何时停止                        │
│  决策：停止条件 + 产物落盘 + 遗留处理                        │
│              ↓ 产出：完成报告 + 遗留清单                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 分层决策铁律（每层核心铁律）

```
═══════ Layer 1 发现铁律 ═══════
 L1.1 单维度不可证伪      — 必多维度交叉验证（视觉+行为+数据+控制台）
 L1.2 认证路由必先登录    — 受 auth 保护路由必先取得登录态再取证
 L1.3 大规模必委派        — 路由数 > 6 必拆 sub-agent 并行

═══════ Layer 2 严重性铁律（V11.8.3 核心）═══════
 L2.1 L1 阻断立即修        — 单独修，修完才继续
 L2.2 每波必回归          — Wave 1/2/3 后各自回归验证
 L2.3 预算耗尽即停止      — ROI 驱动，不硬撑

═══════ Layer 3 修复铁律 ═══════
 L3.1 根因不明不修复      — 必 6 层排查 + GitNexus impact()/context()
 L3.2 e2e 先行            — 必初始 FAIL（证明 bug 真实存在）
 L3.3 INITIAL PASS = 不是 bug — e2e 初始 PASS → 回退 OPEN
 L3.4 跨层修复最小化      — Ponytail 决策阶梯
 L3.5 修复回写 bug 单     — bug 单 .md + index.md + .state-card.md
 L3.6 **GITNEXUS FIRST（V11.8.5 NEW — 蒸馏自 agent 不使用 gitnexus）** — Step L3.1 必跑 GitNexus impact()/context()/query() 至少 2 个调用，禁止仅靠 6 层排查不查代码图谱（Article V 不可降级）

═══════ Layer 4 收敛铁律 ═══════
 L4.1 L1 未清零不结束      — 核心阻断优先
 L4.2 遗留必上报          — 未修完的 L1/L2 必上报
 L4.3 5 项证据独立抽检    — 收敛前主代理必跑 M6.1-M6.5
```

---

## 分层决策流程

### Step 0 — 4 步流程门禁串接（V11.8.x P2-2 NEW）

Stage 6 Bug Fix 流程必须通过 `repair-flow-gate.py --strict` 机械串联 4 步流程（见 [registry/repair-flow.yaml](../../registry/repair-flow.yaml) L97-110）：
`step-1-e2e-fail` → `step-2-6layer` → `step-3-fix-and-regression` → `step-4-user-confirm`

**Step 1 / Step 2 / Step 3 入口硬约束**（每个 step 启动前必跑）：

```bash
# Step 1 入口
python scripts/repair-flow-gate.py --step step-1-e2e-fail --strict \
    --evidence-paths <step-1.md>,<step-2.md>,<step-3.md>,<step-4.md>
# 期望: step-1 首次跑可不带 step-2/3/4 实际文件,先建占位;但数量 + 顺序必须按 P2_2_STEP_ORDER
```

**Step 4 跑前必前 3 步证据齐**（stage 流转强制阻断）：

```bash
# Step 4 入口:前 3 步证据文件必须存在,顺序正确
python scripts/repair-flow-gate.py --step step-4-user-confirm --strict \
    --evidence-paths docs/bugs/<bug-id>/step-1-e2e-fail.md,docs/bugs/<bug-id>/step-2-6layer.md,docs/bugs/<bug-id>/step-3-fix-and-regression.md,docs/bugs/<bug-id>/step-4-user-confirm.md
# 退出码: 0 = PASS(step 流转允许); 1 = FAIL(stage 流转阻断)
```

**失败处理**（V11.8.x P2-2 强制）：

- strict 模式失败 → **禁止** 推进到下一 stage / 关闭 bug
- 错误消息含「预期 4 项 / 顺序映射 / 缺失文件」三类,必须先修复再重跑
- 失败证据写入 `docs/bugs/<bug-id>/strict-fail-<timestamp>.log` 供 review 阶段追溯

---

### Layer 1 发现分层

```
Step L1.1: 维度选择
    → 选择观察维度：视觉 / 行为 / 数据 / 控制台（至少 2D）
    → 详见 [bug-layer-1-discovery.md](references/bug-layer-1-discovery.md) §L1.1

Step L1.2: 覆盖策略
    → 根据项目阶段选择：冒烟覆盖 / 全量覆盖 / 重点覆盖
    → 冒烟：核心路由（登录/支付/主流程）
    → 全量：所有公开路由 + 认证路由
    → 重点：本次变更影响范围
    → 详见 [bug-layer-1-discovery.md](references/bug-layer-1-discovery.md) §L1.2

Step L1.3: 委派决策
    → 路由数 ≤ 6：主代理亲自
    → 路由数 > 6：拆 sub-agent 并行
    → 详见 [bug-layer-1-discovery.md](references/bug-layer-1-discovery.md) §L1.3

Step L1.4: 执行观察
    → 按选定维度 + 覆盖策略 + 委派方式执行
    → 认证路由走登录态获取流程（技术栈决定具体步骤）
    → 输出：Bug 候选清单 + 截图证据
```

### Layer 2 严重性分层

```
Step L2.1: 严重性判定
    → 每个候选 bug 判定 L1/L2/L3/L4
    → L1 阻断：核心流程完全无法使用
    → L2 不可用：功能缺陷但不阻断
    → L3 视觉瑕疵：UI 问题，功能正常
    → 详见 [bug-layer-2-severity.md](references/bug-layer-2-severity.md) §L2.1

Step L2.2: 波次分配
    → Wave 1（冒烟波）：只修 L1，修完回归
    → Wave 2（功能波）：按模块分批修 L2（每批 ≤ 3）
    → Wave 3（细节波）：批量修 L3（可 ≤ 5 一批）
    → 详见 [bug-layer-2-severity.md](references/bug-layer-2-severity.md) §L2.2

Step L2.3: 时间预算分配
    → 发现阶段 20% + 修复阶段 60% + 收敛阶段 20%
    → 预算耗尽即停止，统计剩余上报
    → 详见 [bug-layer-2-severity.md](references/bug-layer-2-severity.md) §L2.4
```

### Layer 3 修复分层（每个 bug 执行一次）

```
Step L3.1: 根因定位
    → 6 层排查：网络 → 接入 → 应用 → 数据 → 集成 → 客户端
    → GitNexus 影响面评估（V11.8.5 NEW — 必跑 3 调用）：
       L3.1.1 mcp__gitnexus__impact(target=故障symbol, direction=upstream) → 受影响符号列表
       L3.1.2 mcp__gitnexus__context(name=故障symbol) → 调用链
       L3.1.3 mcp__gitnexus__query(query=相关concept) → 概念相关其他符号
    → 禁止 grep/Glob 替代（Article V 不可降级）
    → 详见 [bug-layer-3-repair.md](references/bug-layer-3-repair.md) §L3.1

Step L3.2: 修复范围决策
    → Ponytail 最小化：改配置 < 改单文件 < 改多文件 < 改架构
    → 详见 [bug-layer-3-repair.md](references/bug-layer-3-repair.md) §L3.2

Step L3.3: e2e 先行 + TDD
    → 写 e2e 复现 bug → 必 FAIL → 修复 → 必 PASS → 回归
    → INITIAL PASS = 不是 bug，回退 OPEN
    → 详见 [bug-layer-3-repair.md](references/bug-layer-3-repair.md) §L3.3

Step L3.4: 状态同步
    → close-bug.sh BUG-NNN <agent-id>
    → bug 单 .md + index.md + .state-card.md 三文件同步
    → 详见 [bug-layer-3-repair.md](references/bug-layer-3-repair.md) §L3.4
```

### Layer 4 收敛分层

```
Step L4.1: 停止条件判定
    → L1 + L2 清零 → 正常结束
    → 预算耗尽 → 统计剩余上报
    → 发现无法修复的 L1 → 立即阻断上报
    → 详见 [bug-layer-4-convergence.md](references/bug-layer-4-convergence.md) §L4.1

Step L4.2: 5 项证据独立抽检
    → M6.1 截图与 bug 单对应
    → M6.2 visible_text 关键字验证
    → M6.3 console 无 error
    → M6.4 三文件状态同步
    → M6.5 git diff 范围验证
    → 详见 [bug-hunt-5-check.md](references/bug-hunt-5-check.md)

Step L4.3: 产物落盘 + 遗留上报
    → Bug 单 + e2e 测试 + 截图证据
    → 遗留 L1/L2 必上报，L3 可延后
    → 详见 [bug-layer-4-convergence.md](references/bug-layer-4-convergence.md) §L4.3-§L4.4
```

---

## 6 层排查（Layer 3 Step L3.1 用）

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

| 产物 | 路径 | 分层 |
|------|------|------|
| Bug 单 | `docs/bugs/{change-id}/BUG-NNN-{slug}.md` | Layer 1 → Layer 4 |
| 截图证据 | `docs/evidence/{date}/bug-hunt/{slug}.png` | Layer 1 |
| 严重性分类 | bug 单 `severity` 字段 | Layer 2 |
| e2e 测试 | `tests/e2e/test_{bug-id}.{py,ts}` | Layer 3 |
| 修复代码 | `src/{module}/{file}.{ts,py,rs}` | Layer 3 |
| 完成报告 | `docs/bugs/{change-id}/bug-hunt-report.md` | Layer 4 |

---

## 工具脚本（Stage 6 子包内 `scripts/bug-hunt/`）

| 脚本 | 用途 | 触发分层 |
|------|------|---------|
| `scripts/bug-hunt/new-bug.sh` | 6 字段 bug 单生成 | Layer 1 |
| `scripts/bug-hunt/close-bug.sh` | bug 单 3 文件同步 | Layer 3 |
| `scripts/bug-hunt/dev-hmr-recovery.sh` | HMR stale 4 步恢复 | Layer 1 |
| `scripts/bug-hunt/archive-screenshot.sh` | 截图归档 | Layer 1 |

---

## 反模式（6 条）

| # | 反例 | 分层 | 详细 |
|:---:|------|:----:|------|
| 1 | 单维度判定 PASS | L1 | 只截图不读可见文本 |
| 2 | 跳过 e2e 先行直接修 | L3 | 无法证明修复有效 |
| 3 | 跨层过度修复 | L3 | 违反 Ponytail |
| 4 | 修复未回写 bug 单 | L3 | 状态不同步 |
| 5 | 所有 bug 一视同仁修 | L2 | L1 未优先 |
| 6 | 预算耗尽仍继续修 | L4 | ROI 低 |

---

## 参考索引

### 4 层分层决策 references（V11.8.3 核心）
- [bug-layer-1-discovery.md](references/bug-layer-1-discovery.md) — 发现分层决策
- [bug-layer-2-severity.md](references/bug-layer-2-severity.md) — 严重性分波决策
- [bug-layer-3-repair.md](references/bug-layer-3-repair.md) — 修复分层决策
- [bug-layer-4-convergence.md](references/bug-layer-4-convergence.md) — 收敛分层决策

### 辅助 references
- [bug-hunt-4d-observation.md](references/bug-hunt-4d-observation.md) — 4 维度观察法
- [bug-hunt-5-check.md](references/bug-hunt-5-check.md) — 5 项证据独立抽检
- [bug-hunt-battle-report.md](references/bug-hunt-battle-report.md) — V11.8.2 实战报告
- [six-layer-diagnosis.md](references/six-layer-diagnosis.md) — 6 层排查详细
- [cross-layer-fix.md](references/cross-layer-fix.md) — 跨层修复决策
- [bug-state-machine.md](references/bug-state-machine.md) — OPEN/IN-FIX/FIXED/VERIFIED/CLOSED

### V11 公共 references
- [state-card-protocol.md](../../references/state-card-protocol.md)
- [gitnexus-tools.md](../../references/gitnexus-tools.md)
- [common-iron-rules.md](../../references/common-iron-rules.md)

---

## 变更日志

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-08-15 | V11.8.3 | Stage 6 重构为 4 层分层决策框架（发现 → 严重性 → 修复 → 收敛），不规定具体模块数/步骤数，提供通用决策模型。新增 Layer 2 严重性分波（Wave 1/2/3 + 回归），解决 V11.8.2 批处理效率问题。 |
| 2026-08-15 | V11.8.2 | Stage 6 扩为 7 步统一工序（Phase A 批量发现 + Phase B 单点修复）+ 13 铁律 + 6 反例 + 6 工具脚本。 |