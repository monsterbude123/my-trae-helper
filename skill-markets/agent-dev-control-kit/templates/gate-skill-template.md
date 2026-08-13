# Gate Skill Template — 门禁类技能模板

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

<详细描述此门禁技能的功能和用途>

## 门禁层级

| 层级 | 触发时机 | 检查项 | 通过标准 |
|------|---------|--------|---------|
| L1 | <trigger-1> | <checks-1> | <criteria-1> |
| L2 | <trigger-2> | <checks-2> | <criteria-2> |
| L3 | <trigger-3> | <checks-3> | <criteria-3> |
| L4 | <trigger-4> | <checks-4> | <criteria-4> |

## 检查项定义

### Check 1: <check-name-1>

**层级**：<L1/L2/L3/L4>

**执行命令**：<command>

**通过标准**：<pass-criteria>

**失败处理**：<fail-action>

**超时时间**：<timeout>

### Check 2: <check-name-2>

**层级**：<L1/L2/L3/L4>

**执行命令**：<command>

**通过标准**：<pass-criteria>

**失败处理**：<fail-action>

**超时时间**：<timeout>

## 门禁执行流程

### 链式执行

```
┌──────────┐    ┌──────────┐    ┌──────────┐
│ Check 1  │ →  │ Check 2  │ →  │ Check 3  │
└──────────┘    └──────────┘    └──────────┘
     ↓               ↓               ↓
   PASS/FAIL      PASS/FAIL      PASS/FAIL
```

### 执行伪代码

```pseudo
function executeGate(context):
  checks = [
    { name: "<check-1>", command: "<cmd-1>", criteria: "<criteria-1>" },
    { name: "<check-2>", command: "<cmd-2>", criteria: "<criteria-2>" },
    { name: "<check-3>", command: "<cmd-3>", criteria: "<criteria-3>" }
  ]

  results = []

  FOR each check IN checks:
    result = execute(check)

    IF result.status == "FAIL" THEN
      RETURN {
        status: "BLOCKED",
        failed_at: check.name,
        results: results
      }
    END IF

    results.push(result)
  END FOR

  RETURN {
    status: "PASS",
    results: results
  }
END function
```

## 通过标准

### 标准定义

| 指标 | 阈值 | 说明 |
|------|------|------|
| `<metric-1>` | `<threshold-1>` | `<description-1>` |
| `<metric-2>` | `<threshold-2>` | `<description-2>` |
| `<metric-3>` | `<threshold-3>` | `<description-3>` |

### 验证逻辑

```pseudo
function validatePass(result):
  thresholds = {
    "<metric-1>": <threshold-1>,
    "<metric-2>": <threshold-2>,
    "<metric-3>": <threshold-3>
  }

  FOR each metric, threshold IN thresholds:
    IF result[metric] > threshold THEN
      RETURN {
        status: "FAIL",
        reason: f"{metric} exceeded threshold: {result[metric]} > {threshold}"
      }
    END IF
  END FOR

  RETURN { status: "PASS" }
END function
```

## 门禁报告格式

### 成功报告

```
=== Gate Check Report ===
Time: <timestamp>
Level: <L1/L2/L3/L4>
Branch: <branch-name>

Checks:
  ✅ <check-1>: passed (<duration-1>)
  ✅ <check-2>: passed (<duration-2>)
  ✅ <check-3>: passed (<duration-3>)

Metrics:
  <metric-1>: <value-1> (threshold: <threshold-1>) ✅
  <metric-2>: <value-2> (threshold: <threshold-2>) ✅
  <metric-3>: <value-3> (threshold: <threshold-3>) ✅

Result: ✅ PASS
Total Duration: <total-duration>
```

### 失败报告

