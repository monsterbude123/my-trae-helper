# 反例 4：plan.md 超长

> plan.md ≤ 80 行 + Capabilities ≤ 5 项。超长 = Stage 1 Spec 失去输入价值。

## 现象

```
plan.md: 200 行 / 10 Capabilities / 30 Tasks  # ❌ 超长
```

**识别信号**:
- `wc -l plan.md` > 80
- Capabilities 项数 > 5
- Tasks 项数 > 20
- Closure 闭环步骤 > 5

## 根因

| 根因 | 占比 |
|------|:---:|
| 把所有细节塞进 plan.md | 50% |
| 混淆 plan vs spec 边界 | 30% |
| 不知道怎么拆分 | 20% |

## 教训

**plan.md 是规划不是实施，超长 = Stage 1 Spec 失去输入价值。**

plan.md 应该回答"做什么 + 为什么 + 影响面"，不回答"怎么做"。怎么做留给 Stage 1 Spec。

## 正确替代

### 拆分原则

| 当前 | 拆分到 |
|------|--------|
| Capabilities > 5 | 拆成多个 change（或 Non-Goals） |
| Tasks > 20 | Stage 1 Spec 详细化 |
| Closure > 5 步 | 拆成多个 P0 子闭环 |
| plan.md > 80 行 | 移到 references/ 或 Stage 1 Spec |

### 拆分示例

**拆分前**（10 Capabilities，120 行）:
```markdown
## Capabilities
1. 用户注册
2. 用户登录
3. 用户登出
4. 密码重置
5. 邮箱验证
6. 手机验证
7. OAuth 登录
8. 双因素认证
9. 账号锁定
10. 登录审计
```

**拆分后**（5 Capabilities，70 行）：
```markdown
## Capabilities（变更范围）
1. 用户注册（含邮箱验证）
2. 用户登录（含 OAuth）
3. 密码重置
4. 双因素认证
5. 登录审计

## Non-Goals（不在本次）
- 手机验证（后续 change）
- 账号锁定（运营工具内化）
- 用户登出（基础功能，无需变更）
```

## 拆分标准

| 阈值 | 拆分动作 |
|------|---------|
| Capabilities > 5 | 拆 change 或移到 Non-Goals |
| Tasks > 20 | Stage 1 Spec 详细化（不变 plan.md）|
| Closure > 5 | 拆 P0 闭环或拆 change |
| 行数 > 80 | 详细实现移到 references/ |

## 反模式细化

### 反例 A：把所有需求都列 Capabilities

```
Capabilities: 注册 + 登录 + 登出 + 重置 + 验证 + OAuth + 2FA + 锁定 + 审计  # ❌ 9 项
正确: 拆为 5 项本期 + 4 项 Non-Goals
```

### 反例 B：Tasks 写成 Implementation Plan

```
Tasks: 
  - [ ] 创建 UserService 类
  - [ ] 写 password_hash 函数
  - [ ] 写 token_sign 函数
  ...（30 项）  # ❌ 写成实施计划
正确: Tasks ≤ 20 项 + Stage 1 Spec 详细化
```

### 反例 C：Closure 闭环步骤过多

```
Closure: 8 步  # ❌ 超铁律 9
正确: 拆成 2 个 P0 闭环（每个 ≤ 5 步）或拆 change
```

## 检测方法

```yaml
checklist:
  - [ ] plan.md 行数 ≤ 80？
  - [ ] Capabilities 项数 ≤ 5？
  - [ ] Tasks 项数 ≤ 20？
  - [ ] Closure 闭环步骤 ≤ 5？
```

任一未通过 → 触发本反例 → 精简 plan.md。

```bash
wc -l docs/specs/changes/{change-id}/plan.md  # 必须 ≤ 80
```

## 关联引用

- [SKILL.md §铁律 8](../SKILL.md) — PLAN ≤ 80 LINES
- [SKILL.md §铁律 9](../SKILL.md) — CLOSURE ≤ 5 STEPS
- [plan-template.md](../templates/plan-template.md) — 模板约束
