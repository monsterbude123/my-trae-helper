# Bug 单模板 — Stage -1 Intake / Stage 6 Bug Fix

> 位置: `docs/bugs/{bug-id}.md`

---

```yaml
---
bug_id: {module}-{NNN}-{slug}
title: "{一句话描述}"
severity: P0 | P1 | P2
status: OPEN | IN_PROGRESS | CLOSED
created_at: {ISO 8601}
updated_at: {ISO 8601}
reporter: "主上下文"
assignee: "debugger"
---

# Bug: {title}

## 1. 症状 (Symptom)

{用户实际看到}

## 2. 期望 (Expected)

{正确行为}

## 3. 复现步骤 (Reproduction Steps)

1. {步骤 1}
2. {步骤 2}
3. {步骤 3}

## 4. 环境信息 (Environment)

- OS: {Windows/Mac/Linux}
- 浏览器: {Chrome 100+}
- 版本: {1.2.3}

## 5. 影响范围 (Impacted Users)

{用户/范围 + 频率}

## 6. 触发词 (Trigger Phrase)

{原始用户输入}

## 7. 6 层排查记录（Stage 6 填写）

| 层 | 排查结果 |
|----|---------|
| 网络层 | {N/A or 异常} |
| 接入层 | {N/A or 异常} |
| 应用层 | {根因} |
| 数据层 | {N/A or 异常} |
| 集成层 | {N/A or 异常} |
| 客户端层 | {N/A or 异常} |

## 8. e2e 先行测试（Stage 6 Step 2）

`tests/e2e/test_bug_{id}.py`:
```python
def test_bug_{id}_reproduction():
    result = reproduce_bug_steps()
    assert result == expected
```

INITIAL 状态: FAIL ✅（证明 bug 真实存在）

## 9. 修复 (Fix)

### 根因
{6 层排查结论}

### 修复文件
- file:line: {改动}
- file:line: {改动}

### 测试
- 单元测试: file:line PASS
- 集成测试: file:line PASS

## 8.5 关闭记录（CLOSED 必填）

- **关闭时间**: {ISO 8601}
- **关闭人**: debugger
- **根因**: {根因描述}
- **修复文件**: [file:line list]
- **关闭方式**: e2e PASS + 回归 PASS + 用户签字
```

---

## 关联引用

- [Stage -1 Intake](../skills/01-intake/SKILL.md)
- [Stage 6 Bug Fix](../skills/12-bug-fix/SKILL.md)
- [bug-state-machine.md](../skills/12-bug-fix/references/bug-state-machine.md)