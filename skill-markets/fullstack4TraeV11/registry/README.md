# V11 Flow 层 Registry（声明式门禁注册表）

> **定位**：V11 的 **flow 层**（纯程序化解析）。人类/agent 不硬读本目录，由脚本程序化消费。
> **对比**：fact 层（SKILL.md / README / references/*.md）供人类+agent 阅读；本目录供脚本解析。
> **设计对齐**：agent-dev-control-kit 的 `registry/` 模式（gates.yaml / guards.yaml 声明式 + config_schema 校验）。

---

## 四表结构

| 表 | 文件 | 职责 | 消费脚本 |
|----|------|------|---------|
| 门禁表 | `gates.yaml` | 13 个 stage 每个的门禁声明（id/脚本/触发宿主/校验） | `run-all-guards.py` / `stage-gate.py` |
| 守卫表 | `guards.yaml` | 公共守卫脚本声明（id/脚本/config_schema/阈值） | `run-all-guards.py` |
| 状态机表 | `state-machine.yaml` | 状态卡 = 状态机（状态/转换/驾驶舱角色） | `_lib_state_card.py` / `state-card-validator.py` |
| 修复流程表 | `repair-flow.yaml` | Bug 修复流程（触发/步骤/门禁） | `run-all-guards.py` |

---

## 设计原则

1. **fact / flow 分离**：人类读 fact 层（.md），脚本读 flow 层（.yaml）。禁止在 .yaml 里写人类长文，禁止在 .md 里定义程序化门禁逻辑。
2. **状态卡 = 状态机**：状态卡本质是状态机，`current_stage` 是当前状态，`next_stage` 是转换。驾驶舱角色（主上下文）是唯一允许改状态字段的 actor。
3. **每 stage 必有一门禁**：13 个 stage 每个必须在 `gates.yaml` 登记，不允许"无门禁"stage。
4. **可解析性铁律**：所有 .yaml 必须能被 `yaml.safe_load` 解析 + 通过 schema 校验，否则 `run-all-guards.py` 报 FAIL。
5. **脚本统一消费**：不靠 agent 硬读 md 表格，全部由脚本读 registry 决定跑什么门禁。

---

## Schema 契约（四表字段规范）

### gates.yaml

```yaml
version: 1.0.0
description: V11 门禁注册表（13 stage 每个必登记一门禁）
gates:
  - id: stage-1-spec            # 唯一 id
    stage: 1/spec               # 对应 stage（格式 {n}/{name}）
    name: Spec 门禁
    script: spec-validate-hook.py   # 关联脚本（scripts/ 下）
    host: husky-pre-commit          # 触发宿主：husky-pre-commit | husky-pre-push | stage-gate | manual
    guards: [spec-frontmatter]      # 依赖的守卫 id（guards.yaml）
    required_artifacts: ["docs/specs/changes/{change_id}/spec.md"]
    fail_action: BLOCK             # BLOCK | WARN | ALLOW
```

### guards.yaml

```yaml
version: 1.0.0
description: V11 守卫注册表
guards:
  - id: spec-frontmatter
    name: Spec frontmatter 校验
    script: spec-validate-hook.py
    category: quality
    config_schema: schemas/guards/spec-frontmatter.json
    default_threshold: null
```

### state-machine.yaml

```yaml
version: 1.0.0
description: V11 状态卡状态机定义
initial_state: -1/intake
terminal_states: [5/accept]
pilot: main-context          # 驾驶舱角色：唯一允许改状态字段的 actor
states:
  - id: -1/intake
    name: 需求摄取
    allowed_transitions: [0/plan]
    required_artifacts: []
    gate: stage-intake
  - id: 0/plan
    name: 规划
    allowed_transitions: [0.5/test-plan]
    required_artifacts: [plan.md]
    gate: stage-plan
transitions:
  - from: -1/intake
    to: 0/plan
    condition: "stage_gate PASS"
    gate: stage-gate.py
```

### repair-flow.yaml

```yaml
version: 1.0.0
description: V11 Bug 修复流程声明
triggers:
  - id: bug-reported
    name: Bug 上报
    gate: reason-classifier.py
steps:
  - id: step-1-e2e-fail
    name: e2e 先行确认 FAIL
    gate: e2e-first
  - id: step-2-6layer
    name: 6 层排查
    gate: six-layer-diagnosis
terminal_condition: "tests pass + user confirmed CLOSED"
gates:
  - id: e2e-first
    name: e2e 先行门禁
    script: acceptance-audit.py
    fail_action: BLOCK
```

---

## 校验方式

```bash
# 全量跑（读四表决定门禁）
python scripts/run-all-guards.py --registry-dir registry/ --project-root .

# 单表校验
python scripts/run-all-guards.py --registry-dir registry/ --table gates --validate-only
```

---

*flow 层建立于 V11.5（2026-08-14）— 对齐 agent-dev-control-kit registry 模式*