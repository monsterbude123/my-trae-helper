# Change-Dir Layout V12 Preview — V12 物理布局模板(V11 主版本可选)

> **定位**:V12 物理隔离思想的 V11 主版本预览布局。V11 项目用 `init-from-zero.py --layout v12-preview` 一次性创建本骨架;V12 主版本 ADR 通过后本目录 = 标准 layout,无需迁移。
>
> **不破坏 V11 主版本**:不动 `SKILL.md frontmatter version`;既有 V11 项目不动;本文件作"项目级目录约定"使用。

---

## §0 物理布局(目标)

```
docs/specs/changes/{change-id}/
├── fact/                              # 事实唯一源(跨 stage 共享,V12 §1)
│   ├── .state-card.md                 # 项目级 .state-card.md 副本(只读)
│   ├── spec.md                        # Layer 1: AC / INV / Edge Cases
│   ├── plan.md                        # Layer 2: Capabilities / Non-Goals
│   ├── test-plan.md                   # Stage 0.5: 测试覆盖矩阵
│   ├── prototype.md                   # Stage 1.5: prototype 设计
│   └── contracts/                     # Layer 3: 契约 4 件套
│       ├── domain-models.md
│       ├── api-contracts.md
│       ├── events.md
│       └── validation-rules.md
├── stage/                             # 流程文档(可重置,V12 §2)
│   ├── -1-intake/
│   │   ├── intake-notes.md            # 主代理本 stage 笔记
│   │   └── handoff-out.md             # ≤200 字交下一 stage
│   ├── 0-plan/
│   │   ├── plan-notes.md
│   │   └── handoff-out.md
│   ├── 0.5-test-plan/
│   │   ├── test-plan-notes.md
│   │   └── handoff-out.md
│   ├── 1-spec/
│   │   ├── spec-notes.md
│   │   └── handoff-out.md
│   ├── 1.5-prototype/
│   │   ├── prototype-notes.md
│   │   └── handoff-out.md
│   ├── 2-contract/
│   │   ├── contract-notes.md
│   │   └── handoff-out.md
│   ├── 3-implement/
│   │   ├── impl-notes.md              # TDD 过程记录
│   │   ├── backend-impl-notes.md      # backend-implementer 产物
│   │   ├── frontend-impl-notes.md     # frontend-implementer 产物
│   │   └── handoff-out.md
│   ├── 3.5-real-verify/
│   │   ├── verify-notes.md
│   │   └── handoff-out.md
│   ├── 4-review/
│   │   ├── review-notes.md            # test-expert 4 维评分
│   │   └── handoff-out.md
│   ├── 4.5-rot-scan/
│   │   ├── rot-notes.md
│   │   └── handoff-out.md
│   └── 5-accept/
│       ├── accept-notes.md
│       └── handoff-out.md
└── archive/                           # 5-accept 后写入(不可变,Article VIII)
```

---

## §1 三层映射(对 V11 既有概念)

| V11 既有概念 | V12 物理布局落位 |
|--------------|-----------------|
| fact 层(spec/plan/contract) | `fact/`(不可重置) |
| process 层(diagnose/fix_result/v1v2v3) | `stage/{N}/{N}-notes.md`(可重置) |
| log 层(changelog/commit log) | `stage/{N}/{N}-notes.md` 或 `logs/`(gitignored) |

**核心原则**(V12 §0 设计哲学):
1. **物理隔离 > 逻辑分层** — 文档不是"标注为 process 层",而是直接放在 `stage/{N}/` 子目录
2. **事实唯一源** — `fact/` 不被 stage 重置影响(物理保护)
3. **子代理边界** — 每个 stage agent 只读自己 `stage/{N}/` + `fact/`,主上下文负责跨 stage 注入

---

## §2 路径白名单(防 process 写 fact / 防 fact 落 stage)

由 [templates/hooks/process-layer-guard.sh](../hooks/process-layer-guard.sh) 强制校验:

