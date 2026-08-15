# Bug 单状态机（Bug State Machine）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> Stage 6 Bug Fix Step 5 必走。V10 bug-workflow.md + Intake bug-state-machine.md 蒸馏。

---

## 状态机（3 个状态）

```
[OPEN] ──→ [IN_PROGRESS] ──→ [CLOSED]
   ↑              │
   └──────────────┘
       (回退条件: e2e INITIAL PASS / 修复失败)
```

| 状态 | 含义 | 维护者 |
|------|------|--------|
| **OPEN** | 已录入，待处理 | Intake / debugger |
| **IN_PROGRESS** | 6 层排查 + TDD 修复中 | debugger |
| **CLOSED** | 修复 + 回归 + 用户确认 | debugger |

## 转换矩阵

| From → To | 触发 | 必要条件 |
|-----------|------|---------|
| (无) → OPEN | Intake 创建 | 6 字段齐全 |
| OPEN → IN_PROGRESS | debugger 启动 | e2e 初始 FAIL |
| IN_PROGRESS → CLOSED | 修复完成 | TDD GREEN + 回归 PASS + 用户签字 |
| IN_PROGRESS → OPEN | e2e 初始 PASS | 不是 bug（回退） |
| IN_PROGRESS → OPEN | TDD 修复 FAIL | 重做循环 |

## CLOSED 回写模板

```markdown
# Bug 单 CLOSED 回写

## 8.5 关闭记录

- **关闭时间**: YYYY-MM-DD HH:mm
- **关闭人**: debugger
- **根因**: [6 层排查结论 + GitNexus impact]
- **修复文件**: [file:line list]
- **关闭方式**: e2e PASS + 回归 PASS + 用户签字
```

---

## 反例

### 反例 A：跳过 OPEN 直接修

```
debugger: 用户报 bug → 立即修代码 → 没创建 bug 单  # ❌
正确: Intake 必先录入 OPEN bug 单 → debugger 启动
```

### 反例 B：CLOSED 后又改

```
debugger: 已 CLOSED → 用户反馈 → Edit bug 单 CLOSED 字段  # ❌ Article XII
正确: 新建 bug 单 + 引用原 bug-id
```

---

## 关联引用

- [SKILL.md §铁律 7](../SKILL.md)
- V10 bug-workflow.md: `V10 来源` (已蒸馏到本文档)
- Intake bug-state-machine.md: [../../01-intake/references/bug-state-machine.md](../../01-intake/references/bug-state-machine.md)
