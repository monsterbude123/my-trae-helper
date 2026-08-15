# Four-Dimension Acceptance — Stage 4 Review — 总览(已废弃 V11.6.0)

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> **V11.6.0 废弃声明**:4 维评分体系已废除,门禁替代为 [acceptance-baseline-extract.md](acceptance-baseline-extract.md) + [ac-gate.py](../../scripts/ac-gate.py) 的 AC 核销判定。
>
> 本文档保留作历史摘要,不再用于判定;dim1-dim4 详情转为**条件触发附加检查**归档(详见 [SKILL.md §附加检查](../SKILL.md))。

---

## 4 维度章节指针(仅供考古)

| 维度 | 弃用权重 | 现状 | 文件 |
|------|:---:|------|------|
| 代码 | 25% | 附加检查(归档) | [dim1-code.md](./four-dim-detail/dim1-code.md) |
| API | 30% | 附加检查(契约对齐) | [dim2-api.md](./four-dim-detail/dim2-api.md) |
| UI/UX | 25% | 附加检查(仅 ui-ux-logic 声明的状态) | [dim3-uiux.md](./four-dim-detail/dim3-uiux.md) |
| 边际（4 项 GitNexus 检查 + 主动证伪 + 失败标签 + 自动循环） | 20% | [dim4-edge.md](./four-dim-detail/dim4-edge.md) |
| 反例（3 条） | — | [anti-patterns.md](./four-dim-detail/anti-patterns.md) |

---

## 4 维评分公式

```
总分 = (通过维度 / 适用维度) × 5.0
- 任一维度 0 分 = 🛑 REJECT
- 总分 ≥ 4.0 才 PASS
- N/A 不计入分母（不可验证才标 N/A + 理由）
```

**4 维权重**:
- 代码 25% / API 30% / UI/UX 25% / 边际 20%
- 完整 scorecard 模板在 [dim1-code.md](./four-dim-detail/dim1-code.md)

---

## 必读

- 4 维评分模板集中在 `dim1-code.md`（含完整 YAML 模板）
- 边际维度含 V10 完整 4 项 GitNexus 检查，详 `dim4-edge.md`
- 反例（3 条）含凑分 / reviewer 改代码 / 边际只跑 impact 三个高频错，详 `anti-patterns.md`

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [four-dimension-scoring.md](../references/four-dimension-scoring.md)
- [skeptical-acceptance.md](../references/skeptical-acceptance.md)
- [multi-round-revision.md](../references/multi-round-revision.md)
- [GitNexus 失败处理协议](../../../references/gitnexus-retry-protocol.md)
- V10 来源（开发期，已蒸馏）: 见 V11 references 与 anti-patterns（部署时不依赖）references/reviewer-templates.md`
