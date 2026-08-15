# 项目目录结构（V11 强制 — 蒸馏自 V10）

> **V11.7.0+ 设计入口**: [AC 核销门禁](../skills/09-review/SKILL.md) · [贾维斯门禁守护](../skills/00-boot/SKILL.md) · 评分制废除 → 门禁制 · 详见 [CHANGELOG.md V11.7.0](../CHANGELOG.md)


> 主上下文加载 skill 后必查：项目实际目录 vs V11 默认 vs 蒸馏需求。
> 来源：V10 `references/project-structure.md`（V10 实战反馈：项目目录不一致导致子代理找不到 artifacts）。

---

## V11 标准目录布局

```
project/
├── AGENTS.md                              # 项目级 AI 规则（agent 读 template 按项目实际生成）
├── .trae/
│   ├── fullstack4traev11.config.yaml     # 项目级 stage_config 覆盖
│   ├── state-card.md                     # V11 项目级状态卡已迁移到 docs/specs/.state-card.md(此位置不再使用)
│   ├── hooks/                            # V11 13 hooks（详见 templates/hooks/）
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
│   ├── specs/                            # ★ Spec 真相源
│   │   ├── .state-card.md                #   Spec 状态卡（单源）
│   │   ├── INDEX.md                      #   Spec 索引（agent 发现入口）
│   │   ├── changes/                      #   进行中的 changes
│   │   │   └── {change-id}/              #     每个 change 一个目录
│   │   │       ├── spec.md               #       Spec（Delta 或完整）
│   │   │       ├── plan.md               #       计划
│   │   │       ├── test-plan.md          #       测试计划
│   │   │       ├── prototypes/           #       UI 原型（涉及 UI 时）
│   │   │       │   ├── design-prompt.md
│   │   │       │   └── ui-ux-logic.md
│   │   │       ├── contracts/            #       Feature 级契约
│   │   │       │   ├── api-contracts.md
│   │   │       │   ├── domain-models.md
│   │   │       │   ├── events.md
│   │   │       │   └── validation-rules.md
│   │   │       └── .state-card.md        #       Change 级状态卡（V11 命名）
│   │   └── archive/                      #   只读归档（Article VIII 不可变）
│   │       ├── done/
│   │       │   └── {archived-change-id}/ #     已完成的 change
│   │       └── out/
│   │           └── spec-purge/           #     V10 spec-purge 历史（V11 兼容）
│   ├── modules/                          # 模块文档（DOC SYNC 写入）
│   │   └── {module-name}.md
│   ├── reports/                          # 审查/验收报告历史（log 层）
│   ├── verifications/                    # ★ V10 视觉证据目录
│   │   └── web/tauri/cli/library/backend
│   └── bugs/                             # Bug 单（仅 bug 单 CLOSED 后归档）
│       └── {bug-id}.md
├── tests/
│   ├── unit/                             # 单元测试
│   ├── integration/                      # 集成测试
│   ├── e2e/                              # E2E 测试
│   └── contracts/                        # 契约测试（V11 Stage 2）
├── src/                                  # 源代码（按语言约定）
├── secrets/                              # forbidden_paths（Article XVII）
├── deploy/                               # forbidden_paths（部署配置）
└── archive/                              # forbidden_paths（项目级归档）
```

---

## 主上下文必查（V11 §0.5）

```
□ docs/specs/ 存在？（必）
  ├─ 不存在 → 询问用户"项目惯例 vs V11 默认"
  └─ 存在 → Glob 检查 spec.md 格式 vs V11 spec-template
□ docs/specs/changes/ 存在？（必 — V11 用 changes/ 子目录，非 V10 的 {feature}/）
  ├─ 不存在 → 用 V11 setup-feature.py 创建
  └─ 存在 → 检查每个 change 目录结构
□ docs/specs/archive/ 存在？（必 — 归档不可变）
  ├─ 不存在 → Stage 5 Accept 前必建
  └─ 存在 → 检查 done/ 与 out/spec-purge/
□ tests/contracts/ 存在？（必 — V11 Stage 2 契约测试）
□ .trae/hooks/ 存在？（必 — V11 13 hooks）
  └─ 不全 → 运行 install-hooks.py --force
□ docs/specs/.state-card.md 存在？（必 — V11 项目级状态卡，V11 路径重构已迁移出 .trae/）
```

---

## 与 V10 的关键差异

| 维度 | V10 | V11 |
|------|-----|-----|
| Spec 路径 | `docs/specs/{feature}/` | `docs/specs/changes/{change-id}/` |
| 状态卡路径 | `docs/specs/.state-card.md` | `docs/specs/.state-card.md`(项目级)+ `docs/specs/changes/{id}/.state-card.md`(change 级)|
| 归档路径 | `docs/archive/done/{feature}/` | `docs/archive/done/{change-id}/` |
| prototype 文档 | design-prompt.md + ui-ux-logic.md（V10 双源）| 同 V10（已蒸馏）|
| 契约目录 | `docs/specs/{feature}/contracts/` | `docs/specs/changes/{change-id}/contracts/` + `tests/contracts/` |

---

## 关联引用

- [SKILL.md §0.5 加载协议](../SKILL.md) — 主上下文必查
- [stage-card-protocol.md](stage-card-protocol.md) — 状态卡 schema
- [stage-interaction-protocol.md](stage-interaction-protocol.md) — 阶段产物路径
- V10 来源（开发期，已蒸馏）：见 V11 references 与 anti-patterns