**fact/ 允许的文件**:
- `spec.md` / `plan.md` / `test-plan.md` / `prototype.md`(Layer 1/2 文档)
- `contracts/{4 件套}.md`(契约 4 件套)
- `.state-card.md`(项目级状态卡副本)

**fact/ 禁止的文件**:
- `*-notes.md`(process 层命名)
- `*handoff*.md`(桥接文档,属 process)
- `diagnosis-*.md` / `fix-*.md` / `v[0-9]*`(process 层命名约定)

**stage/{N}/ 允许的文件**:
- `{N}-notes.md`(本 stage 笔记)
- `*handoff-out.md`(桥接下 stage)
- 角色专属(Stage 3-implement): `backend-impl-notes.md` / `frontend-impl-notes.md`

**stage/{N}/ 禁止的文件**:
- `spec.md` / `plan.md` / `contracts/`(属 fact 层)
- 跨 stage 引用(只允许 `handoff-out.md`)

**docs/specs/changes/{id}/ 根目录**:
- ❌ 禁止任何 .md 文件(必须落 `fact/` 或 `stage/{N}/` 之一)

---

## §3 V11 → V12-preview 迁移路径

| 步骤 | 操作 |
|------|------|
| 1 | `init-from-zero.py --layout v12-preview --change {id}`(创建骨架) |
| 2 | 现有 `docs/specs/changes/{id}/.state-card.md` → 移到 `fact/.state-card.md`(硬链接,内容不变) |
| 3 | 现有 `spec.md` / `plan.md` / `test-plan.md` / `prototype.md` → 移到 `fact/` 对应文件名 |
| 4 | 现有 `contracts/` → 移到 `fact/contracts/` |
| 5 | 现有 `verify-report.md` / `review-report.md` / `rot-scan.md` → 移到对应 `stage/{N}/` 子目录 |
| 6 | 现有 `docs/specs/changes/{id}/archive/`(若存在)→ 保留原位 |

**严禁操作**:直接 `mv docs/specs/changes/{id}/*` 一次到位——必须按文件分类移动,且每步后跑 `process-layer-guard.sh` 验证。

---

## §4 何时用 v12-preview vs v11-default(V11.8.7.1 起 v11-default 已废弃)

> **V11.8.7.1 UPDATE**:`--layout` 仅 `v12-preview`,V11 既有项目用 `--migrate-from-v11` 升级。
> 旧 v11-default 表(临时修复 / 紧急 change)不再适用 — 所有项目强制 V12 物理布局。

**默认行为**:`init-from-zero.py` 不带 `--layout` 参数 = `v12-preview`(V11.8.7.1 起,旧 v11-default 已废弃)。

---

## §5 V12 ADR 通过后的状态

- v12-preview 项目 = 已对齐 V12 标准 layout,无需再迁移
- v11-default 项目 = 需跑 `upgrade-from-v11.py`(V12 升级脚本,V12 ADR 通过后新建)
- 本文件保留作 V11 主版本下"主动对齐 V12"的入口文档

---

## §6 关联引用

- [references/stage-physical-isolation.md](../references/stage-physical-isolation.md) — V12 提案原文(273 行)
- [references/todos/v12-physical-isolation/migration-checklist.md](../references/todos/v12-physical-isolation/migration-checklist.md) — V12 ADR 通过后的一次性迁移
- [references/todos/P0-v12-physical-rollout.md](../references/todos/P0-v12-physical-rollout.md) — 本布局的 todo 索引
- [templates/hooks/process-layer-guard.sh](../hooks/process-layer-guard.sh) — 物理路径校验 hook
- [scripts/stage-gate.py](../scripts/stage-gate.py) — `--reset-to` 子命令(保留 fact/,清 stage/N+1/)
- [skills/00-boot/agents/](../skills/00-boot/agents/) — 多角色产物落位说明