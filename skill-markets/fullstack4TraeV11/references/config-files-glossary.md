# V11 项目级配置文件总览（4 类文件）

> `init-from-zero.py` 跑完后,项目根 `.trae/` 沉淀 4 类配置文件。本文件只做指针化索引,字段不重复 README/SKILL.md。

## §1 4 类文件速查

| 文件 | 角色 | schema 来源 |
|------|------|-------------|
| `.trae/fullstack4traev11.config.yaml` | Layer 3 项目级 stage_config 覆盖(项目 > V11 > 全局) | `dependency-config.md §Layer 3` |
| `.trae/hooks.json` | TRAE IDE 5 种 event hook 注册 | `.trae/hooks/HOOKS.md`(项目内) |
| `.trae/registry/{gates,guards,state-machine,repair-flow}.yaml` | Flow 层 Registry — 13 stage 门禁声明 | `registry/README.md` |
| 状态卡(项目级 + change 级 + bug 级) | V11 状态机本体,每 stage 流转写一次 | `state-card-protocol.md §二` |

## §2 统一字段表

### 2.1 `.trae/fullstack4traev11.config.yaml`
生成时机 `init-from-zero.py` Step 1 `create_config`(L135-150)。默认字段 `project` / `stage_config` / `required_stages` / `forbidden_paths`;扩展字段 `project_skills` / `hooks` / `state_card` / `report_growth` / `document_layer` / `health_legend`。谁可改:主上下文(子代理 Edit 需白名单)。运行时由 `stage-gate.py` / `run-all-guards.py` / registry 解析时读。失效后果:stage_config 覆盖跳过 → V11.5 项目级优先失效。

### 2.2 `.trae/hooks.json`
生成时机:TRAE IDE 自动初始化;init 仅生成 `hooks/` 目录 shell(L153-195)。关键 hook:SessionStart→gitnexus-session-check + session-start;PreToolUse→doc-sync-gate + contract-gate;PostToolUse→spec-validate + auto-test + drift-detect;Stop→tasks-integrity + gitnexus-session-finalize。谁可改:仅贾维斯(V11.7.0 hash 锁 + 白名单)。失效后果:hooks-fidelity.py FAIL → §0.5.2 加载协议第 1 项 FAIL。

### 2.3 `.trae/registry/*.yaml`
生成时机:init Step 1 创 `.trae/registry/` 目录,默认 = V11 通用层,项目可自定义。关键字段(gates):`id` / `stage`(必 13 stage) / `name` / `layer`(docs/module/app/system) / `script` / `host` / `guards` / `required_artifacts` / `fail_action`。谁可改:主上下文(无贾维斯白名单,改后重跑 `run-all-guards.py` 验证)。失效后果:run-all-guards.py FAIL → 13 stage 门禁矩阵失效。

### 2.4 状态卡(3 类)
路径:`docs/specs/.state-card.md`(项目级)+ `docs/specs/changes/{id}/.state-card.md`(change 级)+ `docs/bugs/{id}/.state-card.md`(bug 级)。生成时机:init Step 4 建 `docs/` 骨架,`.state-card.md` 内容由 agent 填充,init 不写。关键字段:`card_type` / `card_id` / `current_stage` / `stage_status` / `health` / `artifacts` / `gate_result` / `next_stage`。5 protected 字段:`stage_status` / `current_stage` / `gate_result.status` / `health` / `next_stage.id`(仅主上下文)。失效后果:gate FAIL → 流水线冻结;陈旧(updated_at > 30 分钟且 working)→ validator L108 FAIL。

## §3 何时跑 schema 校验

```
1. 改 fullstack4traev11.config.yaml → run-all-guards.py --validate-only
2. 改 .trae/registry/*.yaml      → run-all-guards.py --table gates --validate-only
3. 改 .state-card.md              → state-card-validator.py <path>
4. 改 hooks.json / .trae/hooks/*  → hooks-fidelity.py(hash 锁 + 5 event 覆盖)
```

## §4 升级字段生效顺序

```
1. README.md / SKILL.md / CHANGELOG.md(协议源)
2. registry/{gates,state-machine,repair-flow}.yaml(stage / 转换 / 门禁)
3. fullstack4traev11.config.yaml(项目级 stage_config 覆盖)
4. .state-card.md(current_stage / next_stage 同步)
5. run-all-guards.py + state-card-validator.py 全量回归
```

铁律:1→5 顺序走;跨级修改 → 状态卡路由漂移 → stage-gate FAIL。

## §5 关联引用

[dependency-config.md](dependency-config.md) · [state-card-protocol.md](state-card-protocol.md) · [project-structure.md](project-structure.md) · [registry/README.md](../registry/README.md)