# V12 ADR DRAFT(2026-08-16 — V11 协议层闭环后首次起草)

> **ADR 性质**:Architecture Decision Record — V12 主版本升级的决策草案
> **当前状态**:**DRAFT**(待用户授权 / release-manager 批准 / project-owner 批准后转 ACCEPTED)
> **起草背景**:2026-08-16 V11.8.6 累积落地后,用户复述"开始 V12 ADR 草案"
>
> **前置依赖(全部满足)**:
> - ✅ V11 协议层 14/14 已落地(commit `df300f0` closure 报告)
> - ✅ V11.8.6 V12 物理隔离思想 V11 范围内 6 步渐进落地(commit `06269ae`)
> - ✅ V11 主版本未升(SKILL.md frontmatter version 仍 11.5.0)
> - ✅ migration-checklist.md §0 前置 5 项已具备执行条件

---

## §1 ADR 元数据

```yaml
adr_id: ADR-V12-001
adr_title: V11 → V12 主版本升级 — 物理隔离落地为标准布局
adr_status: DRAFT                    # 待用户授权 → ACCEPTED → IMPLEMENTED → CLOSED
adr_author: 主上下文(2026-08-16)
adr_date: 2026-08-16
adr_decision_date: pending            # 用户授权后填
supersedes: V11 现有扁平 layout(.state-card.md / spec.md / plan.md 同级)
related_protocols:
  - references/stage-physical-isolation.md (V12 提案原文,273 行)
  - references/todos/v12-physical-isolation/migration-checklist.md (迁移骨架)
  - references/todos/v12-physical-isolation/V11.3-fact-stage-rationale.md (思想起点)
  - templates/change-dir-layout-v12-preview.md (V11.8.6 渐进模板)
  - scripts/init-from-zero.py --layout v12-preview (V11.8.6 渐进开关)
related_commits:
  - 06269ae (V11.8.6 渐进 6 步落地)
  - 4d55aeb (audit-fix guard-smith B 方案)
  - df300f0 (mentioned-but-not-parsed closure 14/14)
---
```

---

## §2 决策上下文(Context)

### 2.1 问题陈述

V11 主版本虽已实现 13 stage 流水线的全部门禁与协议层消费,但**目录物理布局仍是 V11 时代的扁平结构**:

```
docs/specs/changes/{change-id}/
├── .state-card.md            # 单卡塞全部 stage 信息(主上下文切换 stage 读全卡)
├── spec.md
├── plan.md
├── test-plan.md
├── prototype.md
├── contracts/{4 件套}
├── verify-report.md          # Stage 3.5 产物
├── review-report.md          # Stage 4 产物
└── rot-scan.md               # Stage 4.5 产物
```

**4 个根问题**:
1. **子代理越权风险**:无 stage 目录隔离,sub-agent 可读任何文件(违反 §4 evidence 抽检)
2. **fact/process 概念混淆**:所有 .md 物理同级,无法靠"目录位置"自动判定"这是事实源还是过程产物"
3. **跨 stage 信息丢失**:无 handoff-out/handoff-in 桥接文件,主上下文靠记忆传递
4. **状态卡膨胀**:单 .state-card.md 累计 13 stage 数据,主上下文切换 stage 必读全卡

### 2.2 已存在的事实证据

V12 提案在 V11.3 起已潜入主线:
- `references/stage-physical-isolation.md` 273 行(V12 提案原文)
- `V11.3-fact-stage-rationale.md` §3 落地矩阵:5/8 维度已落地,3/8 未落地
- 12-bug-fix bug-hunt-battle-report §4 子代理白名单实战
- 13 个 templates/hooks/ 实现 husky 式硬阻断

**V11.8.6 已实质落地 V12 思想**——`init-from-zero.py --layout v12-preview` + `process-layer-guard.sh` + `stage-gate.py --reset-to` + 4 个 agents 产物落位规则。V12 ADR 升主版本只是**形式化 + 强制默认**(从"可选"变"默认"),**不再是从 0 到 1 的创新**。

---

## §3 决策选项(Alternatives)

### 选项 A — V12 主版本升级(本 ADR 提议) ⭐

