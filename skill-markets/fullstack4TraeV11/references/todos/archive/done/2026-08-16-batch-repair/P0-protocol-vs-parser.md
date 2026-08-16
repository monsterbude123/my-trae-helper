# P0 — 协议层 vs 解析层核心承诺未落地

> 状态:P0 = 协议层核心承诺无解析脚本。本文件 2 条。

---

## P0-1 — `run-all-guards.py` 不读项目级 `.trae/registry/`

```yaml
---
id: AUDIT-#6
title: run-all-guards.py 需自动探测项目级 registry
status: done
priority: P0
discovered_at: 2026-08-16
discovered_by: 子代理 B(general_purpose_task)
protocol_ref: references/dependency-config.md L19-25(Layer 3 项目级 > V11 通用)
              skills/12-bug-fix/references/bug-hunt-battle-report.md §9.5 缺漏 5(V11 自承认)
parser_ref: scripts/run-all-guards.py L139-150(--registry-dir 默认 None → skill_root/registry,fallback V11 通用层而非项目)
fix_path: scripts/run-all-guards.py L138-152 加 .trae/registry/ 自动探测 + 优先用项目层
completed_at: 2026-08-16T
evidence: 子代理 [TODO-REPAIR] 完成 — scripts/run-all-guards.py L138-185 新增 resolve_registry_dir() + main() 集成;主上下文兜底验证 /tmp/test_v11_realidr/.trae/registry/{4 yaml} 真实触发 auto-detected 输出('[v11-gate] auto-detected project registry: .trae\registry');tests/unit/test_runall_registry_autodetect.py 4 用例全 PASS
---
```

### 背景

V11 §14.5 + [references/dependency-config.md](references/dependency-config.md) §Layer 3 明确写"项目级 > V11 通用层"。但 `run-all-guards.py` 加载 5 表时,默认 `--registry-dir` 是 V11 通用 `registry/`,项目级 `.trae/registry/*.yaml` 必须手动 `--registry-dir .trae/registry` 才能用。

V11 自承认见 `bug-hunt-battle-report.md` §9.5 — 列为缺漏 5。

### 协议层证据

`references/dependency-config.md` L19-25:
> Layer 3 项目级覆盖 > Layer 1 全局 > Layer 2 V11 内置

`bug-hunt-battle-report.md` §9.5:
> run-all-guards.py --project-root . 读 V11 通用 registry/,不看项目 .trae/registry/

### 解析层证据

`scripts/run-all-guards.py` L139-150:
```python
parser.add_argument("--registry-dir", default=None, ...)
registry_dir = pathlib.Path(args.registry_dir) if args.registry_dir else skill_root / "registry"
```
无自动探测逻辑。

### 影响范围

- 实际跑 vvicat 项目的 `run-all-guards.py` 必须每次带 `--registry-dir .trae/registry`
- 项目级 `gates.yaml` (如 `.trae/registry/gates.yaml` 含 13 stage 项目路径)被静默 fallback 到 V11 通用层时,所需 artifact 文件找不到 → 13 stage 全 FAIL 的假阳性
- 影响所有 CI / GitHub Actions 上跑该项目 `run-all-guards.py` 的流水线

### 建议路径

`scripts/run-all-guards.py` L138 之前插入:

```python
# 自动探测:项目根存在 .trae/registry/{4 个 yaml} → 优先用
project_registry = pathlib.Path(args.project_root or ".") / ".trae" / "registry"
if not args.registry_dir and project_registry.exists():
    required = ["gates.yaml", "guards.yaml", "state-machine.yaml", "repair-flow.yaml"]
    if all((project_registry / r).exists() for r in required):
        registry_dir = project_registry
        print(f"[v11-gate] auto-detected project registry: {registry_dir}", file=sys.stderr)
```

修完后跑:

```bash
# 真反例
mkdir /tmp/test_proj && cd /tmp/test_proj && python ~/.../run-all-guards.py --project-root .  # 无 .trae/registry → 用 V11 通用
mkdir /tmp/test_proj/.trae/registry && cp registry/*.yaml /tmp/test_proj/.trae/registry/  # 项目级被自动探测 → 用项目
```

---

## P0-2 — `state-machine.yaml` 13 states + 14 transitions 无任何消费方

```yaml
---
id: AUDIT-#4
title: state-machine.yaml 必须被 stage-gate.py 消费(validate_transition)
status: done
priority: P0
discovered_at: 2026-08-16
discovered_by: 子代理 B
protocol_ref: registry/state-machine.yaml L73-124(13 states + 14 transitions + pilot)
              references/state-card-protocol.md L562-569 §九(状态转换必须通过 validate_transition)
parser_ref: scripts/_lib_state_card.py L144-203(load_state_machine / validate_transition 等函数已定义,但 scripts/ 内 grep 调用者零命中)
fix_path: scripts/stage-gate.py 主入口加 validate_transition(current_stage → next_stage) FAIL=exit 1
completed_at: 2026-08-16T
evidence: 子代理 [TODO-REPAIR] 完成 — scripts/stage-gate.py L213-237 argparse 加 --next-stage/--registry-dir/--project-root;L243-285 transition_check 调 validate_transition() FAIL→exit 2;L31-35 VALID_STAGES 修正为 7/health 与 registry 一致;tests/unit/test_stage_gate_transition.py 40 用例全 PASS(16 合法 + 10 非法 + 10 bug-fix 支线 + 4 自动探测)
---
```

### 背景

V11 的 13 stage 状态机本体是 `registry/state-machine.yaml`,但 `_lib_state_card.py` 已写 `validate_transition()` 函数定义,**仅文本级示例** 出现,scripts/ 中无任何调用方。`run-all-guards.py` L166-167 只校验 YAML 结构合法,完全不消费 transitions 内容。

### 协议层证据

`registry/state-machine.yaml` L73-124:定义 13 states + 14 transitions + pilot。

`references/state-card-protocol.md` L562-569 §九:
> 状态转换必须通过 validate_transition() 校验

### 解析层证据

```bash
$ grep -rn "load_state_machine\|validate_transition\|is_terminal_state" scripts/
scripts/_lib_state_card.py:144-203   # 仅定义点
scripts/README.md:79-82              # README 文本示例
# 零调用方
```

### 影响范围

- Stage 切换前没有机械校验"X → Y"转换是否合法(例:`-1/intake → 4/review` 非法跳跃无人拦截)
- 13 stage 流转承诺 = 文本级协议,无脚本兜底
- 状态卡层面"说当前 stage 是 X"完全靠 agent 自觉

### 建议路径

`scripts/stage-gate.py` L238 `validate_state_card()` 之后插入 `validate_transition()` 调用,需要 `--next-stage` 参数。然后在 `.trae/hooks/pre-stage.sh` 加 `stage-gate.py --state-card X --next-stage Y` 强校验。

**反例真跑**:`stage-gate.py --state-card <valid 5/accept> --next-stage 0/plan` 必须 exit 1。

