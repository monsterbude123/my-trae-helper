# 反例 3：覆盖率门槛宽松（Coverage Too Low）

> 行 ≥ 90% / 分支 ≥ 85% / 函数 ≥ 95% 是 V11 硬门槛。宽松 = Stage 3 必补风险 + Stage 4 Review 质疑（REJECT）。

**违反**：铁律 2（覆盖率 ≥ 90%）+ 铁律 8（不跳门槛）
**严重度**：P1（直接导致 Stage 4 Review REJECT + Stage 5 Accept 阻塞）

---

## 现象

```yaml
# test-plan.md（反例版本）

## 覆盖率目标
- 行覆盖率: ≥ 70%   # ❌ 反例：低于 V11 硬门槛
- 分支覆盖率: 未标注
- 函数覆盖率: 未标注

## 关键路径覆盖率: 未标注

# 或另一种反例
## 覆盖率目标
- 尽力覆盖   # ❌ 反例：抽象表述，无数字

# 实施结果
pnpm test --coverage
# Lines: 78.4%   # ❌ < 90% = 必补
# Branches: 71.2%   # ❌ < 85% = 必补
# Functions: 82.1%   # ❌ < 95% = 必补
```

**识别信号**:
- 覆盖率数字 < 硬门槛（行 < 90% / 分支 < 85% / 函数 < 95%）
- test-plan.md 未明确标注硬门槛数字
- "尽力覆盖" / "尽可能高" 等抽象表述
- Stage 3 实施者直接交 80% coverage，无补测动作

---

## 根因

- **认知维度**：把覆盖率当作"参考指标"而非"硬门槛"
- **成本维度**：觉得"补测试 = 浪费时间"，不如写新功能
- **流程维度**：跳过 coverage-rules.md 4 维度门槛（行/分支/函数/关键路径）

| 根因 | 占比 |
|------|:---:|
| 视覆盖率为参考指标（非硬门槛）| 50% |
| 觉得补测试浪费时间（成本意识）| 30% |
| 不知道 4 维度门槛具体数字 | 20% |

---

## 教训

- **V11 实战**：Stage 3 实施者交付 80% line coverage，自评"已覆盖主要功能"。Stage 4 Review 拿覆盖率报告 → REJECT → 补测 1.5 天
- **真实场景**：业务侧隐藏 helper 函数（`format_currency` / `parse_date` / `validate_email`）未覆盖。这些是生产事故高发点。覆盖率门槛宽松 = 生产事故 2 倍概率
- **关键路径 100% 反例**：支付回调函数 0 测试（"反正测过类似函数"），生产环境支付回调失败 → 直接资金损失

---

## 正确替代

```yaml
# ✅ 正确：覆盖率硬门槛 + 4 维度

# 1. test-plan.md 必含覆盖率声明
## 覆盖率目标（V11 Article II 硬门槛）
- 行覆盖率: ≥ 90%
- 分支覆盖率: ≥ 85%
- 函数覆盖率: ≥ 95%
- 关键路径覆盖率: 100%

# 2. Stage 3 实施者提交前必跑
pnpm test --coverage
# 必含输出:
#   Lines:   ≥ 90%  ← 必达
#   Branches: ≥ 85%  ← 必达
#   Functions: ≥ 95% ← 必达
#   Critical paths: 100%  ← 必达（支付/认证/资金流）

# 3. 未达门槛必走补测流程
未达门槛 → 列出未覆盖行（lcov html 报告）
       → 优先级排序（关键路径 > 错误处理 > 边界 > 性能）
       → TDD 补测（RED → GREEN）
       → 重跑覆盖率 → 必达
```

```yaml
# ✅ 关键路径强制 100% 覆盖清单

critical_paths:
  payment:
    - src/payment/callback.py::handle_callback   # 支付回调
    - src/payment/refund.py::process_refund        # 退款
  auth:
    - src/auth/login.py::authenticate              # 登录认证
    - src/auth/token.py::verify_token              # Token 校验
  data_integrity:
    - src/db/transaction.py::commit                # DB 事务提交
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走 4 维度核验
1. 覆盖率报告 4 维度必达（行/分支/函数/关键路径）
2. 关键路径覆盖率 = 100%（不允许 < 100%）
3. 实施者交付时未达门槛 → 🛑 REJECT
4. "尽力覆盖"等抽象表述 → 🛑 REJECT（要求数字）
5. 补测后未重跑覆盖率 → 🛑 REJECT
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| test-plan.md 标注 "≥ 70%" | Stage 4 Review 直接 REJECT |
| 实施者口头"覆盖率达标"无报告 | 🛑 Article V 违反（无证据） |
| 只看 line coverage 不看 branch | if/else 一边未测 = 漏洞 |
| 关键路径 < 100% 强行通过 | 生产事故 → 用户信任崩塌 |
| "尽力覆盖" 抽象表述 | 🛑 REJECT（要求数字） |

---

## 关联引用

- [SKILL.md §铁律 2](../SKILL.md) — 覆盖率门槛 ≥ 90%
- [SKILL.md §铁律 8](../SKILL.md) — 不跳门槛
- [coverage-rules.md](../references/coverage-rules.md) — 4 维度门槛详表
- 公共铁律 Article II: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
