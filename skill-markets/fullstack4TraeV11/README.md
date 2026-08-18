# V12 — Fullstack4TraeV11（高内聚专家架构）

> 全栈文档驱动开发技能包 V12.0.0。V11 物理隔离思想升主版本（2026-08-16 ADR ACCEPTED）。
>
> **当前版本 V12.0.0** — V12 默认布局 = `fact/` + `stage/{N}/` 物理隔离 + `handoff-out/handoff-in` 桥接 + 状态卡每 stage 独立。
>
> 历次重要升级：
> - **V12.0.0** (2026-08-16) — 主版本升级：`init-from-zero.py --layout` 默认 `v12-preview`；V11 扁平布局**永久废弃**；`registry/roles.yaml` 升格为白名单；13 stage 命名约定斜杠
> - **V11.8.7.1** (2026-08-18) — 5 项用户硬要求 3 连修（V11 扁平默认移除 / archive 保留 V12 / module 占位修复 / 多 archive 路径合一）
> - **V11.8.7** (2026-08-17) — case 2 audit-fix（7 个 V11 规范问题修补）
> - **V11.8.6** (2026-08-16) — V12 物理隔离渐进落地（6 步）
> - **V11.8.5.P1** (2026-08-16) — §3.7 #10 commit 准入最小集程序化
> - **V11.8.5** (2026-08-16) — 协议层承诺 → 脚本落地（13/14 done + 1 留置）
> - **V11.8.4** (2026-08-15) — commit 准入最小集与全量验收分层（Stage 3.5/4.5 异步化）
> - **V11.8.3** (2026-08-15) — Stage 6 重构为 4 层分层决策框架
> - **V11.8.2** (2026-08-15) — Stage 6 Bug Fix & Hunt 统一工序
> - **V11.8.1** (2026-08-15) — bug-hunt / E2E 跨阶段实战报告
> - **V11.7.0** — 贾维斯门禁守护体系(防 agent 改标准通过自己)+ AC 核销门禁

---

## 核心特点

- **高内聚专家架构**: 每个 stage 自包含（SKILL/README/workflows/references/templates/anti-patterns）
- **13 stage 流水线**: Intake → Plan → Test Plan → Spec → Prototype → Contract → Implement → Real Verify → Review → Rot Scan → Accept + Bug Fix + Project Health
- **贾维斯门禁守护（V12 沿用 V11.7.0）**: 唯一可改 gate 的 sub-agent + 三层防线(协议/白名单/hash 锁)+ L-module/app/system 分层
- **AC 核销门禁（V12 沿用 V11.6.0）**: 验收是 Guard/Gate 层的机械门禁,不再是评审员打分
- **V12 默认布局**: `fact/` + `stage/{N}/` 物理隔离 + 13 stage 独立状态卡
- **独立部署**: 不依赖 V10 目录
- **V10 思想完整继承**: 17 Articles 宪法（V11.1 新增 Article XVII Secret Redaction）+ 10 项腐化扫描 + 5 类项目验证

---

## 工作原理

V12 是一个**文档驱动 + 三层控制**的全栈开发技能包。它的核心不是"写代码"，而是通过一套**不可绕过的门禁**，强制 agent 在每一阶段产出正确产物，防止"虚假交付"。

### 1. 三层控制架构（V12 沿用 V11.4 + V11.7.0 加固）

V12 用三层架构把"靠 agent 自觉"升级为"靠制度硬化"：

