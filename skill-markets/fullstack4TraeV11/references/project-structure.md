# 项目目录结构（V12.0.0 主版本升级强制 — 蒸馏自 V10 + V11 物理隔离落地）

> **V12.0.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V12.0.0](../CHANGELOG.md)


> 主上下文加载 skill 后必查：项目实际目录 vs V12 默认 vs 蒸馏需求。
> 来源：V10 `references/project-structure.md`（V10 实战反馈：项目目录不一致导致子代理找不到 artifacts）+ V11 物理隔离落地 → V12 强制默认。

---

## V12 标准目录布局（V12.0.0 主版本升级强制）

```
project/
├── AGENTS.md                              # 项目级 AI 规则（agent 读 template 按项目实际生成）
├── .trae/
│   ├── fullstack4traev11.config.yaml     # 项目级 stage_config 覆盖
│   ├── hooks/                            # V12 13 hooks（详见 templates/hooks/）
│   │   ├── pre-stage.sh / post-stage.sh / pre-accept.sh
│   │   ├── gitnexus-session-{check,finalize}.py
│   │   ├── session-start.py / complexity-guard.py
│   │   ├── doc-sync-gate.py / contract-gate.py
│   │   ├── spec-validate-hook.py / auto-test.py / drift-detect.py
│   │   └── tasks-integrity.py
│   ├── hooks.json                        # TRAE IDE event 注册（fullstack-hooks.json）
│   └── rules/                            # 项目级 rules（agent 读 template 按需配置）
│       ├── stack.md / paths.md / git.md
├── docs/
│   ├── specs/                            # ★ Spec 真相源（V12 物理布局）
│   │   ├── INDEX.md                      #   Spec 索引（agent 发现入口）
│   │   └── changes/                      #   进行中的 changes
│   │       ├── _module.md                #     项目级模块真相源(V12 强制默认)
│   │       └── {change-id}/              #     每个 change 一个目录(V12 物理布局)
│   │           ├── fact/                 #       4 层文档真相源(V12 强制)
│   │           │   ├── spec.md           #         AC / INV / Edge Cases
│   │           │   ├── plan.md           #         Capabilities / Non-Goals
│   │           │   ├── test-plan.md      #         测试计划
│   │           │   ├── prototype.md      #         Stage 1.5 原型产物(可选)
│   │           │   ├── contracts/        #         4 件套契约
│   │           │   │   ├── api-contracts.md
│   │           │   │   ├── domain-models.md
│   │           │   │   ├── events.md
│   │           │   │   └── validation-rules.md
│   │           │   └── .state-card.md    #         Change 级状态卡副本(只读)
│   │           ├── stage/                #       13 stage 流程产物(V12 强制)
│   │           │   ├── -1/intake/{intake-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 0/plan/{plan-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 0.5/test-plan/{test-plan-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 1/spec/{spec-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 1.5/prototype/{prototype-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 2/contract/{contract-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 3/implement/{impl-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 3.5/real-verify/{verify-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 4/review/{review-notes,handoff-out}.md + .state-card.md
│   │           │   ├── 4.5/rot-scan/{rot-notes,handoff-out}.md + .state-card.md
│   │           │   └── 5/accept/{accept-notes,handoff-out}.md + .state-card.md
│   │           └── archive/              #       Stage 5 完成后写入(V12 不可变,保留物理布局)
│   └── archive/                          # 只读归档（Article VIII 不可变）
│       └── done/
│           └── {archived-change-id}/     #   已完成的 change (V12 保留物理布局)
├── tests/
│   ├── unit/                             # 单元测试
│   ├── integration/                      # 集成测试
│   ├── e2e/                              # E2E 测试
│   └── contracts/                        # 契约测试（V12 Stage 2）
├── src/                                  # 源代码（按语言约定）
├── secrets/                              # forbidden_paths（Article XVII）
├── deploy/                               # forbidden_paths（部署配置）
└── archive/                              # forbidden_paths（项目级归档）
```

---

### §C V11 兼容段(已废弃,V11.8.7.1 起永久废弃)

V11 扁平布局(`docs/specs/changes/{id}/spec.md` 等文件直接平铺)永久废弃。所有项目必须 V12 物理布局 `fact/` + `stage/{N}/` 强制默认。

既有 V11 项目迁移走 `--migrate-from-v11` 主路径,8 步原子迁移(详见 [V12-MIGRATION-PROTOCOL.md](../todos/v12-physical-isolation/V12-MIGRATION-PROTOCOL.md))。

---

