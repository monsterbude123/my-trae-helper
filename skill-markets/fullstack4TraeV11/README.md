# V11 — Fullstack4TraeV11（高内聚专家架构）

> 全栈文档驱动开发技能包 V11。V10 思想传承 + 架构升级。

---

## 核心特点

- **高内聚专家架构**: 每个 stage 自包含（SKILL/README/workflows/references/templates/anti-patterns）
- **13 stage 流水线**: Intake → Plan → Test Plan → Spec → Prototype → Contract → Implement → Real Verify → Review → Rot Scan → Accept + Bug Fix + Project Health
- **独立部署**: 不依赖 V10 目录
- **V10 思想完整继承**: 17 Articles 宪法（V11.1 新增 Article XVII Secret Redaction）+ 10 项腐化扫描 + 4 维评分 + 5 类项目验证

---

## 工作原理

V11 是一个**文档驱动 + 三层控制**的全栈开发技能包。它的核心不是"写代码"，而是通过一套**不可绕过的门禁**，强制 agent 在每一阶段产出正确产物，防止"虚假交付"。

### 1. 三层控制架构（V11.4 NEW）

V11 用三层架构把"靠 agent 自觉"升级为"靠制度硬化"：

```
┌─────────────────────────────────────────────┐
│  Gate 层（门禁）— 不可绕过，失败即阻断        │
│  ├─ Git 子层：L1 commit / L2 push /          │
│  │   L3 merge / L4 release（husky + CI 触发）│
│  └─ Stage 子层：pre-stage / post-stage /     │
│      pre-accept（阶段切换门禁）               │
└─────────────────────────────────────────────┘
              ↓ PASS 才进入下一层
┌─────────────────────────────────────────────┐
│  Guard 层（守卫）— 工具调用前后自动检查       │
│  ├─ TRAE IDE event hook（5 种 event）        │
│  └─ Shell hook（3 个，阶段切换用）            │
└─────────────────────────────────────────────┘
              ↓ PASS 才进入下一层
┌─────────────────────────────────────────────┐
│  Execution 层（执行）— 13 stage 流水线        │
│  每个 stage 自包含 + 文档驱动 + 状态卡追踪    │
└─────────────────────────────────────────────┘
```

**联动铁律**：Gate PASS → Guard → Execution。任一层 FAIL → 阻断 + 5 字段阻塞报告。Gate 层失败不可绕过（exit ≠ 0）。

**硬化手段**（防止 agent 欺骗绕过）：
- **环境变量强制**：gate 脚本要求 `V11_GATE_ENFORCED` / `V11_GATE_STAGE` / `V11_GATE_CALLER`，缺失即失败
- **SHA-256 签名**：门禁结果签名验签，无法伪造
- **审计轨迹**：状态卡变更写入 `.trae/logs/state-card-audit.jsonl`
- **echo-skip 检测**：守卫脚本拒绝占位符/假通过
- **hooks-fidelity**：验证 hook 是否真实安装、真实执行

### 2. 文档驱动：状态卡（State Card）

每个变更（change）在 `docs/specs/changes/{id}/.state-card.md` 维护一张状态卡，记录：

```yaml
card_type: state-card
current_stage: 1-spec
gate_result: PENDING
last_gate_time: null
```

- **阶段切换**：`stage-gate.py --state-card ...` 校验当前阶段产物是否达标
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
- **物理隔离（V11.3）**：`fact/` + `stage/` 目录隔离，防止子代理越界改非本 stage 文件
- **验收即证据**：不接受"应该可以了"，只接受命令实际输出

### 4. 版本演进

| 版本 | 核心演进 |
|------|---------|
| V11.0 | 高内聚专家架构 + 13 stage |
| V11.1 | Article XVII Secret Redaction + 反虚假交付 |
| V11.2 | 项目级生态管理 + 可验证声明硬约束 |
| V11.3 | 物理隔离 + prototype 演进 + 人工判定覆盖 |
| V11.4 | **三层架构**（Gate/Guard/Execution）+ 门禁硬化 |

---

## 目录结构

