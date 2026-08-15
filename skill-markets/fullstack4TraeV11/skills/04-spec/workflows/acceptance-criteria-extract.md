# Acceptance Criteria Extract — Stage 1 Spec

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 1 Spec 必走。验收标准提取协议。

---

## 6 类 AC（V11.6.0 新增第 6 类 UI 交互 AC）

| 类型 | 描述 | 示例 |
|------|------|------|
| **功能性 AC** | 用户视角可观察的行为 | "用户登录后跳转到首页" |
| **非功能性 AC** | 性能/可用性/安全 | "登录响应 < 200ms" |
| **错误 AC** | 失败场景处理 | "密码错误提示不暴露用户是否存在" |
| **兼容性 AC** | 浏览器/版本兼容 | "支持 Chrome 100+" |
| **集成 AC** | 与外部系统集成 | "SSO 与 Okta 集成成功" |
| **UI 交互 AC** (V11.6.0 NEW) | 用户与 UI 交互能触达预期后端行为 | "点击新增按钮 → 弹表单 → POST 201 → 列表刷新",必填 `ui_flow_ref` 指向 ui-ux-logic 交互流 |

---

## AC 提取流程

```
Step 1: 读上游 plan.md（Capabilities + Non-Goals）
Step 2: 读用户原始 prompt（spec.md INV 来源）
Step 3: 每 Capability 衍生 ≥1 个 AC
Step 4: 每 AC 必含 GIVEN-WHEN-THEN 三段式
Step 5: 错误场景必含（× 边界值 + 错误路径）
```

---

## GIVEN-WHEN-THEN 模板

```yaml
AC-1: 用户登录成功
  given: "用户已注册，邮箱 verified"
  when: "用户输入正确邮箱密码"
  then:
    - "返回 200 + JWT token"
    - "token 有效期 1 小时"
    - "用户被重定向到 /home"

AC-2: 用户登录失败（密码错）
  given: "用户已注册"
  when: "用户输入错误密码"
  then:
    - "返回 401"
    - "错误信息: '用户名或密码错误'"
    - "不暴露用户是否存在"

AC-3: 登录性能
  given: "正常负载"
  when: "1000 并发登录请求"
  then:
    - "P99 响应 < 200ms"
    - "成功率 ≥ 99%"

AC-UI-1: 新增按钮可见并触发新增（V11.6.0 NEW — 第 6 类 UI 交互 AC）
  given: "列表页加载完成"
  when: "用户点击 Header 右侧'新增'按钮"
  then:
    - "弹出新增表单(对应 ui-ux-logic 流-1)"
    - "提交后 POST /items 返回 201(对应 TC-001)"
    - "列表刷新且含新条目(对应 TC-010, E2E)"
  ui_flow_ref: "ui-ux-logic.md#流-1"
```

---

## INV 定义

```yaml
INV-1: 认证必在授权前（Article 安全约束）
  rule: "任何 API 必先 authenticate 再 authorize"
INV-2: 事务原子性（Article 数据一致性）
  rule: "订单创建 + 库存扣减 必在同一事务"
INV-3: 不可幂等性敏感操作必加幂等键
  rule: "支付/扣款 API 必含 idempotency_key"
```

---

## Edge Cases（边界 + 异常）

```yaml
EC-1: 网络中断时登录
EC-2: 数据库连接超时
EC-3: token 过期刚好在请求中
EC-4: 并发同一用户登录多次
EC-5: 极大输入（10MB 密码）
EC-6: 特殊字符密码（emoji/中文）
```

---

## 输出: spec.md

```yaml
# Spec: {change-id}

## Acceptance Criteria (AC)

### AC-1: 用户登录成功
  ...
### AC-2: 用户登录失败
  ...

## Invariants (INV)

### INV-1: 认证必在授权前
  ...

## Edge Cases (EC)

### EC-1: 网络中断时登录
  ...
```

---

## 反例

### 反例 A：AC 不含 GIVEN-WHEN-THEN

```
AC-1: 用户能登录  # ❌ 无验证条件
正确: AC-1: 用户登录成功 + given/when/then
```

### 反例 B：遗漏错误 AC

```
AC: 全是正向场景，无错误处理  # ❌
正确: 错误 AC 必含（密码错 / 网络错 / token 过期等）
```

---

## 关联引用

- [SKILL.md](../SKILL.md)
- [Stage 2 Contract](../../06-contract/SKILL.md)
- [Stage 3 Test Plan Gate](../../03-test-plan/SKILL.md)