```
=== Gate Check Report ===
Time: <timestamp>
Level: <L1/L2/L3/L4>
Branch: <branch-name>

Checks:
  ✅ <check-1>: passed (<duration-1>)
  ❌ <check-2>: FAILED - <error-message>
  ⏭️  <check-3>: skipped (blocked by previous failure)

Result: 🛑 BLOCKED
Failed at: <check-2>
Reason: <error-message>

Action Required:
  1. <action-1>
  2. <action-2>
```

## 门禁配置

### YAML 配置

```yaml
gate:
  name: "<gate-name>"
  level: <L1/L2/L3/L4>
  trigger: "<trigger-event>"

  checks:
    - name: "<check-1>"
      command: "<cmd-1>"
      timeout: <timeout-1>
      blocking: true
      retry: 0

    - name: "<check-2>"
      command: "<cmd-2>"
      timeout: <timeout-2>
      blocking: true
      retry: 1

  thresholds:
    <metric-1>: <threshold-1>
    <metric-2>: <threshold-2>

  on_fail:
    action: "block"
    notify: ["<channel-1>", "<channel-2>"]
```

### JSON 配置

```json
{
  "gate": {
    "name": "<gate-name>",
    "level": "<L1/L2/L3/L4>",
    "trigger": "<trigger-event>",
    "checks": [
      {
        "name": "<check-1>",
        "command": "<cmd-1>",
        "timeout": <timeout-1>,
        "blocking": true,
        "retry": 0
      },
      {
        "name": "<check-2>",
        "command": "<cmd-2>",
        "timeout": <timeout-2>,
        "blocking": true,
        "retry": 1
      }
    ],
    "thresholds": {
      "<metric-1>": <threshold-1>,
      "<metric-2>": <threshold-2>
    },
    "on_fail": {
      "action": "block",
      "notify": ["<channel-1>", "<channel-2>"]
    }
  }
}
```

## 集成方式

### Git Hooks 集成

```bash
# .husky/pre-commit
npm run gate:commit

# .husky/pre-push
npm run gate:push
```

### CI/CD 集成

```yaml
# .github/workflows/gate.yml
name: Gate Checks
on: [push, pull_request]

jobs:
  gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run gate:all
```

### 本地 CLI 集成

```bash
# 执行所有门禁检查
npm run gate:all

# 执行特定层级门禁
npm run gate:L1
npm run gate:L2
npm run gate:L3
npm run gate:L4

# 跳过门禁（紧急情况）
npm run gate:skip --reason="emergency fix"
```

## 错误处理

### 错误码定义

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| G001 | 检查命令执行失败 | 检查命令是否正确 |
| G002 | 检查超时 | 增加超时时间或优化检查 |
| G003 | 阈值超标 | 修复问题或调整阈值 |
| G004 | 依赖检查未通过 | 先通过依赖检查 |

### 错误处理流程

```pseudo
function handleGateError(error):
  CASE error.code:
    WHEN "G001":
      log("Check command failed: " + error.detail)
      suggest("Verify command is installed and accessible")
    WHEN "G002":
      log("Check timeout: " + error.check)
      suggest("Increase timeout or optimize check")
    WHEN "G003":
      log("Threshold exceeded: " + error.metric)
      suggest("Fix issue or adjust threshold")
    OTHERWISE:
      log("Unknown error: " + error.code)
  END CASE

  RETURN generateReport(error)
END function
```

## 示例用法

### 示例 1: 正常通过

```markdown
**触发**：git commit

**执行检查**：
1. lint: ✅ passed (2s)
2. typecheck: ✅ passed (3s)
3. test:unit: ✅ passed (5s) - 42 tests passed

**结果**：✅ PASS，允许提交
```

### 示例 2: 门禁阻断

```markdown
**触发**：git push

**执行检查**：
1. lint: ✅ passed (2s)
2. typecheck: ❌ FAILED
   - src/utils.ts:42: Type 'string' is not assignable to type 'number'

**结果**：🛑 BLOCKED，修复类型错误后重新提交
```

## 注意事项

1. <note-1>
2. <note-2>
3. <note-3>

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | <date> | 初始版本 |