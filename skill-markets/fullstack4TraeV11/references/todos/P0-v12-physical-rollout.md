# P0-v12-physical-rollout(2026-08-16 用户复述 + 主上下文决策)

> **本条目来源**:用户 2026-08-16 反馈"多角色关注文档管理的就应该按 V12 物理隔离标准去实现"+ 主上下文核查 [v12-physical-isolation/migration-checklist.md](v12-physical-isolation/migration-checklist.md) §0 前置 5 项 + [V11.3-fact-stage-rationale.md](v12-physical-isolation/V11.3-fact-stage-rationale.md) §3 落地矩阵。
>
> **决策依据**:V12 是主版本升级([migration-checklist.md §0](v12-physical-isolation/migration-checklist.md) L8-18 5 项前置未达),但 V12 的"目录物理布局 + handoff-in/handoff-out 桥接"是**目录约定**——**V11 主版本内可渐进落地**。本条目即填补该真空。
>
> **本文件保留原因**:V11.8.6 全部 6 步落地后,保留作协议层引用与"已对齐 V12"的索引证据。

---

## P0-v12-rollout — V12 物理隔离思想在 V11 主版本内渐进落地(6 步)

```yaml
---
id: V12-ROLLOUT-6STEPS
title: V12 物理隔离思想在 V11 主版本内的渐进落地(不升主版本)
status: done(本会话 6 步全部落地 + 测试 7/7 PASS + hook PASS/FAIL 双态验证通过 + commit)
priority: P0
discovered_at: 2026-08-16
discovered_by: 用户复述"V12 fact/stage 物理隔离未完全落地" + 主上下文核查
protocol_ref: references/stage-physical-isolation.md §1 目录物理布局(273 行 V12 提案)
              v12-physical-isolation/migration-checklist.md §0 前置 + §1.1 目标 layout
              v12-physical-isolation/V11.3-fact-stage-rationale.md §3 落地矩阵
fix_path: 6 步渐进落地(V11 主版本内,不动 SKILL.md frontmatter version)
resolved_at: 2026-08-16T22:30(本会话)
resolved_by: 主上下文决策(用户授权 A 方案)
evidence:
  - templates/change-dir-layout-v12-preview.md — V12 物理布局模板(V11 可选,~120 行)
  - init-from-zero.py 新增 --layout v12-preview — Step 4.5 创建 fact/ + stage/ 骨架(11 stage 子目录 + 14 README)
  - references/sub-agent-rules.md §1.0 — 增"V11 项目可选按 V12 物理布局"指针(MUST + 2 NEVER)
  - skills/00-boot/agents/{jarvis,backend-implementer,frontend-implementer,test-expert}.md — 增 "fact/ + stage/{N}/" 产物落位说明(4 个 agents)
  - scripts/stage-gate.py — 新增 --reset-to 子命令(保留 fact/ + 清 stage/N+1/ 之后,不动 archive/)
  - templates/hooks/process-layer-guard.sh — 物理路径校验 hook(3 规则:根禁 .md / fact 禁 process 名 / stage 禁 fact 名;PASS/FAIL 双态验证通过)
  - tests/unit/test_stage_gate_reset.py — --reset-to 7 用例全 PASS(2026-08-16 19.24s)
  - CHANGELOG.md V11.8.6 条目 — 聚合以上 6 步(详细 + 兼容性保证)
  - 主上下文兜底验证(2026-08-16 22:30):
      * python -m pytest unit/test_stage_gate_reset.py unit/test_stage_gate_transition.py unit/test_commit_minimum_check.py unit/test_encoding_windows.py -v
        → 66/66 passed in 19.24s(0 回归)
      * bash skill-markets/fullstack4TraeV11/templates/hooks/process-layer-guard.sh
        → ✅ PASS(无 v12-preview 项目时跳过)
      * bash skill-markets/fullstack4TraeV11/templates/hooks/process-layer-guard.sh (v12-preview 项目 + 根目录违规 fix-bug-report.md)
        → ❌ FAIL exit 1,错误信息清晰
      * bash skill-markets/fullstack4TraeV11/templates/hooks/process-layer-guard.sh (v12-preview 项目,合规)
        → ✅ PASS exit 0
      * python scripts/commit-minimum-check.py --help
        → 含中文输出不崩(Windows PYTHONIOENCODING 兜底生效)
---
```

