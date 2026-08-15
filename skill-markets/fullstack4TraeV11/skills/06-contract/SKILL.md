---
name: fullstack-06-contract
description: "Stage 2 契约四件套 — 契约是不可变的接口真相，先于实现。DOMAIN FIRST + ADDITIVE/BREAKING 变更流程 + 孤儿契约测试清理。触发词：contract / 契约 / API / 接口 / 领域模型 / schema / validation。"
stage: 2
parent: fullstack4traev11
depends_on:
  skills: [frontend-backend-contract-alignment]
  stages: [1.5/prototype]
  references:
    - ../../references/state-card-protocol.md
    - ../../references/stage-interaction-protocol.md
    - ../../references/common-iron-rules.md
  scripts:
    - ../../scripts/stage-gate.py
    - ../../scripts/gate-integrity-guard.py   # V11.7.0 NEW hash 锁校验
    - ../../scripts/orphan-detector.py
    - ../../templates/hooks/contract-gate.py
---

> **V11.7.0+ 设计入口**:
> - **AC 核销门禁(Stage 4 Review)** → [skills/09-review/SKILL.md](../09-review/SKILL.md) + [acceptance-baseline-extract.md](../09-review/workflows/acceptance-baseline-extract.md)
> - **贾维斯门禁守护(防 agent 改标准)** → [skills/00-boot/SKILL.md](../00-boot/SKILL.md) + [agents/jarvis.md](../00-boot/agents/jarvis.md) + [gate-configuration-protocol.md](../../references/gate-configuration-protocol.md)
> - **变更**: 评分制废除 → 门禁制;4 维详情转附加检查;`registry/gates.yaml` v1.2.0 加 layer 分层字段(docs/module/app/system)

# Stage 2 Contract — 契约四件套

> 第一性原则：**契约是不可变的接口真相，先于实现**。契约 approved 后不可单方面改。

## 边界

| Contract 处理 | Contract 不处理 |
|--------------|----------------|
| 领域模型 / API 契约 / 事件 / 校验规则 | 规格编写 → Stage 1 Spec |
| 孤儿契约测试清理 | 实施编码 → Stage 3 Implement |
| ADDITIVE / BREAKING 变更流程 | 验收 → Stage 4 Review |

## 铁律（10 条）

```
1. CONTRACT IS IMMUTABLE  — 契约 approved 后不可单方面改
2. DOMAIN FIRST           — 先定领域模型，再定接口（V10 实战）
3. ORPHAN TEST SWEEP      — 写新契约前必跑 orphan-detector.py 清理孤儿（V10 腐烂点 12）
4. ADDITIVE OVER BREAKING — 优先加法变更；破坏必用户确认
5. DELTA ONLY             — 只写增量，已有模型引用 docs/ 路径
6. CONTRACT DRIVES TEST   — 契约是 TDD 测试唯一依据
7. NO CODE NO CONTRACT    — 无已 approved 契约不写代码
8. CONTRACT-GATE          — contract-gate.py 必 PASS（4 件套齐全 + 测试骨架）
9. THREE-WAY SYNC         — 契约修改必同步改 docs/ 文档 + 测试代码（V10 配置治理 D-009）
10. SKEPTICAL VALIDATION   — P0/P1 修复按 [skeptical-validation-protocol.md](../../references/skeptical-validation-protocol.md) 质疑性校验
```

## 骨架流程（5 步）

```
Step 1: 读上游（spec.md + plan.md + ARCHITECTURE.md + 已批准 contracts/）
Step 2: domain-models.md（先于接口，含 INV）
Step 3: api-contracts.md + events.md + validation-rules.md
Step 4: orphan-detector.py 扫描 → 清理孤儿契约测试
Step 5: contract-gate.py 验证 → 状态卡更新 + 标记 approved
```

## 关键产物

| 产物 | 路径 |
|------|------|
| domain-models.md | `docs/specs/changes/{id}/contracts/domain-models.md` |
| api-contracts.md | `docs/specs/changes/{id}/contracts/api-contracts.md` |
| events.md | `docs/specs/changes/{id}/contracts/events.md`(如 INV 含跨服务事件则必填,否则可缺 — 详见 `references/contract-four-suite.md §1.3`) |
| validation-rules.md | `docs/specs/changes/{id}/contracts/validation-rules.md` |
| 测试骨架 | `__tests__/contracts/*.test.{ts,py,rs}` |

## ADDITIVE / BREAKING 变更流程

| 类型 | 流程 | 版本 |
|------|------|------|
| **ADDITIVE**（新增可选字段/接口）| 直接添加 + 通知 | minor |
| **BREAKING**（删字段/改类型/改路径）| **必用户确认** | major |

**V10 实战（D-009）**: 前后端 config key 大小写不一致（前端 camelCase / 后端 regex 严格小写）。修复走 BREAKING 流程，必用户确认 + 3 处同步（代码 + 契约文档 + 测试）。

## 反模式（5 条索引到 anti-patterns/）

| # | 反例 | 文件 |
|:---:|------|------|
| 1 | 跳过 DOMAIN FIRST 直接写 API | anti-patterns/01-skip-domain.md |
| 2 | 跳过孤儿契约测试清理 | anti-patterns/02-skip-orphan-sweep.md |
| 3 | BREAKING 变更不用户确认 | anti-patterns/03-breaking-without-confirm.md |
| 4 | 契约漂移（代码与契约不一致）| anti-patterns/04-contract-drift.md |
| 5 | V10 实战蒸馏 | anti-patterns/V10-battle-tested.md |

## 参考索引

- [README.md](README.md)
- [contract-four-suite.md](references/contract-four-suite.md) — 四件套详细规则
- [orphan-test-sweep.md](references/orphan-test-sweep.md) — 孤儿测试扫描
- 4 个契约模板: [templates/](templates/)
- 公共铁律 Article VIII: [../../references/common-iron-rules.md](../../references/common-iron-rules.md)
- V10 实战参考: [anti-patterns/V10-battle-tested.md](anti-patterns/V10-battle-tested.md)
