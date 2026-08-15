# AskQuestion Anti-Patterns — AskUserQuestion 反模式库

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> V11 Stage -1 Intake / Stage 0 Plan 必读。避免错误使用 AskUserQuestion。

---

## 6 类 AskUserQuestion 反模式

### 反例 1：一次问 5+ 个问题

```python
# ❌ 反例
AskUserQuestion(questions=[
    {"question": "类型?", "options": [...]},
    {"question": "语言?", "options": [...]},
    {"question": "数据库?", "options": [...]},
    {"question": "部署?", "options": [...]},
    {"question": "测试?", "options": [...]},
])
```

后果: 用户疲劳，回答率降低。

正确: 一次问 1-4 个最关键问题，其余进 plan.md。

### 反例 2：选项模糊

```python
# ❌ 反例
AskUserQuestion(questions=[
    {"question": "选择方案?", "options": [
        {"label": "方案 A", "description": "..."},
        {"label": "方案 B", "description": "..."},
        {"label": "方案 C", "description": "..."},
    ]}
])
# 方案描述都很长，用户看不出区别
```

后果: 用户随机选。

正确: 每个选项 description ≤ 2 句，明确差异化（不是覆盖式列举）。

### 反例 3：缺失"Other"选项

```python
# ❌ 反例
AskUserQuestion(questions=[
    {"question": "框架?", "options": [{"label": "React"}, {"label": "Vue"}]}
])
# 假设用户用 Svelte 时无选项
```

后果: 用户无法表达真实意图。

正确: 由 SDK 自动添加 "Other" 选项（不要自己写死）。

### 反例 4：问题过于技术

```python
# ❌ 反例
AskUserQuestion(questions=[
    {"question": "用 useReducer 还是 useState for complex state?"}
])
# 非技术用户无法回答
```

正确: 翻译为业务语言（"状态多吗？" 而非"用 useReducer？"）。

### 反例 5：强行必答

```python
# ❌ 反例
# 把 AskUserQuestion 当成强制确认
AskUserQuestion(questions=[
    {"question": "确认删除所有数据吗？"}  # 强制 yes/no
])
```

正确: 强制 yes/no 应走 NotifyUser 工具或独立 alert() 机制。

### 反例 6：与 NotifyUser 混淆

```
AskUserQuestion: 需要用户做决策（如选择方案 A/B/C）
NotifyUser: 通知用户已完成（如 spec ready for review）
```

混淆使用 = 用户体验崩坏。

---

## 4 步决策法

```
何时用 AskUserQuestion:
  1. 有 2-4 个明确互斥选项
  2. 用户决策会改变实施路径
  3. 不可推断（用户没说）
  4. 时机合适（不是启动后立即问）
```

全部 YES → AskUserQuestion

任一 NO → 走 plan.md 假设或默认推断

---

## 关联引用

- [stage-interaction-protocol.md](stage-interaction-protocol.md) — 阶段间交互
- [common-iron-rules.md](common-iron-rules.md) — Article V 验证性主张
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns
