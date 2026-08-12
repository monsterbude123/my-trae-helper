# Agent Delegate Protocol — 委派 GATE 头 + Completion Report 校验

> 主 agent 委派 sub-agent 时如何注入强制门禁,以及 sub-agent 汇报时如何校验。
> 这是 `[PROJECT-RULES-GATE]` 机制的完整协议。

---

## §0 协议要点

| 要点 | 说明 |
|------|------|
| 触发点 | 主 agent 调用 `Task()` 委派 sub-agent |
| 强制字段 | sub-agent 的 Completion Report 必须含 `rules_loaded` / `rules_skipped` |
| 失败行为 | 缺字段 = 🛑 REJECT(主 agent 必须打回重做,不接受"我已读但没声明") |
| 适用范围 | 任何 sub-agent 类型(general-purpose / search / Explore 等) |
| 与 V11 关系 | 本协议是 V11 同名协议的独立分发版,不带 PIPELINE / DOC_WHITELIST 块 |

---

## §1 主 agent 端 — 委派头部模板

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

完整模板: [workflows/sub-agent-delegate-load.md](../workflows/sub-agent-delegate-load.md)

---

## §2 sub-agent 端 — 必走 4 步

**Step 1**: 收到 prompt → 检测含 `[PROJECT-RULES-GATE]` 块(没有则向主 agent 报错"协议违反")

**Step 2**: 调 `Skill(name="project-rules")` → 拿到本任务相关 rules(按路由表 §3)

**Step 3**: `Read` 选中的 rule 文件(从 `.trae/skills/project_rules_skills/references/` 而非 `.trae/rules/`)

**Step 4**: 完成任务时,在 Completion Report 显式声明:

```yaml
rules_loaded:
  - coding-standards.md (reason: 改 API 涉及代码风格)
  - paths.md (reason: 改 API 涉及路径合法性)
rules_skipped:
  - stack.md
  - git.md
```

---

## §3 主 agent 端 — 校验规则

sub-agent 返回后,主 agent **必须**校验 Completion Report:

```python
def validate_rules_report(report: dict) -> bool:
    """校验 sub-agent 的 Completion Report 是否符合 [PROJECT-RULES-GATE] 协议"""
    required_fields = ["rules_loaded", "rules_skipped"]
    for field in required_fields:
        if field not in report:
            return False
    if not isinstance(report["rules_loaded"], list):
        return False
    if not isinstance(report["rules_skipped"], list):
        return False
    return True
```

**校验失败的处理**:

```
🛑 REJECT: sub-agent 未遵守 [PROJECT-RULES-GATE] 协议

缺失字段: rules_loaded / rules_skipped

请 sub-agent 重做,补全 rules_loaded / rules_skipped 字段后重报。
```

主 agent 不得在缺字段时自行脑补或视为通过。

---

## §4 路由表使用(场景 → rules)

主 agent / sub-agent 加载 Skill(name="project-rules") 后会看到本项目的路由表(SKILL.md §3)。常用映射:

| 场景 | 加载 |
|------|------|
| 改 API / 改契约 | coding-standards.md + paths.md |
| 改前端 / 改样式 | coding-standards.md + paths.md |
| 改依赖 / 改 build | stack.md + paths.md |
| 提 PR / 合分支 | git.md + paths.md |
| 修 bug | coding-standards.md + paths.md |
| 任何其他场景 | 全加载 |

**未命中场景 = 全加载**(避免漏加载导致规则违反)。

---

## §5 反例

### ❌ 错误:主 agent 不注入 GATE 头

```python
Task(
    subagent_type="general-purpose",
    description="改 API",
    prompt="请帮我改 user API..."  # 没有强制入口
)
```

### ❌ 错误:sub-agent 不声明 rules

Completion Report:
```yaml
artifacts: [user-api.ts 修改完成]
status: PASS
evidence: ...
# 缺 rules_loaded / rules_skipped → 🛑 REJECT
```

### ❌ 错误:sub-agent 直接 Read .trae/rules/

```
Read(".trae/rules/stack.md")  # 跳过 skill 入口 → 🛑 REJECT
```

### ✅ 正确:主 agent + sub-agent 双方遵守

主 agent prompt:
```python
prompt="""
[PROJECT-RULES-GATE]
  必须先调用 Skill(name="project-rules") 获取本任务所需 rules,再开始工作。
[/PROJECT-RULES-GATE]

[TASK]
  帮我改 user API:加一个分页参数
[/TASK]
"""
```

sub-agent Completion Report:
```yaml
artifacts: [user-api.ts 修改完成]
status: PASS
evidence: ...
rules_loaded:
  - coding-standards.md (reason: 改 API 涉及代码风格)
  - paths.md (reason: 改 API 涉及路径合法性)
rules_skipped:
  - stack.md
  - git.md
```

---

## §6 进阶:动态路由

如果项目 `.trae/rules/` 数量 > 6,主 agent 可在 SKILL.md §3 扩展路由表:

```markdown
| 改 Rust 后端 | coding-standards.md + paths.md + stack.md |
| 写新文档 | paths.md |
```

**注意**: 修改 SKILL.md 后,sub-agent 加载时会看到最新路由表。本 skill 不强制 forge 重跑(因为 SKILL.md 本身就是项目可编辑的),但建议主 agent 写 changelog。

---

## §7 与 V11 PIPELINE 协议共存

如果项目同时装 V11 和本 skill,主 agent 委派时**两个头部都要**:

```python
prompt="""
[PROJECT-RULES-GATE]              # 本 skill 注入
  必须先调用 Skill(name="project-rules") ...
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

两者**不冲突**:
- PROJECT-RULES-GATE: 管 rules 加载
- PIPELINE: 管 V11 阶段
- DOC_WHITELIST: 管可读文档
- FORBIDDEN: 管禁读路径

---

## §8 强制检查(汇总)

```
❌ 主 agent 委派时未注入 [PROJECT-RULES-GATE] = 🛑 REJECT
❌ Sub-agent 在 Completion Report 未声明 rules_loaded / rules_skipped = 🛑 REJECT
❌ Sub-agent 直接 Read .trae/rules/*.md(绕过 skill) = 🛑 REJECT
❌ Sub-agent 声明 rules_loaded 但实际没 Read(rule 名与 Read 不一致) = 🛑 REJECT
❌ 主 agent 校验不通过时自行脑补 = 🛑 REJECT
```