## §1 真空识别

按 [V11.3-fact-stage-rationale.md §3](v12-physical-isolation/V11.3-fact-stage-rationale.md) 落地矩阵:
- 🟢 README L160 物理隔离概念 / stage-physical-isolation.md(273 行)/ 子代理白名单实战段 / husky 式硬阻断 — **已落地**
- ❌ **fact/stage/ 目录物理分** — 未落地
- ❌ **每 stage 独立 .state-card.md** — 未落地
- ❌ **handoff-in/handoff-out 桥接** — 未落地
- ❌ **stage-gate.py --reset-to** — 未落地

按 [migration-checklist.md §0](v12-physical-isolation/migration-checklist.md) L8-18,V12 ADR 5 项前置均未达成 → **不能升 V12 主版本**。

**真空**:V11 主版本内多角色文档管理**无标准**——4 个角色(jarvis/backend-implementer/frontend-implementer/test-expert)产物落位混乱(`docs/specs/changes/{id}/` 扁平 layout,无 fact/process 物理隔离)。

---

## §2 6 步落地路径(V11 主版本内,不破坏 V11 归档)

### Step 1: V12 物理布局模板(V11 可选使用)

**新建**: `templates/change-dir-layout-v12-preview.md`(~80 行)

```
docs/specs/changes/{change-id}/
├── fact/                        # 事实唯一源(跨 stage 共享,V12 §1)
│   ├── .state-card.md           # 项目级 .state-card.md 副本(只读)
│   ├── spec.md                  # Layer 1: AC / INV / Edge Cases
│   ├── plan.md                  # Layer 2: Capabilities / Non-Goals
│   ├── test-plan.md
│   ├── prototype.md
│   └── contracts/{4 件套}      # domain-models / api-contracts / events / validation-rules
├── stage/                       # 流程文档(可重置,V12 §2)
│   ├── -1-intake/
│   │   ├── intake-notes.md      # 主代理本 stage 笔记
│   │   └── handoff-out.md       # ≤200 字交下一 stage
│   ├── 0-plan/...
│   ├── 0.5-test-plan/...
│   ├── 1-spec/...
│   ├── 1.5-prototype/...
│   ├── 2-contract/...
│   ├── 3-implement/...
│   ├── 3.5-real-verify/...
│   ├── 4-review/...
│   ├── 4.5-rot-scan/...
│   └── 5-accept/...
└── archive/                     # 5-accept 后写入(不可变)
```

### Step 2: `init-from-zero.py` 加 `--layout v12-preview`

**修改**: `scripts/init-from-zero.py` argparse 加 `--layout {v11-default|v12-preview}` 参数
- v11-default(默认)= V11 现有扁平 layout(行为不变)
- v12-preview= 创建上述 fact/ + stage/{11 个}/ 骨架(11 个 stage 子目录)

**触发位置**: Step4 文档系统骨架生成后追加 Step4.5

### Step 3: `sub-agent-rules.md` §1 加指针

**修改**: `references/sub-agent-rules.md` §1 文档分层(已含 fact/process/log 三层定义)末尾加:

```
MUST: V11 项目可选按 V12 物理布局(fact/ + stage/{N}/) 写产物 ——
     见 templates/change-dir-layout-v12-preview.md
NEVER: V11 项目初始化时默认按 v11-default 布局,后补 fact/ 目录(破坏既有归档)
正确替代: init-from-zero.py --layout v12-preview 一次性创建
```

### Step 4: 4 个角色 agent 文件加产物落位说明

**修改**: `skills/00-boot/agents/{jarvis,backend-implementer,frontend-implementer,test-expert}.md`
每个角色加**"产物落位规则"**章节:
- jarvis → 落 `fact/.state-card.md`(状态卡副本)+ `stage/{N}/.state-card.md`(每 stage 独立卡)
- backend-implementer → 落 `stage/3-implement/{impl-notes,handoff-out}.md`(不写 fact/ 防污染)
- frontend-implementer → 落 `stage/3-implement/{impl-notes,handoff-out}.md`(不写 fact/)
- test-expert → 落 `stage/3.5-real-verify/{verify-notes,handoff-out}.md` + `stage/4-review/{review-notes,handoff-out}.md`

