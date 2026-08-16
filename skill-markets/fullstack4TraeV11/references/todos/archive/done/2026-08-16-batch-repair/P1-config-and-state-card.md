# P1 — 配置 / 状态卡 / §14.5 优先级

> 状态:P1 = 配置层与状态卡字段层未消费。本文件 3 条。

---

## P1-1 — `fullstack4traev11.config.yaml` 字段定义但无运行消费脚本

```yaml
---
id: AUDIT-#1
title: 新增 scripts/project-priority-resolver.py 实现 Layer 3 项目级覆盖算法
status: done
priority: P1
discovered_at: 2026-08-16
discovered_by: 子代理 B(从 dependency-config.md §Layer 3 蒸馏)
protocol_ref: references/dependency-config.md L70-125(Layer 3 字段定义 + resolve_skills 伪代码)
parser_ref: grep `def resolve_skills` 仅命中 dependency-config.md L107(md 伪代码),scripts/ 无实现
fix_path: scripts/project-priority-resolver.py 新建
completed_at: 2026-08-16T
evidence: scripts/project-priority-resolver.py 新建(248 行)含 3 子命令 --stage/--check-forbidden/--merge-anti-patterns;主上下文兜底跑 --stage 3/implement --json exit 0 输出真实三层 layers 字段;tests/unit/test_project_priority_resolver.py 12 用例全 PASS
---
```

### 背景

[references/dependency-config.md](references/dependency-config.md) §Layer 3 (L70-125) 定义 `.trae/fullstack4traev11.config.yaml` 全部字段:project / stage_config / required_stages / forbidden_paths。同时给出 `resolve_skills(stage_id, project_config)` Python 算法,作为 3 层优先级解析的伪代码。

但脚本里无任何程序化消费 — `forbidden_paths` / `stage_config.{stage_id}.skills` 只在 md 中存在。

### 协议层证据

`references/dependency-config.md` L107-125:

```python
def resolve_skills(stage_id, project_config):
    """3 层优先级解析"""
    skills = []
    skills.extend(load_global_skills())            # Layer 1
    v11_config = load_v11_stage_config(stage_id)
    skills.extend(v11_config.get("skills", []))    # Layer 2
    project_overrides = project_config.get("stage_config", {}).get(stage_id, {})
    project_skills = project_overrides.get("skills", [])
    skills = project_skills + skills                # Layer 3 优先
    return list(dict.fromkeys(skills))
```

### 解析层证据

```bash
$ grep -rn "project-priority-resolver\|resolve_skills(" scripts/
# 零命中
```

唯一命中是 `references/dependency-config.md` L107(伪代码本身)。

### 影响范围

- `forbidden_paths` 字段(配置禁读路径,如 `docs/archive/**`, `.trae/tmp/**`)从未被 gate 脚本读取 → agent 误读 archive 是无阻断的
- `stage_config.skills` 项目级覆盖 = 协议主张但无解析 → 等于"项目级优先"承诺空头
- 配置写啥都行,因为没有脚本告诉"配置必须生效"

### 建议路径

新增 `scripts/project-priority-resolver.py`:

```python
# 接口
--project-root <path>                     # 读 .trae/fullstack4traev11.config.yaml
--stage <id>                              # 输出该 stage 的合并 skill 列表
--check-forbidden <path>                  # 校验 path 是否在 forbidden_paths
--json
```

修完跑真反例:

```bash
# P 项目 .trae/fullstack4traev11.config.yaml 含 required_stages + forbidden_paths
python project-priority-resolver.py --project-root . --stage 3/implement --json
# → 期望输出 skills 列表(项目级 cover 在 V11 默认之上)
python project-priority-resolver.py --project-root . --check-forbidden docs/archive/foo.md
# → 期望 exit 0 阻断
```

---

## P1-2 — state-card validator 缺 17 字段校验

```yaml
---
id: AUDIT-#2
title: state-card-validator.py 补 17 字段校验
status: done
priority: P1
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: references/state-card-protocol.md L78-152(~30 字段全列表)
parser_ref: scripts/state-card-validator.py L26-31(REQUIRED_FIELDS 13) + L34(NULLABLE_FIELDS 5)
fix_path: scripts/state-card-validator.py L58 validate_fields() 扩 17 字段
completed_at: 2026-08-16T
evidence: scripts/state-card-validator.py L46-50 新增 VALID_BUG_SEVERITY + RESET_HISTORY_REQUIRED_KEYS;L138-220 5 类校验块;tests/unit/test_state_card_validator_extended.py 12 用例全 PASS
---
```

### 背景

`state-card-protocol.md` 列 ~30 字段。validator 实际校验 13 REQUIRED + 5 NULLABLE = 18 字段。**缺口 ~17 字段未校验**(以 protocol 定义为准)。

### 协议层证据

