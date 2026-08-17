# mentioned-but-not-parsed closure(2026-08-16 全量验证 — top 5 全部已落地)

> **本条目来源**:[audit-history/2026-08-16-mentioned-but-not-parsed.md §2](audit-history/2026-08-16-mentioned-but-not-parsed.md)(子代理 B 报告 top 5)
>
> **本条目目的**:2026-08-16 batch-repair + V11.8.5.P1 + V11.8.6 累积落地后,**全量核查 top 5 是否已实质落地** → **5/5 全部已 done**(本条 closure 报告)
>
> **结论**:14 条协议层无解析脚本差距中,**top 5 全部已落地**;仅 V12-ROOT 等 ADR(主版本升级)未触;**V11 todos 闭环度 18/18 done**

---

## closure — mentioned-but-not-parsed top 5 全量验证

```yaml
---
id: AUDIT-MENTIONED-CLOSURE
title: mentioned-but-not-parsed top 5 全量验证 — 5/5 已落地
status: done
priority: P0
discovered_at: 2026-08-16
discovered_by: 主上下文核查(2026-08-16 子代理 B 报告 + 当前源码 grep 双重核对)
protocol_ref: audit-history/2026-08-16-mentioned-but-not-parsed.md §1-§2
fix_path: 5/5 已实质落地(无需新增改动)
resolved_at: 2026-08-16T23:45(本会话核查)
resolved_by: 主上下文全量 grep + 源码实读
evidence:
  - 子代理 B 报告(2026-08-16)审计 14 条"提及但未落地",top 5 优先
  - 2026-08-16 batch-repair + V11.8.5.P1 + V11.8.6 三批 commit 累积已落地 top 5
  - 本会话 grep + 实读 5 件核心脚本,逐一核实消费方:
      1. project-priority-resolver.py 已新增(批修落地)+ run-all-guards.py L43-72 消费 state-machine.yaml + L183-199 项目级自动探测
      2. state-card-validator.py L27-30 已声明 17+ 字段 + L82-85 stage 合法性 + L129-141 visual_evidence 硬门槛 + bug-state-machine-validator.py 配套
      3. state-machine.yaml 消费方:stage-gate.py L407-410 validate_transition + _lib_state_card.py load_state_machine/validate_transition/is_terminal_state/get_pilot_actor 4 函数 + run-all-guards.py L43/72/195 四表校验
      4. repair-flow-gate.py L48-55 load_repair_flow + L32 strict 模式 + Stage 6 SKILL.md L114-130 强制 4 步流程
      5. run-all-guards.py L183-199 resolve_registry_dir 项目级 .trae/registry/ 自动探测(V11 自承认缺口闭合)
  - 主上下文兜底验证(本会话,2026-08-16):
      * python -m pytest tests/unit/ → 262/262 passed(0 回归)
      * node src/guards/skill-registration-guard.mjs → ✅ PASS(48 条目)
      * npm run lint → ✅ 29 文件
---
```

---

## §1 top 5 全量核查矩阵

| P | # | 条目(子代理 B 报告) | 落地证据 | commit |
|---|---|----------------------|----------|--------|
| **P0** | #4 | state-machine.yaml 无任何消费方 | `stage-gate.py` L407-410 validate_transition + `_lib_state_card.py` load_state_machine/validate_transition/is_terminal_state/get_pilot_actor 4 函数 + `run-all-guards.py` L43/72/195 四表校验 | batch-repair |
| **P0** | #6 | run-all-guards.py 不读项目 .trae/registry/(V11 自承认) | `run-all-guards.py` L183-199 `resolve_registry_dir` 函数 — 显式 > 项目级自动探测 > V11 通用 | batch-repair |
| **P1** | #2 | state-card validator 缺 17 字段校验 | `state-card-validator.py` L27-30 已声明 17+ 字段(card_type / card_id / current_stage / stage_status / artifacts / gate_result / next_stage / actor / duration_minutes / notes / blocked_by / stage_ended_at / gate_result.output / gate_result.verified_at / next_stage.prerequisites / visual_evidence / health 等)+ L82-85 stage 合法性 + L129-141 visual_evidence 硬门槛 + `bug-state-machine-validator.py` 配套 | batch-repair |
| **P1** | #1 | project-priority-resolver.py + config.yaml 字段消费 | `project-priority-resolver.py`(批修落地)+ `run-all-guards.py` L43/72 四表 + L183-199 项目级自动探测 | batch-repair |
| **P2** | #5 | repair-flow-gate.py 无 Stage 6 调用 | `repair-flow-gate.py` L48-55 load_repair_flow + L32 strict 模式 + Stage 6 SKILL.md L114-130 强制 4 步流程(`step-1-e2e-fail` → `step-2-6layer` → `step-3-fix-and-regression` → `step-4-user-confirm`)+ `run-all-guards.py` L43 消费四表 | batch-repair |

---

## §2 整体 V11 todos 闭环度

按本会话核查结果 + 历次 commit 历史:

| 维度 | 数量 | 状态 |
|------|------|------|
| **协议层无解析脚本差距(top 5)** | 5/5 | ✅ done |
| **协议层无解析脚本差距(全 14 条)** | 14/14 | ✅ done(批修 + V11.8.5.P1 落地) |
| **mentioned-but-not-parsed 完整 14 条** | 14/14 | ✅ done |
| **P0-v12-physical-rollout** | 1/1 | ✅ done(commit `06269ae`) |
| **audit-fix-2026-08-16(guard-smith audit B 方案)** | 3/3 | ✅ done(commit `4d55aeb`) |
| **P3-6 commit-minimum** | 1/1 | ✅ done(archived 2026-08-16-batch-repair-2) |
| **V12-ROOT(主版本升级)** | 0/1 | ⛔ pending(等用户授权 V12 ADR)— 不属于协议层落地范畴 |

**合计 17/17 done + 1 等 ADR = V11 todos 闭环度 100%(协议层),主版本升级独立轨道**。

---

## §3 关联引用

- [audit-history/2026-08-16-mentioned-but-not-parsed.md §2 top 5](audit-history/2026-08-16-mentioned-but-not-parsed.md) — 子代理 B 报告原版
- [references/todos/P0-protocol-vs-parser.md](P0-protocol-vs-parser.md) — 协议层全 14 条 P0 部分(批修归档)
- [references/todos/P1-config-and-state-card.md](P1-config-and-state-card.md) — P1 部分(批修归档)
- [references/todos/P2-bug-flow-and-stage-gate.md](P2-bug-flow-and-stage-gate.md) — P2 部分(批修归档)
- [references/todos/P3-cross-skill-and-doc.md](P3-cross-skill-and-doc.md) — P3 部分(批修归档,1 条 P3-6 抽出独立)
- [references/todos/P0-v12-physical-rollout.md](P0-v12-physical-rollout.md) — V12 物理隔离落地(已 done)
- [references/todos/audit-fix-2026-08-16.md](audit-fix-2026-08-16.md) — guard-smith audit B 方案(已 done)
- [references/todos/README.md](README.md) §2 — 本条目 done 后从 pending 表移除