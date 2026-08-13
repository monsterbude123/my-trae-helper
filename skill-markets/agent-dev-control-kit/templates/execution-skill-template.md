# Execution Skill Template — 执行类技能模板

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

<详细描述此技能的功能和用途>

## 输入规范

### 必需参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `<param-1>` | `<type>` | `<description>` | `<example>` |
| `<param-2>` | `<type>` | `<description>` | `<example>` |

### 可选参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `<param-3>` | `<type>` | `<default>` | `<description>` |

## 执行流程

### Phase 1: 输入验证

```pseudo
1. 检查必需参数是否存在
2. 验证参数类型和格式
3. 检查前置条件
4. 若验证失败 → 输出错误信息并终止
```

### Phase 2: 核心执行

```pseudo
1. 初始化执行环境
2. 执行主逻辑
3. 记录执行日志
4. 处理中间状态
```

### Phase 3: 输出校验

```pseudo
1. 验证输出格式
2. 检查输出完整性
3. 生成执行报告
4. 返回结果
```

### Phase 4: 清理与收尾

```pseudo
1. 释放临时资源
2. 更新状态记录
3. 触发后置回调（如有）
```

## 输出规范

### 成功输出

```json
{
  "status": "success",
  "data": {
    "<result-key-1>": "<result-value-1>",
    "<result-key-2>": "<result-value-2>"
  },
  "metrics": {
    "duration": "<execution-time>",
    "steps": "<step-count>"
  }
}
```

### 失败输出

```json
{
  "status": "error",
  "error": {
    "code": "<error-code>",
    "message": "<error-message>",
    "phase": "<failed-phase>",
    "context": "<error-context>"
  }
}
```

## 错误处理

### 错误分级

| 级别 | 代码前缀 | 处理方式 |
|------|---------|---------|
| CRITICAL | E1xx | 立即终止，输出错误报告 |
| ERROR | E2xx | 终止当前操作，尝试恢复 |
| WARNING | E3xx | 记录警告，继续执行 |
| INFO | E4xx | 记录信息，不影响执行 |

### 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|---------|
| E101 | 缺少必需参数 | 检查输入参数 |
| E102 | 参数类型错误 | 验证参数格式 |
| E201 | 执行超时 | 增加超时时间或优化逻辑 |
| E202 | 资源不足 | 释放资源或扩容 |

## 示例用法

### 示例 1: <scenario-1>

```markdown
**用户请求**：<user-request>

**执行过程**：
1. 输入验证：验证 <param-1> = <value-1>
2. 核心执行：<action-description>
3. 输出校验：确认 <output-1> 符合预期
4. 返回结果：<result-description>
```

### 示例 2: <scenario-2>

```markdown
**用户请求**：<user-request>

**执行过程**：
1. 输入验证：<validation-step>
2. 核心执行：<execution-step>
3. 输出校验：<verification-step>
4. 返回结果：<result>
```

## 配置项

```yaml
execution:
  timeout: 300s        # 执行超时时间
  retry: 3             # 失败重试次数
  log_level: INFO      # 日志级别
  parallel: false      # 是否并行执行
```

## 依赖说明

### 必需依赖

- `<dependency-1>`：用于 <purpose-1>
- `<dependency-2>`：用于 <purpose-2>

### 可选依赖

- `<optional-dep-1>`：用于 <purpose>

## 注意事项

1. <note-1>
2. <note-2>
3. <note-3>

## 版本历史

| 版本 | 日期 | 变更说明 |
|------|------|---------|
| 1.0.0 | <date> | 初始版本 |