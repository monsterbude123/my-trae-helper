# Four-Dimension Acceptance — Stage 4 Review

> Stage 4 Review 必走。4 维验收协议。

---

## 4 维度评分模板

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
      gitnexus_impact: "无下游副作用"
      docs_synced: true
      extension_points: true

total: "{Σ(score × weight) / Σ(weight)}"  # 加权平均
```

---

## 评分公式

```
总分 = (通过维度 / 适用维度) × 5.0
- 任一维度 0 分 = 🛑 REJECT
- 总分 ≥ 4.0 才 PASS
- N/A 不计入分母（不可验证才标 N/A + 理由）
```

---

## 主动证伪（高风险清单核查）

```yaml
falsification_checklist:
  - check: "边界遗漏"
    how: "测 0/1/max/null/空字符串/极大值"
  - check: "依赖污染"
    how: "检查 import 是否全在 pyproject.toml/package.json"
  - check: "未提交文件"
    how: "git status | grep untracked"
  - check: "隐藏 TODO"
    how: "grep -E 'TODO|FIXME|XXX' src/"
  - check: "测试篡改"
    how: "比对测试 commit + 验证断言非空"
  - check: "桩代码标记"
    how: "grep -E 'STUB|NotImplementedError' src/  # 必明确标识"
```

---

## 失败标签（Stage 2.6 自动循环）

| 标签 | 含义 |
|------|------|
| `MISMATCH` | 货不对版（功能与 spec 不符）|
| `UNDERPERFORM` | 功能不达标 |
| `USER_VIEW_FAIL` | 用户视角 FAIL |
| `TEST_GAP` | 测试覆盖缺口 |
| `DRIFT` | 代码与契约漂移 |

---

## 自动循环协议

```
Round 1: 退回 implementer 重做 + 失败标签必填
Round 2: 升级上报用户（5 字段阻塞报告）
Round 3+: rescue hatch — 回退 Phase 0（Intake）
```

---

## 输出: review-report.md

```yaml
# Review Report: {change-id}

## 4 维评分

| 维度 | 权重 | 评分 | evidence |
|------|------|------|----------|
| 代码 | 25% | [0-5] | ... |
| API | 30% | [0-5] | ... |
| UI/UX | 25% | [0-5] | ... |
| 边际 | 20% | [0-5] | ... |

**总分**: [Σ]

## 主动证伪

- [ ] 边界遗漏？
- [ ] 依赖污染？
- ...

## 结论

[ ] PASS（≥4.0 + 4 维全评 + 证据齐全 + 用户签字）
[ ] REJECT（任一 FAIL → 失败标签）
```

---

## 反例

### 反例 A：凑分

```
代码 3.0 / API 4.0 / UIUX 2.5 / 边际 3.0 → 总分 3.1  # ❌
正确: 任一维度 0 分 = REJECT
```

### 反例 B：reviewer 改代码

```
reviewer: 发现代码 bug → 直接 Edit  # ❌ REVIEWER DOES NOT FIX
正确: 退回 implementer 修改
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [four-dimension-scoring.md](../references/four-dimension-scoring.md)
- [skeptical-acceptance.md](../references/skeptical-acceptance.md)
- [multi-round-revision.md](../references/multi-round-revision.md)