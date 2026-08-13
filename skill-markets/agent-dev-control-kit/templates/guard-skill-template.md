# Guard Skill Template — 守卫类技能模板

> 复制此模板到 `skill-markets/<your-skill>/SKILL.md`，替换占位符

---
name: <skill-name>
description: <一句话描述 + 触发条件>。当用户提到"<trigger-word-1>"、"<trigger-word-2>"时主动加载。
version: 1.0.0
requires:
  skills: [<dependency-skill-1>]
  optional: [<optional-skill-1>]
---

# <Skill Name>

## 触发词

- <trigger-word-1> / <trigger-word-2> / <trigger-word-3>

## 功能说明

<详细描述此守卫技能的功能和用途>

## 守卫类型

- **前置守卫**：执行前检查前置条件
- **后置守卫**：执行后验证结果完整性
- **异常守卫**：捕获异常并降级处理
- **状态守卫**：维护状态一致性

## 守卫规则

### Rule 1: <rule-name-1>

**类型**：<guard-type>

**触发条件**：<trigger-condition>

**检查逻辑**：

```pseudo
IF <condition-1> AND <condition-2> THEN
  RETURN PASS
ELSE
  RETURN FAIL WITH <error-message>
END IF
```

**通过标准**：<pass-criteria>

**失败处理**：<fail-action>

### Rule 2: <rule-name-2>

**类型**：<guard-type>

**触发条件**：<trigger-condition>

**检查逻辑**：

```pseudo
CHECK <state-1>
IF <state-1> IS VALID THEN
  PROCEED
ELSE
  BLOCK WITH <reason>
END IF
```

**通过标准**：<pass-criteria>

**失败处理**：<fail-action>

## 前置守卫（Pre-Guard）

### 检查清单

| 检查项 | 条件 | 失败处理 |
|--------|------|---------|
| `<check-1>` | `<condition-1>` | `<action-1>` |
| `<check-2>` | `<condition-2>` | `<action-2>` |
| `<check-3>` | `<condition-3>` | `<action-3>` |

### 实现模板

```pseudo
function preGuard(context):
  checks = [
    { name: "<check-1>", condition: <condition-1>, action: "<action-1>" },
    { name: "<check-2>", condition: <condition-2>, action: "<action-2>" },
    { name: "<check-3>", condition: <condition-3>, action: "<action-3>" }
  ]

  FOR each check IN checks:
    IF NOT evaluate(check.condition) THEN
      RETURN {
        status: "BLOCKED",
        reason: check.name,
        action: check.action,
        context: context
      }
    END IF
  END FOR

  RETURN { status: "PASS", context: context }
END function
```

## 后置守卫（Post-Guard）

### 验证清单

| 验证项 | 条件 | 失败处理 |
|--------|------|---------|
| `<verify-1>` | `<condition-1>` | `<action-1>` |
| `<verify-2>` | `<condition-2>` | `<action-2>` |
| `<verify-3>` | `<condition-3>` | `<action-3>` |

### 实现模板

```pseudo
function postGuard(result, context):
  IF result.status != "success" THEN
    RETURN result
  END IF

  validations = [
    { name: "<verify-1>", condition: <condition-1>, action: "<action-1>" },
    { name: "<verify-2>", condition: <condition-2>, action: "<action-2>" },
    { name: "<verify-3>", condition: <condition-3>, action: "<action-3>" }
  ]

  FOR each validation IN validations:
    IF NOT evaluate(validation.condition, result) THEN
      RETURN {
        status: "INVALID",
        reason: validation.name,
        action: validation.action,
        result: result
      }
    END IF
  END FOR

  RETURN { status: "VALIDATED", result: result }
END function
```

## 异常守卫（Exception-Guard）

### 异常类型

| 异常类型 | 触发条件 | 处理策略 |
|---------|---------|---------|
| `<exception-1>` | `<trigger-1>` | `<strategy-1>` |
| `<exception-2>` | `<trigger-2>` | `<strategy-2>` |
| `<exception-3>` | `<trigger-3>` | `<strategy-3>` |

