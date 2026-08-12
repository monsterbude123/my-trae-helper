# 反例 1：INV 凭空臆造（INV Fabrication）

> INV（不变量）必须基于业务规则（订单一致性 / 资金安全 / 认证前置）。凭空写 INV = Stage 4 Review REJECT + 实施后用户拒绝需求。

**违反**：铁律 6（NEVER 凭空 INV）
**严重度**：P1（直接导致 Stage 4 Review REJECT + 实施返工）

---

## 现象

```markdown
# spec.md（反例版本）

## INV-001: 用户名长度
所有用户名为 5-20 字符

# ❌ 反例：凭空臆造
#   - 没有业务规则文档支持（产品 PRD 无此约束）
#   - 没有用户访谈记录
#   - 没有行业标准引用（如 RFC / ISO）
#   - 凭空拍脑袋数字

## INV-002: 密码强度
密码必须包含大小写 + 数字 + 特殊字符

# ❌ 反例：臆造 4 类字符混合（实际很多系统只要 8 位以上）

## INV-003: 订单金额
订单金额必须为正数

# � 反例：实际业务有退款订单（负数）或 0 元赠品订单
```

**识别信号**:
- spec.md §INV 章节含数字阈值（长度/范围/字符集）但无 `based_on:` 引用
- spec.md §INV 无业务规则文档链接（如 PRD-001 / RFC-5322）
- INV 字段直接由 spec-writer 写出，未经产品/业务确认
- Stage 4 Review 时 reviewer 追问"这条 INV 哪来的"无法回答

---

## 根因

- **认知维度**：把 INV 当作"完整性补丁"（写起来看着完整），而非"业务规则断言"
- **流程维度**：跳过 acceptance-enhancement.md §INV 推导 Step（业务规则 → INV）
- **责任维度**：spec-writer 越权定义业务规则（实际应由 PM/产品决定）

| 根因 | 占比 |
|------|:---:|
| 视 INV 为完整性补丁（非业务断言）| 50% |
| 跳过 acceptance-enhancement §INV 推导 | 30% |
| spec-writer 越权（责任主体错位）| 20% |

---

## 教训

- **V11 实战**：spec-writer 写"INV: 用户名 5-20 字符"无依据。Stage 4 Review → 产品经理答"我们其实允许 3-30 字符" → spec.md 重写 → 返工 1 天
- **真实场景**：INV-002 密码强度 4 类字符混合，生产环境老用户集体投诉"无法登录"（他们的密码只有 3 类）→ 紧急修改需求 → 流失 30% 用户
- **资金事故反例**：INV-003 订单金额必须为正 → 退款订单（负数）系统拒绝 → 用户无法退款 → 客服投诉爆表

---

## 正确替代

```yaml
# ✅ 正确：INV 必含业务规则溯源

## INV-001: 用户名长度
所有用户名为 3-30 字符
based_on:
  - 产品 PRD §3.2 (2024-Q1 用户调研报告)
  - 行业参考: Twitter 用户名 ≤ 15, GitHub 用户名 ≤ 39
  - 业务理由: 支持中文用户名（2 字符）+ 国际化邮箱前缀
evidence:
  - docs/specs/changes/{change-id}/prd-3.2-user-research.md

## INV-002: 密码强度
密码 ≥ 8 字符
based_on:
  - NIST SP 800-63B §5.1.1.2 (推荐 ≥ 8 字符而非强制字符集)
  - 产品 PRD §3.3 安全合规
evidence:
  - NIST 文档链接 + 产品评审会议纪要

## INV-003: 订单金额
订单金额可正（购买）、可负（退款）、可零（赠品）
based_on:
  - 业务规则 BR-007: 退款流程（docs/business-rules.md §7）
  - 业务规则 BR-012: 赠品营销规则
evidence:
  - 财务部 + 运营部联合签字（2024-03-15）
```

```markdown
# spec.md INV 章节模板（强制含 based_on）

## 不变量（INV）

### INV-NNN: {规则名称}
**断言**: {数学/逻辑表达式}

**based_on**（必填，不可空）:
- 业务规则: {BR-XXX 或 PRD-XXX §Y.Y}
- 文档证据: {file:line 或 URL}
- 责任人: {PM / 法务 / 财务 / 安全}

**验证方式**: {UNIT / INV / E2E}

**反例**: {不满足 INV 时的具体场景 + 期望行为}
```

---

## Stage 4 Review 验证协议

```yaml
# reviewer 必走
1. 逐条 INV 检查 based_on 字段
2. based_on 为空 / 模糊 → 🛑 REJECT
3. based_on 仅含"常识" / "行业惯例"（无具体文档）→ 🛑 REJECT
4. 数字阈值类 INV（长度/范围）→ 必含文档链接或会议纪要
5. 资金 / 安全 / 合规类 INV → 必含责任人签字
6. spec-writer 自我声明"我定的" → 🛑 REJECT（越权）
```

---

## 反模式识别（V11 实战踩雷）

| 反例类型 | 后果 |
|---------|------|
| INV 凭空写无依据 | Stage 4 REJECT + 返工 |
| INV based_on 写"常识" | 🛑 REJECT（要具体文档）|
| INV 数字拍脑袋（5-20 字符）| 实施后产品否决 |
| 资金类 INV 无财务签字 | 🛑 P0 资金事故风险 |
| spec-writer 自我声明"我定的" | 🛑 越权（必走产品） |

---

## 关联引用

- [SKILL.md §铁律 6](../SKILL.md) — NEVER 凭空 INV
- [acceptance-enhancement.md §INV](../references/acceptance-enhancement.md) — INV 推导 Step
- 公共铁律 Article V: [../../../references/common-iron-rules.md](../../../references/common-iron-rules.md)
