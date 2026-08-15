# 意图 2：change-start（feature / refactor）— intent-types.md 详情

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 父文件：[../intent-types.md](../intent-types.md)
> 来源：原 intent-types.md 第 58-93 行（保留信息密度）

---

## 意图 2：change-start（feature / refactor）

**定义**: 在现有项目上新增功能或重构现有功能。

**触发词**:
- "新需求" / "新增功能" / "加个 X" / "增加 Y 功能"
- "重构" / "改造" / "重新设计" / "优化"

**子意图**:
- `feature` — 新增功能（如"加个用户登录"）
- `refactor` — 重构现有功能（如"把 X 拆成 Y"）
- `enhancement` — 增强现有功能（如"加个筛选"）
- `migration` — 数据迁移 / 版本升级（如"从 V1 升到 V2"）

**典型流程**:
```
Stage -1 Intake → Stage 0 Plan（change 级 plan.md）
  → Stage 0.5 Test Plan（验收维度 → 测试用例）
  → Stage 1 Spec（change 级 spec.md）
  → Stage 1.5 Prototype（如有 UI 改动）
  → Stage 2 Contract（change 级 contracts/）
  → Stage 3 Implement（change 级代码 + 测试）
  → Stage 3.5 Real Verify
  → Stage 4 Review
  → Stage 4.5 Rot Scan
  → Stage 5 Accept
```

**状态卡**: change 级（位置 `docs/specs/changes/{change-id}/.state-card.md`）

**change-id 规则**: `{YYYY-MM-DD}-{slug}`（如 `2026-08-11-add-user-auth`）

**关键产出**:
- `docs/specs/changes/{change-id}/plan.md`
- `docs/specs/changes/{change-id}/spec.md`
- `docs/specs/changes/{change-id}/contracts/`（四件套）
- 代码改动 + 测试 + 模块文档

---

## 关联引用

- 父文件：[../intent-types.md](../intent-types.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
