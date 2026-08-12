---
name: bug-fix
description: "Stage 6 独立专精流程 — 根因不明不修复 + e2e 先行 + 6 层排查 + TDD 修复。触发词：bug / 修复 / e2e 先行 / 6 层排查 / debugger。"
stage: 6
parent: fullstack4traev11
depends_on:
  skills: [gitnexus4Trae]
  stages: [-1/intake]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/gitnexus-tools.md
    - ./references/gitnexus-6-layer.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
  scripts:
    - ../../scripts/stage-gate.py
---

# Stage 6 Bug Fix — 独立专精流程

> 第一性原则：**根因不明不修复，e2e 先行证明 bug 真实存在**。

## 铁律（9 条 — V10 debugger.md 蒸馏）

```
1. 根因不明不修复     — 必 6 层排查 + GitNexus impact
2. e2e 先行           — 必初始 FAIL（证明 bug 真实存在）
3. INITIAL PASS = 不是 bug — e2e 初始 PASS → 回退 OPEN
4. 5 步精简流程       — 理解期望 → e2e 先行 → 数据分析 → TDD 修复 → 验收
5. TDD 即时           — 改实现同步改测试（V10 rot #12）
6. 跨层修复最小化     — Ponytail bug 修复决策阶梯
7. 修复回写 bug 单    — Bug 单状态 OPEN → CLOSED
8. 障碍诚实           — 5 字段阻塞报告（V10 Article XV）
9. SKEPTICAL VALIDATION — P0/P1 bug 修复按 [skeptical-validation-protocol.md](../../references/skeptical-validation-protocol.md) 质疑性校验
```

## 5 步精简流程（V10 debugger-methodology.md）

```
Step 1: 理解期望（读 bug 单 + spec.md + INV）
Step 2: e2e 先行（必初始 FAIL → 证明 bug 真实存在）
Step 3: 数据分析（GitNexus impact + 6 层排查）
Step 4: TDD 修复（RED → GREEN → REFACTOR）
Step 5: 验收（回归测试 + bug 单 CLOSED）
```

## 6 层排查（V10 debugger-methodology.md）

| 层 | 检查 |
|----|------|
| **网络层** | curl / DNS / TLS / proxy |
| **接入层** | API gateway / 路由 / 限流 |
| **应用层** | 业务逻辑 / 中间件 / 状态 |
| **数据层** | DB schema / 索引 / 事务 |
| **集成层** | 第三方服务 / SDK |
| **客户端层** | UI / 缓存 / localStorage |

## 关键产物

| 产物 | 路径 |
|------|------|
| Bug 单 | `docs/bugs/{bug-id}.md`（Intake 创建）|
| e2e 测试 | `tests/e2e/test_{bug-id}.py`（初始 FAIL → GREEN）|
| 修复代码 | `src/{module}/{file}.{ts,py,rs}` |
| 根因报告 | `docs/bugs/{bug-id}-root-cause.md`（可选）|

## 反模式（4 条）

| # | 反例 | 详细 |
|:---:|------|------|
| 1 | 跳过 e2e 先行直接修 | anti-patterns/01-skip-e2e-first.md |
| 2 | 跨层过度修复（违反 Ponytail）| anti-patterns/02-cross-layer-overkill.md |
| 3 | 修复未回写 bug 单 | anti-patterns/03-not-update-bug.md |
| 4 | 大小写不敏感比较违规 | anti-patterns/04-case-insensitive-bug.md |

## 参考索引

- [README.md](README.md)
- [five-step-flow.md](references/five-step-flow.md)
- [six-layer-diagnosis.md](references/six-layer-diagnosis.md)
- [cross-layer-fix.md](references/cross-layer-fix.md)
- [bug-state-machine.md](references/bug-state-machine.md)
- V10 debugger.md: `V10 来源` (已蒸馏到本文档)
- V10 debugger-methodology.md: `V10 来源` (已蒸馏到本文档)
- V10 bug-workflow.md: `V10 来源` (已蒸馏到本文档)
- V10 实战蒸馏: [anti-patterns/V10-battle-tested.md](anti-patterns/V10-battle-tested.md)
