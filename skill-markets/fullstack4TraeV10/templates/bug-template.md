---
layer: fact
bug_id: {module}-{seq}-{brief}
status: OPEN
severity: P1|P2|P3
created_at: {YYYY-MM-DD HH:mm}
---

# Bug: {brief}

## 用户原话

> {user_raw_quote}

## 用户操作

1. {step_1}
2. {step_2}
3. {step_3}

## 实际效果

- **现象**: {observed_anomaly}
- **截图/报错**: {screenshot_or_error}

## 关联功能文档

- {related_doc_path_or_section}

## 期望

{expected_behavior}

## 状态流转

| 时间 | 状态 | 操作者 | 说明 |
|------|------|--------|------|
| {created_at} | OPEN | 主上下文 | 录入 |

## 根因诊断

> 待 debugger 填写

## 修复记录

> 待 implementer 填写