```
┌─────────────────────────────────────────────┐
│  Gate 层（门禁）— 不可绕过，失败即阻断        │
│  ├─ Git 子层：L1 commit / L2 push /          │
│  │   L3 merge / L4 release（husky + CI 触发）│
│  └─ Stage 子层：pre-stage / post-stage /     │
│      pre-accept（阶段切换门禁）               │
│  V11.7.0+: Stage 4 Review → ac-gate.py      │
│           AC 核销门禁(逐 AC 核销,任一 FAIL   │
│           = BLOCK;评审员无敌权,脚本权威)      │
└─────────────────────────────────────────────┘
              ↓ PASS 才进入下一层
┌─────────────────────────────────────────────┐
│  Guard 层（守卫）— 工具调用前后自动检查       │
│  ├─ TRAE IDE event hook（5 种 event）        │
│  └─ Shell hook（3 个，阶段切换用）            │
│  V11.7.0+: gate-integrity-guard.py hash 锁  │
│           跑任何 gate 前强校验 hash;不匹配    │
│           = BLOCK(机械兜底,防 agent 改标准)  │
└─────────────────────────────────────────────┘
              ↓ PASS 才进入下一层
┌─────────────────────────────────────────────┐
│  Execution 层（执行）— 13 stage 流水线        │
│  每个 stage 自包含 + 文档驱动 + 状态卡追踪    │
│  V11.7.0+: pre-stage 装载层(00-boot/agents/ │
│           jarvis.md)— 委派贾维斯铺三层 gate  │
└─────────────────────────────────────────────┘
```

**联动铁律**：Gate PASS → Guard → Execution。任一层 FAIL → 阻断 + 5 字段阻塞报告。Gate 层失败不可绕过（exit ≠ 0）。

