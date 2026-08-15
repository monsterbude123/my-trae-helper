# Test Plan Template — Stage 0.5 Test Plan

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 位置: `docs/specs/changes/{id}/test-plan.md`

---

```yaml
# Test Plan: {change-id}

## 1. 测试场景清单

来源: spec.md AC + Edge Cases + 业务 E2E 场景
总数: {N} 个场景

| ID | 描述 | 来源 AC | 类型 | 优先级 |
|----|------|---------|------|--------|
| P0-S1 | {场景} | AC-1, AC-2 | e2e | P0 |
| P1-S1 | {场景} | AC-3 | integration | P1 |
| P2-S1 | {场景} | AC-5 | unit | P2 |

## 2. 覆盖映射表

| spec AC | 场景 ID | 测试类型 | 测试文件 | 覆盖率 |
|---------|--------|---------|---------|--------|
| AC-1 | P0-S1 | e2e | tests/e2e/test_p0_flow.py | 100% |
| AC-2 | P0-S1 | e2e | tests/e2e/test_p0_flow.py | 100% |
| AC-3 | P1-S1 | integration | tests/integration/test_api.py | 100% |
| AC-5 | P2-S1 | unit | tests/unit/test_user.py | 100% |

## 3. 覆盖率门槛（V10.12 §Test Plan Gate）

- P0: 100% 必覆盖
- P1: ≥ 80%
- P2: ≥ 50%

## 4. 未覆盖场景

| AC | 原因 |
|----|------|
| AC-7 | {未覆盖原因 + 风险评估} |

## 4.3 验证命令（必可执行）

```bash
pytest tests/e2e/ -v  # Stage 4 Review 实跑验证
pytest tests/integration/ -v
pytest tests/unit/ -v
```

## 5. e2e 场景详细

### P0-S1: {场景名}
  preconditions:
    - {前置 1}
    - {前置 2}
  steps:
    - {操作 1}
    - {操作 2}
  expected:
    - {结果 1}
    - {结果 2}
```

---

## 关联引用

- [Stage 0.5 Test Plan](../../skills/03-test-plan/SKILL.md)
- [coverage-matrix-build.md](../../skills/03-test-plan/workflows/coverage-matrix-build.md)
- [Stage 4 Review §Step 2.4](../../skills/09-review/references/multi-round-revision.md)
