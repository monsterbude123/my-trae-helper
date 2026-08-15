# 反例 1：无验收维度直接测试（No Acceptance Dimension）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 0.5 Test Plan 必走"Capability → Acceptance Dimension → Test Case"三层拆解。跳过维度拆解 = 测试覆盖不全 + Stage 4 Review 失败定位无依据。

**违反**：铁律 1（验收维度先于测试用例）
**严重度**：P2（过程性缺陷，但会导致 Stage 4 Review 不可逆返工）

---

## 现象

```markdown
# test-plan.md（反例版本）

## Capabilities
- C1: 用户登录
- C2: 用户登出

## Test Cases
- TC-01: login('alice', 'pass123') → 200
- TC-02: logout(token) → 200

# ❌ 反例：Capability 直接对应 1 个 test，
#          无"验收维度"中间层
#          Stage 4 Review 时若 login 失败，无法判断失败在哪个维度
```

**识别信号**:
- plan.md 每个 Capability 只列 1-2 个测试
- 无"正常路径 / 异常路径 / 边界条件 / 安全性 / 性能"维度拆解
- 测试标题只描述"功能名称"（如 `test_login`）而非"维度 + 场景"
- Stage 4 Review 时 reviewer 写"哪个 Capability 失败"无法定位到具体维度

---

## 根因

- **认知维度**：把"测试"等同于"功能验证"（functional verification），没意识到功能本身包含 ≥ 3 维度
- **流程维度**：跳过 coverage-mapping.md §Step 2 维度拆解 Step，直接进 §Step 3 测试用例编写
- **习惯维度**：从 Stage 3 实施倒推 Stage 0.5 plan，测试是"事后补"，而非"事前拆"

| 根因 | 占比 |
|------|:---:|
| 把测试当功能验证（缺维度意识）| 60% |
| 跳过 coverage-mapping §Step 2 流程 | 30% |
| 从实施倒推 plan（顺序错误）| 10% |

---

## 教训

- **V11 实战**：Stage 4 Review 阶段，reviewer 拿到测试报告 + 失败 case，无法判定"失败属于哪个 Capability 的哪个维度"，返工补测试 → 浪费 2-4h
- **真实场景**：`test_login` 失败可能是（a）正常路径失败（b）空密码边界（c）密码错误异常（d）SQL 注入安全（e）并发性能。缺维度拆解显著拉长失败定位耗时
- **Stage 4 Review 阻塞**：reviewer 维度评分（功能/可用/安全/性能）无法独立打分，因为测试未按维度组织

---

## 正确替代

```yaml
# ✅ 正确流程（coverage-mapping.md §Step 2 强制）

Step 1: 列 Capability
  - C1: 用户登录

Step 2: 拆验收维度（每个 Capability 必 ≥ 3 维度）
  - C1-功能维度: 正常登录 / 错误密码 / 空字段
  - C1-异常维度: 网络中断 / 服务超时 / DB 连接失败
  - C1-安全维度: SQL 注入 / 暴力破解 / CSRF token 缺失
  - C1-边界维度: 用户名超长 / 密码含特殊字符 / Unicode
  - C1-性能维度: 100 并发登录 / P99 延迟

Step 3: 维度 → 测试用例映射
  - C1-功能维度 → TC-01, TC-02, TC-03
  - C1-异常维度 → TC-04, TC-05, TC-06
  - C1-安全维度 → TC-07, TC-08, TC-09
  - ...

Step 4: 覆盖率断言
  - 每个 Capability 维度数 ≥ 3
  - 每个维度测试数 ≥ 1
  - test_to_capability 矩阵完整
```

```markdown
# test-plan.md（正确版本）

## Capability C1: 用户登录
### 验收维度
| 维度 | 场景 | 测试 |
|------|------|------|
| 功能 | 正常登录 | TC-01 |
| 功能 | 密码错误 | TC-02 |
| 功能 | 空字段 | TC-03 |
| 异常 | 网络中断 | TC-04 |
| 异常 | 服务超时 | TC-05 |
| 安全 | SQL 注入 | TC-07 |
| 安全 | 暴力破解 | TC-08 |
| 边界 | 用户名超长 | TC-10 |
| 边界 | Unicode | TC-11 |
| 性能 | 100 并发 | TC-13 |
```

---

## 关联引用

- [SKILL.md §铁律 1](../SKILL.md) — 验收维度先于测试用例
- [coverage-mapping.md §Step 2](../workflows/coverage-mapping.md) — 维度拆解 Step
- [coverage-rules.md](../references/coverage-rules.md) — 维度覆盖率硬门槛
- 公共铁律 Article I(质量优先 — 1.2 不可为赶进度降低测试覆盖 ≥ 90%): [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
