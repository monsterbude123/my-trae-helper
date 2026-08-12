# Coverage Matrix Build — Stage 0.5 Test Plan

> Stage 0.5 Test Plan 必走。覆盖矩阵构建协议。

---

## 覆盖矩阵结构

```yaml
test_coverage_matrix:
  P0_scenarios:
    - id: "P0-S1"
      spec_ref: "AC-1, AC-2"
      test_type: "e2e"
      test_file: "tests/e2e/test_p0_flow.py::test_login_flow"
      covered: "✅"
      evidence: "测试已 PASS"
  P1_scenarios:
    - id: "P1-S1"
      spec_ref: "AC-3"
      test_type: "integration"
      test_file: "tests/integration/test_api.py::test_health"
      covered: "✅"
  P2_scenarios:
    - id: "P2-S1"
      spec_ref: "AC-5"
      test_type: "unit"
      covered: "⚠️"
      note: "低优先级场景"
```

---

## 覆盖率要求（V10.12 §Test Plan Gate）

| 优先级 | 覆盖率门槛 | 不可达成处理 |
|--------|:---:|------|
| **P0** | 100% | 🛑 REJECT — 必全部覆盖 |
| **P1** | ≥ 80% | ⚠️ 报告未覆盖理由 |
| **P2** | ≥ 50% | ⚠️ 报告未覆盖理由 |

---

## 测试场景分类

### E2E 测试
- 用户视角完整流程
- 跨多个 module
- 真实数据库 / 服务

### Integration 测试
- 2-3 个 module 集成
- mock 外部依赖

### Unit 测试
- 单函数 / 单类
- 全部 mock

---

## 输出: `test_plan.md`

```yaml
# Test Plan: {change-id}

## 1. 测试场景清单

来源: spec.md AC + Edge Cases + 业务 E2E 场景
总数: {N} 个场景

## 2. 覆盖映射

| spec AC | 场景 ID | 测试类型 | 测试文件 | 覆盖率 |
|---------|--------|---------|---------|--------|
| AC-1 | P0-S1 | e2e | test_p0_flow.py | 100% |
| AC-2 | P0-S1 | e2e | test_p0_flow.py | 100% |
| AC-3 | P1-S1 | integration | test_api.py | 100% |
| AC-5 | P2-S1 | unit | test_unit.py | 100% |

## 3. 未覆盖场景

- AC-7: 低优 → 不覆盖，记录原因

## 4. 验证命令

```bash
# 按项目栈选择（V11.2 栈无关编排器）
pytest tests/{e2e,integration,unit}/ -v          # Python
vitest run tests/{e2e,integration,unit}/ -v      # TypeScript
jest --testPathPattern='e2e|integration|unit'   # JavaScript
cargo test --test {e2e,integration,unit}        # Rust
go test ./tests/{e2e,integration,unit}/...      # Go
```
```

---

## 反例

### 反例 A：覆盖率不足未说明

```
Test Plan: P0 覆盖 60%  # ❌ REJECT（< 100%）
正确: P0 必 100% + 不可达成时报告 + Article XVI 论证
```

### 反例 B：编造测试文件路径

```
Test Plan: tests/foo.test.ts:999  # ❌ 文件不存在
正确: 真实 file:line + 跑测试验证
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [Stage 4 Review §Step 2.4](../../09-review/references/multi-round-revision.md)
- [stage-interaction-protocol.md](../../references/stage-interaction-protocol.md)