```
fullstack4TraeV11/
├── SKILL.md              # 总编排器（必读）
├── README.md             # 本文件
├── CHANGELOG.md          # 版本变更
├── references/           # 公共 references
├── templates/            # 公共 templates
├── scripts/              # 公共脚本（Python，全部实装）
├── skills/               # 13 stage skill（高内聚）
│   ├── 01-intake/
│   ├── 02-plan/
│   ├── ...
│   └── 13-project-health/
└── stage-physical-isolation.md  # 物理隔离规范（V11.3 NEW）
```

---

## 13 stage 流水线

| Stage | 名称 | SKILL.md |
|:---:|------|----------|
| -1 | Intake | [skills/01-intake/SKILL.md](skills/01-intake/SKILL.md) |
| 0 | Plan | [skills/02-plan/SKILL.md](skills/02-plan/SKILL.md) |
| 0.5 | Test Plan | [skills/03-test-plan/SKILL.md](skills/03-test-plan/SKILL.md) |
| 1 | Spec | [skills/04-spec/SKILL.md](skills/04-spec/SKILL.md) |
| 1.5 | Prototype | [skills/05-prototype/SKILL.md](skills/05-prototype/SKILL.md) |
| 2 | Contract | [skills/06-contract/SKILL.md](skills/06-contract/SKILL.md) |
| 3 | Implement | [skills/07-implement/SKILL.md](skills/07-implement/SKILL.md) |
| 3.5 | Real Verify | [skills/08-real-verify/SKILL.md](skills/08-real-verify/SKILL.md) |
| 4 | Review | [skills/09-review/SKILL.md](skills/09-review/SKILL.md) |
| 4.5 | Rot Scan | [skills/10-rot-scan/SKILL.md](skills/10-rot-scan/SKILL.md) |
| 5 | Accept | [skills/11-accept/SKILL.md](skills/11-accept/SKILL.md) |
| 6 | Bug Fix | [skills/12-bug-fix/SKILL.md](skills/12-bug-fix/SKILL.md) |
| 7 | Project Health | [skills/13-project-health/SKILL.md](skills/13-project-health/SKILL.md) |

---

## 快速开始

### 1. 加载 V11 主 SKILL.md

主上下文收到 "Use Skill: fullstack4traev11" 后必走 §0.5 加载协议：

1. 加载 SKILL.md（含 stage_config）
2. 必读公共 references（constitution / common-iron-rules / common-anti-patterns / stage-card-protocol / stage-interaction-protocol / dependency-config / document-layer / report-growth / ask-question-anti-patterns）
3. Glob 项目级约定（AGENTS.md / docs/ / .trae/rules/）
4. 3 层依赖合并（项目 > V11 > 全局）
5. 进入 Stage -1 Intake 工作模式

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
# 状态卡门禁
python scripts/stage-gate.py --state-card docs/specs/changes/{id}/.state-card.md

# 全局阶段门禁（含 verify-rot-scan）
python scripts/phase-gate.py --state-card docs/specs/.state-card.md --verify-rot-scan --change-id {id}

# 腐化扫描
python scripts/proactive-scan.py --project-root . --output rot-scan.md --output-fix-list fix-list.json

# 元检测（rot-detector 自身）
python scripts/self-diagnose.py --project-root .

# 4 维评分
python scripts/acceptance-audit.py --review-report docs/specs/changes/{id}/review-report.md
```

---

## V11.3 增强（opt-in）

- **stage-gate-pre-stage.sh**: husky 式硬阻断门禁（templates/hooks/，独立于 pre-stage.sh）
- **stage-physical-isolation.md**: fact/ + stage/ 物理隔离规范
- 见 [CHANGELOG.md](CHANGELOG.md) 详情

---

## 部署

```bash
# V11 部署到 ~/.trae-cn/skills/
cp -r skill-markets/fullstack4TraeV11/* ~/.trae-cn/skills/fullstack4TraeV11/

# 验证
ls ~/.trae-cn/skills/fullstack4TraeV11/skills/
ls ~/.trae-cn/skills/fullstack4TraeV11/scripts/
```

---

## 关联引用

- [SKILL.md](SKILL.md) - V11 总编排器（V11 入口）
- [CHANGELOG.md](CHANGELOG.md) - 版本变更
- [references/constitution.md](references/constitution.md) - 17 Articles 宪法
- [references/common-iron-rules.md](references/common-iron-rules.md) - 公共铁律
- [references/stage-physical-isolation.md](references/stage-physical-isolation.md) - 物理隔离规范