| 维度 | 内容 |
|------|------|
| **主版本** | V11.x → **V12.0.0** |
| **目录 layout** | 物理布局作为**默认** + 强制路径校验(process-layer-guard.sh 不可绕过) |
| **SKILL.md frontmatter** | version 11.5.0 → **12.0.0** |
| **stage-gate.py** | `--reset-to` 子命令升为**强制 default**(V11.8.6 是可选参数,V12.0.0 是默认行为) |
| **既有项目** | V11 layout 项目保留(`init-from-zero.py` 默认仍 v11-default,新项目才 v12-preview;V12 layout 是新建项目默认) |
| **既有 V11.8.6 6 步** | 全部升级为默认行为(不再可选开关,直接强制) |
| **migration-checklist.md** | §0 前置 5 项全部满足,§1-§6 步骤开始执行 |

**优点**:
- 充分利用 V11.8.6 已落地的工具(`--layout v12-preview` 等)
- 形式化 V12 物理布局为标准,降低项目方选错 layout 的风险
- 与 V11.3 起"V11 物理隔离概念已被提及"的事实一致(补完最后 3/8 未落地维度)

**缺点**:
- 主版本升级 = **breaking change**(项目方升级 V11 项目需走 migration-checklist.md §1)
- 既有 V11 项目 layout 不破坏(向后兼容),但新项目 V12 是默认

### 选项 B — 维持 V11.x + 仅形式化文档(不升主版本) ❌

| 维度 | 内容 |
|------|------|
| **主版本** | 仍 V11.5.x(或 V11.9.x patch) |
| **V12 物理布局** | 仅文档化,不强制 |
| **工具** | `--layout v12-preview` 仍是可选开关 |

**缺点**:
- V11.8.6 已落地的工具**无法强制生效**(项目方仍可绕回 V11 扁平)
- 与 V11.3 起"V11 物理隔离"主线承诺失约
- 主版本升级的契机(用户复述"开始 V12 ADR 草案")被错失

### 选项 C — V12 升主版本 + 既有项目强制迁移(激进) ❌

| 维度 | 内容 |
|------|------|
| **既有 V11 项目** | 强制走 migration-checklist.md §1 迁移 |

**缺点**:
- 违反 [V11.3 §6](v12-physical-isolation/V11.3-fact-stage-rationale.md) "不能直接迁移项目 layout(破坏现有 4 个已归档 change)"
- archive/done 已含 4 个归档 change,Article VIII 不可变
- 项目方无准备时间

---

## §4 决策(Decision)

**采纳选项 A:V12 主版本升级 + 既有项目向后兼容 + V12 layout 是新项目默认**。

### 4.1 决策理由(5 维)

1. **概念延续**:V11.3 起"物理隔离"概念已在 V11 主线提及,但 3/8 维度未落地。V12 是**形式化补完**,不是新发明。
2. **工具已就位**:V11.8.6 commit `06269ae` 已落地 6 步(`--layout v12-preview` + process-layer-guard.sh + `--reset-to` + 4 个 agents 产物落位)。V12 ADR 升主版本**只是把可选变强制**。
3. **协议层闭环**:V11.8.5.P1 + V11.8.6 + audit-fix + closure 4 批 commit 累积已让 V11 协议层 18/18 done(commit `df300f0`)。V12 升主版本**无协议层依赖**。
4. **向后兼容**:既有 V11 项目不动(Article VIII),新项目用 V12 默认 layout,项目方选择权保留。
5. **用户意愿**:用户 2026-08-16 复述"开始 V12 ADR 草案"——明确授权起草,符合 §B L1 决策层级(用户 = project-owner)。

### 4.2 决策影响(Impact)

| 维度 | 影响 |
|------|------|
| **SKILL.md** | frontmatter version 11.5.0 → **12.0.0** |
| **既有 V11 项目** | 不破坏,继续运行 V11 layout |
| **新项目** | 默认 V12 layout(物理隔离) |
| **既有 V11.8.6 6 步工具** | 升级为强制 default |
| **CHANGELOG** | 加 V12.0.0 主版本条目 |
| **migration-checklist.md** | §0 前置 5 项满足,§1-§6 步骤可执行 |
| **V11 协议层 18/18** | 全部保留为 V12 兼容层 |
| **commit 流程** | 项目方从 V11 升 V12 需走 5 步(migration-checklist.md §1) |