### 实现模板

```pseudo
function exceptionGuard(error, context):
  handlers = {
    "<exception-1>": {
      strategy: "<strategy-1>",
      fallback: <fallback-action-1>
    },
    "<exception-2>": {
      strategy: "<strategy-2>",
      fallback: <fallback-action-2>
    }
  }

  handler = handlers[error.type] OR handlers["default"]

  CASE handler.strategy:
    WHEN "retry":
      RETURN retryWithBackoff(context, maxRetries: 3)
    WHEN "fallback":
      RETURN executeFallback(handler.fallback, context)
    WHEN "compensate":
      RETURN executeCompensation(context)
    OTHERWISE:
      RETURN { status: "FAILED", error: error }
  END CASE
END function
```

## 状态守卫（State-Guard）

### 状态机定义

```
┌─────────┐  event-1  ┌─────────┐
│ state-1 │ ────────→ │ state-2 │
└─────────┘           └─────────┘
     ↑                     │
     └──── event-2 ────────┘
```

### 状态转换规则

| 当前状态 | 触发事件 | 目标状态 | 前置条件 | 后置验证 |
|---------|---------|---------|---------|---------|
| `<state-1>` | `<event-1>` | `<state-2>` | `<precondition>` | `<postcondition>` |
| `<state-2>` | `<event-2>` | `<state-1>` | `<precondition>` | `<postcondition>` |

### 实现模板

```pseudo
function stateGuard(currentState, event, context):
  transitions = {
    "<state-1>": {
      "<event-1>": {
        target: "<state-2>",
        precondition: <check-precondition>,
        postcondition: <check-postcondition>
      }
    },
    "<state-2>": {
      "<event-2>": {
        target: "<state-1>",
        precondition: <check-precondition>,
        postcondition: <check-postcondition>
      }
    }
  }

  transition = transitions[currentState][event]

  IF NOT transition.precondition(context) THEN
    RETURN { status: "BLOCKED", reason: "Precondition failed" }
  END IF

  newState = transition.target

  IF NOT transition.postcondition(context) THEN
    RETURN { status: "ROLLBACK", reason: "Postcondition failed" }
  END IF

  RETURN { status: "TRANSITIONED", state: newState }
END function
```

## 守卫组合模式

### 链式守卫

```pseudo
result = preGuard(context)
  .then(execute)
  .then(postGuard)
  .catch(exceptionGuard)
```

### 并行守卫

```pseudo
results = parallel([
  guard-1(context),
  guard-2(context),
  guard-3(context)
])

IF all(results.passed) THEN
  proceed()
ELSE
  block(failed_guards)
END IF
```

### 条件守卫

```pseudo
IF context.type == "type-1" THEN
  apply(guard-set-1)
ELSE IF context.type == "type-2" THEN
  apply(guard-set-2)
ELSE
  apply(default-guard-set)
END IF
```

## 配置项

```yaml
guard:
  enabled: true
  strict_mode: true      # 严格模式：任何失败即阻断
  log_level: INFO
  timeout: 30s
  retry:
    enabled: true
    max_attempts: 3
    backoff: exponential
```

## 示例用法

### 示例 1: 前置守卫

```markdown
**场景**：<scenario-description>

**守卫检查**：
1. 检查 <condition-1>：✅ PASS
2. 检查 <condition-2>：✅ PASS
3. 检查 <condition-3>：✅ PASS

**结果**：PASS，允许执行
```

### 示例 2: 守卫阻断

```markdown
**场景**：<scenario-description>

**守卫检查**：
1. 检查 <condition-1>：✅ PASS
2. 检查 <condition-2>：❌ FAIL - <reason>

**结果**：BLOCKED，<action>
```

## 注意事项

1. <note-1>
2. <note-2>
3. <note-3>

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | <date> | 初始版本 |