# 验收维度 → 测试用例工作流（Coverage Mapping）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 0.5 Test Plan Step 2-3 核心工作流。验收维度拆解 + 测试用例映射。

---

## 流程

```
[Step 1] 读 plan.md + spec.md → 识别 Capabilities + AC 全集（V11.6.0 必包含 spec.md 的 AC-ID）
  ↓
[Step 2] 验收维度拆解（每个 Capability → ≥ 3 维度）
  ├─ 功能正确性（happy path）
  ├─ 边界条件（min/max/empty/zero）
  └─ 异常处理（invalid input / timeout / 资源不足）
  ↓
[Step 3] 测试用例映射（每个验收维度 → ≥ 1 测试用例，**V11.6.0 强制 ac 字段 = AC-ID**）
  ├─ 标注测试层级（E2E / INV / UNIT）
  ├─ 标注测试文件路径
  ├─ 标注 `ac` 映射（必填 AC-ID，禁止自由文本）
  ├─ 标注 `ui_flow` 引用（AC-UI-N 必填 ui-ux-logic 流-ID）
  └─ 标注 test_to_capability 映射
  ↓
[Step 3.5] AC ⇄ TC 双向补齐检（V11.6.0 NEW）
  ├─ 从 spec 提取 AC 全集 A
  ├─ 从 test-plan 提取所有 tc.ac 字段 = B
  ├─ 检查 A ⊆ B（每个 AC 至少 1 个 TC，否则 BLOCK 退回 Step 3 补）
  └─ 禁止"AC 在 spec 中但无 TC 映射"否则 ac-gate.py G4 拦
  ↓
[Step 4] 覆盖率门槛校验
  ├─ 行 ≥ 90%
  ├─ 分支 ≥ 85%
  ├─ 函数 ≥ 95%
  └─ 关键路径 100%
  ↓
[Step 5] 产出 test-plan.md（含 ac 字段 + ui_flow 引用）
```

---

## Step 2：验收维度拆解模板

每个 Capability 拆为 3 类验收维度：

| 维度类型 | 含义 | 示例（用户登录） |
|---------|------|----------------|
| **功能正确性** | happy path | 正确用户名+密码 → 200 + token |
| **边界条件** | 极端值 | 用户名长度 1/255 / 空密码 / 极大并发 |
| **异常处理** | 错误路径 | 错误密码 / 用户不存在 / DB 不可达 |

**Capability 拆解示例**:
```yaml
capability: "用户登录"
acceptance_dimensions:
  - dimension: "正确凭据可登录"
    type: functional
  - dimension: "错误凭据被拒绝"
    type: error_handling
  - dimension: "并发登录不冲突"
    type: boundary
```

> **V11.6.0 变更**:每个 dimension 必可以被拆为 spec.md 中已定义的 AC-ID(该 AC 必在 spec.md 存在)。不允许使用未在 spec.md 中定义的 capability 维度。

---

## Step 3：测试用例映射模板

每个验收维度映射到至少 1 个测试用例(**V11.6.0 强制 ac 字段 = AC-ID**):

```yaml
test_cases:
  - id: TC-001
    name: test_user_login_with_valid_credentials
    layer: UNIT
    file: tests/unit/test_user_service.py::test_login_valid
    ac: AC-1                            # ← V11.6.0 必填(AC-ID),ac-gate.py G5 校验
    ui_flow: null                       # ← V11.6.0 必填(为 null 表示非交互型 AC)
    acceptance_dimension: "正确凭据可登录"
    capability: "用户登录"
    assertion: "返回 user.id + token"

  - id: TC-002
    name: test_user_login_with_invalid_password
    layer: UNIT
    file: tests/unit/test_user_service.py::test_login_invalid_pwd
    ac: AC-2
    ui_flow: null
    acceptance_dimension: "错误凭据被拒绝"
    capability: "用户登录"
    assertion: "抛出 InvalidCredentialsError"

  - id: TC-010
    name: test_concurrent_login_no_conflict
    layer: E2E
    file: tests/e2e/test_auth_flow.py::test_concurrent_login
    ac: AC-1
    ui_flow: null
    acceptance_dimension: "并发登录不冲突"
    capability: "用户登录"
    assertion: "2 个并发登录都返回独立 token"

  - id: TC-020                             # ← V11.6.0 NEW: UI 交互 AC 用例
    name: test_add_btn_triggers_create
    layer: E2E
    file: tests/e2e/test_list_flow.py::test_add_btn
    ac: AC-UI-1
    ui_flow: "ui-ux-logic.md#流-1"          # ← V11.6.0 必填,指向 ui-ux-logic 的交互流
    acceptance_dimension: "新增按钮可见并触发新增"
    capability: "列表页新增"
    assertion: "点击 Header 新增按钮 → 弹表单 → POST 201 → 列表刷新"
```

---

## 测试层级最低组合

| 层级 | 数量 | 何时算 1 个 |
|------|:---:|-----------|
| **E2E** | ≥ 2 | 跨多个模块/服务的端到端流程 |
| **INV** | ≥ 1 | 不变量测试（数据一致性 / 安全约束 / 业务规则） |
| **UNIT** | ≥ 5 | 单函数/方法测试 |
| **总计** | ≥ 8 | 所有 Capability 合计 |

---

## Step 4：覆盖率门槛

```yaml
coverage_thresholds:
  line: 0.90
  branch: 0.85
  function: 0.95
  critical_path: 1.00
```

**不足处置**:
1. test-plan.md 标注"覆盖率不足"段
2. Stage 1 Spec 标注"覆盖率不足"风险
3. Stage 3 Implement 必补（不可豁免）

---

## 反例

### 反例 A：Capability 直接对应 1 个测试

```
capability: "用户登录"
test: test_user_login  # ❌ 1 个测试覆盖 3 维度
正确: 拆为 3 个测试（valid / invalid / concurrent）
```

### 反例 B：测试无断言

```
def test_user_login():
    user_service.login("alice", "pass123")  # ❌ 无 assertion
正确: assert result.token is not None
```

### 反例 C：覆盖率报告未生成

```
Step 4 跳过 → 直接产 test-plan.md  # ❌ 缺覆盖率数据
正确: 按项目栈跑覆盖率命令（pytest / vitest / jest / cargo test / go test 任选）→ 生成 coverage 报告 → 校验门槛
```

> 通用命令模板见 [../references/coverage-rules.md §检测命令](../references/coverage-rules.md)

---

### 反例 D(V11.6.0 NEW):`ac` 自由文本

```
- id: TC-001
  acceptance_dimension: "正确凭据可登录"  # ❌ 自由文本,ac-gate.py G5 拦
正确:
  - id: TC-001
    ac: AC-1                            # ← AC-ID,机械断言可拦截
```

### 反例 E(V11.6.0 NEW):AC 无 TC 映射

```
spec:
  AC-1: 用户登录
  AC-2: 用户修改密码
test-plan:
  - TC-001 ac: AC-1
  # ❌ AC-2 无 TC → ac-gate.py G4 拦
正确: 每个 AC 至少 1 个 TC,Step 3.5 双向补齐检必跑

---

## 关联引用

- [SKILL.md](../SKILL.md) — 阶段入口
- [coverage-rules.md](../references/coverage-rules.md) — 覆盖率门槛规则
- [test-plan.md](../templates/test-plan.md) — test-plan.md 模板