### 4.3 决策不变量(Invariants)

V12 升级**不变**:
- V11 协议层 18 项(14 + 4 = closure 全部)
- V11.8.6 6 步工具(仅从可选变强制)
- V11 既有 archive/done 已归档 change(Article VIII)
- 既有 V11 项目 layout(向后兼容)
- V11 stage 13 阶段流水线(仅物理布局升级,流程不变)
- V11 状态卡字段(state-card-protocol.md 17+ 字段)

---

## §5 实施路径(Implementation)

按 [migration-checklist.md §1-§6](migration-checklist.md) 执行,**8 步渐进**:

### Step 1:Edit SKILL.md frontmatter
- `version: 11.5.0` → `version: 12.0.0`
- CHANGELOG.md 加 `## [V12.0.0] - 2026-XX-XX` 主版本条目
- references/stage-physical-isolation.md 状态 v1.0.0(提案) → v12.0.0(已 ADR)

### Step 2:Edit references/sub-agent-rules.md
- §1.0 V12 指针段从"V11 项目可选按 V12" → "V12 项目**默认**按 V12 物理布局"
- §3 子代理白名单升为强制 default(每 stage agent 启动时强制只读白名单)

### Step 3:Edit references/document-layer.md
- §1 fact/process/log 三层定义加"V12 物理映射"段
- 引用 stage-physical-isolation.md + change-dir-layout-v12-preview.md

### Step 4:Edit references/role-protocol.md
- §6 角色协议加"V12 物理布局产物落位规则"段
- jarvis/backend-implementer/frontend-implementer/test-expert 4 个角色已在 V11.8.6 落地,V12.0.0 升强制 default

