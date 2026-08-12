# Sub-Agent 委派模板 — PROJECT-RULES-GATE 头部

> 任何主 agent 委派 sub-agent 执行任务时,**头部必须**包含以下内容。

## 完整委派头部

```python
Task(
    subagent_type="{agent-type}",
    description="<task-summary>",
    prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
  在 Completion Report 中必须声明 rules_loaded / rules_skipped 清单。
[/PROJECT-RULES-GATE]

[PIPELINE]
  stage: {stage-name}
  ...
[/PIPELINE]

[DOC_WHITELIST]
  {whitelist}
[/DOC_WHITELIST]

[FORBIDDEN]
  docs/archive/**, .trae/tmp/**
[/FORBIDDEN]

[TASK]
  {task-description, ≤200 chars}
[/TASK]

[OUTPUT]
  必填 4 字段 + rules_loaded / rules_skipped 清单:
  - artifacts
  - status (PASS | FAIL | PARTIAL)
  - evidence (command + output + file:line)
  - next_hook (pre-stage.sh | post-stage.sh | pre-accept.sh)
  - rules_loaded: [list of loaded rule files with reason]
  - rules_skipped: [list of skipped rule files]
[/OUTPUT]

{task-specific-content}
"""
)
```

## 强制检查

```
❌ 主 agent 委派 sub-agent 时未注入 [PROJECT-RULES-GATE] 头部 = 🛑 REJECT
❌ Sub-agent 在 Completion Report 未声明 rules_loaded / rules_skipped = 🛑 REJECT
❌ Sub-agent 直接 Read .trae/rules/*.md(绕过 skill) = 🛑 REJECT
```

## 反例

```python
# ❌ 错误:不注入 PROJECT-RULES-GATE
Task(
    subagent_type="general-purpose",
    description="改 API",
    prompt="请帮我改 user API..."  # 没有强制入口
)

# ✅ 正确:头部注入 PROJECT-RULES-GATE
Task(
    subagent_type="general-purpose",
    description="改 API",
    prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
[/PROJECT-RULES-GATE]

[TASK]
  请帮我改 user API...
[/TASK]
"""
)
```

---

*来源: fullstack4TraeV11 init-from-zero.py --rules-as-skill 自动生成。*