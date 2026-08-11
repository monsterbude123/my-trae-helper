# Stage 0.5 Test Plan — 元信息

> 第一性原则：**验收维度决定测试覆盖，测试覆盖决定交付质量**。

---

## 第一性原则（3 条）

### 原则 1：验收维度先于测试用例

每个 Capability 必须拆为 ≥ 3 验收维度（如功能正确性 / 边界条件 / 异常处理），每个验收维度映射到至少 1 个测试用例。

### 原则 2：覆盖率硬门槛

行覆盖率 ≥ 90% / 分支 ≥ 85% / 函数 ≥ 95% / 关键路径 100%。不足 = Stage 1 Spec 标注 + Stage 3 必补。

### 原则 3：测试在 spec 前

test-plan.md 是 Stage 1 Spec 的输入（含 Expected Behaviors 的测试视角）。test-plan 必在 spec 之前完成。

---

## 完整骨架（5 步）

```
Step 1: 读 plan.md → 识别 Capabilities（≤ 5 项）
Step 2: 验收维度拆解（每个 Capability → ≥ 3 验收维度）
Step 3: 测试用例映射（每个验收维度 → 至少 1 个测试用例）
  ├─ E2E 测试（≥ 2）
  ├─ INV 不变量测试（≥ 1）
  └─ UNIT 单元测试（≥ 5）
Step 4: 覆盖率门槛校验（行 ≥ 90% / 分支 ≥ 85% / 函数 ≥ 95%）
Step 5: 产出 test-plan.md + 状态卡更新
```

---

## 反例（4 条）

### 反例 1：无验收维度直接测试

**正确替代**: Step 2 必走验收维度拆解（每个 Capability ≥ 3 维度）。

### 反例 2：测试不可追溯

**正确替代**: Step 3 必含 test_to_capability 映射表。

### 反例 3：覆盖率门槛宽松

**正确替代**: 行 ≥ 90% 硬门槛（铁律 2）。

### 反例 4：跳过 E2E / INV

**正确替代**: E2E ≥ 2 + INV ≥ 1 + UNIT ≥ 5 最低组合（铁律 3）。

## 关联引用

- [SKILL.md](SKILL.md) | [workflows/](workflows/) | [references/](references/) | [templates/](templates/) | [anti-patterns/](anti-patterns/)