**硬化手段**（防止 agent 欺骗绕过）：
- **环境变量强制**：gate 脚本要求 `V12_GATE_ENFORCED` / `V12_GATE_STAGE` / `V12_GATE_CALLER`，缺失即失败
- **SHA-256 签名**：门禁结果签名验签，无法伪造
- **审计轨迹**：状态卡变更写入 `.trae/logs/state-card-audit.jsonl`
- **echo-skip 检测**：守卫脚本拒绝占位符/假通过
- **hooks-fidelity**：验证 hook 是否真实安装、真实执行
- **hash 锁（V12 沿用 V11.7.0）**：所有 gate 相关文件(scripts/ac-gate.py + gates/gate-config.json + .husky/*)锁在 gate.lock.yaml;任何未委派贾维斯的改动 → hash 不匹配 → BLOCK
- **AC 核销门禁（V12 沿用 V11.6.0）**：验收从"评审员打分"重构为"逐 AC 机械核销";AC-ID ↔ TC-ID 强映射,UI 交互 AC 引用 ui-ux-logic 流

### 1.5 贾维斯门禁守护（V12 沿用 V11.7.0 — 防 agent 改标准通过自己）

> 借鉴市场级 `guard-gate-smith` 架构(管 my-trae-helper 仓库本身),贾维斯管 **V12 装载后的目标项目**,作用域互不重叠。

**核心问题**:任何 agent(包括 reviewer / implementer / 主 agent 自己)都可能为通过门禁改标准 — 文档约束对 LLM 是软的,白名单机制对"懂规矩的 agent"是中的,**机械兜底对一切 agent 是硬的**。

**三层防线**(由软到硬,任一层兜底):

| 层 | 机制 | 挡住谁 |
|----|------|--------|
| 协议层 | `[JARVIS-DELEGATION]` 委派头部(7 步 SOP) | 守规矩的 agent |
| 白名单层 | jarvis.md §3 路径白名单 | 越权直改的 agent(事后审计) |
| 机械层 | `gate-integrity-guard.py` hash 锁 | **一切绕过行为(事前拦截)** |

**贾维斯 6 时机**:

| 时机 | 触发 | 贾维斯动作 |
|------|------|-----------|
| ① 初始化 | 项目首次用 V12 / 新增分层 | `gate-installer.py` 铺三层 gate + 生成 `gate.lock.yaml` |
| ② 自检 | 任何 gate 执行前(自动) | `gate-integrity-guard.py --verify`,不匹配 = BLOCK |
| ③ 指导开发 | 任何 agent 请求改 gate | 接受委派 → 评估 → 改 → 重签 lock → 报告 |
| ④ 通用验收 gate 设计 | 技术策划产出/更新技术方案 | 接收 `[JARVIS-DELEGATION]`（type: gate-design）→ 把方案的验收规则转译为可执行 gate 配置 |
| ⑤ 文档-代码一致性 gate | 技术策划方案声明文档↔代码映射约束 | 配置 doc-sync-gate.py 规则(spec 字段 ↔ 实现符号) |
| ⑥ 升级初始化与迁移 | V12 技能升级 / 既有 V11 项目迁移 | 跑 `--migrate-from-v11` 主路径迁移脚本 → 校验 gate.lock 兼容 → 重新初始化并出迁移报告 |

**L-module / L-app / L-system 分层模型**(每层独立扩 guard,不交叉污染):

```
L-system 系统层 — AC 核销验收 + 腐化扫描 + 发布门禁      → 挂 L3 merge / L4 release
L-app    应用层 — 契约对齐 + 模块集成 + 真实验证         → 挂 L2 pre-push
L-module 模块基础层 — CRUD 单测 + 模块结构             → 挂 L1 pre-commit
docs     流程前置层 — 文档完整性(按 stage 顺序跑)
```

**P0 自检发现并修复**:`--generate` 旧版本在 verify BLOCK 时会把"被篡改状态"固化为新基线。V11.7.0 修复:默认先 verify;FAIL 时拒绝非强制重签,强制必须附 `--reason '<[JARVIS-DELEGATION] 委派编号>'` 作为会话审计。

```bash
# 危险(已堵):篡改后默认 generate → 把篡改固化
python gate-integrity-guard.py --generate --root .

# 安全:只有审计重签能走通
python gate-integrity-guard.py --generate --root . --force --reason "JARVIS-2026-08-15-001 ac-gate G4 阈值放宽"
```

详见 [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md) + [skills/00-boot/agents/jarvis.md](skills/00-boot/agents/jarvis.md) + [references/gate-configuration-protocol.md](references/gate-configuration-protocol.md)。

### 2. 文档驱动：状态卡（State Card）

V12 多卡模式:每个变更（change）在 `stage/{N}/.state-card.md` 维护独立的阶段状态卡,项目级副本落 `fact/.state-card.md`：

```yaml
card_type: state-card
current_stage: 1/spec
stage_status: pending
last_gate_time: null
```

- **阶段切换**：`stage-gate.py --state-card stage/{N}/.state-card.md` 校验当前阶段产物是否达标
- **全局门禁**：`phase-gate.py --verify-rot-scan` 校验跨阶段完整性
- 状态卡是 13 stage 流水线的"方向盘"，gate 都是围绕它运转

### 3. 13 stage 流水线如何被驱动

```
主上下文（编排器）                     sub-agent（执行）
     │                                     │
     │ 委派头部（注入状态卡+上游报告）      │
     ├────────────────────────────────────→│ 加载 stage SKILL
     │                                     │ 执行 stage
     │  ←———— 返回 Completion Report ──────┤
     │                                     │
     │ 验收（9 CROSS-SESSION VERIFY，      │
     │ 亲自跑 evidence 命令，不用记忆）     │
     │                                     │
     │ 通过 → 更新状态卡 → 进入下一 stage   │
```

- **高内聚**：每个 stage skill 自包含（SKILL/README/workflows/references/scripts），编排器只做路由 + 门禁 + 状态卡同步
- **物理隔离（V12 强制默认）**：`fact/` + `stage/{N}/` 目录隔离，防止子代理越界改非本 stage 文件
- **验收即证据**：不接受"应该可以了"，只接受命令实际输出

### 4. 版本演进

| 版本 | 核心演进 |
|------|---------|
| **V12.0.0** | **主版本升级**：V12 默认布局(`fact/` + `stage/{N}/`) + 13 stage 独立状态卡 + handoff-out/handoff-in 桥接 + `--migrate-from-v11` 主路径 |
| V11.8.7.1 | 5 项用户硬要求 3 连修（V11 扁平默认移除 / archive 保留 V12 / module 占位修复）|
| V11.8.7 | case 2 audit-fix（7 个 V11 规范问题修补）|
| V11.8.6 | V12 物理隔离渐进落地（6 步）|
| V11.8.5.P1 | §3.7 #10 commit 准入最小集程序化 |
| V11.8.5 | 协议层承诺 → 脚本落地 |
| V11.8.4 | commit 准入最小集与全量验收分层 |
| V11.8.3 | Stage 6 重构为 4 层分层决策框架 |
| V11.8.2 | Stage 6 Bug Fix & Hunt 统一工序 |
| V11.8.1 | bug-hunt / E2E 跨阶段实战报告 |
| V11.7.0 | 贾维斯门禁守护体系(防 agent 改标准)+ hash 锁 + 分层模型 |

---

## 目录结构

```
fullstack4TraeV11/
├── SKILL.md              # 总编排器（必读）
├── README.md             # 本文件
├── CHANGELOG.md          # 版本变更
├── references/           # 公共 references
│   ├── gate-configuration-protocol.md   # V12 沿用 V11.7.0 贾维斯委派 7 步 SOP
│   ├── trap-instructions.yaml            # 反例 → 指令映射
│   └── ...
├── templates/            # 公共 templates
├── scripts/              # 公共脚本（Python，全部实装）
│   ├── ac-gate.py                       # V12 沿用 V11.6.0 AC 核销门禁(G1-G5)
│   ├── stage-gate.py                    # V12 阶段门禁(SHA-256 签名)
│   ├── gate-installer.py                # V12 沿用 V11.7.0 贾维斯 installer
│   └── gate-integrity-guard.py          # V12 沿用 V11.7.0 hash 锁(防篡改)
├── registry/             # Flow 层 Registry(V11.5+, V12 沿用)
│   ├── gates.yaml                       # 13 stage 门禁 + V12 沿用 layer 字段
│   ├── guards.yaml
│   ├── roles.yaml                       # V12 NEW: 8 角色注册表 + 路径白名单
│   ├── state-machine.yaml
│   ├── repair-flow.yaml
│   └── stacks.yaml
├── skills/               # 13 stage skill（高内聚）
│   ├── 00-boot/             # V12 沿用 V11.7.0 pre-stage 装载层
│   │   ├── SKILL.md
│   │   └── agents/jarvis.md # 贾维斯定义
│   ├── 01-intake/
│   ├── 02-plan/
│   ├── ...
│   └── 13-project-health/
└── stage-physical-isolation.md  # 物理隔离规范（V12 强制默认）
```

---

## 13 stage 流水线

| 阶段 | 名称 | SKILL.md | layer (V12 沿用 V11.7.0) |
|:---:|------|----------|------------------|
| pre | **贾维斯装载(V12 沿用 V11.7.0)** | [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md) + [agents/jarvis.md](skills/00-boot/agents/jarvis.md) | — |
| -1 | Intake | [skills/01-intake/SKILL.md](skills/01-intake/SKILL.md) | docs |
| 0 | Plan | [skills/02-plan/SKILL.md](skills/02-plan/SKILL.md) | docs |
| 0.5 | Test Plan | [skills/03-test-plan/SKILL.md](skills/03-test-plan/SKILL.md) | docs |
| 1 | Spec | [skills/04-spec/SKILL.md](skills/04-spec/SKILL.md) | docs |
| 1.5 | Prototype | [skills/05-prototype/SKILL.md](skills/05-prototype/SKILL.md) | docs |
| 2 | Contract | [skills/06-contract/SKILL.md](skills/06-contract/SKILL.md) | app |
| 3 | Implement | [skills/07-implement/SKILL.md](skills/07-implement/SKILL.md) | module |
| 3.5 | Real Verify | [skills/08-real-verify/SKILL.md](skills/08-real-verify/SKILL.md) | app |
| 4 | Review | [skills/09-review/SKILL.md](skills/09-review/SKILL.md) | **system (V12 沿用 V11.6.0 ac-gate)** |
| 4.5 | Rot Scan | [skills/10-rot-scan/SKILL.md](skills/10-rot-scan/SKILL.md) | system |
| 5 | Accept | [skills/11-accept/SKILL.md](skills/11-accept/SKILL.md) | system |
| 6 | Bug Fix | [skills/12-bug-fix/SKILL.md](skills/12-bug-fix/SKILL.md) | system |
| 7 | Project Health | [skills/13-project-health/SKILL.md](skills/13-project-health/SKILL.md) | system |

**贾维斯装载(pre-stage)**:会话第一步委派贾维斯铺三层 gate + 签 hash 锁,不走 13 stage 状态机,不产生状态卡流转。详见 [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md)。

---

## 快速开始

### 1. 加载 V12 主 SKILL.md

主上下文收到 "Use Skill: fullstack4traev11" 后必走 §0.5 加载协议：

1. 加载 SKILL.md（含 stage_config）
2. 必读公共 references（constitution / common-iron-rules / common-anti-patterns / state-card-protocol / stage-interaction-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns）
3. Glob 项目级约定（AGENTS.md / docs/ / .trae/rules/）
4. 3 层依赖合并（项目 > V12 > 全局）
5. **V12 沿用 V11.7.0**: 会话第一步委派贾维斯铺三层 gate + 签 hash 锁（见 [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md)）
6. 进入 Stage -1 Intake 工作模式

### 2. 委派到 Stage skill

主上下文委派 sub-agent 时，按 stage skill 的 SKILL.md 必走 4 步：

```
[1] 加载 stage skill SKILL.md
[2] 注入上下文（状态卡 + 上游 Completion Report）
[3] 委派 sub-agent-{stage}
[4] 验收（必走 9 CROSS-SESSION VERIFY，亲自跑 evidence 命令）
```

### 3. 公共脚本使用

```bash
# V12 默认状态卡门禁(per-stage)
python scripts/stage-gate.py --state-card stage/-1/intake/.state-card.md
python scripts/stage-gate.py --state-card stage/3/implement/.state-card.md
python scripts/stage-gate.py --reset-to stage/3/implement

# 全局阶段门禁（含 verify-rot-scan）
python scripts/phase-gate.py --state-card fact/.state-card.md --verify-rot-scan --change-id {id}

# 腐化扫描
python scripts/proactive-scan.py --project-root . --output rot-scan.md --output-fix-list fix-list.json

# 元检测（rot-detector 自身）
python scripts/self-diagnose.py --project-root .

# V12 沿用 V11.6.0 AC 核销门禁(取代评分制)
python scripts/ac-gate.py \
  --review-report stage/4/review/review-notes.md \
  --spec fact/spec.md \
  --test-plan fact/test-plan.md

# V12 沿用 V11.7.0 贾维斯 installer(项目初始化/分层新增)
python scripts/gate-installer.py --target <项目根> --preset <nodejs|python> --layers module,app,system

# V12 沿用 V11.7.0 hash 锁校验(跑 gate 前必调)
python scripts/gate-integrity-guard.py --verify --root <项目根>

# V12 沿用 V11.7.0 重新签锁(仅贾维斯)
python scripts/gate-integrity-guard.py --generate --root <项目根>
# 强制重签(检测到未授权前提时,需附 --reason):
python scripts/gate-integrity-guard.py --generate --root <项目根> --force --reason "JARVIS-2026-08-15-001 阈值变更描述"

# V12 主路径迁移(既有 V11 项目)
python scripts/init-from-zero.py --migrate-from-v11 [path] [--dry-run] [--no-backup]
```

---

## V12 增强(强制默认)

### V12 默认布局(`fact/` + `stage/{N}/`)

- **`fact/`**: 4 层文档真相源(spec.md / plan.md / contracts/ / test-plan.md / prototype.md / module.md)
- **`stage/{N}/`**: 13 stage 流程产物(notes/handoff-out/state-card),每 stage 独立子目录
- **状态卡每 stage 独立**: `stage/{N}/.state-card.md` + 项目级副本 `fact/.state-card.md`
- **`process-layer-guard.sh`**: 强制路径校验 hook(V12 默认启用)
- **`--migrate-from-v11`**: V11 项目迁移主路径(8 步原子迁移)
- 见 [CHANGELOG.md V12.0.0 条目](CHANGELOG.md) 详情

### 贾维斯门禁守护体系(V12 沿用 V11.7.0)

- **skills/00-boot/SKILL.md** + **agents/jarvis.md** — pre-stage 角色装载层 + 贾维斯定义(6 时机/3 层/白名单/5 步流程)
- **references/gate-configuration-protocol.md** — 调用方 7 步 SOP
- **scripts/gate-installer.py** — 时机① installer(读 registry/gates.yaml 按分层铺目标项目 hook)
- **scripts/gate-integrity-guard.py** — 时机② hash 锁(`--verify`/`--generate`/`--force --reason`)
- **registry/gates.yaml v1.2.0** — 13 gate 全部加 `layer` 字段(docs/module/app/system)
- **registry/roles.yaml v1.0.0** (V12 NEW) — 8 角色注册表 + 路径白名单
- **3 反例**(trap-instructions.yaml) — `V11-JARVIS-BYPASS-LOCK` / `V11-JARVIS-FORCE-WITHOUT-AUDIT` / `V11-JARVIS-OVERRIDE-LAYER`

### AC 核销门禁(V12 沿用 V11.6.0)

- **scripts/ac-gate.py** — G1-G5 机械门禁(矩阵存在/至少 1 行/逐行通过/spec 全覆盖/TC 防编造)
- **skills/04-spec/workflows/acceptance-criteria-extract.md** — 6 类 AC(新增 UI 交互 AC,引用 ui-ux-logic 流)
- **skills/09-review/workflows/acceptance-baseline-extract.md** — Step -2 验收基准提取 4 步流程
- **skills/09-review/templates/review-report-template.md** — AC 核销矩阵(6 列)为判定本体
- **skills/03-test-plan/workflows/coverage-mapping.md** — 强制 `ac: AC-ID` + `ui_flow` 字段 + Step 3.5 双向补齐检

### 物理隔离(V12 强制默认)

- **stage-gate-pre-stage.sh**: husky 式硬阻断门禁（templates/hooks/，独立于 pre-stage.sh）
- **stage-physical-isolation.md**: fact/ + stage/ 物理隔离规范(V12 强制默认)

---

## 项目状态（2026-08-18 update）

V12.0.0 — 主版本升级 + V11.8.7.1 5 项硬要求 3 连修：

| 维度 | 进度 |
|------|------|
| V12 主版本升级 | ✅ DONE |
| 13 stage 独立状态卡 | ✅ DONE |
| handoff-out/handoff-in 桥接 | ✅ DONE |
| `--migrate-from-v11` 主路径 | ✅ DONE |
| 5 项用户硬要求(V11.8.7.1) | ✅ DONE |

**注**：本仓库是 my-trae-helper 元项目的 `skill-markets/fullstack4TraeV11/` 子目录，跨仓 commit 受 §B 7 步 SOP 治理。详见 [CHANGELOG.md](CHANGELOG.md) 与 [references/todos/](references/todos/README.md)。

---

## 部署

```bash
# V12 部署到 ~/.trae-cn/skills/
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/

# 验证
ls ~/.trae-cn/skills/fullstack4TraeV11/skills/
ls ~/.trae-cn/skills/fullstack4TraeV11/scripts/
```

---

## 关联引用

- [SKILL.md](SKILL.md) - V12 总编排器（V12 入口）
- [CHANGELOG.md](CHANGELOG.md) - 版本变更(V12.0.0 主版本升级 + V11.6.0 AC 核销 + V11.7.0 贾维斯)
- [references/constitution.md](references/constitution.md) - 17 Articles 宪法
- [references/common-iron-rules.md](references/common-iron-rules.md) - 公共铁律
- [references/stage-physical-isolation.md](references/stage-physical-isolation.md) - 物理隔离规范(V12 强制默认)
- [references/gate-configuration-protocol.md](references/gate-configuration-protocol.md) - **V12 沿用 V11.7.0** 贾维斯委派 7 步 SOP
- [references/trap-instructions.yaml](references/trap-instructions.yaml) - 反例 → 指令映射
- [skills/00-boot/SKILL.md](skills/00-boot/SKILL.md) - **V12 沿用 V11.7.0** 贾维斯启动装载器
- [skills/00-boot/agents/jarvis.md](skills/00-boot/agents/jarvis.md) - **V12 沿用 V11.7.0** 贾维斯定义(白名单 + 5 步响应流程 + 6 时机)
- [registry/gates.yaml](registry/gates.yaml) - **V12 沿用 V11.7.0 layer 字段** 13 stage 门禁 + 分层
- [registry/roles.yaml](registry/roles.yaml) - **V12 NEW** 8 角色注册表 + 路径白名单