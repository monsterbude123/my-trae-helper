# 意图 3：change-start (doc-sync) — intent-types.md 详情

> 父文件：[../intent-types.md](../intent-types.md)
> 来源：原 intent-types.md 第 97-118 行（保留信息密度）

---

## 意图 3：change-start (doc-sync)（文档同步）

**定义**: 同步文档与代码（drift 修复 / 归档后文档更新 / API 文档增量更新）。

**触发词**:
- "文档同步" / "更新文档" / "同步 spec"
- "doc sync" / "update README"

**典型流程**:
```
Stage -1 Intake → Stage 1 Spec（更新 spec.md）
  → Stage 5 Accept (lite) — 直接归档
  （可选 Stage 2 Contract 增量更新）
```

**状态卡**: change 级

**change-id 规则**: `{YYYY-MM-DD}-doc-sync-{slug}`（如 `2026-08-11-doc-sync-api-ref`）

**关键产出**:
- `docs/specs/changes/{change-id}/spec.md`（更新后的）
- 更新后的 docs/api-endpoints/ / domain-models/ / events/

---

## 关联引用

- 父文件：[../intent-types.md](../intent-types.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
