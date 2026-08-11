# Tasks-Driven Implement — Stage 3

> Stage 3 Implement 必走。tasks.md 驱动的 TDD 实施协议。

---

## 流程

```
Step 1: 读 docs/specs/changes/{id}/tasks.md（来自 Stage 0/1 联合）
Step 2: 统计进度 N/M tasks complete
Step 3: 对每个 pending task 走 TDD 三步循环
Step 4: 完成后标记 [x] + 同步 spec.md AC [x]
```

---

## tasks.md 模板

```yaml
# Tasks: {change-id}

## Phase 1: 基础设施

- [ ] T-1: 创建 domain model 类（User / Email / UserStatus）
- [ ] T-2: 创建 repository 接口
- [ ] T-3: 配置 DB migration

## Phase 2: 核心实现

- [ ] T-4: POST /api/v1/auth/login 契约实现
- [ ] T-5: 密码哈希服务
- [ ] T-6: JWT token 生成 + 验证

## Phase 3: 测试

- [ ] T-7: contract_test_login（验证契约一致性）
- [ ] T-8: integration_test_login（端到端）
- [ ] T-9: e2e_test_login（用户视角）
```

---

## TDD 三步循环（per task）

```
[Task N] 必走 4 阶段:
  🔴 RED: 写失败测试
    ├─ 单元测试（针对单个函数）
    ├─ 集成测试（针对 module 交互）
    └─ 必 INITIAL FAIL

  🟢 GREEN: 最简实现
    ├─ 只让当前 RED 通过
    └─ 不"顺便"实现其他

  ♻️ REFACTOR: 优化质量
    ├─ DRY / 命名 / 拆分
    └─ 保持测试通过

  🔍 DRIFT CHECK: 对照契约
    ├─ 接口签名一致？
    ├─ 字段类型一致？
    ├─ 错误码一致？
    └─ 不一致 → 立即报告回流
```

---

## 进度汇报格式

```yaml
## Completion Report - implementer

artifacts:
  - src/auth/login.py
  - src/auth/token.py
  - __tests__/contracts/test_login.test.ts
  - __tests__/integration/test_login.test.py

test: 50/50         # 单元 + 集成 + e2e
contract_tests: 8/8 # 契约测试
coverage: 92%        # 行覆盖

status: "✅"
next_stage: "3.5/real-verify"
```

---

## 反例

### 反例 A：跳过 RED

```
implementer: 写 GREEN 实现 → 测试通过  # ❌ 无 RED 验证
正确: RED → GREEN → REFACTOR → DRIFT CHECK
```

### 反例 B：一次性写多个 task

```
implementer: 同时写 T-1/T-2/T-3 → 一次性提交  # ❌ rot #12
正确: 逐个 task 走 TDD + 同步状态
```

### 反例 C：DRIFT 不报告

```
implementer: 实现改了接口 → 不报告 → 默默更新契约  # ❌
正确: DRIFT CHECK 必报告回流（V11 §4.5 漂移）
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [tdd-workflow.md](../references/tdd-workflow.md)
- [drift-detect.md](../references/drift-detect.md)