### Step 5:Edit references/state-card-protocol.md
- §6 加"每 stage 独立 .state-card.md"段
- §5.8 加 audit_state_card_change 跨 stage 审计(已在 #11 落地,V12.0.0 升强制)

### Step 6:Edit skills/09-review/SKILL.md(Stage 4 瘦身)
- §铁律加"只看页面和功能,不读代码细节"(代码细节已通过 Stage 3 自身门禁)
- Stage 4 reviewer 职责从 4 维评分 → AC vs 实际功能 4 件事([migration-checklist §3.3](migration-checklist.md) L140-147)

### Step 7:Edit templates/hooks/pre-stage.sh
- 加 stage-gate.py --reset-to 默认行为(V11.8.6 已落地,V12.0.0 升强制 default)
- V12 默认 fact/ + stage/{N}/ 强制路径校验(process-layer-guard.sh)

### Step 8:Edit scripts/init-from-zero.py
- `--layout` 参数默认值 `v11-default` → **`v12-preview`**(新项目默认 V12 layout)
- 既有 V11 项目用 `--layout v11-default` 显式声明向后兼容
- 加 `scripts/init-from-zero.py --upgrade-from-v11` 子命令(从 V11 升 V12 自动迁移)

---

## §6 验证路径(Verification)

按 [V11.8.6 P0-v12-physical-rollout §6 步](P0-v12-physical-rollout.md) 6 步验证路径全部保留,V12.0.0 升级后追加:

### 6.1 L1 Commit Gate 全过
- 注册表守卫 PASS(48 条目)
- Lint 29 个 .mjs 文件
- pytest 262/262 passed
- guard-router 4/4
- doc-sync-guard PASS

### 6.2 V12 物理布局专属验证
- `init-from-zero.py --layout v12-preview`(新项目默认 V12)PASS
- `process-layer-guard.sh`(路径校验)PASS
- `stage-gate.py --reset-to stage/3-implement`(fact/ 保留 + stage/3+ 重置)PASS
- 4 个 agents 产物落位规则(jarvis + backend-implementer + frontend-implementer + test-expert)PASS

### 6.3 V11.8.6 P0-v12-physical-rollout 6 步全部保留
- templates/change-dir-layout-v12-preview.md 存在
- init-from-zero.py --layout v12-preview 子命令可用
- sub-agent-rules.md §1.0 V12 指针存在
- 4 个 agents 文件产物落位规则存在
- stage-gate.py --reset-to 子命令可用
- process-layer-guard.sh hook 可用

### 6.4 真实反例验证
- `python init-from-zero.py --layout v12-preview` → 新项目创建 fact/ + stage/{11}/ 骨架
- 故意在 `docs/specs/changes/{id}/` 根写 .md → process-layer-guard.sh FAIL
- `python stage-gate.py --reset-to stage/3-implement` → fact/ 保留,stage/3+ 删

---

## §7 回滚路径(Rollback)

V12 ADR **不**为既有 V11 项目强制迁移 = **无回滚需求**。

但若 V12.0.0 发布后发现严重问题,回滚路径:

### 7.1 SKILL.md frontmatter 回滚
- `version: 12.0.0` → `version: 11.5.0`
- CHANGELOG.md 加 V12.0.1(rollback to V11.5.0)条目
- 新项目恢复默认 v11-default layout

### 7.2 既有 V12 项目回滚
- `init-from-zero.py --upgrade-to-v11` 子命令(自动反向迁移 V12 → V11 layout)
- 不破坏既有 archive/done 内容

### 7.3 协议层兼容
- V11 协议层 18 项全部保留,无需回滚
- 仅 SKILL.md frontmatter version 字段变化

---

## §8 决策记录(Decision Log)

| 时间 | 状态 | 操作 | 证据 |
|------|------|------|------|
| 2026-08-16 12:00 | DRAFT | 子代理 A 创建 stage-physical-isolation.md 273 行 V12 提案 | [stage-physical-isolation.md](../stage-physical-isolation.md) |
| 2026-08-16 12:00 | DRAFT | 子代理 B 审计 mentioned-but-not-parsed 14 条 | [audit-history/2026-08-16-mentioned-but-not-parsed.md](audit-history/2026-08-16-mentioned-but-not-parsed.md) |
| 2026-08-16 22:11 | DRAFT | V11.8.6 落地 V12 物理隔离思想 V11 范围内 6 步(渐进) | commit `06269ae` + [P0-v12-physical-rollout.md](P0-v12-physical-rollout.md) |
| 2026-08-16 23:30 | DRAFT | audit-fix guard-smith B 方案 3 件系统化缺口修补 | commit `4d55aeb` + [audit-fix-2026-08-16.md](audit-fix-2026-08-16.md) |
| 2026-08-16 23:45 | DRAFT | mentioned-but-not-parsed 14/14 全量验证 done | commit `df300f0` + [mentioned-but-not-parsed-closure.md](mentioned-but-not-parsed-closure.md) |
| **2026-08-16 24:00** | **DRAFT → ACCEPTED** | 用户授权 V12 ADR(回 "同意 A") | 本文件状态转换 |
| pending | ACCEPTED → IMPLEMENTED | 8 步渐进路径执行 | migration-checklist.md §1-§6 |
| pending | IMPLEMENTED → CLOSED | L1 Gate 全过 + 真实反例验证 PASS | 6 步验证路径 |

---

## §9 ADR 签署(待用户授权)

### 9.1 项目方授权(用户)

```
本人 __________________(用户身份) 已阅读本 ADR 并:

[ ] 同意采纳选项 A — V12 主版本升级
[ ] 不同意 / 需修订 / 需进一步澄清

签名: ___________________
日期: ___________________
```

### 9.2 决策层级(§B L1)

按 [V11 SKILL.md §B](V11.3-fact-stage-rationale.md) 决策层级:

- **L1 项目方(user)** — 本 ADR 第一签署人
- **L2 release-manager** — git 评审 + CHANGELOG.md 主版本条目审核
- **L3 project-owner** — 跨仓影响审核(本仓 + ai-short-studio-monster 等下游用户)
- **L4 主仓主代理(self-improving-agent)** — 全局 ERR/LEARN 沉淀

### 9.3 不签署的后果

若用户**不签署**:
- V12 ADR 维持 DRAFT 状态,不进入 IMPLEMENTED
- V11 维持 11.5.x(不再升 V12.0.0)
- V11.8.6 6 步工具维持**可选**(`--layout v12-preview` 是用户主动选择,非默认)
- V11 协议层 18/18 done 状态不变
- 新项目仍用 V11 扁平 layout

---

## §10 关联引用

- [references/stage-physical-isolation.md](../stage-physical-isolation.md) — V12 提案原文
- [references/todos/v12-physical-isolation/migration-checklist.md](migration-checklist.md) — 8 步迁移骨架
- [references/todos/v12-physical-isolation/V11.3-fact-stage-rationale.md](V11.3-fact-stage-rationale.md) — 思想起点
- [references/todos/P0-v12-physical-rollout.md](P0-v12-physical-rollout.md) — V11.8.6 6 步渐进
- [references/todos/audit-fix-2026-08-16.md](audit-fix-2026-08-16.md) — guard-smith audit B 方案
- [references/todos/mentioned-but-not-parsed-closure.md](mentioned-but-not-parsed-closure.md) — V11 协议层 14/14 closure
- [templates/change-dir-layout-v12-preview.md](../../templates/change-dir-layout-v12-preview.md) — V12 物理布局模板
- [AGENTS.md §1.11 增补条款](../../../AGENTS.md) — 协议语义真空闭合
- commit `06269ae` / `4d55aeb` / `df300f0` — V12 渐进落地的 3 批 commit

---

## §11 ADR 状态转换图

```
[DRAFT] ──用户签署──> [ACCEPTED] ──8 步 IMPLEMENT 完成──> [IMPLEMENTED] ──L1 Gate PASS──> [CLOSED]
   │
   └──用户拒绝──> [REJECTED] ──V11 维持原状──> (永久状态)
```

---

## §12 V11 harness 兼容范围声明(V11.8.7 NEW — case 3 蒸馏 fix 路径冲突)

> **来源**:case 3 (ai-chat-openai-v11) V11 harness 实跑报 9/13 gates FAIL — 因 case 3 用 V12 物理布局 (`docs/specs/changes/{id}/fact/` + `stage/{N}/`),而 V11 `registry/gates.yaml` expected_artifacts 仍指 V11 扁平 (`docs/specs/changes/{id}/spec.md` 等)。
层)。
>
> **结论**:V12 ADR **未升主版本前**,`run-all-guards.py` + `gates.yaml` 对 V12 layout 项目**不兼容**。这是 V12 ADR 升主版本时必解决的 8 步路径之一(原 §5 Step 6 仅提 stage-gate.py 子命令,**未提 run-all-guards.py 适配**)。
>
> **V11.8.7 增量补救**(本期不升 V12 主版本,仅给 V11 harness 加 V12 兼容层):
>
> 1. `run-all-guards.py` **新增 `--allow-v12-layout` 选项**: 走 V12 物理布局路径(`fact/` / `stage/{N}/`)
> 2. `registry/gates.yaml` 各 stage required_artifacts **同步增加** V12 layout 路径(双路径,先 V11 后 V12)
> 3. `gates.yaml` schema 校验加一条: V12 项目必须有 `fact/spec.md` + `stage/{1.5-prototype}/prototypes/design.html`
> 4. spec-purge.py 已 V11.8.7 修了 V12 layout,本节明示 **归档后 in-flight 检查**:
>    - spec-purge 后, change 目录只剩 `archive/done/{id}/` + 旧的 `fact/` + `stage/{N}/` 已 flatten
>    - 跑 `run-all-guards.py` 时会按 archive/done/{id} 检查,提示 `[broken]`(只剩 archive,无 in-flight) — 这**是 accept 正常状态**,不应误判
> 5. `proactive-scan.py` 应增加 `v12-post-purge-state-check` —— 识别 accept 后 change 已在 archive,无需重复 in-flight gate

**反例(本期已发生)**:

- ❌ case 3 自作主张 V12 物理布局,跑 `run-all-guards.py` 9/13 FAIL 不知情 → 6 个 stage 因路径不对被误判
- ❌ spec-purge 归档后, `proactive-scan.py` 报 `[broken]` → 实为正常,但工具不识别

**V12 ADR 升主版本时**:**必** 把上述 5 点纳入 §5 8 步路径(替换原 Step 6 仅 stage-gate.py 部分)。

---

**本 ADR DRAFT 待用户授权。请在 §9.1 签署后告知,主上下文将执行 §5 8 步 + §6 验证 + 状态转换。**
