---
name: fullstack-07-implement
description: "Stage 3 TDD RED→GREEN — 契约驱动 + 深度业务理解 + TDD 三步循环 + 漂移检测。触发词：implement / 开发 / 写代码 / TDD / 测试 / code。"
stage: 3
parent: fullstack4traev11
depends_on:
  skills: [ponytail4Trae, gitnexus4Trae]
  stages: [2/contract]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
    - ../../references/common-anti-patterns.md
    - ./references/gitnexus-impact.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/code-hygiene.py
    - ../../scripts/orphan-detector.py
    - ../../scripts/dist-hash-check.py
    - ../../scripts/state-card-validator.py
---

# Stage 3 Implement — TDD RED→GREEN

> 第一性原则：**TDD RED→GREEN，最简实现优先**。契约为唯一入口，深度理解业务后再编码。

## 边界

| Implement 处理 | Implement 不处理 |
|---------------|----------------|
| TDD RED→GREEN 三步循环 | 规格编写 → Stage 1 Spec |
| 漂移检测 + 回流 | 契约编写 → Stage 2 Contract |
| 代码卫生 + 模块文档 | 验收 → Stage 4 Review |

## 铁律（10 条 — V10 implementer.md 蒸馏）

```
1. 深度理解再编码  — 读 spec+contracts → GitNexus context() → 输出"理解确认"（V10 铁律 1）
2. TDD 即时 + 红绿重构 — 改实现/删组件 → 立即同步改测试/删测试 + 🔴RED → 🟢GREEN → ♻️REFACTOR + 🔍DRIFT CHECK（V10 铁律 2 合并）
3. 漂移必报告      — 发现与 Spec/Contract 不一致 → 立即报告回流（V10 铁律 3）
4. 基础模块留文档   — 可作为增值功能基底的模块 → 产出接入文档（V10 铁律 4）
5. Bundle Staleness — 改 TS 后必跑 dist-hash-check.py，stale = 🛑 REJECT（V10 腐烂点 13）
6. 代码卫生        — 单文件 ≤ 800 行；函数 ≤ 50 行；禁止魔法数字（V10 铁律 6）
7. 量化必汇报 + 不量化不验收 — 输出 test: {pass}/{total}, contract_tests: {pass}/{total}, coverage: {X}% （V10 铁律 7）
8. 禁止虚假绿灯    — 不可修改测试让用例通过；不可跳过 TDD 🔴 阶段（V10 铁律 8）
9. SKEPTICAL VALIDATION — 实现方案/升级改动走 [skeptical-validation-protocol.md](../../references/skeptical-validation-protocol.md)
10. 禁止编造测试证据 — 禁 `tests/foo.test.ts:999` 实际不存在 / 禁 `grep` 充当覆盖（V10.12 ANTI-反模式 1+2）
```

## 骨架流程（4 步 — V10 implementer.md Step 1-4）

```
Step 1: 门禁检查（spec.md + contracts/ + state-card 存在）
Step 2: 深度理解（GitNexus context + modules/ 文档 → 输出"理解确认"）
Step 3: TDD 循环（tasks.md 逐项 🔴RED → 🟢GREEN → ♻️REFACTOR → 🔍DRIFT CHECK）
Step 4: 模块接入文档（条件触发）+ 量化汇报
```

## 关键产物

| 产物 | 路径 |
|------|------|
| 代码 | `src/{module}/{feature}.{ts,py,rs}` |
| 测试 | `__tests__/{unit,integration,e2e}/{feature}.test.*` |
| 模块文档 | `docs/modules/{module}/README.md`（条件触发）|
| 量化报告 | Completion Report 含 test/contract_tests/coverage |

## 量化汇报格式（Completion Report 4 字段）

```yaml
## Completion Report - Implementer
- artifacts: [代码路径 + 测试路径 + 模块文档路径]
- test: {pass}/{total}        # 必填（如 50/50）
- contract_tests: {pass}/{total}  # 必填（如 8/8）
- coverage: {X}%             # 必填（如 92%）
- status: ✓ | ⚠️ | ✗
```

**V10 铁律 7**: 缺一不验收。

## 反模式（5 条索引到 anti-patterns/）

| # | 反例 | V10 来源 |
|:---:|------|---------|
| 1 | 跳过 RED 直接写 GREEN | implementer 铁律 2 + 8 |
| 2 | 编造测试证据 | V10.12 ANTI-反模式 1+2 |
| 3 | 改实现不改测试（V10 rot #12）| implementer 铁律 2 合并 |
| 4 | 漂移静默（不报告回流）| implementer 铁律 3 |
| 5 | V10 实战蒸馏（rot #13 Bundle Staleness 独有）| implementer 铁律 5 |

## 参考索引

- [README.md](README.md)
- [tdd-workflow.md](references/tdd-workflow.md) — TDD 三步循环
- [code-hygiene.md](references/code-hygiene.md) — 代码卫生
- [drift-detect.md](references/drift-detect.md) — 漂移检测
- 公共铁律 Article I/VI/IX: [../../references/common-iron-rules.md](../../references/common-iron-rules.md)
- V10 实战蒸馏: [anti-patterns/V10-battle-tested.md](anti-patterns/V10-battle-tested.md)
