# 维度 1：代码维度（25%）— four-dim-acceptance.md 详情

> 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
> 来源：原 four-dim-acceptance.md 第 7-50 行（保留信息密度 — 含 4 维评分模板整体框架）

---

## 4 维度评分模板（含代码维度）

```yaml
review_scorecard:
  code:
    weight: 25%
    score: [0-5]
    evidence:
      unit_test_pass: "{n}/{n}"
      contract_test_pass: "{n}/{n}"
      coverage: "{x}%"
      lint_errors: 0
      todo_fixme_count: 0
  api:
    weight: 30%
    score: [0-5]
    evidence:
      endpoints_real: true
      signature_consistent: true
      data_model_consistent: true
      error_code_consistent: true
  uiux:
    weight: 25%
    score: [0-5]
    evidence:
      visual_consistency: true
      interaction_logic: true
      ui_details_checklist: 6/6
      screenshots: ["docs/verifications/{id}/default.png"]
  marginal:
    weight: 20%
    score: [0-5]
    evidence:
      # V10 reviewer-templates.md 4 项 GitNexus 检查（完整版）
      gitnexus_detect_changes: "[detect_changes 输出]"
      gitnexus_impact: "[impact(target) 列下游 + 公共模块影响面]"
      public_module_impact: "[公共模块变更 → impact() 输出]"
      regression_log: "[全量回归测试日志]"
      module_doc: "[模块接入文档路径 + 关键段]"
      extension_points: true
      docs_synced: true

total: "{Σ(score × weight) / Σ(weight)}"  # 加权平均
```

---

## 代码维度评分细则

**权重**: 25%

**evidence 字段**:
- `unit_test_pass`: 单元测试通过数 / 总数（必 100%）
- `contract_test_pass`: 契约测试通过数 / 总数（必 100%）
- `coverage`: 覆盖率（百分比）
- `lint_errors`: lint 错误数（必 0）
- `todo_fixme_count`: TODO/FIXME 数（必 0，桩代码另算）

**通过判定**:
- score ≥ 4.0 + 5 项 evidence 全 PASS
- 任一 evidence FAIL → 维度 score = 0 → 总分 REJECT

---

## 关联引用

- 父文件：[../four-dim-acceptance.md](../four-dim-acceptance.md)
- SKILL.md：[../../SKILL.md](../../SKILL.md)
