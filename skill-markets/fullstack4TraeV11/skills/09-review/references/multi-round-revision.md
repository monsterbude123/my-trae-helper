# 多轮修订协议（Multi-Round Revision）

> Stage 4 Review Step 2.6 必走。V10 reviewer Step 2.6 自动循环机制。

---

## Round 1: 退回 implementer

```
Reviewer: REJECT + 失败标签
  ↓
Implementer: 重做
  ↓
Reviewer: 再 Review
  ├─ PASS → 通过
  └─ FAIL → Round 2
```

## Round 2: 升级上报用户

```
Reviewer: REJECT + 失败标签 + 5 字段阻塞报告
  ↓
上报用户决策:
  ├─ 用户接受现状 → 显式豁免
  ├─ 用户决策回退上游 Stage → 回退
  └─ 用户要求继续 → Round 3+
```

## Round 3+: rescue hatch（回退 Phase 0）

```
Reviewer: 连续 3 轮失败 → 回退 Phase 0（Intake）重新审视需求
```

---

## 失败分类标签（V10.12 NEW）

| 标签 | 含义 |
|------|------|
| `MISMATCH` | 货不对版（功能与 spec 不符）|
| `UNDERPERFORM` | 功能不达标 |
| `USER_VIEW_FAIL` | 用户视角 FAIL |
| `TEST_GAP` | 测试覆盖缺口 |
| `DRIFT` | 代码与契约漂移 |

---

## 反例

### 反例 A：连续 5 轮小修小补

```
Round 1: 退 → implementer 修补命名
Round 2: 退 → implementer 修补格式
Round 3: 退 → implementer 修补空行
Round 4: 退 → implementer 修补注释
Round 5: 退 → ???  # ❌ V10.8 反复反馈升级根因诊断

正确: Round 2 升级用户 → 用户决策回退上游
```

### 反例 B：失败标签缺失

```
Reviewer: REJECT  # ❌ 无失败标签
正确: REJECT + 失败分类标签 + 5 字段阻塞报告
```

---

## 关联引用

- [SKILL.md §铁律 10](../SKILL.md) — 关键门禁套件
- V10 multi-round-revision-protocol.md: `V10 来源` (已蒸馏到本文档)