### Step 5: `stage-gate.py` 加 `--reset-to` 子命令

**修改**: `scripts/stage-gate.py` 新增子命令 `reset-to`
```
python stage-gate.py --change {id} --reset-to stage/{N}
```
行为(借鉴 V12 §2.1):
1. 保留 `fact/` 整个目录(事实源)
2. 删除 `stage/{N+1}/` ~ `stage/5-accept/` 全部内容(流程文档可重置)
3. 保留 `stage/-1-intake/` ~ `stage/{N}/`(用户决策"保留"则跳过)
4. 重置当前 stage 状态卡 = {N}, stage_status=pending
5. 写入 reset_history 字段(沿用 V11 §7.4)

### Step 6: 新建 `templates/hooks/process-layer-guard.sh` 物理路径校验 hook

**新建**: `templates/hooks/process-layer-guard.sh`(~60 行 bash)

校验规则(任何 agent 写 `docs/specs/changes/{id}/` 时):
- ❌ **写 fact/ 时禁止文件名含 `notes`/`handoff`/`diagnosis`/`v[0-9]` 字样**(这些是 process 层命名)
- ❌ **写 stage/ 时禁止文件名含 `spec.md`/`plan.md`/`contracts/`**(这些是 fact 层命名)
- 路径必须在 `fact/` 或 `stage/{N}/` 之一,不得落在 `docs/specs/changes/{id}/` 根(防回到 V11 扁平)
- 退出码:0=PASS / 1=FAIL

---

## §3 落地原则(避免破坏 V11 主版本)

| 维度 | 约束 |
|------|------|
| **SKILL.md frontmatter version** | ❌ 不动(仍是 11.x,不升 12.0.0) |
| **既有 V11 项目** | 不强制迁移(v11-default 布局保持) |
| **既有 archive/done/** | 不动(Article VIII 不可变) |
| **新项目或新 change-id** | 可用 `--layout v12-preview`(主动对齐) |
| **V12 ADR 通过后** | 已用 `--layout v12-preview` 的项目 = 已就位,无迁移成本 |

---

## §4 反向提示词(蒸馏写入)

```yaml
NEVER: 假设 V12 物理布局 = V11 init 自动产出
触发条件: V11 项目 init-from-zero.py 完成后
错误代价: 多角色 agent 写产物时无标准 → fact/process 混置 → state-card 漂移
正确替代: init-from-zero.py --layout v12-preview 主动对齐 V12

NEVER: sub-agent 写 stage/{N}/{notes,handoff}.md 时落到 docs/specs/changes/{id}/ 根
触发条件: 任何 V11 项目阶段产物
错误代价: 回到 V11 扁平 layout,fact/process 物理隔离 0%
正确替代: 严格按 templates/change-dir-layout-v12-preview.md 落 fact/ + stage/{N}/

NEVER: stage-gate.py --reset-to 不留 fact/
触发条件: 用户命令"打回 stage{N}"
错误代价: 事实源丢失 → spec/plan/contracts 不可恢复
正确替代: --reset-to 默认保留 fact/,仅清 stage/{N+1}/ ~ stage/5-accept/(借鉴 V12 §2.1)
```

---

## §5 关联引用

- [references/stage-physical-isolation.md](../stage-physical-isolation.md) — V12 提案原文(273 行,§1 目录布局 + §3 子代理白名单 + §4 验收瘦身)
- [v12-physical-isolation/migration-checklist.md](v12-physical-isolation/migration-checklist.md) — V12 一次性迁移清单(本条目互补:本条目是 V11 渐进,v12-rolldown 是 V12 一次性)
- [v12-physical-isolation/V11.3-fact-stage-rationale.md](v12-physical-isolation/V11.3-fact-stage-rationale.md) — 思想起点 + 落地矩阵
- [skills/00-boot/agents/](../skills/00-boot/agents/) — 多角色协议(jarvis/backend-implementer/frontend-implementer/test-expert)
- [references/sub-agent-rules.md](../sub-agent-rules.md) — §1 fact/process/log 三层定义 + 本条目新增 V12 指针
- [scripts/stage-gate.py](../stage-gate.py) — 本条目新增 --reset-to 子命令
- [templates/change-dir-layout-v12-preview.md](../templates/change-dir-layout-v12-preview.md) — 本条目新增 V12 物理布局模板