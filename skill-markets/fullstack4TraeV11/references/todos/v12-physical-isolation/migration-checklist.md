# V11 default layout → V12 fact/stage/ 子目录迁移检查清单

> **定位**:V12 ADR 一旦授权,从 V11 默认扁平 layout 迁移到 V12 物理隔离 layout 的具体步骤。
> **当前状态**:V12 提案未升主版本,本文件**仅作迁移骨架**,不执行任何迁移。

---

## §0 触发的"V12 ADR 决议"前置

| # | 前置检查 | 通过判定 |
|---|---------|---------|
| 0.1 | 用户明确表态"同意 V12 ADR 升级" | 用户消息确认 |
| 0.2 | §B L1 决策层级:release-manager / project-owner 至少 1 人批准 | git 评审 PASS |
| 0.3 | 当前 CHANGELOG.md 增"V12.0.0"主版本条目 | commit hash |
| 0.4 | `references/stage-physical-isolation.md` 当前是 v1.0.0 V12 提案,需更新为 v12.0.0 已 ADR 状态 | commit hash |
| 0.5 | 项目方已迁移完毕 + 不破坏旧 4 个归档 | `[5 已归档 change]` 状态卡 = archived |

未通过 0.1-0.5 任一项 → **不得执行以下任何步骤**。

---

## §1 项目重组步骤(从 V11 → V12 物理布局)

### 1.1 项目根(每个 change 目录都做这个模板)

迁移前:
```
docs/specs/changes/{change-id}/
├── .state-card.md
├── plan.md
├── spec.md
├── test-plan.md
├── prototype.md
├── contracts/{4 件套}
├── verify-report.md
├── review-report.md
└── rot-scan-{date}.md
```

迁移后:
```
docs/specs/changes/{change-id}/
├── fact/                           # 物理移入
│   ├── .state-card.md              # 项目级 .state-card.md → fact/.state-card.md 副本(只读)
│   ├── spec.md
│   ├── plan.md
│   ├── test-plan.md
│   ├── prototype.md
│   └── contracts/{4 件套}
├── stage/                          # 物理新建 + 文件按 stage 重写
│   ├── -1-intake/{intake-notes,handoff-out}.md
│   ├── 0-plan/{plan-notes,handoff-out}.md
│   ├── 0.5-test-plan/{test-plan-notes,handoff-out}.md
│   ├── 1-spec/{spec-notes,handoff-out}.md
│   ├── 1.5-prototype/{prototype-notes,handoff-out}.md
│   ├── 2-contract/{contract-notes,handoff-out}.md
│   ├── 3-implement/{impl-notes,handoff-out}.md
│   ├── 3.5-real-verify/{verify-notes,handoff-out}.md
│   ├── 4-review/{review-notes,handoff-out}.md
│   ├── 4.5-rot-scan/{rot-notes,handoff-out}.md
│   └── 5-accept/{accept-notes,handoff-out}.md
└── archive/                        # 5-accept 完成后写入
```

### 1.2 docs/specs/.state-card.md 迁移到 fact/.state-card.md

主上下文持的项目级 .state-card.md 也迁到 `docs/specs/.state-card.md` → 副本到 `fact/.state-card.md`。

> **不要直接 mv**:`init-from-zero.py --upgrade-from-v11` 应该做。手动 mv 会破坏与 docs 子仓 link。

### 1.3 docs/bugs/{bug-id}/ 同步重组

```
docs/bugs/{bug-id}/
├── .state-card.md                   # 主卡
├── fact/                            # 事实唯一源
│   ├── symptom.md
│   ├── reproduce.md
│   └── root-cause.md
├── stage/                           # stage by stage
│   ├── {entry}/{notes}.md
│   ├── {4-layer-diagnosis}/notes.md
│   ├── {fix-applied}/notes.md
│   ├── {verify-passed}/notes.md
│   └── {closed}/notes.md
└── archive/
```

### 1.4 docs/evidence/ 与 docs/sessions/ 保留

这两个目录不属于 change 级,不迁移。

---

## §2 主上下文 + 子代理协议改造

### 2.1 子代理白名单(每 stage agent 启动时只读白名单)

按 [stage-physical-isolation.md §3 L100-128](../stage-physical-isolation.md) 子代理白名单:

| Stage | 白名单 | 黑名单 |
|---|---|---|
| -1 Intake | `fact/spec.md`(如存在)+ AGENTS.md + rules/ | 其他 stage/ 全禁 |
| 0 Plan | `fact/spec.md + stage/-1-intake/handoff-out.md + 同 stage` | 其他 stage |
| 0.5 Test Plan | `fact/spec.md + fact/plan.md + stage/0-plan/handoff-out.md` | 其他 stage |
| 1 Spec | `fact/plan.md + stage/0.5-test-plan/handoff-out.md` | 其他 stage |
| 1.5 Prototype | `fact/spec.md + stage/1-spec/handoff-out.md` | 其他 stage |
| 2 Contract | `fact/spec.md + stage/1-spec/handoff-out.md` | 其他 stage |
| 3 Implement | `fact/contracts/ + stage/2-contract/handoff-out.md` | 其他 stage |
| 3.5 Real Verify | `fact/contracts/ + stage/3-implement/handoff-out.md + code/` | 其他 stage |
| **4 Review** | **fact/spec.md AC + 截图 + 视频** | **stage/3-implement/* 代码细节** |
| 4.5 Rot Scan | `fact/ + 全 stage/(只读诊断)` | archive/(写) |
| 5 Accept | `fact/ + stage/4.5-rot-scan/handoff-out.md` | archive/(写) |

### 2.2 主上下文跨 stage 信息桥接

每 stage agent 完成后,主上下文读 `stage/N/handoff-out.md`(≤200 字) + `stage/N/notes.md`(主上下文化笔记),提纯跨 stage 摘要,写入 `stage/N+1/handoff-in.md`。

---

## §3 阶段门禁硬化

### 3.1 `scripts/stage-gate.py` 加 `--reset-to`

```bash
python stage-gate.py --change {id} --reset-to stage/3-implement
# V12 强制:保留 fact/,删除 stage/3-implement/ ~ stage/5-accept/,重置状态卡 stage_status=pending
```

### 3.2 `templates/hooks/pre-stage.sh` 加 stage-gate.py 必跑

```bash
python stage-gate.py \
    --state-card "$STATE_CARD" \
    --next-stage "$EXPECTED_NEXT_STAGE" \
    --check-transition || { echo "🛑 阶段转换非法"; exit 1; }
```

### 3.3 验收 stage 4 瘦身

Stage 4 Review 只做 4 件事:[stage-physical-isolation.md §4 L131-147](../stage-physical-isolation.md):
1. 读 `fact/spec.md` AC 清单
2. 看 prototype 截图(如 prototype)
3. 看 real-verify 截图/视频
4. 对比 AC vs 实际功能

**不做**:读代码细节、评判代码风格、重构建议、性能优化建议。

---

## §4 反例(V12 蒸馏自 canvas-asset-folders)

[stage-physical-isolation.md §6 L193-233](../stage-physical-isolation.md) 给出 5 类反例:

| # | 现象 | 后果 | 纠正 |
|---|------|------|------|
| 1 | sub-agent 读过白名单外文件 | 上下文膨胀 + 决策被旧报告污染 | 委派 doc_whitelist 严格边界 |
| 2 | 验收 stage 评判代码细节 | review 时间膨胀 + 职责重叠 | Stage 4 铁律 = 不读代码 |
| 3 | 状态卡膨胀未隔离 | 主上下文每次切 stage 读全卡 | 每 stage 独立 .state-card.md |
| 4 | 阶段门禁放水 | 实施未过 TDD 就入验证 | stage-gate.py --check 强门禁 |
| 5 | 重置时误删 fact 层 | 事实源丢失 | --reset-to 默认保留 fact/ |

---

## §5 数据迁移防丢 checklist

迁移过程中 4 个防丢事项:

1. `mv` 后立即读 fact/ 文件内容对比 — 不能少字节
2. 子代理 handoff-out.md 全部从 0-plan 开始重建(原文件不一定每个 stage 都有)
3. docs 子仓 commit 必须每目录 1 commit,不能合并
4. 主仓 `.git/info/exclude` 屏蔽 docs/ 不变 — docs 子仓独立跟踪

---

## §6 不迁移标志

以下情况**严禁做 V12 迁移**:

| 情况 | 不迁移原因 |
|------|----------|
| 项目处于 Stage 3.5 进行中(verify-report 未完) | 物理重置会中断 in-progress stage |
| 已有的 archive/done/{id}/ 已含当前 change 内容 | archive 不可修改(Article VIII) |
| 项目正在 GitNexus 索引跑分析 | 物理移动会让 index 陈旧 |
| 任何 stage agent 持 5 protected 字段未落库 | 子代理状态不安全 |

---

## §7 关联引用

- [stage-physical-isolation.md](../stage-physical-isolation.md) — V12 提案
- [v12-physical-isolation/V11.3-fact-stage-rationale.md](V11.3-fact-stage-rationale.md) — 思想起点
- [P0-protocol-vs-parser.md](../P0-protocol-vs-parser.md) — V12 实施前置依赖

