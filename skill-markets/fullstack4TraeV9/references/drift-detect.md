# 漂移检测 + 回流

> 发现规格/契约/代码不一致时，立即报告回流。
> ADDITIVE/BREAKING 契约变更流程。

---

## 漂移类型

| 类型 | 描述 | 触发者 |
|------|------|--------|
| Spec 漂移 | Spec 描述与实际需求不一致 | implementer |
| 契约漂移 | 代码实现与 Contract 四件套不一致 | reviewer |
| 文档漂移 | 模块文档与代码实现不一致 | DOC SYNC 自检 |
| 目标漂移 | 用户需求在开发中发生变化 | 用户中途修改 |

---

## 严重度判定

| 等级 | 条件 | 行动 |
|------|------|------|
| LOW | 注释/命名不一致 | 直接修复 |
| MEDIUM | 接口参数变更 | 通知用户确认后更新 |
| HIGH | 核心逻辑变更 | 🛑 停止开发，回流上游 |

---

## 回流判定树

```
发现漂移
  │
  ├── Spec 漂移 → 回流 spec-writer
  │    重走: Spec → Contract → Implement → Review
  │
  ├── 契约漂移 → 回流 contract-writer
  │    重走: Contract → Implement → Review
  │
  ├── 文档漂移 → DOC SYNC 修复
  │    不回流，reviewer 直接同步文档
  │
  └── 目标漂移 → 回流 Intake
       全链重走: Intake → Define → Spec → Contract → Implement → Review

同一 change Review FAIL 3 次 → 🛑 标记 🔴 高风险，汇报用户
```

---

## 契约变更流程（ADDITIVE / BREAKING）

```
需要改 approved 契约
    │
    ├── ADDITIVE（兼容 — 新增可选字段/接口/枚举值）
    │     直接添加 → 更新契约版本（minor）
    │
    └── BREAKING（不兼容 — 删字段/改类型/改路径/删枚举值）
         🛑 必须用户显式确认
         确认后 → 更新契约版本（major）→ 回流下游全链
```

---

## 禁止行为

- ❌ 发现漂移后静默迁就
- ❌ 绕过回流直接编码
- ❌ 修改测试掩盖漂移
- ❌ 单方面修改 approved 契约（必须走 ADDITIVE/BREAKING 流程）
