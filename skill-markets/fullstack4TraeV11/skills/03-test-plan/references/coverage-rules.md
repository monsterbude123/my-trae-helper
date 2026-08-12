# 覆盖率门槛规则（Coverage Rules）

> Stage 0.5 Test Plan Step 4 必走。覆盖率是测试质量的硬指标。

---

## 覆盖率层级

| 层级 | 门槛 | 测量方式（按项目栈选择） |
|------|:---:|---------|
| 行覆盖率（line） | ≥ 90% | pytest --cov (Python) / vitest --coverage (TS) / jest --coverage (JS) / cargo tarpaulin (Rust) / go tool cover (Go) |
| 分支覆盖率（branch） | ≥ 85% | pytest --cov-branch (Python) / vitest --coverage (TS) / jest --coverage (JS) / cargo tarpaulin (Rust) / go tool cover -func (Go) |
| 函数覆盖率（function） | ≥ 95% | pytest --cov (Python) / vitest --coverage (TS) / jest --coverage (JS) / cargo tarpaulin (Rust) / go tool cover (Go) |
| 关键路径（critical path） | 100% | E2E 覆盖（栈无关，按项目栈选对应 E2E 框架） |

> **V11.2 适配**: 表格第 3 列列出 5 种栈的等价命令,按项目实际栈选择。完整命令模板见下文 §检测命令。

---

## 关键路径定义

满足以下任一条件视为关键路径：

| 条件 | 示例 |
|------|------|
| 涉及安全 | 认证 / 授权 / Token 签发 |
| 涉及资金 | 支付 / 退款 / 结算 |
| 涉及数据完整性 | 数据库事务 / 状态机 |
| 涉及业务核心规则 | 用户登录 / 订单创建 |

**关键路径必须 E2E 覆盖 100%**（不是单元测试覆盖）。

---

## 不足处置流程

```
Step 4 检测覆盖率不足
  ├─ 行覆盖率 < 90%
  ├─ 分支 < 85%
  ├─ 函数 < 95%
  └─ 关键路径 < 100%
  ↓
test-plan.md 标注 "## 覆盖率不足" 段
  ├─ 当前值 + 目标值
  ├─ 未覆盖行/分支清单
  └─ 计划在哪个 stage 补
  ↓
Stage 1 Spec 继承风险标注
  ↓
Stage 3 Implement 必补（不可豁免）
```

---

## 豁免机制（Article II 限制）

覆盖率门槛**不可豁免**。但允许**合理 N/A**：

| N/A 场景 | 处置 |
|---------|------|
| 第三方库代码 | N/A（不计入分母） |
| 自动生成的代码 | N/A（说明生成工具） |
| 仅类型定义的 stub | N/A（无逻辑） |
| 调试代码 | 必删（不留 .bak） |

**N/A 必填理由**（不留空）。

---

## 检测命令

```bash
# 行覆盖率（按项目栈选择）
pytest --cov=src --cov-report=term-missing                                              # Python (pytest)
vitest run --coverage                                                                   # TypeScript (vitest)
jest --coverage                                                                         # JavaScript (jest)
cargo test --coverage                                                                   # Rust (cargo-tarpaulin)
go test -coverprofile=coverage.out && go tool cover -func=coverage.out                  # Go

# 分支覆盖率（按项目栈选择）
pytest --cov=src --cov-branch --cov-report=term-missing                                 # Python
vitest run --coverage --coverage.include='src/**'                                       # TypeScript
jest --coverage --coverageReporters=text --coverageThreshold='{"global":{"branches":85}}'  # JavaScript
cargo test --lib -- --cfg=tarpaulin                                                     # Rust
go test -cover -covermode=count                                                         # Go

# 关键路径 E2E 覆盖（按项目栈选择）
pytest tests/e2e/ --cov=src --cov-report=term                                           # Python
vitest run tests/e2e/ --coverage                                                        # TypeScript
jest --testPathPattern=e2e --coverage                                                   # JavaScript
cargo test --test e2e                                                                   # Rust
go test ./tests/e2e/...                                                                 # Go
```

> **V11.2 适配原则**: 03-test-plan 是栈无关编排器,**命令按项目实际栈选择**。在 `.trae/rules/stack.md` 必查项目主测试框架,然后用对应命令。禁止硬编码 `pytest` 假设 Python 栈。

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — 覆盖率门槛 ≥ 90%
- [coverage-mapping.md](../workflows/coverage-mapping.md) — 验收维度 → 测试用例
- [test-plan.md](../templates/test-plan.md) — test-plan.md 模板
- 公共铁律 Article II 满分硬门禁: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