`references/state-card-protocol.md` L78-152:
- 13 REQUIRED
- 8 OPTIONAL(`visual_evidence.screenshots` / `parent_change` / `related_changes` / `bug_id` / `bug_severity` / `risk_level` / `priority` / `reset_history`)
- `next_stage.skill_name` + `expected_inputs` + `prerequisites`

### 解析层证据

```bash
$ grep "contains_change_components\|parent_change\|related_changes\|risk_level\|priority" scripts/state-card-validator.py
# 零命中
```

`scripts/state-card-validator.py` L215-231 还承认:
> "真正权限校验需 git diff 上下文工作"

### 影响范围

- 状态卡字段完全自由填写,protocol 形同虚设
- §5.8 子代理擅自升级状态 = 仅有 info 提示,**未做 git diff 实际校验**
- reset_history / parent_change 等"流程关键"字段无脚本兜底

### 建议路径

`scripts/state-card-validator.py` L58 `validate_fields()` 扩 5 类校验:

1. `stage_status == "completed"` → `stage_ended_at` 必填非 null
2. `card_type == "bug"` → `bug_severity ∈ {P0, P1, P2, P3}`(对照 [bug-state-machine.md L11-19])
3. `parent_change` 引用必须存在(`docs/specs/changes/{parent_change}/.state-card.md` 文件存在)
4. `visual_evidence.screenshots[].read_by_main_context == true` 否则 FAIL
5. `reset_history` 必含 `date` / `from_stage` / `to_stage` / `reason` / `reset_by` 5 字段

修完跑:

```bash
# 真反例 1:完成态但 stage_ended_at=null → 期望 FAIL
# 真反例 2:bug 卡无 bug_severity → 期望 FAIL
# PASS 态:valid fixture → 期望 PASS
```

---

## P1-3 — §14.5 项目级 rules > V11 通用层优先级无解析脚本

```yaml
---
id: AUDIT-#8
title: scripts/project-priority-resolver.py 实现 §14.5 优先级合成
status: done
priority: P1(与 P1-1 共用同一脚本)
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: references/SKILL.md L702-740 §14.5(MUST/NEVER/适用场景)
parser_ref: grep §14.5 / `project-priority-resolver` 在 scripts/ 中零命中
fix_path: 见 P1-1(同一脚本 + 不同子命令)
completed_at: 2026-08-16T
evidence: 与 P1-1 合并完成 — scripts/project-priority-resolver.py --merge-anti-patterns 子命令实现 Layer 3 project rules 优先合成
---
```

### 背景

SKILL.md §14.5 是 V11.2 NEW 核心承诺:"项目级 rules 优先于 V11 通用层"。但 [V11.2 §14.5 references/SKILL.md L702-740](references/SKILL.md) 协议层有 MUST / NEVER / 适用场景 + §14.5.2 引用触发词,scripts/ 中无任何消费。

### 协议层证据

`references/SKILL.md` L702-740 §14.5:
```
MUST: 项目级 rules 优先于 V11 通用层
MUST: 项目级 .trae/skills/project_rules_skills/references/anti-patterns.md 可补 V11 通用层缺失的反例
MUST: 项目级 .trae/skills/project_rules_skills/rules/governance.md 可强制 V11 通用层未硬化的门槛
NEVER: 盲信 V11 通用层, 缺项目级叠加
```

适用场景:
- V11 通用层缺反例 → 项目级 anti-patterns.md 补全
- V11 通用层误判 → 项目级 rules 纠正
- V11 通用层缺硬门槛 → 项目级 governance 强制

### 解析层证据

```bash
$ grep -rn "project-priority-resolver\|priority.*resolver\|§14.5" scripts/
# 仅 CHANGELOG.md 引用
$ grep -rn "anti-patterns.md\|governance.md" scripts/
# 零命中
```

### 影响范围

- 项目级 anti-patterns.md / governance.md 即使写了"强制门槛",**V11 脚本不读**
- 主上下文读 V11 references/ 时看不到项目级新增反例
- 真实失败案例不会被项目级 rules 拦截

### 建议路径

与 P1-1 共用 `scripts/project-priority-resolver.py`,加子命令:

```bash
python project-priority-resolver.py \
  --project-root . \
  --merge-anti-patterns \
  --output references/merged-anti-patterns.md
```

输出:合并 V11 通用层 + 项目级 anti-patterns.md,去重 + 同名合并后给主上下文读。

---

## 子代理 A 相关 — `config-files-glossary.md` 已交付(2026-08-16)

```yaml
---
id: GLOSSARY-2026-08-16
title: 子代理 A 已交付 config-files-glossary.md(本目录同包)
status: done
priority: P1(归属本组别)
discovered_at: 2026-08-16
discovered_by: 主上下文会话
delivered_at: 2026-08-16
delivered_path: references/config-files-glossary.md
evidence: 36 行,5 段统一 schema
---
```

文档化已完成(非代码层修复),后续 P1-1 / P1-3 实施时引用此文件作为"schema 来源"。