## 主上下文必查（V12 §0.5）

```
□ docs/specs/ 存在？（必）
  ├─ 不存在 → 询问用户"项目惯例 vs V12 默认"
  └─ 存在 → Glob 检查 spec.md 格式 vs V12 spec-template
□ docs/specs/changes/ 存在？（必 — V12 用 changes/ 子目录，非 V10 的 {feature}/）
  ├─ 不存在 → 用 V12 setup-feature.py 创建
  └─ 存在 → 检查每个 change 目录结构(V12 物理布局 fact/ + stage/{N}/)
□ docs/archive/done/ 存在？（必 — 归档不可变,Article VIII）
  ├─ 路径由 `_lib_paths.get_archive_dir(project_root)` 解析（默认 `docs/archive/done`，可在 `.trae/fullstack4traev11.config.yaml` 的 `paths.archive` 覆盖）
  ├─ 不存在 → Stage 5 Accept 前必建（spec-purge.py 自动创建）
  └─ 存在 → 检查 done/ 子目录（V12 spec-purge.py 写入路径,V12 保留物理布局）

□ docs/specs/changes/_module.md 存在？(必 — 项目级模块真相源,V12.0.0 强制默认;由 init-from-zero.py Step 4.6 创建)
  ├─ 路径由 init-from-zero.py::create_project_module() 写入(默认 `docs/specs/changes/_module.md`)
  ├─ 是 V12 项目级结构骨架(项目级真相源),spec-purge.py 复制注入到 `archive/{id}/_module.md`
  ├─ **V11.8.7.1 REMOVED**:`docs/specs/changes/archive/` 占位目录已废弃,真相源 = `docs/archive/done/`
  └─ 重命名/删除需同步改 `_lib_paths` defaults

□ docs/specs/changes/{id}/fact/ + stage/{N}/ 存在？(必 — V12 物理布局)
  ├─ 不存在 → V12 项目必跑 `init-from-zero.py --layout v12-preview` 创建骨架
  └─ 存在 → 检查每个 stage 子目录 + .state-card.md 完整性

□ docs/modules/ **不存在**？(必 — V11.8.7.1 REMOVED,V10 蒸馏残留,见 V11-AP17)
  ├─ V10 `stage-2-doc-sync` 期望产物,但 V12 13 stage 流程无对应 stage 写入
  ├─ V12 模块真相源 = `docs/specs/changes/_module.md`(项目级) + `docs/specs/changes/{id}/fact/module.md`(change 级)
  ├─ 若 init 残留此目录,删 `docs/modules/.gitkeep` 即可
  └─ `templates/hooks/doc-sync-gate.py` 已移除该目录 BLOCK 检查(原 V10 残留会死锁)
□ tests/contracts/ 存在？（必 — V12 Stage 2 契约测试）
□ .trae/hooks/ 存在？（必 — V12 13 hooks）
  └─ 不全 → 运行 install-hooks.py --force
□ fact/.state-card.md 存在？（必 — V12 项目级状态卡）
```

---

## 与 V10 的关键差异

| 维度 | V10 | V12 |
|------|-----|-----|
| Spec 路径 | `docs/specs/{feature}/` | `docs/specs/changes/{change-id}/fact/spec.md` |
| 状态卡路径 | `docs/specs/.state-card.md` | V12 多卡：`fact/.state-card.md`(项目级) + `stage/{N}/.state-card.md`(13 stage 独立卡) |
| 归档路径 | `docs/archive/done/{feature}/` | `docs/archive/done/{change-id}/`(由 `.trae/fullstack4traev11.config.yaml` `paths.archive` 配置;默认 `docs/archive/done`,见 [config.example.yaml](./config.example.yaml)) + V12 保留物理布局 |
| prototype 文档 | design-prompt.md + ui-ux-logic.md（V10 双源）| V12: `stage/1.5/prototype/{prototype-notes,handoff-out}.md` |
| 契约目录 | `docs/specs/{feature}/contracts/` | V12: `docs/specs/changes/{change-id}/fact/contracts/` + `tests/contracts/` |
| V11 扁平布局 | 不存在 | **永久废弃**（V11.8.7.1 起） |

---

## 关联引用

- [SKILL.md §0.5 加载协议](../SKILL.md) — 主上下文必查
- [state-card-protocol.md](state-card-protocol.md) — V12 多卡状态卡协议
- [stage-interaction-protocol.md](stage-interaction-protocol.md) — V12 阶段产物路径
- V10 来源（开发期，已蒸馏）：见 V12 references 与 anti-patterns