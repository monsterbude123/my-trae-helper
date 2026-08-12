# Sub-Agent 委派模板 — PROJECT-RULES-GATE 头部

> 任何主 agent 委派 sub-agent 执行任务时,**头部必须**包含以下内容。
> 这是独立于 fullstack4TraeV11 的最小协议头,适用于任何 sub-agent 类型。

---

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

[TASK]
  {task-description, ≤200 chars}
[/TASK]

[OUTPUT]
  必填 4 字段 + rules_loaded / rules_skipped 清单:
  - artifacts
  - status (PASS | FAIL | PARTIAL)
  - evidence (command + output + file:line)
  - next_hook (任一阶段后钩子,本 skill 无关)
  - rules_loaded: [list of loaded rule files with reason]
  - rules_skipped: [list of skipped rule files]
[/OUTPUT]

{task-specific-content}
"""
)
```

---

## 与 fullstack4TraeV11 共存

如果项目同时装 V11,头部还要加 V11 的块:

```python
prompt="""
[PROJECT-RULES-GATE]              # 本 skill 注入
  ...
[/PROJECT-RULES-GATE]

[PIPELINE]                         # V11 注入
  stage: {stage-name}
[/PIPELINE]

[DOC_WHITELIST]                    # V11 注入
  ...
[/DOC_WHITELIST]

[FORBIDDEN]                        # V11 注入
  ...
[/FORBIDDEN]

[TASK]
  ...
[/TASK]
"""
```

两者职责不重叠:
- **PROJECT-RULES-GATE**: 管 rules 加载(本 skill)
- **PIPELINE / DOC_WHITELIST / FORBIDDEN**: 管 V11 阶段 / 文档可见性 / 禁读路径

---

## 强制检查

```
❌ 主 agent 委派 sub-agent 时未注入 [PROJECT-RULES-GATE] 头部 = 🛑 REJECT
❌ Sub-agent 在 Completion Report 未声明 rules_loaded / rules_skipped = 🛑 REJECT
❌ Sub-agent 直接 Read .trae/rules/*.md(绕过 skill) = 🛑 REJECT
```

---

## 反例

### ❌ 错误:不注入 PROJECT-RULES-GATE

```python
Task(
    subagent_type="general-purpose",
    description="改 API",
    prompt="请帮我改 user API..."  # 没有强制入口
)
```

### ❌ 错误:sub-agent 漏声明

Completion Report:
```yaml
artifacts: [user-api.ts 修改完成]
status: PASS
evidence: ...
# 缺 rules_loaded / rules_skipped → 🛑 REJECT
```

### ✅ 正确:头部注入 PROJECT-RULES-GATE + sub-agent 完整声明

主 agent prompt:
```python
prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
[/PROJECT-RULES-GATE]

[TASK]
  请帮我改 user API 加一个分页参数
[/TASK]
"""
```

sub-agent Completion Report:
```yaml
artifacts: [user-api.ts 修改完成]
status: PASS
evidence: |
  Read .trae/skills/project_rules_skills/references/coding-standards.md
  Read .trae/skills/project_rules_skills/references/paths.md
  改 src/api/user.ts: 增加 pagination 参数
rules_loaded:
  - coding-standards.md (reason: 改 API 涉及代码风格)
  - paths.md (reason: 改 API 涉及路径合法性)
rules_skipped:
  - stack.md
  - git.md
```

---

## 协议出处

- 来源: project-rules-gate v0.1(references/agent-delegate-protocol.md)
- 衍生: fullstack4TraeV11 [PROJECT-RULES-GATE] 块(同名同协议)
- 适用范围: 任何项目,任何 sub-agent 类型

---

*由 project-rules-gate 锻造器自动复制到 .trae/skills/project_rules_skills/workflows/*
